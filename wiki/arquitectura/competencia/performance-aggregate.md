---
title: "Competencia — Aggregate Performance"
type: arquitectura-componente
bc: competencia
capa: domain
tipo_componente: aggregate
responsabilidad: "Ciclo de vida de la actuación de un atleta: AP, llamada, resultado, tarjeta y resolución"
interfaces_out:
  - EventStorePort
adr_refs: [ADR-001, ADR-008, ADR-014]
last_updated: "2026-05-23"
sources:
  - src/competencia/domain/aggregates/performance.py
  - src/competencia/domain/aggregates/performance_events.py
  - src/competencia/domain/aggregates/performance_state.py
us_origen:
  - US-1.1.1-setup-esqueleto-bc-competencia
  - US-1.4.1-asignar-tarjeta-roja-black-out-con-distancia
  - US-1.4.2-flujo-e2e-audit-log-get-events
  - US-4.1.2-tipo-tarjeta-blanca-con-penalizaciones-penalizacion
  - US-4.1.5-descomponer-aggregate-performance-en-modulos
  - US-ADJ-1.1-refactoring-domain-ot-programado-event-handlers-snake
  - US-ADJ-1.2-refactoring-domain-helpers-recalcular-ots-aplicar-swap
tests:
  - tests/features/US-1.4.1-blackout-con-distancia.feature
  - tests/features/US-1.4.2-flujo-e2e.feature
  - tests/integration/competencia/test_flujo_e2e.py
  - tests/features/US-4.1.2-tarjeta-blanca-penalizaciones.feature
---

# Aggregate Performance

## Responsabilidad

Modela el **ciclo de vida completo de la actuación de un atleta** en una disciplina: desde el anuncio de su marca (AP) hasta la asignación de tarjeta y resolución final. Es el aggregate de mayor riqueza de dominio del sistema.

**Stream ID:** `performance-{competencia_id}-{participante_id}-{disciplina}`

## Ciclo de vida

```
AnunciadaAP → Llamada → ResultadoRegistrado → [EnRevision →] Ejecutada   (camino nominal)
AnunciadaAP → Llamada → DNS                                               (no presentado)
DNS → ResultadoRegistrado → ...                                           (corrección DNS)
```

## Invariantes

| Invariante | Descripción |
|-----------|-------------|
| INV-P-01 | `valorAP > 0` — validado por value object `AP` |
| INV-P-05 | `llamar()` solo si la Competencia está `EnEjecucion` — verificado por handler |
| INV-P-06 | `registrar_resultado()` solo desde `Llamada` |
| INV-P-07 | `asignar_tarjeta()` solo desde `ResultadoRegistrado` |
| INV-P-08 | `registrar_dns()` solo desde `Llamada` |
| INV-P-11 | Tarjeta Roja requiere `motivo_dq` obligatorio |
| INV-P-11b | Tarjeta Amarilla requiere `motivo_texto` obligatorio |
| INV-P-12 | `corregir_resultado()` solo desde `Ejecutada`; motivo obligatorio |

## Comandos de dominio

| Método | Precondición | Evento emitido |
|--------|-------------|----------------|
| `registrar_ap()` | Cualquier estado inicial | `APRegistrado` |
| `llamar()` | Estado `AnunciadaAP` | `AtletaLlamado` |
| `registrar_resultado()` | Estado `Llamada` | `ResultadoRegistrado` |
| `registrar_dns()` | Estado `Llamada` | `DNSRegistrado` |
| `asignar_tarjeta()` | Estado `ResultadoRegistrado` | `TarjetaAsignada` |
| `resolver_revision()` | Estado `EnRevision` | `RevisionResuelta` |
| `corregir_resultado()` | Estado `Ejecutada` | `ResultadoCorregido` |
| `corregir_resultado_tras_dns()` | Estado `DNS` | `ResultadoCorregidoTrasDNS` |

## Eventos publicados

`APRegistrado` · `AtletaLlamado` · `ResultadoRegistrado` · `DNSRegistrado` · `TarjetaAsignada` · `RevisionResuelta` · `ResultadoCorregido` · `ResultadoCorregidoTrasDNS`

## Cálculo de RP

El RP visible para ranking es `rp_penalizado` si existen penalizaciones, o `rp_medido` en caso contrario. La lógica de cálculo está encapsulada en `RPFinal` y `ResolucionTarjeta` (value objects). Las penalizaciones son acumulables (ADR-014).

## Tarjetas

| Tipo | Resultado |
|------|-----------|
| Blanca | Performance válida — RP medido es el final |
| BlancaConPenalizaciones | Válida pero RP reducido por infracciones técnicas |
| Amarilla | Pasa a `EnRevision` — el organizador la resuelve |
| Roja | Descalificación — requiere `MotivoDQ` reglamentario |

## Reconstitución

`Performance.reconstitute(events)` — el primer evento debe ser `APRegistrado`. La reconstitución está separada en `performance_state.py` para mantener el aggregate limpio.

## Relaciones

**Contenedor:** [[arquitectura/competencia]]

- Escribe en [[event-store-port]]
- Es orquestado por handlers en [[handler-utils]]
- Su estado es leído por [[performances-ap-port]] y [[performances-estado-port]]
- Vinculado con [[competencia-aggregate]] por `competencia_id`

## Código fuente

| Archivo | Descripción |
|---|---|
| `src/competencia/domain/aggregates/performance.py` | Aggregate Performance — ciclo de vida del atleta |
| `src/competencia/domain/aggregates/performance_events.py` | Eventos de dominio del aggregate Performance |
| `src/competencia/domain/aggregates/performance_state.py` | Estado interno del aggregate Performance (reconstitución) |

## ADRs relacionados

- [[ADR-001-event-sourcing-competencia]]
- [[ADR-014-penalizaciones-acumulables]] — lógica de penalizaciones en RP
