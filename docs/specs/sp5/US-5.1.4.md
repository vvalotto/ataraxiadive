# US-5.1.4: Generación y ajuste de grilla desde la UI del organizador

**Estado**: `To Do`
**Sprint**: SP5 — La Puesta en Marcha
**Incremento**: INC-5.1
**Bounded Context**: `frontend` (consume `competencia/api/` — endpoints existentes)
**Capas afectadas**: `frontend/src/pages/organizador/`, `frontend/src/api/competencia.ts`

---

## Descripción

Como **organizador**,
quiero **generar la grilla de salida automáticamente y reordenar manualmente las posiciones si es necesario**
para **tener la grilla confirmada y lista antes de iniciar la ejecución de la disciplina**.

---

## Contexto del dominio

### Modelo involucrado

| Elemento | Nombre | Responsabilidad |
|---|---|---|
| Aggregate | `Competencia` | Estado: Configurada → GrillaConfirmada → EnEjecucion |
| Command | `ConfigurarIntervaloOTCommand` | Crea la competencia con intervalo entre atletas |
| Command | `AjustarGrillaCommand` | Reordena posiciones en la grilla (cambios de posicion/andarivel) |
| Command | `ConfirmarGrillaCommand` | Cierra la grilla para edición, pasa a GrillaConfirmada |
| Query | `ObtenerGrillaHandler` | Devuelve la grilla ordenada por posición con AP, OT calculado |
| Componente | `TablaGrilla` | Tabla draggable de atletas ordenada por posición |
| Componente | `ConfigurarGrillaForm` | Formulario para intervalo OT y primer OT |

### Lenguaje ubicuo relevante

- **Grilla:** lista ordenada de atletas con su posición, andarivel y OT calculado.
- **OT (Official Top):** hora de inicio de la performance, calculada automáticamente según posición e intervalo.
- **Intervalo OT:** tiempo entre actuaciones consecutivas (en minutos).
- **GrillaConfirmada:** estado de la competencia donde la grilla está fija — ya no se puede reordenar.
- **Reordenamiento manual:** el organizador puede cambiar el orden de la grilla antes de confirmarla.

---

## Especificación del comportamiento

### Invariantes

- **INV-5.1.4-01:** La competencia debe existir (`POST /competencia`) antes de que la grilla pueda generarse y consultarse.
- **INV-5.1.4-02:** El reordenamiento solo es posible si la competencia está en estado `Configurada` (antes de `ConfirmarGrilla`).
- **INV-5.1.4-03:** Una vez confirmada la grilla (`GrillaConfirmada`), la tabla queda en modo read-only.
- **INV-5.1.4-04:** El botón "Confirmar grilla" aparece solo si hay al menos un atleta en la grilla.

### Operación 1 — Crear competencia (si no existe)

**Nombre**: `POST /competencia`

| | Descripción |
|---|---|
| **Precondición** | No existe competencia para la disciplina en el torneo. Organizador autenticado. |
| **Postcondición** | Competencia creada en estado `Configurada` con el intervalo OT especificado. |
| **Body** | `{ competencia_id, disciplina, intervalo_minutos, configurado_por, torneo_id }` |

### Operación 2 — Ver grilla

**Nombre**: `GET /competencia/{competencia_id}/grilla`

Devuelve lista de performances con AP, posición, andarivel y OT calculado.

### Operación 3 — Ajustar grilla

**Nombre**: `POST /competencia/{competencia_id}/ajustar-grilla`

| | Descripción |
|---|---|
| **Precondición** | Competencia en estado `Configurada`. |
| **Postcondición** | Posiciones actualizadas según los cambios. |
| **Body** | `{ disciplina, cambios: [{ performance_id, campo: "posicion_grilla", valor_nuevo }] }` |

### Operación 4 — Confirmar grilla

**Nombre**: `POST /competencia/{competencia_id}/confirmar-grilla`

| | Descripción |
|---|---|
| **Precondición** | Competencia en estado `Configurada`. Al menos un atleta en grilla. |
| **Postcondición** | Competencia en estado `GrillaConfirmada`. Grilla fija. |

**Ejemplo concreto:**

