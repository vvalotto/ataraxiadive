# US-5.1.3: Vista de inscriptos en Preparación — estado de AP por atleta

**Estado**: `To Do`
**Sprint**: SP5 — La Puesta en Marcha
**Incremento**: INC-5.1
**Bounded Context**: `frontend` (consume `registro/api/` + `competencia/api/` — endpoints existentes)
**Capas afectadas**: `frontend/src/pages/organizador/`, `frontend/src/api/registro.ts`, `frontend/src/api/competencia.ts`

---

## Descripción

Como **organizador**,
quiero **ver la lista de atletas inscriptos al torneo con indicación de si ya registraron su AP por disciplina**
para **saber quiénes están listos para generar la grilla antes de iniciar la ejecución**.

---

## Contexto del dominio

### Modelo involucrado

| Elemento | Nombre | Responsabilidad |
|---|---|---|
| Aggregate | `Inscripcion` | Registro del atleta en el torneo con disciplinas elegidas |
| Query | `listar_inscriptos` | Lista de inscripciones por torneo con atleta + disciplinas |
| Componente | `TablaInscriptos` | Tabla con columnas atleta / disciplinas / estado AP |
| Componente | `EstadoAPBadge` | Badge verde (AP registrado) / amarillo (sin AP) por disciplina |

### Lenguaje ubicuo relevante

- **Inscripto:** atleta que se registró en el torneo con al menos una disciplina.
- **AP (Announced Performance):** marca que el atleta declara antes de competir. Sin AP no puede ingresar a la grilla.
- **Estado de AP:** si el atleta ya registró su AP para una disciplina dada. El backend de competencia expone esta información a través de la grilla o las performances.

---

## Especificación del comportamiento

### Invariantes

- **INV-5.1.3-01:** La lista de inscriptos es read-only para el organizador en esta vista — no puede modificar inscripciones desde aquí.
- **INV-5.1.3-02:** El estado de AP se determina consultando `GET /competencia/{competencia_id}/grilla` — si el atleta aparece con una `AP` definida, tiene AP registrado.
- **INV-5.1.3-03:** La vista es accesible desde el estado `Preparacion` (y posteriores) del torneo.

### Operación principal — cargarInscriptos

| | Descripción |
|---|---|
| **Precondición** | Organizador autenticado. Torneo en estado `Preparacion` o posterior. |
| **Postcondición** | Lista de atletas con su estado de AP por disciplina visible en pantalla. |
| **Excepciones** | Sin inscriptos → mensaje "No hay atletas inscriptos en este torneo". |

**Flujo de datos:**

```
1. GET /registro/torneos/{torneo_id}/inscriptos
   → lista de { inscripcion_id, atleta_id, disciplinas[], estado }

2. Para cada disciplina del torneo:
   GET /competencias?torneo_id={id}&disciplina={disc}
   → competencia_id

3. GET /competencia/{competencia_id}/grilla
   → lista de atletas con AP

4. Cruzar atleta_id: si está en grilla con AP definida → "AP registrado"; si no → "Sin AP"
```

**Ejemplo concreto:**

```
Torneo T1 en Preparacion. 3 atletas inscriptos en DNF: García (AP=75m), López (sin AP), Ruiz (AP=60m).
Postcondición: tabla muestra:
  García  | DNF: ● AP registrado (75m)
  López   | DNF: ○ Sin AP
  Ruiz    | DNF: ● AP registrado (60m)
```

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-5.1.3 — Vista de inscriptos con estado de AP

  Background:
    Given el organizador "org@ataraxia.com" está autenticado con rol ORGANIZADOR
    And el torneo "BA 2026" con id T1 está en estado Preparacion
    And la disciplina DNF tiene competencia_id C1

  Scenario: lista de inscriptos con estado de AP mixto
    Given hay 3 atletas inscriptos en DNF: García (AP=75m), López (sin AP), Ruiz (AP=60m)
    When el organizador accede al tab "Inscriptos" del torneo T1
    Then ve 3 filas en la tabla
    And García muestra badge verde "AP registrado" con valor 75m
    And López muestra badge amarillo "Sin AP"
    And Ruiz muestra badge verde "AP registrado" con valor 60m

  Scenario: filtrar por disciplina cuando el torneo tiene múltiples
    Given el torneo T1 tiene disciplinas DNF y STA
    And hay atletas inscriptos en ambas disciplinas
    When el organizador selecciona el filtro "DNF"
    Then solo ve los atletas inscriptos en DNF

  Scenario: sin inscriptos muestra mensaje vacío
    Given no hay atletas inscriptos en el torneo T1
    When el organizador accede al tab "Inscriptos"
    Then ve el mensaje "No hay atletas inscriptos en este torneo"

  Scenario: atleta inscripto en varias disciplinas muestra estado por disciplina
    Given el atleta García está inscripto en DNF y STA
    And tiene AP en DNF pero no en STA
    When el organizador ve la tabla
    Then García muestra DNF: AP registrado | STA: Sin AP en la misma fila
```

---

## Impacto arquitectónico

- [x] No — consume endpoints existentes.

**Capa(s) afectadas:**
- [x] Frontend — componente `TablaInscriptos`, `EstadoAPBadge`
- [x] Frontend — tab "Inscriptos" en `DetalleTorneo` (creado en US-5.1.2)
- [x] Frontend — `api/registro.ts`: `listarInscriptos(torneoId)`
- [x] Frontend — `api/competencia.ts`: `obtenerGrilla(competenciaId)`

---

## Referencias

- Endpoint inscriptos: `src/registro/api/router.py` línea 216 — `GET /registro/torneos/{id}/inscriptos`
- Endpoint grilla: `src/competencia/api/router.py` — `GET /competencia/{id}/grilla`
- Plan SP5: `docs/plans/sp5/PLAN-SP5.md §INC-5.1`

---

## Notas de implementación

- **Cruce de datos:** el endpoint de inscriptos devuelve `atleta_id` y `disciplinas`. La información de AP vive en la grilla de competencia. El frontend hace el cruce: para cada disciplina del torneo, obtiene la grilla y busca al atleta por `atleta_id`.
- **Performance:** si hay muchas disciplinas, hacer los fetches de grillas en paralelo con `Promise.all`.
- **Filtro de disciplina:** selector de disciplina en la parte superior de la tabla — por defecto muestra "Todas".
- **Columnas de la tabla:** Atleta (apellido, nombre) | Club | Categoría | Género | por cada disciplina: estado AP.
- **No mostrar el `atleta_id` en la UI** — solo nombre, club, categoría, género.

---

*Redactado: 2026-04-20 — INC-5.1 Panel del Organizador*
