---
title: "Competencia — Aggregate Competencia"
type: arquitectura-componente
bc: competencia
capa: domain
tipo_componente: aggregate
responsabilidad: "Ciclo de vida de una disciplina en un torneo: grilla, confirmación, ejecución y finalización con hash SHA-256"
interfaces_out:
  - EventStorePort
adr_refs: [ADR-001, ADR-008, ADR-018]
last_updated: "2026-05-23"
sources:
  - src/competencia/domain/aggregates/competencia.py
us_origen:
  - US-1.4.2-flujo-e2e-audit-log-get-events
  - US-2.2.1-disciplina-descriptor-value-object-port
  - US-2.3.1-ejecucion-multi-andarivel
  - US-3.3.1-torneo-id-opcional-en-competencia-para-overall
  - US-4.1.1-motivo-dq-str-enum-tarjeta-asignacion-extendida-brecha
  - US-4.1.2-tipo-tarjeta-blanca-con-penalizaciones-penalizacion
  - US-4.1.4-orden-spe-descendente-en-grilla-de-salida
  - US-4.1.7-descomponer-grilla-de-salida-ajustar-y-ranking
  - US-4.3.4-estado-en-revision-resolver-revision-ui-tarjeta
  - US-6.4.1-romper-ciclo-adp-en-competencia-domain-aggregates
  - US-ADJ-3.1-extraer-grilla-de-salida-vo-eliminar-disciplinas-sp3
  - US-ADJ-3.2-extraer-tarjeta-asignacion-vo
  - US-ADJ-3.5-limpiar-imports-cross-module-en-ports-de-competencia
  - US-ADJ-4.1-renombrar-dynb-dbf-y-spe2x50-spe-acronimos-dominio-real
  - US-ADJ-4.2-corregir-orden-grilla-sta-ascendente
  - US-ADJ-4.6-value-object-tiempo-ap-parsear-mm-ss-segundos
  - US-ADJ-6.1-renombrar-faz-faas-en-codigo
---

# Aggregate Competencia

## Responsabilidad

Modela el ciclo de vida de **una disciplina dentro de un torneo**. Gestiona la grilla de salida (generación, ajuste, confirmación) y el estado de la competencia desde Preparación hasta Finalización. Persiste su estado únicamente a través del Event Store (ADR-001).

**Stream ID:** `competencia-{competencia_id}`

## Ciclo de vida

```
Preparacion → Confirmada → EnEjecucion → Finalizada
```

| Estado | Transición |
|--------|-----------|
| `Preparacion` | Estado inicial. Permite configurar intervalo OT y generar/ajustar grilla. |
| `Confirmada` | Grilla congelada. `confirmar_grilla()` es irreversible (INV-C-02). |
| `EnEjecucion` | El juez inició la competencia. Se pueden llamar atletas y registrar resultados. |
| `Finalizada` | Todas las performances completadas. Hash SHA-256 persistido (ADR-018). |

## Invariantes

| Invariante | Descripción |
|-----------|-------------|
| INV-C-01 | `intervaloDisciplina` debe estar configurado antes de `generar_grilla()` |
| INV-C-02 | La grilla confirmada no puede ser regenerada ni ajustada |
| INV-C-03 | Solo se puede iniciar la competencia desde estado `Confirmada` |
| INV-C-04 | No se puede finalizar si quedan performances en `AnunciadaAP` o `Llamada` |

## Comandos de dominio

| Método | Precondición | Evento emitido |
|--------|-------------|----------------|
| `configurar_intervalo_ot()` | Grilla no confirmada | `IntervaloOTConfigurado` |
| `generar_grilla()` | Intervalo configurado, grilla no confirmada | `GrillaDeSalidaGenerada` |
| `ajustar_grilla()` | Grilla generada, no confirmada | `GrillaDeSalidaAjustada` |
| `asignar_juez_performance()` | Grilla generada | `JuezPerformanceAsignado` |
| `confirmar_grilla()` | Grilla generada, no confirmada | `GrillaConfirmada` |
| `iniciar_competencia()` | Estado `Confirmada` | `CompetenciaIniciada` |
| `finalizar()` | Sin performances pendientes | `CompetenciaFinalizada` |

## Eventos publicados

`IntervaloOTConfigurado` · `GrillaDeSalidaGenerada` · `GrillaDeSalidaAjustada` · `GrillaConfirmada` · `JuezPerformanceAsignado` · `CompetenciaIniciada` · `CompetenciaFinalizada`

## Reconstitución

`Competencia.reconstitute(competencia_id, disciplina, events)` — reconstruye el estado proyectando eventos en orden. Compatible con streams sin `torneo_id` (backward compat — INV-CT-03).

## Relaciones

**Contenedor:** [[arquitectura/competencia]]

- Contiene [[grilla-de-salida]] como entidad interna
- Escribe en [[event-store-port]] (única salida de datos)
- Al finalizar, persiste `hash_sha256` calculado por [[calculador-hash-competencia]]
- Los handlers de application orquestan la interacción — ver [[handler-utils]]

## Código fuente

| Archivo | Descripción |
|---|---|
| `src/competencia/domain/aggregates/competencia.py` | Aggregate Competencia — ciclo de vida, grilla, invariantes |

## ADRs relacionados

- [[ADR-001-event-sourcing-competencia]] — justificación del Event Sourcing
- [[ADR-008-event-store-sqlite]] — implementación del store
- [[ADR-018-hash-sha256-auditoria]] — hash de cierre
