from __future__ import annotations

from uuid import uuid4

import pytest

from registro.domain.aggregates.juez import Juez


def _juez(**kwargs) -> Juez:
    defaults = dict(juez_id=uuid4(), email="juez@test.com")
    defaults.update(kwargs)
    return Juez(**defaults)


class TestJuezAggregate:
    def test_crear_juez_minimo(self) -> None:
        juez = _juez()
        assert juez.numero_licencia is None
        assert juez.federacion is None

    def test_crear_juez_completo(self) -> None:
        juez = _juez(numero_licencia="ARG-001", federacion="AIDA")
        assert juez.numero_licencia == "ARG-001"
        assert juez.federacion == "AIDA"

    def test_email_invalido_lanza_error(self) -> None:
        with pytest.raises(ValueError, match="email"):
            _juez(email="no-es-email")

    def test_email_vacio_lanza_error(self) -> None:
        with pytest.raises(ValueError, match="email"):
            _juez(email="")

    def test_numero_licencia_vacio_lanza_error(self) -> None:
        with pytest.raises(ValueError, match="numero_licencia"):
            _juez(numero_licencia="")

    def test_federacion_vacia_lanza_error(self) -> None:
        with pytest.raises(ValueError, match="federacion"):
            _juez(federacion="  ")

    def test_actualizar_numero_licencia(self) -> None:
        juez = _juez()
        juez.actualizar(numero_licencia="ARG-042")
        assert juez.numero_licencia == "ARG-042"

    def test_actualizar_federacion(self) -> None:
        juez = _juez()
        juez.actualizar(federacion="CMAS")
        assert juez.federacion == "CMAS"

    def test_actualizar_parcial_no_borra_otros(self) -> None:
        juez = _juez(numero_licencia="ARG-001", federacion="AIDA")
        juez.actualizar(numero_licencia="ARG-999")
        assert juez.federacion == "AIDA"

    def test_actualizar_sin_argumentos_no_cambia_nada(self) -> None:
        juez = _juez(numero_licencia="ARG-001")
        juez.actualizar()
        assert juez.numero_licencia == "ARG-001"

    def test_actualizar_numero_licencia_vacio_lanza_error(self) -> None:
        juez = _juez()
        with pytest.raises(ValueError, match="numero_licencia"):
            juez.actualizar(numero_licencia="")

    def test_actualizar_federacion_vacia_lanza_error(self) -> None:
        juez = _juez()
        with pytest.raises(ValueError, match="federacion"):
            juez.actualizar(federacion="")
