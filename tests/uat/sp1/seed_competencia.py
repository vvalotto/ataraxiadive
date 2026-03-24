"""Seed UAT SP1 — siembra el flujo DoD completo en data/competencia.db.

Ejecutar desde la raíz del proyecto:
    uv run python tests/uat/sp1/seed_competencia.py

Postcondición:
    - data/competencia.db contiene el flujo de 5 atletas
    - quality/reports/uat/SP1/uat_ids.json contiene los IDs generados
      (usados luego por run_uat.sh para las llamadas HTTP)

Flujo DoD SP1:
    A: AP 60m → Llamar → Resultado 60m → Tarjeta blanca
    B: AP 40m → Llamar → DNS
    C: AP 80m → Llamar → Resultado 72m → Tarjeta amarilla (sin superficie)
    D: AP 50m → Llamar → Resultado 55m → Tarjeta blanca → Corregir a 53m
    E: AP 90m → Llamar → Resultado 90m → Tarjeta roja (black-out, distancia 45m)
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from uuid import UUID, uuid4

# Asegurar que src/ esté en el path cuando se ejecuta directamente
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from competencia.application.commands.asignar_tarjeta import (
    AsignarTarjetaCommand,
    AsignarTarjetaHandler,
)
from competencia.application.commands.corregir_resultado import (
    CorregirResultadoCommand,
    CorregirResultadoHandler,
)
from competencia.application.commands.llamar_atleta import LlamarAtletaCommand, LlamarAtletaHandler
from competencia.application.commands.registrar_ap import RegistrarAPCommand, RegistrarAPHandler
from competencia.application.commands.registrar_dns import RegistrarDNSCommand, RegistrarDNSHandler
from competencia.application.commands.registrar_resultado import (
    RegistrarResultadoCommand,
    RegistrarResultadoHandler,
)
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.tipo_tarjeta import TipoTarjeta
from competencia.domain.value_objects.unidad_medida import UnidadMedida
from competencia.infrastructure.competencia_estado_stub import StubCompetenciaEstadoAdapter
from competencia.infrastructure.event_store.sqlite_event_store import SQLiteEventStore

_DISCIPLINA = Disciplina.STA
_JUEZ = "juez-uat-001"
_OT = datetime.now(timezone.utc)
_DB_PATH = str(ROOT / "data" / "competencia.db")
_IDS_PATH = ROOT / "quality" / "reports" / "uat" / "SP1" / "uat_ids.json"


async def seed() -> dict[str, str]:
    """Ejecuta el flujo DoD SP1 y retorna los IDs generados."""
    store = SQLiteEventStore(_DB_PATH)
    stub = StubCompetenciaEstadoAdapter()

    cid = uuid4()
    pid_a, pid_b, pid_c, pid_d, pid_e = [uuid4() for _ in range(5)]

    print(f"competencia_id : {cid}")
    print(f"atleta_a       : {pid_a}")
    print(f"atleta_b       : {pid_b}")
    print(f"atleta_c       : {pid_c}")
    print(f"atleta_d       : {pid_d}")
    print(f"atleta_e       : {pid_e}")
    print()

    # ── Registrar APs ──────────────────────────────────────────────────────
    for pid, valor in [(pid_a, "60"), (pid_b, "40"), (pid_c, "80"), (pid_d, "50"), (pid_e, "90")]:
        await RegistrarAPHandler(store, stub).handle(
            RegistrarAPCommand(
                competencia_id=cid,
                participante_id=pid,
                disciplina=_DISCIPLINA,
                valor_ap=Decimal(valor),
                unidad=UnidadMedida.Metros,
            )
        )
    print("✓ APs registrados (5/5)")

    # ── Atleta A: tarjeta blanca ────────────────────────────────────────────
    await LlamarAtletaHandler(store, stub).handle(
        LlamarAtletaCommand(
            competencia_id=cid, participante_id=pid_a, disciplina=_DISCIPLINA,
            ot_programado=_OT, posicion_grilla=1,
        )
    )
    await RegistrarResultadoHandler(store).handle(
        RegistrarResultadoCommand(
            competencia_id=cid, participante_id=pid_a, disciplina=_DISCIPLINA,
            valor_rp=Decimal("60"), unidad=UnidadMedida.Metros, registrado_por=_JUEZ,
        )
    )
    await AsignarTarjetaHandler(store).handle(
        AsignarTarjetaCommand(
            competencia_id=cid, participante_id=pid_a, disciplina=_DISCIPLINA,
            tipo=TipoTarjeta.Blanca, asignada_por=_JUEZ,
        )
    )
    print("✓ Atleta A: tarjeta blanca")

    # ── Atleta B: DNS ───────────────────────────────────────────────────────
    await LlamarAtletaHandler(store, stub).handle(
        LlamarAtletaCommand(
            competencia_id=cid, participante_id=pid_b, disciplina=_DISCIPLINA,
            ot_programado=_OT, posicion_grilla=2,
        )
    )
    await RegistrarDNSHandler(store).handle(
        RegistrarDNSCommand(
            competencia_id=cid, participante_id=pid_b, disciplina=_DISCIPLINA,
            registrado_por=_JUEZ,
        )
    )
    print("✓ Atleta B: DNS")

    # ── Atleta C: tarjeta amarilla ──────────────────────────────────────────
    await LlamarAtletaHandler(store, stub).handle(
        LlamarAtletaCommand(
            competencia_id=cid, participante_id=pid_c, disciplina=_DISCIPLINA,
            ot_programado=_OT, posicion_grilla=3,
        )
    )
    await RegistrarResultadoHandler(store).handle(
        RegistrarResultadoCommand(
            competencia_id=cid, participante_id=pid_c, disciplina=_DISCIPLINA,
            valor_rp=Decimal("72"), unidad=UnidadMedida.Metros, registrado_por=_JUEZ,
        )
    )
    await AsignarTarjetaHandler(store).handle(
        AsignarTarjetaCommand(
            competencia_id=cid, participante_id=pid_c, disciplina=_DISCIPLINA,
            tipo=TipoTarjeta.Amarilla, asignada_por=_JUEZ, motivo="sin superficie",
        )
    )
    print("✓ Atleta C: tarjeta amarilla")

    # ── Atleta D: tarjeta blanca + corrección ──────────────────────────────
    await LlamarAtletaHandler(store, stub).handle(
        LlamarAtletaCommand(
            competencia_id=cid, participante_id=pid_d, disciplina=_DISCIPLINA,
            ot_programado=_OT, posicion_grilla=4,
        )
    )
    await RegistrarResultadoHandler(store).handle(
        RegistrarResultadoCommand(
            competencia_id=cid, participante_id=pid_d, disciplina=_DISCIPLINA,
            valor_rp=Decimal("55"), unidad=UnidadMedida.Metros, registrado_por=_JUEZ,
        )
    )
    await AsignarTarjetaHandler(store).handle(
        AsignarTarjetaCommand(
            competencia_id=cid, participante_id=pid_d, disciplina=_DISCIPLINA,
            tipo=TipoTarjeta.Blanca, asignada_por=_JUEZ,
        )
    )
    await CorregirResultadoHandler(store).handle(
        CorregirResultadoCommand(
            competencia_id=cid, participante_id=pid_d, disciplina=_DISCIPLINA,
            valor_rp=Decimal("53"), unidad=UnidadMedida.Metros,
            registrado_por=_JUEZ, motivo="error de lectura",
        )
    )
    print("✓ Atleta D: tarjeta blanca + corrección a 53m")

    # ── Atleta E: black-out con distancia ──────────────────────────────────
    await LlamarAtletaHandler(store, stub).handle(
        LlamarAtletaCommand(
            competencia_id=cid, participante_id=pid_e, disciplina=_DISCIPLINA,
            ot_programado=_OT, posicion_grilla=5,
        )
    )
    await RegistrarResultadoHandler(store).handle(
        RegistrarResultadoCommand(
            competencia_id=cid, participante_id=pid_e, disciplina=_DISCIPLINA,
            valor_rp=Decimal("90"), unidad=UnidadMedida.Metros, registrado_por=_JUEZ,
        )
    )
    await AsignarTarjetaHandler(store).handle(
        AsignarTarjetaCommand(
            competencia_id=cid, participante_id=pid_e, disciplina=_DISCIPLINA,
            tipo=TipoTarjeta.Roja, asignada_por=_JUEZ,
            motivo="black-out", distancia_blackout=Decimal("45"),
        )
    )
    print("✓ Atleta E: tarjeta roja (black-out, distancia 45m)")

    ids = {
        "competencia_id": str(cid),
        "atleta_a": str(pid_a),
        "atleta_b": str(pid_b),
        "atleta_c": str(pid_c),
        "atleta_d": str(pid_d),
        "atleta_e": str(pid_e),
    }

    _IDS_PATH.parent.mkdir(parents=True, exist_ok=True)
    _IDS_PATH.write_text(json.dumps(ids, indent=2))
    print(f"\n✓ IDs guardados en {_IDS_PATH.relative_to(ROOT)}")

    return ids


if __name__ == "__main__":
    asyncio.run(seed())
