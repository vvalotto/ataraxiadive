---
title: "RNF-02 — Disponibilidad: operación sin conectividad"
type: trazabilidad-rnf
rnf_id: RNF-02
atributo: Disponibilidad
last_updated: "2026-05-31"
adr_refs:
  - ADR-003-offline-first-pwa
  - ADR-015-dexie-indexeddb-frontend
bcs_afectados:
  - todos
---

# RNF-02 — Disponibilidad

**Driver:** la competencia no se detiene por el sistema. El juez debe poder operar sin internet.

| Atributo | Valor |
|---|---|
| Conectividad en competencias | Frecuentemente precaria (piletas, lagos, mar) |
| Modo offline para el juez | Requerido |
| Plan B manual | Registro en papel como contingencia |

## Decisiones arquitectónicas derivadas

- [[decisiones/ADR-003-offline-first-pwa]] — arquitectura PWA offline-first con sincronización posterior
- [[decisiones/ADR-015-dexie-indexeddb-frontend]] — Dexie/IndexedDB como caché local del cliente

## Relación con el dominio

→ [[conceptos/atributos-calidad]]
