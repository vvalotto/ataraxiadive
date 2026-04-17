from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from notificaciones.application.commands.enviar_notificacion import (
    EnviarNotificacionCommand,
    EnviarNotificacionHandler,
)
from notificaciones.application.commands.solicitar_envio import (
    SolicitarEnvioCommand,
    SolicitarEnvioHandler,
)
from notificaciones.application.policies._helpers import registrar_fallo_sin_email
from notificaciones.domain.ports.notificacion_repository import NotificacionRepository
from notificaciones.domain.value_objects.contenido_email import ContenidoEmail
from notificaciones.domain.value_objects.destinatario import Destinatario


@dataclass(frozen=True)
class ResultadoPublicadoAtleta:
    atleta_id: str
    atleta_email: str | None
    atleta_nombre: str
    posicion: int | None
    rp: str
    tarjeta: str | None
    estado: str = "Clasificado"


@dataclass(frozen=True)
class PodioPublicado:
    posicion: int
    atleta_nombre: str
    rp: str


@dataclass(frozen=True)
class ResultadosPublicados:
    id: str
    torneo_id: str | None
    torneo_nombre: str
    disciplina: str
    resultados: tuple[ResultadoPublicadoAtleta, ...]
    podio: tuple[PodioPublicado, ...]


class ResultadosPublicadosTemplatePort(Protocol):
    def render(
        self,
        *,
        evento: ResultadosPublicados,
        resultado: ResultadoPublicadoAtleta,
    ) -> ContenidoEmail: ...


class PoliticaP11Handler:
    def __init__(
        self,
        *,
        repository: NotificacionRepository,
        solicitar_envio_handler: SolicitarEnvioHandler,
        enviar_notificacion_handler: EnviarNotificacionHandler,
        template: ResultadosPublicadosTemplatePort,
    ) -> None:
        self._repository = repository
        self._solicitar_envio_handler = solicitar_envio_handler
        self._enviar_notificacion_handler = enviar_notificacion_handler
        self._template = template

    async def handle(self, evento: ResultadosPublicados) -> None:
        for resultado in evento.resultados:
            if resultado.estado == "Retirado":
                continue
            await self._procesar_resultado(evento, resultado)

    async def _procesar_resultado(
        self,
        evento: ResultadosPublicados,
        resultado: ResultadoPublicadoAtleta,
    ) -> None:
        evento_fuente_id = self._evento_fuente_id(evento, resultado)
        if not resultado.atleta_email or not resultado.atleta_email.strip():
            await registrar_fallo_sin_email(evento_fuente_id, self._repository)
            return

        contenido = self._template.render(evento=evento, resultado=resultado)
        notificacion_id = await self._solicitar_envio_handler.handle(
            SolicitarEnvioCommand(
                evento_fuente_id=evento_fuente_id,
                destinatario=Destinatario(
                    email=resultado.atleta_email,
                    nombre=resultado.atleta_nombre,
                ),
                contenido=contenido,
            )
        )
        if notificacion_id is None:
            return
        await self._enviar_notificacion_handler.handle(
            EnviarNotificacionCommand(notificacion_id=notificacion_id)
        )

    @staticmethod
    def _evento_fuente_id(
        evento: ResultadosPublicados,
        resultado: ResultadoPublicadoAtleta,
    ) -> str:
        return f"{evento.id}:{resultado.atleta_id}"
