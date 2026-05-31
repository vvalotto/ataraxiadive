---
title: "Torneo — Router FastAPI"
type: arquitectura-componente
bc: torneo
capa: api
tipo_componente: router
responsabilidad: "API HTTP del BC Torneo: CRUD de torneos + 7 endpoints de transición de estado + disciplinas y jueces"
interfaces_out: []
adr_refs: [ADR-005]
last_updated: "2026-05-23"
sources:
  - src/torneo/api/router.py
us_origen:
  - US-3.1.2-api-rest-torneo-crud-transiciones-repositorio-sq-lite
  - US-6.6.1-endpoint-publico-get-torneos-sin-autenticacion
  - US-ADJ-8.1-sp-adj-08-ux-paneles-organizador-post-uat-inc-5-2
tests:
  - tests/features/US-3.1.2-api-rest-torneo.feature
  - tests/integration/torneo/test_sqlite_torneo_repository.py
  - tests/features/US-6.6.1-endpoint-publico-torneos.feature
  - tests/integration/torneo/test_torneos_publicos_api.py
  - tests/features/US-ADJ-8.1-claridad-operativa-panel-organizador.feature
---

# Router — BC Torneo

`APIRouter(prefix="/torneos", tags=["torneos"])`

---

## Endpoints — CRUD

| Método | Path | Auth | Handler | Descripción |
|--------|------|------|---------|-------------|
| `POST` | `/torneos` | `OrganizadorDep` | `CrearTorneoHandler` | Crea torneo (201) |
| `GET` | `/torneos` | público | `ListarTorneosHandler` | Lista torneos — filtra CANCELADO |
| `GET` | `/torneos/{id}` | público | `ObtenerTorneoHandler` | Torneo por ID |
| `PUT` | `/torneos/{id}` | `OrganizadorDep` | `ActualizarTorneoHandler` | Actualiza datos (CREADO o INSCRIPCION_ABIERTA) |

---

## Endpoints — Ciclo de vida

| Método | Path | Auth | Transición | Precondición externa |
|--------|------|------|-----------|----------------------|
| `PUT` | `/{id}/abrir-inscripcion` | `OrganizadorDep` | CREADO → INSCRIPCION_ABIERTA | — |
| `PUT` | `/{id}/cerrar-inscripcion` | `OrganizadorDep` | INSCRIPCION_ABIERTA → PREPARACION | BC Registro: APs completos |
| `PUT` | `/{id}/iniciar-ejecucion` | `OrganizadorDep` | PREPARACION → EJECUCION | BC Competencia: grilla lista |
| `PUT` | `/{id}/volver-preparacion` | `OrganizadorDep` | EJECUCION → PREPARACION | — |
| `PUT` | `/{id}/iniciar-premiacion` | `OrganizadorDep` | EJECUCION → PREMIACION | BC Competencia: resultados completos |
| `PUT` | `/{id}/cerrar` | `OrganizadorDep` | PREMIACION → CERRADO | — |
| `PUT` | `/{id}/cancelar` | `OrganizadorDep` | cualquier → CANCELADO | — |

---

## Endpoints — Disciplinas y Jueces

| Método | Path | Auth | Descripción |
|--------|------|------|-------------|
| `PUT` | `/{id}/disciplinas` | `OrganizadorDep` | Asigna disciplinas al torneo (reemplaza lista) |
| `PUT` | `/{id}/disciplinas/{disc}/juez` | `OrganizadorDep` | Asigna juez a disciplina específica |
| `GET` | `/{id}/disciplinas` | público | Lista disciplinas con jueces asignados |
| `GET` | `/{id}/jueces/{juez_id}/disciplinas` | público | Disciplinas asignadas a un juez |

---

## Precondiciones y post-acciones globales

El router expone 4 funciones de configuración que permiten inyectar callbacks desde `app.py`:

```python
configure_cierre_inscripcion_precondition(fn)  # BC Registro: verificar APs
configure_ejecucion_precondition(fn)            # BC Competencia: grilla generada
configure_ejecucion_post_action(fn)             # BC Competencia: inicializar competencia
configure_premiacion_precondition(fn)           # BC Competencia: validar finalización
```

Este patrón mantiene BC Torneo ignorante de los otros BCs: sólo conoce firmas `Callable[[UUID], Awaitable[None]]`.

---

## Relaciones

**Contenedor:** [[arquitectura/torneo]]

- Usa [[command-handlers-torneo]] y [[query-handlers-torneo]]
- Instancia [[sqlite-torneo-repository]] via `_repo()`
- Auth guard: `OrganizadorDep` de `shared/api/dependencies.py`
- Las precondiciones/post-acciones son provistas por [[router-registro]] y BC Competencia al inicializar `app.py`

## Código fuente

| Archivo | Descripción |
|---|---|
| `src/torneo/api/router.py` | Router FastAPI — endpoints HTTP del BC |
