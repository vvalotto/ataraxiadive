"""Command y Handler para CalcularRanking — US-2.4.2."""
from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from competencia.domain.ports.event_store_port import EventStorePort
from shared.domain.value_objects.disciplina import Disciplina
from shared.domain.value_objects.disciplina_descriptor import DisciplinaDescriptor
from resultados.infrastructure.repositories.disciplina_descriptor_adapter import (
    DisciplinaDescriptorAdapter,
)
from resultados.domain.aggregates.ranking_competencia import RankingCompetencia
from resultados.domain.ports.resultados_competencia_port import ResultadosCompetenciaPort


# ── Command ───────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class CalcularRankingCommand:
    """Comando para calcular el ranking de una disciplina.

    Attributes:
        competencia_id: Identificador de la competencia.
        disciplina: Disciplina cuyo ranking se calcula.
    """

    competencia_id: UUID
    disciplina: Disciplina


# ── Handler ───────────────────────────────────────────────────────────────────


class CalcularRankingHandler:
    """Handler del comando CalcularRanking.

    Orquesta:
    1. Obtener resultados finales via ACL (ResultadosCompetenciaPort).
    2. Construir RankingCompetencia aggregate.
    3. Calcular y persistir ResultadosCalculados en stream de BC Resultados.

    Args:
        ranking_store: Event Store del BC Resultados (data/resultados.db).
        resultados_port: ACL hacia BC Competencia.
        descriptor: Descriptor de disciplina para ordenamiento.
    """

    def __init__(
        self,
        ranking_store: EventStorePort,
        resultados_port: ResultadosCompetenciaPort,
        descriptor: DisciplinaDescriptor | None = None,
    ) -> None:
        self._ranking_store = ranking_store
        self._resultados_port = resultados_port
        self._descriptor = descriptor or DisciplinaDescriptorAdapter()

    async def handle(self, command: CalcularRankingCommand) -> None:
        """Ejecuta el comando CalcularRanking.

        Args:
            command: Datos del ranking a calcular.

        Raises:
            ResultadosIncompletos: Si no hay resultados para calcular.
        """
        resultados = await self._resultados_port.get_resultados_finales(
            command.competencia_id, command.disciplina
        )

        stream_id = _build_stream_id(command.competencia_id, command.disciplina)
        existing = await self._ranking_store.load(stream_id)

        ranking = RankingCompetencia.reconstitute(
            competencia_id=command.competencia_id,
            disciplina=command.disciplina,
            events=existing,
        )

        descriptor = self._descriptor.describe(command.disciplina)
        ranking.calcular(resultados, descriptor)

        for event in ranking.pull_events():
            await self._ranking_store.append(
                stream_id=stream_id,
                event_type=event.event_type,
                payload=event.to_payload(),
            )


# ── Helpers ───────────────────────────────────────────────────────────────────


def _build_stream_id(competencia_id: UUID, disciplina: Disciplina) -> str:
    """Construye el stream ID canónico para un RankingCompetencia."""
    return f"ranking-{competencia_id}-{disciplina.value}"
