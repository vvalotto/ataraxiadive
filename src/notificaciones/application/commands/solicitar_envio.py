from __future__ import annotations

from dataclasses import dataclass

from notificaciones.domain.aggregates.notificacion import Notificacion
from notificaciones.domain.ports.notificacion_repository import NotificacionRepository
from notificaciones.domain.value_objects.canal_envio import CanalEnvio
from notificaciones.domain.value_objects.contenido_email import ContenidoEmail
from notificaciones.domain.value_objects.destinatario import Destinatario
from notificaciones.domain.value_objects.evento_fuente_id import EventoFuenteId
from notificaciones.domain.value_objects.notificacion_id import NotificacionId


@dataclass(frozen=True)
class SolicitarEnvioCommand:
    evento_fuente_id: str
    destinatario: Destinatario
    contenido: ContenidoEmail
    canal: CanalEnvio = CanalEnvio.EMAIL


class SolicitarEnvioHandler:
    def __init__(self, repository: NotificacionRepository) -> None:
        self._repository = repository

    async def handle(self, command: SolicitarEnvioCommand) -> NotificacionId | None:
        evento_fuente_id = EventoFuenteId(command.evento_fuente_id)
        aggregate = await Notificacion.solicitar_envio(
            evento_fuente_id=evento_fuente_id,
            destinatario=command.destinatario,
            contenido=command.contenido,
            canal=command.canal,
            existe_envio_exitoso_previo=await self._repository.exists_success_by_evento_fuente_id(
                str(evento_fuente_id)
            ),
        )
        if aggregate is None:
            return None
        await persistir_eventos_pendientes(self._repository, aggregate)
        return aggregate.notificacion_id


async def persistir_eventos_pendientes(
    repository: NotificacionRepository,
    aggregate: Notificacion,
) -> None:
    for event in aggregate.pull_events():
        await repository.append(aggregate.stream_id, event.event_type, event.to_payload())
