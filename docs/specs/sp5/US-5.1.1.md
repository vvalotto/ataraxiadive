# US-5.1.1: Crear/editar torneo — formulario del organizador

**Estado**: `To Do`
**Sprint**: SP5 — La Puesta en Marcha
**Incremento**: INC-5.1
**Bounded Context**: `frontend` (consume `torneo/api/` — endpoints existentes)
**Capas afectadas**: `frontend/src/pages/organizador/`, `frontend/src/api/torneo.ts`

---

## Descripción

Como **organizador**,
quiero **crear un torneo desde la UI completando nombre, sede, fechas, entidad organizadora y disciplinas**
para **tener el torneo registrado en el sistema y listo para gestionar su ciclo de vida**.

---

## Contexto del dominio

### Modelo involucrado

| Elemento | Nombre | Responsabilidad |
|---|---|---|
| Aggregate | `Torneo` | Ciclo de vida del torneo; estado inicial `Creado` |
| Value Object | `Sede` | nombre + ciudad + país |
| Value Object | `EntidadOrganizadora` | nombre + tipo |
| Value Object | `Disciplina` | enum FAAS: STA, DNF, DYN, DBF, SPE_2X50, SPE_4X50, SPE_8X50, SPE_16X50 |
| Página | `CrearTorneo` | Formulario de alta + edición de disciplinas |
| Componente | `DisciplinaSelector` | Checkboxes de disciplinas disponibles |

### Lenguaje ubicuo relevante

- **Torneo:** evento de apnea con nombre, sede, fechas y disciplinas habilitadas.
- **Sede:** lugar físico donde se realiza el torneo (nombre del lugar + ciudad + país).
- **Estado Creado:** estado inicial del torneo — aún no abierto a inscripciones.
- **Disciplina:** modalidad del torneo (STA, DNF, DYN, DBF, SPE_2X50, SPE_4X50, SPE_8X50, SPE_16X50).

---

## Especificación del comportamiento

### Invariantes

- **INV-5.1.1-01:** El nombre del torneo no puede estar vacío.
- **INV-5.1.1-02:** `fecha_fin ≥ fecha_inicio` — el backend valida y devuelve 422 si no se cumple.
- **INV-5.1.1-03:** Se debe seleccionar al menos una disciplina antes de enviar el formulario.
- **INV-5.1.1-04:** Las disciplinas solo pueden asignarse cuando el torneo está en estado `Creado` o `Preparacion` — si el backend rechaza con 409, la UI muestra el error sin recargar.

### Operación principal — Crear torneo

**Nombre**: `POST /torneos`

| | Descripción |
|---|---|
| **Precondición** | Usuario autenticado con rol ORGANIZADOR. Campos nombre, sede, fechas, entidad_organizadora válidos. |
| **Postcondición** | Torneo creado con estado `Creado`. `torneo_id` disponible para el siguiente paso (asignación de disciplinas). |
| **Excepciones** | 422 si fecha_fin < fecha_inicio o nombre vacío. |

### Operación secundaria — Asignar disciplinas

**Nombre**: `PUT /torneos/{torneo_id}/disciplinas`

| | Descripción |
|---|---|
| **Precondición** | Torneo en estado `Creado`. Al menos una disciplina seleccionada. |
| **Postcondición** | Disciplinas asignadas al torneo. |
| **Excepciones** | 409 si torneo no está en estado permitido (backend `AsignacionNoPermitida`). |

**Ejemplo concreto:**

