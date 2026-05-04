from __future__ import annotations

import json
import re
import zlib
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
INPUT_DIR = ROOT / "data" / "datos_prueba"
OUTPUT_DIR = ROOT / "data" / "datasets" / "buenos_aires_2025"

DISCIPLINE_FILES = {
    "DBF": "DBF (Buenos Aires 2025).pdf",
    "DNF": "DNF (Buenos Aires 2025).pdf",
    "DYN": "DYN (Buenos Aires 2025).pdf",
    "SPE": "SPE (Buenos Aires 2025).pdf",
    "STA": "STA (Buenos Aires 2025).pdf",
}

CATEGORIES = ("JUNIOR", "SENIOR", "MASTER")
RESULT_PATTERN = re.compile(r"(DNS|DQ|\d{2}:\d{2}[,.]\d{2}|\d{2}:\d{2}\.\d{2}|\d+,\d{2})$")


@dataclass(frozen=True)
class TextItem:
    page: int
    x: float
    y: float
    font: str
    text: str


def _load_objects(pdf_path: Path) -> dict[int, bytes]:
    data = pdf_path.read_bytes()
    objects: dict[int, bytes] = {}
    for match in re.finditer(rb"(\d+)\s+(\d+)\s+obj(.*?)endobj", data, re.S):
        objects[int(match.group(1))] = match.group(3).strip()
    return objects


def _load_cmaps(objects: dict[int, bytes]) -> dict[int, dict[int, str]]:
    cmaps: dict[int, dict[int, str]] = {}
    for obj_id, body in objects.items():
        if b"stream" not in body:
            continue
        header, stream_part = body.split(b"stream", 1)
        stream, _ = stream_part.split(b"endstream", 1)
        stream = stream.strip(b"\r\n")
        if b"/FlateDecode" in header:
            try:
                stream = zlib.decompress(stream)
            except zlib.error:
                continue
        if b"beginbfchar" not in stream:
            continue

        cmap: dict[int, str] = {}
        for src, dst in re.findall(rb"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>", stream):
            cmap[int(src, 16)] = bytes.fromhex(dst.decode()).decode("utf-16-be")
        cmaps[obj_id] = cmap
    return cmaps


def extract_text_items(pdf_path: Path) -> list[TextItem]:
    objects = _load_objects(pdf_path)
    cmaps = _load_cmaps(objects)

    page_ids = []
    for obj_id, body in objects.items():
        if b"/Type /Page" in body and b"/Parent" in body:
            page_ids.append(obj_id)
    page_ids.sort()

    items: list[TextItem] = []
    for page_number, page_id in enumerate(page_ids, start=1):
        page = objects[page_id]
        resources_id = int(re.search(rb"/Resources\s+(\d+)\s+0\s+R", page).group(1))
        resources = objects[resources_id]
        fonts = {
            name.decode(): int(font_id)
            for name, font_id in re.findall(rb"/(F\d+)\s+(\d+)\s+0\s+R", resources)
        }
        font_cmaps: dict[str, dict[int, str]] = {}
        for font_name, font_obj_id in fonts.items():
            match = re.search(rb"/ToUnicode\s+(\d+)\s+0\s+R", objects[font_obj_id])
            font_cmaps[font_name] = cmaps.get(int(match.group(1)), {}) if match else {}

        contents_array = re.search(rb"/Contents\s*\[(.*?)\]", page, re.S)
        if contents_array:
            content_ids = [int(value) for value in re.findall(rb"(\d+)\s+0\s+R", contents_array.group(1))]
        else:
            content_ids = [int(re.search(rb"/Contents\s+(\d+)\s+0\s+R", page).group(1))]

        for content_id in content_ids:
            content = objects[content_id]
            header, stream_part = content.split(b"stream", 1)
            stream, _ = stream_part.split(b"endstream", 1)
            stream = stream.strip(b"\r\n")
            if b"/FlateDecode" in header:
                stream = zlib.decompress(stream)
            text = stream.decode("latin1", "ignore")

            current_font = ""
            x = 0.0
            y = 0.0
            for line in text.split("\n"):
                font_match = re.search(r"/(F\d+)\s+\d+(?:\.\d+)?\s+Tf", line)
                if font_match:
                    current_font = font_match.group(1)
                tm_match = re.search(r"1 0 0(?:\.0+)? -1 ([0-9.]+) ([0-9.]+) Tm", line)
                if tm_match:
                    x = float(tm_match.group(1))
                    y = float(tm_match.group(2))

                for array_content in re.findall(r"\[(.*?)\]\s*TJ", line):
                    chars: list[str] = []
                    for hex_group in re.findall(r"<([0-9A-Fa-f]+)>", array_content):
                        raw = bytes.fromhex(hex_group)
                        cmap = font_cmaps.get(current_font, {})
                        for index in range(0, len(raw), 2):
                            code = int.from_bytes(raw[index:index + 2], "big")
                            chars.append(cmap.get(code, f"<{code:04X}>"))
                    decoded = "".join(chars).strip()
                    if decoded:
                        items.append(TextItem(page=page_number, x=x, y=y, font=current_font, text=decoded))

    return items


