from __future__ import annotations

import asyncio
from datetime import date
from typing import Any
from uuid import UUID, uuid4

import aiosqlite
import pytest
from fastapi.testclient import TestClient

from app import app, build_on_inscripcion_confirmada_callback
from identidad.api.dependencies import get_current_user
from notificaciones.application.commands.enviar_notificacion import EnviarNotificacionHandler
from notificaciones.application.commands.solicitar_envio import SolicitarEnvioHandler
from notificaciones.application.policies.politica_p10 import PoliticaP10Handler
from notificaciones.infrastructure.event_store.sqlite_notificacion_event_store import (
    SQLiteNotificacionEventStore,
)
from notificaciones.infrastructure.repositories.sqlite_notificacion_repository import (
    SQLiteNotificacionRepository,
)
from notificaciones.infrastructure.templates.inscripcion_confirmada_template import (
    InscripcionConfirmadaTemplate,
)
from registro.api.router import configure_inscripcion_notificaciones
from registro.domain.aggregates.atleta import Atleta
from registro.domain.aggregates.inscripcion import Inscripcion
from registro.domain.value_objects.categoria import Categoria
from registro.infrastructure.repositories.sqlite_atleta_repository import SQLiteAtletaRepository
from shared.domain.value_objects.disciplina import Disciplina
from torneo.domain.aggregates.torneo import Torneo
from torneo.domain.value_objects.entidad_organizadora import EntidadOrganizadora
from torneo.domain.value_objects.sede import Sede
from torneo.infrastructure.repositories.sqlite_torneo_repository import SQLiteTorneoRepository


class FakeEmailPort:
    def __init__(self) -> None:
        self.sent = 0
        self.messages: list[dict[str, str]] = []

    async def enviar(self, destinatario, contenido) -> str:
        self.sent += 1
        self.messages.append(
            {
                "to": destinatario.email,
                "subject": contenido.asunto,
                "body": contenido.cuerpo_texto,
            }
        )
        return f"provider-{self.sent}"


@pytest.fixture
def p10_endpoint_context(tmp_path, monkeypatch):
    registro_db = tmp_path / "registro.db"
    torneo_db = tmp_path / "torneo.db"
    notificaciones_db = tmp_path / "notificaciones.db"
    monkeypatch.setenv("REGISTRO_DB_PATH", str(registro_db))
    monkeypatch.setenv("TORNEO_DB_PATH", str(torneo_db))
    monkeypatch.setenv("NOTIFICACIONES_DB_PATH", str(notificaciones_db))

    atleta_id = uuid4()
    torneo_id = uuid4()
    atleta_repo = SQLiteAtletaRepository(str(registro_db))
    torneo_repo = SQLiteTorneoRepository(str(torneo_db))
    email = FakeEmailPort()
    notificaciones_repo = SQLiteNotificacionRepository(
        SQLiteNotificacionEventStore(str(notificaciones_db))
    )
    p10 = PoliticaP10Handler(
        repository=notificaciones_repo,
        solicitar_envio_handler=SolicitarEnvioHandler(notificaciones_repo),
        enviar_notificacion_handler=EnviarNotificacionHandler(notificaciones_repo, email),
        template=InscripcionConfirmadaTemplate(),
    )

    async def _seed() -> None:
        await atleta_repo.save(
            Atleta(
                atleta_id=atleta_id,
                nombre="Ana",
                apellido="Paz",
                email="ana.paz@ataraxiadive.io",
                fecha_nacimiento=date(1992, 4, 12),
                categoria=Categoria.SENIOR_FEMENINO,
                club="Azul",
            )
        )
        torneo = Torneo(
            torneo_id=torneo_id,
            nombre="Open BA 2026",
            descripcion="Torneo de apnea",
            fecha_inicio=date(2026, 5, 15),
            fecha_fin=date(2026, 5, 16),
            sede=Sede(nombre="Club Nautico", ciudad="Buenos Aires", pais="Argentina"),
            entidad_organizadora=EntidadOrganizadora(nombre="ADA", tipo="FEDERACION"),
        )
        torneo.abrir_inscripcion()
        await torneo_repo.save(torneo)

    asyncio.run(_seed())
    callback = build_on_inscripcion_confirmada_callback(
        p10_handler=p10,
        atleta_repo=atleta_repo,
        torneo_repo=torneo_repo,
    )
    configure_inscripcion_notificaciones(callback)
    app.dependency_overrides[get_current_user] = lambda: {
        "sub": str(atleta_id),
        "email": "ana.paz@ataraxiadive.io",
        "rol": "ATLETA",
    }

    yield {
        "atleta_id": atleta_id,
        "torneo_id": torneo_id,
        "notificaciones_db": notificaciones_db,
        "email": email,
        "callback": callback,
    }

    app.dependency_overrides.clear()
    configure_inscripcion_notificaciones(None)


async def _event_types(db_path) -> list[str]:
    async with aiosqlite.connect(db_path) as db:
        cursor = await db.execute("SELECT event_type FROM notificaciones_events ORDER BY id ASC")
        rows = await cursor.fetchall()
    return [row[0] for row in rows]


async def _count_enviadas(db_path, evento_fuente_id: str) -> int:
    async with aiosqlite.connect(db_path) as db:
        cursor = await db.execute(
            """
            SELECT COUNT(*)
            FROM notificaciones_events
            WHERE event_type = 'NotificacionEnviada'
              AND json_extract(payload, '$.evento_fuente_id') = ?
            """,
            (evento_fuente_id,),
        )
        row = await cursor.fetchone()
    return int(row[0])


def test_post_inscripciones_dispara_p10_y_persiste_notificacion(
    p10_endpoint_context: dict[str, Any],
) -> None:
    client = TestClient(app)

    response = client.post(
        "/registro/inscripciones",
        json={
            "atleta_id": str(p10_endpoint_context["atleta_id"]),
            "torneo_id": str(p10_endpoint_context["torneo_id"]),
            "disciplinas": ["STA", "DNF"],
        },
    )

    assert response.status_code == 201
    assert p10_endpoint_context["email"].sent == 1
    assert p10_endpoint_context["email"].messages[0]["to"] == "ana.paz@ataraxiadive.io"
    assert "Open BA 2026" in p10_endpoint_context["email"].messages[0]["subject"]
    assert asyncio.run(_event_types(p10_endpoint_context["notificaciones_db"])) == [
        "NotificacionSolicitada",
        "NotificacionEnviada",
    ]


def test_callback_p10_no_duplica_email_para_misma_inscripcion(
    p10_endpoint_context: dict[str, Any],
) -> None:
    client = TestClient(app)
    response = client.post(
        "/registro/inscripciones",
        json={
            "atleta_id": str(p10_endpoint_context["atleta_id"]),
            "torneo_id": str(p10_endpoint_context["torneo_id"]),
            "disciplinas": ["STA"],
        },
    )
    inscripcion_id = UUID(response.json()["inscripcion_id"])

    asyncio.run(
        p10_endpoint_context["callback"](
            Inscripcion(
                inscripcion_id=inscripcion_id,
                atleta_id=p10_endpoint_context["atleta_id"],
                torneo_id=p10_endpoint_context["torneo_id"],
                disciplinas=frozenset({Disciplina.STA}),
            )
        )
    )

    assert p10_endpoint_context["email"].sent == 1
    assert (
        asyncio.run(
            _count_enviadas(
                p10_endpoint_context["notificaciones_db"],
                str(inscripcion_id),
            )
        )
        == 1
    )
