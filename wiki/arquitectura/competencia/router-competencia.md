---
title: "Competencia — Router FastAPI"
type: arquitectura-componente
bc: competencia
capa: api
tipo_componente: router
responsabilidad: "Endpoints HTTP del BC Competencia: interfaz del juez y del organizador para grilla y ejecución"
interfaces_out:
  - CommandHandlers
  - QueryHandlers
adr_refs: [ADR-002, ADR-012]
last_updated: "2026-05-23"
sources:
  - src/competencia/api/router.py
  - src/competencia/api/schemas.py
  - src/competencia/api/dependencies.py
  - src/competencia/api/exception_handlers.py
us_origen:
  - US-2.0-exception-management-cross-bc
  - US-2.2.2-api-disciplina-aware-validacion-de-unidades
  - US-ADJ-1.4-refactoring-api-dip-en-router-p-08-a-composition-root
  - US-ADJ-1.5-refactoring-api-srp-router-en-schemas-py-dependencies
  - US-ADJ-2.8-refactoring-api-dip-fix-event-store-dep-tipado-como
  - US-ADJ-6.7-uat-sp4-inc-4-4-4-5-4-6-bug-sp4-001-002-ux-fixes
  - US-ADJ-7.2-bug-sp4-004-exponer-tarjeta-asignada-en-grilla
---

# Router FastAPI — BC Competencia

## Responsabilidad

Capa de entrada HTTP del BC. Expone endpoints para el panel del juez (ejecución de competencia) y el panel del organizador (gestión de grilla). Traduce requests HTTP → Commands/Queries, invoca handlers y retorna responses con schemas Pydantic.

## Grupos de endpoints

### Gestión de grilla (Organizador)

| Método | Path | Handler |
|--------|------|---------|
| `POST` | `/competencias/{id}/intervalo-ot` | `ConfigurarIntervaloOTHandler` |
| `POST` | `/competencias/{id}/generar-grilla` | `GenerarGrillaHandler` |
| `PATCH` | `/competencias/{id}/ajustar-grilla` | `AjustarGrillaHandler` |
| `POST` | `/competencias/{id}/confirmar-grilla` | `ConfirmarGrillaHandler` |
| `POST` | `/competencias/{id}/asignar-juez-performance` | `AsignarJuezPerformanceHandler` |

### Ejecución (Juez)

| Método | Path | Handler |
|--------|------|---------|
| `POST` | `/competencias/{id}/iniciar` | `IniciarCompetenciaHandler` |
| `POST` | `/competencias/{id}/llamar-atleta` | `LlamarAtletaHandler` |
| `POST` | `/performances/{id}/resultado` | `RegistrarResultadoHandler` |
| `POST` | `/performances/{id}/dns` | `RegistrarDNSHandler` |
| `POST` | `/performances/{id}/tarjeta` | `AsignarTarjetaHandler` |
| `POST` | `/performances/{id}/resolver-revision` | `ResolverRevisionHandler` |
| `POST` | `/performances/{id}/corregir` | `CorregirResultadoHandler` |
| `POST` | `/performances/{id}/corregir-tras-dns` | `CorregirResultadoTrasDNSHandler` |
| `POST` | `/competencias/{id}/finalizar` | `FinalizarCompetenciaManualHandler` |

### Consultas (Read)

| Método | Path | Handler |
|--------|------|---------|
| `GET` | `/competencias/{id}/grilla` | `ObtenerGrillaHandler` |
| `GET` | `/competencias/{id}/estado` | `ObtenerEstadoCompetenciaHandler` |
| `GET` | `/competencias/{id}/progreso` | `ObtenerProgresoHandler` |
| `GET` | `/competencias/{id}/performance-actual` | `ObtenerPerformanceActualHandler` |
| `GET` | `/competencias/{id}/proximas-performances` | `ObtenerProximasPerformancesHandler` |
| `GET` | `/torneos/{id}/competencias` | `ObtenerCompetenciasPorTorneoHandler` |

## Autorización

Guards via `shared/api/dependencies.py`: `JuezDep` (endpoints de ejecución), `OrganizadorDep` (gestión de grilla). Conformist sobre [[ADR-020-modelo-usuarios-roles]] / [[ADR-019-politica-contrasenas]].

## Manejo de errores

`exception_handlers.py` mapea excepciones de dominio a respuestas RFC 7807 (ADR-012).

## Relaciones

**Contenedor:** [[arquitectura/competencia]]

## Código fuente

| Archivo | Descripción |
|---|---|
| `src/competencia/api/router.py` | Router FastAPI — endpoints HTTP del BC |
| `src/competencia/api/schemas.py` | Schemas Pydantic — request/response |
| `src/competencia/api/dependencies.py` | Guards de rol: JuezDep, OrganizadorDep |
| `src/competencia/api/exception_handlers.py` | Mapeo excepciones → RFC 7807 |

## ADRs relacionados

- [[ADR-002-fastapi-backend]] — FastAPI como framework
- [[ADR-012-rfc7807-errores-http]] — formato de errores HTTP
