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

    Tiempo resistencia (STA):
        P_i = (t_i - t_min) / (t_max - t_min) × 100
        t_max → 100 pts (más tiempo = mejor), t_min → 0 pts.

    Tiempo velocidad (SPE_*):
        P_i = (t_max - t_i) / (t_max - t_min) × 100
        t_min → 100 pts (más rápido = mejor), t_max → 0 pts.

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
            return _calcular_tiempo(resultados, mayor_es_mejor=disciplina.tiempo_mayor_es_mejor())
        return _calcular_distancia(resultados)


def _calcular_distancia(resultados: list[ResultadoFinal]) -> dict[UUID, Decimal]:
    grupos = _agrupar_por_categoria(resultados)
    puntos: dict[UUID, Decimal] = {}
    for grupo in grupos.values():
        validos = [r for r in grupo if _es_valido(r) and r.rp is not None]
        d_max = max((r.rp for r in validos), default=None)
        for r in grupo:
            if d_max is None or not _es_valido(r) or r.rp is None:
                puntos[r.atleta_id] = _CERO
            else:
                puntos[r.atleta_id] = _redondear(r.rp / d_max * _CIEN)
    return puntos


def _calcular_tiempo(
    resultados: list[ResultadoFinal], *, mayor_es_mejor: bool = False
) -> dict[UUID, Decimal]:
    grupos = _agrupar_por_categoria(resultados)
    puntos: dict[UUID, Decimal] = {}
    for grupo in grupos.values():
        validos = [r for r in grupo if _es_valido(r) and r.rp is not None]
        t_min = min((r.rp for r in validos), default=None)
        t_max = max((r.rp for r in validos), default=None)
        for r in grupo:
            puntos[r.atleta_id] = _puntaje_tiempo(r, t_min, t_max, mayor_es_mejor=mayor_es_mejor)
    return puntos


def _agrupar_por_categoria(
    resultados: list[ResultadoFinal],
) -> dict[str, list[ResultadoFinal]]:
    grupos: dict[str, list[ResultadoFinal]] = {}
    for r in resultados:
        key = r.categoria.value if r.categoria else "SIN_CATEGORIA"
        grupos.setdefault(key, []).append(r)
    return grupos


def _puntaje_tiempo(
    resultado: ResultadoFinal,
    t_min: Decimal | None,
    t_max: Decimal | None,
    *,
    mayor_es_mejor: bool = False,
) -> Decimal:
    if t_min is None or not _es_valido(resultado) or resultado.rp is None:
        return _CERO
    if t_max == t_min:
        return _CIEN
    if mayor_es_mejor:
        # STA: mayor tiempo = mejor → t_max recibe 100 pts
        return _redondear((resultado.rp - t_min) / (t_max - t_min) * _CIEN)
    # SPE: menor tiempo = mejor → t_min recibe 100 pts
    return _redondear((t_max - resultado.rp) / (t_max - t_min) * _CIEN)


def _es_valido(r: ResultadoFinal) -> bool:
    if r.es_dns:
        return False
    tarjeta = (r.tarjeta or "").lower()
    return tarjeta not in {"roja", "red"}


def _redondear(valor: Decimal) -> Decimal:
    return valor.quantize(_DOS_DECIMALES, rounding=ROUND_HALF_UP)
