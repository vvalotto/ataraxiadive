# US-5.7.1: Mis torneos inscriptos con estado actual

**Estado**: `To Do`
**Sprint**: SP5 — La Puesta en Marcha
**Incremento**: INC-5.7
**Bounded Context**: `frontend`
**Capas afectadas**: `frontend/src/pages/atleta/AtletaTorneosPage.tsx`

---

## Descripcion

Como **atleta**,
quiero **ver en la sección Torneos una lista diferenciada de los torneos en los que ya estoy inscripto, con su estado actual**,
para **distinguir de un vistazo los torneos en ejecución o finalizados de los que aún están abiertos para inscripción**.

---

## Fuente de verdad UX

- `docs/design/ux/wireframes-atleta.md §S-02 Torneos Disponibles`
- `docs/design/ux/flujos-por-rol.md §3 Rol: Atleta`

---

## Contexto de diseño

`AtletaTorneosPage` ya existe y muestra dos secciones: "Inscripciones abiertas" (donde el atleta NO está inscripto) y "Próximos". No hay sección para torneos donde el atleta **sí** está inscripto.

Esta US agrega una tercera sección "Mis torneos" que muestra los torneos donde el atleta tiene inscripción confirmada, con su estado actual. Los datos ya están disponibles: `listarInscripcionesDeAtleta` + `fetchTorneos`.

---

## Alcance funcional

### Sección "Mis torneos"

Nueva sección al inicio de `AtletaTorneosPage`, antes de "Inscripciones abiertas":

- **Posición:** primera sección de la página
- **Título de sección:** "Mis torneos"
- **Contenido por card:**
  - nombre del torneo
  - fecha inicio · sede y ciudad
  - badge de estado del torneo (`EN_EJECUCION`, `FINALIZADO`, `INSCRIPCION_CERRADA`)
  - chips de disciplinas inscriptas
- **Acción:** tap → `/atleta/torneos/:torneoId` (ya existente)
- **Estado vacío:** "Aún no estás inscripto en ningún torneo."

### Ajuste de sección "Inscripciones abiertas"

Excluye torneos donde el atleta ya está inscripto (comportamiento ya parcialmente implementado, consolidar).

---

## Invariantes

- **INV-5.7.1-01:** La sección "Mis torneos" solo muestra torneos con inscripción activa del atleta; no incluye torneos disponibles para inscribirse.
- **INV-5.7.1-02:** La sección "Inscripciones abiertas" no incluye torneos donde el atleta ya está inscripto.
- **INV-5.7.1-03:** No se requieren nuevos endpoints backend — los datos se derivan de `listarInscripcionesDeAtleta` + `fetchTorneos`.

---

## Especificacion del comportamiento

### Flujo de datos

```text
loadTorneos()
  → GET /registro/atletas/me                     (atleta_id)
  → GET /registro/atletas/{atleta_id}/inscripciones  (set de torneo_id inscriptos)
  → GET /torneos                                 (todos los torneos)
  → separar en:
      misInscriptos = torneos donde torneo_id ∈ inscripciones
      abiertosSinInscripcion = torneos INSCRIPCION_ABIERTA donde torneo_id ∉ inscripciones
      proximos = torneos EN_PREPARACION o PUBLICADO
```

### Orden de secciones en pantalla

1. **Mis torneos** (inscriptos) — ordenados por fecha_inicio ascendente
2. **Inscripciones abiertas** (no inscripto) — ordenados por fecha_inicio ascendente
3. **Próximos** — sin cambios

---

## Criterios de aceptacion (BDD)

```gherkin
Feature: US-5.7.1 — Mis torneos inscriptos en la página Torneos

  Background:
    Given el atleta "ana@email.com" está autenticado con rol ATLETA
    And existe el torneo "BA Open 2026" en estado "EN_EJECUCION"
    And Ana está inscripta en "BA Open 2026" con disciplinas DNF y STA
    And existe el torneo "Open Litoral 2026" en estado "INSCRIPCION_ABIERTA" sin inscripción de Ana

  Scenario: atleta ve sus torneos inscriptos en la primera sección
    When Ana navega a la tab "Torneos"
    Then ve la sección "Mis torneos" primero
    And "BA Open 2026" aparece en "Mis torneos" con badge "EN EJECUCIÓN"
    And "BA Open 2026" muestra chips "DNF" y "STA"

  Scenario: torneo inscripto no aparece en inscripciones abiertas
    When Ana navega a la tab "Torneos"
    Then "BA Open 2026" no aparece en la sección "Inscripciones abiertas"
    And "Open Litoral 2026" sí aparece en "Inscripciones abiertas"

  Scenario: estado vacío cuando el atleta no tiene inscripciones
    Given el atleta no está inscripto en ningún torneo
    When navega a la tab "Torneos"
    Then ve el mensaje "Aún no estás inscripto en ningún torneo." en la sección "Mis torneos"
```

---

## Impacto arquitectonico

- [x] Frontend únicamente — `AtletaTorneosPage.tsx` y la función `loadTorneos` interna.
- [ ] Sin cambios de backend.

### Componentes afectados

```
frontend/src/pages/atleta/
└── AtletaTorneosPage.tsx   ← agregar sección "Mis torneos" + ajustar filtros
```

---

## Referencias

- `frontend/src/pages/atleta/AtletaTorneosPage.tsx` — implementación actual
- `frontend/src/api/registro.ts` — `listarInscripcionesDeAtleta`
- `frontend/src/api/torneo.ts` — `fetchTorneos`, `listarDisciplinasTorneo`
- `docs/design/ux/wireframes-atleta.md §S-02`

---

*Redactado: 2026-04-30 — INC-5.7*
