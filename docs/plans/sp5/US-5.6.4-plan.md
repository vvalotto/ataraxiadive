# Plan de Implementación — US-5.6.4: RankingOverall con puntos acumulados

**Incremento:** INC-5.6 | **Sprint:** SP5

---

## Diagnóstico

`RankingOverall` usa actualmente un algoritmo posicional (suma de posiciones, menor es mejor).
`EntradaRanking.puntos: Decimal` fue añadido en US-5.6.3. US-5.6.4 extiende `RankingOverall`
para sumar esos puntos FAAS en lugar de posiciones.

## Cambios por capa

### Domain
- `entrada_overall.py`: `puntaje: int` → `puntos_overall: Decimal`; `detalle: dict[str, int]` → `dict[str, Decimal]`
- `exceptions.py`: nueva `DisciplinasNoFinalizadas` (INV-5.6.4-04)
- `ranking_overall.py`: reescribir algoritmo (sumar `EntradaRanking.puntos` DESC, ausente=0); validar INV-5.6.4-04; eliminar `penalizacion_ausente`; actualizar serialización

### Application
- `calcular_overall.py`: incluir TODAS las disciplinas en el mapa (incluso con entries vacías) para que el aggregate valide INV-5.6.4-04
- `obtener_overall.py`: DTO `puntos_overall: Decimal` (reemplaza `puntaje: int`); `detalle: dict[str, Decimal]`

### API
- `router.py`: respuesta `GET /{torneo_id}/overall` → `puntos_overall` en lugar de `puntaje`

### Tests a actualizar
- `test_ranking_overall.py` — reescribir para usar puntos FAAS
- `test_calcular_overall_handler.py` — `_ranking_event` incluye `puntos`; nuevo test INV-5.6.4-04
- `test_obtener_overall_handler.py` — DTO con `puntos_overall`
- `test_router_overall.py` — respuesta con `puntos_overall`
- `test_obtener_overall_integration.py` — payload con `puntos_overall`

## Decisiones clave

- Backward compat del event store: `_dict_a_entrada` usa fallback `"0.00"` para eventos legacy sin `puntos_overall`
- `penalizacion_ausente` eliminado: ausente en una disciplina aporta 0 puntos FAAS (INV-5.6.4-01)
- INV-5.6.4-04 vive en el domain aggregate (no en el handler)
- Orden: `puntos_overall` DESC, estabilidad por `atleta_id` str

## Estimación
- Domain: 25 min | Application: 15 min | Tests: 30 min | BDD: 20 min | QG: 10 min
- Total estimado: 100 min
