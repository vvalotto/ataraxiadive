# Plan de Implementación — US-5.6.3
# RankingCompetencia con puntaje FAAS por categoría

**BC:** `resultados`
**Estimación:** 5 puntos
**Fecha:** 2026-04-26

---

## Componentes a modificar (en orden de dependencia)

### 1. Value Object — `EntradaRanking`
**Archivo:** `src/resultados/domain/value_objects/entrada_ranking.py`
- Agregar campo `puntos: Decimal` con default `Decimal("0.00")` (INV-5.6.3-04)
- El campo tiene default para no romper construcciones legacy

### 2. Aggregate — `RankingCompetencia`
**Archivo:** `src/resultados/domain/aggregates/ranking_competencia.py`

**Cambio de firma de `calcular()`:**
```python
# ANTES
def calcular(self, resultados, descriptor: DisciplinaDescriptor) -> None:
# DESPUÉS
def calcular(self, resultados, algoritmo: AlgoritmoPuntaje | None = None) -> None:
```

**Nueva lógica `_calcular_entries`:**
- Cuando `algoritmo is None` → path legacy (sort by RP, puntos=0.00)
- Cuando `algoritmo` provisto → computar `puntos_map = algoritmo.calcular(resultados, disciplina)`, sort by puntos desc dentro de cada categoría, tie-break por RP (INV-5.6.3-02)

**Serialización/deserialización:**
- `_entrada_a_dict`: agregar `"puntos": str(e.puntos)`
- `_dict_a_entrada`: leer `d.get("puntos", "0.00")` con fallback (INV-5.6.3-05)

### 3. Command Handler — `CalcularRankingHandler`
**Archivo:** `src/resultados/application/commands/calcular_ranking.py`
- Eliminar `descriptor = self._descriptor.describe(command.disciplina)`
- Cambiar `ranking.calcular(resultados, descriptor)` → `ranking.calcular(resultados, self._algoritmo)`
- Mantener `descriptor` en `__init__` por compat con tests de integración legacy

### 4. Query Handler — `ObtenerRankingHandler` + DTO
**Archivo:** `src/resultados/application/queries/obtener_ranking.py`
- Agregar `puntos: str` a `RankingEntradaDTO`
- Mapear `puntos=str(entry.puntos)` en `handle()`

### 5. API Router
**Archivo:** `src/resultados/api/router.py`
- Agregar `"puntos": e.puntos` al dict de cada entrada en `get_ranking()`

---

## Tests a crear

### Unitarios (nuevos) — `tests/unit/resultados/domain/test_ranking_competencia.py`
- `test_calcular_con_faas_incluye_puntos_en_entradas`
- `test_calcular_con_faas_ordena_por_puntos_desc`
- `test_calcular_dns_puntos_cero_con_algoritmo`
- `test_calcular_sin_algoritmo_mantiene_behavior_legacy`
- `test_reconstitute_incluye_puntos_del_evento`
- `test_serialización_incluye_puntos`
- `test_deserializacion_legacy_puntos_fallback_cero`

### Integración (nuevos) — `tests/integration/resultados/test_calcular_ranking_integration.py`
- `test_calcular_ranking_con_algoritmo_faas_incluye_puntos`

### BDD — `tests/features/steps/`
- Implementar step definitions para `US-5.6.3-ranking-puntos-faas.feature`

---

## Invariantes a respetar
- INV-5.6.3-01: posición por `puntos` desc (cuando algoritmo provisto)
- INV-5.6.3-02: empate por RP como desempate secundario
- INV-5.6.3-03: DNS/Roja → `puntos=0`, al final, `en_podio=False`
- INV-5.6.3-04: `puntos` con 2 decimales
- INV-5.6.3-05: serialización incluye `puntos`; fallback `"0.00"` en reconstitución legacy

---

## Estrategia de compatibilidad
Todos los tests existentes que llaman `ranking.calcular(resultados, None)` seguirán funcionando
porque el path legacy (algoritmo=None) preserva el ordenamiento por RP.
Los tests de integración que instancian `CalcularRankingHandler` sin `algoritmo=` tampoco se rompen.
