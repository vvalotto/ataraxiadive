"""Test de integración E2E — US-3.3.2: Flujo Torneo → Registro → Competencia.

Valida el contrato implícito entre los 3 BCs incorporados en INC-3.1, INC-3.2 e INC-3.3:
  - atleta_id (Registro) == participante_id (Competencia)  [INV-E2E-01]
  - competencia referencia el torneo_id creado              [INV-E2E-02]
  - la grilla contiene exactamente los atletas con AP       [INV-E2E-03]

El vínculo Registro→Competencia es implícito en SP3: mismo UUID, sin ACL formal.
El ACL formal (AtletaInscripto → ParticipanteHabilitado) queda para SP4.

Patrón: handlers directos con SQLite en tmp_path (no HTTP).
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4

import aiosqlite
import pytest
import pytest_asyncio

from competencia.application.commands.configurar_intervalo_ot import (
    ConfigurarIntervaloOTCommand,
    ConfigurarIntervaloOTHandler,
)
from competencia.application.commands.confirmar_grilla import (
    ConfirmarGrillaCommand,
    ConfirmarGrillaHandler,
)
from competencia.application.commands.generar_grilla import (
    GenerarGrillaCommand,
    GenerarGrillaHandler,
)
from competencia.application.commands.registrar_ap import (
    RegistrarAPCommand,
    RegistrarAPHandler,
)
from competencia.application.queries.obtener_estado_competencia import (
    ObtenerEstadoCompetenciaHandler,
    ObtenerEstadoCompetenciaQuery,
)
from competencia.application.queries.obtener_grilla import (
    ObtenerGrillaHandler,
    ObtenerGrillaQuery,
)
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.unidad_medida import UnidadMedida
from competencia.infrastructure.event_store.sqlite_event_store import SQLiteEventStore
from competencia.infrastructure.repositories.competencia_estado_adapter import (
    CompetenciaEstadoAdapter,
)
from competencia.infrastructure.repositories.disciplina_descriptor_adapter import (
    DisciplinaDescriptorAdapter,
)
from competencia.infrastructure.repositories.performances_ap_adapter import (
    PerformancesAPAdapter,
)
from registro.application.commands.inscribir_atleta import (
    InscribirAtletaCommand,
    InscribirAtletaHandler,
)
from registro.application.commands.registrar_atleta import (
    RegistrarAtletaCommand,
    RegistrarAtletaHandler,
)
from registro.domain.value_objects.categoria import Categoria
from registro.infrastructure.acl.sqlite_torneo_consulta import SQLiteTorneoConsulta
from registro.infrastructure.repositories.sqlite_atleta_repository import (
    SQLiteAtletaRepository,
)
from registro.infrastructure.repositories.sqlite_inscripcion_repository import (
    SQLiteInscripcionRepository,
)
from shared.domain.value_objects.disciplina import Disciplina as SharedDisciplina
from torneo.application.commands.crear_torneo import CrearTorneoCommand, CrearTorneoHandler
from torneo.application.commands.transicionar_torneo import (
    AbrirInscripcionHandler,
    TransicionarTorneoCommand,
)
from torneo.infrastructure.repositories.sqlite_torneo_repository import (
    SQLiteTorneoRepository,
)

_CREATE_EVENTS_TABLE = """
    CREATE TABLE events (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        stream_id   TEXT    NOT NULL,
        event_type  TEXT    NOT NULL,
        payload     TEXT    NOT NULL,
        version     INTEGER NOT NULL,
        occurred_at TEXT    NOT NULL
            DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
        UNIQUE (stream_id, version)
    )
