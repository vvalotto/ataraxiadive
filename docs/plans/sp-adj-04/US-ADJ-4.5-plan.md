# Plan de Implementación — US-ADJ-4.5
## Ranking y overall por categoría/género

**Branch:** `feature/US-ADJ-4.5-ranking-categoria`
**Sprint:** SP-ADJ-04

---

## Cambios identificados

### src/ (impacto alto)
| Archivo | Cambio |
|---------|--------|
| `src/resultados/domain/ports/resultados_competencia_port.py` | Agregar `categoria` a `ResultadoFinal` y crear `AtletaCategoriaPort` |
| `src/resultados/domain/value_objects/entrada_ranking.py` | Agregar `categoria` |
| `src/resultados/domain/value_objects/entrada_overall.py` | Agregar `categoria` |
| `src/resultados/domain/aggregates/ranking_competencia.py` | Segmentar cálculo y payload persistido por categoría |
| `src/resultados/domain/aggregates/ranking_overall.py` | Segmentar overall por categoría |
| `src/resultados/domain/events/resultados_calculados.py` | Documentar y persistir payload agrupado por categoría |
| `src/resultados/domain/events/ranking_overall_calculado.py` | Documentar y persistir payload agrupado por categoría |
| `src/resultados/application/commands/calcular_ranking.py` | Enriquecer `ResultadoFinal` con categoría vía nuevo port |
| `src/resultados/application/commands/calcular_overall.py` | Reagrupar rankings por categoría para overall |
| `src/resultados/application/queries/obtener_ranking.py` | Proyectar DTO agrupado por categoría |
| `src/resultados/application/queries/obtener_overall.py` | Proyectar DTO agrupado por categoría |
| `src/resultados/api/router.py` | Cambiar shape HTTP de `ranking` y `overall` a `rankings: [{categoria, entradas}]` |
| `src/resultados/infrastructure/repositories/resultados_competencia_adapter.py` | Mantener DTO base y compatibilidad con nuevo enrichment |
| `src/resultados/infrastructure/repositories/atleta_categoria_adapter.py` | Nuevo ACL a Registro para obtener `Categoria` por `atleta_id` |
| `src/app.py` | Inyectar `AtletaCategoriaAdapter` en composición de `CalcularRankingHandler` |

### tests/ (impacto alto)
| Archivo | Cambio |
|---------|--------|
| `tests/unit/resultados/domain/test_ranking_competencia.py` | Cambiar a ranking segmentado por categoría |
| `tests/unit/resultados/domain/test_ranking_overall.py` | Cambiar a overall segmentado por categoría |
| `tests/unit/resultados/application/test_calcular_overall_handler.py` | Ajustar shape agrupado |
| `tests/unit/resultados/application/test_obtener_overall_handler.py` | Ajustar DTO agrupado |
| `tests/unit/resultados/api/test_router_overall.py` | Ajustar contrato HTTP |
| `tests/integration/resultados/*` | Ajustar cálculos y lecturas persistidas |
| `tests/**/resultados*` | Buscar cualquier assert/payload que asuma ranking flat |
| `tests/unit/test_app_p09.py` | Verificar compatibilidad del callback overall |
| `tests/integration/test_p09_callback_integration.py` | Verificar evento overall tras cálculo segmentado |

### docs/ (mínimas de la US)
| Archivo | Cambio |
|---------|--------|
| `docs/plans/sp-adj-04/PLAN-SP-ADJ-04.md` | Marcar progreso cuando la US cierre |
| `docs/reports/US-ADJ-4.5-report.md` | Evidencia de implementación |
| `docs/traceability/matrix.md` | RF-PM-05 pasa a implementado al cerrar |
| `docs/specs/sp-adj-04/US-ADJ-4.5.md` | Mantener sincronía si el inventario final difiere mínimamente |
| `docs/design/domain-model.md` | Confirmar wording de ranking/overall por categoría si requiere ajuste |

---

## Tareas de implementación

1. **[T1]** Modelar categoría dentro de los DTOs y value objects de Resultados
2. **[T2]** Refactorizar `RankingCompetencia` para calcular y reconstituir entradas agrupadas por categoría
3. **[T3]** Refactorizar `RankingOverall` para combinar solo atletas de la misma categoría
4. **[T4]** Crear `AtletaCategoriaPort` y su adaptador de infraestructura hacia BC Registro
5. **[T5]** Adaptar handlers de cálculo para enriquecer resultados y propagar segmentación
6. **[T6]** Adaptar queries y router al nuevo contrato HTTP agrupado
7. **[T7]** Actualizar documentación mínima y trazabilidad de la US

---

## Validación pipeline

1. Ejecutar `pytest` focalizado sobre `tests/unit/resultados`, `tests/integration/resultados`, `tests/unit/test_app_p09.py` y `tests/integration/test_p09_callback_integration.py`
2. Ejecutar `CodeGuard` sobre componentes impactados de `src/resultados` y `src/app.py`
3. Crear reporte de implementación
4. Actualizar tracking y cerrar la US

---

## Riesgos

- Es la US de mayor alcance de `SP-ADJ-04`: cambia dominio, persistencia de eventos, queries y API.
- La reconstitución desde eventos viejos puede requerir compatibilidad hacia atrás si existen payloads flat persistidos.
- El overall hoy asume un único ranking por disciplina; segmentarlo por categoría cambia la forma del acumulado y el contrato del endpoint.
- El nuevo ACL a Registro introduce un acoplamiento extra en Resultados; debe quedar encapsulado detrás del port.
- `P-09` dispara cálculo overall automático; cualquier cambio en shape o streams puede afectar ese callback si no se ajustan bien los tests.

---

## Notas

- Esta US debe ir sola en su branch, como ya lo indica la spec.
- La API resultante debe usar listas por categoría; no se aceptan keys dinámicas en JSON.
- Los tests pertenecen a la validación del pipeline, no a las tareas de implementación.
