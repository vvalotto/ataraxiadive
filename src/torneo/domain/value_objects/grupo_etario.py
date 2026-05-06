from __future__ import annotations

from enum import StrEnum


class GrupoEtario(StrEnum):
    JUNIOR = "JUNIOR"
    SENIOR = "SENIOR"
    MASTER = "MASTER"


ORDEN_GRUPOS_ETARIOS: tuple[GrupoEtario, ...] = (
    GrupoEtario.JUNIOR,
    GrupoEtario.SENIOR,
    GrupoEtario.MASTER,
)


def ordenar_grupos_etarios(grupos: frozenset[GrupoEtario]) -> list[GrupoEtario]:
    return [grupo for grupo in ORDEN_GRUPOS_ETARIOS if grupo in grupos]
