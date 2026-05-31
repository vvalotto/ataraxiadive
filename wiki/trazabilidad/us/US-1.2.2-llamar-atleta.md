---
title: "US-1.2.2 — LlamarAtleta"
type: trazabilidad-us
sp: SP1
inc: INC-1.2
bc: competencia
estado: cerrada
fecha_cierre: "2026-03-22"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §6
us_id: US-1.2.2
tests_count: 41
rf:
  - RF-EJ-02-registro-dns-no-presentado
software_items:
  - src/competencia/application/commands/llamar_atleta.py
test_units:
  - tests/features/US-1.2.2-llamar-atleta.feature
  - tests/integration/competencia/test_llamar_atleta_integration.py
origen_tipo: rf
componentes_wiki:
  - arquitectura/competencia/command-handlers
---

# US-1.2.2 — LlamarAtleta

## Descripción

Inicia el turno de un atleta en la grilla. Marca el inicio del OT (Official Top) para el atleta convocado.

## RFs cubiertos

| RF | Descripción |
|----|-------------|
| [[RF-EJ-02-registro-dns-no-presentado]] | DNS = descalificación inmediata, sin espera (P-07, INV-P-08) |

## Comando principal

`LlamarAtleta`

## Invariantes aplicadas

- INV-P-05: solo se puede llamar al próximo atleta según orden de grilla

## Tests

| Suite | Resultado |
|-------|-----------|
| unit/competencia/domain | ✅ |
| unit/competencia/application | ✅ |
| unit/competencia/infrastructure | ✅ |
| integration/competencia | ✅ |
| features/US-1.2.2 | ✅ |
| **Total acumulado** | **41 tests (92%)** |

## Estado

✅ Completado — 2026-03-22
