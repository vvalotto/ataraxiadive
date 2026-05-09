"""Servicio de dominio AlgoritmoPuntajeFAAS — reglamento FAAS."""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal
from uuid import UUID

from resultados.domain.ports.algoritmo_puntaje import AlgoritmoPuntaje
from resultados.domain.ports.resultados_competencia_port import ResultadoFinal
from shared.domain.value_objects.disciplina import Disciplina

_DOS_DECIMALES = Decimal("0.01")
_CIEN = Decimal("100")
_CERO = Decimal("0.00")


class AlgoritmoPuntajeFAAS(AlgoritmoPuntaje):
    """Implementa el reglamento FAAS para calcular puntos por disciplina.

    Distancia (DNF, DYN, DBF, …):
        P_i = (d_i / d_max) × 100
        d_max = max RP entre atletas con tarjeta blanca.

    Tiempo (STA, SPE_*):
        P_i = (t_max - t_i) / (t_max - t_min) × 100
        t_min → 100 pts (más rápido), t_max → 0 pts (más lento).
        Caso borde: t_max == t_min → todos reciben 100.

    DNS y tarjeta roja → 0 puntos; excluidos del cálculo de referencia.
    """

    def calcular(
        self,
        resultados: list[ResultadoFinal],
        disciplina: Disciplina,
    ) -> dict[UUID, Decimal]:
        if not resultados:
            return {}

        if disciplina.es_tiempo():
            return _calcular_tiempo(resultados)
        return _calcular_distancia(resultados)


def _calcular_distancia(resultados: list[ResultadoFinal]) -> dict[UUID, Decimal]:
    validos = [r for r in resultados if _es_valido(r) and r.rp is not None]
    d_max = max((r.rp for r in validos), default=None)

    puntos: dict[UUID, Decimal] = {}
    for r in resultados:
        if d_max is None or not _es_valido(r) or r.rp is None:
            puntos[r.atleta_id] = _CERO
        else:
            puntos[r.atleta_id] = _redondear(r.rp / d_max * _CIEN)
    return puntos


def _calcular_tiempo(resultados: list[ResultadoFinal]) -> dict[UUID, Decimal]:
    validos = [r for r in resultados if _es_valido(r) and r.rp is not None]
    t_min = min((r.rp for r in validos), default=None)
    t_max = max((r.rp for r in validos), default=None)

    puntos: dict[UUID, Decimal] = {}
    for r in resultados:
        puntos[r.atleta_id] = _puntaje_tiempo(r, t_min, t_max)
    return puntos


def _puntaje_tiempo(
    resultado: ResultadoFinal,
    t_min: Decimal | None,
    t_max: Decimal | None,
) -> Decimal:
    if t_min is None or not _es_valido(resultado) or resultado.rp is None:
        return _CERO
    if t_max == t_min:
        return _CIEN
    return _redondear((t_max - resultado.rp) / (t_max - t_min) * _CIEN)


def _es_valido(r: ResultadoFinal) -> bool:
    if r.es_dns:
        return False
    tarjeta = (r.tarjeta or "").lower()
    return tarjeta not in {"roja", "red"}


def _redondear(valor: Decimal) -> Decimal:
    return valor.quantize(_DOS_DECIMALES, rounding=ROUND_HALF_UP)
