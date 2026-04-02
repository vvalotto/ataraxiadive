"""Aggregate RankingOverall — cálculo posicional multi-disciplina por torneo."""

from __future__ import annotations

import json
from typing import Any
from uuid import UUID

from resultados.domain.events.ranking_overall_calculado import RankingOverallCalculado
from resultados.domain.value_objects.entrada_overall import EntradaOverall
from resultados.domain.value_objects.entrada_ranking import EntradaRanking
from shared.domain.base.aggregate_root import AggregateRoot
from shared.domain.value_objects.disciplina import Disciplina


class RankingOverall(AggregateRoot):
    """Aggregate raíz del ranking general por torneo.

    Stream ID: "ranking-overall-{torneo_id}"
    """

    def __init__(self, torneo_id: UUID) -> None:
        super().__init__()
        self._torneo_id = torneo_id
        self._entries: list[EntradaOverall] = []
        self._calculado = False

    @property
    def torneo_id(self) -> UUID:
        """Identificador del torneo."""
        return self._torneo_id

    @property
    def entries(self) -> list[EntradaOverall]:
        """Entradas calculadas del overall."""
        return list(self._entries)

    @property
    def calculado(self) -> bool:
        """True si el overall ya fue calculado."""
        return self._calculado

    def calcular(
        self,
        torneo_id: UUID,
        rankings_por_disciplina: dict[Disciplina, list[EntradaRanking]],
        penalizacion_ausente: int | None = None,
    ) -> list[EntradaOverall]:
        """Calcula y registra el ranking overall."""
        entries = _calcular_entries(rankings_por_disciplina, penalizacion_ausente)
        if not entries:
            self._entries = []
            self._calculado = False
            return []

        event = RankingOverallCalculado(
            event_type="RankingOverallCalculado",
            aggregate_id=str(torneo_id),
            occurred_at=RankingOverallCalculado.now(),
            torneo_id=str(torneo_id),
            disciplinas=tuple(disciplina.value for disciplina in rankings_por_disciplina),
            total=len(entries),
            entries=tuple(_entrada_a_dict(entry) for entry in entries),
            calculado_en=RankingOverallCalculado.now().isoformat(),
        )
        self._entries = entries
        self._calculado = True
        self._record(event)
        return list(entries)

    @classmethod
    def reconstitute(cls, torneo_id: UUID, events: list[dict[str, Any]]) -> "RankingOverall":
        """Reconstruye el aggregate desde el Event Store."""
        ranking = cls(torneo_id)
        for event in events:
            ranking._apply_stored(event)
        return ranking

    def _apply_stored(self, event: dict[str, Any]) -> None:
        payload = self._parse_payload(event["payload"])
        if event["event_type"] == "RankingOverallCalculado":
            self._entries = [_dict_a_entrada(entry) for entry in payload["entries"]]
            self._calculado = True

    @staticmethod
    def _parse_payload(payload: Any) -> dict[str, Any]:
        if isinstance(payload, str):
            return json.loads(payload)  # type: ignore[no-any-return]
        return payload  # type: ignore[return-value]


def _calcular_entries(
    rankings_por_disciplina: dict[Disciplina, list[EntradaRanking]],
    penalizacion_ausente: int | None,
) -> list[EntradaOverall]:
    """Aplica la fórmula posicional overall."""
    rankings_validos = _filtrar_rankings_validos(rankings_por_disciplina)
    if not rankings_validos:
        return []

    acumulado = _acumular_puntajes(rankings_validos, penalizacion_ausente)
    puntuados = _ordenar_puntuados(acumulado)

    entries: list[EntradaOverall] = []
    posicion_actual = 1
    for index, (atleta_id, detalle, puntaje) in enumerate(puntuados):
        if index > 0 and puntaje == puntuados[index - 1][2]:
            posicion = entries[-1].posicion
        else:
            posicion = posicion_actual

        entries.append(
            EntradaOverall(
                posicion=posicion,
                atleta_id=atleta_id,
                puntaje=puntaje,
                detalle=detalle,
                en_podio=posicion <= 3,
            )
        )
        posicion_actual = len(entries) + 1

    return entries


def _filtrar_rankings_validos(
    rankings_por_disciplina: dict[Disciplina, list[EntradaRanking]],
) -> dict[Disciplina, list[EntradaRanking]]:
    return {
        disciplina: entries for disciplina, entries in rankings_por_disciplina.items() if entries
    }


def _acumular_puntajes(
    rankings_validos: dict[Disciplina, list[EntradaRanking]],
    penalizacion_ausente: int | None,
) -> dict[UUID, dict[str, int]]:
    atletas = {entry.atleta_id for entries in rankings_validos.values() for entry in entries}
    acumulado: dict[UUID, dict[str, int]] = {atleta_id: {} for atleta_id in atletas}

    for disciplina, entries in rankings_validos.items():
        posiciones = {entry.atleta_id: entry.posicion for entry in entries}
        peor_posicion = _calcular_penalizacion(entries, penalizacion_ausente)
        for atleta_id in atletas:
            acumulado[atleta_id][disciplina.value] = posiciones.get(atleta_id, peor_posicion)
    return acumulado


def _calcular_penalizacion(entries: list[EntradaRanking], penalizacion_ausente: int | None) -> int:
    if penalizacion_ausente is not None:
        return penalizacion_ausente
    return max(entry.posicion for entry in entries) + 1


def _ordenar_puntuados(
    acumulado: dict[UUID, dict[str, int]],
) -> list[tuple[UUID, dict[str, int], int]]:
    return sorted(
        ((atleta_id, detalle, sum(detalle.values())) for atleta_id, detalle in acumulado.items()),
        key=lambda item: (item[2], str(item[0])),
    )


def _entrada_a_dict(entry: EntradaOverall) -> dict[str, Any]:
    """Serializa EntradaOverall a payload JSON."""
    return {
        "posicion": entry.posicion,
        "atleta_id": str(entry.atleta_id),
        "puntaje": entry.puntaje,
        "detalle": entry.detalle,
        "en_podio": entry.en_podio,
    }


def _dict_a_entrada(data: dict[str, Any]) -> EntradaOverall:
    """Deserializa payload a EntradaOverall."""
    return EntradaOverall(
        posicion=data["posicion"],
        atleta_id=UUID(data["atleta_id"]),
        puntaje=data["puntaje"],
        detalle=dict(data["detalle"]),
        en_podio=data["en_podio"],
    )
