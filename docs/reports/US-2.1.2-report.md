# Reporte US-2.1.2 — Generar / Regenerar Grilla de Salida

**Sprint:** SP2 · **Incremento:** Inc 2.1 — La Grilla de Salida
**Branch:** `feature/US-2.1.2-generar-grilla`
**Fecha:** 2026-03-25
**Estado:** ✅ Completado

---

## Resumen

Implementación del comando `GenerarGrilla` y su handler, incluyendo la lógica de dominio
`Competencia.generar_grilla()`. Cubre ordenamiento STA (tiempo mayor→menor) y DNF (distancia
menor→mayor), cálculo de OTs por posición, y la invariante INV-C-01 (intervalo configurado).

---

## Artefactos producidos

### Dominio
- `src/competencia/domain/value_objects/entrada_grilla.py` — `EntradaGrilla` frozen dataclass
- `src/competencia/domain/events/grilla_de_salida_generada.py` — `GrillaDeSalidaGenerada`
- `src/competencia/domain/ports/performances_ap_port.py` — `PerformancesAPPort` + `PerformancesAPData`
- `src/competencia/domain/aggregates/competencia.py` — extendido: `generar_grilla()`, invariantes, reconstitución

### Aplicación
- `src/competencia/application/commands/generar_grilla.py` — `GenerarGrillaCommand` + `GenerarGrillaHandler`

### Infraestructura
- `src/competencia/infrastructure/repositories/performances_ap_adapter.py` — `PerformancesAPAdapter`

### Tests
- `tests/unit/competencia/domain/test_generar_grilla.py` — 14 tests unitarios de dominio
- `tests/unit/competencia/application/test_generar_grilla_handler.py` — 7 tests del handler
- `tests/integration/competencia/test_generar_grilla_integration.py` — 6 tests de integración
- `tests/features/steps/generar_grilla_steps.py` — 6 escenarios BDD
- `tests/features/US-2.1.2-generar-grilla.feature` — feature file

---

## Métricas de calidad

| Métrica | Valor | Umbral |
|---------|-------|--------|
| Cobertura domain/ | 98% | ≥ 90% |
| Cobertura application/ | 98% | ≥ 90% |
| Tests totales | 33 nuevos (236 acumulados) | — |
| BDD scenarios | 6/6 ✅ | 100% |
| Warnings CodeGuard | 0 (post-fix) | — |
| CRITICAL violations | 0 | 0 |

---

## Invariantes validadas

- **INV-C-01:** Intervalo OT debe estar configurado antes de generar grilla → `IntervaloNoConfigurado`
- **P-01:** STA ordena por AP descendente (tiempo); DNF ordena por AP ascendente (distancia)
- **P-02:** `OT_pos = ot_inicio + timedelta(minutes=(pos-1) * intervalo.minutos)`
- **GrillaYaConfirmada:** No se puede regenerar si la grilla fue confirmada

---

## Decisiones técnicas

- **PerformancesAPPort pattern:** El handler consulta el puerto y pasa los datos al aggregate.
  El aggregate no depende del puerto, manteniendo el dominio puro.
- **tuple inmutable en GrillaDeSalidaGenerada:** `performances: tuple[dict, ...]` para
  cumplir el requisito de frozen dataclass.
- **pytest-bdd 8.x datatables:** Datatables se pasan como `list[list[str]]`, no como objeto
  con `.rows`. Los steps usan `datatable[1:]` para saltar el header.
