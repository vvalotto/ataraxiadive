"""Router FastAPI del BC Resultados — endpoints de consulta de ranking."""

from __future__ import annotations

import csv
import io
import os
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, Response

from competencia.infrastructure.repositories.sqlite_competencias_por_torneo import (
    SQLiteCompetenciasPorTorneo,
)
from resultados.application.queries.exportar_resultados import (
    ExportResultadosDTO,
    ExportarResultadosHandler,
    ExportarResultadosQuery,
)
from shared.domain.value_objects.disciplina import Disciplina
from shared.infrastructure.event_store.sqlite_event_store import SQLiteEventStore
from shared.api.dependencies import OrganizadorDep
from torneo.infrastructure.repositories.sqlite_torneo_repository import SQLiteTorneoRepository
from resultados.application.queries.obtener_ranking import (
    ObtenerRankingHandler,
    ObtenerRankingQuery,
)
from resultados.application.queries.obtener_overall import (
    ObtenerOverallHandler,
    ObtenerOverallQuery,
)
from resultados.domain.exceptions import TorneoNoEncontrado
from resultados.infrastructure.repositories.atleta_info_adapter import AtletaInfoAdapter

router = APIRouter(prefix="/resultados", tags=["resultados"])


# ── Dependency providers ──────────────────────────────────────────────────────


def get_ranking_store() -> SQLiteEventStore:
    """Dependency: instancia del Event Store de BC Resultados."""
    db_path = os.getenv("RESULTADOS_DB_PATH", "data/resultados.db")
    return SQLiteEventStore(db_path)


def get_competencia_store() -> SQLiteEventStore:
    """Dependency: Event Store del BC Competencia."""
    db_path = os.getenv("COMPETENCIA_DB_PATH", "data/competencia.db")
    return SQLiteEventStore(db_path)


def get_competencias_por_torneo_projection() -> SQLiteCompetenciasPorTorneo:
    """Dependency: proyección de competencias por torneo."""
    return SQLiteCompetenciasPorTorneo()


def get_torneo_repository() -> SQLiteTorneoRepository:
    """Dependency: repositorio SQLite del BC Torneo."""
    return SQLiteTorneoRepository()


def get_atleta_info_adapter() -> AtletaInfoAdapter:
    """Dependency: ACL a Registro para nombre, categoría y club."""
    return AtletaInfoAdapter()


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


def get_exportar_resultados_handler(
    ranking_store: Annotated[SQLiteEventStore, Depends(get_ranking_store)],
    competencia_store: Annotated[SQLiteEventStore, Depends(get_competencia_store)],
    competencias_por_torneo: Annotated[
        SQLiteCompetenciasPorTorneo, Depends(get_competencias_por_torneo_projection)
    ],
    torneo_repo: Annotated[SQLiteTorneoRepository, Depends(get_torneo_repository)],
    atleta_info_adapter: Annotated[AtletaInfoAdapter, Depends(get_atleta_info_adapter)],
) -> ExportarResultadosHandler:
    """Dependency: handler de exportación consolidada."""
    return ExportarResultadosHandler(
        ranking_store=ranking_store,
        competencia_store=competencia_store,
        competencias_por_torneo=competencias_por_torneo,
        torneo_repo=torneo_repo,
        atleta_info_adapter=atleta_info_adapter,
    )


ExportarResultadosHandlerDep = Annotated[
    ExportarResultadosHandler, Depends(get_exportar_resultados_handler)
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
                            "puntos": e.puntos,
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
                            "puntos_overall": str(e.puntos_overall),
                            "detalle": {k: str(v) for k, v in e.detalle.items()},
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


@router.get("/{torneo_id}/export")
async def get_export_resultados(
    torneo_id: UUID,
    format: str,
    handler: ExportarResultadosHandlerDep,
    _: OrganizadorDep,
) -> Response:
    """Exporta los resultados completos del torneo en CSV o JSON."""
    if format not in {"csv", "json"}:
        return JSONResponse(
            status_code=400,
            content={"detail": 'Formato inválido. Usar "csv" o "json"'},
        )

    try:
        exportacion = await handler.handle(ExportarResultadosQuery(torneo_id=torneo_id))
    except TorneoNoEncontrado as exc:
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    filename = f"resultados-{torneo_id}.{format}"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}

    if format == "json":
        return JSONResponse(
            status_code=200,
            content=_exportacion_a_json(exportacion),
            headers=headers,
        )

    return Response(
        status_code=200,
        content=_exportacion_a_csv(exportacion),
        headers=headers,
        media_type="text/csv; charset=utf-8",
    )


def _exportacion_a_json(exportacion: ExportResultadosDTO) -> dict[str, object]:
    disciplinas = []
    for disciplina in exportacion.disciplinas:
        bloque: dict[str, object] = {
            "disciplina": disciplina.disciplina,
            "estado": disciplina.estado,
            "ranking": [
                {
                    "posicion": entry.posicion,
                    "atleta_id": entry.atleta_id,
                    "atleta_nombre": entry.atleta_nombre,
                    "categoria": entry.categoria,
                    "club": entry.club,
                    "ap": entry.ap,
                    "rp": entry.rp,
                    "tarjeta": entry.tarjeta,
                    "penalizaciones": entry.penalizaciones,
                    "puntos": entry.puntos,
                }
                for entry in disciplina.ranking
            ],
        }
        if disciplina.hash_sha256 is not None:
            bloque["hash_sha256"] = disciplina.hash_sha256
        disciplinas.append(bloque)

    return {
        "torneo_id": exportacion.torneo_id,
        "torneo_nombre": exportacion.torneo_nombre,
        "exportado_en": exportacion.exportado_en,
        "disciplinas": disciplinas,
        "overall": [
            {
                "posicion": entry.posicion,
                "atleta_id": entry.atleta_id,
                "atleta_nombre": entry.atleta_nombre,
                "categoria": entry.categoria,
                "club": entry.club,
                "puntos_totales": str(entry.puntos_totales),
            }
            for entry in exportacion.overall
        ],
    }


def _exportacion_a_csv(exportacion: ExportResultadosDTO) -> str:
    output = io.StringIO()
    writer = csv.writer(output, delimiter=";")
    writer.writerow(
        [
            "disciplina",
            "posicion",
            "atleta_nombre",
            "categoria",
            "club",
            "ap",
            "rp",
            "tarjeta",
            "penalizaciones",
            "puntos",
        ]
    )

    for disciplina in exportacion.disciplinas:
        for entry in disciplina.ranking:
            writer.writerow(
                [
                    disciplina.disciplina,
                    entry.posicion,
                    entry.atleta_nombre,
                    entry.categoria,
                    entry.club,
                    entry.ap or "",
                    entry.rp or "",
                    entry.tarjeta,
                    entry.penalizaciones,
                    entry.puntos,
                ]
            )

    for entry in exportacion.overall:
        writer.writerow(
            [
                "Overall",
                entry.posicion,
                entry.atleta_nombre,
                entry.categoria,
                entry.club,
                "",
                "",
                "",
                0,
                entry.puntos_totales,
            ]
        )

    return output.getvalue()
