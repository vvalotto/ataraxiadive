"""Step definitions BDD — US-ADJ-4.6: TiempoAP."""

from __future__ import annotations

from decimal import Decimal

import pytest
from pytest_bdd import parsers, scenarios, then, when

from shared.domain.value_objects.tiempo_ap import TiempoAP

scenarios("../US-ADJ-4.6-tiempo-ap.feature")


@pytest.fixture
def context() -> dict:
    return {}


@when(parsers.parse('se crea TiempoAP desde "{texto}"'))
def crear_desde_mmss(context: dict, texto: str) -> None:
    context["tiempo_ap"] = TiempoAP.desde_mmss(texto)


@when(parsers.parse('se intenta crear TiempoAP desde "{texto}"'))
def intentar_desde_mmss(context: dict, texto: str) -> None:
    try:
        TiempoAP.desde_mmss(texto)
    except ValueError as exc:
        context["error"] = str(exc)


@when(parsers.parse('se crea TiempoAP desde segundos Decimal("{valor}")'))
def crear_desde_segundos(context: dict, valor: str) -> None:
    context["tiempo_ap"] = TiempoAP.desde_segundos(Decimal(valor))


@when(parsers.parse('se intenta crear TiempoAP desde segundos Decimal("{valor}")'))
def intentar_desde_segundos(context: dict, valor: str) -> None:
    try:
        TiempoAP.desde_segundos(Decimal(valor))
    except ValueError as exc:
        context["error"] = str(exc)


@then(parsers.parse("el valor en segundos es {segundos:d}"))
def validar_segundos(context: dict, segundos: int) -> None:
    assert context["tiempo_ap"].segundos == Decimal(segundos)


@then("el sistema lanza FormatoTiempoInvalido")
def validar_error_formato(context: dict) -> None:
    assert "FormatoTiempoInvalido" in context["error"]


@then("el sistema lanza ValorTiempoInvalido")
def validar_error_valor(context: dict) -> None:
    assert "ValorTiempoInvalido" in context["error"]
