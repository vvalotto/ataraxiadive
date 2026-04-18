from __future__ import annotations

import asyncio
import json
from typing import Any

import aiosqlite
import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from notificaciones.application.commands.enviar_notificacion import EnviarNotificacionHandler
from notificaciones.application.commands.solicitar_envio import SolicitarEnvioHandler
from notificaciones.application.policies.politica_p11 import (
    PodioPublicado,
    PoliticaP11Handler,
    ResultadoPublicadoAtleta,
    ResultadosPublicados,
)
from notificaciones.infrastructure.event_store.sqlite_notificacion_event_store import (
    SQLiteNotificacionEventStore,
)
from notificaciones.infrastructure.repositories.sqlite_notificacion_repository import (
    SQLiteNotificacionRepository,
)
from notificaciones.infrastructure.templates.resultados_publicados_template import (
    ResultadosPublicadosTemplate,
)

scenarios("../US-4.5.4-politica-p11.feature")


class FakeEmailPort:
    def __init__(self) -> None:
        self.fail_first = False
        self.calls = 0
        self.messages: list[dict[str, str]] = []

    async def enviar(self, destinatario, contenido) -> str | None:
        self.calls += 1
        if self.fail_first and self.calls == 1:
            raise RuntimeError("proveedor_no_disponible")
        self.messages.append(
            {
                "to": destinatario.email,
                "subject": contenido.asunto,
                "body": contenido.cuerpo_texto,
            }
        )
        return f"provider-{self.calls}"


@pytest.fixture
def ctx(tmp_path) -> dict[str, Any]:
    db_path = tmp_path / "notificaciones.db"
    repo = SQLiteNotificacionRepository(SQLiteNotificacionEventStore(str(db_path)))
    email = FakeEmailPort()
    handler = PoliticaP11Handler(
        repository=repo,
        solicitar_envio_handler=SolicitarEnvioHandler(repo),
        enviar_notificacion_handler=EnviarNotificacionHandler(repo, email),
        template=ResultadosPublicadosTemplate(),
    )
    return {
        "db_path": db_path,
        "repo": repo,
        "email": email,
        "handler": handler,
        "evento": _evento(),
        "error": None,
    }


def _base_resultados() -> tuple[ResultadoPublicadoAtleta, ...]:
    return (
        ResultadoPublicadoAtleta("ath-1", "martin@example.com", "Martin Garcia", 1, "96m", "Blanca"),
        ResultadoPublicadoAtleta("ath-2", "ana@example.com", "Ana Lopez", 2, "88m", "Blanca"),
        ResultadoPublicadoAtleta("ath-3", "diego@example.com", "Diego Vega", 3, "DNS", None, "DNS"),
    )


def _evento(
    *,
    evento_id: str = "evt-res-001",
    resultados: tuple[ResultadoPublicadoAtleta, ...] | None = None,
) -> ResultadosPublicados:
    return ResultadosPublicados(
        id=evento_id,
        torneo_id="torneo-001",
        torneo_nombre="Open BA 2026",
        disciplina="DNF",
        resultados=resultados or _base_resultados(),
        podio=(
            PodioPublicado(posicion=1, atleta_nombre="Martin Garcia", rp="96m"),
            PodioPublicado(posicion=2, atleta_nombre="Ana Lopez", rp="88m"),
            PodioPublicado(posicion=3, atleta_nombre="Diego Vega", rp="DNS"),
        ),
    )


async def _events(db_path) -> list[dict[str, Any]]:
    async with aiosqlite.connect(db_path) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT event_type, payload FROM notificaciones_events ORDER BY id ASC"
        )
        rows = await cursor.fetchall()
    return [
        {"event_type": row["event_type"], "payload": json.loads(row["payload"])}
        for row in rows
    ]


@given("el evento ResultadosPublicados contiene 3 atletas con emails validos")
def given_evento_tres_atletas(ctx: dict[str, Any]) -> None:
    ctx["evento"] = _evento()


@given(parsers.parse('los resultados "{evento_id}" ya fueron publicados y emails enviados'))
def given_resultados_ya_publicados(ctx: dict[str, Any], evento_id: str) -> None:
    async def _run() -> None:
        ctx["evento"] = _evento(evento_id=evento_id)
        await ctx["handler"].handle(ctx["evento"])

    asyncio.run(_run())


@given("uno de los 3 atletas no tiene email registrado")
def given_un_atleta_sin_email(ctx: dict[str, Any]) -> None:
    resultados = (
        ResultadoPublicadoAtleta("ath-1", None, "Martin Garcia", 1, "96m", "Blanca"),
        *_base_resultados()[1:],
    )
    ctx["evento"] = _evento(resultados=resultados)


@given("el proveedor de email falla solo para el primer atleta")
def given_falla_primer_atleta(ctx: dict[str, Any]) -> None:
    ctx["email"].fail_first = True


@given(parsers.parse('un atleta tiene estado "{estado}" en los resultados'))
def given_atleta_estado(ctx: dict[str, Any], estado: str) -> None:
    resultados = (
        _base_resultados()[0],
        _base_resultados()[1],
        ResultadoPublicadoAtleta("ath-3", "diego@example.com", "Diego Vega", 3, estado, None, estado),
    )
    ctx["evento"] = _evento(resultados=resultados)


