"""
Tests de integración del dominio Torneo — US-3.1.1.
Verifica la coherencia entre aggregate, value objects, excepciones y puerto.
Los tests de repositorio SQLite se implementan en US-3.1.2.
"""

from datetime import date
from uuid import UUID

import pytest

from torneo.domain import (
    EntidadOrganizadora,
    EstadoTorneo,
    Sede,
    Torneo,
    TorneoRepositoryPort,
    TransicionEstadoInvalida,
)


def make_torneo() -> Torneo:
    return Torneo(
        nombre="Copa Patagonia 2026",
        descripcion="Clasificatorio regional",
        fecha_inicio=date(2026, 9, 10),
        fecha_fin=date(2026, 9, 12),
        sede=Sede(nombre="Puerto Madryn Club", ciudad="Puerto Madryn", pais="Argentina"),
        entidad_organizadora=EntidadOrganizadora(nombre="FADA Patagonia", tipo="FEDERACION"),
    )


def test_torneo_id_es_uuid_unico() -> None:
    t1 = make_torneo()
    t2 = make_torneo()
    assert isinstance(t1.torneo_id, UUID)
    assert t1.torneo_id != t2.torneo_id


def test_flujo_cancelacion_mitad_ciclo() -> None:
    t = make_torneo()
    t.abrir_inscripcion()
    t.cerrar_inscripcion()
    t.iniciar_ejecucion()
    t.volver_a_preparacion()
    t.iniciar_ejecucion()
    t.cancelar()
    assert t.estado == EstadoTorneo.CANCELADO


def test_flujo_retroceso_multiple() -> None:
    """Ejecución→Preparación puede repetirse varias veces."""
    t = make_torneo()
    t.abrir_inscripcion()
    t.cerrar_inscripcion()
    t.iniciar_ejecucion()
    t.volver_a_preparacion()
    t.iniciar_ejecucion()
    t.volver_a_preparacion()
    assert t.estado == EstadoTorneo.PREPARACION


def test_puerto_repositorio_es_abstracto() -> None:
    """TorneoRepositoryPort no puede instanciarse directamente."""
    with pytest.raises(TypeError):
        TorneoRepositoryPort()  # type: ignore[abstract]


def test_exports_dominio_completos() -> None:
    """Todos los símbolos públicos del dominio están exportados desde torneo.domain."""
    from torneo.domain import (  # noqa: F401
        EntidadOrganizadora,
        EstadoTorneo,
        Sede,
        Torneo,
        TorneoCerrado,
        TorneoNoEncontrado,
        TorneoRepositoryPort,
        TransicionEstadoInvalida,
    )
