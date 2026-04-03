# Plan de Implementacion — US-ADJ-3.8

## Resumen

Eliminar el acoplamiento directo de `resultados` al aggregate `Performance` de
`competencia`, reescribiendo `ResultadosCompetenciaAdapter` para que lea
eventos crudos del stream y construya `ResultadoFinal` sin reconstituir el
modelo interno del otro BC.

## Objetivo observable

- `resultados_competencia_adapter.py` deja de importar desde
  `competencia.domain`
- el adapter sigue devolviendo los mismos `ResultadoFinal`
- ranking por disciplina y overall siguen funcionando igual

## Alcance

- `src/resultados/infrastructure/repositories/resultados_competencia_adapter.py`
- tests unitarios/integracion de `resultados` impactados por el adapter
- artefactos de plan, calidad y reporte de la US

No incluye:

- cambios en contratos de `resultados/domain/ports/`
- cambios en aggregates de `competencia`
- cambios en endpoints HTTP
- activos BDD nuevos

## Decisiones de diseño

1. El adapter va a traducir desde eventos crudos del upstream, no desde el
   aggregate `Performance`.
2. La extraccion se encapsulara en un helper privado tipo
   `_extraer_resultado_de_stream(...)`.
3. Se interpretaran solo los eventos necesarios para el contrato actual:
   - `APRegistrado` o evento equivalente para unidad
   - `AtletaLlamado` / `PerformanceIniciada` solo si aporta identidad o no hace
     falta
   - `ResultadoRegistrado`
   - `TarjetaAsignada`
   - `DNSRegistrado`
4. El adapter seguira filtrando por disciplina y devolviendo solo estados
   finales observables para `resultados`.

## Implementacion por area

### Adapter

- eliminar imports desde `competencia.domain.aggregates.performance`
- eliminar import de `EstadoPerformance`
- recorrer `stream_events` y derivar:
  - `atleta_id`
  - `disciplina`
  - `rp`
  - `unidad`
  - `tarjeta`
  - `es_dns`
- devolver `None` si la performance no corresponde a la disciplina o no esta
  finalizada

### Tests

- correr tests existentes de `resultados`
- agregar/ajustar test si falta un caso directo del adapter

## Riesgos a controlar

1. usar nombres de eventos o payloads incorrectos
2. perder el caso `DNS`
3. calcular mal `unidad` o `tarjeta` por depender de otro evento del stream
4. romper el ranking si el adapter deja de devolver exactamente el mismo shape

## Validacion prevista

- `pytest tests/unit/resultados/application/test_calcular_ranking_handler.py -q`
- `pytest tests/integration/resultados/test_calcular_ranking_integration.py -q`
- `grep "from competencia.domain" src/resultados/infrastructure/repositories/resultados_competencia_adapter.py`
- `py_compile` del adapter
- `codeguard` sobre el adapter
- `git diff --check`

## Artefactos esperados al cierre

- adapter desacoplado de `competencia.domain`
- evidencia de quality gates
- `docs/reports/US-ADJ-3.8-report.md`
