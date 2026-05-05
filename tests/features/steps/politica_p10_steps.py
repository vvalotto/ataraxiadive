from __future__ import annotations

import asyncio
from typing import Any

import aiosqlite
import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from notificaciones.application.commands.enviar_notificacion import EnviarNotificacionHandler
from notificaciones.application.commands.solicitar_envio import SolicitarEnvioHandler
from notificaciones.application.policies.politica_p10 import (
    InscripcionConfirmada,
    PoliticaP10Handler,
)
from notificaciones.infrastructure.event_store.sqlite_notificacion_event_store import (
    SQLiteNotificacionEventStore,
)
from notificaciones.infrastructure.repositories.sqlite_notificacion_repository import (
    SQLiteNotificacionRepository,
)
from notificaciones.infrastructure.templates.inscripcion_confirmada_template import (
    InscripcionConfirmadaTemplate,
)

scenarios("../US-4.5.3-politica-p10.feature")


class FakeEmailPort:
    def __init__(self) -> None:
        self.fail = False
        self.sent = 0
        self.messages: list[dict[str, Any]] = []

    async def enviar(self, destinatario, contenido) -> str | None:
        if self.fail:
            raise RuntimeError("proveedor_no_disponible")
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
def ctx(tmp_path) -> dict[str, Any]:
    db_path = tmp_path / "notificaciones.db"
    repo = SQLiteNotificacionRepository(SQLiteNotificacionEventStore(str(db_path)))
    email = FakeEmailPort()
    handler = PoliticaP10Handler(
        repository=repo,
        solicitar_envio_handler=SolicitarEnvioHandler(repo),
        enviar_notificacion_handler=EnviarNotificacionHandler(repo, email),
        template=InscripcionConfirmadaTemplate(),
    )
    return {
        "db_path": db_path,
        "repo": repo,
        "email": email,
        "handler": handler,
        "evento": _evento(),
        "error": None,
    }


def _evento(
    *,
    evento_id: str = "evt-reg-001",
    atleta_nombre: str = "Martin Garcia",
    atleta_email: str | None = "garcia@apnea.com",
    torneo_nombre: str = "Open BA 2026",
    torneo_fecha: str = "2026-05-15",
    torneo_sede: str = "Club Nautico",
    disciplinas: tuple[str, ...] = ("DNF", "STA"),
) -> InscripcionConfirmada:
    return InscripcionConfirmada(
        id=evento_id,
        atleta_id="ath-123",
        atleta_email=atleta_email,
        atleta_nombre=atleta_nombre,
        torneo_nombre=torneo_nombre,
        torneo_fecha=torneo_fecha,
        torneo_sede=torneo_sede,
        disciplinas=disciplinas,
    )


async def _events(db_path) -> list[dict[str, Any]]:
    async with aiosqlite.connect(db_path) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("""
            SELECT event_type, payload
            FROM notificaciones_events
            ORDER BY id ASC
            """)
        rows = await cursor.fetchall()
    return [{"event_type": row["event_type"], "payload": row["payload"]} for row in rows]


@given(parsers.parse('el sistema recibe el evento InscripcionConfirmada para "{nombre}"'))
def given_evento_para_atleta(ctx: dict[str, Any], nombre: str) -> None:
    ctx["evento"] = _evento(atleta_nombre=nombre)


@given(parsers.parse('el evento tiene email "{email}" y torneo "{torneo}"'))
def given_email_y_torneo(ctx: dict[str, Any], email: str, torneo: str) -> None:
    evento = ctx["evento"]
    ctx["evento"] = _evento(
        atleta_nombre=evento.atleta_nombre,
        atleta_email=email,
        torneo_nombre=torneo,
        disciplinas=evento.disciplinas,
    )


@given(parsers.parse('el evento contiene las disciplinas "{disciplina_a}" y "{disciplina_b}"'))
def given_disciplinas(ctx: dict[str, Any], disciplina_a: str, disciplina_b: str) -> None:
    evento = ctx["evento"]
    ctx["evento"] = _evento(
        atleta_nombre=evento.atleta_nombre,
        atleta_email=evento.atleta_email,
        torneo_nombre=evento.torneo_nombre,
        torneo_fecha=evento.torneo_fecha,
        torneo_sede=evento.torneo_sede,
        disciplinas=(disciplina_a, disciplina_b),
    )


@given(parsers.parse('el evento InscripcionConfirmada "{evento_id}" ya fue procesado exitosamente'))
def given_evento_ya_procesado(ctx: dict[str, Any], evento_id: str) -> None:
    async def _run() -> None:
        ctx["evento"] = _evento(evento_id=evento_id)
        await ctx["handler"].handle(ctx["evento"])

    asyncio.run(_run())


