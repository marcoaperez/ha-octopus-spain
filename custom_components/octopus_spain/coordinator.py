"""Coordinator de energía (consumo/vertido) para Octopus Spain."""

import logging
from datetime import datetime, timedelta

import homeassistant.util.dt as dt_util
from homeassistant.components.recorder import get_instance
from homeassistant.components.recorder.statistics import get_last_statistics
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import ENERGY_UPDATE_INTERVAL, READING_GRANULARITY, STATISTICS_BACKFILL_DAYS
from .lib.octopus_spain import OctopusApiError, OctopusSpain
from .statistics import DOMAIN_SOURCE, _row_start_to_datetime, async_import_statistics

_LOGGER = logging.getLogger(__name__)


class EnergyCoordinator(DataUpdateCoordinator):
    """Coordina la descarga de lecturas y su inyección como estadísticas."""

    def __init__(self, hass: HomeAssistant, email: str, password: str):
        super().__init__(
            hass=hass,
            logger=_LOGGER,
            name="Octopus Spain Energy",
            update_interval=timedelta(hours=ENERGY_UPDATE_INTERVAL),
        )
        self._api = OctopusSpain(email, password)

    async def _async_update_data(self):
        if not await self._api.login():
            return self.data or {}

        try:
            accounts = await self._api.accounts()
            result = {}
            end = dt_util.utcnow().replace(minute=0, second=0, microsecond=0)
            for account in accounts:
                for cups in await self._api.cups(account):
                    start = await self._compute_start(cups, end)
                    readings = await self._api.readings(account, start, end, READING_GRANULARITY)
                    await async_import_statistics(self.hass, cups, "consumo", readings["import"])
                    if readings["export"]:
                        await async_import_statistics(self.hass, cups, "vertido", readings["export"])
                    result[cups] = self._last_day(readings["import"])
            return result
        except OctopusApiError as err:
            raise UpdateFailed(f"Error de la API de Octopus: {err}") from err

    async def _compute_start(self, cups: str, end: datetime) -> datetime:
        """Si ya hay estadísticas, parte de la última hora; si no, backfill."""
        statistic_id = f"{DOMAIN_SOURCE}:consumo_{cups.lower()}"
        last = await get_instance(self.hass).async_add_executor_job(get_last_statistics, self.hass, 1, statistic_id, True, {"sum"})
        if last.get(statistic_id):
            return _row_start_to_datetime(last[statistic_id][0]["start"])
        return end - timedelta(days=STATISTICS_BACKFILL_DAYS)

    @staticmethod
    def _last_day(import_readings: list[dict]) -> dict:
        """Suma del último día disponible (para el sensor 'consumo último día')."""
        if not import_readings:
            return {"last_day_kwh": None, "last_day_date": None}
        last_date = max(r["start"].date() for r in import_readings)
        total = round(sum(r["value"] for r in import_readings if r["start"].date() == last_date), 3)
        return {"last_day_kwh": total, "last_day_date": last_date}
