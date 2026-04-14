from __future__ import annotations

import pytest

from notificaciones.domain.aggregates.notificacion import Notificacion
from notificaciones.domain.value_objects.canal_envio import CanalEnvio
from notificaciones.domain.value_objects.contenido_email import ContenidoEmail
from notificaciones.domain.value_objects.destinatario import Destinatario
from notificaciones.domain.value_objects.evento_fuente_id import EventoFuenteId
from notificaciones.infrastructure.event_store.sqlite_notificacion_event_store import (
    SQLiteNotificacionEventStore,
)
from notificaciones.infrastructure.repositories.sqlite_notificacion_repository import (
    SQLiteNotificacionRepository,
)


@pytest.mark.asyncio
async def test_repository_persiste_y_rehidrata_stream(tmp_path) -> None:
    db_path = tmp_path / "notificaciones.db"
    repo = SQLiteNotificacionRepository(SQLiteNotificacionEventStore(str(db_path)))

    aggregate = await Notificacion.solicitar_envio(
        evento_fuente_id=EventoFuenteId("reg-001"),
        destinatario=Destinatario(email="juan@example.com", nombre="Juan"),
        contenido=ContenidoEmail(asunto="Inscripcion", cuerpo_texto="ok"),
        canal=CanalEnvio.EMAIL,
        existe_envio_exitoso_previo=False,
    )
    assert aggregate is not None

    for event in aggregate.pull_events():
        await repo.append(aggregate.stream_id, event.event_type, event.to_payload())

    stored = await repo.load(aggregate.stream_id)
    reconstituted = Notificacion.reconstitute(stored)

    assert reconstituted.estado == "Solicitada"
    assert reconstituted.destinatario is not None
    assert reconstituted.destinatario.email == "juan@example.com"


@pytest.mark.asyncio
async def test_repository_detecta_exito_previod_por_evento_fuente_id(tmp_path) -> None:
    db_path = tmp_path / "notificaciones.db"
    repo = SQLiteNotificacionRepository(SQLiteNotificacionEventStore(str(db_path)))

    aggregate = await Notificacion.solicitar_envio(
        evento_fuente_id=EventoFuenteId("reg-001"),
        destinatario=Destinatario(email="juan@example.com"),
        contenido=ContenidoEmail(asunto="Inscripcion", cuerpo_texto="ok"),
        canal=CanalEnvio.EMAIL,
        existe_envio_exitoso_previo=False,
    )
    assert aggregate is not None
    for event in aggregate.pull_events():
        await repo.append(aggregate.stream_id, event.event_type, event.to_payload())
    aggregate.registrar_envio_exitoso("provider-1")
    for event in aggregate.pull_events():
        await repo.append(aggregate.stream_id, event.event_type, event.to_payload(), expected_version=1)

    assert await repo.exists_success_by_evento_fuente_id("reg-001") is True
    assert await repo.exists_success_by_evento_fuente_id("reg-002") is False


@pytest.mark.asyncio
async def test_streams_independientes_comparten_mismo_store(tmp_path) -> None:
    db_path = tmp_path / "notificaciones.db"
    repo = SQLiteNotificacionRepository(SQLiteNotificacionEventStore(str(db_path)))

    first = await Notificacion.solicitar_envio(
        evento_fuente_id=EventoFuenteId("reg-001"),
        destinatario=Destinatario(email="uno@example.com"),
        contenido=ContenidoEmail(asunto="A", cuerpo_texto="ok"),
        canal=CanalEnvio.EMAIL,
        existe_envio_exitoso_previo=False,
    )
    second = await Notificacion.solicitar_envio(
        evento_fuente_id=EventoFuenteId("reg-002"),
        destinatario=Destinatario(email="dos@example.com"),
        contenido=ContenidoEmail(asunto="B", cuerpo_texto="ok"),
        canal=CanalEnvio.EMAIL,
        existe_envio_exitoso_previo=False,
    )
    assert first is not None
    assert second is not None

    for event in first.pull_events():
        await repo.append(first.stream_id, event.event_type, event.to_payload())
    for event in second.pull_events():
        await repo.append(second.stream_id, event.event_type, event.to_payload())

    first_stream = await repo.load(first.stream_id)
    second_stream = await repo.load(second.stream_id)

    assert len(first_stream) == 1
    assert len(second_stream) == 1
    assert first_stream[0]["payload"]["evento_fuente_id"] == "reg-001"
    assert second_stream[0]["payload"]["evento_fuente_id"] == "reg-002"
