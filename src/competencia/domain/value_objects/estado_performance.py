"""Value Object EstadoPerformance — máquina de estados del ciclo de vida."""

from __future__ import annotations

from enum import StrEnum


class EstadoPerformance(StrEnum):
    """Estados del ciclo de vida de una Performance.

    Transiciones válidas:
        AnunciadaAP → Llamada → ResultadoRegistrado → Ejecutada  (camino nominal)
        AnunciadaAP → Llamada → DNS                              (atleta no se presentó)
    """

    AnunciadaAP = "AnunciadaAP"  # AP registrado, esperando llamado
    Llamada = "Llamada"  # Atleta llamado al OT
    ResultadoRegistrado = "ResultadoRegistrado"  # RP registrado, esperando tarjeta
    Ejecutada = "Ejecutada"  # Tarjeta asignada (estado final)
    DNS = "DNS"  # Did Not Start (estado final)
