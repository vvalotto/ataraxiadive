"""Value Object TipoTarjeta — tipo de tarjeta asignada a una Performance."""

from __future__ import annotations

from enum import StrEnum


class TipoTarjeta(StrEnum):
    """Tipo de tarjeta asignada al finalizar una Performance.

    Blanca: Performance válida — sin penalización.
    Amarilla: Penalización parcial con deducción — motivo obligatorio (INV-P-11).
    Roja: Descalificación — motivo obligatorio (INV-P-11).
    """

    Blanca = "Blanca"
    Amarilla = "Amarilla"
    Roja = "Roja"
