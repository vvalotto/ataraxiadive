---
title: "RNF-05 — Seguridad: auditoría inalterable de resultados"
type: trazabilidad-rnf
rnf_id: RNF-05
atributo: Seguridad
last_updated: "2026-05-31"
adr_refs:
  - ADR-018-hash-sha256-auditoria
  - ADR-019-politica-contrasenas
  - ADR-020-modelo-usuarios-roles
bcs_afectados:
  - competencia
  - identidad
---

# RNF-05 — Seguridad

**Driver:** la integridad de los resultados es la credibilidad del torneo.

| Atributo | Valor |
|---|---|
| Log de auditoría de acciones del juez | Requerido e inalterable |
| Protección contra manipulación de resultados | Requerida |
| Juez en disciplina no asignada | Solo lectura |

## Decisiones arquitectónicas derivadas

- [[decisiones/ADR-018-hash-sha256-auditoria]] — hash SHA-256 sobre secuencia de eventos al cerrar disciplina
- [[decisiones/ADR-019-politica-contrasenas]] — política de contraseñas: mínimo 10 chars + mayúscula + número
- [[decisiones/ADR-020-modelo-usuarios-roles]] — roles por disciplina; guards en cada endpoint

## Relación con el dominio

→ [[conceptos/atributos-calidad]]
