# Plan Técnico — US-ADJ-6.2
## Eliminar ciclo ADP — `reconstituir_performance` como classmethod

*Generado: 2026-04-17 — Fase 2 /implement-us US-ADJ-6.2*

---

## Situación actual

`Performance.reconstitute()` ya existe como classmethod pero solo delega:

```python
# performance.py línea 473
return reconstituir_performance(events)
```

El ciclo ADP:
```
performance.py
  → importa reconstituir_performance de performance_state.py  (line 20)
performance_state.py
  → lazy import de Performance de performance.py  (dentro de reconstituir_performance)
```

---

## Solución

### T1 — Internalizar lógica en `Performance.reconstitute()`

Mover el cuerpo de `reconstituir_performance()` directamente al classmethod,
usando `performance_state.apply_stored()` y `performance_state.parse_payload()`
que ya no necesitan importar `Performance`.

```python
@classmethod
def reconstitute(cls, events: list[dict[str, Any]]) -> "Performance":
    if not events:
        raise ValueError("No se puede reconstituir Performance sin eventos")
    if events[0]["event_type"] != "APRegistrado":
        raise ValueError(
            f"El primer evento debe ser APRegistrado, recibido: {events[0]['event_type']}"
        )
    first_payload = performance_state.parse_payload(events[0]["payload"])
    performance = cls(
        performance_id=UUID(first_payload["performance_id"]),
        competencia_id=UUID(first_payload["competencia_id"]),
        participante_id=UUID(first_payload["participante_id"]),
        disciplina=Disciplina(first_payload["disciplina"]),
    )
    for event in events:
        performance_state.apply_stored(performance, event)
    return performance
```

### T2 — Ajustar import en `performance.py`

Cambiar:
```python
from competencia.domain.aggregates.performance_state import reconstituir_performance
```
Por:
```python
from competencia.domain.aggregates import performance_state
```

### T3 — Limpiar `performance_state.py`

Eliminar:
- La función `reconstituir_performance()` completa
- El bloque `if TYPE_CHECKING:` con el import de `Performance`

Las funciones `apply_*` y `apply_stored` permanecen intactas — no importan `Performance`.

---

## Archivos afectados

| Archivo | Cambio |
|---------|--------|
| `src/competencia/domain/aggregates/performance.py` | T1 + T2 |
| `src/competencia/domain/aggregates/performance_state.py` | T3 |

## Tests afectados

Tests existentes de `Performance.reconstitute()` son la red de seguridad — deben
pasar sin modificación.

## Estimación

| Tarea | Estimado |
|-------|----------|
| T1+T2+T3 | 15 min |
| Tests + CodeGuard | 10 min |
| **Total** | **25 min** |
