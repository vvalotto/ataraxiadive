# Reporte de Implementación — US-5.6.4

**Historia**: RankingOverall por categoría con puntos acumulados
**Sprint**: SP5 — La Puesta en Marcha | **Incremento**: INC-5.6
**Branch**: feature/US-5.6.4-ranking-overall-puntos
**Fecha**: 2026-04-27

---

## Resumen de Cambios

### Domain
- `entrada_overall.py`: `puntaje: int` + `detalle: dict[str, int]` → `puntos_overall: Decimal` + `detalle: dict[str, Decimal]`
- `exceptions.py`: nueva `DisciplinasNoFinalizadas` (INV-5.6.4-04)
- `ranking_overall.py`: algoritmo reescrito — suma `EntradaRanking.puntos` FAAS DESC en lugar de posiciones; validación INV-5.6.4-04; backward compat para eventos legacy

### Application
- `calcular_overall.py`: incluye todas las disciplinas en el mapa (incluso vacías) para que el aggregate valide INV-5.6.4-04
- `obtener_overall.py`: DTO `puntos_overall: Decimal` + `detalle: dict[str, Decimal]`
- `exportar_resultados.py`: `puntos_totales` actualizado a `Decimal`

### API
- `router.py`: `GET /{torneo_id}/overall` retorna `puntos_overall` (str) + `detalle` con valores str

## Métricas

| Fase | Artefacto | Resultado |
|------|-----------|-----------|
| BDD | 5 escenarios | 5/5 PASS |
| Unit | `test_ranking_overall.py` | 11 tests nuevos |
| Unit | `test_calcular_overall_handler.py` | 2 tests (1 nuevo INV-5.6.4-04) |
| Unit | `test_obtener_overall_handler.py` | 3 tests actualizados |
| Unit | `test_router_overall.py` | 2 tests actualizados |
| Integration | `test_calcular_overall_integration.py` | 2 tests (1 nuevo INV-5.6.4-04) |
| Integration | `test_obtener_overall_integration.py` | 1 test actualizado |
| **Total** | | **91 tests resultados — 91/91 PASS** |
| CodeGuard | src/resultados/ | 0 errores |

## Decisiones Técnicas

1. **Eliminación de `penalizacion_ausente`**: ya no aplica — ausente en FAAS = 0 puntos
2. **INV-5.6.4-04 en el domain**: la validación vive en `RankingOverall.calcular()`, no en el handler
3. **Backward compat**: `_dict_a_entrada` usa fallback `"0.00"` para eventos sin `puntos_overall`
4. **Serialización Decimal**: `puntos_overall` y `detalle` serializados como strings en JSON

## Invariantes Verificados

- INV-5.6.4-01: ✅ `puntos_overall = Σ puntos_disciplina` (ausente = 0)
- INV-5.6.4-02: ✅ Posición determinada por `puntos_overall` DESC
- INV-5.6.4-03: ✅ Empate comparte posición
- INV-5.6.4-04: ✅ `DisciplinasNoFinalizadas` si alguna disciplina sin ranking
- INV-5.6.4-05: ✅ Precisión 2 decimales (`quantize(Decimal("0.01"))`)
