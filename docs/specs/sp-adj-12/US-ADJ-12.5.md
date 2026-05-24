---
us_id: US-ADJ-12.5
rf_ids: []
type: feature-backend
---

# US-ADJ-12.5 — BC Registro: inscripción con estado de aceptación

| Campo | Valor |
|-------|-------|
| **ID** | US-ADJ-12.5 |
| **Sprint** | SP-ADJ-12 |
| **Tipo** | feature backend |
| **Issue** | #202 |
| **Prioridad** | Media |
| **Área** | `registro` — domain · infrastructure · api |

---

## Descripción

El organizador necesita poder aceptar o rechazar inscripciones individuales para gestionar la participación en el torneo. Actualmente todas las inscripciones quedan en estado implícitamente aceptado sin control explícito.

---

## Precondición

- Existe al menos una inscripción activa en BC Registro.
- El organizador tiene JWT con rol ORGANIZADOR.

## Postcondición

- `Inscripcion` tiene campo `estado_aceptacion: EstadoAceptacion` (enum `ACEPTADO` / `RECHAZADO`).
- Todas las inscripciones nuevas tienen `estado_aceptacion = ACEPTADO` por defecto.
- Inscripciones existentes en SQLite quedan con `estado_aceptacion = 'ACEPTADO'` (migración automática).
- El endpoint `PATCH /registro/inscripciones/{id}/aceptacion` permite al organizador cambiar el estado.
- El endpoint `GET /registro/inscripciones/{id}/detalle` devuelve datos completos del atleta + estado_aceptacion + URLs de adjuntos.
- El endpoint `GET /registro/torneos/{id}/inscriptos-detalle` incluye `estado_aceptacion` en cada item.

## Invariantes

- INV-ACC-01: `estado_aceptacion` solo puede ser `ACEPTADO` o `RECHAZADO`.
- INV-ACC-02: El PATCH requiere rol ORGANIZADOR; ATLETA recibe 403.
- INV-ACC-03: El valor por defecto al inscribirse es siempre `ACEPTADO`.
- INV-ACC-04: La migración de columna no destruye datos existentes.

---

## Criterios de Aceptación

1. **Default ACEPTADO:** Al inscribirse, `estado_aceptacion` es `ACEPTADO`.
2. **PATCH cambia estado:** `PATCH /inscripciones/{id}/aceptacion` con `{estado: "RECHAZADO"}` actualiza el campo y persiste.
3. **Re-aceptación:** Se puede volver a `ACEPTADO` desde `RECHAZADO`.
4. **Autorización:** Solo ORGANIZADOR puede usar el PATCH. ATLETA recibe 403.
5. **GET detalle:** Devuelve nombre, apellido, categoría, club, brevet, dni, teléfono, estado_aceptacion, apto_medico_url, constancia_pago_url.
6. **listar_inscriptos_detalle incluye estado_aceptacion:** Cada item del listado tiene el campo.
7. **Migración automática:** Instancias existentes de SQLite adquieren columna con DEFAULT `'ACEPTADO'`.

---

## Implementación

### 1. VO `EstadoAceptacion`

```python
# src/registro/domain/value_objects/estado_aceptacion.py
class EstadoAceptacion(StrEnum):
    ACEPTADO = "ACEPTADO"
    RECHAZADO = "RECHAZADO"
```

### 2. `Inscripcion` aggregate

- Campo: `estado_aceptacion: EstadoAceptacion = EstadoAceptacion.ACEPTADO`
- `from_row`: leer `data.get("estado_aceptacion") or "ACEPTADO"`
- Método: `cambiar_aceptacion(nuevo_estado: EstadoAceptacion) -> None`

### 3. `SQLiteInscripcionRepository`

- `_CREATE_TABLE`: agregar columna `estado_aceptacion TEXT NOT NULL DEFAULT 'ACEPTADO'`
- `_ensure_schema`: `ALTER TABLE ... ADD COLUMN estado_aceptacion ...`
- `_UPSERT_INSCRIPCION`: incluir columna y valor
- `_inscripcion_to_values`: agregar `inscripcion.estado_aceptacion.value`

### 4. Application command

```
src/registro/application/commands/cambiar_aceptacion_inscripcion.py
→ CambiarAceptacionInscripcionCommand + CambiarAceptacionInscripcionHandler
```

### 5. API

- Schema `CambiarAceptacionRequest`: `{estado: EstadoAceptacion}`
- Schema `InscripcionDetalleResponse`: datos atleta + estado_aceptacion + URLs adjuntos
- `InscriptoDetalleResponse`: agregar campo `estado_aceptacion`
- `PATCH /inscripciones/{id}/aceptacion` → requiere `OrganizadorDep`
- `GET /inscripciones/{id}/detalle` → requiere `OrganizadorDep`
- `listar_inscriptos_detalle`: incluir `estado_aceptacion` en response

---

## Tests

- **Unit:** `test_inscripcion.py` — estado default, cambiar_aceptacion, from_row con campo nuevo
- **Unit:** `test_cambiar_aceptacion_handler.py` — handler happy path y not found
- **Integration:** `test_sqlite_inscripcion_repository.py` — persistencia y migración
- **Integration:** `test_aceptacion_endpoint.py` — PATCH y GET endpoints + autorización
- **BDD:** `US-ADJ-12.5-registro-estado-aceptacion.feature`

---

## Archivos modificados/creados

| Archivo | Cambio |
|---------|--------|
| `src/registro/domain/value_objects/estado_aceptacion.py` | Nuevo VO |
| `src/registro/domain/aggregates/inscripcion.py` | Campo + método cambiar_aceptacion |
| `src/registro/infrastructure/repositories/sqlite_inscripcion_repository.py` | Migración + UPSERT |
| `src/registro/application/commands/cambiar_aceptacion_inscripcion.py` | Nuevo command handler |
| `src/registro/api/router.py` | Schemas + 2 endpoints nuevos + update InscriptoDetalleResponse |
