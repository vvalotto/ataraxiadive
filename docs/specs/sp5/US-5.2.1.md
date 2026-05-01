# US-5.2.1: Vista maestro-detalle de disciplinas en ejecucion

**Estado**: `To Do`
**Sprint**: SP5 — La Puesta en Marcha
**Incremento**: INC-5.2
**Bounded Context**: `frontend` (consume `torneo/api/` y `competencia/api/`)
**Capas afectadas**: `frontend/src/components/organizador/`, `frontend/src/api/competencia.ts`, `frontend/src/api/torneo.ts`

---

## Descripcion

Como **organizador**,
quiero **ver todas las disciplinas del torneo en ejecucion en una vista maestro-detalle y habilitar individualmente cada prueba**
para **controlar el inicio operativo de cada disciplina y monitorear su avance desde un unico lugar**.

---

## Contexto del dominio

### Modelo involucrado

| Elemento | Nombre | Responsabilidad |
|---|---|---|
| Aggregate | `Competencia` | Ciclo de vida de una disciplina: `Preparacion` -> `Confirmada` -> `EnEjecucion` -> `Finalizada` |
| Command | `IniciarCompetenciaCommand` | Habilita una competencia confirmada para que el juez ejecute performances |
| Query | `ObtenerCompetenciasPorTorneoHandler` | Devuelve competencias materializadas por torneo |
| Query | `ObtenerEstadoCompetenciaHandler` | Devuelve estado, grilla confirmada, intervalo y hash de cierre |
| Query | `ObtenerGrillaHandler` | Devuelve grilla OT ordenada para la disciplina seleccionada |
| Query | `ObtenerProgresoHandler` | Devuelve total, ejecutadas, DNS y completadas |
| Query | `ObtenerPerformanceActualHandler` | Devuelve atleta actualmente en ejecucion |
| Query | `ObtenerProximasPerformancesHandler` | Devuelve proximas performances pendientes |
| Componente | `EjecucionPanel` | Vista maestro-detalle de disciplinas del torneo |
| Componente | `MonitorDisciplina` | Detalle operativo de la disciplina seleccionada |

### Lenguaje ubicuo relevante

- **Vista maestro-detalle:** lista de disciplinas del torneo como maestro; detalle operativo de la disciplina seleccionada.
- **Habilitar disciplina:** accion del organizador que ejecuta `POST /competencia/{id}/iniciar`.
- **Disciplina pendiente:** disciplina del torneo que todavia no tiene competencia creada o no tiene grilla confirmada.
- **Disciplina lista para iniciar:** competencia con grilla confirmada y juez asignado, aun no iniciada.
- **Disciplina en ejecucion:** competencia en estado `EnEjecucion`.
- **Disciplina finalizada:** competencia en estado `Finalizada`.

---

## Especificacion del comportamiento

### Invariantes

- **INV-5.2.1-01:** El tab `Ejecucion` solo es operable cuando el torneo esta en estado `EJECUCION`.
- **INV-5.2.1-02:** El maestro muestra todas las disciplinas configuradas del torneo, no solo las competencias en estado `EnEjecucion`.
- **INV-5.2.1-03:** La accion `Habilitar disciplina` solo aparece habilitada si existe `competencia_id`, la grilla esta confirmada y la disciplina tiene juez asignado.
- **INV-5.2.1-04:** `POST /competencia/{id}/iniciar` solo se dispara desde el detalle de una disciplina seleccionada.
- **INV-5.2.1-05:** Si una disciplina ya esta `EnEjecucion` o `Finalizada`, la accion `Habilitar disciplina` no se muestra.
- **INV-5.2.1-06:** El detalle nunca debe permitir operar una disciplina sin juez asignado; debe mostrar el bloqueo operativo.

### Operacion principal — cargar maestro de disciplinas

| | Descripcion |
|---|---|
| **Precondicion** | Usuario autenticado con rol ORGANIZADOR. Torneo en estado `EJECUCION`. |
| **Postcondicion** | Se muestra una fila/card por disciplina configurada del torneo, enriquecida con competencia, estado, juez, grilla y progreso cuando existan datos. |

**Flujo de datos:**

```
1. GET /torneos/{torneo_id}/disciplinas
   -> fuente primaria de disciplinas configuradas y juez asignado
2. GET /competencia?torneo_id={torneo_id}
   -> competencias ya materializadas por disciplina
3. Para cada disciplina con competencia_id:
   GET /competencia/{id}/estado?disciplina={disciplina}
   GET /competencia/{id}/progreso
4. Renderizar maestro con:
   disciplina, juez, competencia_id, estado_competencia,
   grilla_confirmada, completadas/total y estado operativo derivado
```

### Operacion secundaria — seleccionar disciplina

| | Descripcion |
|---|---|
| **Precondicion** | La disciplina existe en el torneo. |
| **Postcondicion** | El detalle muestra grilla OT, juez asignado, performance actual, proximas performances y progreso. |

**Flujo de datos del detalle:**

```
GET /competencia/{id}/grilla?disciplina={disciplina}
GET /competencia/{id}/performance/actual
GET /competencia/{id}/performance/proximas?disciplina={disciplina}
GET /competencia/{id}/progreso
```

### Operacion terciaria — habilitar disciplina

**Nombre**: `POST /competencia/{competencia_id}/iniciar`

| | Descripcion |
|---|---|
| **Precondicion** | Competencia en estado `Confirmada`, grilla confirmada, juez asignado. |
| **Postcondicion** | Competencia transiciona a `EnEjecucion`; el juez puede llamar atletas y registrar performances. |
| **Body** | `{ disciplina, juez_id }` |
| **Excepciones** | 409 si la competencia no esta en estado `Confirmada`; 404 si no existe competencia; bloqueo frontend si falta juez o grilla confirmada. |

