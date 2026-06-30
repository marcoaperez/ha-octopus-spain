"""Tests del cliente API (lib/octopus_spain.py)."""

from datetime import datetime, timezone

import pytest

import custom_components.octopus_spain.lib.octopus_spain as mod
from custom_components.octopus_spain.lib.octopus_spain import OctopusApiError, OctopusSpain


class _FakeClient:
    """Cliente GraphQL simulado que devuelve una respuesta fija."""

    def __init__(self, response):
        self._response = response

    async def execute_async(self, query, variables=None):
        return self._response


class _SeqClient:
    """Cliente simulado que devuelve respuestas por flujo (import/export), paginando."""

    def __init__(self, by_field):
        self._by_field = {k: list(v) for k, v in by_field.items()}

    async def execute_async(self, query, variables=None):
        field = "importReadings" if "importReadings" in query else "exportReadings"
        return self._by_field[field].pop(0)


def _patch(monkeypatch, response):
    monkeypatch.setattr(mod, "GraphqlClient", lambda *a, **k: _FakeClient(response))


def _conn(field, nodes, has_next, end_cursor=None):
    """Construye una respuesta de una conexión de lecturas (una página)."""
    return {
        "data": {
            "supplyPoints": {
                "edges": [
                    {
                        "node": {
                            "readings": {
                                field: {
                                    "pageInfo": {"hasNextPage": has_next, "endCursor": end_cursor},
                                    "edges": [{"node": n} for n in nodes],
                                }
                            }
                        }
                    }
                ]
            }
        }
    }


def _node(hour, value):
    return {
        "value": value,
        "units": "KILOWATT_HOURS",
        "intervalStart": f"2026-06-28T{hour:02d}:00:00+02:00",
        "intervalEnd": f"2026-06-28T{hour + 1:02d}:00:00+02:00",
    }


_START = datetime(2026, 6, 28, tzinfo=timezone.utc)
_END = datetime(2026, 6, 29, tzinfo=timezone.utc)


async def test_cups_extrae_identificadores(monkeypatch):
    _patch(monkeypatch, {"data": {"account": {"properties": [{"electricitySupplyPoints": [{"cups": "ES0021000013208057RM"}]}]}}})
    api = OctopusSpain("e", "p")
    api._token = "t"
    assert await api.cups("A-1") == ["ES0021000013208057RM"]


async def test_readings_pagina_y_concatena(monkeypatch):
    """readings() debe seguir pageInfo.endCursor y concatenar todas las páginas."""
    p1 = _conn("importReadings", [_node(0, "1.0")], True, "c1")
    p2 = _conn("importReadings", [_node(1, "2.0")], False)
    exp = _conn("exportReadings", [], False)
    monkeypatch.setattr(mod, "GraphqlClient", lambda *a, **k: _SeqClient({"importReadings": [p1, p2], "exportReadings": [exp]}))
    api = OctopusSpain("e", "p")
    api._token = "t"
    out = await api.readings("A-1", _START, _END)
    assert [r["value"] for r in out["import"]] == [1.0, 2.0]
    assert out["export"] == []


async def test_readings_sin_punto_devuelve_vacio(monkeypatch):
    _patch(monkeypatch, {"data": {"supplyPoints": {"edges": []}}})
    api = OctopusSpain("e", "p")
    api._token = "t"
    out = await api.readings("A-1", _START, _END)
    assert out == {"import": [], "export": []}


async def test_readings_lanza_error_si_la_api_devuelve_errors(monkeypatch):
    """Si la API responde con errors (sin data), debe lanzar OctopusApiError con el mensaje."""
    _patch(monkeypatch, {"errors": [{"message": "Query exceeds maximum allowed node count."}]})
    api = OctopusSpain("e", "p")
    api._token = "t"
    with pytest.raises(OctopusApiError) as exc:
        await api.readings("A-1", _START, _END)
    assert "node count" in str(exc.value)
