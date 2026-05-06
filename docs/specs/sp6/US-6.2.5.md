# US-6.2.5: Nuevo Torneo — Selección de Grupos Etarios JUNIOR/SENIOR/MASTER

**Estado**: `Done`
**Incremento**: INC-6.2 — Ajustes Organizador  
**Hallazgos**: UI-ORG-07  
**Bounded Context**: `torneo` · `frontend`  
**Capas afectadas**: `frontend/pages/organizador/CrearTorneoPage.tsx`, `src/torneo/api/router.py`, `src/torneo/domain/`

---

## Descripción

Como **organizador creando un torneo**,
quiero **seleccionar qué grupos etarios participan (JUNIOR / SENIOR / MASTER)**
para **que el sistema sepa desde el inicio qué categorías habilitar en inscripción y rankings**.

---

## Contexto del Hallazgo

### UI-ORG-07 — Formulario de nuevo torneo sin selección de categorías

**Ubicación**: `frontend/src/pages/organizador/CrearTorneoPage.tsx`

El formulario de creación no tiene campo para categorías. Los seis valores posibles del enum `Categoria` son combinaciones de grupo etario (JUNIOR, SENIOR, MASTER) y género (MASCULINO, FEMENINO). Para el organizador tiene más sentido seleccionar los **grupos** (JUNIOR, SENIOR, MASTER) — el género resulta del registro del atleta.

---

## Fuente de verdad UX

- `docs/design/ux/wireframes-organizador.md` — estructura aprobada del portal organizador y criterios visuales del formulario de torneo.
- `docs/design/ux/prototipos/prototipo-organizador.html` — prototipo navegable aprobado para el rol organizador.
- `docs/plans/sp6/PLAN-SP6.md` — hallazgo UI-ORG-07 detectado en validación SP5.
- `frontend/src/pages/organizador/CrearTorneoPage.tsx` — implementación React actual comparada contra el hallazgo.

---

## Especificación

### Tarea 1: Campo multi-select de grupos en CrearTorneoPage

| | |
|---|---|
| **Precondición** | El formulario no tiene campo de categorías; el payload de creación tampoco lo incluye |
| **Postcondición** | El formulario tiene un campo multi-select con opciones: JUNIOR, SENIOR, MASTER. Al menos uno debe estar seleccionado para poder enviar el formulario |
| **Invariante** | Si el usuario no selecciona ninguno, el botón "Crear torneo" permanece deshabilitado o muestra un mensaje de validación |

```typescript
const GRUPOS_ETARIOS = ['JUNIOR', 'SENIOR', 'MASTER'] as const
type GrupoEtario = typeof GRUPOS_ETARIOS[number]

// Estado local:
const [gruposSeleccionados, setGruposSeleccionados] = useState<GrupoEtario[]>(['SENIOR'])

// Toggle:
function toggleGrupo(grupo: GrupoEtario) {
  setGruposSeleccionados((prev) =>
    prev.includes(grupo) ? prev.filter((g) => g !== grupo) : [...prev, grupo]
  )
}
```

UI sugerida: tres botones tipo toggle pill (igual al estilo de filtros ya existentes en el proyecto).

### Tarea 2: Incluir grupos en el payload de creación

| | |
|---|---|
| **Precondición** | El payload `POST /torneos` no incluye campo de categorías |
| **Postcondición** | El payload incluye `"grupos_etarios": ["SENIOR", "MASTER"]` (o los seleccionados) |
| **Invariante** | El campo es requerido — el endpoint rechaza payloads sin `grupos_etarios` o con lista vacía |

### Tarea 3: Backend — agregar `grupos_etarios` al torneo

| | |
|---|---|
| **Precondición** | La entidad `Torneo` (o su DTO de creación) no tiene campo de categorías |
| **Postcondición** | `POST /torneos` acepta y persiste `grupos_etarios: list[str]` con valores válidos (JUNIOR, SENIOR, MASTER). `GET /torneos/{id}` incluye el campo en la respuesta |
| **Invariante** | Lista vacía es error de validación 422. Valores fuera del enum son error 422. El campo no afecta ninguna otra lógica de dominio en este incremento |

Alcance acotado: solo persistir y retornar el campo. No impactar ni filtrar inscripciones ni rankings en esta US (esa integración queda fuera de scope SP6 salvo que se especifique en INC posterior).

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-6.2.5 — Selección de categorías en nuevo torneo

  Scenario: El formulario tiene selector de grupos etarios
    Given el organizador abre "Nuevo torneo"
    Then ve tres opciones: JUNIOR, SENIOR, MASTER
    And SENIOR está seleccionado por defecto

  Scenario: No se puede crear sin seleccionar al menos un grupo
    Given el organizador deselecciona todos los grupos
    Then el botón "Crear torneo" está deshabilitado

  Scenario: El torneo creado persiste los grupos seleccionados
    Given el organizador selecciona JUNIOR y MASTER
    When crea el torneo exitosamente
    Then el endpoint GET /torneos/{id} retorna grupos_etarios=["JUNIOR","MASTER"]

  Scenario: Payload sin grupos_etarios es rechazado
    Given un cliente que envía POST /torneos sin grupos_etarios
    Then el servidor retorna 422
```

---

## Notas de implementación

- La integración con inscripción/rankings (validar que el atleta pertenece a un grupo habilitado) está **fuera de scope** de esta US — solo persistir el dato
- `grupos_etarios` quedó modelado en el dominio `Torneo` con value object propio `GrupoEtario` para evitar acoplamiento directo con `registro.domain.value_objects.Categoria`
- Migración SQLite: agregar columna `grupos_etarios TEXT NOT NULL DEFAULT '["SENIOR"]'`

---

## Referencias

- Hallazgo: `docs/plans/sp6/PLAN-SP6.md` — UI-ORG-07
- Página: `frontend/src/pages/organizador/CrearTorneoPage.tsx`
- Enum: `src/registro/domain/value_objects/categoria.py`
- Router torneo: `src/torneo/api/router.py`

---

## Resultado de implementación

- `POST /torneos` requiere `grupos_etarios` y valida `JUNIOR`, `SENIOR`, `MASTER`.
- `GET /torneos` y `GET /torneos/{id}` retornan `grupos_etarios` en orden determinístico.
- La persistencia SQLite migra torneos existentes con default `["SENIOR"]`.
- La pantalla de alta de torneo muestra toggles para los tres grupos etarios con `SENIOR` seleccionado por defecto.
- La validación impide enviar el formulario sin al menos un grupo etario.

---

*Redactado: 2026-05-05 — SP6 INC-6.2*
