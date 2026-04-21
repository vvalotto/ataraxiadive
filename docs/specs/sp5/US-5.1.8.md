# US-5.1.8: Componer disciplinas + competencias en "Ver competencias"

**Estado**: `To Do`
**Sprint**: SP5 — La Puesta en Marcha
**Incremento**: INC-5.1-ADJ
**Bounded Context**: `frontend` (consume `torneo/api/` + `competencia/api/`)
**Capas afectadas**: `frontend/src/pages/organizador/TorneoCompetenciasPage.tsx`

---

## Descripción

Como **organizador**,
quiero ver todas las disciplinas configuradas del torneo en la pantalla "Ver competencias"
para **no encontrarla vacía en fases tempranas cuando todavía no se han creado las competencias**.

---

## Contexto del dominio

### Modelo involucrado

| Elemento | Nombre | Responsabilidad |
|---|---|---|
| Page | `TorneoCompetenciasPage` | Muestra disciplinas del torneo con estado de competencia |
| Query | `GET /torneos/{torneo_id}/disciplinas` | Fuente primaria de disciplinas configuradas (`torneo.db`) |
| Query | `GET /competencia?torneo_id={id}` | Fuente secundaria de competencias materializadas (`competencia.db`) |
| Composición | disciplina + competencia opcional | Una card por disciplina; `competencia_id` puede no existir aún |

### Hallazgo UAT origen

- **UAT-5.1-01:** `TorneoCompetenciasPage` solo consulta competencias materializadas. En torneos en `INSCRIPCION_ABIERTA` o `PREPARACION`, la pantalla muestra "no tiene competencias configuradas" aunque el torneo sí tenga disciplinas.

### Causa raíz

`fetchCompetenciasPorTorneo(torneoId)` consulta `GET /competencia?torneo_id={id}`. Ese endpoint devuelve objetos `Competencia` ya creados en `competencia.db`, que solo existen a partir de que se genera la grilla. Para estados anteriores, la fuente correcta es `GET /torneos/{id}/disciplinas` (que existe y es consultada por `JuecesPanel`).

---

## Especificación del comportamiento

### Invariantes

- **INV-5.1.8-01:** La pantalla siempre muestra una card por disciplina configurada en el torneo, independientemente del estado del torneo.
- **INV-5.1.8-02:** "Ver auditoria" se habilita solo si existe `competencia_id` para esa disciplina.
- **INV-5.1.8-03:** Si una disciplina no tiene competencia, muestra estado `Competencia pendiente` con indicación de usar el tab `Grilla`.
- **INV-5.1.8-04:** El cruce entre disciplinas y competencias es por campo `disciplina` (código string).

### Operación principal

| | Descripción |
|---|---|
| **Precondición** | `torneoId` disponible en URL params |
| **Postcondición** | Se renderizan N cards, una por disciplina en `GET /torneos/{id}/disciplinas`; cada card muestra `competencia_id` si existe |

**Ejemplo concreto:**

```
Torneo T1 en INSCRIPCION_ABIERTA.
GET /torneos/T1/disciplinas → [{ disciplina: "DNF", juez_id: null }, { disciplina: "STA", juez_id: "J1" }]
GET /competencia?torneo_id=T1 → []

Resultado esperado:
  Card 1: DNF — "Competencia pendiente" — "Ver auditoria" deshabilitado
  Card 2: STA — "Competencia pendiente" — "Ver auditoria" deshabilitado
```

```
Torneo T1 en EJECUCION.
GET /torneos/T1/disciplinas → [{ disciplina: "DNF", juez_id: "J1" }, { disciplina: "STA", juez_id: "J2" }]
GET /competencia?torneo_id=T1 → [{ competencia_id: "C1", disciplina: "DNF", torneo_id: "T1" }]

Resultado esperado:
  Card 1: DNF — competencia_id=C1 — "Ver auditoria" habilitado (link a /organizador/competencias/C1/auditoria)
  Card 2: STA — "Competencia pendiente" — "Ver auditoria" deshabilitado
```

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-5.1.8 — Composición disciplinas + competencias en Ver competencias

  Background:
    Given el organizador "org@ataraxia.com" está autenticado con rol ORGANIZADOR

  Scenario: torneo en INSCRIPCION_ABIERTA muestra disciplinas aunque no haya competencias
    Given el torneo T1 está en INSCRIPCION_ABIERTA con disciplinas DNF y STA
    And no existen competencias en competencia.db para T1
    When el organizador navega a "Ver competencias" de T1
    Then se muestran dos cards: una para DNF y otra para STA
    And ambas cards muestran estado "Competencia pendiente"
    And el botón "Ver auditoria" está deshabilitado en ambas

  Scenario: torneo en EJECUCION muestra disciplinas con y sin competencia
    Given el torneo T1 está en EJECUCION con disciplinas DNF y STA
    And existe competencia C1 para disciplina DNF en T1
    And no existe competencia para disciplina STA en T1
    When el organizador navega a "Ver competencias" de T1
    Then la card de DNF muestra "Ver auditoria" habilitado con link a C1
    And la card de STA muestra estado "Competencia pendiente"

  Scenario: pantalla vacía reemplazada por disciplinas configuradas
    Given el torneo T1 en INSCRIPCION_ABIERTA tiene disciplina DNF
    When el organizador navega a "Ver competencias"
    Then no se muestra el mensaje "Este torneo no tiene competencias configuradas"
    And sí se muestra la card de DNF

  Scenario: error al cargar disciplinas muestra mensaje de error
    Given el endpoint GET /torneos/T1/disciplinas falla con 500
    When el organizador navega a "Ver competencias"
    Then se muestra un mensaje de error de carga
```

---

## Impacto arquitectónico

- [x] No — modificación exclusiva de lógica de presentación y composición en la page.

**Capa(s) afectadas:**
- [x] Frontend — `TorneoCompetenciasPage.tsx`: agregar query a `listarDisciplinasTorneo(torneoId)` y cruzar con competencias existentes
- [x] Frontend — `api/torneo.ts`: ya tiene `listarDisciplinasTorneo` — reutilizar

---

## Referencias

- Hallazgo UAT: `.work/revision-sp5/01-hallazgos-uat-inc-5.1.md` §UAT-5.1-01
- Plan: `docs/plans/inc-5.1-adj/PLAN-INC-5.1-ADJ.md §US-5.1.8`
- Código fuente: `frontend/src/pages/organizador/TorneoCompetenciasPage.tsx`
- Endpoint disciplinas: `src/torneo/api/router.py` — `GET /torneos/{id}/disciplinas`
- Endpoint ya usado por JuecesPanel: `frontend/src/components/organizador/JuecesPanel.tsx` línea 22

---

*Redactado: 2026-04-21 — INC-5.1-ADJ ajuste post-UAT panel organizador*