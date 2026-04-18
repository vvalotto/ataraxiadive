"""Prepara fixtures minimas para probar manualmente US-4.3.3.

Deja un torneo activo con:
- competencia STA para DNS / BKO
- competencia DNF para blanca con penalizaciones

Uso:
    ./.venv/bin/python scripts/setup_us_4_3_3_fixture.py
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TORNEO_DB = ROOT / "data" / "torneo.db"
COMPETENCIA_DB = ROOT / "data" / "competencia.db"
IDENTIDAD_DB = ROOT / "data" / "identidad.db"

JUEZ_EMAIL = "juez@ataraxia.com"

FIXTURES = [
    {
        "disciplina": "STA",
        "competencia_id": "11111111-1111-1111-1111-111111111431",
        "performance_id": "22222222-2222-2222-2222-222222224311",
        "atleta_id": "33333333-3333-3333-3333-333333334311",
        "valor_ap": "300",
        "unidad": "Segundos",
    },
    {
        "disciplina": "DNF",
        "competencia_id": "11111111-1111-1111-1111-111111111433",
        "performance_id": "22222222-2222-2222-2222-222222224333",
        "atleta_id": "33333333-3333-3333-3333-333333334333",
        "valor_ap": "75",
        "unidad": "Metros",
    },
]


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


def asegurar_asignaciones_juez(torneo_id: str, disciplinas_raw: str, juez_id: str) -> None:
    disciplinas = json.loads(disciplinas_raw)
    by_code = {entry.get("disciplina"): entry for entry in disciplinas}

    for fixture in FIXTURES:
      if fixture["disciplina"] in by_code:
          by_code[fixture["disciplina"]]["juez_id"] = juez_id
      else:
          disciplinas.append({"disciplina": fixture["disciplina"], "juez_id": juez_id})

    with sqlite3.connect(TORNEO_DB) as conn:
        conn.execute(
            "UPDATE torneos SET disciplinas_torneo = ? WHERE torneo_id = ?",
            (json.dumps(disciplinas), torneo_id),
        )
        conn.commit()


def asegurar_proyecciones_competencia(torneo_id: str) -> None:
    with sqlite3.connect(COMPETENCIA_DB) as conn:
        for fixture in FIXTURES:
            exists = conn.execute(
                "SELECT 1 FROM competencias_por_torneo WHERE competencia_id = ?",
                (fixture["competencia_id"],),
            ).fetchone()
            if exists is None:
                conn.execute(
                    """
                    INSERT INTO competencias_por_torneo (competencia_id, torneo_id, disciplina)
                    VALUES (?, ?, ?)
                    """,
                    (fixture["competencia_id"], torneo_id, fixture["disciplina"]),
                )
        conn.commit()


def reset_streams(juez_id: str, torneo_id: str) -> None:
    with sqlite3.connect(COMPETENCIA_DB) as conn:
        for fixture in FIXTURES:
            now = utc_now()
            stream_id = f"competencia-{fixture['competencia_id']}"
            performance_stream_id = (
                f"performance-{fixture['competencia_id']}-{fixture['atleta_id']}-{fixture['disciplina']}"
            )

            conn.execute("DELETE FROM events WHERE stream_id = ?", (stream_id,))
            conn.execute("DELETE FROM events WHERE stream_id = ?", (performance_stream_id,))

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
                                "competencia_id": fixture["competencia_id"],
                                "disciplina": fixture["disciplina"],
                                "intervalo_minutos": 9,
                                "configurado_por": "fixture-us-4.3.3",
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
                                "competencia_id": fixture["competencia_id"],
                                "disciplina": fixture["disciplina"],
                                "ot_inicio": now,
                                "performances": [
                                    {
                                        "performance_id": fixture["performance_id"],
                                        "atleta_id": fixture["atleta_id"],
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
                                "competencia_id": fixture["competencia_id"],
                                "disciplina": fixture["disciplina"],
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
                                "competencia_id": fixture["competencia_id"],
                                "disciplina": fixture["disciplina"],
                                "juez_id": juez_id,
                                "iniciada_en": now,
                                "occurred_at": now,
                            }
                        ),
                        4,
                    ),
                    (
                        performance_stream_id,
                        "APRegistrado",
                        json.dumps(
                            {
                                "performance_id": fixture["performance_id"],
                                "competencia_id": fixture["competencia_id"],
                                "participante_id": fixture["atleta_id"],
                                "disciplina": fixture["disciplina"],
                                "valor_ap": fixture["valor_ap"],
                                "unidad": fixture["unidad"],
                                "occurred_at": now,
                            }
                        ),
                        1,
                    ),
                ],
            )
        conn.commit()


def main() -> None:
    juez_id = obtener_juez_id()
    torneo_id, disciplinas_raw = obtener_torneo_activo()
    asegurar_asignaciones_juez(torneo_id, disciplinas_raw, juez_id)
    asegurar_proyecciones_competencia(torneo_id)
    reset_streams(juez_id, torneo_id)

    print("Fixture US-4.3.3 lista")
    print(f"  torneo_id: {torneo_id}")
    for fixture in FIXTURES:
        print(
            f"  {fixture['disciplina']}: competencia={fixture['competencia_id']} atleta={fixture['atleta_id']}"
        )


if __name__ == "__main__":
    main()
