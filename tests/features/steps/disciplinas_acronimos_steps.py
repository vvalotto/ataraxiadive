"""Step definitions BDD — US-ADJ-4.1: Disciplinas con acrónimos AIDA correctos."""

from __future__ import annotations

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from shared.domain.value_objects.disciplina import Disciplina
from shared.domain.value_objects.disciplina_descriptor import DisciplinaDescriptor

scenarios("../US-ADJ-4.1-disciplinas-acronimos-aida.feature")


@given("el sistema conoce las disciplinas AIDA", target_fixture="disciplinas")
def dado_sistema_con_disciplinas() -> set[str]:
    return {d.value for d in Disciplina}


@when(parsers.parse('se consulta la disciplina "{nombre}"'), target_fixture="disciplina")
def cuando_consulta_disciplina(nombre: str) -> Disciplina:
    return Disciplina(nombre)


@then("el sistema la reconoce como disciplina de distancia")
def entonces_es_distancia(disciplina: Disciplina) -> None:
    assert disciplina.es_distancia()


@then("su orden de grilla es ascendente")
def entonces_orden_ascendente(disciplina: Disciplina) -> None:
    descriptor = DisciplinaDescriptor.para(disciplina)
    assert descriptor.orden_ascendente is True


@when(
    parsers.parse('se intenta usar "{nombre}" como disciplina'),
    target_fixture="nombre_invalido",
)
def cuando_intenta_usar_invalido(nombre: str) -> str:
    return nombre


@then("el sistema rechaza el valor como disciplina desconocida")
def entonces_rechaza_desconocido(nombre_invalido: str) -> None:
    with pytest.raises(ValueError):
        Disciplina(nombre_invalido)