@given("el sistema recibe un evento InscripcionConfirmada sin email de atleta")
def given_evento_sin_email(ctx: dict[str, Any]) -> None:
    ctx["evento"] = _evento(atleta_email=None)


@given("el proveedor de email falla al enviar la confirmacion")
def given_proveedor_falla(ctx: dict[str, Any]) -> None:
    ctx["email"].fail = True


@given(parsers.parse('el evento tiene torneo "{torneo}", fecha "{fecha}" y sede "{sede}"'))
def given_torneo_fecha_sede(ctx: dict[str, Any], torneo: str, fecha: str, sede: str) -> None:
    evento = ctx["evento"]
    ctx["evento"] = _evento(
        atleta_nombre=evento.atleta_nombre,
        atleta_email=evento.atleta_email,
        torneo_nombre=torneo,
        torneo_fecha=fecha,
        torneo_sede=sede,
        disciplinas=evento.disciplinas,
    )


@when("se procesa la politica P-10")
def when_procesar_p10(ctx: dict[str, Any]) -> None:
    async def _run() -> None:
        try:
            await ctx["handler"].handle(ctx["evento"])
        except Exception as exc:  # noqa: BLE001
            ctx["error"] = exc

    asyncio.run(_run())


@when(parsers.parse('la politica P-10 recibe nuevamente el evento "{evento_id}"'))
def when_reprocesar_evento(ctx: dict[str, Any], evento_id: str) -> None:
    ctx["evento"] = _evento(evento_id=evento_id)
    when_procesar_p10(ctx)


@then(parsers.parse('se crea un aggregate Notificacion en estado "{estado}"'))
def then_estado_notificacion(ctx: dict[str, Any], estado: str) -> None:
    events = asyncio.run(_events(ctx["db_path"]))
    assert events
    if estado == "Enviada":
        assert events[-1]["event_type"] == "NotificacionEnviada"
    elif estado == "Fallida":
        assert events[-1]["event_type"] == "NotificacionFallida"
    else:
        raise AssertionError(f"Estado no soportado en test: {estado}")


@then(parsers.parse('el email llega a "{email}" con asunto "{asunto}"'))
def then_email_llega(ctx: dict[str, Any], email: str, asunto: str) -> None:
    assert ctx["email"].messages[-1]["to"] == email
    assert ctx["email"].messages[-1]["subject"] == asunto


@then(parsers.parse('el cuerpo del email contiene el torneo "{torneo}"'))
def then_cuerpo_contiene_torneo(ctx: dict[str, Any], torneo: str) -> None:
    assert torneo in ctx["email"].messages[-1]["body"]


@then(parsers.parse('el cuerpo del email contiene las disciplinas "{a}" y "{b}"'))
def then_cuerpo_contiene_disciplinas(ctx: dict[str, Any], a: str, b: str) -> None:
    body = ctx["email"].messages[-1]["body"]
    assert a in body
    assert b in body


@then("no se envia un segundo email")
def then_no_segundo_email(ctx: dict[str, Any]) -> None:
    assert ctx["email"].sent == 1


@then(parsers.parse('el store conserva exactamente una NotificacionEnviada para "{evento_id}"'))
def then_una_enviada(ctx: dict[str, Any], evento_id: str) -> None:
    events = asyncio.run(_events(ctx["db_path"]))
    enviadas = [event for event in events if event["event_type"] == "NotificacionEnviada"]
    assert len(enviadas) == 1
    assert evento_id in enviadas[0]["payload"]


@then(parsers.parse('el motivo del fallo es "{motivo}"'))
def then_motivo_fallo(ctx: dict[str, Any], motivo: str) -> None:
    events = asyncio.run(_events(ctx["db_path"]))
    assert motivo in events[-1]["payload"]


@then("la politica P-10 no lanza excepcion")
def then_no_exception(ctx: dict[str, Any]) -> None:
    assert ctx["error"] is None


@then("el fallo queda registrado en el event store de notificaciones")
def then_fallo_registrado(ctx: dict[str, Any]) -> None:
    events = asyncio.run(_events(ctx["db_path"]))
    assert events[-1]["event_type"] == "NotificacionFallida"


@then("la inscripcion del atleta no se revierte")
def then_inscripcion_no_revertida(ctx: dict[str, Any]) -> None:
    assert ctx["error"] is None


@then(parsers.parse('el asunto del email incluye "{texto}"'))
def then_asunto_incluye(ctx: dict[str, Any], texto: str) -> None:
    assert texto in ctx["email"].messages[-1]["subject"]


@then(parsers.parse('el cuerpo del email contiene "{texto}"'))
def then_cuerpo_contiene(ctx: dict[str, Any], texto: str) -> None:
    assert texto in ctx["email"].messages[-1]["body"]
