from __future__ import annotations

from datetime import date
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from registro.application.commands.actualizar_atleta import (
    ActualizarAtletaCommand,
    ActualizarAtletaHandler,
)
from registro.domain.aggregates.atleta import Atleta
from registro.domain.exceptions import AtletaNoEncontrado
from registro.domain.value_objects.categoria import Categoria


def _atleta() -> Atleta:
    return Atleta(
        atleta_id=uuid4(),
        nombre="Ana",
        apellido="Garcia",
        email="ana@test.com",
        fecha_nacimiento=date(1990, 5, 10),
        categoria=Categoria.SENIOR_FEMENINO,
        club="Poseidon",
    )


class TestAtletaActualizar:
    def test_actualizar_nombre(self) -> None:
        atleta = _atleta()
        atleta.actualizar(nombre="Juan")
        assert atleta.nombre == "Juan"

    def test_actualizar_club(self) -> None:
        atleta = _atleta()
        atleta.actualizar(club="Neptuno")
        assert atleta.club == "Neptuno"

    def test_actualizar_categoria(self) -> None:
        atleta = _atleta()
        atleta.actualizar(categoria=Categoria.MASTER_FEMENINO)
        assert atleta.categoria == Categoria.MASTER_FEMENINO

    def test_patch_no_borra_campos_no_provistos(self) -> None:
        atleta = _atleta()
        atleta.actualizar(club="Neptuno")
        assert atleta.nombre == "Ana"
        assert atleta.apellido == "Garcia"
        assert atleta.categoria == Categoria.SENIOR_FEMENINO

    def test_nombre_vacio_lanza_error(self) -> None:
        atleta = _atleta()
        with pytest.raises(ValueError, match="nombre"):
            atleta.actualizar(nombre="   ")

    def test_club_vacio_lanza_error(self) -> None:
        atleta = _atleta()
        with pytest.raises(ValueError, match="club"):
            atleta.actualizar(club="")

    def test_sin_argumentos_no_cambia_nada(self) -> None:
        atleta = _atleta()
        atleta.actualizar()
        assert atleta.nombre == "Ana"
        assert atleta.club == "Poseidon"

    def test_actualizar_fecha_nacimiento(self) -> None:
        atleta = _atleta()
        nueva_fecha = date(1985, 3, 20)
        atleta.actualizar(fecha_nacimiento=nueva_fecha)
        assert atleta.fecha_nacimiento == nueva_fecha

    def test_fecha_nacimiento_futura_lanza_error(self) -> None:
        atleta = _atleta()
        with pytest.raises(ValueError, match="fecha_nacimiento"):
            atleta.actualizar(fecha_nacimiento=date(2099, 1, 1))

    def test_actualizar_brevet(self) -> None:
        atleta = _atleta()
        atleta.actualizar(brevet="AIDA-3")
        assert atleta.brevet == "AIDA-3"

    def test_actualizar_brevet_vacio_lo_limpia(self) -> None:
        atleta = _atleta()
        atleta.actualizar(brevet="AIDA-3")
        atleta.actualizar(brevet="")
        assert atleta.brevet is None


class TestActualizarAtletaHandler:
    @pytest.mark.asyncio
    async def test_handler_actualiza_y_persiste(self) -> None:
        atleta = _atleta()
        repo = AsyncMock()
        repo.find_by_email.return_value = atleta

        result = await ActualizarAtletaHandler(repo).handle(
            ActualizarAtletaCommand(email="ana@test.com", club="Neptuno")
        )

        repo.save.assert_awaited_once_with(atleta)
        assert result.club == "Neptuno"

    @pytest.mark.asyncio
    async def test_handler_lanza_si_no_encontrado(self) -> None:
        repo = AsyncMock()
        repo.find_by_email.return_value = None

        with pytest.raises(AtletaNoEncontrado):
            await ActualizarAtletaHandler(repo).handle(
                ActualizarAtletaCommand(email="noexiste@test.com", nombre="X")
            )

    @pytest.mark.asyncio
    async def test_handler_semántica_patch(self) -> None:
        atleta = _atleta()
        repo = AsyncMock()
        repo.find_by_email.return_value = atleta

        await ActualizarAtletaHandler(repo).handle(
            ActualizarAtletaCommand(email="ana@test.com", club="Neptuno")
        )

        assert atleta.nombre == "Ana"
        assert atleta.apellido == "Garcia"
        assert atleta.club == "Neptuno"
