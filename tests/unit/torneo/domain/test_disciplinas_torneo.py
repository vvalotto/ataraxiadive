"""Tests unitarios — Torneo: asignar_disciplinas + asignar_juez [US-3.4.1]"""

from __future__ import annotations

from datetime import date
from uuid import uuid4

import pytest

from shared.domain.value_objects.disciplina import Disciplina
from torneo.domain.aggregates.torneo import Torneo
from torneo.domain.exceptions import AsignacionNoPermitida, DisciplinaNoEnTorneo
from torneo.domain.value_objects.entidad_organizadora import EntidadOrganizadora
from torneo.domain.value_objects.sede import Sede


def _torneo(**kwargs: object) -> Torneo:
    defaults = dict(
        nombre="Copa Sur",
        descripcion="Desc",
        fecha_inicio=date(2026, 6, 1),
        fecha_fin=date(2026, 6, 3),
        sede=Sede("Piscina Central", "Buenos Aires", "Argentina"),
        entidad_organizadora=EntidadOrganizadora("FAADS", "federacion"),
    )
    defaults.update(kwargs)
    return Torneo(**defaults)  # type: ignore[arg-type]


# ── DisciplinaTorneo VO ───────────────────────────────────────────────────────


class TestDisciplinaTorneoVO:
    def test_con_juez_retorna_nueva_instancia(self) -> None:
        from torneo.domain.value_objects.disciplina_torneo import DisciplinaTorneo

        dt = DisciplinaTorneo(disciplina=Disciplina.STA)
        juez = uuid4()
        dt2 = dt.con_juez(juez)
        assert dt2.juez_id == juez
        assert dt.juez_id is None  # inmutabilidad

    def test_serializar_y_deserializar(self) -> None:
        from torneo.domain.value_objects.disciplina_torneo import DisciplinaTorneo

        juez = uuid4()
        dt = DisciplinaTorneo(disciplina=Disciplina.DNF, juez_id=juez)
        data = dt.to_dict()
        dt2 = DisciplinaTorneo.from_dict(data)
        assert dt2.disciplina == Disciplina.DNF
        assert dt2.juez_id == juez

    def test_serializar_sin_juez(self) -> None:
        from torneo.domain.value_objects.disciplina_torneo import DisciplinaTorneo

        dt = DisciplinaTorneo(disciplina=Disciplina.STA)
        data = dt.to_dict()
        assert data["juez_id"] is None
        dt2 = DisciplinaTorneo.from_dict(data)
        assert dt2.juez_id is None


# ── asignar_disciplinas ───────────────────────────────────────────────────────


class TestAsignarDisciplinas:
    def test_asignar_disciplinas_happy_path(self) -> None:
        t = _torneo()
        t.asignar_disciplinas(frozenset({Disciplina.STA, Disciplina.DNF, Disciplina.DYNB}))
        assert len(t.disciplinas_torneo) == 3
        assert all(dt.juez_id is None for dt in t.disciplinas_torneo)

    def test_disciplinas_inicialmente_vacias(self) -> None:
        t = _torneo()
        assert t.disciplinas_torneo == []

    def test_disciplinas_invalidas_sp3(self) -> None:
        t = _torneo()
        with pytest.raises(ValueError):
            t.asignar_disciplinas(frozenset({Disciplina.CNF}))

    def test_asignar_en_estado_inscripcion_abierta(self) -> None:
        t = _torneo()
        t.abrir_inscripcion()
        t.asignar_disciplinas(frozenset({Disciplina.STA}))
        assert len(t.disciplinas_torneo) == 1

    def test_asignar_en_estado_preparacion(self) -> None:
        t = _torneo()
        t.abrir_inscripcion()
        t.cerrar_inscripcion()
        t.asignar_disciplinas(frozenset({Disciplina.STA}))
        assert len(t.disciplinas_torneo) == 1

    def test_asignar_en_estado_ejecucion_falla(self) -> None:
        t = _torneo()
        t.abrir_inscripcion()
        t.cerrar_inscripcion()
        t.asignar_disciplinas(frozenset({Disciplina.STA}))
        t.iniciar_ejecucion()
        with pytest.raises(AsignacionNoPermitida):
            t.asignar_disciplinas(frozenset({Disciplina.DNF}))

    def test_asignar_en_estado_premiacion_falla(self) -> None:
        t = _torneo()
        t.abrir_inscripcion()
        t.cerrar_inscripcion()
        t.asignar_disciplinas(frozenset({Disciplina.STA}))
        t.iniciar_ejecucion()
        t.iniciar_premiacion()
        with pytest.raises(AsignacionNoPermitida):
            t.asignar_disciplinas(frozenset({Disciplina.DNF}))

    def test_reasignar_disciplinas_sobreescribe(self) -> None:
        t = _torneo()
        t.asignar_disciplinas(frozenset({Disciplina.STA, Disciplina.DNF}))
        t.asignar_disciplinas(frozenset({Disciplina.DYNB}))
        assert len(t.disciplinas_torneo) == 1
        assert t.disciplinas_torneo[0].disciplina == Disciplina.DYNB


