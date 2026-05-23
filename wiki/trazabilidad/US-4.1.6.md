---
title: "US-4.1.6 — _handler_utils.py: helpers comunes para handlers"
type: trazabilidad-us
sp: SP4
inc: INC-4.1
bc: competencia
estado: cerrada
fecha_cierre: "2026-04-08"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §12
us_id: US-4.1.6
tests_count: 36
---

# US-4.1.6 — _handler_utils.py: helpers comunes para handlers

## Descripción

Refactoring técnico: extrae lógica repetida de múltiples handlers a un módulo de utilidades compartido, reduciendo duplicación y complejidad en cada handler.

## Capas afectadas

`competencia/application/`

## Contenido implementado

- `_handler_utils.py` — funciones helper compartidas entre handlers
- Handlers aliviados: `AsignarTarjetaHandler`, `GenerarGrillaHandler`, `LlamarAtletaHandler`, `RegistrarAPHandler`

## Tests

| Suite | Resultado |
|-------|-----------|
| unit/competencia/application | ✅ |
| **Total acumulado** | **36 passed** |

BDD waiver — refactoring de handlers sin comportamiento nuevo.

## Estado

✅ Completado — 2026-04-08
