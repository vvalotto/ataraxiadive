---
title: "US-1.2.1 — RegistrarAP"
type: trazabilidad-us
sp: SP1
inc: INC-1.2
bc: competencia
estado: cerrada
fecha_cierre: "2026-03-21"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §6
us_id: US-1.2.1
tests_count: 34
rf:
  - RF-EJ-08
  - RF-PR-01
  - RF-PR-02
  - RF-PR-03
software_items:
  - src/competencia/application/commands/registrar_ap.py
test_units:
  - tests/features/US-1.2.1-registrar-ap.feature
  - tests/integration/competencia/test_registrar_ap_integration.py
origen_tipo: rf
---

# US-1.2.1 — RegistrarAP

## Descripción

Permite al juez registrar el Anuncio de Performance (AP) de un atleta antes de competir.

## RFs cubiertos

| RF | Descripción |
|----|-------------|
| [[RF-PR-01-anuncio-previo-ap]] | AP = marca declarada por el atleta |
| [[RF-PR-02-validacion-valores-ap]] | AP > 0, sin negativos ni cero (INV-P-01) |
| [[RF-PR-03-ap-definitivo-sin-modificacion]] | AP no modificable una vez registrado (INV-P-02) |
| [[RF-EJ-08-distancias-con-decimales]] | Distancia con decimales (metros) |

## Comando principal

`RegistrarAP`

## Invariantes aplicadas

- INV-P-01: AP > 0
- INV-P-02: AP inmutable post-registro
- INV-P-03, INV-P-04 (derivadas)

## Tests

| Suite | Resultado |
|-------|-----------|
| unit/competencia/domain | ✅ |
| unit/competencia/application | ✅ |
| unit/competencia/infrastructure | ✅ |
| integration/competencia | ✅ |
| features/US-1.2.1 | ✅ |
| **Total acumulado** | **34 tests (92%)** |

## Estado

✅ Completado — 2026-03-21