**Ejemplo concreto:**

```
Torneo T1 en EJECUCION.
Disciplinas configuradas: DNF, STA.
DNF tiene competencia C1, grilla confirmada, juez J1, estado Confirmada.
STA tiene competencia C2, grilla no confirmada, juez J2.

Maestro:
  DNF — Lista para iniciar — juez J1 — 0/12 completadas
  STA — Bloqueada: confirmar grilla — juez J2

Organizador selecciona DNF.
Detalle muestra grilla OT y boton "Habilitar disciplina".
POST /competencia/C1/iniciar { disciplina: "DNF", juez_id: "J1" } -> 204
Detalle recarga: estado EnEjecucion, boton oculto, monitor activo.
```

---

## Criterios de aceptacion (BDD)

```gherkin
Feature: US-5.2.1 — Vista maestro-detalle de ejecucion por disciplina

  Background:
    Given el organizador "org@ataraxia.com" esta autenticado con rol ORGANIZADOR
    And el torneo "BA 2026" con id T1 esta en estado EJECUCION
    And el torneo T1 tiene disciplinas DNF y STA configuradas

  Scenario: maestro muestra todas las disciplinas del torneo
    Given DNF tiene competencia C1 en estado Confirmada con grilla confirmada y juez J1
    And STA tiene competencia C2 en estado Preparacion sin grilla confirmada y juez J2
    When el organizador abre el tab "Ejecucion"
    Then ve una fila o card para DNF
    And ve una fila o card para STA
    And DNF muestra estado "Lista para iniciar"
    And STA muestra bloqueo "Confirmar grilla antes de habilitar"

  Scenario: seleccionar disciplina abre detalle operativo
    Given DNF tiene competencia C1 en estado EnEjecucion con 10 atletas
    And 4 atletas estan completados
    When el organizador selecciona DNF en el maestro
    Then el detalle muestra la grilla OT de DNF
    And muestra el juez asignado
    And muestra progreso "4 / 10"
    And muestra atleta actual si existe
    And muestra proximas performances

  Scenario: habilitar disciplina lista para iniciar
    Given DNF tiene competencia C1 en estado Confirmada
    And DNF tiene grilla confirmada
    And DNF tiene juez J1 asignado
    When el organizador selecciona DNF
    And toca "Habilitar disciplina"
    Then el frontend envia POST /competencia/C1/iniciar con disciplina DNF y juez_id J1
    And la disciplina recarga con estado EnEjecucion
    And la accion "Habilitar disciplina" deja de mostrarse

  Scenario: disciplina sin juez no puede habilitarse
    Given DNF tiene competencia C1 en estado Confirmada
    And DNF tiene grilla confirmada
    And DNF no tiene juez asignado
    When el organizador selecciona DNF
    Then la accion "Habilitar disciplina" esta deshabilitada
    And el detalle muestra "Asignar juez antes de habilitar"
    And no se envia POST /competencia/C1/iniciar

  Scenario: disciplina sin grilla confirmada no puede habilitarse
    Given DNF tiene competencia C1 en estado Preparacion
    And DNF no tiene grilla confirmada
    And DNF tiene juez J1 asignado
    When el organizador selecciona DNF
    Then la accion "Habilitar disciplina" esta deshabilitada
    And el detalle muestra "Confirmar grilla antes de habilitar"
    And no se envia POST /competencia/C1/iniciar

  Scenario: disciplina finalizada se muestra en modo lectura
    Given DNF tiene competencia C1 en estado Finalizada
    When el organizador selecciona DNF
    Then el detalle muestra estado "Finalizada"
    And muestra el hash SHA-256 si esta disponible
    And no muestra acciones de habilitacion
```

---

## Impacto arquitectonico

- [x] No — reutiliza dominio y endpoint existente para iniciar competencia.

**Capa(s) afectadas:**
- [x] Frontend — `EjecucionPanel`: convertir en vista maestro-detalle.
- [x] Frontend — `MonitorDisciplina`: reutilizar para detalle de disciplina seleccionada.
- [x] Frontend — `api/competencia.ts`: agregar wrapper `iniciarCompetencia()`.
- [x] Frontend — composicion de datos con `GET /torneos/{id}/disciplinas` y `GET /competencia?torneo_id=...`.

---

## Referencias

- Plan SP5: `docs/plans/sp5/PLAN-SP5.md §INC-5.2`
- Hallazgo UAT: `.work/revision-sp5/01-hallazgos-uat-inc-5.1.md §UAT-5.1-06`
- Endpoint iniciar: `src/competencia/api/router.py` — `POST /competencia/{competencia_id}/iniciar`
- Command: `src/competencia/application/commands/iniciar_competencia.py`
- Aggregate: `src/competencia/domain/aggregates/competencia.py`
- Spec previa: `docs/specs/sp5/US-5.1.6.md`

---

## Notas de implementacion

- La fuente primaria para listar disciplinas debe ser `GET /torneos/{torneo_id}/disciplinas`; `GET /competencia?torneo_id=...` solo indica que una competencia ya fue creada en el BC Competencia.
- El estado operativo mostrado en el maestro es derivado: sin competencia, sin grilla, sin juez, lista para iniciar, en ejecucion o finalizada.
- El boton de habilitacion debe usar el `juez_id` asignado en Torneo; no debe pedirlo manualmente en esta pantalla.
- Mantener el refresco automatico del monitor cada 30 segundos para competencias en `EnEjecucion`.
- Esta US no implementa cierre manual; el detalle debe reservar el espacio de accion para `US-5.2.2`.

---

*Redactado: 2026-04-22 — INC-5.2 Ejecucion por Disciplina*
