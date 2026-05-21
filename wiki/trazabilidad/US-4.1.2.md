---
title: "US-4.1.2 — TipoTarjeta.BlancaConPenalizaciones + PenalizacionTecnica VO (Brecha CMAS #2)"
type: trazabilidad-us
sp: SP4
inc: INC-4.1
bc: competencia
estado: completado
fecha_cierre: "2026-04-08"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §12
---

# US-4.1.2 — TipoTarjeta.BlancaConPenalizaciones + PenalizacionTecnica VO

## Descripción

Modela la tarjeta blanca con penalizaciones técnicas: el atleta logra la actuación pero recibe deducciones al RP por infracciones menores (ej: protocolo parcial). Implementa ADR-014.

## RFs / Brechas cubiertos

Brecha CMAS #2 — tarjeta blanca con penalizaciones acumulables.

## Contenido implementado

- `TipoTarjeta.BlancaConPenalizaciones` — nueva variante del enum
- VO `PenalizacionTecnica` con tipo y deducción en metros
- Cálculo: `RP = medido − Σ deducciones`
- Regla: las penalizaciones son acumulables (N × 3m por infracción de tipo X)

## Decisiones arquitectónicas aplicadas

| ADR | Aplicación |
|-----|-----------|
| [[ADR-014]] | Penalizaciones acumulables — modelo de deducción N×3m |

## Tests

| Suite | Resultado |
|-------|-----------|
| unit/competencia/domain | ✅ |
| unit/competencia/application | ✅ |
| unit/resultados | ✅ |
| integration/resultados | ✅ |
| features/US-4.1.2 | ✅ |
| **Total acumulado** | **107 passed** |

## Estado

✅ Completado — 2026-04-08
