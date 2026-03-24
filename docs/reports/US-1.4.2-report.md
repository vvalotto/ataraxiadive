# Reporte de Implementación — US-1.4.2

| Campo | Valor |
|-------|-------|
| **US** | US-1.4.2 — Flujo Completo E2E: AP → Tarjeta |
| **Incremento** | 1.4 — Todo Conectado |
| **BC** | Competencia (Event Sourcing) |
| **Branch** | `feature/US-1.4.2-flujo-e2e` |
| **Fecha** | 2026-03-23 |
| **Tiempo real** | ~21 min |
| **Estimación** | 65 min |

---

## Métricas de Calidad

| Métrica | Valor | Umbral | Estado |
|---------|-------|--------|--------|
| Pylint (BC Competencia) | 9.55/10 | ≥ 8.0 | ✅ |
| Coverage total | 98% | ≥ 90% | ✅ |
| Tests pasando | 207/207 | 100% | ✅ |
| DesignReviewer CRITICAL | 0 | 0 | ✅ |

---

## Tests Implementados

| Tipo | Cantidad | Archivos |
|------|----------|---------|
| Unit | 5 | `test_obtener_eventos.py` |
| Integración | 7 | `test_flujo_e2e.py` |
| BDD | 6 | `US-1.4.2-flujo-e2e.feature` + `flujo_e2e_steps.py` |
| **Total nuevos** | **18** | |
| **Total acumulado SP1** | **207** | |

---

## Componentes Implementados

| Capa | Archivo | Descripción |
|------|---------|-------------|
| `domain/ports/` | `event_store_port.py` | `+load_all_events_ordered()` método abstracto |
| `infrastructure/event_store/` | `sqlite_event_store.py` | Implementación con SELECT ORDER BY id |
| `application/queries/` | `obtener_eventos.py` | `ObtenerEventosHandler` + `EventoDTO` |
| `api/` | `router.py` | `GET /competencia/{id}/events` |

---

## Escenarios BDD Cubiertos

1. ✅ Flujo completo para atleta con tarjeta blanca (AP → Llamar → Resultado → Tarjeta)
2. ✅ Flujo con DNS registrado
3. ✅ Corrección de resultado después de ejecutada
4. ✅ Flujo con black-out y distancia obligatoria (RF-EJ-07 verificado E2E)
5. ✅ Endpoint `/events` retorna traza completa en orden de secuencia
6. ✅ Read Models consistentes con Event Store (DoD SP1)

---

## Decisiones Técnicas

- **`load_all_events_ordered()`** usa `ORDER BY id ASC` (id autoincrement) para preservar el orden global de inserción — más fiel a la causalidad real que ordenar por `stream_id + version`.
- **`performance_id` en `EventoDTO`**: resultado de `stream_id.removeprefix(prefix)`, que retorna `{participante_id}-{disciplina}` — la clave natural de la performance en SP1.
- **Sin cambios al aggregate `Performance`**: toda la US opera en capa query/API — confirma que el dominio está completo para SP1.

---

## DoD SP1 Verificado

El test `test_progreso_consistente_con_event_store` confirma:
- 5 performances ejecutadas (A, B-DNS, C, D-corregida, E-blackout)
- Event Store con 18+ eventos en orden global
- Read Models consistentes con el Event Store

**SP1 — La Performance: DoD completo** ✅

---

## Observaciones Experimentales

Esta US demostró que la arquitectura hexagonal + Event Sourcing permite agregar
nuevas capacidades de lectura (audit log) sin tocar el dominio. El endpoint
`GET /events` emergió directamente del Event Store sin lógica adicional —
validando el principio de que el ES es la fuente de verdad observable.

**Tiempo real vs estimado:** 21 min vs 65 min estimados (-68%). La US era
predominantly read-side, sin nueva lógica de dominio, lo que explica la diferencia.
