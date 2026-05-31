---
title: "RNF-04 — Configurabilidad: reglas de negocio como datos"
type: trazabilidad-rnf
rnf_id: RNF-04
atributo: Configurabilidad
last_updated: "2026-05-31"
adr_refs:
  - ADR-004-reglas-como-datos
bcs_afectados:
  - competencia
  - torneo
---

# RNF-04 — Configurabilidad

**Driver:** las reglas del dominio cambian con los reglamentos federativos. El sistema debe absorberlos sin cambios de código.

| Atributo | Quién configura | Alcance |
|---|---|---|
| Disciplinas | Administrador | Global |
| Categorías | Administrador | Global |
| Fórmula de puntos (FAAS) | Configurable | Por torneo |

## Decisiones arquitectónicas derivadas

- [[decisiones/ADR-004-reglas-como-datos]] — `discipline_config` y `category_config` en `torneo.db`; reglas no hardcodeadas

## Relación con el dominio

→ [[conceptos/atributos-calidad]]
