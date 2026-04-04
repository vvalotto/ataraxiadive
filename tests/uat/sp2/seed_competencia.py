"""Seed UAT SP2 — siembra el flujo DoD completo en data/competencia.db y data/resultados.db.

Ejecutar desde la raíz del proyecto en dos fases:

    Fase 1 (antes de que el servidor confirme e inicie vía HTTP):
        uv run python tests/uat/sp2/seed_competencia.py fase1

    Fase 2 (después de que el servidor haya ejecutado POST confirmar-grilla + POST iniciar):
        uv run python tests/uat/sp2/seed_competencia.py fase2

Postcondición de fase1:
    - data/competencia.db contiene: IntervaloOTConfigurado, APRegistrado ×5, GrillaDeSalidaGenerada
    - quality/reports/uat/SP2/uat_ids.json contiene los IDs generados

Postcondición de fase2:
    - data/competencia.db contiene el flujo de ejecución completo + CompetenciaFinalizada
    - data/resultados.db contiene el ranking calculado (P-08)

Flujo DoD SP2 — disciplina STA, 3 andariveles, 5 atletas:
    A: AP 300s → grilla pos.1 → Llamar (and.1) → Resultado 300s → Tarjeta blanca
    B: AP 240s → grilla pos.2 → Llamar (and.2) → DNS
    C: AP 180s → grilla pos.3 → Llamar (and.3) → Resultado 180s → Tarjeta blanca
    D: AP 150s → grilla pos.4 → Llamar (and.1) → Resultado 160s → Tarjeta blanca → Corregir 155s
    E: AP 120s → grilla pos.5 → Llamar (and.2) → Resultado 90s → Tarjeta roja (black-out)
       → CompetenciaFinalizada → CalcularRanking (P-08)
"""

from __future__ import annotations

import asyncio
import json
import os
import sys

