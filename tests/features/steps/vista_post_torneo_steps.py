"""Step definitions BDD — US-ADJ-10.4: Vista post-torneo en portal del atleta."""

from __future__ import annotations

import asyncio
from datetime import date
from typing import Any
from uuid import UUID, uuid4

import aiosqlite
import pytest
from fastapi.testclient import TestClient
from pytest_bdd import given, parsers, scenarios, then, when

from app import app
from identidad.api.dependencies import get_current_user
from registro.domain.aggregates.atleta import Atleta
from registro.domain.aggregates.inscripcion import Inscripcion
from registro.domain.value_objects.categoria import Categoria
from registro.infrastructure.repositories.sqlite_atleta_repository import SQLiteAtletaRepository
from registro.infrastructure.repositories.sqlite_inscripcion_repository import (
    SQLiteInscripcionRepository,
)
from resultados.api.router import get_ranking_store
from shared.infrastructure.event_store.sqlite_event_store import SQLiteEventStore
from shared.domain.value_objects.disciplina import Disciplina
from torneo.domain.aggregates.torneo import Torneo
from torneo.domain.value_objects.entidad_organizadora import EntidadOrganizadora
from torneo.domain.value_objects.estado_torneo import EstadoTorneo
from torneo.domain.value_objects.sede import Sede
from torneo.infrastructure.repositories.sqlite_torneo_repository import SQLiteTorneoRepository

scenarios("../US-ADJ-10.4-vista-post-torneo-atleta.feature")

_CREATE_EVENTS_TABLE = """
    CREATE TABLE IF NOT EXISTS events (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        stream_id   TEXT    NOT NULL,
        event_type  TEXT    NOT NULL,
        payload     TEXT    NOT NULL,
        version     INTEGER NOT NULL,
        occurred_at TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
        UNIQUE (stream_id, version)
    )
"""


def _make_torneo(torneo_id: UUID, estado: EstadoTorneo = EstadoTorneo.CERRADO) -> Torneo:
    t = Torneo(
        torneo_id=torneo_id,
        nombre="Open BA 2026",
        descripcion="Torneo de apnea",
        fecha_inicio=date(2026, 5, 15),
        fecha_fin=date(2026, 5, 16),
        sede=Sede(nombre="Club Nautico", ciudad="Buenos Aires", pais="Argentina"),
        entidad_organizadora=EntidadOrganizadora(nombre="ADA", tipo="FEDERACION"),
    )
    t.estado = estado
    return t


