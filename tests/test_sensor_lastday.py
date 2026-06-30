"""Test del sensor de consumo del último día disponible."""

from datetime import date
from types import SimpleNamespace

from custom_components.octopus_spain.sensor import OctopusLastDayConsumption


def test_sensor_expone_kwh_y_fecha():
    coord = SimpleNamespace(data={"ES0021000013208057RM": {"last_day_kwh": 10.705, "last_day_date": date(2026, 6, 28)}})
    sensor = OctopusLastDayConsumption("ES0021000013208057RM", coord)

    # pylint: disable=protected-access
    sensor._handle_coordinator_update_value()

    assert sensor.native_value == 10.705
    assert sensor.extra_state_attributes["Fecha"] == date(2026, 6, 28)
