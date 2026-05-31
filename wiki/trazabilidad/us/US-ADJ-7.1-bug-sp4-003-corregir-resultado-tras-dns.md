---
title: "US-ADJ-7.1 — BUG-SP4-003: CorregirResultadoTrasDNS"
type: trazabilidad-us
sp: SP-ADJ-07
inc: SP-ADJ-07
bc: competencia
estado: cerrada
fecha_cierre: "2026-04-19"
last_updated: "2026-05-21"
sources:
  - docs/plans/sp-adj-07/PLAN-SP-ADJ-07.md
  - docs/plans/sp-adj-07/US-ADJ-7.1-plan.md
  - commit e1ac34b, PR #93
us_id: US-ADJ-7.1
tests_count: null
rf: []
software_items:
  - src/competencia/application/commands/corregir_resultado_tras_dns.py
test_units:
  - tests/integration/competencia/test_corregir_resultado_tras_dns_integration.py
origen_tipo: calidad
---

# US-ADJ-7.1 — BUG-SP4-003: CorregirResultadoTrasDNS

## Descripción

Corrige un bug de dominio: un DNS registrado por error era irreversible porque `CorregirResultado` solo operaba sobre performances en estado `Ejecutada`. Introduce un nuevo comando que permite salir del estado `DNS`.

## Bug resuelto

**BUG-SP4-003** — No existe forma de corregir un DNS registrado por error. Afecta la integridad del flujo del juez.

## Contenido implementado

- Nuevo comando `CorregirResultadoTrasDNS` — transiciona `DNS → ResultadoRegistrado`
- Evento `ResultadoCorregidoTrasDNS` con campo `motivo_correccion` obligatorio
- Una vez en `ResultadoRegistrado`, el flujo normal (`AsignarTarjeta`) continúa sin cambios

## Capas afectadas

`competencia/domain/`, `competencia/application/commands/`, `competencia/api/`

## Estado

✅ Completado — 2026-04-19 (commit `e1ac34b`, PR #93)
