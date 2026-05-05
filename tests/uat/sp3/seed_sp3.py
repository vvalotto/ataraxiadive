"""Seed UAT SP3 — siembra el flujo DoD completo para el UAT de "El Torneo".

Datos reales del torneo "Apnea Indoor Buenos Aires 2025" (HITO-17).
Disciplina STA, 6 atletas, 4 categorías.

Ejecutar desde la raíz del proyecto en dos fases:

    Fase 1 (crea Torneo + Registro + Competencia hasta GenerarGrilla):
        uv run python tests/uat/sp3/seed_sp3.py fase1

    Fase 2 (ejecución completa + CompetenciaFinalizada + Ranking + Overall):
        uv run python tests/uat/sp3/seed_sp3.py fase2

Entre fase1 y fase2 el servidor debe ejecutar vía HTTP:
    POST /competencia/{id}/confirmar-grilla
    POST /competencia/{id}/iniciar

DBs utilizadas:
    data/torneo.db       — BC Torneo
    data/registro.db     — BC Registro (atletas + inscripciones)
    data/competencia.db  — BC Competencia (event store)
    data/resultados.db   — BC Resultados (ranking + overall)

Flujo DoD SP3 — disciplina STA, 1 andarivel, 6 atletas reales BA 2025:
    A (Enjuto):    AP 120s → pos.1 → Resultado 393s → Blanca
    C (Montangie): AP 180s → pos.2 → Resultado 277s → Blanca
    D (Valotto):   AP 195s → pos.3 → Resultado 273s → Blanca
    F (Di Lernia): AP 240s → pos.4 → Resultado 243s → Blanca
    E (Alperin):   AP 241s → pos.5 → Resultado 244s → Blanca
    B (Almada):    AP 300s → pos.6 → Resultado 342s → Blanca → CompetenciaFinalizada

Ranking esperado por categoría:
    SENIOR_MASCULINO: A (393s) pos.1, B (342s) pos.2
    SENIOR_FEMENINO:  C (277s) pos.1
    MASTER_MASCULINO: D (273s) pos.1, E (244s) pos.2
    MASTER_FEMENINO:  F (243s) pos.1
"""

from __future__ import annotations

