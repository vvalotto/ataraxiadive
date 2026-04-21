c# US-5.1.9: Precondición de grilla en asignación de jueces

**Estado**: `To Do`
**Sprint**: SP5 — La Puesta en Marcha
**Incremento**: INC-5.1-ADJ
**Bounded Context**: `frontend`
**Capas afectadas**: `frontend/src/components/organizador/JuecesPanel.tsx`, `frontend/src/components/organizador/TablaJueces.tsx`

---

## Descripción

Como **organizador**,
quiero que el selector de juez esté bloqueado para disciplinas sin grilla generada
para **evitar asignar jueces antes de que exista una programación oficial de performances**.

---

## Contexto del dominio

### Modelo involucrado

| Elemento | Nombre | Responsabilidad |
|---|---|---|
| Componente | `JuecesPanel` | Muestra disciplinas del torneo con selector de juez por fila |
| Componente | `TablaJueces` | Tabla con fila por disciplina y `JuezSelector` |
| Query | `GET /competencia?torneo_id={id}` | Lista competencias del torneo con su estado |
| Regla | precondición grilla | Selector habilitado solo si disciplina tiene competencia con grilla generada |

### Hallazgo UAT origen

- **UAT-5.1-02:** `JuecesPanel` muestra el selector habilitado para todas las disciplinas sin verificar si tienen grilla generada. La regla operativa es: juez asignable solo si la disciplina tiene grilla OT confirmada.

### Regla de dominio a aplicar

```
disciplina asignable a juez ⇔ disciplina tiene Competencia en estado con grilla generada
```

Los estados de `Competencia` que indican grilla generada son: `GrillaGenerada`, `GrillaConfirmada`, `EnEjecucion`, `Finalizada`.

---

## Especificación del comportamiento

### Invariantes

- **INV-5.1.9-01:** El `JuezSelector` de una disciplina está habilitado solo si existe una competencia para esa disciplina con estado `GrillaGenerada`, `GrillaConfirmada`, `EnEjecucion` o `Finalizada`.
- **INV-5.1.9-02:** Si la disciplina no tiene competencia (grilla no generada), la fila muestra estado `Generar grilla antes de asignar juez` y el selector está deshabilitado.
- **INV-5.1.9-03:** Una asignación existente es visible aunque la disciplina no tenga grilla, pero el selector permanece bloqueado para evitar cambios.
- **INV-5.1.9-04:** La restricción es exclusivamente de UI; no se requiere cambio en el backend para esta US.

### Operación de verificación

| | Descripción |
|---|---|
| **Precondición** | `JuecesPanel` montado con `torneoId` disponible |
| **Postcondición** | Para cada disciplina, `JuezSelector` habilitado ⇔ `competencias[disciplina].estado ∈ {GrillaGenerada, GrillaConfirmada, EnEjecucion, Finalizada}` |

**Ejemplo concreto:**

```
Torneo T1 en PREPARACION. Disciplinas: DNF, STA.
GET /competencia?torneo_id=T1 → [{ disciplina: "DNF", estado: "GrillaGenerada" }]
                                 (STA no tiene competencia)

Resultado esperado en JuecesPanel:
  Fila DNF: JuezSelector habilitado
  Fila STA: selector deshabilitado + mensaje "Generar grilla antes de asignar juez"
```

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-5.1.9 — Precondición de grilla en asignación de jueces

  Background:
    Given el organizador "org@ataraxia.com" está autenticado con rol ORGANIZADOR
    And el torneo T1 está en estado PREPARACION con disciplinas DNF y STA

  Scenario: disciplina con grilla generada tiene selector habilitado
    Given existe competencia C1 para disciplina DNF en estado GrillaGenerada
    When el organizador accede al tab Jueces
    Then la fila de DNF muestra el JuezSelector habilitado

  Scenario: disciplina sin competencia tiene selector bloqueado
    Given no existe competencia para disciplina STA en T1
    When el organizador accede al tab Jueces
    Then la fila de STA muestra el selector deshabilitado
    And la fila muestra el mensaje "Generar grilla antes de asignar juez"

  Scenario: asignación existente visible aunque grilla no esté generada
    Given existe una asignación de juez para STA en torneo.db
    And no existe competencia para STA en competencia.db
    When el organizador accede al tab Jueces
    Then la fila de STA muestra el juez asignado como texto
    And el selector de STA permanece deshabilitado

  Scenario: asignar juez a disciplina con grilla funciona normalmente
    Given existe competencia C1 para DNF en estado GrillaConfirmada
    And no hay juez asignado a DNF
    When el organizador selecciona un juez en la fila de DNF
    Then el backend recibe PUT /torneos/T1/disciplinas/DNF/juez
    And la fila actualiza con el juez asignado
```

---

## Impacto arquitectónico

- [x] No — modificación exclusiva de lógica de UI; no requiere cambios en backend.

**Capa(s) afectadas:**
- [x] Frontend — `JuecesPanel.tsx`: agregar query a `fetchCompetenciasPorTorneo(torneoId)` para cruzar estado por disciplina
- [x] Frontend — `TablaJueces.tsx`: recibir prop `competenciasPorDisciplina` y propagar a cada fila si el selector debe estar habilitado
- [x] Frontend — `api/competencia.ts`: `fetchCompetenciasPorTorneo` ya existe — reutilizar

---

## Referencias

- Hallazgo UAT: `.work/revision-sp5/01-hallazgos-uat-inc-5.1.md` §UAT-5.1-02
- Plan: `docs/plans/inc-5.1-adj/PLAN-INC-5.1-ADJ.md §US-5.1.9`
- Código fuente: `frontend/src/components/organizador/JuecesPanel.tsx` línea 20
- Código fuente: `frontend/src/api/competencia.ts` — `fetchCompetenciasPorTorneo`

---

*Redactado: 2026-04-21 — INC-5.1-ADJ ajuste post-UAT panel organizador*