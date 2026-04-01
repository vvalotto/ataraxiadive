"""Exception handlers del BC Competencia — mapeo DomainError → RFC 7807 (ADR-012, ADR-013)."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from competencia.domain.exceptions import DomainError


def register_exception_handlers(app: FastAPI) -> None:
    """Registra los exception handlers del BC Competencia en la aplicación FastAPI.

    Mapea DomainError (y cualquier subclase) a HTTP 422 con body RFC 7807.
    Para errores específicos que requieren un status distinto (404, 409),
    registrar handlers adicionales con mayor especificidad.
    """

    @app.exception_handler(DomainError)
    async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "type": "https://ataraxiadive.com/errors/domain-error",
                "title": "Error de dominio",
                "status": 422,
                "detail": str(exc),
            },
        )
