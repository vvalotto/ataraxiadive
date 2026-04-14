"""Resetea los atletas del UAT de INC-4.4 a estado AnunciadaAP.

Para cada atleta en la competencia UAT que tenga estado Ejecutada, DNS o
en cualquier estado posterior a AnunciadaAP, elimina todos los eventos
posteriores al APRegistrado inicial. El aggregate vuelve a AnunciadaAP.

Uso:
    ./.venv/bin/python scripts/reset_uat_4_4_fixture.py
    ./.venv/bin/python scripts/reset_uat_4_4_fixture.py --disciplina DNF
    ./.venv/bin/python scripts/reset_uat_4_4_fixture.py --disciplina STA
"""

from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPETENCIA_DB = ROOT / "data" / "competencia.db"

COMPETENCIA_ID = "d13d78f8-965a-4e55-a41d-6c0aea9b5225"

# Eventos que indican que el atleta ya fue movido de AnunciadaAP
EVENTOS_A_BORRAR = {
    "AtletaLlamado",
    "DNSRegistrado",
    "PerformanceIniciada",
    "ResultadoRegistrado",
    "TarjetaAsignada",
    "RevisionIniciada",
    "RevisionResuelta",
}


def reset_disciplina(conn: sqlite3.Connection, disciplina: str) -> None:
    stream_prefix = f"performance-{COMPETENCIA_ID}-%-{disciplina}"

    # Buscar streams con eventos más allá del APRegistrado inicial
    cursor = conn.execute(
        """
        SELECT DISTINCT stream_id
        FROM events
        WHERE stream_id LIKE ?
          AND event_type IN ({placeholders})
        """.format(placeholders=",".join("?" * len(EVENTOS_A_BORRAR))),
        [stream_prefix, *EVENTOS_A_BORRAR],
    )
    streams = [row[0] for row in cursor.fetchall()]

    if not streams:
        print(f"  [{disciplina}] No hay atletas para resetear.")
        return

    for stream_id in streams:
        # Verificar cuántos eventos tiene este stream
        eventos = conn.execute(
            "SELECT rowid, event_type FROM events WHERE stream_id = ? ORDER BY rowid",
            (stream_id,),
        ).fetchall()

        # Mantener solo el primero (APRegistrado)
        primero_rowid = eventos[0][0]
        a_borrar = [row[0] for row in eventos[1:]]

        if not a_borrar:
            continue

        conn.execute(
            f"DELETE FROM events WHERE rowid IN ({','.join('?' * len(a_borrar))})",
            a_borrar,
        )

        atleta_id = stream_id.split("-")[6]  # UUID del atleta en la posición del stream_id
        print(f"  [{disciplina}] Reset: stream ...{stream_id[-20:]} — borrados {len(a_borrar)} eventos")

    conn.commit()
    print(f"  [{disciplina}] {len(streams)} atleta(s) reseteados a AnunciadaAP.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Reset UAT INC-4.4 fixture")
    parser.add_argument(
        "--disciplina",
        choices=["DNF", "STA", "ALL"],
        default="ALL",
        help="Disciplina a resetear (default: ALL)",
    )
    args = parser.parse_args()

    with sqlite3.connect(COMPETENCIA_DB) as conn:
        if args.disciplina in ("DNF", "ALL"):
            reset_disciplina(conn, "DNF")
        if args.disciplina in ("STA", "ALL"):
            reset_disciplina(conn, "STA")

    print("\nReset completo. Todos los atletas vuelven a AnunciadaAP.")
    print(f"Verificar: GET /competencia/{COMPETENCIA_ID}/grilla?disciplina=DNF")


if __name__ == "__main__":
    main()
