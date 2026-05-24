from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from registro.domain.aggregates.inscripcion import Inscripcion
from registro.domain.exceptions import PlazoCancelacionVencido
from registro.domain.value_objects.estado_aceptacion import EstadoAceptacion
from registro.domain.value_objects.estado_inscripcion import EstadoInscripcion
from shared.domain.value_objects.disciplina import Disciplina
from shared.domain.value_objects.unidad_medida import UnidadMedida


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


def test_from_row_reconstituye_inscripcion_con_ap_y_adjuntos():
    inscripcion_id = uuid4()
    atleta_id = uuid4()
    torneo_id = uuid4()

    ins = Inscripcion.from_row(
        {
            "inscripcion_id": str(inscripcion_id),
            "atleta_id": str(atleta_id),
            "torneo_id": str(torneo_id),
            "disciplinas": '["STA", "DNF"]',
            "estado": "ACTIVA",
            "fecha_inscripcion": "2026-05-09T12:30:00",
            "ap_por_disciplina": (
                '{"STA": {"valor": "120", "unidad": "Segundos"}, '
                '"DNF": {"valor": "75", "unidad": "Metros"}}'
            ),
            "apto_medico_path": "data/adjuntos/ins/apto.pdf",
            "constancia_pago_path": "data/adjuntos/ins/pago.pdf",
        }
    )

    assert ins.inscripcion_id == inscripcion_id
    assert ins.atleta_id == atleta_id
    assert ins.torneo_id == torneo_id
    assert ins.disciplinas == frozenset({Disciplina.STA, Disciplina.DNF})
    assert ins.estado == EstadoInscripcion.ACTIVA
    assert ins.fecha_inscripcion == datetime(2026, 5, 9, 12, 30)
    assert ins.ap_por_disciplina[Disciplina.STA].valor == Decimal("120")
    assert ins.ap_por_disciplina[Disciplina.STA].unidad == UnidadMedida.Segundos
    assert ins.ap_por_disciplina[Disciplina.DNF].valor == Decimal("75")
    assert ins.ap_por_disciplina[Disciplina.DNF].unidad == UnidadMedida.Metros
    assert ins.apto_medico_path == "data/adjuntos/ins/apto.pdf"
    assert ins.constancia_pago_path == "data/adjuntos/ins/pago.pdf"


def test_estado_aceptacion_default_es_aceptado():
    ins = _inscripcion()
    assert ins.estado_aceptacion == EstadoAceptacion.ACEPTADO


def test_cambiar_aceptacion_a_rechazado():
    ins = _inscripcion()
    ins.cambiar_aceptacion(EstadoAceptacion.RECHAZADO)
    assert ins.estado_aceptacion == EstadoAceptacion.RECHAZADO


def test_cambiar_aceptacion_volver_a_aceptado():
    ins = _inscripcion()
    ins.cambiar_aceptacion(EstadoAceptacion.RECHAZADO)
    ins.cambiar_aceptacion(EstadoAceptacion.ACEPTADO)
    assert ins.estado_aceptacion == EstadoAceptacion.ACEPTADO


def test_from_row_reconstruye_estado_aceptacion_rechazado():
    ins = Inscripcion.from_row(
        {
            "inscripcion_id": str(uuid4()),
            "atleta_id": str(uuid4()),
            "torneo_id": str(uuid4()),
            "disciplinas": '["STA"]',
            "estado": "ACTIVA",
            "fecha_inscripcion": "2026-05-09T12:30:00",
            "ap_por_disciplina": "{}",
            "apto_medico_path": None,
            "constancia_pago_path": None,
            "estado_aceptacion": "RECHAZADO",
        }
    )
    assert ins.estado_aceptacion == EstadoAceptacion.RECHAZADO


def test_from_row_sin_estado_aceptacion_usa_default():
    ins = Inscripcion.from_row(
        {
            "inscripcion_id": str(uuid4()),
            "atleta_id": str(uuid4()),
            "torneo_id": str(uuid4()),
            "disciplinas": '["STA"]',
            "estado": "ACTIVA",
            "fecha_inscripcion": "2026-05-09T12:30:00",
            "ap_por_disciplina": "{}",
            "apto_medico_path": None,
            "constancia_pago_path": None,
        }
    )
    assert ins.estado_aceptacion == EstadoAceptacion.ACEPTADO


def test_from_row_reconstituye_ap_vacio():
    ins = Inscripcion.from_row(
        {
            "inscripcion_id": str(uuid4()),
            "atleta_id": str(uuid4()),
            "torneo_id": str(uuid4()),
            "disciplinas": '["STA"]',
            "estado": "ACTIVA",
            "fecha_inscripcion": "2026-05-09T12:30:00",
            "ap_por_disciplina": "{}",
            "apto_medico_path": None,
            "constancia_pago_path": None,
        }
    )

    assert ins.ap_por_disciplina == {}
    assert ins.apto_medico_path is None
    assert ins.constancia_pago_path is None