import aiosqlite
from datetime import datetime, timedelta, timezone
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
from competencia.application.commands.corregir_resultado import (
    CorregirResultadoCommand,
    CorregirResultadoHandler,
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
from competencia.application.commands.registrar_dns import (
    RegistrarDNSCommand,
    RegistrarDNSHandler,
)
from competencia.application.commands.registrar_resultado import (
    RegistrarResultadoCommand,
    RegistrarResultadoHandler,
)
from competencia.application.queries.obtener_grilla import (
    ObtenerGrillaHandler,
    ObtenerGrillaQuery,
)
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
from resultados.application.commands.calcular_ranking import (
    CalcularRankingCommand,
    CalcularRankingHandler,
)
from resultados.infrastructure.repositories.disciplina_descriptor_adapter import (
    DisciplinaDescriptorAdapter as ResultadosDisciplinaDescriptorAdapter,
)
from resultados.infrastructure.repositories.resultados_competencia_adapter import (
    ResultadosCompetenciaAdapter,
)
from shared.domain.value_objects.disciplina import Disciplina
from shared.domain.value_objects.unidad_medida import UnidadMedida
from competencia.domain.value_objects.tipo_tarjeta import TipoTarjeta

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

_DISCIPLINA = Disciplina.STA
_ANDARIVELES = 3
_INTERVALO_MINUTOS = 9
_OT_INICIO = datetime.now(timezone.utc).replace(second=0, microsecond=0) + timedelta(hours=1)
_JUEZ = "juez-uat-sp2"
_DB_PATH = str(ROOT / "data" / "competencia.db")
_RESULTADOS_DB_PATH = str(ROOT / "data" / "resultados.db")
_IDS_PATH = ROOT / "quality" / "reports" / "uat" / "SP2" / "uat_ids.json"


# ── Fase 1: ConfigurarIntervaloOT + RegistrarAP ×5 + GenerarGrilla ───────────


async def fase1() -> None:
    """Siembra la DB hasta GenerarGrilla inclusive.

    El run_uat.sh llamará a POST /confirmar-grilla y POST /iniciar vía HTTP
    entre fase1 y fase2.
    """
    store = SQLiteEventStore(_DB_PATH)
    stub = StubCompetenciaEstadoAdapter()

    cid = uuid4()
    pid_a, pid_b, pid_c, pid_d, pid_e = [uuid4() for _ in range(5)]

    print(f"competencia_id : {cid}")
    print(f"atleta_a       : {pid_a}  (AP 300s)")
    print(f"atleta_b       : {pid_b}  (AP 240s)")
    print(f"atleta_c       : {pid_c}  (AP 180s)")
    print(f"atleta_d       : {pid_d}  (AP 150s)")
    print(f"atleta_e       : {pid_e}  (AP 120s)")
    print()

    # ── ConfigurarIntervaloOT ─────────────────────────────────────────────
    await ConfigurarIntervaloOTHandler(store).handle(
        ConfigurarIntervaloOTCommand(
            competencia_id=cid,
            disciplina=_DISCIPLINA,
            intervalo_minutos=_INTERVALO_MINUTOS,
            configurado_por="organizador-uat",
        )
    )
    print(f"✓ IntervaloOT configurado ({_INTERVALO_MINUTOS} min, {_ANDARIVELES} andariveles)")

    # ── RegistrarAP ×5 (STA: mayor a menor → A pos.1, E pos.5) ──────────
    atletas = [
        (pid_a, Decimal("300")),
        (pid_b, Decimal("240")),
        (pid_c, Decimal("180")),
        (pid_d, Decimal("150")),
        (pid_e, Decimal("120")),
    ]
    ap_handler = RegistrarAPHandler(store, stub, DisciplinaDescriptorAdapter())
    for pid, valor_ap in atletas:
        await ap_handler.handle(
            RegistrarAPCommand(
                competencia_id=cid,
                participante_id=pid,
                disciplina=_DISCIPLINA,
                valor_ap=valor_ap,
                unidad=UnidadMedida.Segundos,
            )
        )
    print("✓ APs registrados (5/5 — A:300s B:240s C:180s D:150s E:120s)")

    # ── GenerarGrilla (3 andariveles) ─────────────────────────────────────
    ap_adapter = PerformancesAPAdapter(store)
    await GenerarGrillaHandler(store, ap_adapter, DisciplinaDescriptorAdapter()).handle(
        GenerarGrillaCommand(
            competencia_id=cid,
            disciplina=_DISCIPLINA,
            ot_inicio=_OT_INICIO,
            andariveles=_ANDARIVELES,
        )
    )
    print(f"✓ Grilla generada (OT inicio: {_OT_INICIO.isoformat()})")
    print("  → Esperado: A pos.1 (OT+0min), B pos.2 (OT+9min), C pos.3 (OT+18min), ...")
    print()
    print("⚠ Fase 1 completada. Siguiente paso:")
    print("  1. Levantá el servidor: uv run fastapi dev src/app.py")
    print(f"  2. POST /competencia/{cid}/confirmar-grilla")
    print(f"  3. POST /competencia/{cid}/iniciar")
    print("  4. Ejecutá: uv run python tests/uat/sp2/seed_competencia.py fase2")

    ids = {
        "competencia_id": str(cid),
        "atleta_a": str(pid_a),
        "atleta_b": str(pid_b),
        "atleta_c": str(pid_c),
        "atleta_d": str(pid_d),
        "atleta_e": str(pid_e),
        "ot_inicio": _OT_INICIO.isoformat(),
        "intervalo_minutos": _INTERVALO_MINUTOS,
        "andariveles": _ANDARIVELES,
    }
    _IDS_PATH.parent.mkdir(parents=True, exist_ok=True)
    _IDS_PATH.write_text(json.dumps(ids, indent=2))
    print(f"\n✓ IDs guardados en {_IDS_PATH.relative_to(ROOT)}")


# ── Fase 2: Ejecución multi-andarivel + CompetenciaFinalizada + Ranking ───────


async def fase2() -> None:
    """Ejecuta las 5 performances usando el adapter REAL de estado (grilla confirmada + iniciada).

    Precondición: el servidor ya ejecutó POST confirmar-grilla y POST iniciar.
    La CompetenciaEstadoAdapter leerá GrillaConfirmada + CompetenciaIniciada del stream.
    """
    # Inicializar data/resultados.db si no tiene la tabla events
    async with aiosqlite.connect(_RESULTADOS_DB_PATH) as db:
        await db.execute(_CREATE_EVENTS_TABLE)
        await db.commit()

    ids = json.loads(_IDS_PATH.read_text())
    cid = UUID(ids["competencia_id"])
    pid_a = UUID(ids["atleta_a"])
    pid_b = UUID(ids["atleta_b"])
    pid_c = UUID(ids["atleta_c"])
    pid_d = UUID(ids["atleta_d"])
    pid_e = UUID(ids["atleta_e"])

    print(f"competencia_id : {cid}")
    print()

    store = SQLiteEventStore(_DB_PATH)
    estado_adapter = CompetenciaEstadoAdapter(store)
    perf_estado_adapter = PerformancesEstadoAdapter(store)

    # Callback P-08: CompetenciaFinalizada → CalcularRanking
    resultados_store = SQLiteEventStore(_RESULTADOS_DB_PATH)

    async def on_finalizada(competencia_id: UUID, disciplina: Disciplina) -> None:
        acl = ResultadosCompetenciaAdapter(store)
        descriptor = ResultadosDisciplinaDescriptorAdapter()
        await CalcularRankingHandler(resultados_store, acl, descriptor).handle(
            CalcularRankingCommand(
                competencia_id=competencia_id,
                disciplina=disciplina,
            )
        )
        print("✓ CalcularRanking ejecutado (P-08)")

    # Obtener grilla para conocer posiciones y OTs reales
    grilla = await ObtenerGrillaHandler(store).handle(
        ObtenerGrillaQuery(competencia_id=cid, disciplina=_DISCIPLINA)
    )
    print(f"✓ Grilla leída ({len(grilla)} entradas)")
    for e in grilla:
        print(f"  pos.{e.posicion} | atleta={e.atleta_id[:8]}... | OT={e.ot_programado}")
    print()

    # Construir mapa atleta_id → entrada de grilla
    grilla_map = {UUID(e.atleta_id): e for e in grilla}

    llamar = LlamarAtletaHandler(store, estado_adapter)
    descriptor_adapter = DisciplinaDescriptorAdapter()

    def _llamar_cmd(pid: UUID) -> LlamarAtletaCommand:
        entrada = grilla_map[pid]
        return LlamarAtletaCommand(
            competencia_id=cid,
            participante_id=pid,
            disciplina=_DISCIPLINA,
            ot_programado=datetime.fromisoformat(entrada.ot_programado),
            posicion_grilla=entrada.posicion,
        )

    # ── Ronda 1: llamar A, B, C simultáneamente (3 andariveles) ──────────
    await llamar.handle(_llamar_cmd(pid_a))
    await llamar.handle(_llamar_cmd(pid_b))
    await llamar.handle(_llamar_cmd(pid_c))
    print("✓ AtletaLlamado: A (and.1), B (and.2), C (and.3) — 3 andariveles ocupados")

    # ── Atleta A: tarjeta blanca → libera andarivel 1 ────────────────────
    await RegistrarResultadoHandler(store, descriptor_adapter).handle(
        RegistrarResultadoCommand(
            competencia_id=cid,
            participante_id=pid_a,
            disciplina=_DISCIPLINA,
            valor_rp=Decimal("300"),
            unidad=UnidadMedida.Segundos,
            registrado_por=_JUEZ,
        )
    )
    await AsignarTarjetaHandler(store, perf_estado_adapter, on_finalizada).handle(
        AsignarTarjetaCommand(
            competencia_id=cid,
            participante_id=pid_a,
            disciplina=_DISCIPLINA,
            tipo=TipoTarjeta.Blanca,
            asignada_por=_JUEZ,
        )
    )
    print("✓ Atleta A: tarjeta blanca (300s)")

    # ── Atleta B: DNS → libera andarivel 2 ───────────────────────────────
    await RegistrarDNSHandler(store, perf_estado_adapter, on_finalizada).handle(
        RegistrarDNSCommand(
            competencia_id=cid,
            participante_id=pid_b,
            disciplina=_DISCIPLINA,
            registrado_por=_JUEZ,
        )
    )
    print("✓ Atleta B: DNS")

    # ── Atleta D: llamar (andarivel 1 libre), luego completar ─────────────
    await llamar.handle(_llamar_cmd(pid_d))
    print("✓ AtletaLlamado: D (and.1) — A y B liberados, C aún activo")

    # ── Atleta C: tarjeta blanca → libera andarivel 3 ────────────────────
    await RegistrarResultadoHandler(store, descriptor_adapter).handle(
        RegistrarResultadoCommand(
            competencia_id=cid,
            participante_id=pid_c,
            disciplina=_DISCIPLINA,
            valor_rp=Decimal("180"),
            unidad=UnidadMedida.Segundos,
            registrado_por=_JUEZ,
        )
    )
    await AsignarTarjetaHandler(store, perf_estado_adapter, on_finalizada).handle(
        AsignarTarjetaCommand(
            competencia_id=cid,
            participante_id=pid_c,
            disciplina=_DISCIPLINA,
            tipo=TipoTarjeta.Blanca,
            asignada_por=_JUEZ,
        )
    )
    print("✓ Atleta C: tarjeta blanca (180s)")

    # ── Atleta E: llamar (andarivel 2 libre) ─────────────────────────────
    await llamar.handle(_llamar_cmd(pid_e))
    print("✓ AtletaLlamado: E (and.2) — D activo (and.1), E activo (and.2)")

    # ── Atleta D: resultado + tarjeta blanca + corrección ─────────────────
    await RegistrarResultadoHandler(store, descriptor_adapter).handle(
        RegistrarResultadoCommand(
            competencia_id=cid,
            participante_id=pid_d,
            disciplina=_DISCIPLINA,
            valor_rp=Decimal("160"),
            unidad=UnidadMedida.Segundos,
            registrado_por=_JUEZ,
        )
    )
    await AsignarTarjetaHandler(store, perf_estado_adapter, on_finalizada).handle(
        AsignarTarjetaCommand(
            competencia_id=cid,
            participante_id=pid_d,
            disciplina=_DISCIPLINA,
            tipo=TipoTarjeta.Blanca,
            asignada_por=_JUEZ,
        )
    )
    await CorregirResultadoHandler(store).handle(
        CorregirResultadoCommand(
            competencia_id=cid,
            participante_id=pid_d,
            disciplina=_DISCIPLINA,
            valor_rp=Decimal("155"),
            unidad=UnidadMedida.Segundos,
            registrado_por=_JUEZ,
            motivo="error de lectura",
        )
    )
    print("✓ Atleta D: tarjeta blanca (160s → corregido a 155s)")

    # ── Atleta E: resultado + tarjeta roja (última → CompetenciaFinalizada) ─
    await RegistrarResultadoHandler(store, descriptor_adapter).handle(
        RegistrarResultadoCommand(
            competencia_id=cid,
            participante_id=pid_e,
            disciplina=_DISCIPLINA,
            valor_rp=Decimal("90"),
            unidad=UnidadMedida.Segundos,
            registrado_por=_JUEZ,
        )
    )
    await AsignarTarjetaHandler(store, perf_estado_adapter, on_finalizada).handle(
        AsignarTarjetaCommand(
            competencia_id=cid,
            participante_id=pid_e,
            disciplina=_DISCIPLINA,
            tipo=TipoTarjeta.Roja,
            asignada_por=_JUEZ,
            motivo="black-out",
            distancia_blackout=Decimal("30"),
        )
    )
    print("✓ Atleta E: tarjeta roja (black-out, dist. 30s) → ÚLTIMA PERFORMANCE")
    print()
    print("✓ Fase 2 completada — flujo DoD SP2 completo en DB")


# ── Entrypoint ────────────────────────────────────────────────────────────────


if __name__ == "__main__":
    fase = sys.argv[1] if len(sys.argv) > 1 else "fase1"
    if fase == "fase1":
        asyncio.run(fase1())
    elif fase == "fase2":
        asyncio.run(fase2())
    else:
        print(f"Uso: seed_competencia.py [fase1|fase2]", file=sys.stderr)
        sys.exit(1)
