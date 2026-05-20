---
title: "ADR-014: Penalizaciones acumulables como BlancaConPenalizaciones"
type: decision
last_updated: "2026-05-20"
sources:
  - docs/adr/ADR-014-penalizaciones-acumulables.md
estado: Aceptada
fecha: 2026-04-08
bcs_afectados: [competencia, resultados]
---

# ADR-014: Penalizaciones acumulables como BlancaConPenalizaciones

## Decisión

Se introduce `TipoTarjeta.BlancaConPenalizaciones` como resultado válido con infracciones técnicas acumulables que reducen la marca final sin descalificar.

## Modelo vigente de Performance

| Campo | Descripción |
|-------|-------------|
| `rp_medido` | Marca física original |
| `rp_penalizado` | Marca efectiva luego de deducciones |
| `rp` | Propiedad compatible: retorna `rp_penalizado` si existe, o `rp_medido` |
| `penalizaciones` | Lista de value objects `PenalizacionTecnica` (código + deducción) |

## Tipos de tarjeta vigentes

| Tarjeta | Resultado | Válida para ranking |
|---------|-----------|:-------------------:|
| `Blanca` | Performance válida sin penalizaciones | ✅ |
| `BlancaConPenalizaciones` | Válida con deducciones acumuladas | ✅ |
| `Roja` | Descalificación | ❌ |

## Reglas de negocio

- `BlancaConPenalizaciones` requiere al menos una penalización.
- RP final = RP medido − suma de deducciones; se clampa a 0 si la suma supera al medido.
- Solo aplica a disciplinas dinámicas — validación en el handler de aplicación.
- `RankingCompetencia` trata `BlancaConPenalizaciones` como tarjeta válida.

## Consecuencias vigentes

- El evento `TarjetaAsignada` lleva: `penalizaciones`, `rp_medido`, `rp_penalizado`.
- Tests y adaptadores de resultados deben asumir **cuatro** tipos de tarjeta (no tres).
- La [[tarjeta]] en el wiki tiene una nota vinculada a este ADR.

## ADRs relacionados

- [[ADR-001-event-sourcing-competencia]] — `TarjetaAsignada` es un evento del event store
- [[ADR-004-reglas-como-datos]] — `card_rule_config` almacena los códigos de penalización configurables
