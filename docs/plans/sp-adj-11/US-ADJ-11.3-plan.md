# Plan de Implementación — US-ADJ-11.3

**Fecha:** 2026-05-16
**Branch:** feature/US-ADJ-11.3-atleta-refactor
**Estimación total:** 48 min

---

## Análisis de Impacto

### Archivos a modificar
| Archivo | Tipo | Cambio |
|---------|------|--------|
| `src/registro/domain/aggregates/atleta.py` | Domain | `club`/`categoria` → opcionales; agregar `dni`/`telefono` |
| `src/registro/infrastructure/repositories/sqlite_atleta_repository.py` | Infra | Migración + 4 campos nuevos/cambiados |
| `src/registro/application/commands/registrar_atleta.py` | Application | Sin `atleta_id`; backend genera; check por email |
| `src/registro/application/commands/actualizar_atleta.py` | Application | Agregar `dni`/`telefono` |
| `src/registro/api/router.py` | API | Schemas + endpoints actualizados |

---

## Tareas

### T1 — Domain: Atleta aggregate [15 min]
- `club: str | None = None`, `categoria: Categoria | None = None`
- Agregar `dni: str | None = None`, `telefono: str | None = None`
- `__post_init__`: remover validación "club no vacío" como obligatorio; si `club` provisto y ≠ None → no puede ser vacío/espacios (INV-11.3-04). Mismo para `dni` y `telefono` (INV-11.3-05).
- `actualizar()`: agregar `dni`/`telefono`; misma lógica de patch parcial

### T2 — Infrastructure: SQLiteAtletaRepository [10 min]
- `_CREATE_TABLE`: `categoria TEXT`, `club TEXT` (sin NOT NULL)
- Agregar `_ensure_columns(conn)`: `ALTER TABLE atletas ADD COLUMN dni TEXT` + `telefono TEXT` si no existen
- `save()`: incluir `dni`, `telefono`
- `find_by_id` / `find_by_email`: SELECT con columnas nombradas incluyendo `dni`, `telefono`
- `_row_to_atleta()`: mapear 10 columnas

### T3 — Application: RegistrarAtletaCommand/Handler [8 min]
- Quitar `atleta_id` del command dataclass
- `club`, `categoria` opcionales; agregar `dni: str | None`, `telefono: str | None`
- Handler: `find_by_email(cmd.email)` → si existe raise `AtletaYaRegistrado`; `atleta_id = uuid4()`; retorna `atleta_id`

### T4 — Application: ActualizarAtletaCommand/Handler [5 min]
- Agregar `dni: str | None = None`, `telefono: str | None = None`
- Handler: pasar a `atleta.actualizar(dni=cmd.dni, telefono=cmd.telefono)`

### T5 — API: router.py [10 min]
- `RegistrarAtletaRequest`: quitar `atleta_id`; `club`/`categoria` opcionales; agregar `dni`/`telefono`
- `AtletaResponse`: agregar `dni: str | None`, `telefono: str | None`
- `ActualizarAtletaMeRequest`: agregar `dni: str | None = None`, `telefono: str | None = None`
- `InscriptoDetalleResponse.categoria`: `Categoria | None`
- Endpoint `registrar_atleta`: construir cmd sin `atleta_id`
- Endpoint `actualizar_atleta_me`: pasar `dni`/`telefono` al cmd

---

## Orden de ejecución

```
T1 (domain) → T2 (infra) → T3 (app registrar) → T4 (app actualizar) → T5 (api)
```

## Riesgos

- **Migración DB:** `ALTER TABLE ADD COLUMN` falla silenciosamente en SQLite si la columna ya existe → usar `try/except OperationalError` dentro de `_ensure_columns`
- **`_row_to_atleta` por posición:** Los SELECTs actuales usan posición — cambiar a columnas nombradas para no romper con el nuevo orden
- **`find_by_email` en handler de registro:** El repositorio actual tiene `UNIQUE` implícito sólo en `email` a nivel de negocio (no hay constraint SQL) — agregar constraint en `_CREATE_TABLE`
