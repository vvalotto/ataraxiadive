"""Seed UAT SP4 — siembra el flujo de performance completo para la prueba de UI.

Crea un torneo con dos competencias (DNF y STA) y 13 atletas, cubriendo los
12 escenarios del flujo de performance del juez más los 3 casos de resume.

  uv run python tests/uat/sp4/seed_sp4.py

DBs utilizadas (se crean automáticamente):
    data/torneo.db       — BC Torneo
    data/registro.db     — BC Registro
    data/competencia.db  — BC Competencia (event store)
    data/identidad.db    — BC Identidad (usuario juez)

Estado final tras el seed:
    Competencia DNF — 10 atletas
      E01 Diego Vega (40m)     → AnunciadaAP   [E-01: DNS en UI]
      E02 Laura Romero (50m)   → AnunciadaAP   [E-02: BKO mid, paso 4]
      E03 Carlos Ibañez (60m)  → AnunciadaAP   [E-03: Blanca simple]
      E04 Ana Flores (70m)     → AnunciadaAP   [E-04: Blanca + penalizaciones]
      E05 Roberto Chen (80m)   → AnunciadaAP   [E-05: Roja DQ estándar]
      E06 Patricia Ruiz (90m)  → AnunciadaAP   [E-06: Roja BKO post]
      E07 Martin Acosta (100m) → EnRevision    [E-07: resolver → Blanca, paso 7]
      E08 Silvia Casas (110m)  → EnRevision    [E-08: resolver → Roja, paso 7]
      R01 Jorge Mendez (120m)  → Llamada       [R-01: resume paso 2]
      R02 Claudia Rios (130m)  → ResultadoRegistrado  [R-02: resume paso 6]

    Competencia STA — 3 atletas
      T01 Javier Herrera (120s)    → AnunciadaAP   [T-01: DNS STA]
      T02 Carolina Espinoza (180s) → AnunciadaAP   [T-02: BKO STA mid]
      T03 Fernando Bravo (240s)    → AnunciadaAP   [T-03: Blanca STA]

    Usuario juez:  juez@uat-sp4.test / juezsp4uat2025
"""

from __future__ import annotations