@when("se procesa la politica P-11")
def when_procesar_p11(ctx: dict[str, Any]) -> None:
    async def _run() -> None:
        try:
            await ctx["handler"].handle(ctx["evento"])
        except Exception as exc:  # noqa: BLE001
            ctx["error"] = exc

    asyncio.run(_run())


@when(parsers.parse('la politica P-11 recibe nuevamente el evento "{evento_id}"'))
def when_reprocesar_p11(ctx: dict[str, Any], evento_id: str) -> None:
    ctx["evento"] = _evento(evento_id=evento_id)
    when_procesar_p11(ctx)


@then("se crean 3 aggregates Notificacion, uno por atleta")
def then_tres_notificaciones(ctx: dict[str, Any]) -> None:
    events = asyncio.run(_events(ctx["db_path"]))
    assert [event["event_type"] for event in events].count("NotificacionSolicitada") == 3


@then(parsers.parse('cada aggregate queda en estado "{estado}"'))
def then_cada_estado(ctx: dict[str, Any], estado: str) -> None:
    events = asyncio.run(_events(ctx["db_path"]))
    if estado == "Enviada":
        assert [event["event_type"] for event in events].count("NotificacionEnviada") == 3
    else:
        raise AssertionError(f"Estado no soportado: {estado}")


@then("cada atleta recibe un email con su posicion individual y el podio")
def then_cada_email_personalizado(ctx: dict[str, Any]) -> None:
    assert len(ctx["email"].messages) == 3
    assert all("Posicion:" in message["body"] for message in ctx["email"].messages)
    assert all("Podio DNF" in message["body"] for message in ctx["email"].messages)


@then(parsers.parse('el email de "{nombre}" contiene "{texto}"'))
def then_email_de_contiene(ctx: dict[str, Any], nombre: str, texto: str) -> None:
    message = next(message for message in ctx["email"].messages if nombre in message["body"])
    assert texto in message["body"]


@then(parsers.parse('el email de "{nombre}" contiene el podio con los 3 primeros clasificados'))
def then_email_de_contiene_podio(ctx: dict[str, Any], nombre: str) -> None:
    message = next(message for message in ctx["email"].messages if nombre in message["body"])
    assert "#1 Martin Garcia - 96m" in message["body"]
    assert "#2 Ana Lopez - 88m" in message["body"]
    assert "#3 Diego Vega - DNS" in message["body"]


@then("no se envian emails duplicados a ningun atleta")
def then_no_duplicados(ctx: dict[str, Any]) -> None:
    assert len(ctx["email"].messages) == 3


@then("el store conserva exactamente una NotificacionEnviada por par evento-atleta")
def then_una_enviada_por_par(ctx: dict[str, Any]) -> None:
    events = asyncio.run(_events(ctx["db_path"]))
    enviadas = [event for event in events if event["event_type"] == "NotificacionEnviada"]
    assert len(enviadas) == 3
    assert {event["payload"]["evento_fuente_id"] for event in enviadas} == {
        "evt-res-001:ath-1",
        "evt-res-001:ath-2",
        "evt-res-001:ath-3",
    }


@then("los 2 atletas con email reciben su notificacion")
def then_dos_con_email(ctx: dict[str, Any]) -> None:
    assert len(ctx["email"].messages) == 2


@then(
    parsers.parse(
        'el atleta sin email tiene una Notificacion en estado "{estado}" con motivo "{motivo}"'
    )
)
def then_sin_email_fallida(ctx: dict[str, Any], estado: str, motivo: str) -> None:
    assert estado == "Fallida"
    events = asyncio.run(_events(ctx["db_path"]))
    fallidas = [event for event in events if event["event_type"] == "NotificacionFallida"]
    assert len(fallidas) == 1
    assert fallidas[0]["payload"]["motivo"] == motivo


@then("la publicacion de resultados no se revierte")
def then_publicacion_no_revierte(ctx: dict[str, Any]) -> None:
    assert ctx["error"] is None


@then(parsers.parse('el primer atleta tiene Notificacion en estado "{estado}"'))
def then_primer_atleta_estado(ctx: dict[str, Any], estado: str) -> None:
    events = asyncio.run(_events(ctx["db_path"]))
    assert estado == "Fallida"
    assert events[1]["event_type"] == "NotificacionFallida"


@then("los atletas restantes reciben su email exitosamente")
def then_restantes_exitosos(ctx: dict[str, Any]) -> None:
    assert len(ctx["email"].messages) == 2


@then(parsers.parse('ese atleta recibe el email con "{texto}" como su resultado'))
def then_dns_recibe_email(ctx: dict[str, Any], texto: str) -> None:
    message = next(message for message in ctx["email"].messages if "Diego Vega" in message["body"])
    assert texto in message["body"]


@then("el email incluye el podio de la disciplina")
def then_email_incluye_podio(ctx: dict[str, Any]) -> None:
    assert any("Podio DNF" in message["body"] for message in ctx["email"].messages)
