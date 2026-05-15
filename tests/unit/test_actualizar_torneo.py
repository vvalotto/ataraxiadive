from __future__ import annotations

from datetime import date
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from torneo.domain.aggregates.torneo import Torneo
from torneo.domain.exceptions import EdicionNoPermitida, TorneoNoEncontrado
from torneo.domain.value_objects.entidad_organizadora import EntidadOrganizadora
from torneo.domain.value_objects.grupo_etario import GrupoEtario
from torneo.domain.value_objects.sede import Sede
from torneo.application.commands.actualizar_torneo import (
    ActualizarTorneoCommand,
    ActualizarTorneoHandler,
)


def _torneo(estado_str: str = "CREADO") -> Torneo:
    from torneo.domain.value_objects.estado_torneo import EstadoTorneo

    torneo = Torneo(
        torneo_id=uuid4(),
        nombre="Torneo Original",
        descripcion="Descripcion original",
        fecha_inicio=date(2026, 6, 1),
        fecha_fin=date(2026, 6, 3),
        sede=Sede(nombre="Piscina", ciudad="Buenos Aires", pais="AR"),
        entidad_organizadora=EntidadOrganizadora(nombre="AIDA", tipo="FEDERACION"),
        grupos_etarios=frozenset({GrupoEtario.SENIOR}),
    )
    if estado_str != "CREADO":
        torneo.estado = EstadoTorneo(estado_str)
    return torneo


def _cmd(torneo_id, nombre="Torneo Editado", ciudad="Cordoba") -> ActualizarTorneoCommand:
    return ActualizarTorneoCommand(
        torneo_id=torneo_id,
        nombre=nombre,
        descripcion="Descripcion editada",
        fecha_inicio=date(2026, 7, 1),
        fecha_fin=date(2026, 7, 3),
        sede_nombre="Club",
        sede_ciudad=ciudad,
        sede_pais="AR",
        grupos_etarios=frozenset({GrupoEtario.SENIOR, GrupoEtario.JUNIOR}),
    )


class TestTorneoActualizar:
    def test_actualizar_en_creado_modifica_campos(self) -> None:
        torneo = _torneo("CREADO")
        torneo.actualizar(
            nombre="Nuevo nombre",
            descripcion="Nueva desc",
            fecha_inicio=date(2026, 7, 1),
            fecha_fin=date(2026, 7, 3),
            sede=Sede(nombre="Club", ciudad="Rosario", pais="AR"),
            grupos_etarios=frozenset({GrupoEtario.JUNIOR}),
        )
        assert torneo.nombre == "Nuevo nombre"
        assert torneo.sede.ciudad == "Rosario"
        assert GrupoEtario.JUNIOR in torneo.grupos_etarios

    def test_actualizar_en_inscripcion_abierta_permitido(self) -> None:
        torneo = _torneo("INSCRIPCION_ABIERTA")
        torneo.actualizar(
            nombre="Editado",
            descripcion="desc",
            fecha_inicio=date(2026, 7, 1),
            fecha_fin=date(2026, 7, 3),
            sede=Sede(nombre="Club", ciudad="Mendoza", pais="AR"),
            grupos_etarios=frozenset({GrupoEtario.SENIOR}),
        )
        assert torneo.nombre == "Editado"

    def test_actualizar_en_ejecucion_lanza_edicion_no_permitida(self) -> None:
        torneo = _torneo("EJECUCION")
        with pytest.raises(EdicionNoPermitida):
            torneo.actualizar(
                nombre="X",
                descripcion="d",
                fecha_inicio=date(2026, 7, 1),
                fecha_fin=date(2026, 7, 3),
                sede=Sede(nombre="C", ciudad="C", pais="AR"),
                grupos_etarios=frozenset({GrupoEtario.SENIOR}),
            )

    def test_actualizar_no_toca_disciplinas(self) -> None:
        from shared.domain.value_objects.disciplina import Disciplina

        torneo = _torneo("CREADO")
        torneo.asignar_disciplinas(frozenset({Disciplina.STA, Disciplina.DNF}))
        disciplinas_antes = list(torneo.disciplinas_torneo)

        torneo.actualizar(
            nombre="Editado",
            descripcion="d",
            fecha_inicio=date(2026, 7, 1),
            fecha_fin=date(2026, 7, 3),
            sede=Sede(nombre="C", ciudad="C", pais="AR"),
            grupos_etarios=frozenset({GrupoEtario.SENIOR}),
        )
        assert torneo.disciplinas_torneo == disciplinas_antes


class TestActualizarTorneoHandler:
    @pytest.mark.asyncio
    async def test_handler_actualiza_y_persiste(self) -> None:
        torneo = _torneo("CREADO")
        repo = AsyncMock()
        repo.find_by_id.return_value = torneo
        handler = ActualizarTorneoHandler(repo)

        await handler.handle(_cmd(torneo.torneo_id))

        repo.save.assert_awaited_once_with(torneo)
        assert torneo.nombre == "Torneo Editado"

    @pytest.mark.asyncio
    async def test_handler_lanza_si_no_encontrado(self) -> None:
        repo = AsyncMock()
        repo.find_by_id.return_value = None
        handler = ActualizarTorneoHandler(repo)

        with pytest.raises(TorneoNoEncontrado):
            await handler.handle(_cmd(uuid4()))

    @pytest.mark.asyncio
    async def test_handler_lanza_si_estado_invalido(self) -> None:
        torneo = _torneo("EJECUCION")
        repo = AsyncMock()
        repo.find_by_id.return_value = torneo
        handler = ActualizarTorneoHandler(repo)

        with pytest.raises(EdicionNoPermitida):
            await handler.handle(_cmd(torneo.torneo_id))
