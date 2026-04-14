from __future__ import annotations

import json
from typing import Any

from notificaciones.domain.events.notificacion_enviada import NotificacionEnviada
from notificaciones.domain.events.notificacion_fallida import NotificacionFallida
from notificaciones.domain.events.notificacion_solicitada import NotificacionSolicitada
from notificaciones.domain.exceptions import EstadoNotificacionInvalido
from notificaciones.domain.value_objects.canal_envio import CanalEnvio
from notificaciones.domain.value_objects.contenido_email import ContenidoEmail
from notificaciones.domain.value_objects.destinatario import Destinatario
from notificaciones.domain.value_objects.evento_fuente_id import EventoFuenteId
from notificaciones.domain.value_objects.notificacion_id import NotificacionId
from shared.domain.base.aggregate_root import AggregateRoot


class Notificacion(AggregateRoot):
    """Aggregate raíz del BC Notificaciones."""

    def __init__(self, notificacion_id: NotificacionId) -> None:
        super().__init__()
        self._notificacion_id = notificacion_id
        self._evento_fuente_id: EventoFuenteId | None = None
        self._destinatario: Destinatario | None = None
        self._contenido: ContenidoEmail | None = None
        self._canal: CanalEnvio | None = None
        self._estado = "Nueva"
        self._proveedor_id: str | None = None
        self._motivo_fallo: str | None = None

    @property
    def notificacion_id(self) -> NotificacionId:
        return self._notificacion_id

    @property
    def evento_fuente_id(self) -> EventoFuenteId | None:
        return self._evento_fuente_id

    @property
    def destinatario(self) -> Destinatario | None:
        return self._destinatario

    @property
    def contenido(self) -> ContenidoEmail | None:
        return self._contenido

    @property
    def canal(self) -> CanalEnvio | None:
        return self._canal

    @property
    def estado(self) -> str:
        return self._estado

    @property
    def proveedor_id(self) -> str | None:
        return self._proveedor_id

    @property
    def motivo_fallo(self) -> str | None:
        return self._motivo_fallo

    @property
    def stream_id(self) -> str:
        return f"notificacion-{self._notificacion_id}"

    @classmethod
    async def solicitar_envio(
        cls,
        *,
        evento_fuente_id: EventoFuenteId,
        destinatario: Destinatario,
        contenido: ContenidoEmail,
        canal: CanalEnvio,
        existe_envio_exitoso_previo: bool,
    ) -> "Notificacion | None":
        if existe_envio_exitoso_previo:
            return None

        aggregate = cls(NotificacionId())
        event = NotificacionSolicitada(
            event_type="NotificacionSolicitada",
            aggregate_id=str(aggregate.notificacion_id),
            occurred_at=NotificacionSolicitada.now(),
            notificacion_id=str(aggregate.notificacion_id),
            evento_fuente_id=str(evento_fuente_id),
            destinatario_email=destinatario.email,
            destinatario_nombre=destinatario.nombre,
            asunto=contenido.asunto,
            cuerpo_texto=contenido.cuerpo_texto,
            cuerpo_html=contenido.cuerpo_html,
            canal=canal.value,
        )
        aggregate._apply(event)
        aggregate._record(event)
        return aggregate

    def registrar_envio_exitoso(self, proveedor_id: str | None = None) -> None:
        self._assert_solicitada()
        if self._evento_fuente_id is None:
            raise EstadoNotificacionInvalido(
                "Notificacion sin evento_fuente_id en estado Solicitada"
            )
        event = NotificacionEnviada(
            event_type="NotificacionEnviada",
            aggregate_id=str(self._notificacion_id),
            occurred_at=NotificacionEnviada.now(),
            notificacion_id=str(self._notificacion_id),
            evento_fuente_id=str(self._evento_fuente_id),
            proveedor_id=proveedor_id,
            enviada_en=NotificacionEnviada.now().isoformat(),
        )
        self._apply(event)
        self._record(event)

    def registrar_fallo(self, motivo: str) -> None:
        self._assert_solicitada()
        if not motivo or not motivo.strip():
            raise ValueError("motivo no puede ser vacío")
        if self._evento_fuente_id is None:
            raise EstadoNotificacionInvalido(
                "Notificacion sin evento_fuente_id en estado Solicitada"
            )
        event = NotificacionFallida(
            event_type="NotificacionFallida",
            aggregate_id=str(self._notificacion_id),
            occurred_at=NotificacionFallida.now(),
            notificacion_id=str(self._notificacion_id),
            evento_fuente_id=str(self._evento_fuente_id),
            motivo=motivo,
            fallida_en=NotificacionFallida.now().isoformat(),
        )
        self._apply(event)
        self._record(event)

    @classmethod
    def reconstitute(cls, events: list[dict[str, Any]]) -> "Notificacion":
        if not events:
            raise ValueError("No se puede reconstituir Notificacion sin eventos")
        first_payload = _parse_payload(events[0]["payload"])
        aggregate = cls(NotificacionId(first_payload["notificacion_id"]))
        for event in events:
            aggregate._apply_stored(event)
        return aggregate

    def _assert_solicitada(self) -> None:
        if self._estado != "Solicitada":
            raise EstadoNotificacionInvalido(
                f"Notificacion {self._notificacion_id} no acepta la operación "
                f"en estado {self._estado}"
            )

    def _apply_stored(self, event: dict[str, Any]) -> None:
        payload = _parse_payload(event["payload"])
        handlers = {
            "NotificacionSolicitada": NotificacionSolicitada.from_payload,
            "NotificacionEnviada": NotificacionEnviada.from_payload,
            "NotificacionFallida": NotificacionFallida.from_payload,
        }
        domain_event = handlers[event["event_type"]](payload)
        self._apply(domain_event)

    def _apply(
        self,
        event: NotificacionSolicitada | NotificacionEnviada | NotificacionFallida,
    ) -> None:
        if isinstance(event, NotificacionSolicitada):
            self._evento_fuente_id = EventoFuenteId(event.evento_fuente_id)
            self._destinatario = Destinatario(
                email=event.destinatario_email,
                nombre=event.destinatario_nombre,
            )
            self._contenido = ContenidoEmail(
                asunto=event.asunto,
                cuerpo_texto=event.cuerpo_texto,
                cuerpo_html=event.cuerpo_html,
            )
            self._canal = CanalEnvio(event.canal)
            self._estado = "Solicitada"
            return
        if isinstance(event, NotificacionEnviada):
            self._proveedor_id = event.proveedor_id
            self._estado = "Enviada"
            return
        self._motivo_fallo = event.motivo
        self._estado = "Fallida"


def _parse_payload(payload: Any) -> dict[str, Any]:
    if isinstance(payload, str):
        return json.loads(payload)  # type: ignore[no-any-return]
    return payload  # type: ignore[return-value]
