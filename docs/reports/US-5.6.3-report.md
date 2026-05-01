# Reporte de Implementación — US-5.6.3
# RankingCompetencia con puntaje FAAS por categoría

**Fecha:** 2026-04-26
**BC:** `resultados`
**Tiempo total:** ~103 min
**Estado:** ✅ Completa

---

## Resumen ejecutivo

US-5.6.3 extiende `RankingCompetencia` para calcular y almacenar puntos FAAS por atleta
(`puntos: Decimal`) y ordenar el ranking por puntos dentro de cada `Categoría`.

---

## Archivos modificados

| Archivo | Cambio |
|---------|--------|
| `domain/value_objects/entrada_ranking.py` | Campo `puntos: Decimal` con default `0.00` |
| `domain/aggregates/ranking_competencia.py` | Firma `calcular()` cambiada; dos paths (FAAS / legacy); serde actualizado |
| `application/commands/calcular_ranking.py` | Pasa `self._algoritmo` en lugar de `descriptor` |
| `application/queries/exportar_resultados.py` | Limpieza: elimina paso de `descriptor` a `calcular()` |
| `application/queries/obtener_ranking.py` | `RankingEntradaDTO` + `puntos: str` |
| `api/router.py` | Respuesta `GET /ranking` incluye `puntos` |

## Tests creados / actualizados

| Archivo | Tests nuevos | Tests actualizados |
|---------|:------------:|:------------------:|
| `test_ranking_competencia.py` | 9 (FAAS) | 0 (legacy sin cambios) |
| `test_calcular_ranking_integration.py` | 1 | 0 |
| `test_US_5_6_3_steps.py` | 4 (BDD) | — |
| `test_router_ranking.py` | 0 | 1 (agregado `"puntos"` al expected) |

**Total tests BC resultados:** 80 unit+integration · 4 BDD · todos verdes

---

## Invariantes verificados

| INV | Descripción | Test |
|-----|-------------|------|
| INV-5.6.3-01 | Posición por `puntos` desc | `test_calcular_con_faas_ordena_por_puntos_desc_dentro_de_categoria` |
| INV-5.6.3-02 | Empate por RP como desempate | `test_calcular_con_faas_empate_puntos_comparte_posicion` |
| INV-5.6.3-03 | DNS/Roja → `puntos=0`, `en_podio=False` | `test_calcular_con_faas_dns_puntos_cero_sin_podio` |
| INV-5.6.3-04 | 2 decimales | `test_calcular_con_faas_incluye_puntos_en_entradas` |
| INV-5.6.3-05 | Serde incluye `puntos`; fallback legacy `"0.00"` | `test_deserializacion_legacy_sin_puntos_usa_fallback_cero` |

---

## Decisión de diseño: compatibilidad legacy

`calcular(algoritmo: AlgoritmoPuntaje | None = None)` mantiene el path legacy
cuando `algoritmo=None`, preservando todos los tests existentes (ordenamiento por RP,
`puntos=0.00` en todas las entradas). El path FAAS activa cuando se inyecta
un algoritmo concreto. Esta separación garantiza cero regresiones en 16 tests legacy.

---

## Quality gates

| Gate | Resultado |
|------|-----------|
| Pylint | 9.65/10 (≥ 8.0) ✅ |
| Cobertura `domain/` + `application/` | 96% (≥ 90%) ✅ |
| DesignReviewer (pre-push) | Ver PR |
| Black | ✅ |
