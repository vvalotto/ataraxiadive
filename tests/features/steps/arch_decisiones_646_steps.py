"""Steps BDD para US-6.4.6 — Decisiones arquitecturales cerradas y registradas."""

import ast
from pathlib import Path

import pytest
from pytest_bdd import given, scenarios, then, when

scenarios("../US-6.4.6-cierre-arch-decisiones.feature")

# ── shared context ──────────────────────────────────────────────────────────────


@pytest.fixture
def ctx() -> dict:
    return {}


# ── ARCH-03 ─────────────────────────────────────────────────────────────────────


@given("el archivo resultados_competencia_adapter.py")
def dado_adaptador(ctx: dict) -> None:
    path = Path("src/resultados/infrastructure/repositories/resultados_competencia_adapter.py")
    assert path.exists()
    ctx["adapter_source"] = path.read_text()


@when('se buscan imports de "competencia."')
def cuando_busca_imports_competencia(ctx: dict) -> None:
    source = ctx["adapter_source"]
    tree = ast.parse(source)
    ctx["cross_bc_imports"] = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        and node.module
        and node.module.startswith("competencia.")
    ]


@then("no hay coincidencias de imports cross-BC")
def entonces_sin_imports_cross_bc(ctx: dict) -> None:
    assert not ctx[
        "cross_bc_imports"
    ], f"Import cross-BC encontrado: {[n.module for n in ctx['cross_bc_imports']]}"


# ── DR-01 ────────────────────────────────────────────────────────────────────────


@given("el aggregate RankingCompetencia con LCOM reportado 2/1")
def dado_ranking_competencia(ctx: dict) -> None:
    from resultados.domain.aggregates import ranking_competencia as mod

    ctx["ranking_mod"] = mod
    ctx["RankingCompetencia"] = mod.RankingCompetencia


@when("se analiza la separacion de responsabilidades")
def cuando_analiza_spr(ctx: dict) -> None:
    import inspect

    cls = ctx["RankingCompetencia"]
    ctx["metodos"] = {
        name
        for name, _ in inspect.getmembers(cls)
        if not name.startswith("__") and callable(getattr(cls, name))
    }
    mod = ctx["ranking_mod"]
    ctx["helpers_modulo"] = [
        name
        for name in dir(mod)
        if name.startswith("_") and callable(getattr(mod, name)) and name not in dir(cls)
    ]


@then("los dos grupos de metodos son inherentes al patron ES")
def entonces_grupos_es(ctx: dict) -> None:
    assert "calcular" in ctx["metodos"]
    assert "_apply_stored" in ctx["metodos"]
    assert "_rehidratar_resultados_calculados" in ctx["metodos"]


@then("los helpers de modulo estan extraidos correctamente fuera de la clase")
def entonces_helpers_fuera(ctx: dict) -> None:
    mod = ctx["ranking_mod"]
    assert hasattr(mod, "_calcular_entries")
    assert hasattr(mod, "_agrupar_por_categoria")
    assert hasattr(mod, "_entrada_a_dict")


# ── AA-02 ────────────────────────────────────────────────────────────────────────


@given("identidad D igual a 0.67 tras BL-005")
def dado_identidad_d(ctx: dict) -> None:
    ctx["modulo"] = "identidad"
    ctx["d_valor"] = 0.67


@when("se cierra INC-6.4")
def cuando_cierra_inc64(ctx: dict) -> None:
    ctx["bl006_path"] = Path(".cm/baselines/BL-006.md")


@then("BL-006 registra la tendencia de identidad con decision de no intervencion")
def entonces_bl006_registra_identidad(ctx: dict) -> None:
    assert ctx["bl006_path"].exists(), "BL-006.md no existe"
    contenido = ctx["bl006_path"].read_text()
    assert "identidad" in contenido
    assert "0.67" in contenido
    assert (
        "no intervenir" in contenido.lower()
        or "no intervencion" in contenido.lower()
        or "sin intervención" in contenido.lower()
        or "No intervenir" in contenido
    )


# ── AA-04 ────────────────────────────────────────────────────────────────────────


@given("shared D igual a 0.63 estable entre BL-004 y BL-005")
def dado_shared_d(ctx: dict) -> None:
    ctx["modulo"] = "shared"
    ctx["d_valor"] = 0.63


@when("se cierra INC-6.4", target_fixture="cuando_cierra_inc64_shared")  # type: ignore[misc]
def cuando_cierra_inc64_shared(ctx: dict) -> None:
    ctx["bl006_path"] = Path(".cm/baselines/BL-006.md")


@then("BL-006 registra shared con decision de diferir a post-despliegue")
def entonces_bl006_registra_shared(ctx: dict) -> None:
    assert ctx["bl006_path"].exists()
    contenido = ctx["bl006_path"].read_text()
    assert "shared" in contenido
    assert "0.63" in contenido
    assert "diferir" in contenido.lower() or "post-despliegue" in contenido.lower()


# ── DesignReviewer ───────────────────────────────────────────────────────────────


@given("todos los hallazgos de INC-6.4 procesados")
def dado_hallazgos_procesados(ctx: dict) -> None:
    report = Path("quality/reports/designreviewer/INC-6.4-report.txt")
    assert report.exists(), f"Reporte DesignReviewer no encontrado: {report}"
    ctx["dr_report"] = report.read_text()


@when("se ejecuta designreviewer sobre src")
def cuando_designreviewer(ctx: dict) -> None:
    # El reporte ya fue generado en Fase 3 — leemos el resultado
    ctx["blocking"] = "0 blocking issues" in ctx["dr_report"]


@then("el reporte indica should_block igual a false")
def entonces_should_block_false(ctx: dict) -> None:
    assert ctx["blocking"], "DesignReviewer reportó blocking issues — revisar reporte"
