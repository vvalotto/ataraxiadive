"""Tests unitarios de DisciplinaDescriptorAdapter — US-2.2.1."""

from __future__ import annotations

import pytest

from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.unidad_medida import UnidadMedida
from competencia.infrastructure.repositories.disciplina_descriptor_adapter import (
    DisciplinaDescriptorAdapter,
)


@pytest.fixture
def adapter() -> DisciplinaDescriptorAdapter:
    return DisciplinaDescriptorAdapter()


class TestAdapterSTA:
    def test_describe_sta_retorna_segundos(self, adapter: DisciplinaDescriptorAdapter) -> None:
        desc = adapter.describe(Disciplina.STA)
        assert desc.unidad_esperada == UnidadMedida.Segundos

    def test_describe_sta_retorna_orden_ascendente(
        self, adapter: DisciplinaDescriptorAdapter
    ) -> None:
        desc = adapter.describe(Disciplina.STA)
        assert desc.orden_ascendente is True


class TestAdapterDistancia:
    def test_describe_dnf_retorna_metros(self, adapter: DisciplinaDescriptorAdapter) -> None:
        desc = adapter.describe(Disciplina.DNF)
        assert desc.unidad_esperada == UnidadMedida.Metros

    def test_describe_dnf_retorna_orden_ascendente(
        self, adapter: DisciplinaDescriptorAdapter
    ) -> None:
        desc = adapter.describe(Disciplina.DNF)
        assert desc.orden_ascendente is True

    @pytest.mark.parametrize(
        "disciplina",
        [
            Disciplina.DNF,
            Disciplina.DYN,
            Disciplina.DBF,
            Disciplina.CNF,
            Disciplina.CWT,
            Disciplina.FIM,
        ],
    )
    def test_todas_distancias_coherentes(
        self, adapter: DisciplinaDescriptorAdapter, disciplina: Disciplina
    ) -> None:
        desc = adapter.describe(disciplina)
        assert desc.unidad_esperada == UnidadMedida.Metros
        assert desc.orden_ascendente is True


class TestAdapterTodasDisciplinas:
    def test_describe_retorna_disciplina_correcta(
        self, adapter: DisciplinaDescriptorAdapter
    ) -> None:
        for disciplina in Disciplina:
            desc = adapter.describe(disciplina)
            assert desc.disciplina == disciplina


class TestAdapterSPEVariantes:
    @pytest.mark.parametrize(
        "disciplina",
        [
            Disciplina.SPE_2X50,
            Disciplina.SPE_4X50,
            Disciplina.SPE_8X50,
            Disciplina.SPE_16X50,
        ],
    )
    def test_describe_spe_variante_retorna_segundos(
        self, adapter: DisciplinaDescriptorAdapter, disciplina: Disciplina
    ) -> None:
        desc = adapter.describe(disciplina)
        assert desc.unidad_esperada == UnidadMedida.Segundos

    @pytest.mark.parametrize(
        "disciplina",
        [
            Disciplina.SPE_2X50,
            Disciplina.SPE_4X50,
            Disciplina.SPE_8X50,
            Disciplina.SPE_16X50,
        ],
    )
    def test_describe_spe_variante_retorna_orden_descendente(
        self, adapter: DisciplinaDescriptorAdapter, disciplina: Disciplina
    ) -> None:
        desc = adapter.describe(disciplina)
        assert desc.orden_ascendente is False
