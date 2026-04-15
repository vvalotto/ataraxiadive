from __future__ import annotations

from typing import Any

import pytest

from notificaciones.application.commands.enviar_notificacion import EnviarNotificacionHandler
from notificaciones.application.commands.solicitar_envio import SolicitarEnvioHandler
from notificaciones.application.policies.politica_p11 import (
    PodioPublicado,
    PoliticaP11Handler,
    ResultadoPublicadoAtleta,
    ResultadosPublicados,
)
from notificaciones.infrastructure.templates.resultados_publicados_template import (
    ResultadosPublicadosTemplate,
)


class FakeNotificacionRepository:
    def __init__(self) -> None:
        self.events_by_stream: dict[str, list[dict[str, Any]]] = {}

    async def append(
        self,
        stream_id: str,
        event_type: str,
        payload: dict[str, Any],
        expected_version: int | None = None,
    ) -> None:
        self.events_by_stream.setdefault(stream_id, []).append(
            {
                "event_type": event_type,
                "payload": payload,
                "version": len(self.events_by_stream.get(stream_id, [])) + 1,
                "occurred_at": payload["occurred_at"],
            }
        )

    async def load(self, stream_id: str) -> list[dict[str, Any]]:
        return self.events_by_stream.get(stream_id, [])

    async def exists_success_by_evento_fuente_id(self, evento_fuente_id: str) -> bool:
        return any(
            event["event_type"] == "NotificacionEnviada"
            and event["payload"]["evento_fuente_id"] == evento_fuente_id
            for events in self.events_by_stream.values()
            for event in events
        )

    def event_types(self) -> list[str]:
        return [
            event["event_type"]
            for events in self.events_by_stream.values()
            for event in events
        ]


class FakeEmailPort:
    def __init__(self, fail_for: set[str] | None = None) -> None:
        self.fail_for = fail_for or set()
        self.messages: list[dict[str, str]] = []

    async def enviar(self, destinatario, contenido) -> str | None:
        if destinatario.email in self.fail_for:
            raise RuntimeError("proveedor_no_disponible")
        self.messages.append(
            {
                "to": destinatario.email,
                "subject": contenido.asunto,
                "body": contenido.cuerpo_texto,
            }
        )
        return f"provider-{len(self.messages)}"


def _evento(*, resultados: tuple[ResultadoPublicadoAtleta, ...] | None = None):
    return ResultadosPublicados(
        id="evt-res-001",
        torneo_id="torneo-001",
        torneo_nombre="Open BA 2026",
        disciplina="DNF",
        resultados=resultados
        or (
            ResultadoPublicadoAtleta(
                atleta_id="ath-1",
                atleta_email="martin@example.com",
                atleta_nombre="Martin Garcia",
                posicion=1,
                rp="96m",
                tarjeta="Blanca",
            ),
            ResultadoPublicadoAtleta(
                atleta_id="ath-2",
                atleta_email="ana@example.com",
                atleta_nombre="Ana Lopez",
                posicion=2,
                rp="88m",
                tarjeta="BlancaConPenalizaciones",
            ),
            ResultadoPublicadoAtleta(
                atleta_id="ath-3",
                atleta_email="diego@example.com",
                atleta_nombre="Diego Vega",
                posicion=3,
                rp="DNS",
                tarjeta=None,
                estado="DNS",
            ),
        ),
        podio=(
            PodioPublicado(posicion=1, atleta_nombre="Martin Garcia", rp="96m"),
            PodioPublicado(posicion=2, atleta_nombre="Ana Lopez", rp="88m"),
            PodioPublicado(posicion=3, atleta_nombre="Diego Vega", rp="DNS"),
        ),
    )


def _handler(repo: FakeNotificacionRepository, email: FakeEmailPort) -> PoliticaP11Handler:
    return PoliticaP11Handler(
        repository=repo,
        solicitar_envio_handler=SolicitarEnvioHandler(repo),
        enviar_notificacion_handler=EnviarNotificacionHandler(repo, email),
        template=ResultadosPublicadosTemplate(),
    )


@pytest.mark.asyncio
async def test_p11_envia_un_email_por_atleta() -> None:
    repo = FakeNotificacionRepository()
    email = FakeEmailPort()

    await _handler(repo, email).handle(_evento())

    assert len(email.messages) == 3
    assert repo.event_types() == [
        "NotificacionSolicitada",
        "NotificacionEnviada",
        "NotificacionSolicitada",
        "NotificacionEnviada",
        "NotificacionSolicitada",
        "NotificacionEnviada",
    ]
    assert all("Podio DNF" in message["body"] for message in email.messages)


@pytest.mark.asyncio
async def test_p11_es_idempotente_por_atleta() -> None:
    repo = FakeNotificacionRepository()
    email = FakeEmailPort()
    handler = _handler(repo, email)

    await handler.handle(_evento())
    await handler.handle(_evento())

    assert len(email.messages) == 3
    assert repo.event_types().count("NotificacionEnviada") == 3


@pytest.mark.asyncio
async def test_p11_atleta_sin_email_no_interrumpe_los_demas() -> None:
    repo = FakeNotificacionRepository()
    email = FakeEmailPort()
    resultados = (
        ResultadoPublicadoAtleta("ath-1", None, "Martin Garcia", 1, "96m", "Blanca"),
        ResultadoPublicadoAtleta("ath-2", "ana@example.com", "Ana Lopez", 2, "88m", "Blanca"),
    )

    await _handler(repo, email).handle(_evento(resultados=resultados))

    assert len(email.messages) == 1
    assert repo.event_types() == [
        "NotificacionFallida",
        "NotificacionSolicitada",
        "NotificacionEnviada",
    ]


@pytest.mark.asyncio
async def test_p11_fallo_de_proveedor_en_un_atleta_continua_con_los_demas() -> None:
    repo = FakeNotificacionRepository()
    email = FakeEmailPort(fail_for={"martin@example.com"})

    await _handler(repo, email).handle(_evento())

    assert len(email.messages) == 2
    assert repo.event_types().count("NotificacionFallida") == 1
    assert repo.event_types().count("NotificacionEnviada") == 2


@pytest.mark.asyncio
async def test_p11_omite_atleta_retirado() -> None:
    repo = FakeNotificacionRepository()
    email = FakeEmailPort()
    resultados = (
        ResultadoPublicadoAtleta(
            "ath-1", "martin@example.com", "Martin Garcia", 1, "96m", "Blanca"
        ),
        ResultadoPublicadoAtleta(
            "ath-2", "ana@example.com", "Ana Lopez", None, "-", None, estado="Retirado"
        ),
    )

    await _handler(repo, email).handle(_evento(resultados=resultados))

    assert len(email.messages) == 1
    assert "ana@example.com" not in {message["to"] for message in email.messages}


@pytest.mark.asyncio
async def test_p11_notifica_atleta_dns() -> None:
    repo = FakeNotificacionRepository()
    email = FakeEmailPort()

    await _handler(repo, email).handle(_evento())

    dns_email = next(message for message in email.messages if message["to"] == "diego@example.com")
    assert "DNS" in dns_email["body"]
    assert "Podio DNF" in dns_email["body"]
