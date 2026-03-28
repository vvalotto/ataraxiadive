"""AtaraxiaDive — FastAPI application entry point (composition root)."""
import os
from typing import Awaitable, Callable
from uuid import UUID

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from competencia.api.exception_handlers import register_exception_handlers
from competencia.api.router import router as competencia_router
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.infrastructure.event_store.sqlite_event_store import SQLiteEventStore
from competencia.infrastructure.repositories.disciplina_descriptor_adapter import (
    DisciplinaDescriptorAdapter,
)
from resultados.application.commands.calcular_ranking import (
    CalcularRankingCommand,
    CalcularRankingHandler,
)
from resultados.api.router import router as resultados_router
from resultados.infrastructure.repositories.resultados_competencia_adapter import (
    ResultadosCompetenciaAdapter,
)


def build_on_finalizada_callback(
    competencia_event_store: SQLiteEventStore,
) -> Callable[[UUID, Disciplina], Awaitable[None]]:
    """Callback P-08 → CalcularRanking. Composition root del cableado cross-BC (ADR-006)."""
    ranking_db_path = os.getenv("RESULTADOS_DB_PATH", "data/resultados.db")
    disciplina_descriptor = DisciplinaDescriptorAdapter()

    async def _on_finalizada(competencia_id: UUID, disciplina: Disciplina) -> None:
        ranking_store = SQLiteEventStore(ranking_db_path)
        acl = ResultadosCompetenciaAdapter(competencia_event_store)
        handler = CalcularRankingHandler(ranking_store, acl, disciplina_descriptor)
        await handler.handle(CalcularRankingCommand(
            competencia_id=competencia_id,
            disciplina=disciplina,
        ))

    return _on_finalizada


app = FastAPI(title="AtaraxiaDive", version="0.1.0")

app.include_router(competencia_router)
app.include_router(resultados_router)
register_exception_handlers(app)


@app.get("/health", response_class=JSONResponse)
async def health_check() -> dict[str, str]:
    """Health-check endpoint — verifica que la aplicación está activa."""
    return {"status": "ok"}
