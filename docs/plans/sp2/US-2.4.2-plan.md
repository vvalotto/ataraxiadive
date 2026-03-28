# Plan de Implementación — US-2.4.2: Calcular Ranking (BC Resultados — núcleo)

**Fecha:** 2026-03-27
**Branch:** feature/US-2.4.2-calcular-ranking
**Incremento:** Inc 2.4 — El Ranking

---

## Arquitectura afectada

```
src/resultados/                           ← BC nuevo (scaffold ya existe vacío)
  domain/
    exceptions.py                         ← NUEVO: ResultadosIncompletos
    value_objects/
      entrada_ranking.py                  ← NUEVO: EntradaRanking VO
    events/
      resultados_calculados.py            ← NUEVO: ResultadosCalculados event
    ports/
      resultados_competencia_port.py      ← NUEVO: ResultadoFinal DTO + port ACL
    aggregates/
      ranking_competencia.py              ← NUEVO: RankingCompetencia aggregate
  application/
    commands/
      calcular_ranking.py                 ← NUEVO: command + handler
    queries/
      obtener_ranking.py                  ← NUEVO: query + handler + DTO
  infrastructure/
    repositories/
      resultados_competencia_adapter.py   ← NUEVO: ACL lee BC Competencia
  api/
    router.py                             ← NUEVO: GET /resultados/{id}/ranking

src/app.py                                ← registrar resultados router
src/competencia/application/_p08_finalizacion.py  ← + callback on_finalizada
src/competencia/application/commands/asignar_tarjeta.py  ← + on_finalizada param
src/competencia/application/commands/registrar_dns.py    ← + on_finalizada param
src/competencia/api/router.py            ← inyectar callback de ranking en deps
```

---

## Tareas

### T1 — Domain BC Resultados: exceptions + EntradaRanking (~10 min)
- `ResultadosIncompletos` excepción de dominio.
- `EntradaRanking(posicion, atleta_id, rp, unidad, tarjeta, es_dns, en_podio)` frozen dataclass.

### T2 — Domain: ResultadoFinal DTO + ResultadosCompetenciaPort (~10 min)
- `ResultadoFinal(atleta_id, rp, unidad, tarjeta, es_dns)` DTO de entrada del ACL.
- ABC `ResultadosCompetenciaPort.get_resultados_finales(cid, disciplina)`.

### T3 — Domain: evento ResultadosCalculados (~10 min)
- Frozen dataclass extendiendo DomainEvent.
- Payload: `competencia_id`, `disciplina`, `total`, `entries` (tuple of dicts).
- `to_payload()` / `from_payload()`.

### T4 — Domain: RankingCompetencia aggregate (~20 min)
- Stream: `ranking-{competencia_id}-{disciplina.value}`.
- `calcular(resultados, descriptor)`:
  - Separa válidas (Blanca/Amarilla) de inválidas (DNS/Roja).
  - Ordena válidas: STA y distancia → RP desc (mayor es mejor para ambas).
  - Asigna posiciones con empate: comparten pos, salta la siguiente.
  - Marca podio: pos 1, 2, 3 (empates incluidos en esa posición).
  - Inválidas al final, sin posición numérica significativa (pos = último_valido + 1..N).
- `_apply_stored` registra `ResultadosCalculados`.

### T5 — Infrastructure: ResultadosCompetenciaAdapter (ACL) (~15 min)
- Lee streams `performance-{cid}-*` del event store de BC Competencia.
- Reconstituye cada `Performance` (usa `Performance.reconstitute()`).
- Filtra por disciplina.
- Extrae `rp`, `tarjeta`, `es_dns`, `unidad` (de `performance.ap.unidad`).
- Retorna `list[ResultadoFinal]`.

### T6 — Application: CalcularRankingHandler (~15 min)
- `CalcularRankingCommand(competencia_id, disciplina)`.
- Handler carga resultados via ACL port → construye aggregate → llama `calcular()` → persiste.
- `DisciplinaDescriptor` inyectado para ordenamiento.

### T7 — Application: ObtenerRankingHandler (~10 min)
- `ObtenerRankingQuery(competencia_id, disciplina)`.
- Lee stream `ranking-{cid}-{disc}`, extrae entries de `ResultadosCalculados`.
- Retorna `list[RankingEntradaDTO]`.

### T8 — API: router BC Resultados + registro en app.py (~10 min)
- `GET /resultados/{competencia_id}/ranking?disciplina=STA`.
- Registrar en `src/app.py`.

### T9 — Integración P-08 → CalcularRanking (~15 min)
- `_p08_finalizacion.py`: añadir parámetro `on_finalizada: Callable | None = None`.
- Llama `await on_finalizada(competencia_id, disciplina)` si presente y finalizó.
- `AsignarTarjetaHandler` y `RegistrarDNSHandler`: pasar `on_finalizada`.
- `router.py` de BC Competencia: inyectar callback que instancia `CalcularRankingHandler`.

---

## Notas de diseño

- **Ordenamiento STA y distancia**: ambas disciplinas se ordenan RP mayor → menor. STA (más tiempo = mejor) y distancia (más metros = mejor) son equivalentes con la misma regla.
- **unidad del RP**: Performance no almacena la unidad del RP. Se usa `performance.ap.unidad` (mismo tipo de medida que el AP declarado).
- **Integración SP2**: callback `on_finalizada` en `_p08_finalizacion.py` — BC Competencia nunca importa de BC Resultados. El router lo inyecta.
- **DB BC Resultados**: `data/resultados.db` (ADR-007). El ACL lee de `data/competencia.db` via event store inyectado.
- **Podio con empates**: si dos atletas empatan en posición 2, ambos tienen `en_podio=True`.
