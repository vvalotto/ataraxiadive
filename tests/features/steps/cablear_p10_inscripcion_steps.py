from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import date
from typing import Any
from uuid import UUID, uuid4

import aiosqlite
import pytest
from fastapi.testclient import TestClient
from pytest_bdd import given, parsers, scenarios, then, when

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
from registro.domain.value_objects.categoria import Categoria
from registro.infrastructure.repositories.sqlite_atleta_repository import SQLiteAtletaRepository
from shared.domain.value_objects.disciplina import Disciplina
from torneo.domain.aggregates.torneo import Torneo
from torneo.domain.value_objects.entidad_organizadora import EntidadOrganizadora
from torneo.domain.value_objects.sede import Sede
from torneo.infrastructure.repositories.sqlite_torneo_repository import SQLiteTorneoRepository

scenarios("../US-4.5.5-cablear-p10-inscripcion.feature")


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


@dataclass(frozen=True)
class CallbackInscripcion:
    inscripcion_id: str
    atleta_id: UUID
    torneo_id: UUID
    disciplinas: frozenset[Disciplina]


@pytest.fixture
def ctx(tmp_path, monkeypatch) -> dict[str, Any]:
    registro_db = tmp_path / "registro.db"
    torneo_db = tmp_path / "torneo.db"
    notificaciones_db = tmp_path / "notificaciones.db"
    monkeypatch.setenv("REGISTRO_DB_PATH", str(registro_db))
    monkeypatch.setenv("TORNEO_DB_PATH", str(torneo_db))
    monkeypatch.setenv("NOTIFICACIONES_DB_PATH", str(notificaciones_db))

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
    data: dict[str, Any] = {
        "registro_db": registro_db,
        "torneo_db": torneo_db,
        "notificaciones_db": notificaciones_db,
        "atleta_id": uuid4(),
        "torneo_id": uuid4(),
        "torneo_nombre": "Open BA 2026",
        "email": email,
        "p10": p10,
        "response": None,
        "error": None,
        "callback": None,
        "callback_inscripcion": None,
    }
    app.dependency_overrides[get_current_user] = lambda: {
        "sub": str(data["atleta_id"]),
        "email": "test@ataraxiadive.io",
        "rol": "ATLETA",
    }

    yield data

    app.dependency_overrides.clear()
    configure_inscripcion_notificaciones(None)


async def _seed_atleta_y_torneo(ctx: dict[str, Any], email: str) -> None:
    atleta_repo = SQLiteAtletaRepository(str(ctx["registro_db"]))
    torneo_repo = SQLiteTorneoRepository(str(ctx["torneo_db"]))
    await atleta_repo.save(
        Atleta(
            atleta_id=ctx["atleta_id"],
            nombre="Ana",
            apellido="Paz",
            email=email,
            fecha_nacimiento=date(1992, 4, 12),
            categoria=Categoria.SENIOR_FEMENINO,
            club="Azul",
        )
    )
    torneo = Torneo(
        torneo_id=ctx["torneo_id"],
        nombre=ctx["torneo_nombre"],
        descripcion="Torneo de apnea",
        fecha_inicio=date(2026, 5, 15),
        fecha_fin=date(2026, 5, 16),
        sede=Sede(nombre="Club Nautico", ciudad="Buenos Aires", pais="Argentina"),
        entidad_organizadora=EntidadOrganizadora(nombre="ADA", tipo="FEDERACION"),
    )
    torneo.abrir_inscripcion()
    await torneo_repo.save(torneo)


def _configurar_callback(ctx: dict[str, Any]) -> None:
    callback = build_on_inscripcion_confirmada_callback(
        p10_handler=ctx["p10"],
        atleta_repo=SQLiteAtletaRepository(str(ctx["registro_db"])),
        torneo_repo=SQLiteTorneoRepository(str(ctx["torneo_db"])),
    )
    ctx["callback"] = callback
    configure_inscripcion_notificaciones(callback)


async def _count_enviadas(db_path, evento_fuente_id: str | None = None) -> int:
    query = "SELECT COUNT(*) FROM notificaciones_events " "WHERE event_type = 'NotificacionEnviada'"
    params: tuple[str, ...] = ()
    if evento_fuente_id is not None:
        query += " AND json_extract(payload, '$.evento_fuente_id') = ?"
        params = (evento_fuente_id,)
    async with aiosqlite.connect(db_path) as db:
        cursor = await db.execute(query, params)
        row = await cursor.fetchone()
    return int(row[0])


@given(parsers.parse('existe un atleta con email "{email}" y un torneo abierto'))
def given_atleta_y_torneo(ctx: dict[str, Any], email: str) -> None:
    asyncio.run(_seed_atleta_y_torneo(ctx, email))


