# US-5.5.2: Vista del organizador — inscriptos con estado AP

**Estado**: `To Do`
**Sprint**: SP5 — La Puesta en Marcha
**Incremento**: INC-5.5
**Bounded Context**: `registro` (endpoint) + `frontend`
**Capas afectadas**: `registro/application/queries/`, `registro/api/router.py`, `frontend/src/api/registro.ts`, `frontend/src/components/organizador/InscriptosPanel.tsx`

---

## Descripcion

Como **organizador**,
quiero **ver la lista de inscriptos con nombre completo, disciplinas y estado de AP por disciplina**
para **saber quién ya declaró su marca y quién aún no, antes de generar las grillas**.

---

## Contexto del dominio

El `InscriptosPanel` ya existe y se muestra en `DetalleTorneoPage` bajo la pestaña "Inscriptos". La vista actualmente hace N+1 queries (un `GET /registro/atletas/{id}` por cada inscripto) para obtener nombre y apellido. Esta US consolida inscripcion + datos del atleta en un único endpoint en BC Registro, reduciendo el número de llamadas al backend.

### Modelo involucrado

| Elemento | Nombre | Descripcion |
|---|---|---|
| Query nueva | `ListarInscriptosDetalleHandler` | Une inscripcion + atleta (nombre, apellido, categoria, club) en una sola llamada |
| Endpoint nuevo | `GET /registro/torneos/{id}/inscriptos-detalle` | OrganizadorDep; responde `InscriptoDetalleDto[]` |
| DTO nuevo | `InscriptoDetalleDto` | `inscripcion_id`, `atleta_id`, `nombre`, `apellido`, `categoria`, `club`, `disciplinas`, `estado` |
| Función frontend nueva | `listarInscriptosDetalle(torneoId)` | En `api/registro.ts` |
| Componente existente actualizado | `InscriptosPanel` | Usa el nuevo endpoint en lugar del N+1 actual |

### Lenguaje ubicuo relevante

- **Inscripto con AP:** atleta con al menos una disciplina en estado `AnunciadaAP` — listo para la grilla.
- **Inscripto sin AP:** atleta inscripto que aún no declaró ninguna marca.
- El estado AP vive en BC Competencia (event store); el endpoint de Registro no lo incluye — el frontend lo cruza contra la grilla.

---

## Especificacion del comportamiento

### Invariantes

- **INV-5.5.2-01:** Solo el organizador puede acceder a la vista detallada de inscriptos.
- **INV-5.5.2-02:** La lista incluye únicamente inscripciones con estado `ACTIVA`; las `CANCELADA` no aparecen.
- **INV-5.5.2-03:** El estado AP por disciplina se calcula desde la grilla de la competencia correspondiente; no se persiste en BC Registro. El frontend lo agrega cruzando con `GET /competencia/{id}/grilla`.

### Operacion principal — listar inscriptos con detalle

**Endpoint nuevo:**

```
GET /registro/torneos/{torneo_id}/inscriptos-detalle
Auth: OrganizadorDep

200 OK → [
  {
    "inscripcion_id": UUID,
    "atleta_id": UUID,
    "nombre": str,
    "apellido": str,
    "categoria": str,   ← "SENIOR" | "MASTER" | "JUNIOR"
    "club": str,
    "disciplinas": [str],
    "estado": "ACTIVA"
  },
  ...
]
```

El handler une los repositorios en la capa de aplicacion: carga inscripciones ACTIVAS del torneo y para cada una busca el atleta por `atleta_id`.

**Flujo en InscriptosPanel actualizado:**

```
ANTES (N+1):
  GET /registro/torneos/{id}/inscriptos        → lista básica (N atletas)
  Para cada atleta_id: GET /registro/atletas/{id} → N llamadas adicionales

DESPUÉS (1 + M):
  GET /registro/torneos/{id}/inscriptos-detalle → lista enriquecida (1 llamada)
  Para cada disciplina del torneo:
    GET /competencia/{comp_id}/grilla           → estado AP (M = disciplinas del torneo)
```

**Ejemplo concreto:**

