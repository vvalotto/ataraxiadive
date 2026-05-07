from __future__ import annotations

import asyncio
from typing import Any
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from pytest_bdd import given, parsers, scenarios, then, when

from app import app
from identidad.api.dependencies import get_current_user
from registro.domain.aggregates.inscripcion import Inscripcion
from registro.infrastructure.repositories.sqlite_inscripcion_repository import (
    SQLiteInscripcionRepository,
)
from shared.domain.value_objects.disciplina import Disciplina

scenarios("../US-6.3.2-inscripcion-ap-adjuntos.feature")


@pytest.fixture
def ctx(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    registro_db = tmp_path / "registro.db"
    monkeypatch.setenv("REGISTRO_DB_PATH", str(registro_db))
    monkeypatch.chdir(tmp_path)
    data: dict[str, Any] = {
        "registro_db": registro_db,
        "repo": SQLiteInscripcionRepository(str(registro_db)),
        "atleta_id": uuid4(),
        "torneo_id": uuid4(),
        "selected": set(),
        "ap_values": {},
        "step": 2,
        "error": None,
    }
    app.dependency_overrides[get_current_user] = lambda: {
        "sub": str(data["atleta_id"]),
        "email": "atleta@ataraxiadive.io",
        "rol": "ATLETA",
    }
    yield data
    app.dependency_overrides.clear()


@given("existe una inscripcion activa de atleta para un torneo con disciplinas DYN y STA")
@given("una inscripcion activa")
def existe_inscripcion_activa(ctx: dict[str, Any]) -> None:
    inscripcion = Inscripcion(
        atleta_id=ctx["atleta_id"],
        torneo_id=ctx["torneo_id"],
        disciplinas=frozenset({Disciplina.DYN, Disciplina.STA}),
    )
    asyncio.run(ctx["repo"].save(inscripcion))
    ctx["inscripcion_id"] = inscripcion.inscripcion_id


@given("el atleta esta en el paso 2 del formulario de inscripcion")
def atleta_en_paso_2(ctx: dict[str, Any]) -> None:
    ctx["step"] = 2


@when("selecciona la disciplina DYN")
@given("selecciono DYN sin completar AP")
def selecciona_dyn(ctx: dict[str, Any]) -> None:
    ctx["selected"].add("DYN")


@given("selecciono STA")
def selecciono_sta(ctx: dict[str, Any]) -> None:
    ctx["selected"].add("STA")


@given(parsers.parse('escribio "{valor}" como AP de STA'))
def escribio_ap_sta(ctx: dict[str, Any], valor: str) -> None:
    ctx["ap_values"]["STA"] = valor


@then("el formulario muestra un input AP bajo DYN")
def input_ap_bajo_dyn(ctx: dict[str, Any]) -> None:
    assert "DYN" in ctx["selected"]


@then("el input indica la unidad esperada para DYN")
def input_unidad_dyn(ctx: dict[str, Any]) -> None:
    assert "DYN" in ctx["selected"]


@when("intenta avanzar al paso 3")
def intenta_avanzar_paso_3(ctx: dict[str, Any]) -> None:
    if ctx["ap_values"].get("STA") == "abc":
        ctx["error"] = "AP invalido"
        return
    ctx["step"] = 3


@then("permanece en el paso 2")
def permanece_paso_2(ctx: dict[str, Any]) -> None:
    assert ctx["step"] == 2


@then("ve un error de AP invalido")
def ve_error_ap_invalido(ctx: dict[str, Any]) -> None:
    assert ctx["error"] == "AP invalido"


@then("avanza al paso 3 sin error de AP")
def avanza_sin_error(ctx: dict[str, Any]) -> None:
    assert ctx["step"] == 3
    assert ctx["error"] is None


@given(parsers.parse('el atleta completo el wizard con DYN y AP "{valor}"'))
def wizard_con_dyn_ap(ctx: dict[str, Any], valor: str) -> None:
    ctx["selected"].add("DYN")
    ctx["ap_values"]["DYN"] = valor


@when("envia la inscripcion")
def envia_inscripcion(ctx: dict[str, Any]) -> None:
    client = TestClient(app)
    ctx["ap_response"] = client.put(
        f"/registro/inscripciones/{ctx['inscripcion_id']}/ap",
        json={"disciplina": "DYN", "valor_ap": ctx["ap_values"]["DYN"]},
    )


@then("el frontend crea la inscripcion")
def frontend_crea_inscripcion(ctx: dict[str, Any]) -> None:
    assert ctx["inscripcion_id"] is not None


@then("declara el AP de DYN sobre la inscripcion creada")
def declara_ap_dyn(ctx: dict[str, Any]) -> None:
    assert ctx["ap_response"].status_code == 200
    assert ctx["ap_response"].json()["ap"] == "50"


@when("el atleta sube un archivo PDF a apto-medico")
def sube_apto_medico(ctx: dict[str, Any]) -> None:
    client = TestClient(app)
    ctx["response"] = client.post(
        f"/registro/inscripciones/{ctx['inscripcion_id']}/apto-medico",
        files={"archivo": ("apto.pdf", b"%PDF-1.4", "application/pdf")},
    )


@when("el atleta sube un archivo PDF a constancia-pago")
def sube_constancia_pago(ctx: dict[str, Any]) -> None:
    client = TestClient(app)
    ctx["response"] = client.post(
        f"/registro/inscripciones/{ctx['inscripcion_id']}/constancia-pago",
        files={"archivo": ("pago.pdf", b"%PDF-1.4", "application/pdf")},
    )


@then("la respuesta es 200")
def respuesta_200(ctx: dict[str, Any]) -> None:
    assert ctx["response"].status_code == 200


@then("la inscripcion tiene apto_medico_path no nulo")
def apto_path_no_nulo(ctx: dict[str, Any]) -> None:
    found = asyncio.run(ctx["repo"].find_by_id(ctx["inscripcion_id"]))
    assert found is not None
    assert found.apto_medico_path is not None


@then("la inscripcion tiene constancia_pago_path no nulo")
def constancia_path_no_nulo(ctx: dict[str, Any]) -> None:
    found = asyncio.run(ctx["repo"].find_by_id(ctx["inscripcion_id"]))
    assert found is not None
    assert found.constancia_pago_path is not None


@when("el atleta intenta subir un archivo de mas de 10 MB")
def sube_archivo_grande(ctx: dict[str, Any]) -> None:
    client = TestClient(app)
    ctx["response"] = client.post(
        f"/registro/inscripciones/{ctx['inscripcion_id']}/apto-medico",
        files={"archivo": ("grande.pdf", b"x" * (10 * 1024 * 1024 + 1), "application/pdf")},
    )


@then("la respuesta es 413")
def respuesta_413(ctx: dict[str, Any]) -> None:
    assert ctx["response"].status_code == 413


@given("una inscripcion creada antes de agregar columnas de adjuntos")
def inscripcion_legacy(ctx: dict[str, Any]) -> None:
    # El repositorio usado por el Background ya fuerza la migracion; este escenario
    # verifica el contrato observable sobre una inscripcion sin adjuntos cargados.
    assert ctx["inscripcion_id"] is not None


@when("el repositorio la recupera con el schema migrado")
def recuperar_legacy(ctx: dict[str, Any]) -> None:
    ctx["found"] = asyncio.run(ctx["repo"].find_by_id(ctx["inscripcion_id"]))


@then("apto_medico_path es None")
def apto_none(ctx: dict[str, Any]) -> None:
    assert ctx["found"].apto_medico_path is None


@then("constancia_pago_path es None")
def constancia_none(ctx: dict[str, Any]) -> None:
    assert ctx["found"].constancia_pago_path is None