```
Torneo T1 Preparacion. Disciplina DNF. Intervalo: 8 min. Primer OT: 09:00.
POST /competencia → competencia_id = C1, estado Configurada
GET /competencia/C1/grilla → [García pos=1 OT=09:00, López pos=2 OT=09:08, Ruiz pos=3 OT=09:16]
Organizador arrastra Ruiz a posición 1:
POST /competencia/C1/ajustar-grilla → { cambios: [Ruiz→pos1, García→pos3, López→pos2] }
GET /competencia/C1/grilla → [Ruiz pos=1 OT=09:00, López pos=2 OT=09:08, García pos=3 OT=09:16]
POST /competencia/C1/confirmar-grilla → estado GrillaConfirmada
Tabla queda en modo read-only.
```

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-5.1.4 — Generación y ajuste de grilla desde el panel organizador

  Background:
    Given el organizador "org@ataraxia.com" está autenticado con rol ORGANIZADOR
    And el torneo "BA 2026" con id T1 está en estado Preparacion
    And la disciplina DNF tiene 3 atletas con AP registrado

  Scenario: crear y visualizar grilla automática
    Given no existe competencia para DNF en el torneo T1
    When el organizador accede al tab "Grilla" del torneo T1 y selecciona disciplina DNF
    And completa intervalo OT "8 minutos" y primer OT "09:00"
    And toca "Generar grilla"
    Then el backend recibe POST /competencia con disciplina=DNF, intervalo=8, torneo_id=T1
    And la tabla muestra los 3 atletas ordenados con OT calculado (09:00, 09:08, 09:16)

  Scenario: reordenar posiciones de la grilla
    Given existe competencia C1 para DNF en estado Configurada
    And la grilla tiene: García pos=1, López pos=2, Ruiz pos=3
    When el organizador arrastra la fila de Ruiz a la posición 1
    Then el backend recibe POST /competencia/C1/ajustar-grilla con los cambios de posición
    And la tabla se actualiza: Ruiz pos=1 OT=09:00, López pos=2 OT=09:08, García pos=3 OT=09:16

  Scenario: confirmar grilla
    Given existe competencia C1 para DNF en estado Configurada con 3 atletas
    When el organizador toca "Confirmar grilla"
    Then el backend recibe POST /competencia/C1/confirmar-grilla
    And la tabla pasa a modo read-only (sin drag, sin edición)
    And el estado de la competencia muestra "Grilla confirmada"

  Scenario: grilla confirmada es read-only
    Given existe competencia C1 para DNF en estado GrillaConfirmada
    When el organizador accede al tab "Grilla" y selecciona DNF
    Then ve la grilla sin controles de reordenamiento
    And el botón "Confirmar grilla" no aparece

  Scenario: sin atletas en grilla el botón confirmar está deshabilitado
    Given existe competencia C1 para DNF en estado Configurada sin atletas
    When el organizador accede al tab "Grilla"
    Then el botón "Confirmar grilla" está deshabilitado
```

---

## Impacto arquitectónico

- [x] No — consume endpoints existentes.

**Capa(s) afectadas:**
- [x] Frontend — componentes `TablaGrilla` (drag-and-drop), `ConfigurarGrillaForm`
- [x] Frontend — tab "Grilla" en `DetalleTorneo` (creado en US-5.1.2)
- [x] Frontend — `api/competencia.ts`: `crearCompetencia()`, `obtenerGrilla()`, `ajustarGrilla()`, `confirmarGrilla()`

---

## Referencias

- Endpoints backend: `src/competencia/api/router.py` — `POST /competencia`, `GET /{id}/grilla`, `POST /{id}/ajustar-grilla`, `POST /{id}/confirmar-grilla`
- Endpoint query por torneo: `GET /competencia?torneo_id=X&disciplina=Y` — `ObtenerCompetenciasPorTorneoHandler`
- Plan SP5: `docs/plans/sp5/PLAN-SP5.md §INC-5.1`

---

## Notas de implementación

- **Drag-and-drop:** usar `@dnd-kit/core` (ya presente en el proyecto desde INC-4.3). La tabla envía todos los cambios de posición en un único `POST ajustar-grilla` al soltar la fila.
- **Selector de disciplina:** dropdown en el tab Grilla para elegir la disciplina a gestionar. Si el torneo tiene múltiples disciplinas, se muestran todas; la competencia se crea/consulta para cada una independientemente.
- **Primer OT:** campo `time` (HH:MM) — la UI genera el `competencia_id` como UUID en el cliente antes de enviarlo al backend.
- **Organización de cambios al ajustar:** al reordenar, la UI recalcula todas las posiciones (1..N) y envía los cambios para las posiciones que cambiaron.
- **`GET /competencia?torneo_id&disciplina`:** usar para verificar si ya existe competencia antes de mostrar el formulario de creación.

---

*Redactado: 2026-04-20 — INC-5.1 Panel del Organizador*
