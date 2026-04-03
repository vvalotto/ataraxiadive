"""Tests unitarios del CalcularRankingHandler y ObtenerRankingHandler — US-2.4.2."""

from __future__ import annotations

from decimal import Decimal
from typing import Any
from unittest.mock import AsyncMock
from uuid import UUID, uuid4

import pytest

from registro.domain.value_objects.categoria import Categoria
from shared.domain.value_objects.disciplina import Disciplina
from resultados.application.commands.calcular_ranking import (
    CalcularRankingCommand,
    CalcularRankingHandler,
)
from resultados.application.queries.obtener_ranking import (
    ObtenerRankingHandler,
    ObtenerRankingQuery,
)
from resultados.domain.exceptions import ResultadosIncompletos
from resultados.domain.ports.resultados_competencia_port import ResultadoFinal

# ── Helpers ───────────────────────────────────────────────────────────────────


def _resultado(
    rp: str = "330",
    unidad: str = "Segundos",
    tarjeta: str = "Blanca",
    atleta_id: UUID | None = None,
) -> ResultadoFinal:
    return ResultadoFinal(
        atleta_id=atleta_id or uuid4(),
        rp=Decimal(rp),
        unidad=unidad,
        tarjeta=tarjeta,
        es_dns=False,
        categoria=Categoria.SENIOR_MASCULINO,
    )


def _raw_event_resultados_calculados(cid: UUID, atleta_id: UUID) -> dict[str, Any]:
    """Evento serializado como lo devolvería el Event Store."""
    import json

    payload = {
        "competencia_id": str(cid),
        "disciplina": "STA",
        "total": 1,
        "entries": [
            {
                "posicion": 1,
                "atleta_id": str(atleta_id),
                "categoria": "SENIOR_MASCULINO",
                "rp": "330",
                "unidad": "Segundos",
                "tarjeta": "Blanca",
                "es_dns": False,
                "en_podio": True,
            }
        ],
        "calculado_en": "2026-03-27T10:00:00",
    }
    return {
        "event_type": "ResultadosCalculados",
        "payload": json.dumps(payload),
    }


# ── CalcularRankingHandler ────────────────────────────────────────────────────


class TestCalcularRankingHandler:
    def _make_handler(
        self,
        resultados: list[ResultadoFinal],
        existing_events: list[dict[str, Any]] | None = None,
    ) -> tuple[CalcularRankingHandler, AsyncMock, AsyncMock]:
        ranking_store = AsyncMock()
        ranking_store.load = AsyncMock(return_value=existing_events or [])
        ranking_store.append = AsyncMock()

        resultados_port = AsyncMock()
        resultados_port.get_resultados_finales = AsyncMock(return_value=resultados)

        handler = CalcularRankingHandler(
            ranking_store=ranking_store,
            resultados_port=resultados_port,
        )
        return handler, ranking_store, resultados_port

    @pytest.mark.asyncio
    async def test_handle_persiste_resultados_calculados(self) -> None:
        """Handle persiste el evento ResultadosCalculados en el ranking store."""
        cid = uuid4()
        handler, ranking_store, _ = self._make_handler([_resultado()])

        command = CalcularRankingCommand(competencia_id=cid, disciplina=Disciplina.STA)
        await handler.handle(command)

        ranking_store.append.assert_called_once()
        call_kwargs = ranking_store.append.call_args.kwargs
        assert call_kwargs["event_type"] == "ResultadosCalculados"
        assert f"ranking-{cid}-STA" == call_kwargs["stream_id"]

    @pytest.mark.asyncio
    async def test_handle_consulta_resultados_port(self) -> None:
        """Handle delega la lectura de resultados al puerto ACL."""
        cid = uuid4()
        handler, _, resultados_port = self._make_handler([_resultado()])

        command = CalcularRankingCommand(competencia_id=cid, disciplina=Disciplina.STA)
        await handler.handle(command)

        resultados_port.get_resultados_finales.assert_called_once_with(cid, Disciplina.STA)

    @pytest.mark.asyncio
    async def test_handle_sin_resultados_lanza_resultados_incompletos(self) -> None:
        handler, _, _ = self._make_handler([])

        command = CalcularRankingCommand(competencia_id=uuid4(), disciplina=Disciplina.STA)
        with pytest.raises(ResultadosIncompletos):
            await handler.handle(command)

    @pytest.mark.asyncio
    async def test_handle_multiples_atletas_persiste_orden_correcto(self) -> None:
        """El payload persistido contiene el orden correcto de entradas."""
        import json

        cid = uuid4()
        atleta_1 = uuid4()
        atleta_2 = uuid4()

        resultados = [
            _resultado("200", atleta_id=atleta_2),
            _resultado("330", atleta_id=atleta_1),
        ]

        handler, ranking_store, _ = self._make_handler(resultados)
        command = CalcularRankingCommand(competencia_id=cid, disciplina=Disciplina.STA)
        await handler.handle(command)

        payload_raw = ranking_store.append.call_args.kwargs["payload"]
        if isinstance(payload_raw, str):
            payload = json.loads(payload_raw)
        else:
            payload = payload_raw

        entries = payload["entries"]
        assert entries[0]["atleta_id"] == str(atleta_1)
        assert entries[0]["posicion"] == 1
        assert entries[1]["atleta_id"] == str(atleta_2)
        assert entries[1]["posicion"] == 2


# ── ObtenerRankingHandler ─────────────────────────────────────────────────────


class TestObtenerRankingHandler:
    @pytest.mark.asyncio
    async def test_handle_sin_eventos_devuelve_lista_vacia(self) -> None:
        """Antes de calcular, el ranking devuelve lista vacía."""
        ranking_store = AsyncMock()
        ranking_store.load = AsyncMock(return_value=[])

        handler = ObtenerRankingHandler(ranking_store=ranking_store)
        query = ObtenerRankingQuery(competencia_id=uuid4(), disciplina=Disciplina.STA)

        result = await handler.handle(query)

        assert result == []

    @pytest.mark.asyncio
    async def test_handle_con_evento_devuelve_entradas(self) -> None:
        """Con un evento calculado, devuelve las entradas del ranking."""
        cid = uuid4()
        atleta_id = uuid4()

        ranking_store = AsyncMock()
        ranking_store.load = AsyncMock(
            return_value=[_raw_event_resultados_calculados(cid, atleta_id)]
        )

        handler = ObtenerRankingHandler(ranking_store=ranking_store)
        query = ObtenerRankingQuery(competencia_id=cid, disciplina=Disciplina.STA)

        result = await handler.handle(query)

        assert len(result) == 1
        assert result[0].categoria == "SENIOR_MASCULINO"
        assert len(result[0].entradas) == 1
        assert result[0].entradas[0].atleta_id == str(atleta_id)
        assert result[0].entradas[0].posicion == 1
        assert result[0].entradas[0].rp == "330"
        assert result[0].entradas[0].unidad == "Segundos"
        assert result[0].entradas[0].tarjeta == "Blanca"
        assert result[0].entradas[0].es_dns is False
        assert result[0].entradas[0].en_podio is True

    @pytest.mark.asyncio
    async def test_handle_lee_stream_correcto(self) -> None:
        """ObtenerRankingHandler lee el stream ranking-{cid}-{disciplina}."""
        cid = uuid4()
        ranking_store = AsyncMock()
        ranking_store.load = AsyncMock(return_value=[])

        handler = ObtenerRankingHandler(ranking_store=ranking_store)
        query = ObtenerRankingQuery(competencia_id=cid, disciplina=Disciplina.STA)
        await handler.handle(query)

        ranking_store.load.assert_called_once_with(f"ranking-{cid}-STA")
