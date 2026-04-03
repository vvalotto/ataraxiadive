"""Adaptador ResultadosCompetenciaAdapter — ACL que lee resultados de BC Competencia."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from shared.domain.ports.event_store_port import EventStorePort
from shared.domain.value_objects.disciplina import Disciplina
from resultados.domain.ports.resultados_competencia_port import (
    ResultadoFinal,
    ResultadosCompetenciaPort,
)


class ResultadosCompetenciaAdapter(ResultadosCompetenciaPort):
    """ACL: lee los streams de BC Competencia y traduce al modelo de BC Resultados.

    Carga todos los streams `performance-{competencia_id}-*` del Event Store de
    BC Competencia, reconstituye cada Performance y extrae los datos necesarios
    para construir el ranking.

    Args:
        competencia_event_store: Event Store del BC Competencia.
    """

    def __init__(self, competencia_event_store: EventStorePort) -> None:
        self._event_store = competencia_event_store

    async def get_resultados_finales(
        self,
        competencia_id: UUID,
        disciplina: Disciplina,
    ) -> list[ResultadoFinal]:
        """Retorna los resultados finales de todas las performances de la disciplina.

        Solo incluye performances en estado Ejecutada o DNS.

        Args:
            competencia_id: Identificador de la competencia.
            disciplina: Disciplina a consultar.

        Returns:
            Lista de ResultadoFinal para todas las performances finalizadas.
        """
        prefix = f"performance-{competencia_id}-"
        all_streams = await self._event_store.load_all_streams_with_prefix(prefix)

        resultados: list[ResultadoFinal] = []
        for stream_events in all_streams:
            if not stream_events:
                continue

            resultado = _extraer_resultado_de_stream(stream_events, disciplina)
            if resultado is None:
                continue

            resultados.append(resultado)

        return resultados


def _extraer_resultado_de_stream(
    stream_events: list[dict],
    disciplina_buscada: Disciplina,
) -> ResultadoFinal | None:
    """Traduce un stream de performance a ResultadoFinal sin reconstituir aggregates."""
    estado = {
        "atleta_id": None,
        "disciplina": None,
        "tarjeta": None,
        "rp": None,
        "unidad": None,
        "es_dns": False,
        "finalizada": False,
    }

    for event in stream_events:
        _aplicar_evento_en_estado(estado, event)

    if not _es_resultado_relevante(estado, disciplina_buscada):
        return None

    return ResultadoFinal(
        atleta_id=estado["atleta_id"],
        rp=None if estado["es_dns"] else estado["rp"],
        unidad=None if estado["es_dns"] else estado["unidad"],
        tarjeta=estado["tarjeta"],
        es_dns=estado["es_dns"],
    )


def _aplicar_evento_en_estado(estado: dict[str, object], event: dict) -> None:
    payload = _parse_payload(event["payload"])
    event_type = event["event_type"]

    if event_type == "APRegistrado":
        _aplicar_ap_registrado(estado, payload)
    elif event_type == "ResultadoRegistrado":
        _aplicar_resultado_registrado(estado, payload)
    elif event_type == "TarjetaAsignada":
        estado["tarjeta"] = payload["tipo"]
        estado["finalizada"] = True
    elif event_type == "DNSRegistrado":
        estado["es_dns"] = True
        estado["finalizada"] = True


def _aplicar_ap_registrado(estado: dict[str, object], payload: dict[str, object]) -> None:
    estado["atleta_id"] = UUID(str(payload["participante_id"]))
    estado["disciplina"] = Disciplina(str(payload["disciplina"]))
    estado["unidad"] = payload["unidad"]


def _aplicar_resultado_registrado(estado: dict[str, object], payload: dict[str, object]) -> None:
    rp_value = payload.get("rp") or payload.get("valor_rp")
    estado["rp"] = Decimal(str(rp_value)) if rp_value is not None else None
    estado["unidad"] = payload.get("unidad", estado["unidad"])


def _es_resultado_relevante(
    estado: dict[str, object],
    disciplina_buscada: Disciplina,
) -> bool:
    return (
        estado["disciplina"] == disciplina_buscada
        and bool(estado["finalizada"])
        and estado["atleta_id"] is not None
    )


def _parse_payload(payload: object) -> dict[str, object]:
    if isinstance(payload, str):
        import json

        return json.loads(payload)
    return payload
