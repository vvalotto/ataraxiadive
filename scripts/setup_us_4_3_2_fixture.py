"""Prepara una fixture minima para probar manualmente US-4.3.2.

Deja la competencia de fixture con una performance en estado AnunciadaAP,
lista para recorrer el flujo llamar -> registrar resultado -> asignar tarjeta.

Uso:
    ./.venv/bin/python scripts/setup_us_4_3_2_fixture.py
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPETENCIA_DB = ROOT / "data" / "competencia.db"
IDENTIDAD_DB = ROOT / "data" / "identidad.db"

COMPETENCIA_ID = "11111111-1111-1111-1111-111111111431"
DISCIPLINA = "STA"
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


def obtener_torneo_id() -> str:
    with sqlite3.connect(COMPETENCIA_DB) as conn:
        row = conn.execute(
            "SELECT torneo_id FROM competencias_por_torneo WHERE competencia_id = ?",
            (COMPETENCIA_ID,),
        ).fetchone()
    if row is None:
        raise RuntimeError(f"No existe proyeccion para competencia {COMPETENCIA_ID}")
    return row[0]


def reset_competencia_stream(juez_id: str, torneo_id: str) -> None:
    stream_id = f"competencia-{COMPETENCIA_ID}"
    now = utc_now()

    with sqlite3.connect(COMPETENCIA_DB) as conn:
        conn.execute("DELETE FROM events WHERE stream_id = ?", (stream_id,))
        conn.executemany(
            """
            INSERT INTO events (stream_id, event_type, payload, version)
            VALUES (?, ?, ?, ?)
            """,
            [
                (
                    stream_id,
                    "IntervaloOTConfigurado",
                    json.dumps(
                        {
                            "competencia_id": COMPETENCIA_ID,
                            "disciplina": DISCIPLINA,
                            "intervalo_minutos": 9,
                            "configurado_por": "fixture-us-4.3.2",
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
                            "ot_inicio": now,
                            "performances": [
                                {
                                    "performance_id": PERFORMANCE_ID,
                                    "atleta_id": ATLETA_ID,
                                    "posicion": 1,
                                    "andarivel": 1,
                                    "ot_programado": now,
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
            ],
        )
        conn.commit()


def reset_performance_stream() -> None:
    stream_id = f"performance-{COMPETENCIA_ID}-{ATLETA_ID}-{DISCIPLINA}"
    now = utc_now()

    with sqlite3.connect(COMPETENCIA_DB) as conn:
        conn.execute("DELETE FROM events WHERE stream_id = ?", (stream_id,))
        conn.execute(
            """
            INSERT INTO events (stream_id, event_type, payload, version)
            VALUES (?, ?, ?, ?)
            """,
            (
                stream_id,
                "APRegistrado",
                json.dumps(
                    {
                        "performance_id": PERFORMANCE_ID,
                        "competencia_id": COMPETENCIA_ID,
                        "participante_id": ATLETA_ID,
                        "disciplina": DISCIPLINA,
                        "valor_ap": "300",
                        "unidad": "Segundos",
                        "occurred_at": now,
                    }
                ),
                1,
            ),
        )
        conn.commit()


def main() -> None:
    juez_id = obtener_juez_id()
    torneo_id = obtener_torneo_id()
    reset_competencia_stream(juez_id, torneo_id)
    reset_performance_stream()
    print("Fixture US-4.3.2 lista")
    print(f"  competencia_id: {COMPETENCIA_ID}")
    print(f"  atleta_id:      {ATLETA_ID}")
    print(f"  disciplina:     {DISCIPLINA}")


if __name__ == "__main__":
    main()
