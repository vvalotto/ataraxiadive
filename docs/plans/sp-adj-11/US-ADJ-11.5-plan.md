# Plan de Implementación — US-ADJ-11.5
# BC Registro: entidad Organizador

**Fecha:** 2026-05-16
**Branch:** feature/US-ADJ-11.5-organizador
**Patrón de referencia:** US-ADJ-11.4 (Juez) — misma estructura, diferente semántica en `actualizar()`

---

## Resumen de artefactos

| # | Tarea | Archivo | Tipo |
|---|-------|---------|------|
| T1 | Aggregate `Organizador` | `src/registro/domain/aggregates/organizador.py` | Nuevo |
| T2 | Port `OrganizadorRepositoryPort` | `src/registro/domain/ports/organizador_repository_port.py` | Nuevo |
| T3 | Excepciones `OrganizadorNoEncontrado` / `OrganizadorYaRegistrado` | `src/registro/domain/exceptions.py` | Modificar |
| T4 | Repo `SQLiteOrganizadorRepository` | `src/registro/infrastructure/repositories/sqlite_organizador_repository.py` | Nuevo |
| T5 | Command `RegistrarOrganizadorCommand` + Handler | `src/registro/application/commands/registrar_organizador.py` | Nuevo |
| T6 | Command `ActualizarOrganizadorCommand` + Handler | `src/registro/application/commands/actualizar_organizador.py` | Nuevo |
| T7 | Query `ObtenerOrganizadorHandler` | `src/registro/application/queries/obtener_organizador.py` | Nuevo |
| T8 | Schemas + 3 endpoints en router | `src/registro/api/router.py` | Modificar |

---

## Decisiones de diseño

### `actualizar()` — semántica distinta a Juez

En `Juez.actualizar()`, `None` significa "no cambiar" (sentinel implícito).
Para `Organizador`, el único campo opcional es `nombre_organizacion`, y el cliente
puede querer limpiarlo a null explícitamente.

**Solución:** patch parcial en capa API. El router usa `_UNSET = object()` para
distinguir campo ausente de `null` explícito. El command siempre recibe el valor
final (ya resuelto). El domain recibe el valor definitivo en `actualizar()` sin
necesidad de sentinel — simplemente asigna lo que llega.

```python
# Router: mapear body a valor final
_UNSET = object()

class ActualizarOrganizadorMeRequest(BaseModel):
    nombre_organizacion: str | None = _UNSET  # campo ausente → _UNSET

# En el endpoint:
if body.nombre_organizacion is _UNSET:
    nombre_final = organizador_actual.nombre_organizacion  # sin cambio
else:
    nombre_final = body.nombre_organizacion  # puede ser None (limpiar)
```

> **Nota:** Pydantic no acepta `object()` como default directo. La implementación
> usa `model_fields_set` para detectar qué campos fueron enviados en el JSON.

### `_repo_organizador()` — helper en router

Mismo patrón que `_juez_repo()`. No hay dependencia FastAPI para inyectar el repo
de organizador en otros endpoints — solo se usa en los 3 endpoints propios.

---

## Estimación

| Tarea | Estimado |
|-------|----------|
| T1–T3 Domain | 10 min |
| T4 Infrastructure | 10 min |
| T5–T7 Application | 10 min |
| T8 API (schemas + endpoints + patch parcial) | 20 min |
| **Total implementación** | **~50 min** |
| Tests unitarios (Fase 4) | 20 min |
| Tests integración (Fase 5) | 15 min |
| BDD steps (Fase 6) | 20 min |
| Quality gates (Fase 7) | 5 min |
| **Total estimado** | **~110 min** |
