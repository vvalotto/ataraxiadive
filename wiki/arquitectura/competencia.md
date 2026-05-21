---
title: "BC Competencia — Core Domain"
type: arquitectura
last_updated: "2026-05-20"
sources:
  - docs/architecture/10-bc-competencia.md
tipo_ddd: Core Domain
persistencia: Event Sourcing
db: competencia.db
---

# BC Competencia — Core Domain

## Rol

**Core Domain** del sistema. Modela la ejecución deportiva de una competencia de apnea. Concentra la mayor densidad de lógica de negocio y el mayor rigor regulatorio.

**Responsabilidades:** configurar y gestionar la competencia por disciplina, generar y ajustar la grilla, administrar el ciclo de vida, registrar anuncios y resultados, asignar tarjetas, registrar DNS, preservar trazabilidad completa de acciones del juez.

## Persistencia

Event Sourcing sobre `competencia.db`. La fuente de verdad es la secuencia de eventos de cada aggregate. El estado se reconstruye por replay. Las consultas se resuelven contra proyecciones en el mismo archivo SQLite.

**Streams:**
- `competencia-{competencia_id}` — aggregate Competencia
- `performance-{performance_id}` — aggregate Performance

## Aggregates principales

### Competencia

Responsable de: configurar intervalos, generar/ajustar/confirmar grilla, iniciar y finalizar la competencia. Preserva invariantes del ciclo de vida.

### Performance

Responsable de: registrar AP, registrar resultado, asignar tarjeta, registrar DNS, corregir resultados con trazabilidad explícita (las correcciones no mutan estado previo — agregan nuevos eventos).

### Referencia a participante

No existe entidad `Participante` materializada. El BC opera con `participante_id` / `atleta_id` como referencias estables en streams, eventos, queries y read models. Los datos descriptivos (nombre) se obtienen vía `AtletaNombrePort`.

## Estructura de capas

| Capa | Responsabilidad |
|------|----------------|
| `api/` | Endpoints HTTP; validación de entrada; traducción a comandos |
| `application/` | Handlers de comandos y queries; orquestación de aggregates |
| `domain/` | Aggregates, value objects, eventos, puertos — sin dependencias de FastAPI/SQLite |
| `infrastructure/` | Event store, repositorios, proyecciones, adaptadores de integración |

## Handlers de aplicación (referencia)

**Competencia:** `GenerarGrillaHandler`, `AjustarGrillaHandler`, `ConfirmarGrillaHandler`, `IniciarCompetenciaHandler`, `FinalizarCompetenciaHandler`

**Performance:** `RegistrarAPHandler`, `LlamarAtletaHandler`, `RegistrarResultadoHandler`, `AsignarTarjetaHandler`, `RegistrarDNSHandler`, `CorregirResultadoHandler`

## Integraciones

### Entrada desde Registro

- Referencias por `atleta_id` / `participante_id`
- `AtletaNombrePort` → `AtletaNombreAdapter` → `registro.db`

### Salida hacia Resultados

- Evento `CompetenciaFinalizada` — fuente de verdad deportiva para cálculo de ranking

### Salida hacia Notificaciones

- Eventos de dominio que disparan comunicaciones downstream (callbacks in-process en SP4)

## Servicios de dominio

- `CalculadorHashCompetencia` — calcula hash SHA-256 de la secuencia canónica de eventos al cerrar una disciplina ([[ADR-018-hash-sha256-auditoria]])

## Restricciones arquitectónicas

- El dominio no depende de FastAPI, SQLite ni librerías externas.
- Las correcciones no mutan estado previo — agregan eventos.
- Competencia no consulta directamente la DB de Registro.
- El read model no es fuente de verdad; deriva del event store.

## ADRs que gobiernan este BC

- [[ADR-001-event-sourcing-competencia]] — justificación del ES; flujo de eventos
- [[ADR-008-event-store-sqlite]] — esquema de la tabla events; concurrencia optimista
- [[ADR-014-penalizaciones-acumulables]] — `BlancaConPenalizaciones`; `rp_medido` / `rp_penalizado`
- [[ADR-018-hash-sha256-auditoria]] — hash SHA-256 en `CompetenciaCerrada`
- [[ADR-006-estructura-bc-first]] — organización hexagonal por capas

## Salud (BL-006 · v1.0.0 · 2026-05-16)

### ArchitectAnalyst

| Métrica | Valor | Severidad | Tendencia |
|---------|-------|-----------|-----------|
| Distancia (D) | 0.459 | WARNING | ↓ mejorando |
| DependencyCycle | `domain/aggregates` ↔ `domain/aggregates/performance` | CRITICAL | = estable |
| should_block | false | — | — |

D=0.459 está en zona de control (< 0.5). El ciclo ADP en `domain/aggregates` fue auditado en INC-6.4 (US-6.4.1) y clasificado como aceptable por la estructura del aggregate. No bloquea.

### DesignReviewer

| Total WARNING | Top smells |
|:---:|---|
| **130** | LongMethod (74) · FeatureEnvy (36) · DataClumps (9) |

**Contexto:** 130 W es el mayor volumen por BC, proporcional a ser el Core Domain. LongMethod es inherente a los handlers hexagonales (un comando = un método con invariantes complejas). FeatureEnvy refleja el patrón CQRS donde los handlers acceden al aggregate + proyecciones + puertos. Ningún CRITICAL.

### Cobertura

Tests presentes desde SP1. Cobertura `domain/` + `application/` ≥ 90% (verificado en BL-001..BL-006). BDD features en `tests/features/`.
