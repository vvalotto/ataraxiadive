# Plan de Implementacion — US-ADJ-3.1

## Resumen

Reducir la complejidad del aggregate `Competencia` extrayendo la logica de
grilla a una entidad de dominio `GrillaDeSalida`, sin cambiar la interfaz
publica ni el contrato de eventos. En paralelo, eliminar la restriccion
`_DISCIPLINAS_SP3` de `Torneo` para que el enum `Disciplina` vuelva a ser la
unica fuente de verdad del dominio.

## Objetivo observable

- `Competencia` mantiene intactos `generar_grilla`, `ajustar_grilla`,
  `confirmar_grilla`, `grilla` y `reconstitute`, pero delega la logica de
  grilla a `GrillaDeSalida`.
- `Torneo.asignar_disciplinas(...)` acepta cualquier `Disciplina` valida del
  enum sin restriccion de sprint.

## Alcance

- `src/competencia/domain/entities/grilla_de_salida.py`
- `src/competencia/domain/aggregates/competencia.py`
- `src/torneo/domain/aggregates/torneo.py`
- tests unitarios y de integracion impactados por el refactor

No incluye:

- escenarios BDD nuevos
- cambios de contrato HTTP
- cambios de schema o persistencia

## Decisiones de diseño

1. `GrillaDeSalida` sera una entidad interna del aggregate: encapsula estado y
   transformaciones de la grilla, pero no emite eventos.
2. `Competencia` sigue siendo el aggregate root y la unica fuente de eventos de
   Event Sourcing.
3. La reconstitucion aplicara los eventos de grilla delegando en
   `GrillaDeSalida`, preservando backward compatibility del stream existente.
4. La logica de ordenamiento, asignacion de andariveles y recalculo de OTs se
   mueve a la entidad para bajar WMC del aggregate sin alterar el
   comportamiento observable.
5. En `Torneo`, la validacion de disciplinas por sprint se elimina; la
   validez queda determinada exclusivamente por el enum `Disciplina`.

## Implementacion por area

### Competencia

- Crear el paquete `competencia/domain/entities/`.
- Implementar `GrillaDeSalida` con operaciones para:
  - generar entradas desde `PerformancesAPData`
  - aplicar cambios de posicion y andarivel
  - recalcular OTs cuando cambian posiciones
  - reconstruirse desde payloads persistidos
- Simplificar `Competencia` para que:
  - valide precondiciones
  - delegue en la entidad
  - arme payloads de eventos con el resultado delegado
  - use la entidad tambien durante `_apply_*`

### Torneo

- Eliminar `_DISCIPLINAS_SP3`.
- Ajustar `asignar_disciplinas()` para ordenar y persistir cualquier
  `Disciplina` recibida.

### Tests

- Reutilizar la suite unitaria existente de `competencia` y `torneo`.
- Ajustar solo los tests que hoy fijan la restriccion SP3 para reflejar la
  nueva regla de dominio.
- No agregar `.feature` nuevas; si hace falta cobertura nueva, agregarla en
  unit/integration.

## Riesgos a resolver

1. Que el refactor cambie la semantica exacta del swap en `ajustar_grilla`.
2. Que la reconstitucion desde `GrillaDeSalidaAjustada` no preserve el
   recalculo de OTs.
3. Que existan tests o adapters que dependan implicitamente de la restriccion
   `_DISCIPLINAS_SP3`.

## Validacion prevista

- `pytest` focalizado sobre:
  - `tests/unit/competencia/domain/test_generar_grilla.py`
  - `tests/unit/competencia/domain/test_ajustar_grilla.py`
  - `tests/unit/competencia/domain/test_confirmar_grilla.py`
  - `tests/unit/torneo/domain/test_disciplinas_torneo.py`
- `git diff --check`
- si el cambio queda estable, corrida adicional de integracion focalizada de
  `competencia`

## Artefactos esperados al cierre

- refactor aplicado en `src/competencia/` y `src/torneo/`
- plan de US en disco
- reporte de implementacion de la US