import asyncio
import json
import sys
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from uuid import UUID, uuid4

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from competencia.application.commands.asignar_tarjeta import (
    AsignarTarjetaCommand,
    AsignarTarjetaHandler,
)
from competencia.application.commands.confirmar_grilla import (
    ConfirmarGrillaCommand,
    ConfirmarGrillaHandler,
)
from competencia.application.commands.configurar_intervalo_ot import (
    ConfigurarIntervaloOTCommand,
    ConfigurarIntervaloOTHandler,
)
from competencia.application.commands.generar_grilla import (
    GenerarGrillaCommand,
    GenerarGrillaHandler,
)
from competencia.application.commands.iniciar_competencia import (
    IniciarCompetenciaCommand,
    IniciarCompetenciaHandler,
)
from competencia.application.commands.llamar_atleta import (
    LlamarAtletaCommand,
    LlamarAtletaHandler,
)
from competencia.application.commands.registrar_ap import (
    RegistrarAPCommand,
    RegistrarAPHandler,
)
from competencia.application.commands.registrar_resultado import (
    RegistrarResultadoCommand,
    RegistrarResultadoHandler,
)
from competencia.application.queries.obtener_grilla import (
    ObtenerGrillaHandler,
    ObtenerGrillaQuery,
)
from competencia.domain.value_objects.tipo_tarjeta import TipoTarjeta
from competencia.infrastructure.competencia_estado_stub import StubCompetenciaEstadoAdapter
from competencia.infrastructure.event_store.sqlite_event_store import SQLiteEventStore
from competencia.infrastructure.repositories.competencia_estado_adapter import (
    CompetenciaEstadoAdapter,
)
from competencia.infrastructure.repositories.disciplina_descriptor_adapter import (
    DisciplinaDescriptorAdapter,
)
from competencia.infrastructure.repositories.performances_ap_adapter import PerformancesAPAdapter
from competencia.infrastructure.repositories.performances_estado_adapter import (
    PerformancesEstadoAdapter,
)
from competencia.infrastructure.repositories.sqlite_competencias_por_torneo import (
    SQLiteCompetenciasPorTorneo,
)
from identidad.application.commands.registrar_usuario import (
    RegistrarUsuarioCommand,
    RegistrarUsuarioHandler,
)
from identidad.domain.value_objects.rol import Rol
from identidad.infrastructure.bcrypt_password_hasher import BcryptPasswordHasher
from identidad.infrastructure.repositories.sqlite_usuario_repository import (
    SQLiteUsuarioRepository,
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
from registro.infrastructure.repositories.sqlite_atleta_repository import SQLiteAtletaRepository
from registro.infrastructure.repositories.sqlite_inscripcion_repository import (
    SQLiteInscripcionRepository,
)
from shared.domain.value_objects.disciplina import Disciplina
from shared.domain.value_objects.unidad_medida import UnidadMedida
from torneo.application.commands.asignar_disciplinas import (
    AsignarDisciplinasCommand,
    AsignarDisciplinasHandler,
)
from torneo.application.commands.crear_torneo import CrearTorneoCommand, CrearTorneoHandler
from torneo.application.commands.asignar_juez import AsignarJuezCommand, AsignarJuezHandler
from torneo.application.commands.transicionar_torneo import (
    AbrirInscripcionHandler,
    CerrarInscripcionHandler,
    IniciarEjecucionHandler,
    TransicionarTorneoCommand,
)
from torneo.infrastructure.repositories.sqlite_torneo_repository import SQLiteTorneoRepository

# ── Paths ──────────────────────────────────────────────────────────────────────

_TORNEO_DB = str(ROOT / "data" / "torneo.db")
_REGISTRO_DB = str(ROOT / "data" / "registro.db")
_COMPETENCIA_DB = str(ROOT / "data" / "competencia.db")
_IDENTIDAD_DB = str(ROOT / "data" / "identidad.db")
_IDS_PATH = ROOT / "quality" / "reports" / "uat" / "SP4" / "uat_ids.json"

# ── DDL ────────────────────────────────────────────────────────────────────────

_CREATE_EVENTS_TABLE = """
    CREATE TABLE IF NOT EXISTS events (
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

# ── Constantes ─────────────────────────────────────────────────────────────────

_INTERVALO_MINUTOS = 7
_OT_BASE = datetime.now(timezone.utc).replace(second=0, microsecond=0) + timedelta(hours=1)
_JUEZ_ID = "juez-uat-sp4"
_JUEZ_EMAIL = "juez@uat-sp4.test"
_JUEZ_PASS = "juezsp4uat2025"

# Atletas DNF: (label, nombre, apellido, cat, ap_metros)
_ATLETAS_DNF = [
    ("E01", "Diego",   "Vega",    Categoria.SENIOR_MASCULINO, 40),
    ("E02", "Laura",   "Romero",  Categoria.SENIOR_FEMENINO,  50),
    ("E03", "Carlos",  "Ibañez",  Categoria.MASTER_MASCULINO, 60),
    ("E04", "Ana",     "Flores",  Categoria.MASTER_FEMENINO,  70),
    ("E05", "Roberto", "Chen",    Categoria.SENIOR_MASCULINO, 80),
    ("E06", "Patricia","Ruiz",    Categoria.SENIOR_FEMENINO,  90),
    ("E07", "Martin",  "Acosta",  Categoria.MASTER_MASCULINO, 100),
    ("E08", "Silvia",  "Casas",   Categoria.MASTER_FEMENINO,  110),
    ("R01", "Jorge",   "Mendez",  Categoria.SENIOR_MASCULINO, 120),
    ("R02", "Claudia", "Rios",    Categoria.SENIOR_FEMENINO,  130),
]

# Atletas STA: (label, nombre, apellido, cat, ap_segundos)
_ATLETAS_STA = [
    ("T01", "Javier",   "Herrera",  Categoria.MASTER_MASCULINO, 120),
    ("T02", "Carolina", "Espinoza", Categoria.MASTER_FEMENINO,  180),
    ("T03", "Fernando", "Bravo",    Categoria.SENIOR_MASCULINO, 240),
]


# ── Helpers ────────────────────────────────────────────────────────────────────

def _ok(msg: str) -> None:
    print(f"  ✓ {msg}")


async def _registrar_atleta_e_inscribir(
    label: str,
    nombre: str,
    apellido: str,
    categoria: Categoria,
    disciplina: Disciplina,
    torneo_id: UUID,
    atleta_repo: SQLiteAtletaRepository,
    inscripcion_repo: SQLiteInscripcionRepository,
    torneo_consulta: SQLiteTorneoConsulta,
) -> UUID:
    aid = uuid4()
    email = f"uat.{label.lower()}@uat-sp4.test"
    await RegistrarAtletaHandler(atleta_repo).handle(
        RegistrarAtletaCommand(
            atleta_id=aid,
            nombre=nombre,
            apellido=apellido,
            email=email,
            fecha_nacimiento=date(1990, 6, 15),
            categoria=categoria,
            club="UAT SP4",
        )
    )
    await InscribirAtletaHandler(inscripcion_repo, torneo_consulta).handle(
        InscribirAtletaCommand(
            atleta_id=aid,
            torneo_id=torneo_id,
            disciplinas=frozenset({disciplina}),
        )
    )
    _ok(f"{label} {nombre} {apellido} ({disciplina.value}, {categoria.value})")
    return aid


async def seed() -> None:
    print()
    print("=" * 65)
    print("  UAT SP4 — Seed: Flujo de Performance (DNF + STA)")
    print("=" * 65)
    print()

    # ── Inicializar event store ───────────────────────────────────────────────
    import aiosqlite

    Path(_COMPETENCIA_DB).parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(_COMPETENCIA_DB) as db:
        await db.execute(_CREATE_EVENTS_TABLE)
        await db.commit()

    # ── Repos ─────────────────────────────────────────────────────────────────
    torneo_repo = SQLiteTorneoRepository(_TORNEO_DB)
    atleta_repo = SQLiteAtletaRepository(_REGISTRO_DB)
    inscripcion_repo = SQLiteInscripcionRepository(_REGISTRO_DB)
    torneo_consulta = SQLiteTorneoConsulta(_TORNEO_DB)
    store = SQLiteEventStore(_COMPETENCIA_DB)
    stub = StubCompetenciaEstadoAdapter()
    descriptor = DisciplinaDescriptorAdapter()

    # ── BC Torneo ─────────────────────────────────────────────────────────────
    print("[Torneo]")
    torneo_id = await CrearTorneoHandler(torneo_repo).handle(
        CrearTorneoCommand(
            nombre="UAT SP4 — Flujo de Performance",
            descripcion="Torneo de prueba para UAT SP4",
            fecha_inicio=date(2025, 12, 1),
            fecha_fin=date(2025, 12, 1),
            sede_nombre="Pileta UAT",
            sede_ciudad="Buenos Aires",
            sede_pais="Argentina",
            entidad_nombre="AIDA Argentina",
            entidad_tipo="Federación",
        )
    )
    _ok(f"Torneo creado: {torneo_id}")

    await AsignarDisciplinasHandler(torneo_repo).handle(
        AsignarDisciplinasCommand(
            torneo_id=torneo_id,
            disciplinas=frozenset({Disciplina.DNF, Disciplina.STA}),
        )
    )
    _ok("Disciplinas asignadas: DNF, STA")

    await AbrirInscripcionHandler(torneo_repo).handle(
        TransicionarTorneoCommand(torneo_id=torneo_id)
    )
    _ok("Inscripción abierta")
    print()

    # ── BC Registro ───────────────────────────────────────────────────────────
    print("[Registro]")
    atleta_ids: dict[str, UUID] = {}
    for label, nombre, apellido, cat, _ in _ATLETAS_DNF:
        atleta_ids[label] = await _registrar_atleta_e_inscribir(
            label, nombre, apellido, cat, Disciplina.DNF,
            torneo_id, atleta_repo, inscripcion_repo, torneo_consulta,
        )
    for label, nombre, apellido, cat, _ in _ATLETAS_STA:
        atleta_ids[label] = await _registrar_atleta_e_inscribir(
            label, nombre, apellido, cat, Disciplina.STA,
            torneo_id, atleta_repo, inscripcion_repo, torneo_consulta,
        )
    print()

    # ── BC Competencia: DNF ───────────────────────────────────────────────────
    print("[Competencia DNF]")
    cid_dnf = uuid4()
    await ConfigurarIntervaloOTHandler(store).handle(
        ConfigurarIntervaloOTCommand(
            competencia_id=cid_dnf,
            disciplina=Disciplina.DNF,
            intervalo_minutos=_INTERVALO_MINUTOS,
            configurado_por="organizador-uat",
            torneo_id=torneo_id,
        )
    )
    _ok(f"DNF configurada: {cid_dnf} (intervalo={_INTERVALO_MINUTOS}min)")

    ap_handler = RegistrarAPHandler(store, stub, descriptor)
    for label, _, _, _, ap_m in _ATLETAS_DNF:
        await ap_handler.handle(
            RegistrarAPCommand(
                competencia_id=cid_dnf,
                participante_id=atleta_ids[label],
                disciplina=Disciplina.DNF,
                valor_ap=Decimal(str(ap_m)),
                unidad=UnidadMedida.Metros,
            )
        )
    _ok("APs DNF registrados (10/10): " + " ".join(
        f"{l}={ap}m" for l, _, _, _, ap in _ATLETAS_DNF
    ))

    ap_adapter = PerformancesAPAdapter(store)
    await GenerarGrillaHandler(store, ap_adapter, descriptor).handle(
        GenerarGrillaCommand(
            competencia_id=cid_dnf,
            disciplina=Disciplina.DNF,
            ot_inicio=_OT_BASE,
            andariveles=1,
        )
    )
    _ok("Grilla DNF generada (ascendente por AP)")

    await ConfirmarGrillaHandler(store).handle(
        ConfirmarGrillaCommand(competencia_id=cid_dnf, disciplina=Disciplina.DNF)
    )
    _ok("Grilla DNF confirmada")
    print()

    # ── BC Competencia: STA ───────────────────────────────────────────────────
    print("[Competencia STA]")
    cid_sta = uuid4()
    await ConfigurarIntervaloOTHandler(store).handle(
        ConfigurarIntervaloOTCommand(
            competencia_id=cid_sta,
            disciplina=Disciplina.STA,
            intervalo_minutos=_INTERVALO_MINUTOS,
            configurado_por="organizador-uat",
            torneo_id=torneo_id,
        )
    )
    _ok(f"STA configurada: {cid_sta} (intervalo={_INTERVALO_MINUTOS}min)")

    sta_ot_base = _OT_BASE + timedelta(hours=3)
    for label, _, _, _, ap_s in _ATLETAS_STA:
        await ap_handler.handle(
            RegistrarAPCommand(
                competencia_id=cid_sta,
                participante_id=atleta_ids[label],
                disciplina=Disciplina.STA,
                valor_ap=Decimal(str(ap_s)),
                unidad=UnidadMedida.Segundos,
            )
        )
    _ok("APs STA registrados (3/3): " + " ".join(
        f"{l}={ap}s" for l, _, _, _, ap in _ATLETAS_STA
    ))

    await GenerarGrillaHandler(store, ap_adapter, descriptor).handle(
        GenerarGrillaCommand(
            competencia_id=cid_sta,
            disciplina=Disciplina.STA,
            ot_inicio=sta_ot_base,
            andariveles=1,
        )
    )
    _ok("Grilla STA generada (ascendente por AP)")

    await ConfirmarGrillaHandler(store).handle(
        ConfirmarGrillaCommand(competencia_id=cid_sta, disciplina=Disciplina.STA)
    )
    _ok("Grilla STA confirmada")
    print()

    # ── BC Identidad: crear usuario juez (antes de cerrar inscripción) ──────────
    print("[Identidad: crear usuario juez]")
    juez_repo = SQLiteUsuarioRepository(_IDENTIDAD_DB)
    juez_id_uuid = await RegistrarUsuarioHandler(juez_repo, BcryptPasswordHasher()).handle(
        RegistrarUsuarioCommand(email=_JUEZ_EMAIL, password=_JUEZ_PASS, rol=Rol.JUEZ)
    )
    _ok(f"Usuario juez creado: {_JUEZ_EMAIL} (id={juez_id_uuid})")

    # Asignar juez a disciplinas ANTES de cerrar inscripción (restricción de dominio)
    juez_handler = AsignarJuezHandler(torneo_repo)
    for disc in [Disciplina.DNF, Disciplina.STA]:
        await juez_handler.handle(
            AsignarJuezCommand(torneo_id=torneo_id, disciplina=disc, juez_id=juez_id_uuid)
        )
        _ok(f"Juez asignado a {disc.value}")
    print()

    # ── Torneo: cerrar inscripción + iniciar ejecución ────────────────────────
    print("[Torneo — transición a EJECUCION]")
    await CerrarInscripcionHandler(torneo_repo).handle(
        TransicionarTorneoCommand(torneo_id=torneo_id)
    )
    _ok("Inscripción cerrada")

    await IniciarEjecucionHandler(torneo_repo).handle(
        TransicionarTorneoCommand(torneo_id=torneo_id)
    )
    _ok("Torneo en EJECUCION — visible en frontend")
    print()

    # ── Iniciar competencias + registrar en proyección por torneo ────────────
    print("[Iniciar competencias]")
    comp_por_torneo = SQLiteCompetenciasPorTorneo(_COMPETENCIA_DB)

    await IniciarCompetenciaHandler(store).handle(
        IniciarCompetenciaCommand(
            competencia_id=cid_dnf,
            disciplina=Disciplina.DNF,
            juez_id=_JUEZ_ID,
        )
    )
    await comp_por_torneo.guardar(cid_dnf, Disciplina.DNF.value, torneo_id)
    _ok("DNF iniciada → estado EnEjecucion + índice por torneo")

    await IniciarCompetenciaHandler(store).handle(
        IniciarCompetenciaCommand(
            competencia_id=cid_sta,
            disciplina=Disciplina.STA,
            juez_id=_JUEZ_ID,
        )
    )
    await comp_por_torneo.guardar(cid_sta, Disciplina.STA.value, torneo_id)
    _ok("STA iniciada → estado EnEjecucion + índice por torneo")
    print()

    # ── Pre-avanzar atletas (E07, E08, R01, R02) ──────────────────────────────
    print("[Pre-advance: leer grilla DNF]")
    grilla_dnf = await ObtenerGrillaHandler(store).handle(
        ObtenerGrillaQuery(competencia_id=cid_dnf, disciplina=Disciplina.DNF)
    )
    grilla_dnf_map = {UUID(e.atleta_id): e for e in grilla_dnf}
    for e in sorted(grilla_dnf, key=lambda x: x.posicion):
        print(f"    pos.{e.posicion:02d} | {e.atleta_id[:8]}... | OT={e.ot_programado[11:16]}")
    print()

    # Handlers sin chequeo de andarivel (seed secuencial)
    estado_adapter = CompetenciaEstadoAdapter(store)
    llamar = LlamarAtletaHandler(store, estado_adapter, andariveles_activos=None)
    resultado_handler = RegistrarResultadoHandler(store, descriptor)
    tarjeta_handler = AsignarTarjetaHandler(store, PerformancesEstadoAdapter(store), None)

    async def _llamar(label: str, andarivel: int = 1) -> None:
        aid = atleta_ids[label]
        entrada = grilla_dnf_map[aid]
        await llamar.handle(
            LlamarAtletaCommand(
                competencia_id=cid_dnf,
                participante_id=aid,
                disciplina=Disciplina.DNF,
                ot_programado=datetime.fromisoformat(entrada.ot_programado),
                posicion_grilla=entrada.posicion,
                andarivel=andarivel,
            )
        )

    async def _resultado_dnf(label: str, metros: int) -> None:
        await resultado_handler.handle(
            RegistrarResultadoCommand(
                competencia_id=cid_dnf,
                participante_id=atleta_ids[label],
                disciplina=Disciplina.DNF,
                valor_rp=Decimal(str(metros)),
                unidad=UnidadMedida.Metros,
                registrado_por=_JUEZ_ID,
            )
        )

    async def _amarilla(label: str) -> None:
        await tarjeta_handler.handle(
            AsignarTarjetaCommand(
                competencia_id=cid_dnf,
                participante_id=atleta_ids[label],
                disciplina=Disciplina.DNF,
                tipo=TipoTarjeta.Amarilla,
                motivo_texto="Revision pendiente del juez",
                asignada_por=_JUEZ_ID,
            )
        )

    print("[Pre-advance: E07 Martin Acosta → EnRevision (Amarilla)]")
    await _llamar("E07")
    await _resultado_dnf("E07", 95)
    await _amarilla("E07")
    _ok("E07 Martin Acosta → EnRevision (RP=95m, Amarilla asignada)")

    print()
    print("[Pre-advance: E08 Silvia Casas → EnRevision (Amarilla)]")
    await _llamar("E08")
    await _resultado_dnf("E08", 108)
    await _amarilla("E08")
    _ok("E08 Silvia Casas → EnRevision (RP=108m, Amarilla asignada)")

    print()
    print("[Pre-advance: R02 Claudia Rios → ResultadoRegistrado]")
    await _llamar("R02")
    await _resultado_dnf("R02", 125)
    _ok("R02 Claudia Rios → ResultadoRegistrado (RP=125m, sin tarjeta)")

    print()
    print("[Pre-advance: R01 Jorge Mendez → Llamada]")
    await _llamar("R01", andarivel=2)  # andarivel 2 → no bloquea andarivel 1 para el UAT
    _ok("R01 Jorge Mendez → Llamada (sin resultado, andarivel=2)")
    print()

    # ── Guardar IDs ───────────────────────────────────────────────────────────
    ids = {
        "torneo_id": str(torneo_id),
        "competencia_dnf_id": str(cid_dnf),
        "competencia_sta_id": str(cid_sta),
        "juez_id": str(juez_id_uuid),
        "juez_email": _JUEZ_EMAIL,
        "juez_password": _JUEZ_PASS,
    }
    for label, nombre, apellido, _, _ in _ATLETAS_DNF + _ATLETAS_STA:
        ids[f"atleta_{label.lower()}"] = str(atleta_ids[label])

    _IDS_PATH.parent.mkdir(parents=True, exist_ok=True)
    _IDS_PATH.write_text(json.dumps(ids, indent=2))
    _ok(f"IDs guardados: {_IDS_PATH.relative_to(ROOT)}")
    print()

    # ── Resumen ───────────────────────────────────────────────────────────────
    print("=" * 65)
    print("  Seed completado exitosamente")
    print("=" * 65)
    print()
    print("  Competencia DNF")
    print(f"    ID  : {cid_dnf}")
    print(f"    URL : /juez/grilla (seleccionar DNF desde /juez/disciplinas)")
    print()
    print("  Competencia STA")
    print(f"    ID  : {cid_sta}")
    print(f"    URL : /juez/grilla (seleccionar STA desde /juez/disciplinas)")
    print()
    print("  Login juez")
    print(f"    email    : {_JUEZ_EMAIL}")
    print(f"    password : {_JUEZ_PASS}")
    print()
    print("  Próximos pasos:")
    print("    1. Levantá el backend : uv run fastapi dev src/app.py")
    print("    2. Levantá el frontend: cd frontend && npm run dev")
    print("    3. Abrí el browser en : http://localhost:5173")
    print("    4. Ejecutá run_uat.sh para checks HTTP + checklist")


if __name__ == "__main__":
    asyncio.run(seed())
