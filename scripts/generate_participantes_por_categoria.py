from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = ROOT / "data" / "datasets" / "buenos_aires_2025" / "athlete_index.json"
OUTPUT_PATH = ROOT / "data" / "datasets" / "buenos_aires_2025" / "participantes_por_categoria.csv"

CATEGORY_ORDER = {"JUNIOR": 0, "SENIOR": 1, "MASTER": 2}


def main() -> None:
    rows = json.loads(DATASET_PATH.read_text(encoding="utf-8"))

    participants: dict[tuple[str, str, str], set[str]] = defaultdict(set)
    for row in rows:
        discipline = row["discipline"]
        if discipline == "OVERALL":
            continue
        key = (row["name"], row["category"], row["club"])
        participants[key].add(discipline)

    ordered_rows = sorted(
        (
            {
                "nombre y apellido": name,
                "categoria": category,
                "escuela": club,
                "disciplinas": ", ".join(sorted(disciplines)),
            }
            for (name, category, club), disciplines in participants.items()
        ),
        key=lambda row: (
            CATEGORY_ORDER.get(row["categoria"], 99),
            row["nombre y apellido"],
            row["escuela"],
        ),
    )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["nombre y apellido", "categoria", "escuela", "disciplinas"],
            delimiter=";",
        )
        writer.writeheader()
        writer.writerows(ordered_rows)

    print(f"Archivo generado: {OUTPUT_PATH}")
    print(f"Participantes: {len(ordered_rows)}")


if __name__ == "__main__":
    main()
