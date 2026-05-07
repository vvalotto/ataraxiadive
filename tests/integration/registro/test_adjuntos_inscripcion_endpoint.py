from __future__ import annotations

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app import app
from identidad.api.dependencies import get_current_user
from registro.domain.aggregates.inscripcion import Inscripcion
from registro.infrastructure.repositories.sqlite_inscripcion_repository import (
    SQLiteInscripcionRepository,
)
from shared.domain.value_objects.disciplina import Disciplina


@pytest.fixture
def adjuntos_context(tmp_path, monkeypatch):
    registro_db = tmp_path / "registro.db"
    monkeypatch.setenv("REGISTRO_DB_PATH", str(registro_db))
    monkeypatch.chdir(tmp_path)

    atleta_id = uuid4()
    torneo_id = uuid4()
    inscripcion = Inscripcion(
        atleta_id=atleta_id,
        torneo_id=torneo_id,
        disciplinas=frozenset({Disciplina.DYN}),
    )
    repo = SQLiteInscripcionRepository(str(registro_db))

    import asyncio

    asyncio.run(repo.save(inscripcion))

    app.dependency_overrides[get_current_user] = lambda: {
        "sub": str(atleta_id),
        "email": "atleta@ataraxiadive.io",
        "rol": "ATLETA",
    }

    yield {
        "client": TestClient(app),
        "repo": repo,
        "inscripcion_id": inscripcion.inscripcion_id,
    }

    app.dependency_overrides.clear()


def test_post_apto_medico_persiste_path(adjuntos_context) -> None:
    response = adjuntos_context["client"].post(
        f"/registro/inscripciones/{adjuntos_context['inscripcion_id']}/apto-medico",
        files={"archivo": ("apto.pdf", b"%PDF-1.4", "application/pdf")},
    )

    assert response.status_code == 200
    assert response.json()["path"].endswith("/apto_medico.pdf")

    import asyncio

    found = asyncio.run(adjuntos_context["repo"].find_by_id(adjuntos_context["inscripcion_id"]))
    assert found is not None
    assert found.apto_medico_path == response.json()["path"]


def test_post_constancia_pago_persiste_path(adjuntos_context) -> None:
    response = adjuntos_context["client"].post(
        f"/registro/inscripciones/{adjuntos_context['inscripcion_id']}/constancia-pago",
        files={"archivo": ("pago.pdf", b"%PDF-1.4", "application/pdf")},
    )

    assert response.status_code == 200
    assert response.json()["path"].endswith("/constancia_pago.pdf")

    import asyncio

    found = asyncio.run(adjuntos_context["repo"].find_by_id(adjuntos_context["inscripcion_id"]))
    assert found is not None
    assert found.constancia_pago_path == response.json()["path"]


def test_post_adjunto_rechaza_archivo_mayor_a_10mb(adjuntos_context) -> None:
    response = adjuntos_context["client"].post(
        f"/registro/inscripciones/{adjuntos_context['inscripcion_id']}/apto-medico",
        files={"archivo": ("grande.pdf", b"x" * (10 * 1024 * 1024 + 1), "application/pdf")},
    )

    assert response.status_code == 413


def test_post_adjunto_retorna_404_para_inscripcion_inexistente(adjuntos_context) -> None:
    response = adjuntos_context["client"].post(
        f"/registro/inscripciones/{uuid4()}/apto-medico",
        files={"archivo": ("apto.pdf", b"%PDF-1.4", "application/pdf")},
    )

    assert response.status_code == 404
