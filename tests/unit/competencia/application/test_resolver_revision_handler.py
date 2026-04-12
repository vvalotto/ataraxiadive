"""Tests unitarios del ResolverRevisionHandler — US-4.3.4."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from competencia.application.commands.resolver_revision import (
    PerformanceNoEncontrada,
    ResolverRevisionCommand,
    ResolverRevisionHandler,
)
from competencia.domain.exceptions import EstadoInvalidoParaResolverRevision, MotivoDQObligatorio
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.motivo_dq import MotivoDQ
from competencia.domain.value_objects.tipo_tarjeta import TipoTarjeta

OT = datetime(2026, 3, 22, 10, 30, 0)


def _ap_event(performance_id: Any, competencia_id: Any, participante_id: Any) -> dict[str, Any]:
    return {
        "event_type": "APRegistrado",
        "payload": {
            "performance_id": str(performance_id),
            "competencia_id": str(competencia_id),
            "participante_id": str(participante_id),
            "disciplina": Disciplina.DNF.value,
            "valor_ap": "50",
            "unidad": "Metros",
            "occurred_at": datetime(2026, 3, 22, 9, 0, 0).isoformat(),
        },
    }


def _llamado_event(performance_id: Any, participante_id: Any) -> dict[str, Any]:
    return {
        "event_type": "AtletaLlamado",
        "payload": {
            "performance_id": str(performance_id),
            "participante_id": str(participante_id),
            "disciplina": Disciplina.DNF.value,
            "posicion_grilla": 1,
            "ot_programado": OT.isoformat(),
            "llamado_en": datetime(2026, 3, 22, 10, 0, 0).isoformat(),
            "occurred_at": datetime(2026, 3, 22, 10, 0, 0).isoformat(),
        },
    }


def _resultado_event(performance_id: Any, participante_id: Any) -> dict[str, Any]:
    return {
        "event_type": "ResultadoRegistrado",
        "payload": {
            "performance_id": str(performance_id),
            "participante_id": str(participante_id),
            "disciplina": Disciplina.DNF.value,
            "valor_rp": "50.5",
            "unidad": "Metros",
            "registrado_por": "juez-001",
            "registrado_en": datetime(2026, 3, 22, 10, 35, 0).isoformat(),
            "occurred_at": datetime(2026, 3, 22, 10, 35, 0).isoformat(),
        },
    }


def _amarilla_event(performance_id: Any, participante_id: Any) -> dict[str, Any]:
    return {
        "event_type": "TarjetaAsignada",
        "payload": {
            "performance_id": str(performance_id),
            "participante_id": str(participante_id),
            "disciplina": Disciplina.DNF.value,
            "tipo": "Amarilla",
            "motivo_dq_codigo": None,
            "motivo_texto": "Revision de superficie",
            "asignada_por": "juez-001",
            "asignada_en": datetime(2026, 3, 22, 10, 40, 0).isoformat(),
            "distancia_blackout": None,
            "penalizaciones": [],
            "rp_medido": "50.5",
            "rp_penalizado": None,
            "occurred_at": datetime(2026, 3, 22, 10, 40, 0).isoformat(),
        },
    }


@pytest.fixture
def competencia_id() -> Any:
    return uuid4()


@pytest.fixture
def participante_id() -> Any:
    return uuid4()


@pytest.fixture
def performance_id() -> Any:
    return uuid4()


@pytest.fixture
def mock_event_store_en_revision(
    performance_id: Any, competencia_id: Any, participante_id: Any
) -> AsyncMock:
    store = AsyncMock()
    store.load.return_value = [
        _ap_event(performance_id, competencia_id, participante_id),
        _llamado_event(performance_id, participante_id),
        _resultado_event(performance_id, participante_id),
        _amarilla_event(performance_id, participante_id),
    ]
    store.append.return_value = None
    return store


@pytest.mark.asyncio
async def test_resolver_revision_blanca_persiste_evento(
    mock_event_store_en_revision: AsyncMock,
    competencia_id: Any,
    participante_id: Any,
) -> None:
    handler = ResolverRevisionHandler(mock_event_store_en_revision)

    await handler.handle(
        ResolverRevisionCommand(
            competencia_id=competencia_id,
            participante_id=participante_id,
            disciplina=Disciplina.DNF,
            tipo=TipoTarjeta.Blanca,
            resuelta_por="juez-001",
        )
    )

    call_kwargs = mock_event_store_en_revision.append.call_args.kwargs
    assert call_kwargs["event_type"] == "RevisionResuelta"
    assert call_kwargs["payload"]["tipo"] == "Blanca"


@pytest.mark.asyncio
async def test_resolver_revision_roja_sin_motivo_falla(
    mock_event_store_en_revision: AsyncMock,
    competencia_id: Any,
    participante_id: Any,
) -> None:
    handler = ResolverRevisionHandler(mock_event_store_en_revision)

    with pytest.raises(MotivoDQObligatorio):
        await handler.handle(
            ResolverRevisionCommand(
                competencia_id=competencia_id,
                participante_id=participante_id,
                disciplina=Disciplina.DNF,
                tipo=TipoTarjeta.Roja,
                resuelta_por="juez-001",
            )
        )


@pytest.mark.asyncio
async def test_resolver_revision_sin_stream_lanza_excepcion(
    competencia_id: Any,
    participante_id: Any,
) -> None:
    store = AsyncMock()
    store.load.return_value = []
    handler = ResolverRevisionHandler(store)

    with pytest.raises(PerformanceNoEncontrada):
        await handler.handle(
            ResolverRevisionCommand(
                competencia_id=competencia_id,
                participante_id=participante_id,
                disciplina=Disciplina.DNF,
                tipo=TipoTarjeta.Blanca,
                resuelta_por="juez-001",
            )
        )


@pytest.mark.asyncio
async def test_resolver_revision_desde_estado_invalido_falla(
    performance_id: Any,
    competencia_id: Any,
    participante_id: Any,
) -> None:
    store = AsyncMock()
    store.load.return_value = [
        _ap_event(performance_id, competencia_id, participante_id),
        _llamado_event(performance_id, participante_id),
        _resultado_event(performance_id, participante_id),
    ]
    handler = ResolverRevisionHandler(store)

    with pytest.raises(EstadoInvalidoParaResolverRevision):
        await handler.handle(
            ResolverRevisionCommand(
                competencia_id=competencia_id,
                participante_id=participante_id,
                disciplina=Disciplina.DNF,
                tipo=TipoTarjeta.Blanca,
                resuelta_por="juez-001",
            )
        )
