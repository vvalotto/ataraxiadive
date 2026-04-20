# US-5.1.5: Asignación de jueces a disciplinas desde la UI

**Estado**: `To Do`
**Sprint**: SP5 — La Puesta en Marcha
**Incremento**: INC-5.1
**Bounded Context**: `frontend` (consume `torneo/api/` + `identidad/api/` — endpoints existentes)
**Capas afectadas**: `frontend/src/pages/organizador/`, `frontend/src/api/torneo.ts`, `frontend/src/api/identidad.ts`

---

## Descripción

Como **organizador**,
quiero **asignar un juez a cada disciplina del torneo desde la UI**
para **que cada juez solo vea y opere las disciplinas que le corresponden al iniciar la ejecución**.

---

## Contexto del dominio

### Modelo involucrado

| Elemento | Nombre | Responsabilidad |
|---|---|---|
| Aggregate | `Torneo` | `DisciplinaTorneo` tiene `juez_id` opcional |
| Command | `AsignarJuezCommand` | Asigna `juez_id` a una disciplina del torneo |
| Query | `listar_disciplinas` | Devuelve disciplinas del torneo con su juez asignado |
| Query | `listar_usuarios` | Lista usuarios con rol JUEZ disponibles para asignar |
| Componente | `TablaJueces` | Lista de disciplinas con selector de juez por fila |
| Componente | `JuezSelector` | Dropdown con jueces disponibles (rol JUEZ) |

### Lenguaje ubicuo relevante

- **Juez:** usuario con rol JUEZ — responsable de operar la UI del juez para una disciplina.
- **Disciplina del torneo:** cada disciplina habilitada tiene exactamente un juez asignado (o ninguno).
- **Asignación:** acción del organizador que vincula un `juez_id` a una `disciplina` del torneo.

---

## Especificación del comportamiento

### Invariantes

- **INV-5.1.5-01:** Un juez solo puede ser asignado a disciplinas que están en el torneo. El backend valida con `DisciplinaNoEnTorneo` (409).
- **INV-5.1.5-02:** La asignación solo está permitida cuando el torneo está en estado `Preparacion`. El backend valida con `AsignacionNoPermitida` (409).
- **INV-5.1.5-03:** Un juez puede ser asignado a múltiples disciplinas del mismo torneo.
- **INV-5.1.5-04:** Solo se muestran en el selector usuarios con rol `JUEZ`.

### Operación principal — asignarJuez

**Nombre**: `PUT /torneos/{torneo_id}/disciplinas/{disciplina}/juez`

| | Descripción |
|---|---|
| **Precondición** | Torneo en estado `Preparacion`. `disciplina` ∈ disciplinas del torneo. `juez_id` es un usuario con rol JUEZ. |
| **Postcondición** | `DisciplinaTorneo.juez_id = juez_id`. |
| **Excepciones** | 409 `DisciplinaNoEnTorneo` — disciplina no habilitada en el torneo. 409 `AsignacionNoPermitida` — torneo no en Preparacion. |

**Ejemplo concreto:**

```
Torneo T1 en Preparacion. Disciplinas: DNF, STA. Jueces disponibles: juez1@, juez2@.
PUT /torneos/T1/disciplinas/DNF/juez { juez_id: "J1" } → 200 { juez_id: "J1" }
PUT /torneos/T1/disciplinas/STA/juez { juez_id: "J2" } → 200 { juez_id: "J2" }
GET /torneos/T1/disciplinas → [DNF: juez_id=J1, STA: juez_id=J2]
```

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-5.1.5 — Asignación de jueces a disciplinas desde el panel organizador

  Background:
    Given el organizador "org@ataraxia.com" está autenticado con rol ORGANIZADOR
    And el torneo "BA 2026" con id T1 está en estado Preparacion
    And T1 tiene las disciplinas DNF y STA
    And existen los usuarios juez1@ataraxia.com y juez2@ataraxia.com con rol JUEZ

  Scenario: asignar juez a disciplina exitosamente
    Given el organizador accede al tab "Jueces" del torneo T1
    When selecciona "juez1@ataraxia.com" para la disciplina DNF
    Then el backend recibe PUT /torneos/T1/disciplinas/DNF/juez con juez_id de juez1
    And la fila de DNF muestra "juez1@ataraxia.com" como juez asignado

  Scenario: reasignar juez a disciplina ya asignada
    Given DNF tiene asignado a juez1@ataraxia.com
    When el organizador cambia el selector de DNF a "juez2@ataraxia.com"
    Then el backend recibe PUT /torneos/T1/disciplinas/DNF/juez con juez_id de juez2
    And la fila de DNF muestra "juez2@ataraxia.com"

  Scenario: disciplina sin juez asignado muestra indicador vacío
    Given STA no tiene juez asignado
    When el organizador accede al tab "Jueces"
    Then la fila de STA muestra el selector con placeholder "Sin juez asignado"

  Scenario: error del backend muestra mensaje inline
    Given el backend devuelve 409 al asignar
    When el organizador intenta asignar un juez
    Then la UI muestra el mensaje de error del backend
    And el selector vuelve al valor anterior

  Scenario: solo aparecen usuarios con rol JUEZ en el selector
    Given existe el usuario "admin@ataraxia.com" con rol ORGANIZADOR
    When el organizador abre el JuezSelector para DNF
    Then "admin@ataraxia.com" no aparece en la lista de opciones
    And sí aparecen juez1@ataraxia.com y juez2@ataraxia.com
```

---

## Impacto arquitectónico

- [x] No — consume endpoints existentes.

**Capa(s) afectadas:**
- [x] Frontend — componentes `TablaJueces`, `JuezSelector`
- [x] Frontend — tab "Jueces" en `DetalleTorneo` (US-5.1.2)
- [x] Frontend — `api/torneo.ts`: `listarDisciplinasTorneo()`, `asignarJuez()`
- [x] Frontend — `api/identidad.ts`: `listarUsuariosPorRol(rol: "JUEZ")`

---

## Referencias

- Endpoint asignar juez: `src/torneo/api/router.py` línea 227 — `PUT /torneos/{id}/disciplinas/{disc}/juez`
- Endpoint listar disciplinas: `src/torneo/api/router.py` línea 248 — `GET /torneos/{id}/disciplinas`
- Endpoint usuarios: `src/identidad/api/router.py` — `GET /identidad/usuarios` (verificar en implementación si existe o crear)
- Plan SP5: `docs/plans/sp5/PLAN-SP5.md §INC-5.1`

---

## Notas de implementación

- **`listarUsuariosPorRol`:** verificar si el endpoint `GET /identidad/usuarios?rol=JUEZ` existe. Si no existe, agregarlo al router de identidad como endpoint de consulta simple (solo lo usa el organizador).
- **`JuezSelector`:** dropdown que carga la lista de jueces al montar el componente (una sola vez por sesión, cachear en store). Mostrar email del juez como label.
- **Flujo de carga del tab:** (1) `GET /torneos/{id}/disciplinas` para ver asignaciones actuales; (2) `GET /identidad/usuarios?rol=JUEZ` para el dropdown. Ambas en paralelo.
- **Estado visual de asignación completa:** cuando todas las disciplinas tienen juez asignado, mostrar un indicador visual (badge verde) en el tab "Jueces" de `DetalleTorneo`.

---

*Redactado: 2026-04-20 — INC-5.1 Panel del Organizador*
