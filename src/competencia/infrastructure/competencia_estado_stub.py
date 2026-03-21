"""Adaptador stub de CompetenciaEstadoPort para SP1.

En SP1 el aggregate Competencia no existe. Este stub implementa el puerto
retornando siempre False (plazo activo, grilla no confirmada).

Se reemplaza en SP2 con la implementación real que lee el stream de Competencia.
"""
from __future__ import annotations

from uuid import UUID

from competencia.domain.ports.competencia_estado_port import CompetenciaEstadoPort
from competencia.domain.value_objects.disciplina import Disciplina


class StubCompetenciaEstadoAdapter(CompetenciaEstadoPort):
    """Implementación stub del puerto CompetenciaEstadoPort para SP1.

    Retorna siempre False: plazo activo y grilla no confirmada.
    Permite implementar y probar INV-P-03 e INV-P-04 sin el aggregate Competencia.
    """

    async def is_plazo_vencido(
        self, competencia_id: UUID, disciplina: Disciplina
    ) -> bool:
        """SP1 stub: plazo siempre activo."""
        return False

    async def is_grilla_confirmada(
        self, competencia_id: UUID, disciplina: Disciplina
    ) -> bool:
        """SP1 stub: grilla nunca confirmada."""
        return False
