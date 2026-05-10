# US-6.6.1: Endpoint público `GET /api/torneos`

**Estado**: `Pending`
**Incremento**: INC-6.6 — Portal Público
**Bounded Context**: `torneo`
**Capas afectadas**:
- `torneo/api/router.py`

---

## Descripción

Como **visitante del portal** (sin autenticación),
quiero **poder listar los torneos disponibles con sus datos básicos sin necesidad de login**
para **conocer el calendario de competencias y decidir si inscribirme**.

---

## Contexto

El endpoint `GET /torneos` existe y ya devuelve la lista de torneos. Sin embargo, no está explícitamente diseñado para consumo público:

- No hay documentación de que es público.
- No se filtran los torneos en estado `CANCELADO` (que no son relevantes para visitantes).
- La respuesta incluye todos los campos, pero conviene verificar que el contrato sea adecuado para el portal.

La decisión de diseño (PLAN-SP6 §3 INC-6.6): **Organizadores = Administradores** — sin rol Admin separado. Los torneos públicos son los creados por organizadores registrados.

---

## Especificación

### Tarea 1 — Verificar que el endpoint es verdaderamente público

| | |
|---|---|
| **Precondición** | `GET /torneos` existe en `torneo/api/router.py:185` |
| **Postcondición** | Confirmado que no existe middleware global de auth que requiera token |
| **Invariante** | No modificar la firma del endpoint |

Verificar en `src/app.py` y en el router que `listar_torneos()` no tiene ningún `Depends(get_current_user)` ni middleware global que exija JWT. Si existe algún middleware que aplica auth a todas las rutas, agregar excepción explícita para `GET /torneos`.

```bash
# Verificar ausencia de auth global
grep -n "middleware\|add_middleware\|HTTPBearer\|security" src/app.py
# Verificar que el endpoint no tiene Depends de auth
grep -A5 "def listar_torneos" src/torneo/api/router.py
```

### Tarea 2 — Filtrar torneos `CANCELADO` de la respuesta pública

| | |
|---|---|
| **Precondición** | `listar_torneos()` devuelve todos los torneos sin filtro |
| **Postcondición** | `GET /torneos` excluye torneos en estado `CANCELADO` |
| **Invariante** | Los otros endpoints del BC Torneo no se ven afectados; el organizador sigue viendo sus torneos cancelados en su panel privado |

El estado `CANCELADO` no tiene valor informativo para el visitante público. Filtrar en el handler o en el endpoint:

```python
# En listar_torneos():
torneos = await handler.handle(ListarTorneosQuery())
return [
    TorneoResponse.from_torneo(t) for t in torneos
    if t.estado.value != "CANCELADO"
]
```

> Alternativa: agregar parámetro `excluir_cancelados: bool = True` al query. Usar la opción más simple.

### Tarea 3 — Verificar contrato de respuesta para el portal

| | |
|---|---|
| **Precondición** | `TorneoResponse` definida en `router.py:121` |
| **Postcondición** | La respuesta incluye todos los campos necesarios para el portal público |
| **Invariante** | No romper contratos existentes (el organizador usa el mismo endpoint para su dashboard) |

Campos requeridos por el portal (verificar que ya existen en `TorneoResponse`):

| Campo | Propósito en el portal |
|-------|----------------------|
| `torneo_id` | clave para navegación |
| `nombre` | título de la tarjeta |
| `fecha_inicio` / `fecha_fin` | fechas de la competencia |
| `sede.ciudad` + `sede.pais` | ubicación |
| `estado` | determina acción contextual |
| `descripcion` | texto informativo |

Si `TorneoResponse` ya incluye todos estos campos (verificar en `router.py:121`), no es necesario ningún cambio de contrato.

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-6.6.1 — Endpoint público GET /api/torneos

  Scenario: Visitante lista torneos sin token
    Given el servidor está corriendo
    When se hace GET /api/torneos sin Authorization header
    Then la respuesta es 200 OK
    And el body es una lista de torneos

  Scenario: Torneos cancelados no aparecen en la lista pública
    Given existe un torneo en estado CANCELADO
    When se hace GET /api/torneos sin autenticación
    Then ese torneo no está en la respuesta

  Scenario: Respuesta incluye los campos del portal
    Given existen torneos en distintos estados (CREADO, INSCRIPCION_ABIERTA, EJECUCION)
    When se hace GET /api/torneos
    Then cada torneo en la respuesta incluye: torneo_id, nombre, fecha_inicio, fecha_fin, sede, estado, descripcion

  Scenario: Endpoint con auth sigue funcionando para el organizador
    Given un organizador autenticado
    When el frontend del organizador llama GET /api/torneos con su token
    Then la respuesta es idéntica a la llamada sin token (mismo contrato)
```

---

## Notas de implementación

- Si el endpoint ya es público (sin middleware global de auth), esta US es principalmente de verificación + filtro de cancelados — implementación mínima.
- El filtro de `CANCELADO` puede hacerse en el endpoint directamente (sin tocar el domain handler) para minimizar el impacto.
- El organizador tiene su propio panel que llama a este mismo endpoint con token — confirmar que el filtro no rompe su vista (los cancelados tampoco son útiles en su lista principal).

---

## Referencias

- Endpoint: `src/torneo/api/router.py:185` — `listar_torneos()`
- `TorneoResponse`: `src/torneo/api/router.py:121`
- `EstadoTorneo`: `src/torneo/domain/value_objects/estado_torneo.py`
- Plan: `docs/plans/sp6/PLAN-SP6.md` — §3 INC-6.6

---

*Redactado: 2026-05-10 — SP6 INC-6.6*
