---
title: "Registro — Router FastAPI"
type: arquitectura-componente
bc: registro
capa: api
tipo_componente: router
responsabilidad: "API HTTP del BC Registro: CRUD de perfiles (atleta/juez/organizador) + gestión de inscripciones y APs"
interfaces_out: []
adr_refs: [ADR-005, ADR-020]
last_updated: "2026-05-23"
sources:
  - src/registro/api/router.py
---

# Router — BC Registro

`APIRouter(prefix="/registro", tags=["registro"])`

---

## Endpoints — Atleta

| Método | Path | Auth | Handler | Descripción |
|--------|------|------|---------|-------------|
| `POST` | `/atletas` | `AtletaDep` | `RegistrarAtletaHandler` | Registra perfil atleta (201) |
| `GET` | `/atletas/me` | `AtletaDep` | `find_by_email` | Perfil del atleta autenticado |
| `PATCH` | `/atletas/me` | `AtletaDep` | `ActualizarAtletaHandler` | Actualiza datos propios |
| `GET` | `/atletas/{atleta_id}` | público | `ObtenerAtletaHandler` | Perfil por ID |

---

## Endpoints — Juez

| Método | Path | Auth | Handler | Descripción |
|--------|------|------|---------|-------------|
| `POST` | `/jueces` | `JuezDep` | `RegistrarJuezHandler` | Registra perfil juez (201) |
| `GET` | `/jueces/me` | `JuezDep` | `ObtenerJuezHandler` | Perfil del juez autenticado |
| `PATCH` | `/jueces/me` | `JuezDep` | `ActualizarJuezHandler` | Actualiza licencia/federación |

---

## Endpoints — Organizador

| Método | Path | Auth | Handler | Descripción |
|--------|------|------|---------|-------------|
| `POST` | `/organizadores` | `OrganizadorDep` | `RegistrarOrganizadorHandler` | Registra perfil organizador (201) |
| `GET` | `/organizadores/me` | `OrganizadorDep` | `ObtenerOrganizadorHandler` | Perfil del organizador autenticado |
| `PATCH` | `/organizadores/me` | `OrganizadorDep` | `ActualizarOrganizadorHandler` | Actualiza nombre organización (PATCH semántico: `None` en el JSON borra el campo) |

---

## Endpoints — Inscripción

| Método | Path | Auth | Handler | Descripción |
|--------|------|------|---------|-------------|
| `POST` | `/inscripciones` | `AtletaDep` | `InscribirAtletaHandler` | Inscribe atleta en torneo (201) |
| `DELETE` | `/inscripciones/{id}` | `AtletaDep` | `CancelarInscripcionHandler` | Cancela inscripción |
| `GET` | `/torneos/{id}/inscriptos` | `OrganizadorDep` | `ListarInscriptosHandler` | Lista inscriptos del torneo |
| `GET` | `/atletas/{id}/inscripciones` | `AtletaDep` | directo repo | Inscripciones del atleta |
| `GET` | `/torneos/{id}/inscriptos-info` | público | directo repo | Nombre y club (sin auth) |
| `GET` | `/torneos/{id}/inscriptos-detalle` | `OrganizadorDep` | directo repo | Con APs declarados |
| `GET` | `/inscripciones/{id}/ap` | autenticado | directo repo | AP de disciplina específica |
| `PUT` | `/inscripciones/{id}/ap` | autenticado | `DeclararAPInscripcionHandler` | Declara AP para disciplina |

---

## Endpoints — Adjuntos

| Método | Path | Auth | Descripción |
|--------|------|------|-------------|
| `POST` | `/inscripciones/{id}/apto-medico` | `AtletaDep` | Sube archivo apto médico (máx 10 MB) |
| `POST` | `/inscripciones/{id}/constancia-pago` | `AtletaDep` | Sube constancia de pago (máx 10 MB) |

---

## Mecanismos especiales

**Callback de notificaciones**: `configure_inscripcion_notificaciones(callback)` — BC Notificaciones inyecta un callback que se dispara después de una inscripción exitosa. El router lo llama dentro de `InscribirAtletaHandler`; si falla, se silencia (best-effort).

**Precondición de cierre**: `build_cierre_inscripcion_precondition()` — retorna una función async que BC Torneo invoca antes de cerrar el período de inscripción. Usa `VerificarCompletitudAPHandler` para verificar que todos los atletas tienen APs completos.

**PATCH semántico en Organizador**: `ActualizarOrganizadorMeRequest` usa `model_fields_set` para distinguir "campo no enviado" (preservar valor) de "campo enviado como null" (borrar). Evita borrados accidentales.

## Relaciones

**Contenedor:** [[arquitectura/registro]]

- Usa [[command-handlers-registro]] y [[query-handlers-registro]]
- Instancia repositorios de [[sqlite-repositories-registro]] via funciones helper `_repo()`, etc.
- Usa [[torneo-consulta-port]] (SQLiteTorneoConsulta) para validaciones de inscripción
- Auth guards: `AtletaDep`, `JuezDep`, `OrganizadorDep` definidos en `shared/api/dependencies.py`

## Código fuente

| Archivo | Descripción |
|---|---|
| `src/registro/api/router.py` | Router FastAPI — endpoints HTTP del BC |
