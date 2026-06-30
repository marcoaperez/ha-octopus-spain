"""Tests del cliente API (lib/octopus_spain.py)."""

import asyncio

import custom_components.octopus_spain.lib.octopus_spain as mod
from custom_components.octopus_spain.lib.octopus_spain import OctopusSpain


class _FakeClient:
    """Cliente GraphQL simulado que devuelve una respuesta fija."""

    def __init__(self, response):
        self._response = response

    async def execute_async(self, query, variables=None):
        return self._response


def _patch(monkeypatch, response):
    monkeypatch.setattr(mod, "GraphqlClient", lambda *a, **k: _FakeClient(response))


def test_cups_extrae_identificadores(monkeypatch):
    _patch(monkeypatch, {"data": {"account": {"properties": [
        {"electricitySupplyPoints": [{"cups": "ES0021000013208057RM"}]}
    ]}}})
    api = OctopusSpain("e", "p")
    api._token = "t"
    assert asyncio.run(api.cups("A-1")) == ["ES0021000013208057RM"]
