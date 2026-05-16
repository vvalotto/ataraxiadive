# Plan de Implementación — US-ADJ-11.10
# Creación automática de perfiles BC Registro al registrarse

**Fecha:** 2026-05-16  
**Track:** Formal — toca `src/identidad/` y `src/registro/`  
**Estimación:** 5 puntos (~150 min)  
**Branch:** `feature/US-ADJ-11.10-perfiles-registro`

---

## Orden de implementación (dependencias)

```
T1 → T2 → T3 → T4 → T5 → T6 → T7 → T8 → T9
```

---

## Tareas

### T1 — `src/identidad/domain/ports/perfil_registro_port.py` (~10 min)
Puerto ABC nuevo en BC Identidad:
```python
class PerfilRegistroPort(ABC):
    async def crear_perfiles(
        self, usuario_id: UUID, nombre: str, apellido: str, email: str,
        roles: list[Rol],
        numero_licencia: str | None, federacion: str | None,
        nombre_organizacion: str | None,
    ) -> None: ...
```

### T2 — `src/registro/domain/aggregates/atleta.py` (~15 min)
- `fecha_nacimiento: date` → `fecha_nacimiento: date | None = None`
- INV-A-04 se valida solo si `fecha_nacimiento is not None`

### T3 — `src/registro/application/commands/registrar_atleta.py` (~10 min)
- `fecha_nacimiento: date | None = None`

### T4 — `src/registro/infrastructure/repositories/sqlite_atleta_repository.py` (~20 min)
- DDL: `fecha_nacimiento TEXT` (quitar `NOT NULL`)
- `save()`: `atleta.fecha_nacimiento.isoformat() if atleta.fecha_nacimiento else None`
- `_row_to_atleta()`: `date.fromisoformat(row[4]) if row[4] else None`
- `_ensure_columns()`: migración de columna (alter no necesario — ya existe)

### T5 — `src/registro/infrastructure/perfil_registro_adapter.py` (~25 min)
Nuevo adapter que implementa `PerfilRegistroPort`:
- Por cada rol en `roles`: crea el perfil correspondiente usando el handler
- Captura `AtletaYaRegistrado`, `JuezYaRegistrado`, `OrganizadorYaRegistrado` → idempotencia
- Recibe repos de Atleta, Juez y Organizador como dependencias

### T6 — `src/identidad/application/commands/registrar_usuario.py` (~20 min)
- Ampliar `RegistrarUsuarioCommand` con campos opcionales:
  `numero_licencia`, `federacion`, `nombre_organizacion`
- `RegistrarUsuarioHandler.__init__` recibe `perfil_registro: PerfilRegistroPort | None = None`
- En `handle()`, después de `await self._repo.save(usuario)`, llamar `perfil_registro.crear_perfiles(...)`

### T7 — `src/identidad/api/router.py` (~15 min)
- Ampliar `RegistroRequest` con campos opcionales:
  `numero_licencia`, `federacion`, `nombre_organizacion`
- Pasar al `RegistrarUsuarioCommand`

### T8 — `src/identidad/api/dependencies.py` (~15 min)
- Agregar `_perfil_registro: PerfilRegistroPort | None`
- Agregar `get_perfil_registro()` dependency
- Ampliar `configure_identity_dependencies()` con `perfil_registro`

### T9 — `src/app.py` (~20 min)
- Instanciar `PerfilRegistroAdapter` con repos de Atleta, Juez, Organizador
- Pasarlo a `configure_identity_dependencies(perfil_registro=...)`

---

## Criterios de Done

- [ ] Puerto `PerfilRegistroPort` en `src/identidad/domain/ports/`
- [ ] `Atleta.fecha_nacimiento` opcional — INV-A-04 condicional
- [ ] `RegistrarAtletaCommand.fecha_nacimiento` opcional
- [ ] Repository SQLite soporta `fecha_nacimiento` null
- [ ] `PerfilRegistroAdapter` crea perfiles por rol
- [ ] `RegistrarUsuarioHandler` llama el puerto post-registro
- [ ] `RegistroRequest` acepta campos opcionales de Juez/Organizador
- [ ] Tests unitarios actualizados y pasando
- [ ] Tests de integración actualizados y pasando
- [ ] `pytest tests/` sin errores

---

## Notas

- El adapter vive en `src/registro/infrastructure/` e implementa un puerto de BC Identidad — esto es el patrón ACL correcto: la implementación está en el BC consumidor.
- `PerfilRegistroPort` es `None` en tests de identidad — el handler lo acepta opcional para no romper tests existentes.
- La migración de `fecha_nacimiento` en SQLite es compatible: filas existentes tienen el valor, filas nuevas pueden tener NULL.
