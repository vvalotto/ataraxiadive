"""Schemas Pydantic para los request bodies del BC Competencia."""

from uuid import UUID

from pydantic import BaseModel

from competencia.domain.value_objects.disciplina import Disciplina


class CambioGrillaSchema(BaseModel):
    """Schema de un cambio individual sobre la Grilla de Salida."""

    performance_id: UUID
    campo: str
    valor_nuevo: int


class AjustarGrillaBody(BaseModel):
    """Body del endpoint POST /ajustar-grilla."""

    disciplina: Disciplina
    cambios: list[CambioGrillaSchema]


class ConfirmarGrillaBody(BaseModel):
    """Body del endpoint POST /confirmar-grilla."""

    disciplina: Disciplina


class IniciarCompetenciaBody(BaseModel):
    """Body del endpoint POST /iniciar."""

    disciplina: Disciplina
    juez_id: str
