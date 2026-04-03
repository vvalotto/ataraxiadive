# Reporte de Implementación — US-ADJ-4.5
## Ranking y overall por categoría/género

**Sprint:** SP-ADJ-04
**Branch:** `feature/US-ADJ-4.5-ranking-categoria`
**Fecha:** 2026-04-03

---

## Resumen

BC Resultados dejó de calcular rankings flat. Tanto `GET /resultados/{id}/ranking`
como `GET /resultados/{torneo_id}/overall` ahora responden agrupados por
categoría/género, y el cálculo interno segmenta posiciones, podio y acumulados
por `Categoria`.

La categoría del atleta se incorpora en el cálculo de ranking mediante un nuevo
ACL hacia BC Registro (`AtletaCategoriaAdapter`), manteniendo a Resultados
desacoplado del detalle de persistencia de Registro.

---

## Cambios implementados

### Código
| Archivo | Cambio |
|---------|--------|
| `src/resultados/domain/ports/resultados_competencia_port.py` | `ResultadoFinal` incorpora `categoria`; nuevo `AtletaCategoriaPort` |
| `src/resultados/domain/value_objects/entrada_ranking.py` | `EntradaRanking` incorpora `categoria` |
| `src/resultados/domain/value_objects/entrada_overall.py` | `EntradaOverall` incorpora `categoria` |
| `src/resultados/domain/aggregates/ranking_competencia.py` | Cálculo y payload de ranking segmentados por categoría |
| `src/resultados/domain/aggregates/ranking_overall.py` | Overall segmentado por categoría |
| `src/resultados/application/commands/calcular_ranking.py` | Enrichment de categoría previo al cálculo |
| `src/resultados/application/queries/obtener_ranking.py` | DTO agrupado por categoría |
| `src/resultados/application/queries/obtener_overall.py` | DTO agrupado por categoría |
| `src/resultados/api/router.py` | Contrato HTTP `rankings: [{categoria, entradas}]` |
| `src/resultados/infrastructure/repositories/atleta_categoria_adapter.py` | Nuevo ACL a Registro |
| `src/app.py` | Inyección de `AtletaCategoriaAdapter` en P-08 |

### Tests
| Archivo | Cambio |
|---------|--------|
| `tests/unit/resultados/domain/test_ranking_competencia.py` | Cobertura explícita de segmentación por categoría |
| `tests/unit/resultados/domain/test_ranking_overall.py` | Cobertura explícita de segmentación overall por categoría |
| `tests/unit/resultados/api/test_router_ranking.py` | Nuevo test del contrato HTTP agrupado para ranking |
| `tests/unit/resultados/api/test_router_overall.py` | Contrato HTTP agrupado para overall |
| `tests/integration/resultados/test_calcular_ranking_integration.py` | Integración con `AtletaCategoriaAdapter` y SQLite de Registro |
| `tests/integration/resultados/test_obtener_overall_integration.py` | Lectura agrupada por categoría |

### Documentación
| Archivo | Cambio |
|---------|--------|
| `docs/plans/sp-adj-04/PLAN-SP-ADJ-04.md` | `US-ADJ-4.5` marcada como implementada |
| `docs/traceability/matrix.md` | `RF-PM-05` y `US-ADJ-4.5` pasan a implementados |
| `docs/design/domain-model.md` | `OverallTorneo` descrito por categoría/género |

---

## Resultados de calidad

| Gate | Resultado |
|------|-----------|
| Pytest focalizado Resultados + P-09 | ✅ 49/49 |
| Regresión BDD focalizada Resultados + P-09 | ✅ 21/21 |
| CodeGuard componentes impactados | ✅ 0 errores, 0 advertencias |

Comando de validación ejecutado:

```bash
./.venv/bin/pytest tests/unit/resultados tests/integration/resultados tests/unit/test_app_p09.py tests/integration/test_p09_callback_integration.py -q
./.venv/bin/pytest tests/features/steps/calcular_ranking_steps.py tests/features/steps/calcular_overall_steps.py tests/features/steps/api_overall_steps.py tests/features/steps/politica_p09_steps.py -q
./.venv/bin/codeguard src/resultados src/app.py
```

---

## Riesgos y notas

- El cálculo ahora depende de un ACL adicional a Registro; si un atleta no existe en
  esa fuente, el cálculo de ranking falla explícitamente.
- Se mantuvo compatibilidad mínima de lectura con payloads flat previos para no
  invalidar fixtures/eventos históricos durante la transición.
- `US-ADJ-4.6` sigue pendiente; el parsing `MM:SS` todavía no está encapsulado en un VO.
