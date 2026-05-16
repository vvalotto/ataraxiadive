from __future__ import annotations

from uuid import uuid4

import pytest

from registro.domain.aggregates.organizador import Organizador


def _org(**kwargs) -> Organizador:
    defaults = dict(organizador_id=uuid4(), email="org@test.com")
    defaults.update(kwargs)
    return Organizador(**defaults)


class TestOrganizadorAggregate:
    def test_crear_minimo(self) -> None:
        org = _org()
        assert org.nombre_organizacion is None

    def test_crear_con_nombre(self) -> None:
        org = _org(nombre_organizacion="Club Apnea BA")
        assert org.nombre_organizacion == "Club Apnea BA"

    def test_email_invalido_lanza_error(self) -> None:
        with pytest.raises(ValueError, match="email"):
            _org(email="no-es-email")

    def test_email_vacio_lanza_error(self) -> None:
        with pytest.raises(ValueError, match="email"):
            _org(email="")

    def test_nombre_organizacion_vacio_lanza_error(self) -> None:
        with pytest.raises(ValueError, match="nombre_organizacion"):
            _org(nombre_organizacion="")

    def test_nombre_organizacion_espacios_lanza_error(self) -> None:
        with pytest.raises(ValueError, match="nombre_organizacion"):
            _org(nombre_organizacion="   ")

    def test_actualizar_nombre(self) -> None:
        org = _org()
        org.actualizar(nombre_organizacion="Federación Apnea Sur")
        assert org.nombre_organizacion == "Federación Apnea Sur"

    def test_actualizar_nombre_a_null_limpia_campo(self) -> None:
        org = _org(nombre_organizacion="Club Viejo")
        org.actualizar(nombre_organizacion=None)
        assert org.nombre_organizacion is None

    def test_actualizar_nombre_vacio_lanza_error(self) -> None:
        org = _org(nombre_organizacion="Club Viejo")
        with pytest.raises(ValueError, match="nombre_organizacion"):
            org.actualizar(nombre_organizacion="")

    def test_actualizar_nombre_espacios_lanza_error(self) -> None:
        org = _org()
        with pytest.raises(ValueError, match="nombre_organizacion"):
            org.actualizar(nombre_organizacion="   ")