```
Paso 1: POST /torneos { nombre: "BA 2026", fecha_inicio: "2026-10-01", fecha_fin: "2026-10-03",
          sede: { nombre: "Club Náutico", ciudad: "Buenos Aires", pais: "Argentina" },
          entidad_organizadora: { nombre: "FAAS", tipo: "Federación" } }
        → 201 { torneo_id: "T1" }
Paso 2: PUT /torneos/T1/disciplinas { disciplinas: ["STA", "DNF", "DYN"] }
        → 200 { ok: true }
Postcondición: Torneo T1 creado con estado Creado, 3 disciplinas asignadas.
               UI navega a /organizador/torneo/T1
```

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-5.1.1 — Crear torneo desde la UI del organizador

  Background:
    Given el organizador "org@ataraxia.com" está autenticado con rol ORGANIZADOR

  Scenario: crear torneo con disciplinas exitosamente
    Given el organizador accede a /organizador/torneos/nuevo
    When completa nombre "BA 2026", sede "Club Náutico / Buenos Aires / Argentina"
    And selecciona fechas 2026-10-01 a 2026-10-03
    And completa entidad organizadora "FAAS / Federación"
    And selecciona las disciplinas STA, DNF, DYN
    And toca "Crear Torneo"
    Then el backend recibe POST /torneos con los datos correctos
    And el backend recibe PUT /torneos/{id}/disciplinas con ["STA", "DNF", "DYN"]
    And la UI navega a /organizador/torneo/{id}
    And el torneo aparece con estado "Creado"

  Scenario: validación frontend — fechas incoherentes
    Given el organizador completa fecha_inicio "2026-10-03" y fecha_fin "2026-10-01"
    When toca "Crear Torneo"
    Then el formulario muestra el error "La fecha de fin debe ser igual o posterior a la de inicio"
    And no se realiza ninguna llamada al backend

  Scenario: validación frontend — nombre vacío
    Given el organizador deja el campo nombre vacío
    When toca "Crear Torneo"
    Then el formulario muestra el error "El nombre es obligatorio"
    And no se realiza ninguna llamada al backend

  Scenario: validación frontend — sin disciplinas seleccionadas
    Given el organizador no selecciona ninguna disciplina
    When toca "Crear Torneo"
    Then el formulario muestra el error "Seleccioná al menos una disciplina"
    And no se realiza ninguna llamada al backend

  Scenario: error de backend muestra mensaje inline
    Given el backend devuelve 422 al crear el torneo
    When el organizador toca "Crear Torneo"
    Then la UI muestra el mensaje de error devuelto por el backend
    And el formulario permanece abierto con los datos ingresados
```

---

## Impacto arquitectónico

- [x] No — consume endpoints existentes (`POST /torneos`, `PUT /torneos/{id}/disciplinas`).

**Capa(s) afectadas:**
- [x] Frontend — nueva página `CrearTorneo`, componente `DisciplinaSelector`
- [x] Frontend — `api/torneo.ts`: agregar `crearTorneo()` y `asignarDisciplinas()`

---

## Referencias

- Endpoints backend: `src/torneo/api/router.py` — `POST /torneos` (línea 121), `PUT /torneos/{id}/disciplinas` (línea 208)
- Plan SP5: `docs/plans/sp5/PLAN-SP5.md §INC-5.1`
- Stack frontend: `docs/design/ux/decisiones-frontend.md`

---

## Notas de implementación

- **Flujo de dos pasos:** primero `POST /torneos` → obtener `torneo_id` → luego `PUT /torneos/{id}/disciplinas`. Si el segundo paso falla, el torneo quedó creado sin disciplinas — mostrar error y permitir reintentar desde el detalle del torneo.
- **`DisciplinaSelector`:** checkboxes de las 8 disciplinas FAAS: STA, DNF, DYN, DBF, SPE_2X50, SPE_4X50, SPE_8X50, SPE_16X50. El display puede mostrar nombres legibles ("SPE 2×50m") mientras envía el valor del enum.
- **Ruta de la página:** `/organizador/torneos/nuevo` — agregar en `App.tsx` con guardia de rol ORGANIZADOR.
- **Tipo de entidad organizadora:** campo libre en la UI — el backend lo acepta como string sin validar el tipo.
- **Post-creación:** navegar a `/organizador/torneo/{torneo_id}` (pantalla de detalle del torneo — se crea en US-5.1.2).

---

*Redactado: 2026-04-20 — INC-5.1 Panel del Organizador*