# ── asignar_juez ─────────────────────────────────────────────────────────────


class TestAsignarJuez:
    def test_asignar_juez_happy_path(self) -> None:
        t = _torneo()
        t.asignar_disciplinas(frozenset({Disciplina.STA}))
        juez = uuid4()
        t.asignar_juez(Disciplina.STA, juez)
        assert t.disciplinas_torneo[0].juez_id == juez

    def test_reasignar_juez_permitido(self) -> None:
        t = _torneo()
        t.asignar_disciplinas(frozenset({Disciplina.STA}))
        juez1, juez2 = uuid4(), uuid4()
        t.asignar_juez(Disciplina.STA, juez1)
        t.asignar_juez(Disciplina.STA, juez2)
        assert t.disciplinas_torneo[0].juez_id == juez2

    def test_asignar_juez_disciplina_no_en_torneo(self) -> None:
        t = _torneo()
        t.asignar_disciplinas(frozenset({Disciplina.STA}))
        with pytest.raises(DisciplinaNoEnTorneo):
            t.asignar_juez(Disciplina.DYN, uuid4())

    def test_asignar_juez_sin_disciplinas_falla(self) -> None:
        t = _torneo()
        with pytest.raises(DisciplinaNoEnTorneo):
            t.asignar_juez(Disciplina.STA, uuid4())

    def test_asignar_juez_estado_ejecucion_falla(self) -> None:
        t = _torneo()
        t.abrir_inscripcion()
        t.cerrar_inscripcion()
        t.asignar_disciplinas(frozenset({Disciplina.STA}))
        t.iniciar_ejecucion()
        with pytest.raises(AsignacionNoPermitida):
            t.asignar_juez(Disciplina.STA, uuid4())


# ── obtener_disciplinas_de_juez ───────────────────────────────────────────────


class TestObtenerDisciplinasDeJuez:
    def test_retorna_disciplinas_del_juez(self) -> None:
        t = _torneo()
        t.asignar_disciplinas(frozenset({Disciplina.STA, Disciplina.DNF, Disciplina.DYNB}))
        juez = uuid4()
        t.asignar_juez(Disciplina.STA, juez)
        t.asignar_juez(Disciplina.DNF, juez)
        resultado = t.obtener_disciplinas_de_juez(juez)
        assert set(resultado) == {Disciplina.STA, Disciplina.DNF}

    def test_juez_sin_disciplinas_retorna_vacio(self) -> None:
        t = _torneo()
        t.asignar_disciplinas(frozenset({Disciplina.STA}))
        assert t.obtener_disciplinas_de_juez(uuid4()) == []

    def test_no_mezcla_disciplinas_de_distintos_jueces(self) -> None:
        t = _torneo()
        t.asignar_disciplinas(frozenset({Disciplina.STA, Disciplina.DNF}))
        juez1, juez2 = uuid4(), uuid4()
        t.asignar_juez(Disciplina.STA, juez1)
        t.asignar_juez(Disciplina.DNF, juez2)
        assert t.obtener_disciplinas_de_juez(juez1) == [Disciplina.STA]
        assert t.obtener_disciplinas_de_juez(juez2) == [Disciplina.DNF]
