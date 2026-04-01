"""Tests unitarios de exception_handlers — mapeo DomainError → RFC 7807 (ADR-012, ADR-013)."""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from competencia.api.exception_handlers import register_exception_handlers
from competencia.domain.exceptions import (
    DomainError,
    EstadoInvalidoParaLlamar,
    GrillaYaConfirmada,
    MotivoObligatorio,
)


@pytest.fixture
def app_con_handlers() -> FastAPI:
    """App mínima con exception handlers registrados y un endpoint que lanza DomainError."""
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/lanza-domain-error")
    def lanza_domain_error() -> None:
        raise DomainError("error genérico de dominio")

    @app.get("/lanza-estado-invalido")
    def lanza_estado_invalido() -> None:
        raise EstadoInvalidoParaLlamar("Performance no está en AnunciadaAP")

    @app.get("/lanza-grilla-confirmada")
    def lanza_grilla_confirmada() -> None:
        raise GrillaYaConfirmada("La grilla ya fue confirmada")

    @app.get("/lanza-motivo-obligatorio")
    def lanza_motivo_obligatorio() -> None:
        raise MotivoObligatorio("Tarjeta roja requiere motivo")

    return app


@pytest.fixture
def client(app_con_handlers: FastAPI) -> TestClient:
    return TestClient(app_con_handlers, raise_server_exceptions=False)


class TestDomainErrorHandler:
    def test_domain_error_retorna_422(self, client: TestClient) -> None:
        response = client.get("/lanza-domain-error")
        assert response.status_code == 422

    def test_domain_error_body_rfc7807(self, client: TestClient) -> None:
        response = client.get("/lanza-domain-error")
        body = response.json()
        assert body["type"] == "https://ataraxiadive.com/errors/domain-error"
        assert body["title"] == "Error de dominio"
        assert body["status"] == 422
        assert body["detail"] == "error genérico de dominio"

    def test_subclase_estado_invalido_retorna_422(self, client: TestClient) -> None:
        """Subclases de DomainError deben ser capturadas por el handler genérico."""
        response = client.get("/lanza-estado-invalido")
        assert response.status_code == 422
        assert "Performance no está en AnunciadaAP" in response.json()["detail"]

    def test_subclase_grilla_confirmada_retorna_422(self, client: TestClient) -> None:
        response = client.get("/lanza-grilla-confirmada")
        assert response.status_code == 422
        assert "La grilla ya fue confirmada" in response.json()["detail"]

    def test_subclase_motivo_obligatorio_retorna_422(self, client: TestClient) -> None:
        response = client.get("/lanza-motivo-obligatorio")
        assert response.status_code == 422
        assert "Tarjeta roja requiere motivo" in response.json()["detail"]

    def test_detail_contiene_mensaje_original(self, client: TestClient) -> None:
        """El campo detail debe incluir el str(exc) original sin modificar."""
        response = client.get("/lanza-domain-error")
        assert response.json()["detail"] == "error genérico de dominio"