```
Organizador accede a DetalleTorneoPage → pestaña "Inscriptos"

InscriptosPanel llama:
  GET /registro/torneos/uuid-ba-open/inscriptos-detalle

Respuesta:
[
  { apellido:"García", nombre:"Ana", categoria:"SENIOR", club:"Club Aqua",
    disciplinas:["DNF","STA"], estado:"ACTIVA" },
  { apellido:"López", nombre:"Carlos", categoria:"MASTER", club:"Club Mar",
    disciplinas:["DYN"], estado:"ACTIVA" }
]

InscriptosPanel consulta grilla para cada competencia:
  comp-dnf/grilla → Ana tiene AP=70 m; Carlos no está (distinta disciplina)
  comp-sta/grilla → Ana sin AP
  comp-dyn/grilla → Carlos sin AP

Tabla resultante:
  García, Ana   | SENIOR | Club Aqua | DNF: AP(70m) · STA: Sin AP
  López, Carlos | MASTER | Club Mar  | DYN: Sin AP
```

---

## Criterios de aceptacion (BDD)

```gherkin
Feature: US-5.5.2 — Vista del organizador con inscriptos y estado AP

  Background:
    Given el torneo "BA Open 2026" tiene inscriptos activos:
      | apellido | nombre | categoria | club      | disciplinas |
      | García   | Ana    | SENIOR    | Club Aqua | DNF, STA    |
      | López    | Carlos | MASTER    | Club Mar  | DYN         |
    And "ana@email.com" registró AP=70 para DNF
    And "pepe@email.com" canceló su inscripcion (estado CANCELADA)

  Scenario: organizador obtiene lista enriquecida de inscriptos
    Given el organizador esta autenticado
    When GET /registro/torneos/{id}/inscriptos-detalle
    Then el sistema responde 200
    And la respuesta contiene a García Ana con disciplinas [DNF, STA]
    And la respuesta contiene a López Carlos con disciplinas [DYN]
    And la respuesta no contiene a Pepe (inscripcion CANCELADA)

  Scenario: InscriptosPanel muestra estado AP por disciplina
    Given el organizador esta en la pestaña "Inscriptos" del torneo
    Then ve "García, Ana" con "AP registrado: 70 m" para DNF
    And ve "García, Ana" con "Sin AP" para STA
    And ve "López, Carlos" con "Sin AP" para DYN

  Scenario: inscripcion cancelada no aparece en la lista
    When GET /registro/torneos/{id}/inscriptos-detalle
    Then la respuesta no incluye inscripciones con estado CANCELADA

  Scenario: acceso sin rol organizador es rechazado
    Given el usuario esta autenticado con rol ATLETA
    When GET /registro/torneos/{id}/inscriptos-detalle
    Then el sistema responde 403

  Scenario: torneo sin inscriptos devuelve lista vacia
    Given el torneo "Torneo Vacío" no tiene inscriptos activos
    When GET /registro/torneos/{id-vacio}/inscriptos-detalle
    Then el sistema responde 200
    And la respuesta es una lista vacia []
```

---

## Impacto arquitectonico

- [x] No — extiende BC Registro con una nueva query; no modifica aggregates ni eventos.

**Capas afectadas:**

- `registro/application/queries/listar_inscriptos_detalle.py` — nuevo handler que lee `InscripcionRepository` y `AtletaRepository` y arma el DTO enriquecido.
- `registro/api/router.py` — endpoint `GET /torneos/{torneo_id}/inscriptos-detalle` (OrganizadorDep).
- `frontend/src/api/registro.ts` — interfaz `InscriptoDetalleDto` + función `listarInscriptosDetalle(torneoId)`.
- `frontend/src/components/organizador/InscriptosPanel.tsx` — reemplazar llamada a `listarInscriptos` + N×`fetchAtleta` por `listarInscriptosDetalle`.

**Nota de implementacion:**

El join inscripcion+atleta se hace en la capa de aplicacion consultando ambos repositorios. No es un JOIN SQL — es una composicion de dos queries en memoria. Para un torneo de hasta ~50 atletas (tamaño esperado en MVP) el overhead es despreciable.

El componente `InscriptosPanel` sigue consultando la grilla por disciplina para obtener el estado AP — esa lógica no cambia. Solo se elimina la carga N+1 de datos del atleta.

---

## Referencias

- Plan SP5: `docs/plans/sp5/PLAN-SP5.md §INC-5.5`
- Query existente: `src/registro/application/queries/listar_inscriptos.py`
- Repository ports: `src/registro/domain/ports/inscripcion_repository_port.py`, `src/registro/domain/ports/atleta_repository_port.py`
- Router Registro: `src/registro/api/router.py`
- Panel organizador: `frontend/src/components/organizador/InscriptosPanel.tsx`
- Página de detalle: `frontend/src/pages/organizador/DetalleTorneoPage.tsx`
- EstadoAPBadge: `frontend/src/components/organizador/EstadoAPBadge.tsx`

---

*Redactado: 2026-04-24 — INC-5.5 Inscripcion completa*