"""


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest_asyncio.fixture
async def infra(tmp_path):
    """Infraestructura compartida de los 3 BCs con paths SQLite coordinados.

    torneo.db es compartida entre SQLiteTorneoRepository (escritura)
    y SQLiteTorneoConsulta (lectura cross-BC desde Registro).
    """
    torneo_db = str(tmp_path / "torneo.db")
    registro_db = str(tmp_path / "registro.db")
    competencia_db = str(tmp_path / "competencia.db")

    # Inicializar tabla events del Event Store (requiere DDL explícito)
    async with aiosqlite.connect(competencia_db) as db:
        await db.execute(_CREATE_EVENTS_TABLE)
        await db.commit()

    torneo_repo = SQLiteTorneoRepository(db_path=torneo_db)
    atleta_repo = SQLiteAtletaRepository(db_path=registro_db)
    inscripcion_repo = SQLiteInscripcionRepository(db_path=registro_db)
    torneo_consulta = SQLiteTorneoConsulta(db_path=torneo_db)
    event_store = SQLiteEventStore(db_path=competencia_db)

    return {
        "torneo_repo": torneo_repo,
        "atleta_repo": atleta_repo,
        "inscripcion_repo": inscripcion_repo,
        "torneo_consulta": torneo_consulta,
        "event_store": event_store,
    }


async def _crear_torneo_abierto(torneo_repo) -> UUID:
    """Crea un torneo y lo abre para inscripción. Retorna torneo_id."""
    cmd = CrearTorneoCommand(
        nombre="Copa E2E 2026",
        descripcion="Torneo de integración E2E",
        fecha_inicio=date(2026, 9, 10),
        fecha_fin=date(2026, 9, 12),
        sede_nombre="Pileta Test",
        sede_ciudad="Buenos Aires",
        sede_pais="Argentina",
        entidad_nombre="FADA",
        entidad_tipo="FEDERACION",
    )
    torneo_id = await CrearTorneoHandler(torneo_repo).handle(cmd)
    await AbrirInscripcionHandler(torneo_repo).handle(TransicionarTorneoCommand(torneo_id))
    return torneo_id


async def _registrar_e_inscribir(
    atleta_repo, inscripcion_repo, torneo_consulta, torneo_id: UUID
) -> UUID:
    """Registra un atleta e inscribe en disciplina STA. Retorna atleta_id."""
    atleta_id = uuid4()
    await RegistrarAtletaHandler(atleta_repo).handle(
        RegistrarAtletaCommand(
            atleta_id=atleta_id,
            nombre="Juan",
            apellido="Perez",
            email="juan@test.com",
            fecha_nacimiento=date(1990, 1, 15),
            categoria=Categoria.SENIOR_MASCULINO,
        )
    )
    await InscribirAtletaHandler(inscripcion_repo, torneo_consulta).handle(
        InscribirAtletaCommand(
            atleta_id=atleta_id,
            torneo_id=torneo_id,
            disciplinas=frozenset({SharedDisciplina.STA}),
        )
    )
    return atleta_id


async def _configurar_competencia(event_store, torneo_id: UUID) -> UUID:
    """Configura una competencia STA con torneo_id. Retorna competencia_id."""
    competencia_id = uuid4()
    await ConfigurarIntervaloOTHandler(event_store).handle(
        ConfigurarIntervaloOTCommand(
            competencia_id=competencia_id,
            disciplina=Disciplina.STA,
            intervalo_minutos=5,
            configurado_por="organizador",
            torneo_id=torneo_id,
        )
    )
    return competencia_id


async def _registrar_ap(event_store, competencia_id: UUID, atleta_id: UUID, valor: int) -> None:
    """Registra AP para un atleta en la competencia."""
    estado_adapter = CompetenciaEstadoAdapter(event_store)
    descriptor_adapter = DisciplinaDescriptorAdapter()
    await RegistrarAPHandler(event_store, estado_adapter, descriptor_adapter).handle(
        RegistrarAPCommand(
            competencia_id=competencia_id,
            disciplina=Disciplina.STA,
            participante_id=atleta_id,
            valor_ap=Decimal(valor),
            unidad=UnidadMedida.Segundos,
        )
    )


async def _generar_y_confirmar_grilla(event_store, competencia_id: UUID) -> None:
    """Genera y confirma la grilla de la competencia."""
    ap_adapter = PerformancesAPAdapter(event_store)
    descriptor_adapter = DisciplinaDescriptorAdapter()

    ot_inicio = datetime(2026, 9, 10, 9, 0, 0, tzinfo=timezone.utc)
    await GenerarGrillaHandler(event_store, ap_adapter, descriptor_adapter).handle(
        GenerarGrillaCommand(
            competencia_id=competencia_id,
            disciplina=Disciplina.STA,
            ot_inicio=ot_inicio,
        )
    )
    await ConfirmarGrillaHandler(event_store).handle(
        ConfirmarGrillaCommand(
            competencia_id=competencia_id,
            disciplina=Disciplina.STA,
        )
    )


# ── Tests ─────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_flujo_completo_inscripcion_ap_grilla(infra):
    """INV-E2E-01/02/03: flujo completo desde Torneo hasta grilla con 1 atleta."""
    torneo_id = await _crear_torneo_abierto(infra["torneo_repo"])
    atleta_id = await _registrar_e_inscribir(
        infra["atleta_repo"],
        infra["inscripcion_repo"],
        infra["torneo_consulta"],
        torneo_id,
    )
    competencia_id = await _configurar_competencia(infra["event_store"], torneo_id)

    # AP y grilla (participante_id = atleta_id — INV-E2E-01)
    await _registrar_ap(infra["event_store"], competencia_id, atleta_id, 360)
    await _generar_y_confirmar_grilla(infra["event_store"], competencia_id)

    # Verificar grilla (INV-E2E-03)
    grilla = await ObtenerGrillaHandler(infra["event_store"]).handle(
        ObtenerGrillaQuery(competencia_id=competencia_id, disciplina=Disciplina.STA)
    )
    assert len(grilla) == 1
    assert grilla[0].atleta_id == str(atleta_id)  # INV-E2E-01

    # Verificar torneo_id en competencia (INV-E2E-02)
    estado = await ObtenerEstadoCompetenciaHandler(infra["event_store"]).handle(
        ObtenerEstadoCompetenciaQuery(competencia_id=competencia_id, disciplina=Disciplina.STA)
    )
    assert estado.torneo_id == torneo_id  # INV-E2E-02


@pytest.mark.asyncio
async def test_atleta_sin_ap_no_aparece_en_grilla(infra):
    """RF-PR-04: solo atletas con AP aparecen en la grilla."""
    torneo_id = await _crear_torneo_abierto(infra["torneo_repo"])

    atleta_con_ap = await _registrar_e_inscribir(
        infra["atleta_repo"], infra["inscripcion_repo"], infra["torneo_consulta"], torneo_id
    )
    # Segundo atleta: registrado e inscripto pero sin AP
    atleta_sin_ap = uuid4()
    await RegistrarAtletaHandler(infra["atleta_repo"]).handle(
        RegistrarAtletaCommand(
            atleta_id=atleta_sin_ap,
            nombre="Maria",
            apellido="Lopez",
            email="maria@test.com",
            fecha_nacimiento=date(1992, 5, 20),
            categoria=Categoria.SENIOR_FEMENINO,
        )
    )
    await InscribirAtletaHandler(infra["inscripcion_repo"], infra["torneo_consulta"]).handle(
        InscribirAtletaCommand(
            atleta_id=atleta_sin_ap,
            torneo_id=torneo_id,
            disciplinas=frozenset({SharedDisciplina.STA}),
        )
    )

    competencia_id = await _configurar_competencia(infra["event_store"], torneo_id)
    await _registrar_ap(infra["event_store"], competencia_id, atleta_con_ap, 300)
    await _generar_y_confirmar_grilla(infra["event_store"], competencia_id)

    grilla = await ObtenerGrillaHandler(infra["event_store"]).handle(
        ObtenerGrillaQuery(competencia_id=competencia_id, disciplina=Disciplina.STA)
    )
    assert len(grilla) == 1
    assert grilla[0].atleta_id == str(atleta_con_ap)


@pytest.mark.asyncio
async def test_multiples_atletas_ordenados_por_ap_descendente(infra):
    """RF-PR-05: STA — mayor AP primero (360s → 300s → 240s)."""
    torneo_id = await _crear_torneo_abierto(infra["torneo_repo"])
    competencia_id = await _configurar_competencia(infra["event_store"], torneo_id)

    atletas_y_aps = [(uuid4(), ap) for ap in [360, 300, 240]]

    for atleta_id, ap_segundos in atletas_y_aps:
        await RegistrarAtletaHandler(infra["atleta_repo"]).handle(
            RegistrarAtletaCommand(
                atleta_id=atleta_id,
                nombre="Atleta",
                apellido=f"AP{ap_segundos}",
                email=f"atleta{ap_segundos}@test.com",
                fecha_nacimiento=date(1990, 1, 1),
                categoria=Categoria.SENIOR_MASCULINO,
            )
        )
        await InscribirAtletaHandler(infra["inscripcion_repo"], infra["torneo_consulta"]).handle(
            InscribirAtletaCommand(
                atleta_id=atleta_id,
                torneo_id=torneo_id,
                disciplinas=frozenset({SharedDisciplina.STA}),
            )
        )
        await _registrar_ap(infra["event_store"], competencia_id, atleta_id, ap_segundos)

    await _generar_y_confirmar_grilla(infra["event_store"], competencia_id)

    grilla = await ObtenerGrillaHandler(infra["event_store"]).handle(
        ObtenerGrillaQuery(competencia_id=competencia_id, disciplina=Disciplina.STA)
    )
    assert len(grilla) == 3
    assert grilla[0].atleta_id == str(atletas_y_aps[0][0])  # 360s — posición 1
    assert grilla[1].atleta_id == str(atletas_y_aps[1][0])  # 300s — posición 2
    assert grilla[2].atleta_id == str(atletas_y_aps[2][0])  # 240s — posición 3
