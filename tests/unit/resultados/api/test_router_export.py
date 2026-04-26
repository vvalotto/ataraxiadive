"""Tests HTTP del router de resultados para exportación CSV/JSON."""

from __future__ import annotations

from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient

from identidad.api.dependencies import get_current_user
from resultados.application.queries.exportar_resultados import (
    ExportDisciplinaDTO,
    ExportDisciplinaEntradaDTO,
    ExportOverallEntradaDTO,
    ExportResultadosDTO,
)
from resultados.api.router import (
    get_exportar_resultados_handler,
    router,
)
from resultados.domain.exceptions import TorneoNoEncontrado


class _HandlerOk:
    async def handle(self, _query):
        return ExportResultadosDTO(
            torneo_id=str(uuid4()),
            torneo_nombre="Open BA 2026",
            exportado_en="2026-04-16T18:00:00Z",
            disciplinas=[
                ExportDisciplinaDTO(
                    disciplina="DNF",
                    estado="Finalizada",
                    hash_sha256="a3f7c2",
                    ranking=[
                        ExportDisciplinaEntradaDTO(
                            posicion=1,
                            atleta_id=str(uuid4()),
                            atleta_nombre="Martin Garcia",
                            categoria="SENIOR_MASCULINO",
                            club="Club Nautico",
                            ap="60",
                            rp="58",
                            tarjeta="Blanca",
                            penalizaciones=0,
                            puntos=1,
                        )
                    ],
                )
            ],
            overall=[
                ExportOverallEntradaDTO(
                    posicion=1,
                    atleta_id=str(uuid4()),
                    atleta_nombre="Martin Garcia",
                    categoria="SENIOR_MASCULINO",
                    club="Club Nautico",
                    puntos_totales=3,
                )
            ],
        )


class _Handler404:
    async def handle(self, _query):
        raise TorneoNoEncontrado("Torneo no encontrado")


def _build_app(handler, rol: str = "ORGANIZADOR") -> TestClient:
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_exportar_resultados_handler] = lambda: handler
    app.dependency_overrides[get_current_user] = lambda: {
        "sub": "test-user",
        "email": "test@test.com",
        "rol": rol,
    }
    return TestClient(app)


def test_export_json_devuelve_attachment_y_secciones() -> None:
    torneo_id = uuid4()
    client = _build_app(_HandlerOk())

    response = client.get(f"/resultados/{torneo_id}/export?format=json")

    assert response.status_code == 200
    assert (
        response.headers["content-disposition"]
        == f'attachment; filename="resultados-{torneo_id}.json"'
    )
    payload = response.json()
    assert "disciplinas" in payload
    assert "overall" in payload
    assert payload["disciplinas"][0]["hash_sha256"] == "a3f7c2"


def test_export_csv_devuelve_attachment_y_header_con_punto_y_coma() -> None:
    torneo_id = uuid4()
    client = _build_app(_HandlerOk())

    response = client.get(f"/resultados/{torneo_id}/export?format=csv")

    assert response.status_code == 200
    assert (
        response.headers["content-disposition"]
        == f'attachment; filename="resultados-{torneo_id}.csv"'
    )
    primera_linea = response.text.splitlines()[0]
    assert (
        primera_linea
        == "disciplina;posicion;atleta_nombre;categoria;club;ap;rp;tarjeta;penalizaciones;puntos"
    )


def test_export_format_invalido_devuelve_400() -> None:
    torneo_id = uuid4()
    client = _build_app(_HandlerOk())

    response = client.get(f"/resultados/{torneo_id}/export?format=xlsx")

    assert response.status_code == 400
    assert "csv" in response.json()["detail"]
    assert "json" in response.json()["detail"]


def test_export_torneo_inexistente_devuelve_404() -> None:
    torneo_id = uuid4()
    client = _build_app(_Handler404())

    response = client.get(f"/resultados/{torneo_id}/export?format=json")

    assert response.status_code == 404


def test_export_juez_no_puede_acceder() -> None:
    torneo_id = uuid4()
    client = _build_app(_HandlerOk(), rol="JUEZ")

    response = client.get(f"/resultados/{torneo_id}/export?format=json")

    assert response.status_code == 403
