"""
Script UAT — Recalcular rankings y overall para todas las disciplinas del torneo.

Uso cuando P-08/P-09 no se dispararon porque el callback on_finalizada no estaba
cableado en el router (fix aplicado post-seed). Ejecutar una sola vez.

Uso:
  uv run python tests/uat/sp6/recalcular_rankings.py --torneo-id <uuid>
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from uuid import UUID

sys.path.insert(0, "src")

from competencia.application.queries.obtener_competencias_por_torneo import (
    ObtenerCompetenciasPorTorneoHandler,
    ObtenerCompetenciasPorTorneoQuery,
)
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.infrastructure.repositories.disciplina_descriptor_adapter import (
    DisciplinaDescriptorAdapter,
)
from competencia.infrastructure.repositories.sqlite_competencias_por_torneo import (
    SQLiteCompetenciasPorTorneo,
)
from registro.domain.value_objects.categoria import Categoria
from resultados.domain.ports.resultados_competencia_port import AtletaCategoriaPort
from resultados.infrastructure.repositories.atleta_categoria_adapter import AtletaCategoriaAdapter
from resultados.infrastructure.repositories.resultados_competencia_adapter import (
    ResultadosCompetenciaAdapter,
)
from resultados.application.commands.calcular_overall import (
    CalcularOverallCommand,
    CalcularOverallHandler,
)
from resultados.application.commands.calcular_ranking import (
    CalcularRankingCommand,
    CalcularRankingHandler,
)
from resultados.domain.services.algoritmo_faas import AlgoritmoPuntajeFAAS
from shared.infrastructure.event_store.sqlite_event_store import SQLiteEventStore


class AtletaCategoriaAdapterConFallback(AtletaCategoriaPort):
    """Wrapper tolerante: atletas sin registro en BC Registro reciben SENIOR_MASCULINO."""

    def __init__(self) -> None:
        self._inner = AtletaCategoriaAdapter()

    async def get_categoria(self, atleta_id: UUID) -> Categoria:
        try:
            return await self._inner.get_categoria(atleta_id)
        except ValueError:
            print(f"  ⚠ Atleta {atleta_id} sin registro — asignando SENIOR_MASCULINO")
            return Categoria("SENIOR_MASCULINO")


async def main(torneo_id: UUID) -> None:
    competencia_db = os.getenv("COMPETENCIA_DB_PATH", "data/competencia.db")
    resultados_db = os.getenv("RESULTADOS_DB_PATH", "data/resultados.db")
    torneo_db = os.getenv("TORNEO_DB_PATH", "data/torneo.db")

    competencia_store = SQLiteEventStore(competencia_db)
    ranking_store = SQLiteEventStore(resultados_db)

    competencias = await ObtenerCompetenciasPorTorneoHandler(SQLiteCompetenciasPorTorneo()).handle(
        ObtenerCompetenciasPorTorneoQuery(torneo_id=torneo_id)
    )

    print(f"\n=== Recalcular rankings — torneo {torneo_id} ===\n")
    print(f"  Disciplinas encontradas: {[c.disciplina for c in competencias]}\n")

    acl = ResultadosCompetenciaAdapter(competencia_store)
    atleta_categoria_acl = AtletaCategoriaAdapterConFallback()
    descriptor = DisciplinaDescriptorAdapter()
    ranking_handler = CalcularRankingHandler(
        ranking_store, acl, atleta_categoria_acl, descriptor, algoritmo=AlgoritmoPuntajeFAAS()
    )

    for comp in competencias:
        disciplina = Disciplina(comp.disciplina)
        try:
            await ranking_handler.handle(
                CalcularRankingCommand(
                    competencia_id=comp.competencia_id,
                    disciplina=disciplina,
                )
            )
            print(f"  ✓ {comp.disciplina} — ranking calculado")
        except Exception as exc:
            print(f"  ✗ {comp.disciplina} — error: {exc}")

    print("\n  Calculando overall...")
    disciplinas = [Disciplina(c.disciplina) for c in competencias]
    overall_handler = CalcularOverallHandler(ranking_store, SQLiteCompetenciasPorTorneo())
    try:
        await overall_handler.handle(
            CalcularOverallCommand(torneo_id=torneo_id, disciplinas=disciplinas)
        )
        print("  ✓ Overall calculado")
    except Exception as exc:
        print(f"  ✗ Overall — error: {exc}")

    print("\n=== Listo. Recargá la página de Podios. ===\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--torneo-id", required=True)
    args = parser.parse_args()
    asyncio.run(main(UUID(args.torneo_id)))
