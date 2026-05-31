---
title: "Competencia — Helpers HandlerUtils"
type: arquitectura-componente
bc: competencia
capa: application
tipo_componente: service
responsabilidad: "Helpers internos de orquestación compartidos por todos los command handlers: carga, reconstitución y persistencia de aggregates"
interfaces_out:
  - EventStorePort
adr_refs: [ADR-001]
last_updated: "2026-05-23"
sources:
  - src/competencia/application/commands/_handler_utils.py
  - src/competencia/application/commands/_stream_ids.py
---

# Helpers HandlerUtils

## Responsabilidad

Módulo interno (`_handler_utils.py`) que centraliza el **patrón de orquestación** repetido en todos los command handlers del BC:

1. Cargar eventos desde el Event Store
2. Reconstituir el aggregate
3. Ejecutar el comando de dominio
4. Persistir los eventos pendientes

## Funciones principales

| Función | Descripción |
|---------|-------------|
| `cargar_o_fallar(event_store, stream_id, exception_factory)` | Carga el stream; levanta excepción si está vacío |
| `reconstruir_performance(events)` | Reconstituye `Performance.reconstitute(events)` |
| `reconstruir_competencia(competencia_id, disciplina, events)` | Reconstituye `Competencia.reconstitute(...)` |
| `persistir_eventos_pendientes(event_store, stream_id, aggregate)` | Persiste todos los `aggregate.pull_events()` |

## Stream IDs canónicos (`_stream_ids.py`)

| Función | Resultado |
|---------|-----------|
| `build_competencia_stream_id(competencia_id)` | `"competencia-{uuid}"` |
| `build_performance_stream_id(competencia_id, participante_id, disciplina)` | `"performance-{uuid}-{uuid}-{disciplina}"` |

## Valor arquitectónico

Evita que cada handler repita el ciclo load → reconstitute → command → persist. Centralizar aquí garantiza que todos los handlers usen exactamente el mismo patrón de acceso al Event Store.

## Relaciones

**Contenedor:** [[arquitectura/competencia]]

- Usa [[event-store-port]] para todas las operaciones de I/O
- Es usado por todos los command handlers del BC Competencia
- [[competencia-aggregate]] y [[performance-aggregate]] son los aggregates que maneja

## Código fuente

| Archivo | Descripción |
|---|---|
| `src/competencia/application/commands/_handler_utils.py` | Helpers: cargar, reconstituir, persistir aggregates |
| `src/competencia/application/commands/_stream_ids.py` | Stream IDs canónicos (build_*_stream_id) |
