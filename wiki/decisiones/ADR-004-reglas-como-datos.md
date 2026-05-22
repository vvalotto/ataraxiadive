---
title: "ADR-004: Reglas de competencia como datos configurables"
type: decision
last_updated: "2026-05-20"
sources:
  - docs/adr/ADR-004-reglas-como-datos.md
estado: Aceptada
fecha: 2026-03-14
bcs_afectados: [torneo, competencia]
---

# ADR-004: Reglas de competencia como datos configurables

## Decisión

Disciplinas, categorías y reglas de tarjetas se almacenan en la base de datos y son configurables desde el panel sin intervención técnica.

## Por qué

- Las reglas del reglamento de apnea cambian ~cada 2 años. Hardcodearlas requiere ciclos de deploy.
- AC-CF-01: el administrador debe poder agregar disciplinas sin reiniciar el sistema.
- AC-CF-02: las penalizaciones deben ser configurables.

## Consecuencias vigentes

| Tabla | BC propietario | SQLite |
|-------|---------------|--------|
| `discipline_config` | [[bc-torneo]] | `torneo.db` |
| `category_config` | [[bc-torneo]] | `torneo.db` |
| `card_rule_config` | [[competencia]] | `competencia.db` |

- Las **invariantes de dominio** (ej: "una performance cerrada no puede modificarse") siguen en el código — son modelo, no configuración.
- El campo `rules` en `discipline_config` almacena JSON como `TEXT` en SQLite — la validación es responsabilidad de la capa de aplicación.
- Los torneos pasados conservan la configuración con la que se ejecutaron (snapshot al crear el torneo).
- Riesgo: una configuración inválida puede romper una competencia en producción — mitigado con validación estricta al guardar.

## ADRs relacionados

- [[ADR-005-bounded-contexts-ddd-estrategico]] — define qué BC es propietario de cada tabla de configuración
- [[ADR-007-sqlite-persistencia-bc]] — cada tabla vive en el `.db` de su BC
