# Reporte de Implementación — US-5.6.1

**Historia:** Puerto AlgoritmoPuntaje + AlgoritmoPuntajeFAAS  
**Incremento:** INC-5.6  
**Subproyecto:** SP5 — La Puesta en Marcha  
**Producto:** resultados  
**Fecha:** 2026-04-26  
**Duración total:** ~12 min  

---

## Resumen Ejecutivo

Implementación del patrón Strategy para el cálculo de puntajes según reglamento FAAS. Se introdujo el puerto abstracto `AlgoritmoPuntaje` y la primera implementación concreta `AlgoritmoPuntajeFAAS`, que aplica las fórmulas de la Federación Argentina de Apnea Submarina para disciplinas de distancia y tiempo.

**Estado final:** ✅ Completo — todos los gates verdes

---

## Artefactos Producidos

| Artefacto | Ruta | Tipo |
|-----------|------|------|
| Puerto abstracto | `src/resultados/domain/ports/algoritmo_puntaje.py` | Nuevo |
| Implementación FAAS | `src/resultados/domain/services/algoritmo_faas.py` | Nuevo |
| Init servicios | `src/resultados/domain/services/__init__.py` | Nuevo |
| Init ports (export) | `src/resultados/domain/ports/__init__.py` | Modificado |
| Feature BDD | `tests/features/US-5.6.1-algoritmo-puntaje-faas.feature` | Nuevo |
| Steps BDD | `tests/features/steps/test_US_5_6_1_steps.py` | Nuevo |
| Tests unitarios | `tests/unit/resultados/domain/test_algoritmo_faas.py` | Nuevo |
| CodeGuard report | `quality/reports/codeguard/US-5.6.1-codeguard-raw.json` | Nuevo |

---

## Resultados de Tests

| Suite | Tests | Estado |
|-------|-------|--------|
| Unitarios — `TestDistancia` | 6 | ✅ |
| Unitarios — `TestTiempo` | 5 | ✅ |
| Unitarios — `TestCasosBorde` | 4 | ✅ |
| BDD — 8 escenarios | 8 | ✅ |
| **Total** | **23** | **✅** |

Regresión BC Resultados completo: 67 tests pasando.

---

## Quality Gates

| Gate | Resultado |
|------|-----------|
| CodeGuard — errores | 0 |
| CodeGuard — advertencias | 1 (CC=11 en `_calcular_tiempo` — lógica inherente al algoritmo) |
| PEP8 | ✅ Compliant |
| Seguridad | ✅ Sin issues |
| DesignReviewer | Pendiente (cierre INC-5.6) |

---

## Decisiones Técnicas

- **Patrón Strategy:** `AlgoritmoPuntaje` es el puerto (ABC); `AlgoritmoPuntajeFAAS` es la primera implementación. Permite agregar CMAS/AIDA sin modificar el dominio (OCP).
- **Fórmula distancia:** `P_i = (d_i / d_max) × 100` — solo atletas con tarjeta blanca participan del denominador.
- **Fórmula tiempo:** `P_i = (t_max - t_i) / (t_max - t_min) × 100` — caso borde `t_max == t_min` → todos reciben 100.
- **DNS y Tarjeta Roja:** 0 puntos, excluidos del cálculo de referencia.
- **Precisión:** 2 decimales con `ROUND_HALF_UP` (reglamento FAAS).
- **`Disciplina.es_tiempo()`:** reutiliza método existente en `shared/` — sin nueva lógica de discriminación.
