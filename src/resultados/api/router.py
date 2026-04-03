"""Router FastAPI del BC Resultados — endpoints de consulta de ranking."""

from __future__ import annotations

import os
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from shared.domain.value_objects.disciplina import Disciplina
from shared.infrastructure.event_store.sqlite_event_store import SQLiteEventStore
from resultados.application.queries.obtener_ranking import (
    ObtenerRankingHandler,
    ObtenerRankingQuery,
)
from resultados.application.queries.obtener_overall import (
    ObtenerOverallHandler,
    ObtenerOverallQuery,
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


ObtenerRankingHandlerDep = Annotated[ObtenerRankingHandler, Depends(get_obtener_ranking_handler)]


def get_obtener_overall_handler(
    ranking_store: Annotated[SQLiteEventStore, Depends(get_ranking_store)],
) -> ObtenerOverallHandler:
    """Dependency: handler de consulta de overall."""
    return ObtenerOverallHandler(ranking_store)


ObtenerOverallHandlerDep = Annotated[ObtenerOverallHandler, Depends(get_obtener_overall_handler)]


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
        JSON agrupado por categoría.
    """
    rankings = await handler.handle(
        ObtenerRankingQuery(competencia_id=competencia_id, disciplina=disciplina)
    )
    return JSONResponse(
        content={
            "calculado": len(rankings) > 0,
            "rankings": [
                {
                    "categoria": grupo.categoria,
                    "entradas": [
                        {
                            "posicion": e.posicion,
                            "atleta_id": e.atleta_id,
                            "rp": e.rp,
                            "unidad": e.unidad,
                            "tarjeta": e.tarjeta,
                            "es_dns": e.es_dns,
                            "en_podio": e.en_podio,
                        }
                        for e in grupo.entradas
                    ],
                }
                for grupo in rankings
            ],
        },
        status_code=200,
    )


@router.get("/{torneo_id}/overall", response_class=JSONResponse)
async def get_overall(
    torneo_id: UUID,
    handler: ObtenerOverallHandlerDep,
) -> JSONResponse:
    """Retorna el ranking overall calculado del torneo.

    Returns:
        JSON agrupado por categoría.
    """
    rankings = await handler.handle(ObtenerOverallQuery(torneo_id=torneo_id))
    return JSONResponse(
        content={
            "calculado": len(rankings) > 0,
            "rankings": [
                {
                    "categoria": grupo.categoria,
                    "entradas": [
                        {
                            "posicion": e.posicion,
                            "atleta_id": e.atleta_id,
                            "puntaje": e.puntaje,
                            "detalle": e.detalle,
                            "en_podio": e.en_podio,
                        }
                        for e in grupo.entradas
                    ],
                }
                for grupo in rankings
            ],
        },
        status_code=200,
    )
