from __future__ import annotations

import aiosqlite
import pytest

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


class FakeEmailPort:
    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail
        self.sent = 0

    async def enviar(self, destinatario, contenido) -> str | None:
        self.sent += 1
        if self.fail:
            raise RuntimeError("proveedor_no_disponible")
        return "provider-123"


def _evento(email: str | None = "garcia@apnea.com") -> InscripcionConfirmada:
    return InscripcionConfirmada(
        id="evt-reg-001",
        atleta_id="ath-123",
        atleta_email=email,
        atleta_nombre="Martin Garcia",
        torneo_nombre="Open BA 2026",
        torneo_fecha="2026-05-15",
        torneo_sede="Club Nautico",
        disciplinas=("DNF", "STA"),
    )


def _handler(repo: SQLiteNotificacionRepository, email: FakeEmailPort) -> PoliticaP10Handler:
    return PoliticaP10Handler(
        repository=repo,
        solicitar_envio_handler=SolicitarEnvioHandler(repo),
        enviar_notificacion_handler=EnviarNotificacionHandler(repo, email),
        template=InscripcionConfirmadaTemplate(),
    )


async def _event_types(db_path) -> list[str]:
    async with aiosqlite.connect(db_path) as db:
        cursor = await db.execute("SELECT event_type FROM notificaciones_events ORDER BY id ASC")
        rows = await cursor.fetchall()
    return [row[0] for row in rows]


@pytest.mark.asyncio
async def test_p10_persiste_solicitud_y_envio_en_sqlite(tmp_path) -> None:
    db_path = tmp_path / "notificaciones.db"
    repo = SQLiteNotificacionRepository(SQLiteNotificacionEventStore(str(db_path)))
    email = FakeEmailPort()

    await _handler(repo, email).handle(_evento())

    assert email.sent == 1
    assert await _event_types(db_path) == [
        "NotificacionSolicitada",
        "NotificacionEnviada",
    ]
    assert await repo.exists_success_by_evento_fuente_id("evt-reg-001") is True


@pytest.mark.asyncio
async def test_p10_no_duplica_envio_al_reprocesar_evento(tmp_path) -> None:
    db_path = tmp_path / "notificaciones.db"
    repo = SQLiteNotificacionRepository(SQLiteNotificacionEventStore(str(db_path)))
    email = FakeEmailPort()
    handler = _handler(repo, email)

    await handler.handle(_evento())
    await handler.handle(_evento())

    assert email.sent == 1
    assert await _event_types(db_path) == [
        "NotificacionSolicitada",
        "NotificacionEnviada",
    ]


@pytest.mark.asyncio
async def test_p10_persiste_fallo_por_email_ausente(tmp_path) -> None:
    db_path = tmp_path / "notificaciones.db"
    repo = SQLiteNotificacionRepository(SQLiteNotificacionEventStore(str(db_path)))
    email = FakeEmailPort()

    await _handler(repo, email).handle(_evento(email=None))

    assert email.sent == 0
    assert await _event_types(db_path) == ["NotificacionFallida"]


@pytest.mark.asyncio
async def test_p10_persiste_fallo_tecnico_del_proveedor(tmp_path) -> None:
    db_path = tmp_path / "notificaciones.db"
    repo = SQLiteNotificacionRepository(SQLiteNotificacionEventStore(str(db_path)))
    email = FakeEmailPort(fail=True)

    await _handler(repo, email).handle(_evento())

    assert email.sent == 1
    assert await _event_types(db_path) == [
        "NotificacionSolicitada",
        "NotificacionFallida",
    ]