import asyncio
import json
import os
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
from competencia.application.commands.configurar_intervalo_ot import (
    ConfigurarIntervaloOTCommand,
    ConfigurarIntervaloOTHandler,
)
from competencia.application.commands.generar_grilla import (
    GenerarGrillaCommand,
    GenerarGrillaHandler,
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
from resultados.application.commands.calcular_overall import (
    CalcularOverallCommand,
    CalcularOverallHandler,
)
from resultados.application.commands.calcular_ranking import (
    CalcularRankingCommand,
    CalcularRankingHandler,
)
from resultados.infrastructure.repositories.atleta_categoria_adapter import AtletaCategoriaAdapter
from resultados.infrastructure.repositories.disciplina_descriptor_adapter import (
    DisciplinaDescriptorAdapter as ResultadosDisciplinaDescriptorAdapter,
)
from resultados.infrastructure.repositories.resultados_competencia_adapter import (
    ResultadosCompetenciaAdapter,
)
from shared.domain.value_objects.disciplina import Disciplina
from shared.domain.value_objects.unidad_medida import UnidadMedida
from torneo.application.commands.asignar_disciplinas import (
    AsignarDisciplinasCommand,
    AsignarDisciplinasHandler,
)
from torneo.application.commands.crear_torneo import CrearTorneoCommand, CrearTorneoHandler
from torneo.application.commands.transicionar_torneo import (
    AbrirInscripcionHandler,
    TransicionarTorneoCommand,
)
from torneo.infrastructure.repositories.sqlite_torneo_repository import SQLiteTorneoRepository

# ── Paths ──────────────────────────────────────────────────────────────────────

_TORNEO_DB = str(ROOT / "data" / "torneo.db")
_REGISTRO_DB = str(ROOT / "data" / "registro.db")
_COMPETENCIA_DB = str(ROOT / "data" / "competencia.db")
_RESULTADOS_DB = str(ROOT / "data" / "resultados.db")
_IDS_PATH = ROOT / "quality" / "reports" / "uat" / "SP3" / "uat_ids.json"

# ── Constantes del escenario DoD ───────────────────────────────────────────────

_DISCIPLINA = Disciplina.STA
_ANDARIVELES = 1
_INTERVALO_MINUTOS = 9
_OT_INICIO = datetime.now(timezone.utc).replace(second=0, microsecond=0) + timedelta(hours=1)
_JUEZ = "juez-uat-sp3"

# Atletas reales del torneo Buenos Aires 2025 — STA
# Formato: (id_placeholder, nombre, apellido, categoria, club, ap_segundos, rp_segundos)
_ATLETAS = [
    # ID, nombre, apellido, cat, club, AP(s), RP(s)
    ("A", "José", "Enjuto", Categoria.SENIOR_MASCULINO, "FREEDIVING ROSARIO", 120, 393),
    ("B", "Mauro", "Almada", Categoria.SENIOR_MASCULINO, "FREEDIVING BUENOS AIRES", 300, 342),
    ("C", "María", "Montangie", Categoria.SENIOR_FEMENINO, "ESC. BUCEO CETACEOS", 180, 277),
    ("D", "Víctor", "Valotto", Categoria.MASTER_MASCULINO, "REGATAS SANTA FE", 195, 273),
    ("E", "Alejandro", "Alperin", Categoria.MASTER_MASCULINO, "OHANA FREEDIVERS", 241, 244),
    ("F", "Alina", "Di Lernia", Categoria.MASTER_FEMENINO, "ESCUELA MARES", 240, 243),
]

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


# ── Fase 1 ─────────────────────────────────────────────────────────────────────


async def fase1() -> None:
    """Crea Torneo → Registro → Competencia hasta GenerarGrilla inclusive."""

    print("=" * 60)
    print("  UAT SP3 — Fase 1: Torneo + Registro + Competencia")
    print("=" * 60)
    print()

    torneo_repo = SQLiteTorneoRepository(_TORNEO_DB)
    atleta_repo = SQLiteAtletaRepository(_REGISTRO_DB)
    inscripcion_repo = SQLiteInscripcionRepository(_REGISTRO_DB)
    torneo_consulta = SQLiteTorneoConsulta(_TORNEO_DB)

    # ── BC Torneo ─────────────────────────────────────────────────────────────
    torneo_id = await CrearTorneoHandler(torneo_repo).handle(
        CrearTorneoCommand(
            nombre="Apnea Indoor Buenos Aires 2025",
            descripcion="Torneo oficial AIDA Indoor — Buenos Aires, Argentina",
            fecha_inicio=date(2025, 11, 15),
            fecha_fin=date(2025, 11, 16),
            sede_nombre="Club de Natación San Andrés",
            sede_ciudad="Buenos Aires",
            sede_pais="Argentina",
            entidad_nombre="AIDA Argentina",
            entidad_tipo="Federación",
        )
    )
    print(f"✓ Torneo creado: {torneo_id}")

    await AsignarDisciplinasHandler(torneo_repo).handle(
        AsignarDisciplinasCommand(
            torneo_id=torneo_id,
            disciplinas=frozenset({Disciplina.STA}),
        )
    )
    print("✓ Disciplinas asignadas: STA")

    await AbrirInscripcionHandler(torneo_repo).handle(
        TransicionarTorneoCommand(torneo_id=torneo_id)
    )
    print("✓ Torneo abierto para inscripción")
    print()

    # ── BC Registro: Atletas ──────────────────────────────────────────────────
    atleta_ids: dict[str, UUID] = {}
    for label, nombre, apellido, cat, club, ap_s, _ in _ATLETAS:
        aid = uuid4()
        atleta_ids[label] = aid
        await RegistrarAtletaHandler(atleta_repo).handle(
            RegistrarAtletaCommand(
                atleta_id=aid,
                nombre=nombre,
                apellido=apellido,
                email=f"uat.{label.lower()}.{apellido.lower().replace(' ', '')}@uat-sp3.test",
                fecha_nacimiento=date(1990, 1, 1),
                categoria=cat,
                club=club,
            )
        )
        print(f"✓ Atleta {label} registrado: {nombre} {apellido} ({cat.value}) — {club}")

    print()

    # ── BC Registro: Inscripciones ────────────────────────────────────────────
    inscripcion_ids: dict[str, UUID] = {}
    for label, _, _, _, _, _, _ in _ATLETAS:
        iid = await InscribirAtletaHandler(inscripcion_repo, torneo_consulta).handle(
            InscribirAtletaCommand(
                atleta_id=atleta_ids[label],
                torneo_id=torneo_id,
                disciplinas=frozenset({Disciplina.STA}),
            )
        )
        inscripcion_ids[label] = iid
        print(f"✓ Atleta {label} inscripto en STA (inscripcion_id={iid})")

    print()

    # ── BC Competencia: ConfigurarIntervaloOT + APs + Grilla ──────────────────
    store = SQLiteEventStore(_COMPETENCIA_DB)
    stub = StubCompetenciaEstadoAdapter()
    cid = uuid4()

    await ConfigurarIntervaloOTHandler(store).handle(
        ConfigurarIntervaloOTCommand(
            competencia_id=cid,
            disciplina=_DISCIPLINA,
            intervalo_minutos=_INTERVALO_MINUTOS,
            configurado_por="organizador-uat",
            torneo_id=torneo_id,
        )
    )
    print(f"✓ Competencia creada: {cid} (torneo_id={torneo_id}, intervalo={_INTERVALO_MINUTOS}min)")

    ap_handler = RegistrarAPHandler(store, stub, DisciplinaDescriptorAdapter())
    for label, _, _, _, _, ap_s, _ in _ATLETAS:
        await ap_handler.handle(
            RegistrarAPCommand(
                competencia_id=cid,
                participante_id=atleta_ids[label],
                disciplina=_DISCIPLINA,
                valor_ap=Decimal(str(ap_s)),
                unidad=UnidadMedida.Segundos,
            )
        )
    print("✓ APs registrados (6/6): A=120s C=180s D=195s F=240s E=241s B=300s")

    ap_adapter = PerformancesAPAdapter(store)
    await GenerarGrillaHandler(store, ap_adapter, DisciplinaDescriptorAdapter()).handle(
        GenerarGrillaCommand(
            competencia_id=cid,
            disciplina=_DISCIPLINA,
            ot_inicio=_OT_INICIO,
            andariveles=_ANDARIVELES,
        )
    )
    print(f"✓ Grilla generada — orden ascendente: A(120)→C(180)→D(195)→F(240)→E(241)→B(300)")
    print(f"  OT inicio: {_OT_INICIO.isoformat()}")
    print()

    # ── Guardar IDs ───────────────────────────────────────────────────────────
    ids = {
        "torneo_id": str(torneo_id),
        "competencia_id": str(cid),
        "ot_inicio": _OT_INICIO.isoformat(),
        "intervalo_minutos": _INTERVALO_MINUTOS,
        "andariveles": _ANDARIVELES,
    }
    for label in atleta_ids:
        ids[f"atleta_{label.lower()}"] = str(atleta_ids[label])
    for label in inscripcion_ids:
        ids[f"inscripcion_{label.lower()}"] = str(inscripcion_ids[label])

    _IDS_PATH.parent.mkdir(parents=True, exist_ok=True)
    _IDS_PATH.write_text(json.dumps(ids, indent=2))
    print(f"✓ IDs guardados en {_IDS_PATH.relative_to(ROOT)}")
    print()
    print("⚠  Fase 1 completada. Próximos pasos:")
    print("   1. Levantá el servidor: uv run fastapi dev src/app.py")
    print(f'   2. POST /competencia/{cid}/confirmar-grilla  {{"disciplina": "STA"}}')
    print(
        f'   3. POST /competencia/{cid}/iniciar           {{"disciplina": "STA", "juez_id": "{_JUEZ}"}}'
    )
    print("   4. Ejecutá: uv run python tests/uat/sp3/seed_sp3.py fase2")


# ── Fase 2 ─────────────────────────────────────────────────────────────────────


async def fase2() -> None:
    """Ejecuta las 6 performances + P-08 (Ranking) + P-09 (Overall).

    Precondición: servidor ejecutó POST confirmar-grilla y POST iniciar.
    """
    import aiosqlite

    # Inicializar data/resultados.db si no existe
    async with aiosqlite.connect(_RESULTADOS_DB) as db:
        await db.execute(_CREATE_EVENTS_TABLE)
        await db.commit()

    ids = json.loads(_IDS_PATH.read_text())
    torneo_id = UUID(ids["torneo_id"])
    cid = UUID(ids["competencia_id"])
    atleta_ids = {
        label.upper(): UUID(ids[f"atleta_{label}"]) for label in ["a", "b", "c", "d", "e", "f"]
    }

    print("=" * 60)
    print("  UAT SP3 — Fase 2: Ejecución STA + Ranking + Overall")
    print("=" * 60)
    print()
    print(f"competencia_id : {cid}")
    print(f"torneo_id      : {torneo_id}")
    print()

    store = SQLiteEventStore(_COMPETENCIA_DB)
    resultados_store = SQLiteEventStore(_RESULTADOS_DB)
    estado_adapter = CompetenciaEstadoAdapter(store)
    perf_estado_adapter = PerformancesEstadoAdapter(store)
    descriptor_adapter = DisciplinaDescriptorAdapter()

    # ── Callback P-08 + P-09 ─────────────────────────────────────────────────
    async def on_finalizada(
        competencia_id: UUID, disciplina: Disciplina, torneo_id_cb: UUID | None = None
    ) -> None:
        # P-08: calcular ranking por disciplina
        acl = ResultadosCompetenciaAdapter(store)
        atleta_cat_acl = AtletaCategoriaAdapter()
        await CalcularRankingHandler(
            resultados_store, acl, atleta_cat_acl, ResultadosDisciplinaDescriptorAdapter()
        ).handle(CalcularRankingCommand(competencia_id=competencia_id, disciplina=disciplina))
        print("✓ Ranking calculado (P-08)")

        # P-09: calcular overall (todas las disciplinas del torneo deben haber finalizado)
        if torneo_id_cb is not None:
            torneo_repo = SQLiteTorneoRepository(_TORNEO_DB)
            torneo = await torneo_repo.find_by_id(torneo_id_cb)
            if torneo is not None:
                disciplinas = [d for dt in torneo.disciplinas_torneo for d in [dt.disciplina]]
                await CalcularOverallHandler(resultados_store, store).handle(
                    CalcularOverallCommand(torneo_id=torneo_id_cb, disciplinas=disciplinas)
                )
                print("✓ Overall calculado (P-09)")

    # ── Leer grilla (construida en fase 1) ───────────────────────────────────
    grilla = await ObtenerGrillaHandler(store).handle(
        ObtenerGrillaQuery(competencia_id=cid, disciplina=_DISCIPLINA)
    )
    grilla_map = {UUID(e.atleta_id): e for e in grilla}
    print("✓ Grilla leída:")
    for e in sorted(grilla, key=lambda x: x.posicion):
        print(f"  pos.{e.posicion} | atleta={e.atleta_id[:8]}... | OT={e.ot_programado}")
    print()

    llamar_handler = LlamarAtletaHandler(store, estado_adapter)
    resultado_handler = RegistrarResultadoHandler(store, descriptor_adapter)
    tarjeta_handler = AsignarTarjetaHandler(store, perf_estado_adapter, on_finalizada)

    # Ejecutar en orden de grilla (ascendente: A→C→D→F→E→B)
    orden_ejecucion = [
        ("A", 393),
        ("C", 277),
        ("D", 273),
        ("F", 243),
        ("E", 244),
        ("B", 342),  # ← último → CompetenciaFinalizada + P-08 + P-09
    ]

    for label, rp_s in orden_ejecucion:
        aid = atleta_ids[label]
        entrada = grilla_map[aid]

        await llamar_handler.handle(
            LlamarAtletaCommand(
                competencia_id=cid,
                participante_id=aid,
                disciplina=_DISCIPLINA,
                ot_programado=datetime.fromisoformat(entrada.ot_programado),
                posicion_grilla=entrada.posicion,
            )
        )
        await resultado_handler.handle(
            RegistrarResultadoCommand(
                competencia_id=cid,
                participante_id=aid,
                disciplina=_DISCIPLINA,
                valor_rp=Decimal(str(rp_s)),
                unidad=UnidadMedida.Segundos,
                registrado_por=_JUEZ,
            )
        )
        await tarjeta_handler.handle(
            AsignarTarjetaCommand(
                competencia_id=cid,
                participante_id=aid,
                disciplina=_DISCIPLINA,
                tipo=TipoTarjeta.Blanca,
                asignada_por=_JUEZ,
            )
        )
        print(f"✓ Atleta {label}: RP={rp_s}s → Tarjeta Blanca")

    print()
    print("=" * 60)
    print("  Fase 2 completada.")
    print("  Ranking y Overall calculados automáticamente (P-08, P-09).")
    print(f"  Verificar: GET /resultados/{cid}/ranking?disciplina=STA")
    print(f"  Verificar: GET /resultados/{torneo_id}/overall")
    print("=" * 60)


# ── Entry point ────────────────────────────────────────────────────────────────


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ("fase1", "fase2"):
        print("Uso: uv run python tests/uat/sp3/seed_sp3.py fase1|fase2")
        sys.exit(1)

    if sys.argv[1] == "fase1":
        asyncio.run(fase1())
    else:
        asyncio.run(fase2())
