from __future__ import annotations

import json
from typing import Any

import aiosqlite
import pytest

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


class FakeEmailPort:
    def __init__(self) -> None:
        self.messages: list[dict[str, str]] = []

    async def enviar(self, destinatario, contenido) -> str | None:
        self.messages.append({"to": destinatario.email, "body": contenido.cuerpo_texto})
        return f"provider-{len(self.messages)}"


def _evento(*, resultados: tuple[ResultadoPublicadoAtleta, ...] | None = None):
    return ResultadosPublicados(
        id="evt-res-001",
        torneo_id="torneo-001",
        torneo_nombre="Open BA 2026",
        disciplina="DNF",
        resultados=resultados
        or (
            ResultadoPublicadoAtleta("ath-1", "martin@example.com", "Martin Garcia", 1, "96m", "Blanca"),
            ResultadoPublicadoAtleta("ath-2", "ana@example.com", "Ana Lopez", 2, "88m", "Blanca"),
            ResultadoPublicadoAtleta("ath-3", "diego@example.com", "Diego Vega", 3, "DNS", None, "DNS"),
        ),
        podio=(
            PodioPublicado(posicion=1, atleta_nombre="Martin Garcia", rp="96m"),
            PodioPublicado(posicion=2, atleta_nombre="Ana Lopez", rp="88m"),
            PodioPublicado(posicion=3, atleta_nombre="Diego Vega", rp="DNS"),
        ),
    )


def _handler(repo: SQLiteNotificacionRepository, email: FakeEmailPort) -> PoliticaP11Handler:
    return PoliticaP11Handler(
        repository=repo,
        solicitar_envio_handler=SolicitarEnvioHandler(repo),
        enviar_notificacion_handler=EnviarNotificacionHandler(repo, email),
        template=ResultadosPublicadosTemplate(),
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


@pytest.mark.asyncio
async def test_p11_persiste_tres_envios_en_sqlite(tmp_path) -> None:
    db_path = tmp_path / "notificaciones.db"
    repo = SQLiteNotificacionRepository(SQLiteNotificacionEventStore(str(db_path)))
    email = FakeEmailPort()

    await _handler(repo, email).handle(_evento())

    events = await _events(db_path)
    assert len(email.messages) == 3
    assert [event["event_type"] for event in events].count("NotificacionEnviada") == 3
    assert await repo.exists_success_by_evento_fuente_id("evt-res-001:ath-1") is True
    assert await repo.exists_success_by_evento_fuente_id("evt-res-001:ath-2") is True
    assert await repo.exists_success_by_evento_fuente_id("evt-res-001:ath-3") is True


@pytest.mark.asyncio
async def test_p11_no_duplica_al_reprocesar_evento(tmp_path) -> None:
    db_path = tmp_path / "notificaciones.db"
    repo = SQLiteNotificacionRepository(SQLiteNotificacionEventStore(str(db_path)))
    email = FakeEmailPort()
    handler = _handler(repo, email)

    await handler.handle(_evento())
    await handler.handle(_evento())

    events = await _events(db_path)
    assert len(email.messages) == 3
    assert [event["event_type"] for event in events].count("NotificacionEnviada") == 3


@pytest.mark.asyncio
async def test_p11_persiste_fallo_por_email_ausente(tmp_path) -> None:
    db_path = tmp_path / "notificaciones.db"
    repo = SQLiteNotificacionRepository(SQLiteNotificacionEventStore(str(db_path)))
    email = FakeEmailPort()
    resultados = (
        ResultadoPublicadoAtleta("ath-1", None, "Martin Garcia", 1, "96m", "Blanca"),
        ResultadoPublicadoAtleta("ath-2", "ana@example.com", "Ana Lopez", 2, "88m", "Blanca"),
    )

    await _handler(repo, email).handle(_evento(resultados=resultados))

    events = await _events(db_path)
    assert len(email.messages) == 1
    assert [event["event_type"] for event in events] == [
        "NotificacionFallida",
        "NotificacionSolicitada",
        "NotificacionEnviada",
    ]
    assert events[0]["payload"]["evento_fuente_id"] == "evt-res-001:ath-1"
    assert events[0]["payload"]["motivo"] == "destinatario_sin_email"
