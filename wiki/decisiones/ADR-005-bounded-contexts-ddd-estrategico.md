---
title: "ADR-005: Diseño Estratégico DDD — 6 Bounded Contexts"
type: decision
last_updated: "2026-05-20"
sources:
  - docs/adr/ADR-005-bounded-contexts-ddd-estrategico.md
estado: Aceptada
fecha: 2026-03-18
bcs_afectados: [todos]
---

# ADR-005: Diseño Estratégico DDD — 6 Bounded Contexts

## Decisión

6 Bounded Contexts definitivos: 4 de dominio + 2 genéricos. El BC `Configuración` fue eliminado.

## Mapa de BCs

| BC | Tipo | Persistencia | Rol |
|----|------|:-----------:|-----|
| [[competencia]] | Core Domain | Event Sourcing | Lógica no trivial; auditoría regulatoria |
| [[torneo]] | Supporting | CRUD | Ciclo de vida del torneo; catálogos de disciplinas/categorías |
| [[registro]] | Supporting | CRUD | Datos de atletas; inscripciones; anuncios |
| [[resultados]] | Supporting | CRUD + proyecciones | Cálculo derivado de eventos de Competencia |
| [[identidad]] | Generic | CRUD | Cross-cutting de autenticación y roles |
| [[notificaciones]] | Generic | Event Sourcing | Exactly-once delivery (ver [[ADR-017-notificaciones-event-sourcing]]) |

## Por qué 6 BCs y no 7

El BC `Configuración` fue eliminado porque no emergió como frontera natural en el Event Storming Big Picture: ningún evento del dominio le pertenecía exclusivamente. Sus conceptos fueron absorbidos:
- Disciplinas y categorías → **Torneo**
- Reglas de tarjetas → **Competencia**

> Dato experimental: el Event Storming produjo un modelo más simple que el análisis estático de RFs. La compresión de 7 a 6 BCs emergió del comportamiento del dominio.

## Consecuencias vigentes

- Cada BC tiene su propio archivo SQLite (`<bc>.db`) — ver [[ADR-007-sqlite-persistencia-bc]].
- La comunicación entre BCs es **solo por puertos** — nunca imports directos entre BCs.
- Los ACLs viven en `infrastructure/` del BC consumidor.
- `Identidad` es candidato a reemplazar con solución SaaS en el futuro.
- `Notificaciones` tiene trade-off de lock-in con ES documentado en [[ADR-017-notificaciones-event-sourcing]].

## ADRs relacionados

- [[ADR-001-event-sourcing-competencia]] — ES en el Core Domain
- [[ADR-006-estructura-bc-first]] — organización del código por BC
- [[ADR-017-notificaciones-event-sourcing]] — justificación de ES en Notificaciones
