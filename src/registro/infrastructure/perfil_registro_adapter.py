from __future__ import annotations

from uuid import UUID

from identidad.domain.ports.perfil_registro_port import PerfilRegistroPort
from identidad.domain.value_objects.rol import Rol
from registro.application.commands.registrar_atleta import (
    RegistrarAtletaCommand,
    RegistrarAtletaHandler,
)
from registro.application.commands.registrar_juez import (
    RegistrarJuezCommand,
    RegistrarJuezHandler,
)
from registro.application.commands.registrar_organizador import (
    RegistrarOrganizadorCommand,
    RegistrarOrganizadorHandler,
)
from registro.domain.exceptions import AtletaYaRegistrado, JuezYaRegistrado, OrganizadorYaRegistrado
from registro.domain.ports.atleta_repository_port import AtletaRepositoryPort
from registro.domain.ports.juez_repository_port import JuezRepositoryPort
from registro.domain.ports.organizador_repository_port import OrganizadorRepositoryPort


class PerfilRegistroAdapter(PerfilRegistroPort):
    def __init__(
        self,
        atleta_repo: AtletaRepositoryPort,
        juez_repo: JuezRepositoryPort,
        organizador_repo: OrganizadorRepositoryPort,
    ) -> None:
        self._atleta_handler = RegistrarAtletaHandler(atleta_repo)
        self._juez_handler = RegistrarJuezHandler(juez_repo)
        self._organizador_handler = RegistrarOrganizadorHandler(organizador_repo)

    async def crear_perfiles(
        self,
        usuario_id: UUID,
        nombre: str,
        apellido: str,
        email: str,
        roles: list[Rol],
        numero_licencia: str | None = None,
        federacion: str | None = None,
        nombre_organizacion: str | None = None,
    ) -> None:
        if Rol.ATLETA in roles:
            try:
                await self._atleta_handler.handle(
                    RegistrarAtletaCommand(nombre=nombre, apellido=apellido, email=email)
                )
            except AtletaYaRegistrado:
                pass

        if Rol.JUEZ in roles:
            try:
                await self._juez_handler.handle(
                    RegistrarJuezCommand(
                        email=email,
                        numero_licencia=numero_licencia,
                        federacion=federacion,
                    )
                )
            except JuezYaRegistrado:
                pass

        if Rol.ORGANIZADOR in roles:
            try:
                await self._organizador_handler.handle(
                    RegistrarOrganizadorCommand(
                        email=email,
                        nombre_organizacion=nombre_organizacion,
                    )
                )
            except OrganizadorYaRegistrado:
                pass
