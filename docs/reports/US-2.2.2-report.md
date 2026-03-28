# Reporte Final — US-2.2.2: API Disciplina-Aware

| Campo | Valor |
|-------|-------|
| **US** | US-2.2.2 |
| **Incremento** | Inc 2.2 |
| **Branch** | `feature/US-2.2.2-api-disciplina-aware` |
| **Fecha** | 2026-03-27 |
| **Estado** | ✅ Completa |

---

## Resumen

US-2.2.2 agrega validación de unidades (disciplina-aware) en los commands de
registro (AP y Resultado) y ordena `ProximasPerformances` según la posición
real de la grilla oficial (aggregate Competencia). También expone `unidad_esperada`
en el DTO de `PerformanceActual`.

---

## Cambios Implementados

### Domain
- `Performance` aggregate: propiedades `posicion_grilla` y `disciplina` derivadas del stream.

### Application — Commands
- `registrar_ap.py`: validación `UnidadIncompatible` antes de persistir APRegistrado.
- `registrar_resultado.py`: validación `UnidadIncompatible` antes de persistir ResultadoRegistrado.

### Application — Queries
- `ObtenerProximasPerformancesQuery`: requiere `disciplina: Disciplina`.
- `ObtenerProximasPerformancesHandler`: construye `grilla_map` desde el aggregate Competencia y ordena por posición.
- `ObtenerPerformanceActualHandler`: incluye `unidad_esperada` en `PerformanceActualDTO`.

### API
- `router.py`: `DisciplinaDescriptorDep` inyectado en `get_performance_actual`.
  Query param `disciplina` en `/performance/proximas`.
  Campo `unidad_esperada` en la respuesta de `/performance/actual`.

---

## Métricas de Calidad

| Métrica | Valor |
|---------|-------|
| Tests totales | 409 (↑ 14 desde US-2.2.1) |
| Unit tests nuevos | 5 |
| Integration tests nuevos | 2 |
| BDD scenarios nuevos | 7 |
| Cobertura (domain + application) | 97% |
| CodeGuard errores | 0 |
| CodeGuard advertencias | 4 (preexistentes) |
| Regresiones | 0 |

---

## Invariantes Verificadas

| Invariante | Descripción | Test |
|-----------|-------------|------|
| P-06 | STA requiere Segundos; DNF/DYN/CWT requieren Metros | `test_unidad_incompatible_*` |
| P-06 | Unidad incorrecta no persiste eventos | `test_*_no_persiste` |
| P-07 | ProximasPerformances ordena por posición real de grilla | `test_ordena_por_posicion_grilla` |
| — | `unidad_esperada` expuesta en `/performance/actual` | BDD Scenario 6 y 7 |

---

## Tests Corregidos (regresiones preexistentes)

| Archivo | Corrección |
|---------|------------|
| `test_registrar_ap_integration.py` | Fixture `handler` faltaba `disciplina_descriptor=DisciplinaDescriptorAdapter()` |
| `test_registrar_ap_handler.py` | `test_handle_stream_id_contiene_natural_key`: DNF necesita `UnidadMedida.Metros` |
| Múltiples (sesión anterior) | STA+Metros → STA+Segundos en 7+ archivos |
