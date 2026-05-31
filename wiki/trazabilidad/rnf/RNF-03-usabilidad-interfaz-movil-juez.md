---
title: "RNF-03 — Usabilidad: interfaz móvil para el juez"
type: trazabilidad-rnf
rnf_id: RNF-03
atributo: Usabilidad
last_updated: "2026-05-31"
adr_refs:
  - ADR-003-offline-first-pwa
  - ADR-015-dexie-indexeddb-frontend
bcs_afectados:
  - todos
---

# RNF-03 — Usabilidad

**Driver:** cada segundo de fricción con la interfaz es riesgo para la integridad de los datos.

| Atributo | Valor |
|---|---|
| Dispositivo principal del juez | Celular (puede ser tablet) |
| Máximo de acciones para flujo completo | 6 acciones |
| Condiciones adversas | Sol directo, manos mojadas, guantes |
| Idioma | Español |

## Decisiones arquitectónicas derivadas

- [[decisiones/ADR-003-offline-first-pwa]] — PWA optimizada para celular
- [[decisiones/ADR-015-dexie-indexeddb-frontend]] — caché local para respuesta inmediata sin round-trip

## Relación con el dominio

→ [[conceptos/atributos-calidad]]
