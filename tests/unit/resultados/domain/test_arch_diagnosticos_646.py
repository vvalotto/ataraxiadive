"""Tests de diagnóstico arquitectural US-6.4.6 — ARCH-03 y DR-01."""

import ast
import inspect
from pathlib import Path

from resultados.domain.aggregates.ranking_competencia import RankingCompetencia

# tests/unit/resultados/domain/ → 4 niveles hasta la raíz del proyecto
_PROJECT_ROOT = Path(__file__).resolve().parents[4]
_ADAPTER_PATH = (
    _PROJECT_ROOT / "src/resultados/infrastructure/repositories/resultados_competencia_adapter.py"
)


def test_arch03_adaptador_no_importa_competencia() -> None:
    """ARCH-03: ResultadosCompetenciaAdapter no importa nada de competencia.*"""
    source = _ADAPTER_PATH.read_text()
    tree = ast.parse(source)
    cross_bc_imports = [
        node
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        if isinstance(node, ast.ImportFrom)
        and node.module
        and node.module.startswith("competencia.")
    ]
    assert (
        not cross_bc_imports
    ), f"ARCH-03 violado: imports cross-BC encontrados: {[n.module for n in cross_bc_imports]}"


def test_arch03_adaptador_solo_importa_shared_y_resultados() -> None:
    """ARCH-03: Los imports del adaptador no incluyen ningún BC externo (solo shared, resultados, stdlib)."""
    bcs_externos = {"competencia.", "torneo.", "registro.", "identidad.", "notificaciones."}
    source = _ADAPTER_PATH.read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            modulo = node.module
            for bc in bcs_externos:
                assert not modulo.startswith(
                    bc
                ), f"ARCH-03 violado: import de BC externo en adaptador: {modulo}"


def test_dr01_ranking_competencia_metodos_de_instancia() -> None:
    """DR-01: RankingCompetencia tiene exactamente los grupos esperados en ES."""
    # getmembers incluye functions y classmethods — usar todos los nombres no dunder
    todos_los_metodos = {
        name
        for name, _ in inspect.getmembers(RankingCompetencia)
        if not name.startswith("__") and callable(getattr(RankingCompetencia, name))
    }
    grupo_comando = {"calcular"}
    grupo_reconstitucion = {"reconstitute", "_apply_stored", "_rehidratar_resultados_calculados"}

    assert grupo_comando.issubset(
        todos_los_metodos
    ), f"Métodos de comando faltantes: {grupo_comando - todos_los_metodos}"
    assert grupo_reconstitucion.issubset(
        todos_los_metodos
    ), f"Métodos ES faltantes: {grupo_reconstitucion - todos_los_metodos}"


def test_dr01_helpers_de_modulo_estan_fuera_de_la_clase() -> None:
    """DR-01: Los helpers de cálculo son funciones de módulo, no métodos de instancia."""
    import resultados.domain.aggregates.ranking_competencia as mod

    helpers_esperados = [
        "_calcular_entries",
        "_deserializar_entries",
        "_agrupar_por_categoria",
        "_calcular_entries_categoria_con_puntos",
        "_calcular_entries_categoria_legacy",
        "_crear_entry_valida",
        "_crear_entry_invalida",
        "_entrada_a_dict",
        "_dict_a_entrada",
    ]
    for helper in helpers_esperados:
        fn = getattr(mod, helper, None)
        assert fn is not None, f"Helper de módulo '{helper}' no encontrado"
        assert callable(fn), f"'{helper}' no es callable"
        assert not isinstance(fn, type), f"'{helper}' no debe ser una clase"
