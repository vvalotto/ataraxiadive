---
title: "Vista de Dominio"
type: vista
last_updated: "2026-05-20"
sources:
  - docs/dominio/01-dominio_torneos_apnea.md
  - docs/architecture/03-bounded-contexts.md
  - docs/dominio/05-requerimientos_funcionales.md
---

# Vista de Dominio

> El sistema visto desde el negocio y el lenguaje ubicuo.

## Propósito

Responder preguntas sobre qué hace el sistema, qué conceptos maneja, quiénes
son los actores y cómo se relacionan. Es la vista de entrada para onboarding,
para el domain expert y para quien necesita entender el sistema antes de tocarlo.

## Stakeholder principal

Domain expert, nuevo integrante del equipo, product owner.

## Preguntas características

1. ¿Qué hace AtaraxiaDive? ¿Cuál es su propósito?
2. ¿Qué significa Performance en el contexto del sistema?
3. ¿Qué diferencia hay entre Torneo y Competencia como conceptos?
4. ¿Qué es una Grilla y cómo se relaciona con una Disciplina?
5. ¿Quiénes son los actores (Organizador, Juez, Atleta) y qué puede hacer cada uno?
6. ¿Qué reglas del deporte de apnea son relevantes para el sistema?
7. ¿Qué es una tarjeta y qué consecuencias tiene en una performance?

## Bounded Contexts como unidades de negocio

| BC | Rol | Responsabilidad principal |
|----|-----|--------------------------|
| [[competencia]] | Core Domain | Registro de performances, tarjetas, grilla |
| [[torneo]] | Supporting | Ciclo de vida del torneo, disciplinas, sede |
| [[registro]] | Supporting | Atletas, inscripciones, anuncios de performance |
| [[resultados]] | Supporting | Rankings, publicación de resultados |
| [[identidad]] | Generic | Usuarios, roles, autenticación |
| [[notificaciones]] | Generic | Envío de notificaciones, idempotencia |

## Recorridos sugeridos

**Para entender el corazón del sistema:**
`[[competencia]]` → `[[conceptos/performance]]` → `[[conceptos/tarjeta]]`
→ `[[conceptos/grilla]]` → `[[ADR-001-event-sourcing]]`

**Para entender el ciclo de vida completo:**
`[[torneo]]` → `[[registro]]` → `[[competencia]]` → `[[resultados]]`

**Para entender los actores:**
`[[identidad]]` → `[[conceptos/organizador]]` → `[[conceptos/juez]]`
→ `[[conceptos/atleta]]`

## Páginas hub de esta vista

- [[competencia]] — nodo central del core domain
- [[conceptos/performance]] — concepto más rico del dominio
- [[conceptos/grilla]] — estructura de la competencia
- [[torneo]] — punto de entrada al ciclo de vida

---
*Vista pendiente de poblarse — requiere Fase 1 (ingest fundacional)*
