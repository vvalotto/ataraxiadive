---
title: "Penalizacion"
type: concepto
last_updated: "2026-05-22"
sources:
  - wiki/decisiones/ADR-014-penalizaciones-acumulables.md
  - wiki/arquitectura/competencia.md
  - wiki/conceptos/tarjeta.md
---

# Penalizacion

Infracción técnica cometida durante una [[performance]] que reduce la marca final sin descalificar al atleta. Introduce el tipo de [[tarjeta]] `BlancaConPenalizaciones`.

## Modelo de datos (`PenalizacionTecnica`)

| Campo | Descripción |
|-------|-------------|
| `codigo` | Código reglamentario de la infracción (configurable vía [[ADR-004-reglas-como-datos]]) |
| `deduccion` | Metros o segundos que se restan al RP medido |

## Cálculo del RP final

```
rp_penalizado = rp_medido − Σ(deducciones)
rp_penalizado = max(0, rp_penalizado)   ← clamp a 0
```

El campo `rp` del aggregate `Performance` retorna `rp_penalizado` si existe, o `rp_medido` en caso contrario — compatibilidad retroactiva.

## Restricciones de aplicación

- Solo aplica a **disciplinas dinámicas** (no estáticas de tiempo). Validación en el handler de aplicación.
- `BlancaConPenalizaciones` requiere **al menos una** penalización.
- Las penalizaciones son **acumulables** — varias infracciones en la misma performance se suman.
- El aggregate `RankingCompetencia` trata `BlancaConPenalizaciones` como tarjeta válida para ranking.

## Tipos de tarjeta resultantes

| Tarjeta | Penalizaciones | Válida para ranking |
|---------|---------------|:-------------------:|
| `Blanca` | 0 | ✅ |
| `BlancaConPenalizaciones` | ≥ 1 | ✅ (con RP reducido) |
| `Roja` | — (descalificación total) | ❌ |

Ver [[tarjeta]] para el modelo completo de validez.

## Evento generado

`TarjetaAsignada` lleva: `penalizaciones[]`, `rp_medido`, `rp_penalizado`. Los cuatro tipos de tarjeta (incluido `BlancaConPenalizaciones`) deben asumirse en todos los adaptadores y tests que procesen este evento.

## BC propietario

[[competencia]] — el aggregate `Performance` acumula penalizaciones.
[[resultados]] — `EntradaRanking` refleja el RP penalizado como marca efectiva.

## ADRs relacionados

- [[ADR-014-penalizaciones-acumulables]] — decisión de introducir `BlancaConPenalizaciones`
- [[ADR-004-reglas-como-datos]] — los códigos de penalización se configuran como datos, no como constantes
- [[ADR-001-event-sourcing-competencia]] — `TarjetaAsignada` es un evento del event store