def parse_name_category_club(value: str) -> tuple[str, str, str]:
    for category in CATEGORIES:
        index = value.find(category)
        if index != -1:
            return value[:index].strip(), category, value[index + len(category):].strip()
    raise ValueError(f"No se pudo separar nombre/categoría/club: {value!r}")


def parse_schedule_pdf(discipline: str, pdf_path: Path) -> list[dict[str, object]]:
    items = extract_text_items(pdf_path)
    row_starts = [
        item
        for item in items
        if item.page == 1 and item.font == "F2" and item.x < 200 and item.y > 110
    ]
    rows: list[dict[str, object]] = []
    for row in row_starts:
        row_items = [item for item in items if item.page == 1 and abs(item.y - row.y) < 0.35]
        athlete_block = next(item.text for item in row_items if item.x < 200 and item.font == "F2")
        announced = next(item.text for item in row_items if 700 < item.x < 800)
        schedule_info = next(item.text for item in row_items if item.x > 800 and item.font == "F2")
        name, category, club = parse_name_category_club(athlete_block)
        line = int(schedule_info[-1])
        official_slot = schedule_info[:-1]
        rows.append(
            {
                "discipline": discipline,
                "source_pdf": pdf_path.name,
                "name": name,
                "category": category,
                "club": club,
                "announced_performance": announced,
                "official_slot": official_slot,
                "line": line,
            }
        )
    return rows


RESULT_SECTION_RULES: dict[int, list[tuple[float, float, str, str]]] = {
    1: [
        (110.0, 370.0, "STA", "FEMENINO"),
        (420.0, 800.0, "STA", "MASCULINO"),
        (840.0, 1200.0, "DNF", "FEMENINO"),
    ],
    2: [
        (120.0, 560.0, "DNF", "MASCULINO"),
        (560.0, 860.0, "DYN", "FEMENINO"),
        (860.0, 1200.0, "DYN", "MASCULINO"),
    ],
    3: [
        (0.0, 260.0, "DYN", "MASCULINO"),
        (260.0, 560.0, "DBF", "FEMENINO"),
        (560.0, 1020.0, "DBF", "MASCULINO"),
        (1020.0, 1200.0, "SPE", "FEMENINO"),
    ],
    4: [
        (0.0, 300.0, "SPE", "FEMENINO"),
        (300.0, 650.0, "SPE", "MASCULINO"),
        (650.0, 900.0, "OVERALL", "FEMENINO"),
        (900.0, 1200.0, "OVERALL", "MASCULINO"),
    ],
}


def classify_result_section(page: int, y: float) -> tuple[str, str]:
    for start, end, discipline, sex in RESULT_SECTION_RULES[page]:
        if start <= y < end:
            return discipline, sex
    raise ValueError(f"No se pudo clasificar page={page} y={y}")


