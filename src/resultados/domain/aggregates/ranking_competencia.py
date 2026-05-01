"""Aggregate RankingCompetencia — calcula y persiste el ranking de una disciplina."""

from __future__ import annotations

import json
from collections import defaultdict
from decimal import Decimal
from typing import Any
from uuid import UUID

from registro.domain.value_objects.categoria import Categoria
from resultados.domain.events.resultados_calculados import ResultadosCalculados
from resultados.domain.ports.algoritmo_puntaje import AlgoritmoPuntaje
from resultados.domain.ports.resultados_competencia_port import ResultadoFinal
from resultados.domain.value_objects.entrada_ranking import EntradaRanking
from shared.domain.base.aggregate_root import AggregateRoot
from shared.domain.value_objects.disciplina import Disciplina

# Tarjetas que producen un resultado válido (se posicionan antes de DNS/Roja)
_TARJETAS_VALIDAS = {"Blanca", "BlancaConPenalizaciones", "Amarilla"}
_CATEGORIA_DEFAULT = Categoria.SENIOR_MASCULINO


class RankingCompetencia(AggregateRoot):
    """Aggregate raíz del BC Resultados.

    Calcula el ranking de una disciplina a partir de los resultados finales
    de todas las performances (Ejecutada + DNS).

    Stream ID: "ranking-{competencia_id}-{disciplina}"

    Reglas de ordenamiento:
        Con algoritmo (FAAS, INV-5.6.3-01/02):
            1. Performances válidas: puntos desc dentro de cada Categoría.
            2. Empate de puntos: desempate por RP desc.
            3. DNS y tarjeta roja: puntos=0.00, al final, sin posición de podio.
        Sin algoritmo (path legacy):
            1. Performances válidas: RP desc (mayor es mejor).
            2. Empates de RP: comparten posición; la siguiente se omite.
            3. DNS y tarjeta roja: al final, sin marca numérica.
        Podio: posiciones 1, 2 y 3 (incluyendo empates en esas posiciones).
    """

    def __init__(self, competencia_id: UUID, disciplina: Disciplina) -> None:
        super().__init__()
        self._competencia_id = competencia_id
        self._disciplina = disciplina
        self._entries: list[EntradaRanking] = []
        self._calculado: bool = False

    # ── Propiedades ───────────────────────────────────────────────────────────

    @property
    def competencia_id(self) -> UUID:
        """Identificador de la competencia."""
        return self._competencia_id

    @property
    def disciplina(self) -> Disciplina:
        """Disciplina del ranking."""
        return self._disciplina

    @property
    def entries(self) -> list[EntradaRanking]:
        """Entradas del ranking calculado, ordenadas por posición."""
        return list(self._entries)

    @property
    def calculado(self) -> bool:
        """True si el ranking ya fue calculado."""
        return self._calculado

    # ── Comando de dominio ────────────────────────────────────────────────────

    def calcular(
        self,
        resultados: list[ResultadoFinal],
        algoritmo: AlgoritmoPuntaje | None = None,
    ) -> None:
        """Calcula el ranking y emite ResultadosCalculados.

        Args:
            resultados: Lista completa de resultados finales (Ejecutada + DNS).
            algoritmo: AlgoritmoPuntaje para calcular puntos. None → path legacy (sort por RP).

        Raises:
            ResultadosIncompletos: Si la lista está vacía.
        """
        if not resultados:
            from resultados.domain.exceptions import ResultadosIncompletos

            raise ResultadosIncompletos(
                f"RankingCompetencia {self._competencia_id}: sin resultados para calcular"
            )

        entries = _calcular_entries(resultados, algoritmo, self._disciplina)

        now = ResultadosCalculados.now()
        entries_payload = [_entrada_a_dict(e) for e in entries]

        event = ResultadosCalculados(
            event_type="ResultadosCalculados",
            aggregate_id=f"{self._competencia_id}-{self._disciplina.value}",
            occurred_at=now,
            competencia_id=str(self._competencia_id),
            disciplina=self._disciplina.value,
            total=len(entries),
            entries=tuple(entries_payload),
            calculado_en=now.isoformat(),
        )
        self._entries = entries
        self._calculado = True
        self._record(event)

    # ── Reconstitución ────────────────────────────────────────────────────────

    @classmethod
    def reconstitute(
        cls,
        competencia_id: UUID,
        disciplina: Disciplina,
        events: list[dict[str, Any]],
    ) -> "RankingCompetencia":
        """Reconstruye el aggregate desde los eventos del Event Store."""
        ranking = cls(competencia_id=competencia_id, disciplina=disciplina)
        for event in events:
            ranking._apply_stored(event)
        return ranking

    def _apply_stored(self, event: dict[str, Any]) -> None:
        """Aplica un evento almacenado al estado interno."""
        payload = self._parse_payload(event["payload"])
        if event["event_type"] == "ResultadosCalculados":
            self._rehidratar_resultados_calculados(payload)

    def _rehidratar_resultados_calculados(self, payload: dict[str, Any]) -> None:
        self._entries = _deserializar_entries(payload["entries"])
        self._calculado = True

    @staticmethod
    def _parse_payload(payload: Any) -> dict[str, Any]:
        if isinstance(payload, str):
            return json.loads(payload)  # type: ignore[no-any-return]
        return payload  # type: ignore[return-value]


