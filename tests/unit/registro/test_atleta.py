from datetime import date, timedelta
from uuid import uuid4

import pytest

from registro.domain.aggregates.atleta import Atleta
from registro.domain.value_objects.categoria import Categoria


def _valid_atleta(**kwargs) -> Atleta:
    defaults = dict(
        atleta_id=uuid4(),
        nombre="Ana",
        apellido="García",
        email="ana@example.com",
        fecha_nacimiento=date(1990, 5, 15),
    )
    defaults.update(kwargs)
    return Atleta(**defaults)


class TestAtletaCreacion:
    def test_crea_atleta_minimo(self):
        atleta = _valid_atleta()
        assert atleta.nombre == "Ana"
        assert atleta.club is None
        assert atleta.categoria is None
        assert atleta.dni is None
        assert atleta.telefono is None
        assert atleta.brevet is None

    def test_crea_atleta_con_todos_los_campos(self):
        atleta = _valid_atleta(
            club="Club Apnea Norte",
            categoria=Categoria.SENIOR_FEMENINO,
            brevet="AIDA-3",
            dni="30123456",
            telefono="1155559999",
        )
        assert atleta.club == "Club Apnea Norte"
        assert atleta.categoria == Categoria.SENIOR_FEMENINO
        assert atleta.brevet == "AIDA-3"
        assert atleta.dni == "30123456"
        assert atleta.telefono == "1155559999"

    def test_todas_las_categorias(self):
        for cat in Categoria:
            atleta = _valid_atleta(categoria=cat)
            assert atleta.categoria == cat

    def test_club_none_es_valido(self):
        atleta = _valid_atleta(club=None)
        assert atleta.club is None

    def test_categoria_none_es_valida(self):
        atleta = _valid_atleta(categoria=None)
        assert atleta.categoria is None


class TestAtletaInvariantes:
    def test_inv_a01_nombre_vacio(self):
        with pytest.raises(ValueError, match="INV-A-01"):
            _valid_atleta(nombre="")

    def test_inv_a01_nombre_espacios(self):
        with pytest.raises(ValueError, match="INV-A-01"):
            _valid_atleta(nombre="   ")

    def test_inv_a01_apellido_vacio(self):
        with pytest.raises(ValueError, match="INV-A-01"):
            _valid_atleta(apellido="")

    def test_inv_a02_email_invalido(self):
        with pytest.raises(ValueError, match="INV-A-02"):
            _valid_atleta(email="no-es-email")

    def test_inv_a02_email_sin_dominio(self):
        with pytest.raises(ValueError, match="INV-A-02"):
            _valid_atleta(email="ana@")

    def test_inv_a04_fecha_hoy(self):
        with pytest.raises(ValueError, match="INV-A-04"):
            _valid_atleta(fecha_nacimiento=date.today())

    def test_inv_a04_fecha_futura(self):
        with pytest.raises(ValueError, match="INV-A-04"):
            _valid_atleta(fecha_nacimiento=date.today() + timedelta(days=1))

    def test_club_vacio_lanza_error(self):
        with pytest.raises(ValueError, match="club"):
            _valid_atleta(club="")

    def test_club_solo_espacios_lanza_error(self):
        with pytest.raises(ValueError, match="club"):
            _valid_atleta(club="   ")

    def test_dni_vacio_lanza_error(self):
        with pytest.raises(ValueError, match="dni"):
            _valid_atleta(dni="")

    def test_telefono_vacio_lanza_error(self):
        with pytest.raises(ValueError, match="telefono"):
            _valid_atleta(telefono="")
