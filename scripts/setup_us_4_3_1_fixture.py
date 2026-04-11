"""Prepara una fixture minima para probar manualmente US-4.3.1.

Deja el torneo activo con:
- disciplina STA asignada al juez de prueba
- una competencia proyectada para ese torneo
- stream de competencia en estado EnEjecucion

Uso:
    ./.venv/bin/python scripts/setup_us_4_3_1_fixture.py
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

ROOT = Path(__file__).resolve().parents[1]
TORNEO_DB = ROOT / "data" / "torneo.db"
COMPETENCIA_DB = ROOT / "data" / "competencia.db"
IDENTIDAD_DB = ROOT / "data" / "identidad.db"

DISCIPLINA = "STA"
COMPETENCIA_ID = "11111111-1111-1111-1111-111111111431"
PERFORMANCE_ID = "22222222-2222-2222-2222-222222224311"
ATLETA_ID = "33333333-3333-3333-3333-333333334311"
JUEZ_EMAIL = "juez@ataraxia.com"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def obtener_juez_id() -> str:
    with sqlite3.connect(IDENTIDAD_DB) as conn:
        row = conn.execute(
            "SELECT usuario_id FROM usuarios WHERE email = ?",
            (JUEZ_EMAIL,),
        ).fetchone()
    if row is None:
        raise RuntimeError(f"No existe usuario juez para email {JUEZ_EMAIL}")
    return row[0]


def obtener_torneo_activo() -> tuple[str, str]:
    with sqlite3.connect(TORNEO_DB) as conn:
        row = conn.execute(
            "SELECT torneo_id, disciplinas_torneo FROM torneos WHERE estado = 'EJECUCION' LIMIT 1"
        ).fetchone()
    if row is None:
        raise RuntimeError("No existe torneo activo en estado EJECUCION")
    return row[0], row[1]


def asignar_juez_en_torneo(torneo_id: str, disciplinas_torneo_raw: str, juez_id: str) -> None:
    disciplinas = json.loads(disciplinas_torneo_raw)
    updated = False

    for entry in disciplinas:
        if entry.get("disciplina") == DISCIPLINA:
            entry["juez_id"] = juez_id
            updated = True

    if not updated:
        disciplinas.append({"disciplina": DISCIPLINA, "juez_id": juez_id})

    with sqlite3.connect(TORNEO_DB) as conn:
        conn.execute(
            "UPDATE torneos SET disciplinas_torneo = ? WHERE torneo_id = ?",
            (json.dumps(disciplinas), torneo_id),
        )
        conn.commit()


def asegurar_proyeccion_competencia(torneo_id: str) -> None:
    with sqlite3.connect(COMPETENCIA_DB) as conn:
        exists = conn.execute(
            "SELECT 1 FROM competencias_por_torneo WHERE competencia_id = ?",
            (COMPETENCIA_ID,),
        ).fetchone()
        if exists is None:
            conn.execute(
                """
                INSERT INTO competencias_por_torneo (competencia_id, torneo_id, disciplina)
                VALUES (?, ?, ?)
                """,
                (COMPETENCIA_ID, torneo_id, DISCIPLINA),
            )
            conn.commit()


def asegurar_stream_competencia(juez_id: str, torneo_id: str) -> None:
    stream_id = f"competencia-{COMPETENCIA_ID}"
    with sqlite3.connect(COMPETENCIA_DB) as conn:
        row = conn.execute(
            "SELECT COUNT(*) FROM events WHERE stream_id = ?",
            (stream_id,),
        ).fetchone()
        if row is None:
            raise RuntimeError("No se pudo consultar el stream de competencia")
        if row[0] > 0:
            return

        now = utc_now()
        ot_inicio = now

        events = [
            (
                stream_id,
                "IntervaloOTConfigurado",
                json.dumps(
                    {
                        "competencia_id": COMPETENCIA_ID,
                        "disciplina": DISCIPLINA,
                        "intervalo_minutos": 9,
                        "configurado_por": "fixture-us-4.3.1",
                        "torneo_id": torneo_id,
                        "occurred_at": now,
                    }
                ),
                1,
            ),
            (
                stream_id,
                "GrillaDeSalidaGenerada",
                json.dumps(
                    {
                        "competencia_id": COMPETENCIA_ID,
                        "disciplina": DISCIPLINA,
                        "ot_inicio": ot_inicio,
                        "performances": [
                            {
                                "performance_id": PERFORMANCE_ID,
                                "atleta_id": ATLETA_ID,
                                "posicion": 1,
                                "andarivel": 1,
                                "ot_programado": ot_inicio,
                            }
                        ],
                        "generada_en": now,
                        "occurred_at": now,
                    }
                ),
                2,
            ),
            (
                stream_id,
                "GrillaConfirmada",
                json.dumps(
                    {
                        "competencia_id": COMPETENCIA_ID,
                        "disciplina": DISCIPLINA,
                        "confirmada_en": now,
                        "occurred_at": now,
                    }
                ),
                3,
            ),
            (
                stream_id,
                "CompetenciaIniciada",
                json.dumps(
                    {
                        "competencia_id": COMPETENCIA_ID,
                        "disciplina": DISCIPLINA,
                        "juez_id": juez_id,
                        "iniciada_en": now,
                        "occurred_at": now,
                    }
                ),
                4,
            ),
        ]

        conn.executemany(
            """
            INSERT INTO events (stream_id, event_type, payload, version)
            VALUES (?, ?, ?, ?)
            """,
            events,
        )
        conn.commit()


def main() -> None:
    juez_id = obtener_juez_id()
    torneo_id, disciplinas_raw = obtener_torneo_activo()
    asignar_juez_en_torneo(torneo_id, disciplinas_raw, juez_id)
    asegurar_proyeccion_competencia(torneo_id)
    asegurar_stream_competencia(juez_id, torneo_id)

    print("Fixture US-4.3.1 lista")
    print(f"  torneo_id: {torneo_id}")
    print(f"  juez_id:   {juez_id}")
    print(f"  disciplina: {DISCIPLINA}")
    print(f"  competencia_id: {COMPETENCIA_ID}")


if __name__ == "__main__":
    main()
