# Plan de Implementación — US-2.4.1: Competencia Finalizada (automático)

**Fecha:** 2026-03-27
**Branch:** feature/US-2.4.1-competencia-finalizada
**Incremento:** Inc 2.4 — El Ranking

---

## Arquitectura afectada

```
domain/
  exceptions.py              ← + CompetenciaNoFinalizable
  events/
    competencia_finalizada.py  ← NUEVO
  aggregates/
    competencia.py             ← + finalizar() + _apply_competencia_finalizada
  ports/
    performances_estado_port.py  ← NUEVO (PerformancesEstadoData + port)

infrastructure/
  repositories/
    performances_estado_adapter.py  ← NUEVO

application/
  commands/
    asignar_tarjeta.py  ← + P-08 trigger (opt-in via port)
    registrar_dns.py    ← + P-08 trigger (opt-in via port)

api/
  router.py  ← + inyección PerformancesEstadoAdapter en asignar_tarjeta y registrar_dns
```

---

## Tareas

### T1 — Domain: CompetenciaNoFinalizable en exceptions.py (~5 min)
- Agregar la excepción al módulo de excepciones de dominio.

### T2 — Domain: evento CompetenciaFinalizada (~10 min)
- Nuevo frozen dataclass con campos: `competencia_id`, `disciplina`, `total_performances`, `ejecutadas`, `dns_count`, `finalizada_en`.
- Métodos `to_payload()` y `from_payload()`.

### T3 — Domain: PerformancesEstadoPort (~10 min)
- DTO `PerformancesEstadoData(total, ejecutadas, dns_count)` con property `todas_finalizadas`.
- ABC `PerformancesEstadoPort` con método `get_estado(competencia_id, disciplina) -> PerformancesEstadoData`.

### T4 — Domain: Competencia.finalizar() (~10 min)
- Método recibe `total_performances`, `ejecutadas`, `dns_count`.
- Guarda `CompetenciaNoFinalizable` si ejecutadas + dns_count < total_performances.
- Emite `CompetenciaFinalizada`.
- Registra `_apply_competencia_finalizada` en `_apply_stored`.

### T5 — Infrastructure: PerformancesEstadoAdapter (~15 min)
- Carga todos los streams `performance-{cid}-*`.
- Filtra por disciplina.
- Cuenta: `total`, `ejecutadas` (estado Ejecutada), `dns_count` (estado DNS).
- Implementa `get_estado()`.

### T6 — Application: P-08 en AsignarTarjetaHandler (~15 min)
- Ctor acepta `performances_estado: PerformancesEstadoPort | None = None`.
- Tras persistir TarjetaAsignada: si port presente → `get_estado()` → si `todas_finalizadas` → cargar Competencia → `finalizar()` → persistir CompetenciaFinalizada.
- Pattern idéntico al usado en US-2.3.1 (AndarivelesActivosPort).

### T7 — Application: P-08 en RegistrarDNSHandler (~10 min)
- Mismo patrón que T6.

### T8 — API: inyección en router.py (~10 min)
- Crear deps `get_performances_estado_adapter()` y `get_performances_estado_handler_dep()`.
- Actualizar endpoints `POST /asignar-tarjeta` y `POST /registrar-dns` para inyectar el adapter.

---

## Notas de diseño

- **Backward compat**: port opcional — handlers existentes sin port no ejecutan P-08.
- **Stream Competencia**: `competencia-{competencia_id}` — ya existe en `iniciar_competencia.py`.
- **EstadoCompetencia.Finalizada**: ya definida en `estado_competencia.py` — no requiere modificación.
- **Carga de Competencia**: necesita `disciplina` que viene del command (ya disponible en ambos handlers).
