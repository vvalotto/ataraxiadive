from __future__ import annotations

from datetime import date, datetime
from uuid import uuid4

import pytest

from registro.domain.aggregates.inscripcion import Inscripcion
from registro.domain.exceptions import PlazoCancelacionVencido
from registro.domain.value_objects.estado_inscripcion import EstadoInscripcion
from shared.domain.value_objects.disciplina import Disciplina


def _inscripcion(**kwargs) -> Inscripcion:
    defaults = {
        "atleta_id": uuid4(),
        "torneo_id": uuid4(),
        "disciplinas": frozenset({Disciplina.STA}),
    }
    defaults.update(kwargs)
    return Inscripcion(**defaults)


def test_estado_inicial_es_activa():
    ins = _inscripcion()
    assert ins.estado == EstadoInscripcion.ACTIVA


def test_cancelar_antes_del_torneo():
    ins = _inscripcion()
    fecha_inicio = date(2026, 6, 10)
    ins.cancelar(date(2026, 6, 9), fecha_inicio)
    assert ins.estado == EstadoInscripcion.CANCELADA


def test_cancelar_el_dia_del_torneo_lanza_excepcion():
    ins = _inscripcion()
    fecha_inicio = date(2026, 6, 10)
    with pytest.raises(PlazoCancelacionVencido):
        ins.cancelar(date(2026, 6, 10), fecha_inicio)


def test_cancelar_despues_del_torneo_lanza_excepcion():
    ins = _inscripcion()
    fecha_inicio = date(2026, 6, 10)
    with pytest.raises(PlazoCancelacionVencido):
        ins.cancelar(date(2026, 6, 11), fecha_inicio)


def test_inscripcion_tiene_fecha_inscripcion():
    ins = _inscripcion()
    assert isinstance(ins.fecha_inscripcion, datetime)


def test_inscripcion_tiene_id_generado():
    ins = _inscripcion()
    assert ins.inscripcion_id is not None


def test_disciplinas_es_frozenset():
    ins = _inscripcion(disciplinas=frozenset({Disciplina.STA, Disciplina.DNF}))
    assert isinstance(ins.disciplinas, frozenset)
    assert Disciplina.STA in ins.disciplinas
    assert Disciplina.DNF in ins.disciplinas


def test_adjuntar_apto_medico_registra_path():
    ins = _inscripcion()
    ins.adjuntar_apto_medico("data/adjuntos/id/apto_medico.pdf")
    assert ins.apto_medico_path == "data/adjuntos/id/apto_medico.pdf"


def test_adjuntar_constancia_pago_registra_path():
    ins = _inscripcion()
    ins.adjuntar_constancia_pago("data/adjuntos/id/constancia_pago.pdf")
    assert ins.constancia_pago_path == "data/adjuntos/id/constancia_pago.pdf"


def test_adjuntar_apto_medico_rechaza_path_vacio():
    ins = _inscripcion()
    with pytest.raises(ValueError, match="path no puede ser vacío"):
        ins.adjuntar_apto_medico(" ")


def test_adjuntar_constancia_pago_rechaza_path_vacio():
    ins = _inscripcion()
    with pytest.raises(ValueError, match="path no puede ser vacío"):
        ins.adjuntar_constancia_pago("")