@given("el endpoint de inscripcion tiene P-10 configurada")
def given_endpoint_p10_configurada(ctx: dict[str, Any]) -> None:
    _configurar_callback(ctx)


@given(
    parsers.parse(
        'la inscripcion "{inscripcion_id}" ya fue procesada y su NotificacionEnviada existe en el store'
    )
)
def given_inscripcion_ya_procesada(ctx: dict[str, Any], inscripcion_id: str) -> None:
    asyncio.run(_seed_atleta_y_torneo(ctx, "test@ataraxiadive.io"))
    _configurar_callback(ctx)
    ctx["callback_inscripcion"] = CallbackInscripcion(
        inscripcion_id=inscripcion_id,
        atleta_id=ctx["atleta_id"],
        torneo_id=ctx["torneo_id"],
        disciplinas=frozenset({Disciplina.STA}),
    )
    asyncio.run(ctx["callback"](ctx["callback_inscripcion"]))


@given("el callback P-10 recibe una inscripcion con atleta_id inexistente")
def given_callback_atleta_inexistente(ctx: dict[str, Any]) -> None:
    asyncio.run(_seed_atleta_y_torneo(ctx, "test@ataraxiadive.io"))
    _configurar_callback(ctx)
    ctx["callback_inscripcion"] = CallbackInscripcion(
        inscripcion_id="ins-atleta-inexistente",
        atleta_id=uuid4(),
        torneo_id=ctx["torneo_id"],
        disciplinas=frozenset({Disciplina.STA}),
    )


@given("el callback P-10 recibe una inscripcion con torneo_id inexistente")
def given_callback_torneo_inexistente(ctx: dict[str, Any]) -> None:
    asyncio.run(_seed_atleta_y_torneo(ctx, "test@ataraxiadive.io"))
    _configurar_callback(ctx)
    ctx["callback_inscripcion"] = CallbackInscripcion(
        inscripcion_id="ins-torneo-inexistente",
        atleta_id=ctx["atleta_id"],
        torneo_id=uuid4(),
        disciplinas=frozenset({Disciplina.STA}),
    )


@when("se hace POST /registro/inscripciones con atleta_id y torneo_id validos")
def when_post_inscripciones(ctx: dict[str, Any]) -> None:
    client = TestClient(app)
    ctx["response"] = client.post(
        "/registro/inscripciones",
        json={
            "atleta_id": str(ctx["atleta_id"]),
            "torneo_id": str(ctx["torneo_id"]),
            "disciplinas": ["STA"],
        },
    )


@when(parsers.parse('el callback P-10 se ejecuta de nuevo con inscripcion_id "{inscripcion_id}"'))
def when_callback_reprocesa(ctx: dict[str, Any], inscripcion_id: str) -> None:
    ctx["callback_inscripcion"] = CallbackInscripcion(
        inscripcion_id=inscripcion_id,
        atleta_id=ctx["atleta_id"],
        torneo_id=ctx["torneo_id"],
        disciplinas=frozenset({Disciplina.STA}),
    )
    asyncio.run(ctx["callback"](ctx["callback_inscripcion"]))


@when("el callback se ejecuta")
def when_callback_ejecuta(ctx: dict[str, Any]) -> None:
    try:
        asyncio.run(ctx["callback"](ctx["callback_inscripcion"]))
    except Exception as exc:  # noqa: BLE001
        ctx["error"] = exc


@then("la inscripcion se crea con status 201")
def then_status_201(ctx: dict[str, Any]) -> None:
    assert ctx["response"].status_code == 201


@then(parsers.parse('se envia un email a "{email}" con asunto que contiene el nombre del torneo'))
def then_email_enviado(ctx: dict[str, Any], email: str) -> None:
    assert ctx["email"].messages[-1]["to"] == email
    assert ctx["torneo_nombre"] in ctx["email"].messages[-1]["subject"]


@then("el event store de notificaciones registra una NotificacionEnviada")
def then_store_registra_enviada(ctx: dict[str, Any]) -> None:
    assert asyncio.run(_count_enviadas(ctx["notificaciones_db"])) == 1


@then("no se envia un segundo email")
def then_no_segundo_email(ctx: dict[str, Any]) -> None:
    assert ctx["email"].sent == 1


@then(
    parsers.parse(
        'el event store sigue con exactamente una NotificacionEnviada para "{inscripcion_id}"'
    )
)
def then_store_una_enviada(ctx: dict[str, Any], inscripcion_id: str) -> None:
    assert asyncio.run(_count_enviadas(ctx["notificaciones_db"], inscripcion_id)) == 1


@then("no se lanza excepcion")
def then_no_exception(ctx: dict[str, Any]) -> None:
    assert ctx["error"] is None


@then("no se envia ningun email")
def then_no_email(ctx: dict[str, Any]) -> None:
    assert ctx["email"].sent == 0
