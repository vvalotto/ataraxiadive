# Plan Técnico — US-ADJ-6.3
## OCP — Eliminar `inspect.signature` en `_p08_finalizacion.py`

*Generado: 2026-04-17 — Fase 2 /implement-us US-ADJ-6.3*

---

## Situación actual

El callback `on_finalizada` tiene dos firmas en uso:

| Lugar | Firma |
|-------|-------|
| `app.py` (producción) | `(competencia_id, disciplina, torneo_id=None)` — 3 params |
| `tests/uat/sp2/seed_competencia.py` | `(competencia_id, disciplina)` — 2 params |
| `tests/uat/sp3/seed_sp3.py` | `(competencia_id, disciplina, torneo_id_cb=None)` — 3 params |

`_p08_finalizacion.py` usa `inspect.signature` para ramificar entre 2 y 3 params.

---

## Solución

### T1 — Unificar la llamada en `_p08_finalizacion.py`

Siempre llamar con 3 params. Eliminar `inspect` y el condicional:

```python
# ANTES
parametros = inspect.signature(on_finalizada).parameters
if len(parametros) >= 3:
    await on_finalizada(competencia_id, disciplina, competencia.torneo_id)
else:
    await on_finalizada(competencia_id, disciplina)

# DESPUÉS
await on_finalizada(competencia_id, disciplina, competencia.torneo_id)
```

Actualizar el type hint de `on_finalizada` de `Callable[..., Awaitable[None]]`
a `Callable[[UUID, Disciplina, UUID | None], Awaitable[None]]`.

Eliminar `import inspect`.

### T2 — Actualizar `tests/uat/sp2/seed_competencia.py`

Agregar el tercer parámetro opcional al callback de 2 params:

```python
async def on_finalizada(
    competencia_id: UUID, disciplina: Disciplina, _torneo_id: UUID | None = None
) -> None:
```

### T3 — Actualizar type hints en los 3 handlers

En `asignar_tarjeta.py`, `registrar_dns.py`, `resolver_revision.py`:
- Cambiar `Callable[..., Awaitable[None]]` por `Callable[[UUID, Disciplina, UUID | None], Awaitable[None]]`

---

## Archivos afectados

| Archivo | Cambio |
|---------|--------|
| `src/competencia/application/_p08_finalizacion.py` | T1 — eliminar inspect, unificar llamada, tipo explícito |
| `src/competencia/application/commands/asignar_tarjeta.py` | T3 — type hint |
| `src/competencia/application/commands/registrar_dns.py` | T3 — type hint |
| `src/competencia/application/commands/resolver_revision.py` | T3 — type hint |
| `tests/uat/sp2/seed_competencia.py` | T2 — agregar 3er param opcional |

## Estimación

| Tarea | Estimado |
|-------|----------|
| T1 | 10 min |
| T2 + T3 | 5 min |
| Tests + CodeGuard | 10 min |
| **Total** | **25 min** |
