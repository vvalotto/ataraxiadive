"""Tests unitarios de TipoReglamento y campo tipo_reglamento en Torneo [US-5.6.2]."""

from __future__ import annotations

from datetime import date

import pytest

from torneo.domain.aggregates.torneo import Torneo
from torneo.domain.value_objects.entidad_organizadora import EntidadOrganizadora
from torneo.domain.value_objects.sede import Sede
from torneo.domain.value_objects.tipo_reglamento import TipoReglamento


@pytest.fixture
def torneo_base() -> Torneo:
    return Torneo(
        nombre="Torneo Test",
        descripcion="desc",
        fecha_inicio=date(2026, 6, 1),
        fecha_fin=date(2026, 6, 2),
        sede=Sede(nombre="Piscina", ciudad="Buenos Aires", pais="AR"),
        entidad_organizadora=EntidadOrganizadora(nombre="Club", tipo="Club"),
    )


class TestTipoReglamento:
    def test_enum_values(self) -> None:
        assert TipoReglamento.FAAS == "FAAS"
        assert TipoReglamento.CMAS == "CMAS"
        assert TipoReglamento.AIDA == "AIDA"

    def test_from_string(self) -> None:
        assert TipoReglamento("FAAS") is TipoReglamento.FAAS
        assert TipoReglamento("CMAS") is TipoReglamento.CMAS
        assert TipoReglamento("AIDA") is TipoReglamento.AIDA

    def test_invalid_value_raises(self) -> None:
        with pytest.raises(ValueError):
            TipoReglamento("OTRO")


class TestTorneoTipoReglamento:
    def test_default_es_faas(self, torneo_base: Torneo) -> None:
        assert torneo_base.tipo_reglamento == TipoReglamento.FAAS

    def test_creado_con_faas_explicito(self) -> None:
        torneo = Torneo(
            nombre="T",
            descripcion="d",
            fecha_inicio=date(2026, 6, 1),
            fecha_fin=date(2026, 6, 1),
            sede=Sede(nombre="P", ciudad="BA", pais="AR"),
            entidad_organizadora=EntidadOrganizadora(nombre="C", tipo="Club"),
            tipo_reglamento=TipoReglamento.FAAS,
        )
        assert torneo.tipo_reglamento == TipoReglamento.FAAS

    def test_creado_con_cmas(self) -> None:
        torneo = Torneo(
            nombre="T",
            descripcion="d",
            fecha_inicio=date(2026, 6, 1),
            fecha_fin=date(2026, 6, 1),
            sede=Sede(nombre="P", ciudad="BA", pais="AR"),
            entidad_organizadora=EntidadOrganizadora(nombre="C", tipo="Club"),
            tipo_reglamento=TipoReglamento.CMAS,
        )
        assert torneo.tipo_reglamento == TipoReglamento.CMAS


class TestCalcularRankingDI:
    def test_handler_acepta_algoritmo_por_di(self) -> None:
        from unittest.mock import MagicMock
        from resultados.application.commands.calcular_ranking import CalcularRankingHandler
        from resultados.domain.ports.algoritmo_puntaje import AlgoritmoPuntaje

        algoritmo_mock = MagicMock(spec=AlgoritmoPuntaje)
        handler = CalcularRankingHandler(
            ranking_store=MagicMock(),
            resultados_port=MagicMock(),
            algoritmo=algoritmo_mock,
        )
        assert handler._algoritmo is algoritmo_mock

    def test_handler_sin_algoritmo_acepta_none(self) -> None:
        from unittest.mock import MagicMock
        from resultados.application.commands.calcular_ranking import CalcularRankingHandler

        handler = CalcularRankingHandler(
            ranking_store=MagicMock(),
            resultados_port=MagicMock(),
        )
        assert handler._algoritmo is None
