"""Aggregate RankingCompetencia — calcula y persiste el ranking de una disciplina."""

from __future__ import annotations

import json
from collections import defaultdict
from decimal import Decimal
from typing import Any
from uuid import UUID

from registro.domain.value_objects.categoria import Categoria
from shared.domain.base.aggregate_root import AggregateRoot
from resultados.domain.events.resultados_calculados import ResultadosCalculados
from resultados.domain.ports.resultados_competencia_port import ResultadoFinal
from resultados.domain.value_objects.entrada_ranking import EntradaRanking
from shared.domain.value_objects.disciplina import Disciplina
from shared.domain.value_objects.disciplina_descriptor import DisciplinaDescriptor

# Tarjetas que producen un resultado válido (se posicionan antes de DNS/Roja)
_TARJETAS_VALIDAS = {"Blanca", "BlancaConPenalizaciones", "Amarilla"}
_CATEGORIA_DEFAULT = Categoria.SENIOR_MASCULINO


class RankingCompetencia(AggregateRoot):
    """Aggregate raíz del BC Resultados.

    Calcula el ranking de una disciplina a partir de los resultados finales
    de todas las performances (Ejecutada + DNS).

    Stream ID: "ranking-{competencia_id}-{disciplina}"

    Reglas de ordenamiento (RF-PM-03):
        1. Performances válidas (Blanca/BlancaConPenalizaciones/Amarilla): RP mayor → menor.
        2. Empates: comparten posición; la siguiente posición se omite.
        3. DNS y tarjeta roja: al final, sin marca numérica.
        4. Podio: posiciones 1, 2 y 3 (incluyendo empates en esas posiciones).
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
        descriptor: DisciplinaDescriptor,
    ) -> None:
        """Calcula el ranking y emite ResultadosCalculados.

        Args:
            resultados: Lista completa de resultados finales (Ejecutada + DNS).
            descriptor: Descriptor de la disciplina (para ordenamiento).

        Raises:
            ResultadosIncompletos: Si la lista está vacía.
        """
        if not resultados:
            from resultados.domain.exceptions import ResultadosIncompletos

            raise ResultadosIncompletos(
                f"RankingCompetencia {self._competencia_id}: sin resultados para calcular"
            )

        entries = _calcular_entries(resultados)

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
        event_type = event["event_type"]
        payload = self._parse_payload(event["payload"])
        if event_type == "ResultadosCalculados":
            self._apply_resultados_calculados(payload)

    def _apply_resultados_calculados(self, payload: dict[str, Any]) -> None:
        self._entries = [_dict_a_entrada(e) for e in payload["entries"]]
        self._calculado = True

    @staticmethod
    def _parse_payload(payload: Any) -> dict[str, Any]:
        if isinstance(payload, str):
            return json.loads(payload)  # type: ignore[no-any-return]
        return payload  # type: ignore[return-value]


# ── Helpers de dominio ────────────────────────────────────────────────────────


def _calcular_entries(resultados: list[ResultadoFinal]) -> list[EntradaRanking]:
    """Aplica reglas de ordenamiento y asignación de posiciones.

    Válidas (Blanca/BlancaConPenalizaciones/Amarilla): ordenadas por RP desc (mayor es mejor).
    Inválidas (DNS/Roja): al final, en orden de aparición.
    Empates: comparten posición; la siguiente se omite.
    Podio: posiciones 1, 2 y 3.
    """
    grupos = _agrupar_por_categoria(resultados)
    entries: list[EntradaRanking] = []
    for categoria in sorted(grupos, key=lambda cat: cat.value):
        entries.extend(_calcular_entries_categoria(categoria, grupos[categoria]))

    return entries


def _agrupar_por_categoria(
    resultados: list[ResultadoFinal],
) -> dict[Categoria, list[ResultadoFinal]]:
    grupos: dict[Categoria, list[ResultadoFinal]] = defaultdict(list)
    for resultado in resultados:
        grupos[resultado.categoria or _CATEGORIA_DEFAULT].append(resultado)
    return dict(grupos)


def _calcular_entries_categoria(
    categoria: Categoria,
    resultados: list[ResultadoFinal],
) -> list[EntradaRanking]:
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
        pos = _resolver_posicion_valida(entries, validas_ordenadas, resultado, i, posicion_actual)
        entries.append(_crear_entry_valida(categoria, resultado, pos))
        posicion_actual = len(entries) + 1

    for resultado in invalidas:
        entries.append(_crear_entry_invalida(categoria, resultado, posicion_actual))
        posicion_actual += 1

    return entries


def _resolver_posicion_valida(
    entries: list[EntradaRanking],
    validas_ordenadas: list[ResultadoFinal],
    resultado: ResultadoFinal,
    index: int,
    posicion_actual: int,
) -> int:
    if index > 0 and resultado.rp == validas_ordenadas[index - 1].rp:
        return entries[-1].posicion
    return posicion_actual


def _crear_entry_valida(
    categoria: Categoria,
    resultado: ResultadoFinal,
    posicion: int,
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
    }


def _dict_a_entrada(d: dict[str, Any]) -> EntradaRanking:
    """Deserializa un dict a EntradaRanking."""
    return EntradaRanking(
        posicion=d["posicion"],
        atleta_id=UUID(d["atleta_id"]),
        categoria=Categoria(d.get("categoria", _CATEGORIA_DEFAULT.value)),
        rp=Decimal(d["rp"]) if d["rp"] is not None else None,
        unidad=d["unidad"],
        tarjeta=d["tarjeta"],
        es_dns=d["es_dns"],
        en_podio=d["en_podio"],
    )
