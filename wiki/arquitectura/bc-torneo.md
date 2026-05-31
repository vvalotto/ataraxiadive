---
title: "BC Torneo — Supporting Domain"
type: arquitectura
last_updated: "2026-05-23"
sources:
  - docs/architecture/11-bc-torneo.md
l1_ref: "[[arquitectura/sistema]]"
tipo_ddd: supporting
persistencia: CRUD
db: torneo.db
test_coverage: null
componentes:
  - arquitectura/torneo/torneo-aggregate
  - arquitectura/torneo/sqlite-torneo-repository
  - arquitectura/torneo/command-handlers-torneo
  - arquitectura/torneo/query-handlers-torneo
  - arquitectura/torneo/router-torneo
---

# BC Torneo — Supporting Domain

## Rol

**Supporting Domain.** Modela el contenedor organizativo sobre el que se apoyan inscripción, ejecución deportiva, publicación de resultados y cierre del evento.

**Responsabilidades:** crear torneos, administrar el ciclo de vida, conservar datos de sede y entidad organizadora, habilitar operativamente la inscripción, proveer contexto read-only a otros BCs.

## Persistencia

CRUD sobre `torneo.db`. Tabla principal: `torneos`. El estado se actualiza por reemplazo de fila (`INSERT OR REPLACE`). Sin Event Sourcing.

`Sede` y `EntidadOrganizadora` se persisten embebidas en la fila del aggregate como JSON.

## Aggregate principal: Torneo

**Máquina de estados `EstadoTorneo`:**

```
CREADO → INSCRIPCION_ABIERTA → PREPARACION → EJECUCION → PREMIACION → CERRADO
                                                                    ↘ CANCELADO
```

**Invariantes:** nombre no vacío, fechas coherentes (inicio < fin), transiciones de estado válidas, acciones bloqueadas sobre torneo cerrado o cancelado.

## Value Objects

| VO | Descripción |
|----|-------------|
| `EstadoTorneo` | StrEnum; 7 estados posibles |
| `Sede` | nombre, ciudad, país |
| `EntidadOrganizadora` | nombre, tipo |

## Estructura de capas

| Capa | Responsabilidad |
|------|----------------|
| `api/` | Endpoints: crear, listar, obtener, transiciones de estado; `exception_handlers.py` → RFC 7807 |
| `application/` | `CrearTorneoHandler`, `ObtenerTorneoHandler`, `ListarTorneosHandler`, handlers de transición |
| `domain/` | Aggregate `Torneo`, `EstadoTorneo`, `Sede`, `EntidadOrganizadora`, `TorneoRepositoryPort` |
| `infrastructure/` | `SQLiteTorneoRepository` → `torneo.db` |

## Componentes (C4 L3)

| Componente | Capa | Tipo | Responsabilidad |
|---|---|---|---|
| [[arquitectura/torneo/torneo-aggregate\|Torneo Aggregate]] | domain | aggregate | Ciclo de vida completo del torneo: estados, transiciones, disciplinas, sede |
| [[arquitectura/torneo/sqlite-torneo-repository\|SQLiteTorneoRepository]] | infrastructure | repository | Persistencia CRUD del aggregate Torneo en torneo.db |
| [[arquitectura/torneo/command-handlers-torneo\|Command Handlers]] | application | handler | 9 handlers: CRUD + 7 transiciones de ciclo de vida + disciplinas/jueces |
| [[arquitectura/torneo/query-handlers-torneo\|Query Handlers]] | application | handler | 3 handlers: torneo por ID, lista de torneos, disciplinas por juez |
| [[arquitectura/torneo/router-torneo\|Router Torneo]] | api | router | API HTTP: CRUD + transiciones de estado + disciplinas y jueces |

## Integraciones de salida

| Destino | Mecanismo | Datos |
|---------|-----------|-------|
| [[registro]] | Evento `InscripcionHabilitada` | `torneoId`, `fechaFinInscripcion`, `disciplinasDisponibles` |
| [[resultados]] | Consulta read-only por `torneoId` | nombre, sede, fechas |
| [[notificaciones]] | Eventos de dominio | cierre, cancelación |

## Diferencias implementación actual vs. modelo de referencia

- `EntidadOrganizadora` y `Sede` son candidatos a catálogos CRUD propios (no implementado aún).
- `FormulaPuntos` y `VentanaImpugnacion` no forman parte del aggregate implementado.
- Los eventos de dominio para integración (`InscripcionHabilitada`) aún no están materializados en código.

## ADRs relacionados

- [[ADR-004-reglas-como-datos]] — `discipline_config` y `category_config` en `torneo.db`
- [[ADR-005-bounded-contexts-ddd-estrategico]] — posición en el mapa estratégico
- [[ADR-007-sqlite-persistencia-bc]] — persistencia CRUD en SQLite
- [[ADR-012-rfc7807-errores-http]] — exception handlers en la capa API

## Salud (BL-006 · v1.0.0 · 2026-05-16)

### ArchitectAnalyst

| Métrica | Valor | Severidad | Tendencia |
|---------|-------|-----------|-----------|
| Distancia (D) | 0.479 | WARNING | ↓ mejorando |
| should_block | false | — | — |

D=0.479 en zona de control. BC CRUD — la estabilidad es deseable por diseño DDD (alta abstracción, baja inestabilidad). Sin ciclos de dependencia.

### DesignReviewer

| Total WARNING | Top smells |
|:---:|---|
| **15** | FeatureEnvy (8) · LongMethod (2) |

El menor volumen WARNING de los BCs funcionales. FeatureEnvy estructural en los handlers que orquestan Torneo + Registro + Competencia (cross-BC por diseño). Sin CRITICAL.

### Cobertura

Tests de integración desde SP3. BC estable sin cambios arquitectónicos desde BL-003; sin US nueva desde SP-ADJ-07.

**UAT SP6 — flows que ejercen este BC:**
- F-02 Creación de torneo ✅
- F-05 Preparación de competencia (transición de estado) ✅
- F-10 Cierre de torneo ✅

**Nota:** % de cobertura numérico no disponible en BL-006 — pendiente de `pytest --cov` en próximo gate. Los 3 flows UAT pasaron sin waiver.
