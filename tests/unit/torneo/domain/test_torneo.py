from datetime import date
from uuid import UUID

import pytest

from torneo.domain.aggregates.torneo import Torneo
from torneo.domain.exceptions import TorneoCerrado, TransicionEstadoInvalida
from torneo.domain.value_objects.entidad_organizadora import EntidadOrganizadora
from torneo.domain.value_objects.estado_torneo import EstadoTorneo
from torneo.domain.value_objects.grupo_etario import GrupoEtario
from torneo.domain.value_objects.sede import Sede


@pytest.fixture
def sede() -> Sede:
    return Sede(nombre="Club Náutico", ciudad="Buenos Aires", pais="Argentina")


@pytest.fixture
def entidad() -> EntidadOrganizadora:
    return EntidadOrganizadora(nombre="FADA", tipo="FEDERACION")


@pytest.fixture
def torneo(sede: Sede, entidad: EntidadOrganizadora) -> Torneo:
    return Torneo(
        nombre="Open Nacional 2026",
        descripcion="Torneo anual",
        fecha_inicio=date(2026, 6, 1),
        fecha_fin=date(2026, 6, 3),
        sede=sede,
        entidad_organizadora=entidad,
    )


def _torneo_en_estado(estado: EstadoTorneo, sede: Sede, entidad: EntidadOrganizadora) -> Torneo:
    t = Torneo(
        nombre="Torneo Test",
        descripcion="",
        fecha_inicio=date(2026, 6, 1),
        fecha_fin=date(2026, 6, 3),
        sede=sede,
        entidad_organizadora=entidad,
    )
    secuencia = [
        EstadoTorneo.INSCRIPCION_ABIERTA,
        EstadoTorneo.PREPARACION,
        EstadoTorneo.EJECUCION,
        EstadoTorneo.PREMIACION,
        EstadoTorneo.CERRADO,
    ]
    acciones = {
        EstadoTorneo.INSCRIPCION_ABIERTA: t.abrir_inscripcion,
        EstadoTorneo.PREPARACION: t.cerrar_inscripcion,
        EstadoTorneo.EJECUCION: t.iniciar_ejecucion,
        EstadoTorneo.PREMIACION: t.iniciar_premiacion,
        EstadoTorneo.CERRADO: t.cerrar,
    }
    for s in secuencia:
        if t.estado == estado:
            break
        acciones[s]()
    return t


class TestCreacion:
    def test_crear_torneo_valido(self, torneo: Torneo) -> None:
        assert torneo.estado == EstadoTorneo.CREADO
        assert isinstance(torneo.torneo_id, UUID)
        assert torneo.nombre == "Open Nacional 2026"

    def test_nombre_vacio_lanza_error(self, sede: Sede, entidad: EntidadOrganizadora) -> None:
        with pytest.raises(ValueError, match="nombre"):
            Torneo(
                nombre="",
                descripcion="",
                fecha_inicio=date(2026, 6, 1),
                fecha_fin=date(2026, 6, 3),
                sede=sede,
                entidad_organizadora=entidad,
            )

    def test_nombre_solo_espacios_lanza_error(
        self, sede: Sede, entidad: EntidadOrganizadora
    ) -> None:
        with pytest.raises(ValueError, match="nombre"):
            Torneo(
                nombre="   ",
                descripcion="",
                fecha_inicio=date(2026, 6, 1),
                fecha_fin=date(2026, 6, 3),
                sede=sede,
                entidad_organizadora=entidad,
            )

    def test_fecha_fin_anterior_lanza_error(self, sede: Sede, entidad: EntidadOrganizadora) -> None:
        with pytest.raises(ValueError, match="fecha"):
            Torneo(
                nombre="Test",
                descripcion="",
                fecha_inicio=date(2026, 6, 3),
                fecha_fin=date(2026, 6, 1),
                sede=sede,
                entidad_organizadora=entidad,
            )

    def test_fecha_fin_igual_fecha_inicio_es_valido(
        self, sede: Sede, entidad: EntidadOrganizadora
    ) -> None:
        t = Torneo(
            nombre="Test",
            descripcion="",
            fecha_inicio=date(2026, 6, 1),
            fecha_fin=date(2026, 6, 1),
            sede=sede,
            entidad_organizadora=entidad,
        )
        assert t.estado == EstadoTorneo.CREADO

    def test_grupo_etario_default_es_senior(self, torneo: Torneo) -> None:
        assert torneo.grupos_etarios == frozenset({GrupoEtario.SENIOR})

    def test_grupos_etarios_multiples_son_validos(
        self, sede: Sede, entidad: EntidadOrganizadora
    ) -> None:
        t = Torneo(
            nombre="Test",
            descripcion="",
            fecha_inicio=date(2026, 6, 1),
            fecha_fin=date(2026, 6, 1),
            sede=sede,
            entidad_organizadora=entidad,
            grupos_etarios=frozenset({GrupoEtario.JUNIOR, GrupoEtario.MASTER}),
        )
        assert t.grupos_etarios == frozenset({GrupoEtario.JUNIOR, GrupoEtario.MASTER})

    def test_grupos_etarios_vacio_lanza_error(
        self, sede: Sede, entidad: EntidadOrganizadora
    ) -> None:
        with pytest.raises(ValueError, match="grupo etario"):
            Torneo(
                nombre="Test",
                descripcion="",
                fecha_inicio=date(2026, 6, 1),
                fecha_fin=date(2026, 6, 1),
                sede=sede,
                entidad_organizadora=entidad,
                grupos_etarios=frozenset(),
            )