# ── Helpers de dominio ────────────────────────────────────────────────────────


def _calcular_entries(
    resultados: list[ResultadoFinal],
    algoritmo: AlgoritmoPuntaje | None,
    disciplina: Disciplina,
) -> list[EntradaRanking]:
    """Despacha al path con puntos FAAS o al path legacy según el algoritmo."""
    grupos = _agrupar_por_categoria(resultados)
    entries: list[EntradaRanking] = []
    if algoritmo is not None:
        puntos_map = algoritmo.calcular(resultados, disciplina)
        for categoria in sorted(grupos, key=lambda cat: cat.value):
            entries.extend(
                _calcular_entries_categoria_con_puntos(categoria, grupos[categoria], puntos_map)
            )
    else:
        for categoria in sorted(grupos, key=lambda cat: cat.value):
            entries.extend(_calcular_entries_categoria_legacy(categoria, grupos[categoria]))
    return entries


def _deserializar_entries(entries: list[dict[str, Any]]) -> list[EntradaRanking]:
    return [_dict_a_entrada(entry) for entry in entries]


def _agrupar_por_categoria(
    resultados: list[ResultadoFinal],
) -> dict[Categoria, list[ResultadoFinal]]:
    grupos: dict[Categoria, list[ResultadoFinal]] = defaultdict(list)
    for resultado in resultados:
        grupos[resultado.categoria or _CATEGORIA_DEFAULT].append(resultado)
    return dict(grupos)


def _calcular_entries_categoria_con_puntos(
    categoria: Categoria,
    resultados: list[ResultadoFinal],
    puntos_map: dict[UUID, Decimal],
) -> list[EntradaRanking]:
    """Path FAAS: ordena por puntos desc; tie-break por RP desc (INV-5.6.3-01/02)."""
    validas = [r for r in resultados if r.tarjeta in _TARJETAS_VALIDAS]
    invalidas = [r for r in resultados if r.tarjeta not in _TARJETAS_VALIDAS]

    validas_ordenadas = sorted(
        validas,
        key=lambda r: (
            puntos_map.get(r.atleta_id, Decimal("0")),
            r.rp if r.rp is not None else Decimal(0),
        ),
        reverse=True,
    )

    entries: list[EntradaRanking] = []
    posicion_actual = 1
    for i, resultado in enumerate(validas_ordenadas):
        puntos = puntos_map.get(resultado.atleta_id, Decimal("0.00"))
        if i > 0:
            prev_puntos = puntos_map.get(validas_ordenadas[i - 1].atleta_id, Decimal("0.00"))
            pos = entries[-1].posicion if puntos == prev_puntos else posicion_actual
        else:
            pos = posicion_actual
        entries.append(_crear_entry_valida(categoria, resultado, pos, puntos))
        posicion_actual = len(entries) + 1

    for resultado in invalidas:
        entries.append(_crear_entry_invalida(categoria, resultado, posicion_actual))
        posicion_actual += 1

    return entries