def parse_result_row(value: str) -> tuple[str, str, str, str]:
    match = RESULT_PATTERN.search(value)
    if not match:
        raise ValueError(f"No se pudo separar el resultado de {value!r}")
    result = match.group(1)
    prefix = value[:match.start()].strip()
    name, category, club = parse_name_category_club(prefix)
    return name, category, club, result


def parse_overall_row(value: str) -> tuple[str, str, str, str]:
    for sex in ("FEMENINO", "MASCULINO"):
        if value.endswith(sex):
            prefix = value[:-len(sex)].strip()
            name, category, club = parse_name_category_club(prefix)
            return name, category, club, sex
    raise ValueError(f"No se pudo separar el sexo de {value!r}")


def parse_results_pdf(pdf_path: Path) -> list[dict[str, object]]:
    items = extract_text_items(pdf_path)
    rank_items = [
        item
        for item in items
        if item.font in {"F2", "F3"} and item.x < 100 and item.text.isdigit()
    ]
    results: list[dict[str, object]] = []
    for rank_item in rank_items:
        row_items = [
            item
            for item in items
            if item.page == rank_item.page and abs(item.y - rank_item.y) < 0.35 and item.x > 100
        ]
        athlete_item = next(item for item in row_items if item.font in {"F2", "F3"})
        discipline, sex = classify_result_section(rank_item.page, rank_item.y)
        if discipline == "OVERALL":
            name, category, club, sex = parse_overall_row(athlete_item.text)
            result = None
        else:
            name, category, club, result = parse_result_row(athlete_item.text)
        results.append(
            {
                "discipline": discipline,
                "sex": sex,
                "rank": int(rank_item.text),
                "page": rank_item.page,
                "name": name,
                "category": category,
                "club": club,
                "result": result,
            }
        )
    return results


def build_athlete_index(
    schedules: Iterable[dict[str, object]],
    results: Iterable[dict[str, object]],
) -> list[dict[str, object]]:
    merged: dict[tuple[str, str], dict[str, object]] = {}

    for row in schedules:
        key = (str(row["discipline"]), str(row["name"]))
        merged[key] = {
            "discipline": row["discipline"],
            "name": row["name"],
            "category": row["category"],
            "club": row["club"],
            "announced_performance": row["announced_performance"],
            "official_slot": row["official_slot"],
            "line": row["line"],
            "results": [],
        }

    for row in results:
        key = (str(row["discipline"]), str(row["name"]))
        merged.setdefault(
            key,
            {
                "discipline": row["discipline"],
                "name": row["name"],
                "category": row["category"],
                "club": row["club"],
                "announced_performance": None,
                "official_slot": None,
                "line": None,
                "results": [],
            },
        )
        merged[key]["results"].append(
            {
                "sex": row["sex"],
                "rank": row["rank"],
                "result": row["result"],
                "page": row["page"],
            }
        )

    return sorted(merged.values(), key=lambda row: (row["discipline"], row["name"]))


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    schedules = []
    for discipline, filename in DISCIPLINE_FILES.items():
        schedules.extend(parse_schedule_pdf(discipline, INPUT_DIR / filename))

    results = parse_results_pdf(
        INPUT_DIR / "Resultados Competencia Apnea Indoor Buenos Aires 2025.pdf"
    )
    athlete_index = build_athlete_index(schedules, results)

    summary = {
        "competition": "Apnea Indoor Buenos Aires 2025",
        "source_dir": str(INPUT_DIR.relative_to(ROOT)),
        "schedule_rows": len(schedules),
        "result_rows": len(results),
        "athlete_entries": len(athlete_index),
        "disciplines": sorted({row["discipline"] for row in schedules}),
    }

    (OUTPUT_DIR / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (OUTPUT_DIR / "schedules.json").write_text(
        json.dumps(schedules, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (OUTPUT_DIR / "results.json").write_text(
        json.dumps(results, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (OUTPUT_DIR / "athlete_index.json").write_text(
        json.dumps(athlete_index, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
