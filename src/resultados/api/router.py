"""Router FastAPI del BC Resultados — endpoints de consulta de ranking."""
from __future__ import annotations

import os
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from shared.domain.value_objects.disciplina import Disciplina
from competencia.infrastructure.event_store.sqlite_event_store import SQLiteEventStore
from resultados.application.queries.obtener_ranking import (
    ObtenerRankingHandler,
    ObtenerRankingQuery,
)

router = APIRouter(prefix="/resultados", tags=["resultados"])


# ── Dependency providers ──────────────────────────────────────────────────────


def get_ranking_store() -> SQLiteEventStore:
    """Dependency: instancia del Event Store de BC Resultados."""
    db_path = os.getenv("RESULTADOS_DB_PATH", "data/resultados.db")
    return SQLiteEventStore(db_path)


def get_obtener_ranking_handler(
    ranking_store: Annotated[SQLiteEventStore, Depends(get_ranking_store)],
) -> ObtenerRankingHandler:
    """Dependency: handler de consulta de ranking."""
    return ObtenerRankingHandler(ranking_store)


ObtenerRankingHandlerDep = Annotated[
    ObtenerRankingHandler, Depends(get_obtener_ranking_handler)
]


# ── Endpoints ─────────────────────────────────────────────────────────────────


@router.get("/{competencia_id}/ranking", response_class=JSONResponse)
async def get_ranking(
    competencia_id: UUID,
    disciplina: Disciplina,
    handler: ObtenerRankingHandlerDep,
) -> JSONResponse:
    """Retorna el ranking calculado de la disciplina para la competencia.

    El ranking incluye posición, marca efectiva, tarjeta y flag de podio
    para cada atleta. Las performances DNS y tarjeta roja aparecen al final.

    Returns:
        JSON con competencia_id, disciplina, total y lista de entradas del ranking.
        Lista vacía si el ranking aún no fue calculado.
    """
    entradas = await handler.handle(
        ObtenerRankingQuery(competencia_id=competencia_id, disciplina=disciplina)
    )
    return JSONResponse(
        content={
            "competencia_id": str(competencia_id),
            "disciplina": disciplina.value,
            "total": len(entradas),
            "ranking": [
                {
                    "posicion": e.posicion,
                    "atleta_id": e.atleta_id,
                    "rp": e.rp,
                    "unidad": e.unidad,
                    "tarjeta": e.tarjeta,
                    "es_dns": e.es_dns,
                    "en_podio": e.en_podio,
                }
                for e in entradas
            ],
        },
        status_code=200,
    )
