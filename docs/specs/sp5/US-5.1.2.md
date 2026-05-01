# US-5.1.2: Gestión de fases del torneo — botones de transición con validaciones

**Estado**: `To Do`
**Sprint**: SP5 — La Puesta en Marcha
**Incremento**: INC-5.1
**Bounded Context**: `frontend` (consume `torneo/api/` — endpoints existentes)
**Capas afectadas**: `frontend/src/pages/organizador/`, `frontend/src/api/torneo.ts`

---

## Descripción

Como **organizador**,
quiero **ver el estado actual de mi torneo y transicionarlo a la siguiente fase con un botón**
para **controlar el ciclo de vida del torneo respetando las restricciones del dominio**.

---

## Contexto del dominio

### Modelo involucrado

| Elemento | Nombre | Responsabilidad |
|---|---|---|
| Aggregate | `Torneo` | Estado: Creado → Inscripcion → Preparacion → EnEjecucion → Premiacion → Cerrado / Cancelado |
| Página | `DetalleTorneo` | Pantalla principal del organizador — cabecera con estado + acciones disponibles |
| Componente | `FaseBadge` | Badge visual del estado actual del torneo |
| Componente | `AccionesPanel` | Botones de transición disponibles para el estado actual |

### Lenguaje ubicuo relevante

- **Fase:** estado del ciclo de vida del torneo (Creado, Inscripcion, Preparacion, EnEjecucion, Premiacion, Cerrado, Cancelado).
- **Transición:** cambio de estado del torneo — cada fase habilita un conjunto de acciones distintas.
- **Volver a Preparación:** retroceso permitido desde EnEjecucion → Preparacion (para corregir configuración).
- **Cancelado:** estado terminal alcanzable desde cualquier fase activa.

---

## Especificación del comportamiento

### Invariantes

- **INV-5.1.2-01:** Solo se muestran los botones de transición válidos para el estado actual — el backend define la validez; la UI no duplica la lógica de transición.
- **INV-5.1.2-02:** El botón "Cancelar torneo" aparece en todo estado que no sea `Cerrado` ni `Cancelado`.
- **INV-5.1.2-03:** Después de cada transición exitosa, la UI recarga el detalle del torneo para reflejar el nuevo estado.
- **INV-5.1.2-04:** Si el backend devuelve 409, la UI muestra el mensaje de error del backend sin recargar.

### Mapa de transiciones y endpoints

| Estado actual | Acción disponible | Endpoint |
|---|---|---|
| `Creado` | Abrir inscripción | `PUT /torneos/{id}/abrir-inscripcion` |
| `Inscripcion` | Cerrar inscripción → Preparación | `PUT /torneos/{id}/cerrar-inscripcion` |
| `Preparacion` | Iniciar ejecución | `PUT /torneos/{id}/iniciar-ejecucion` |
| `EnEjecucion` | Volver a Preparación | `PUT /torneos/{id}/volver-preparacion` |
| `EnEjecucion` | Iniciar premiación | `PUT /torneos/{id}/iniciar-premiacion` |
| `Premiacion` | Cerrar torneo | `PUT /torneos/{id}/cerrar` |
| Cualquier activo | Cancelar torneo | `PUT /torneos/{id}/cancelar` |

**Ejemplo concreto:**

```
Precondición:  Torneo T1 en estado Inscripcion
Operación:     PUT /torneos/T1/cerrar-inscripcion
               → 200 { ok: true }
Postcondición: Torneo T1 pasa a estado Preparacion.
               La UI oculta "Cerrar inscripción" y muestra "Iniciar ejecución".
               El tab de inscriptos queda visible (read-only).
```

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-5.1.2 — Transiciones de fase del torneo

  Background:
    Given el organizador "org@ataraxia.com" está autenticado con rol ORGANIZADOR
    And existe el torneo "BA 2026" con id T1

  Scenario: torneo en Creado — solo muestra "Abrir inscripción"
    Given el torneo T1 está en estado Creado
    When el organizador accede a /organizador/torneo/T1
    Then ve el badge de estado "Creado"
    And ve el botón "Abrir inscripción"
    And no ve botones de otras transiciones (excepto "Cancelar")

  Scenario: transición exitosa Creado → Inscripcion
    Given el torneo T1 está en estado Creado
    When el organizador toca "Abrir inscripción"
    Then el backend recibe PUT /torneos/T1/abrir-inscripcion
    And la UI recarga el torneo
    And el badge de estado cambia a "Inscripcion"
    And aparece el botón "Cerrar inscripción"

  Scenario: transición EnEjecucion → Preparacion (retroceso permitido)
    Given el torneo T1 está en estado EnEjecucion
    When el organizador toca "Volver a Preparación"
    Then el backend recibe PUT /torneos/T1/volver-preparacion
    And el badge cambia a "Preparacion"

  Scenario: cancelar torneo desde cualquier estado activo
    Given el torneo T1 está en estado Preparacion
    When el organizador toca "Cancelar torneo"
    Then aparece un diálogo de confirmación "¿Cancelar torneo BA 2026? Esta acción no se puede deshacer."
    When confirma la cancelación
    Then el backend recibe PUT /torneos/T1/cancelar
    And el badge cambia a "Cancelado"
    And todos los botones de transición desaparecen

  Scenario: error del backend muestra mensaje sin recargar
    Given el torneo T1 está en estado Preparacion
    And el backend devuelve 409 al intentar iniciar ejecución
    When el organizador toca "Iniciar ejecución"
    Then la UI muestra el mensaje de error del backend
    And el estado del torneo no cambia en la pantalla

  Scenario: torneo Cerrado o Cancelado no muestra botones de transición
    Given el torneo T1 está en estado Cerrado
    When el organizador accede a /organizador/torneo/T1
    Then no ve ningún botón de transición de fase
    And ve el badge de estado "Cerrado"
```

---

## Impacto arquitectónico

- [x] No — consume endpoints existentes (todos los `PUT /torneos/{id}/*` ya implementados).

**Capa(s) afectadas:**
- [x] Frontend — nueva página `DetalleTorneo` con tabs: Detalle / Inscriptos / Grilla / Ejecución
- [x] Frontend — componentes `FaseBadge`, `AccionesPanel`
- [x] Frontend — `api/torneo.ts`: agregar funciones de transición de fase

---

## Referencias

- Endpoints backend: `src/torneo/api/router.py` líneas 155–194 (todos los handlers de transición)
- Plan SP5: `docs/plans/sp5/PLAN-SP5.md §INC-5.1`

---

## Notas de implementación

- **Página `DetalleTorneo`:** estructura con tabs — Detalle (nombre/sede/fechas), Inscriptos (US-5.1.3), Grilla (US-5.1.4), Jueces (US-5.1.5), Ejecución (US-5.1.6). Cada tab se activa según la fase del torneo.
- **`AccionesPanel`:** mapa de estado → botones disponibles definido en el componente (no llama al backend para determinar acciones válidas — la tabla de transiciones es fija del dominio FAAS).
- **Ruta:** `/organizador/torneo/:torneoId` — parametrizada, con guardia de rol ORGANIZADOR.
- **Confirmación de cancelación:** usar un `Dialog` modal — acción irreversible visible para el usuario.
- **Refresco de estado:** después de cada transición exitosa, hacer `GET /torneos/{id}` y actualizar el store.

---

*Redactado: 2026-04-20 — INC-5.1 Panel del Organizador*
