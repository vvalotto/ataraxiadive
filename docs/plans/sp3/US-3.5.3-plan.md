# Plan de Implementacion — US-3.5.3

## Resumen

Exponer la consulta publica del ranking overall de un torneo en el BC
`resultados`, reutilizando el patron de `ObtenerRankingHandler` para leer el
ultimo `RankingOverallCalculado` persistido por `US-3.5.1` y disparado por
`US-3.5.2`.

## Objetivo observable

`GET /resultados/{torneo_id}/overall` responde siempre `200` y devuelve:

- `calculado=true` con entradas ordenadas cuando el overall existe
- `calculado=false` con `ranking=[]` cuando el overall aun no fue calculado

## Alcance

- `src/resultados/application/queries/obtener_overall.py`
- `src/resultados/api/router.py`
- artefactos del pipeline exigidos por la US

No incluye:

- recalculo del overall (`US-3.5.1`)
- politica de disparo `P-09` (`US-3.5.2`)
- autenticacion o permisos adicionales para el endpoint

## Decisiones de diseño

1. El stream canonico de lectura es `ranking-overall-{torneo_id}`.
2. `ObtenerOverallHandler` devolvera DTOs HTTP-friendly, sin exponer el
   aggregate directamente.
3. La ausencia de overall persistido se modela como lista vacia y
   `calculado=false`; nunca se responde `404`.
4. El endpoint convivira en `src/resultados/api/router.py` con el endpoint
   existente de ranking por disciplina y reutilizara el mismo provider de
   `ranking_store`.
5. El campo `detalle` se devolvera tal como fue persistido en el evento:
   disciplina -> posicion usada en el overall.

## Implementacion por capa

### Aplicacion

- Crear `ObtenerOverallQuery` con `torneo_id: UUID`.
- Crear `OverallEntradaDTO` con:
  - `posicion`
  - `atleta_id`
  - `puntaje`
  - `detalle`
  - `en_podio`
- Implementar `ObtenerOverallHandler` que:
  - cargue el stream `ranking-overall-{torneo_id}`
  - reconstituya `RankingOverall`
  - proyecte la ultima version a DTOs ordenados por posicion
  - retorne `[]` si no existen eventos

### API

- Definir `get_obtener_overall_handler(...)` y `ObtenerOverallHandlerDep`.
- Agregar `GET /{torneo_id}/overall`.
- Responder JSON con:
  - `torneo_id`
  - `total`
  - `calculado`
  - `ranking`

## Riesgos a resolver

1. `RankingOverall.reconstitute(...)` debe tolerar stream vacio igual que
   `RankingCompetencia`; si no, el handler tendra que proteger ese caso antes.
2. La forma exacta del payload `entries` persistido por
   `RankingOverallCalculado` debe mapearse a DTOs sin perder `detalle`.

## Artefactos esperados al cierre

- query handler y endpoint overall operativos en `src/resultados/`
- evidencia de quality gates
- `docs/reports/US-3.5.3-report.md`
