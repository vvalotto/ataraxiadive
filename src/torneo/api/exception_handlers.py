from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from registro.domain.exceptions import APIncompletoParaPreparacion
from torneo.domain.exceptions import (
    DisciplinaObsoleta,
    EjecucionNoPermitida,
    PremiacionNoPermitida,
    TorneoCerrado,
    TorneoNoEncontrado,
    TransicionEstadoInvalida,
)


def register_torneo_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(APIncompletoParaPreparacion)
    async def ap_incompleto_para_preparacion_handler(
        request: Request, exc: APIncompletoParaPreparacion
    ) -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content={
                "type": "https://ataraxiadive.com/errors/ap-incompleto-para-preparacion",
                "title": "No se puede cerrar inscripción",
                "status": 409,
                "detail": str(exc),
            },
        )

    @app.exception_handler(TorneoNoEncontrado)
    async def torneo_no_encontrado_handler(
        request: Request, exc: TorneoNoEncontrado
    ) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={
                "type": "https://ataraxiadive.com/errors/torneo-no-encontrado",
                "title": "Torneo no encontrado",
                "status": 404,
                "detail": str(exc),
            },
        )

    @app.exception_handler(TransicionEstadoInvalida)
    async def transicion_invalida_handler(
        request: Request, exc: TransicionEstadoInvalida
    ) -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content={
                "type": "https://ataraxiadive.com/errors/transicion-invalida",
                "title": "Transición de estado inválida",
                "status": 409,
                "detail": str(exc),
            },
        )

    @app.exception_handler(PremiacionNoPermitida)
    async def premiacion_no_permitida_handler(
        request: Request, exc: PremiacionNoPermitida
    ) -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content={
                "type": "https://ataraxiadive.com/errors/premiacion-no-permitida",
                "title": "Premiación no permitida",
                "status": 409,
                "detail": str(exc),
            },
        )

    @app.exception_handler(EjecucionNoPermitida)
    async def ejecucion_no_permitida_handler(
        request: Request, exc: EjecucionNoPermitida
    ) -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content={
                "type": "https://ataraxiadive.com/errors/ejecucion-no-permitida",
                "title": "Ejecución no permitida",
                "status": 409,
                "detail": str(exc),
            },
        )

    @app.exception_handler(TorneoCerrado)
    async def torneo_cerrado_handler(request: Request, exc: TorneoCerrado) -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content={
                "type": "https://ataraxiadive.com/errors/torneo-cerrado",
                "title": "Torneo cerrado",
                "status": 409,
                "detail": str(exc),
            },
        )

    @app.exception_handler(DisciplinaObsoleta)
    async def disciplina_obsoleta_handler(
        request: Request, exc: DisciplinaObsoleta
    ) -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content={
                "type": "https://ataraxiadive.com/errors/disciplina-obsoleta",
                "title": "Disciplina obsoleta",
                "status": 409,
                "detail": str(exc),
            },
        )
