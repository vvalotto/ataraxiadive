# Plan de Implementación — US-2.1.2
# Generar / Regenerar Grilla de Salida

**Fecha:** 2026-03-25
**Branch:** `feature/US-2.1.2-generar-grilla`
**Estimación:** 60-90 min

---

## Artefactos nuevos

| # | Tipo | Archivo | Descripción |
|---|------|---------|-------------|
| T1 | NEW | `domain/value_objects/entrada_grilla.py` | Dataclass `EntradaGrilla` — una fila de la grilla (performance_id, atleta_id, posicion, andarivel, ot_programado) |
| T2 | NEW | `domain/events/grilla_de_salida_generada.py` | `GrillaDeSalidaGenerada` — snapshot completo de la grilla |
| T3 | NEW | `domain/ports/performances_ap_port.py` | `PerformancesAPPort` (ABC) + `PerformancesAPData` (DTO) — contrato para consultar APs de una competencia |
| T4 | MOD | `domain/aggregates/competencia.py` | Agregar `generar_grilla()` + `_apply_grilla_de_salida_generada()` en dispatch |
| T5 | NEW | `infrastructure/repositories/performances_ap_adapter.py` | Implementación de `PerformancesAPPort` que lee el Event Store |
| T6 | NEW | `application/commands/generar_grilla.py` | `GenerarGrillaCommand` + `GenerarGrillaHandler` |

## Tests

| # | Tipo | Archivo | Descripción |
|---|------|---------|-------------|
| T7 | NEW | `tests/unit/competencia/domain/test_generar_grilla.py` | Tests unitarios del método `generar_grilla()` — ordenamiento P-01, cálculo OT P-02, invariantes |
| T8 | NEW | `tests/unit/competencia/application/test_generar_grilla_handler.py` | Tests del handler con mocks |
| T9 | NEW | `tests/integration/competencia/test_generar_grilla_integration.py` | Test E2E con SQLite real: AP → GenerarGrilla → stream |
| T10 | NEW | `tests/features/steps/generar_grilla_steps.py` | Step definitions BDD (6 escenarios) |

---

## Lógica de negocio clave

### Ordenamiento P-01
- `Disciplina.es_tiempo()` → sort AP descendente (STA: mayor primero)
- `Disciplina.es_distancia()` → sort AP ascendente (DNF/DYN: menor primero)

### Cálculo OT P-02
```
ot_atleta = ot_inicio + timedelta(minutes=(posicion - 1) * intervalo.minutos)
```

### Flujo del handler
1. Load stream `competencia-{id}` → reconstituir `Competencia`
2. Llamar `PerformancesAPPort.get_performances_con_ap(competencia_id)` → lista de `PerformancesAPData`
3. `competencia.generar_grilla(ot_inicio, performances, andariveles=1)`
4. Persistir `GrillaDeSalidaGenerada` en stream `competencia-{id}`

### PerformancesAPAdapter
- Lee todos los streams `performance-{competencia_id}-*`
- Por cada stream, reconstruye la Performance y extrae (performance_id, atleta_id, ap)
- Filtra solo los que tienen `_estado == AnunciadaAP`

---

## Orden de ejecución

```
T1 → T2 → T3 → T4 → T5 → T6   (dominio → infra → aplicación)
T7 → T8 → T9 → T10              (tests al final)
```

---

*Generado en Fase 2 de /implement-us*
