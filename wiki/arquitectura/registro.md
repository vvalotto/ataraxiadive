---
title: "BC Registro — Supporting Domain"
type: arquitectura
last_updated: "2026-05-20"
sources:
  - docs/architecture/12-bc-registro.md
tipo_ddd: Supporting Domain
persistencia: CRUD
db: registro.db
---

# BC Registro — Supporting Domain

## Rol

**Supporting Domain.** Modela la información personal del atleta y su participación en un torneo específico.

**Responsabilidades:** registrar atletas, validar datos personales, crear y cancelar inscripciones, impedir duplicados y ventanas fuera de plazo, exponer listados de inscriptos, actuar como fuente upstream de datos para Competencia.

## Persistencia

CRUD sobre `registro.db`. Tablas: `atletas`, `inscripciones`. Sin Event Sourcing.

Con ADR-020 también incluirá: `jueces`, `organizadores` (perfiles de rol extendidos).

## Aggregates principales

### Atleta

Invariantes: nombre y apellido no vacíos, email con formato válido, fecha de nacimiento en el pasado. Conserva categoría (autodeclarada) y brevet.

### Inscripcion

Modela la participación de un atleta en un torneo. Invariantes: atleta y torneo existen, torneo abierto para inscripción, sin duplicados, cancelación solo antes de la fecha de inicio del torneo.

**Estados:** `ACTIVA`, `CANCELADA`

## Value Objects

| VO | Descripción |
|----|-------------|
| `Categoria` | StrEnum — movido a `shared/` en ADR-022 |
| `EstadoInscripcion` | `ACTIVA` / `CANCELADA` |

## Estructura de capas

| Capa | Responsabilidad |
|------|----------------|
| `api/` | Endpoints atleta e inscripción; serialización JSON; mapeo de errores |
| `application/` | `RegistrarAtletaHandler`, `ObtenerAtletaHandler`, `InscribirAtletaHandler`, `CancelarInscripcionHandler`, `ListarInscriptosHandler` |
| `domain/` | `Atleta`, `Inscripcion`, `Categoria`, `EstadoInscripcion`, `TorneoConsultaPort`, puertos de repo |
| `infrastructure/` | `SQLiteAtletaRepository`, `SQLiteInscripcionRepository`, `SQLiteTorneoConsulta` (ACL read-only → `torneo.db`) |

## Integración de entrada: Torneo

`TorneoConsultaPort` → `SQLiteTorneoConsulta`: lectura read-only sobre `torneo.db` para verificar que el torneo está abierto, obtener fecha de inicio y disciplinas disponibles. El acoplamiento de infraestructura queda contenido en el ACL.

## Integración de salida: Competencia

**Actual:** Referencias `participante_id` / `atleta_id` en streams de Competencia. `AtletaNombreAdapter` en Competencia consulta `registro.db` para datos descriptivos.

**Objetivo:** Evento `AtletaInscripto` + ACL en Competencia que traduce `Atleta` → `Participante`.

## Integraciones adicionales

- **Notificaciones:** Emite `InscripcionConfirmada` (policy P-10) — email al atleta.
- **Identidad:** Conformist — valida JWT en cada request.

## Diferencias implementación actual vs. modelo de referencia

- Eventos de salida (`AtletaRegistrado`, `AtletaInscripto`, `InscripcionCancelada`) no materializados en código.
- Consulta de disciplinas del torneo devuelve todas como solución transitoria.
- Perfiles extendidos (`Juez`, `Organizador`) incorporados en ADR-020 (SP6+).

## ADRs relacionados

- [[ADR-005-bounded-contexts-ddd-estrategico]] — posición en el mapa estratégico
- [[ADR-007-sqlite-persistencia-bc]] — persistencia CRUD en SQLite
- [[ADR-020-modelo-usuarios-roles]] — perfiles Juez y Organizador en este BC
- [[ADR-022-categoria-shared]] — `Categoria` movida a `shared/`
