---
title: "BC Registro — Supporting Domain"
type: arquitectura
last_updated: "2026-05-23"
sources:
  - docs/architecture/12-bc-registro.md
tipo_ddd: supporting
persistencia: CRUD
db: registro.db
test_coverage: 90
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

## Salud (BL-006 · v1.0.0 · 2026-05-16)

### ArchitectAnalyst

| Métrica | Valor | Severidad | Tendencia |
|---------|-------|-----------|-----------|
| Distancia (D) | 0.583 | **CRITICAL** | ↑ degradando |
| should_block | false | — | — |

D=0.583 supera el umbral de alerta. La degradación es explicada: SP-ADJ-11 incorporó las entidades `Juez` y `Organizador` con stack completo de infraestructura/aplicación, incrementando la inestabilidad del BC. Diferido para evaluación post-v1.0.

### DesignReviewer

| Total WARNING | Top smells |
|:---:|---|
| **37** | LongMethod (18) · FeatureEnvy (12) |

LongMethod en handlers de inscripción (reglas RF-IN-05/06 con múltiples ramas de validación). FeatureEnvy refleja la orquestación multi-BC de inscripción (Registro + Identidad). Sin CRITICAL.

### Cobertura

Tests de integración desde SP3. Cobertura `domain/` + `application/` ≥ 90%.
