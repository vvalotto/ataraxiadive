"""Stream IDs canónicos para el BC Competencia.

Fuente única de verdad para el formato de los stream IDs del Event Store.
Un error de formato es silencioso (load retorna lista vacía), por lo que
centralizar aquí previene divergencias entre handlers.
"""
from uuid import UUID

from competencia.domain.value_objects.disciplina import Disciplina


def performance_stream_id(
    competencia_id: UUID,
    participante_id: UUID,
    disciplina: Disciplina,
) -> str:
    """Stream ID canónico para una Performance.

    Format: "performance-{competencia_id}-{participante_id}-{disciplina}"
    """
    return f"performance-{competencia_id}-{participante_id}-{disciplina.value}"


def competencia_stream_id(competencia_id: UUID) -> str:
    """Stream ID canónico para una Competencia.

    Format: "competencia-{competencia_id}"
    """
    return f"competencia-{competencia_id}"
