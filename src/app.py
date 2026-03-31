"""AtaraxiaDive — FastAPI application entry point (composition root)."""
import os
from typing import Awaitable, Callable
from uuid import UUID

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from competencia.api.exception_handlers import register_exception_handlers
from competencia.api.router import router as competencia_router
from resultados.api.router import router as resultados_router
from identidad.api.router import router as identidad_router
from registro.api.router import router as registro_router
from torneo.api.exception_handlers import register_torneo_exception_handlers
from torneo.api.router import router as torneo_router
from resultados.application.commands.calcular_ranking import (
    CalcularRankingCommand,
    CalcularRankingHandler,
)
from resultados.infrastructure.repositories.disciplina_descriptor_adapter import (
    DisciplinaDescriptorAdapter,
)
from resultados.infrastructure.repositories.resultados_competencia_adapter import (
    ResultadosCompetenciaAdapter,
)
from shared.domain.value_objects.disciplina import Disciplina
from shared.infrastructure.event_store.sqlite_event_store import SQLiteEventStore

app = FastAPI(title="AtaraxiaDive", version="0.1.0")

app.include_router(identidad_router)
app.include_router(registro_router)
app.include_router(competencia_router)
app.include_router(resultados_router)
app.include_router(torneo_router)
register_exception_handlers(app)
register_torneo_exception_handlers(app)


# ── Política P-08: CompetenciaFinalizada → CalcularRanking ────────────────────
# El callback se construye aquí (composition root) y se inyectará a los handlers
# de competencia que lo necesiten (AsignarTarjetaHandler, RegistrarDNSHandler)
# cuando se agreguen los endpoints HTTP de performance en SP3+.


def build_on_finalizada_callback(
    competencia_event_store: SQLiteEventStore,
) -> Callable[[UUID, Disciplina], Awaitable[None]]:
    """Construye el callback P-08 → CalcularRanking.

    Args:
        competencia_event_store: Event Store del BC Competencia para que el ACL
            pueda leer las performances al calcular el ranking.

    Returns:
        Callable async (competencia_id, disciplina) → None que dispara CalcularRanking.
    """
    ranking_db_path = os.getenv("RESULTADOS_DB_PATH", "data/resultados.db")

    async def _on_finalizada(competencia_id: UUID, disciplina: Disciplina) -> None:
        ranking_store = SQLiteEventStore(ranking_db_path)
        acl = ResultadosCompetenciaAdapter(competencia_event_store)
        descriptor = DisciplinaDescriptorAdapter()
        handler = CalcularRankingHandler(ranking_store, acl, descriptor)
        await handler.handle(CalcularRankingCommand(
            competencia_id=competencia_id,
            disciplina=disciplina,
        ))

    return _on_finalizada


@app.get("/health", response_class=JSONResponse)
async def health_check() -> dict[str, str]:
    """Health-check endpoint — verifica que la aplicación está activa."""
    return {"status": "ok"}
