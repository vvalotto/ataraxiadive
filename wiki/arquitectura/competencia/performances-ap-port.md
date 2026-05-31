---
title: "Competencia — Port PerformancesAPPort"
type: arquitectura-componente
bc: competencia
capa: domain
tipo_componente: port
responsabilidad: "Consulta de performances en estado AnunciadaAP para una competencia — insumo para generar la grilla"
interfaces_out:
  - EventStorePort
adr_refs: [ADR-001, ADR-008]
last_updated: "2026-05-23"
sources:
  - src/competencia/domain/ports/performances_ap_port.py
  - src/competencia/infrastructure/repositories/performances_ap_adapter.py
---

# Port PerformancesAPPort

## Responsabilidad

Puerto para obtener las **performances con AP registrado** (`AnunciadaAP`) de una competencia dada. Es el insumo principal del `GenerarGrillaHandler` — sin este port no hay grilla.

## Contrato

```python
async def get_performances_con_ap(competencia_id: UUID) -> list[PerformancesAPData]
```

`PerformancesAPData` es un DTO frozen con: `performance_id`, `atleta_id`, `valor_ap`, `unidad`.

## Consumidor

`GenerarGrillaHandler` — lee este port para obtener los APs y construir la `GrillaDeSalida`.

## Implementación concreta: PerformancesAPAdapter

Lee todos los streams `performance-{competencia_id}-*` del [[event-store-port]], reconstituye cada `Performance` y filtra las que están en estado `AnunciadaAP`.

**Estrategia:** scan por prefijo de stream_id — no requiere índice adicional, opera sobre el Event Store.

## Relaciones

**Contenedor:** [[arquitectura/competencia]]

- Depende de [[event-store-port]] para leer los streams
- Reconstituye [[performance-aggregate]] como paso intermedio
- Es consumido por `GenerarGrillaHandler` (capa application)

## Código fuente

| Archivo | Descripción |
|---|---|
| `src/competencia/domain/ports/performances_ap_port.py` | Puerto abstracto PerformancesAPPort |
| `src/competencia/infrastructure/repositories/performances_ap_adapter.py` | Adapter — reconstituye performances desde event store |
