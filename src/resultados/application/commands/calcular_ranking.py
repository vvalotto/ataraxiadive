"""Command y Handler para CalcularRanking — US-2.4.2."""

from __future__ import annotations

from dataclasses import replace
from dataclasses import dataclass
from uuid import UUID

from registro.domain.value_objects.categoria import Categoria
from shared.domain.ports.event_store_port import EventStorePort
from shared.domain.value_objects.disciplina import Disciplina
from shared.domain.value_objects.disciplina_descriptor import DisciplinaDescriptor
from resultados.infrastructure.repositories.disciplina_descriptor_adapter import (
    DisciplinaDescriptorAdapter,
)
from resultados.domain.aggregates.ranking_competencia import RankingCompetencia
from resultados.domain.ports.algoritmo_puntaje import AlgoritmoPuntaje
from resultados.domain.ports.resultados_competencia_port import (
    AtletaCategoriaPort,
    ResultadoFinal,
    ResultadosCompetenciaPort,
)

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
        atleta_categoria_port: AtletaCategoriaPort | None = None,
        descriptor: DisciplinaDescriptor | None = None,
        algoritmo: AlgoritmoPuntaje | None = None,
    ) -> None:
        self._ranking_store = ranking_store
        self._resultados_port = resultados_port
        self._atleta_categoria_port = atleta_categoria_port or _CategoriaFallbackPort()
        self._descriptor = descriptor or DisciplinaDescriptorAdapter()
        self._algoritmo = algoritmo

    async def handle(self, command: CalcularRankingCommand) -> None:
        """Ejecuta el comando CalcularRanking.

        Args:
            command: Datos del ranking a calcular.

        Raises:
            ResultadosIncompletos: Si no hay resultados para calcular.
        """
        resultados_crudos = await self._resultados_port.get_resultados_finales(
            command.competencia_id, command.disciplina
        )
        resultados = await self._enriquecer_con_categoria(resultados_crudos)

        stream_id = _build_stream_id(command.competencia_id, command.disciplina)
        existing = await self._ranking_store.load(stream_id)

        ranking = RankingCompetencia.reconstitute(
            competencia_id=command.competencia_id,
            disciplina=command.disciplina,
            events=existing,
        )

        ranking.calcular(resultados, self._algoritmo)

        for event in ranking.pull_events():
            await self._ranking_store.append(
                stream_id=stream_id,
                event_type=event.event_type,
                payload=event.to_payload(),
            )

    async def _enriquecer_con_categoria(
        self,
        resultados: list[ResultadoFinal],
    ) -> list[ResultadoFinal]:
        enriquecidos: list[ResultadoFinal] = []
        for resultado in resultados:
            categoria = await self._atleta_categoria_port.get_categoria(resultado.atleta_id)
            enriquecidos.append(replace(resultado, categoria=categoria))
        return enriquecidos


class _CategoriaFallbackPort(AtletaCategoriaPort):
    """Fallback para tests/unit legacy que no inyectan el ACL real."""

    async def get_categoria(self, atleta_id: UUID) -> Categoria:
        return Categoria.SENIOR_MASCULINO


# ── Helpers ───────────────────────────────────────────────────────────────────


def _build_stream_id(competencia_id: UUID, disciplina: Disciplina) -> str:
    """Construye el stream ID canónico para un RankingCompetencia."""
    return f"ranking-{competencia_id}-{disciplina.value}"