def _calcular_entries_categoria_legacy(
    categoria: Categoria,
    resultados: list[ResultadoFinal],
) -> list[EntradaRanking]:
    """Path legacy (sin algoritmo): ordena por RP desc; puntos=0.00."""
    validas = [r for r in resultados if r.tarjeta in _TARJETAS_VALIDAS]
    invalidas = [r for r in resultados if r.tarjeta not in _TARJETAS_VALIDAS]
    validas_ordenadas = sorted(
        validas,
        key=lambda r: r.rp if r.rp is not None else Decimal(0),
        reverse=True,
    )

    entries: list[EntradaRanking] = []
    posicion_actual = 1
    for i, resultado in enumerate(validas_ordenadas):
        if i > 0 and resultado.rp == validas_ordenadas[i - 1].rp:
            pos = entries[-1].posicion
        else:
            pos = posicion_actual
        entries.append(_crear_entry_valida(categoria, resultado, pos))
        posicion_actual = len(entries) + 1

    for resultado in invalidas:
        entries.append(_crear_entry_invalida(categoria, resultado, posicion_actual))
        posicion_actual += 1

    return entries


def _crear_entry_valida(
    categoria: Categoria,
    resultado: ResultadoFinal,
    posicion: int,
    puntos: Decimal = Decimal("0.00"),
) -> EntradaRanking:
    return EntradaRanking(
        posicion=posicion,
        atleta_id=resultado.atleta_id,
        categoria=categoria,
        rp=resultado.rp,
        unidad=resultado.unidad,
        tarjeta=resultado.tarjeta,
        es_dns=False,
        en_podio=posicion <= 3,
        puntos=puntos,
    )


def _crear_entry_invalida(
    categoria: Categoria,
    resultado: ResultadoFinal,
    posicion: int,
) -> EntradaRanking:
    return EntradaRanking(
        posicion=posicion,
        atleta_id=resultado.atleta_id,
        categoria=categoria,
        rp=None if resultado.es_dns else resultado.rp,
        unidad=None if resultado.es_dns else resultado.unidad,
        tarjeta=resultado.tarjeta,
        es_dns=resultado.es_dns,
        en_podio=False,
        puntos=Decimal("0.00"),
    )


def _entrada_a_dict(e: EntradaRanking) -> dict[str, Any]:
    """Serializa una EntradaRanking a dict JSON-serializable."""
    return {
        "posicion": e.posicion,
        "atleta_id": str(e.atleta_id),
        "categoria": e.categoria.value,
        "rp": str(e.rp) if e.rp is not None else None,
        "unidad": e.unidad,
        "tarjeta": e.tarjeta,
        "es_dns": e.es_dns,
        "en_podio": e.en_podio,
        "puntos": str(e.puntos),
    }


def _dict_a_entrada(d: dict[str, Any]) -> EntradaRanking:
    """Deserializa un dict a EntradaRanking. Fallback puntos="0.00" para eventos legacy."""
    return EntradaRanking(
        posicion=d["posicion"],
        atleta_id=UUID(d["atleta_id"]),
        categoria=Categoria(d.get("categoria", _CATEGORIA_DEFAULT.value)),
        rp=Decimal(d["rp"]) if d["rp"] is not None else None,
        unidad=d["unidad"],
        tarjeta=d["tarjeta"],
        es_dns=d["es_dns"],
        en_podio=d["en_podio"],
        puntos=Decimal(d.get("puntos", "0.00")),
    )
