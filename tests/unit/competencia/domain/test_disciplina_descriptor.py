"""Tests unitarios de DisciplinaDescriptor VO — US-2.2.1."""

from __future__ import annotations

import pytest

from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.disciplina_descriptor import DisciplinaDescriptor
from competencia.domain.value_objects.unidad_medida import UnidadMedida


class TestDescriptorSTA:
    def test_unidad_es_segundos(self) -> None:
        d = DisciplinaDescriptor.para(Disciplina.STA)
        assert d.unidad_esperada == UnidadMedida.Segundos

    def test_orden_ascendente(self) -> None:
        d = DisciplinaDescriptor.para(Disciplina.STA)
        assert d.orden_ascendente is True

    def test_disciplina_correcta(self) -> None:
        d = DisciplinaDescriptor.para(Disciplina.STA)
        assert d.disciplina == Disciplina.STA


class TestDescriptorSPEVariantes:
    @pytest.mark.parametrize(
        "disciplina",
        [
            Disciplina.SPE_2X50,
            Disciplina.SPE_4X50,
            Disciplina.SPE_8X50,
            Disciplina.SPE_16X50,
        ],
    )
    def test_unidad_es_segundos(self, disciplina: Disciplina) -> None:
        d = DisciplinaDescriptor.para(disciplina)
        assert d.unidad_esperada == UnidadMedida.Segundos

    @pytest.mark.parametrize(
        "disciplina",
        [
            Disciplina.SPE_2X50,
            Disciplina.SPE_4X50,
            Disciplina.SPE_8X50,
            Disciplina.SPE_16X50,
        ],
    )
    def test_orden_es_descendente(self, disciplina: Disciplina) -> None:
        d = DisciplinaDescriptor.para(disciplina)
        assert d.orden_ascendente is False

    def test_spe_generica_permanece_legacy(self) -> None:
        d = DisciplinaDescriptor.para(Disciplina.SPE)
        assert d.unidad_esperada == UnidadMedida.Metros
        assert d.orden_ascendente is True

    def test_helpers_spe(self) -> None:
        assert Disciplina.SPE_2X50.es_spe() is True
        assert Disciplina.SPE_2X50.es_tiempo() is True
        assert Disciplina.SPE.es_spe() is True
        assert Disciplina.SPE.es_tiempo() is False


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
class TestDescriptorDistancia:
    def test_unidad_es_metros(self, disciplina: Disciplina) -> None:
        d = DisciplinaDescriptor.para(disciplina)
        assert d.unidad_esperada == UnidadMedida.Metros

    def test_orden_ascendente(self, disciplina: Disciplina) -> None:
        d = DisciplinaDescriptor.para(disciplina)
        assert d.orden_ascendente is True

    def test_disciplina_correcta(self, disciplina: Disciplina) -> None:
        d = DisciplinaDescriptor.para(disciplina)
        assert d.disciplina == disciplina


class TestDescriptorFactoryMethod:
    def test_todas_las_disciplinas_tienen_descriptor(self) -> None:
        for disciplina in Disciplina:
            desc = DisciplinaDescriptor.para(disciplina)
            assert desc.disciplina == disciplina
            assert desc.unidad_esperada in (UnidadMedida.Segundos, UnidadMedida.Metros)

    def test_descriptor_es_inmutable(self) -> None:
        d = DisciplinaDescriptor.para(Disciplina.STA)
        with pytest.raises((AttributeError, TypeError)):
            d.orden_ascendente = True  # type: ignore[misc]
