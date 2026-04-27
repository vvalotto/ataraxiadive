"""Aggregate RankingOverall — cálculo posicional multi-disciplina por torneo."""

from __future__ import annotations

import json
from decimal import Decimal
from typing import Any
from uuid import UUID

from registro.domain.value_objects.categoria import Categoria
from resultados.domain.events.ranking_overall_calculado import RankingOverallCalculado
from resultados.domain.value_objects.entrada_overall import EntradaOverall
from resultados.domain.value_objects.entrada_ranking import EntradaRanking
from shared.domain.base.aggregate_root import AggregateRoot
from shared.domain.value_objects.disciplina import Disciplina

_CATEGORIA_DEFAULT = Categoria.SENIOR_MASCULINO
_DOS_DECIMALES = Decimal("0.01")


class RankingOverall(AggregateRoot):
    """Aggregate raíz del ranking general por torneo.

    Stream ID: "ranking-overall-{torneo_id}"

    Regla de ordenamiento (US-5.6.4):
        puntos_overall = Σ puntos_disciplina (FAAS). Mayor es mejor.
        Atleta ausente en una disciplina aporta 0 puntos (INV-5.6.4-01).
        Empates comparten posición (INV-5.6.4-03).
        Solo calculable cuando todas las disciplinas tienen ranking (INV-5.6.4-04).
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
    ) -> list[EntradaOverall]:
        """Calcula y registra el ranking overall sumando puntos FAAS.

        Raises:
            DisciplinasNoFinalizadas: si alguna disciplina no tiene ranking calculado (INV-5.6.4-04).
        """
        _validar_disciplinas_finalizadas(rankings_por_disciplina)

        entries = _calcular_entries(rankings_por_disciplina)
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


# ── Helpers de dominio ────────────────────────────────────────────────────────


def _validar_disciplinas_finalizadas(
    rankings_por_disciplina: dict[Disciplina, list[EntradaRanking]],
) -> None:
    """INV-5.6.4-04: rechaza si alguna disciplina no tiene ranking calculado."""
    sin_finalizar = [d for d, e in rankings_por_disciplina.items() if not e]
    if sin_finalizar:
        from resultados.domain.exceptions import DisciplinasNoFinalizadas

        nombres = ", ".join(d.value for d in sin_finalizar)
        raise DisciplinasNoFinalizadas(
            f"Overall rechazado: disciplinas sin ranking finalizado: {nombres}"
        )


def _calcular_entries(
    rankings_por_disciplina: dict[Disciplina, list[EntradaRanking]],
) -> list[EntradaOverall]:
    """Suma puntos FAAS por atleta y disciplina, agrupa por Categoría."""
    entries: list[EntradaOverall] = []
    for categoria in sorted(_categorias_presentes(rankings_por_disciplina), key=lambda c: c.value):
        acumulado = _acumular_puntos_categoria(rankings_por_disciplina, categoria)
        entries.extend(_crear_entries_categoria(categoria, acumulado))
    return entries


def _categorias_presentes(
    rankings_por_disciplina: dict[Disciplina, list[EntradaRanking]],
) -> set[Categoria]:
    return {entry.categoria for entries in rankings_por_disciplina.values() for entry in entries}


def _acumular_puntos_categoria(
    rankings_por_disciplina: dict[Disciplina, list[EntradaRanking]],
    categoria: Categoria,
) -> dict[UUID, tuple[Decimal, dict[str, Decimal]]]:
    """Retorna {atleta_id: (puntos_total, {disciplina: puntos})} para la categoría."""
    atletas = {
        entry.atleta_id
        for entries in rankings_por_disciplina.values()
        for entry in entries
        if entry.categoria == categoria
    }
    detalle: dict[UUID, dict[str, Decimal]] = {a: {} for a in atletas}

    for disciplina, entries in rankings_por_disciplina.items():
        for entry in entries:
            if entry.categoria == categoria:
                detalle[entry.atleta_id][disciplina.value] = entry.puntos

    result: dict[UUID, tuple[Decimal, dict[str, Decimal]]] = {}
    for atleta_id, d in detalle.items():
        total = sum(d.values(), Decimal("0.00")).quantize(_DOS_DECIMALES)
        result[atleta_id] = (total, d)
    return result


def _crear_entries_categoria(
    categoria: Categoria,
    acumulado: dict[UUID, tuple[Decimal, dict[str, Decimal]]],
) -> list[EntradaOverall]:
    """Ordena por puntos_overall DESC y asigna posiciones con empates."""
    puntuados = sorted(
        acumulado.items(),
        key=lambda item: (-item[1][0], str(item[0])),
    )

    entries: list[EntradaOverall] = []
    posicion_actual = 1
    for i, (atleta_id, (puntos_overall, detalle)) in enumerate(puntuados):
        if i > 0 and puntos_overall == puntuados[i - 1][1][0]:
            posicion = entries[-1].posicion
        else:
            posicion = posicion_actual

        entries.append(
            EntradaOverall(
                posicion=posicion,
                atleta_id=atleta_id,
                categoria=categoria,
                puntos_overall=puntos_overall,
                detalle=detalle,
                en_podio=posicion <= 3,
            )
        )
        posicion_actual = len(entries) + 1
    return entries


def _entrada_a_dict(entry: EntradaOverall) -> dict[str, Any]:
    """Serializa EntradaOverall a payload JSON."""
    return {
        "posicion": entry.posicion,
        "atleta_id": str(entry.atleta_id),
        "categoria": entry.categoria.value,
        "puntos_overall": str(entry.puntos_overall),
        "detalle": {k: str(v) for k, v in entry.detalle.items()},
        "en_podio": entry.en_podio,
    }


def _dict_a_entrada(data: dict[str, Any]) -> EntradaOverall:
    """Deserializa payload a EntradaOverall. Soporta eventos legacy (sin puntos_overall)."""
    puntos_overall = Decimal(str(data.get("puntos_overall", "0.00"))).quantize(_DOS_DECIMALES)
    detalle_raw = data.get("detalle", {})
    detalle = {k: Decimal(str(v)).quantize(_DOS_DECIMALES) for k, v in detalle_raw.items()}
    return EntradaOverall(
        posicion=data["posicion"],
        atleta_id=UUID(data["atleta_id"]),
        categoria=Categoria(data.get("categoria", _CATEGORIA_DEFAULT.value)),
        puntos_overall=puntos_overall,
        detalle=detalle,
        en_podio=data["en_podio"],
    )
