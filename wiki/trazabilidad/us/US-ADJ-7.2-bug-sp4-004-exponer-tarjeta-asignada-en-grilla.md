---
title: "US-ADJ-7.2 — BUG-SP4-004: exponer tarjeta_asignada en /grilla"
type: trazabilidad-us
sp: SP-ADJ-07
inc: SP-ADJ-07
bc: competencia, frontend
estado: cerrada
fecha_cierre: "2026-04-19"
last_updated: "2026-05-21"
sources:
  - docs/plans/sp-adj-07/PLAN-SP-ADJ-07.md
  - docs/plans/sp-adj-07/US-ADJ-7.2-plan.md
  - commit 4007259, PR #92
us_id: US-ADJ-7.2
tests_count: null
rf: []
software_items:
  - src/competencia/api/router.py
test_units:
  - tests/integration/competencia/test_grilla_tarjeta_asignada_api.py
origen_tipo: calidad
componentes_wiki:
  - arquitectura/competencia/router-competencia
---

# US-ADJ-7.2 — BUG-SP4-004: exponer tarjeta_asignada en /grilla

## Descripción

Corrige que el endpoint de grilla no exponía el tipo de tarjeta asignada a cada atleta, impidiendo que la UI de auditoría mostrara los colores correctos por resultado.

## Bug resuelto

**BUG-SP4-004** — `/grilla` no incluye `tarjeta_asignada` — pantalla de auditoría sin colores diferenciados por tipo de tarjeta.

## Contenido implementado

**Backend:**
- `EntradaGrillaDTO` — campo `tarjeta_asignada: str | None` agregado
- `_PerformanceProjection` — extrae `performance.tarjeta.value if performance.tarjeta else None`

**Frontend:**
- `AuditoriaPage` — estilos condicionales por tipo de tarjeta (blanca / con penalizaciones / amarilla / roja)

## Estado

✅ Completado — 2026-04-19 (commit `4007259`, PR #92)
