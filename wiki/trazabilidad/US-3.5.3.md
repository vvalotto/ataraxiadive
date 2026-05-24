---
title: "US-3.5.3 — API GET /resultados/{torneo_id}/overall"
type: trazabilidad-us
sp: SP3
inc: INC-3.5
bc: resultados
estado: cerrada
fecha_cierre: "2026-04-02"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §9
us_id: US-3.5.3
tests_count: null
rf:
  - RF-PM-06
software_items:
  - src/resultados/application/queries/obtener_overall.py
  - src/resultados/api/router.py
test_units:
  - tests/features/US-3.5.3-api-overall.feature
  - tests/integration/resultados/test_obtener_overall_integration.py
origen_tipo: rf
---

# US-3.5.3 — API GET /resultados/{torneo_id}/overall

## Descripción

Expone el ranking overall del torneo vía endpoint REST, permitiendo consultar el ranking general calculado por [[US-3.5.1]] y disparado por [[US-3.5.2]].

## RFs cubiertos

| RF | Descripción |
|----|-------------|
| RF-PM-06 | Publicación en plataforma + descarga |

## Contenido implementado

- `GET /resultados/{torneo_id}/overall` — devuelve ranking global por categoría/género
- Acceso restringido: solo disponible cuando el torneo está en estado `CERRADO` o `PREMIACION`
- Respuesta incluye posición, atleta, club, categoría, puntos totales

## Tests

| Suite | Resultado |
|-------|-----------|
| unit/resultados/application | ✅ |
| unit/resultados/api | ✅ |
| integration/resultados | ✅ |
| features/US-3.5.3-api-overall | ✅ |
| **Total** | **10 tests focalizados** |

## Estado

✅ Completado — 2026-04-02
