---
title: "US-4.1.1 — MotivoDQ StrEnum + TarjetaAsignacion extendida (Brecha CMAS #1)"
type: trazabilidad-us
sp: SP4
inc: INC-4.1
bc: competencia
estado: cerrada
fecha_cierre: "2026-04-08"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §12
us_id: US-4.1.1
tests_count: 102
---

# US-4.1.1 — MotivoDQ StrEnum + TarjetaAsignacion extendida

## Descripción

Implementa los motivos de descalificación reglamentarios CMAS/FAAS mediante un StrEnum tipado, extendiendo `TarjetaAsignacion` para capturar el motivo específico de cada DQ.

## RFs / Brechas cubiertos

Brecha CMAS #1 — motivos de DQ no modelados.

## Contenido implementado

- `MotivoDQ` StrEnum: `BKO_SUPERFICIE`, `BKO_SUBACUATICO`, `NO_PROTOCOLO`, `INFRACCION_TECNICA`, `NO_INICIO_VENTANA`, `SALIDA_FALSO`
- `TarjetaAsignacion` VO extendido con campo `motivo_dq: Optional[MotivoDQ]`

## Motivación

El sistema original solo registraba "tarjeta roja" sin especificar el motivo. El reglamento CMAS exige registrar el motivo exacto de cada DQ para la documentación oficial del torneo.

## Tests

| Suite | Resultado |
|-------|-----------|
| unit/competencia/domain | ✅ |
| unit/competencia/application | ✅ |
| integration/competencia | ✅ |
| features/US-4.1.1 | ✅ |
| **Total acumulado** | **102 passed** |

## Estado

✅ Completado — 2026-04-08