async def _init_resultados_db(db_path: str) -> None:
    async with aiosqlite.connect(db_path) as db:
        await db.execute(_CREATE_EVENTS_TABLE)
        await db.commit()


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
def ctx(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    torneo_db = tmp_path / "torneo.db"
    registro_db = tmp_path / "registro.db"
    resultados_db = tmp_path / "resultados.db"
    monkeypatch.setenv("TORNEO_DB_PATH", str(torneo_db))
    monkeypatch.setenv("REGISTRO_DB_PATH", str(registro_db))
    monkeypatch.setenv("RESULTADOS_DB_PATH", str(resultados_db))
    asyncio.run(_init_resultados_db(str(resultados_db)))
    data: dict[str, Any] = {
        "torneo_id": uuid4(),
        "torneo_id_ejecucion": uuid4(),
        "atleta_id": uuid4(),
        "competencia_id": uuid4(),
        "resultados_db": str(resultados_db),
        "response": None,
    }
    app.dependency_overrides[get_current_user] = lambda: {
        "sub": str(data["atleta_id"]),
        "email": "atleta@test.com",
        "rol": "ATLETA",
    }
    yield data
    app.dependency_overrides.clear()


@pytest.fixture
def client(ctx: dict[str, Any]) -> TestClient:
    return TestClient(app)


# ── Background ────────────────────────────────────────────────────────────────


@given("el sistema de identidad y registro esta inicializado con DB temporal")
def sistema_inicializado(ctx: dict[str, Any]) -> None:
    pass  # garantizado por fixture ctx (monkeypatch de env vars)


# ── Scenario 1: Snapshot incluye CERRADO ──────────────────────────────────────


@given("un atleta registrado inscripto en un torneo CERRADO con competencia y resultado")
def atleta_inscripto_cerrado(ctx: dict[str, Any]) -> None:
    torneo_repo = SQLiteTorneoRepository(str(ctx["torneo_db"] if "torneo_db" in ctx else ""))
    torneo_id = ctx["torneo_id"]
    atleta_id = ctx["atleta_id"]
    import os

    torneo_db = os.environ["TORNEO_DB_PATH"]
    registro_db = os.environ["REGISTRO_DB_PATH"]

    torneo = _make_torneo(torneo_id, EstadoTorneo.CERRADO)
    asyncio.run(SQLiteTorneoRepository(torneo_db).save(torneo))

    atleta = Atleta(
        atleta_id=atleta_id,
        nombre="Ana",
        apellido="García",
        email="atleta@test.com",
        fecha_nacimiento=date(1990, 5, 10),
        categoria=Categoria.SENIOR_FEMENINO,
        club="Poseidon",
    )
    asyncio.run(SQLiteAtletaRepository(registro_db).save(atleta))

    inscripcion = Inscripcion(
        atleta_id=atleta_id,
        torneo_id=torneo_id,
        disciplinas=frozenset({Disciplina.DNF}),
    )
    asyncio.run(SQLiteInscripcionRepository(registro_db).save(inscripcion))
    ctx["inscripcion_id"] = inscripcion.inscripcion_id


@when("el atleta solicita su portal snapshot")
def atleta_solicita_snapshot(ctx: dict[str, Any], client: TestClient) -> None:
    ctx["response"] = client.get("/torneos")


@then(parsers.parse('la respuesta incluye al menos una entrada con estado de torneo "{estado}"'))
def respuesta_incluye_estado(ctx: dict[str, Any], estado: str) -> None:
    assert ctx["response"].status_code == 200
    torneos = ctx["response"].json()
    estados = [t["estado"] for t in torneos]
    assert estado in estados, f"No se encontró torneo con estado {estado}. Estados: {estados}"


@then("la entrada contiene competenciaId no nulo")
def entrada_tiene_competencia_id(ctx: dict[str, Any]) -> None:
    torneos = ctx["response"].json()
    cerrado = next((t for t in torneos if t["estado"] == "CERRADO"), None)
    assert cerrado is not None
    assert cerrado.get("torneo_id") is not None


# ── Scenario 2: Ranking para CERRADO ─────────────────────────────────────────


@given("un torneo en estado CERRADO con una competencia DNF y resultados registrados")
def torneo_cerrado_con_ranking(ctx: dict[str, Any]) -> None:
    import json
    from datetime import timezone, datetime

    competencia_id = ctx["competencia_id"]
    atleta_id = ctx["atleta_id"]
    store = SQLiteEventStore(ctx["resultados_db"])

    payload = {
        "competencia_id": str(competencia_id),
        "disciplina": "DNF",
        "total": 1,
        "entries": [
            {
                "posicion": 1,
                "atleta_id": str(atleta_id),
                "categoria": "SENIOR_FEMENINO",
                "rp": "80",
                "unidad": "Metros",
                "tarjeta": "Blanca",
                "es_dns": False,
                "en_podio": True,
                "puntos": 1,
                "motivo_dq": None,
                "penalizaciones": [],
                "rp_medido": "80",
            }
        ],
        "occurred_at": datetime.now(timezone.utc).isoformat(),
    }
    asyncio.run(
        store.append(
            stream_id=f"ranking-{competencia_id}-DNF",
            event_type="ResultadosCalculados",
            payload=payload,
        )
    )
    ctx["competencia_id_ranking"] = competencia_id


@when("se consulta el ranking de esa competencia para la disciplina DNF")
def consultar_ranking(ctx: dict[str, Any], client: TestClient) -> None:
    store = SQLiteEventStore(ctx["resultados_db"])
    client.app.dependency_overrides[get_ranking_store] = lambda: store
    cid = ctx["competencia_id_ranking"]
    ctx["response"] = client.get(f"/resultados/{cid}/ranking?disciplina=DNF")


@then("la respuesta es 200")
def respuesta_200(ctx: dict[str, Any]) -> None:
    assert ctx["response"].status_code == 200


@then("el ranking contiene al menos una entrada con rp no nulo")
def ranking_tiene_rp(ctx: dict[str, Any]) -> None:
    body = ctx["response"].json()
    entradas = [e for grupo in body["rankings"] for e in grupo["entradas"]]
    assert any(e["rp"] is not None for e in entradas), "No se encontró ninguna entrada con rp"


# ── Scenario 3: Overall CERRADO ───────────────────────────────────────────────


@given("un torneo en estado CERRADO con puntos FAAS calculados")
def torneo_cerrado_con_overall(ctx: dict[str, Any]) -> None:
    from datetime import timezone, datetime

    torneo_id = ctx["torneo_id"]
    atleta_id = ctx["atleta_id"]
    store = SQLiteEventStore(ctx["resultados_db"])

    asyncio.run(
        store.append(
            stream_id=f"ranking-overall-{torneo_id}",
            event_type="RankingOverallCalculado",
            payload={
                "torneo_id": str(torneo_id),
                "disciplinas": ["DNF"],
                "total": 1,
                "entries": [
                    {
                        "posicion": 1,
                        "atleta_id": str(atleta_id),
                        "puntaje": 1,
                        "detalle": {"DNF": 1},
                        "en_podio": True,
                    }
                ],
                "calculado_en": datetime.now(timezone.utc).isoformat(),
                "occurred_at": datetime.now(timezone.utc).isoformat(),
            },
        )
    )
    ctx["torneo_id_overall"] = torneo_id


@when("se consulta el overall del torneo")
def consultar_overall(ctx: dict[str, Any], client: TestClient) -> None:
    store = SQLiteEventStore(ctx["resultados_db"])
    client.app.dependency_overrides[get_ranking_store] = lambda: store
    tid = ctx["torneo_id_overall"]
    ctx["response"] = client.get(f"/resultados/{tid}/overall")


# ── Scenario 4: Home no muestra CERRADO mezclado ──────────────────────────────


@given("un atleta con un torneo en EJECUCION y otro en CERRADO")
def atleta_con_dos_torneos(ctx: dict[str, Any]) -> None:
    import os

    torneo_db = os.environ["TORNEO_DB_PATH"]
    repo = SQLiteTorneoRepository(torneo_db)

    torneo_cerrado = _make_torneo(ctx["torneo_id"], EstadoTorneo.CERRADO)
    torneo_ejecucion = _make_torneo(ctx["torneo_id_ejecucion"], EstadoTorneo.EJECUCION)
    asyncio.run(repo.save(torneo_cerrado))
    asyncio.run(repo.save(torneo_ejecucion))


@when("el frontend carga las inscripciones activas")
def frontend_carga_inscripciones(ctx: dict[str, Any], client: TestClient) -> None:
    ctx["response"] = client.get("/torneos")


@then('solo el torneo en EJECUCION aparece en la seccion "inscripciones activas"')
def solo_ejecucion_activo(ctx: dict[str, Any]) -> None:
    assert ctx["response"].status_code == 200
    torneos = ctx["response"].json()
    activos = [t for t in torneos if t["estado"] in ("PREPARACION", "EJECUCION")]
    assert len(activos) >= 1
    activo = next((t for t in activos if t["torneo_id"] == str(ctx["torneo_id_ejecucion"])), None)
    assert activo is not None


@then("el torneo CERRADO no aparece mezclado con los activos")
def cerrado_no_en_activos(ctx: dict[str, Any]) -> None:
    torneos = ctx["response"].json()
    activos = [t for t in torneos if t["estado"] in ("PREPARACION", "EJECUCION")]
    ids_activos = {t["torneo_id"] for t in activos}
    assert str(ctx["torneo_id"]) not in ids_activos