class TestTransiciones:
    def test_ciclo_completo(self, torneo: Torneo) -> None:
        torneo.abrir_inscripcion()
        assert torneo.estado == EstadoTorneo.INSCRIPCION_ABIERTA
        torneo.cerrar_inscripcion()
        assert torneo.estado == EstadoTorneo.PREPARACION
        torneo.iniciar_ejecucion()
        assert torneo.estado == EstadoTorneo.EJECUCION
        torneo.iniciar_premiacion()
        assert torneo.estado == EstadoTorneo.PREMIACION
        torneo.cerrar()
        assert torneo.estado == EstadoTorneo.CERRADO

    def test_retroceso_ejecucion_a_preparacion(
        self, sede: Sede, entidad: EntidadOrganizadora
    ) -> None:
        t = _torneo_en_estado(EstadoTorneo.EJECUCION, sede, entidad)
        t.volver_a_preparacion()
        assert t.estado == EstadoTorneo.PREPARACION

    def test_transicion_invalida_creado_a_ejecucion(self, torneo: Torneo) -> None:
        with pytest.raises(TransicionEstadoInvalida):
            torneo.iniciar_ejecucion()

    def test_transicion_invalida_desde_cancelado(self, torneo: Torneo) -> None:
        torneo.abrir_inscripcion()
        torneo.cancelar()
        with pytest.raises(TransicionEstadoInvalida):
            torneo.abrir_inscripcion()

    def test_no_se_puede_avanzar_desde_cerrado(
        self, sede: Sede, entidad: EntidadOrganizadora
    ) -> None:
        t = _torneo_en_estado(EstadoTorneo.CERRADO, sede, entidad)
        with pytest.raises(TorneoCerrado):
            t.abrir_inscripcion()


class TestCancelar:
    def test_cancelar_desde_inscripcion_abierta(self, torneo: Torneo) -> None:
        torneo.abrir_inscripcion()
        torneo.cancelar()
        assert torneo.estado == EstadoTorneo.CANCELADO

    def test_cancelar_desde_preparacion(self, sede: Sede, entidad: EntidadOrganizadora) -> None:
        t = _torneo_en_estado(EstadoTorneo.PREPARACION, sede, entidad)
        t.cancelar()
        assert t.estado == EstadoTorneo.CANCELADO

    def test_cancelar_desde_ejecucion(self, sede: Sede, entidad: EntidadOrganizadora) -> None:
        t = _torneo_en_estado(EstadoTorneo.EJECUCION, sede, entidad)
        t.cancelar()
        assert t.estado == EstadoTorneo.CANCELADO

    def test_cancelar_torneo_cerrado_lanza_error(
        self, sede: Sede, entidad: EntidadOrganizadora
    ) -> None:
        t = _torneo_en_estado(EstadoTorneo.CERRADO, sede, entidad)
        with pytest.raises(TorneoCerrado):
            t.cancelar()

    def test_cancelar_torneo_ya_cancelado_lanza_error(self, torneo: Torneo) -> None:
        torneo.abrir_inscripcion()
        torneo.cancelar()
        with pytest.raises(TransicionEstadoInvalida):
            torneo.cancelar()


class TestValueObjects:
    def test_sede_es_inmutable(self, sede: Sede) -> None:
        with pytest.raises(Exception):
            sede.nombre = "otro"  # type: ignore[misc]

    def test_entidad_organizadora_es_inmutable(self, entidad: EntidadOrganizadora) -> None:
        with pytest.raises(Exception):
            entidad.nombre = "otro"  # type: ignore[misc]

    def test_estado_torneo_valores(self) -> None:
        assert EstadoTorneo.CREADO == "CREADO"
        assert EstadoTorneo.CANCELADO == "CANCELADO"
