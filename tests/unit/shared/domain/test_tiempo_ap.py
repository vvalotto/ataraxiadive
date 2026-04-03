"""Tests unitarios de TiempoAP."""

from __future__ import annotations

from decimal import Decimal

import pytest

from shared.domain.value_objects.tiempo_ap import TiempoAP


def test_desde_mmss_valido() -> None:
    assert TiempoAP.desde_mmss("02:30").segundos == Decimal("150")


def test_desde_hhmmss_valido() -> None:
    assert TiempoAP.desde_mmss("01:00:00").segundos == Decimal("3600")


@pytest.mark.parametrize("texto", ["abc", "2:xx", "1:2:3:4", "02:60", "01:99:00"])
def test_desde_mmss_invalido(texto: str) -> None:
    with pytest.raises(ValueError, match="FormatoTiempoInvalido"):
        TiempoAP.desde_mmss(texto)


def test_desde_mmss_cero_invalido() -> None:
    with pytest.raises(ValueError, match="ValorTiempoInvalido"):
        TiempoAP.desde_mmss("00:00")


def test_desde_segundos_directo() -> None:
    assert TiempoAP.desde_segundos(Decimal("196")).segundos == Decimal("196")


@pytest.mark.parametrize("valor", [Decimal("0"), Decimal("-1")])
def test_desde_segundos_invalido(valor: Decimal) -> None:
    with pytest.raises(ValueError, match="ValorTiempoInvalido"):
        TiempoAP.desde_segundos(valor)
