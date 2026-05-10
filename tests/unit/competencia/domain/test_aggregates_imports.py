"""Regresiones de imports para aggregates de competencia."""

from __future__ import annotations

import importlib


def test_imports_directos_de_aggregates_funcionan() -> None:
    """Los consumidores deben importar cada aggregate desde su modulo concreto."""
    competencia_module = importlib.import_module("competencia.domain.aggregates.competencia")
    performance_module = importlib.import_module("competencia.domain.aggregates.performance")

    assert competencia_module.Competencia.__name__ == "Competencia"
    assert performance_module.Performance.__name__ == "Performance"


def test_paquete_aggregates_no_reexporta_aggregate_roots() -> None:
    """El paquete no importa aggregates concretos para evitar ciclos ADP."""
    aggregates_package = importlib.import_module("competencia.domain.aggregates")

    assert not hasattr(aggregates_package, "Competencia")
    assert not hasattr(aggregates_package, "Performance")
