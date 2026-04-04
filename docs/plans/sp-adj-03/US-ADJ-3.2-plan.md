# Plan de Implementacion — US-ADJ-3.2

## Resumen

Extraer el concepto `TarjetaAsignacion` como Value Object del dominio de
`competencia`, para encapsular las invariantes de asignacion de tarjeta y
reducir el acoplamiento de reglas dentro de `Performance.asignar_tarjeta()`.

## Objetivo observable

- existe `competencia/domain/value_objects/tarjeta_asignacion.py`
- `Performance.asignar_tarjeta()` delega la validacion de
  `tipo/motivo/distancia_blackout` al VO
- el comportamiento externo del handler y del aggregate no cambia

## Alcance

- `src/competencia/domain/value_objects/tarjeta_asignacion.py`
- `src/competencia/domain/aggregates/performance.py`
- tests unitarios/integracion impactados por asignacion de tarjeta
- artefactos de plan, calidad y reporte de la US

No incluye:

- cambios de contrato HTTP
- activos BDD nuevos
- cambios en otros aggregates o policies

## Decisiones de diseño

1. `TarjetaAsignacion` sera un VO inmutable que valida en constructor:
   - motivo obligatorio para Amarilla y Roja
   - distancia obligatoria para `black-out`
2. `Performance` conserva el control del estado y la emision de eventos; solo
   delega la validacion del conjunto de datos.
3. El VO expondra atributos simples reutilizables por el aggregate al armar el
   evento `TarjetaAsignada`.

## Implementacion por area

### Dominio

- crear `tarjeta_asignacion.py`
- mover al VO la validacion de:
  - `MotivoObligatorio`
  - `DistanciaBlackoutObligatoria`
- actualizar `Performance.asignar_tarjeta()` para:
  - construir el VO
  - usar sus valores al persistir el evento
  - mantener el mismo efecto sobre estado y datos internos

### Tests

- correr tests unitarios actuales de `asignar_tarjeta`
- correr integracion actual de `asignar_tarjeta`
- agregar test unitario directo del VO solo si falta evidencia de las
  invariantes en la capa de dominio

## Riesgos a controlar

1. cambiar el tipo exacto o el payload de `TarjetaAsignada`
2. romper el caso `black-out` con `distancia_blackout`
3. duplicar validacion entre VO y aggregate

## Validacion prevista

- `pytest tests/unit/competencia/application/test_asignar_tarjeta_handler.py -q`
- `pytest tests/integration/competencia/test_asignar_tarjeta_integration.py -q`
- `py_compile` de archivos impactados
- `codeguard` sobre `performance.py` y `tarjeta_asignacion.py`
- `git diff --check`

## Artefactos esperados al cierre

- nuevo VO `TarjetaAsignacion`
- `Performance` simplificada en la asignacion de tarjeta
- evidencia de quality gates
- `docs/reports/US-ADJ-3.2-report.md`
