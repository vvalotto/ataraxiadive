# Reporte de Implementación — US-ADJ-11.10

**Historia:** Creación automática de perfiles BC Registro al registrarse  
**Sprint:** SP-ADJ-11  
**Track:** Formal — toca `src/identidad/` y `src/registro/`  
**Fecha:** 2026-05-16  
**Branch:** `feature/US-ADJ-11.10-perfiles-registro`

---

## Artefactos generados / modificados

| Artefacto | Tipo | Cambio |
|-----------|------|--------|
| `src/identidad/domain/ports/perfil_registro_port.py` | Nuevo | Puerto ABC `PerfilRegistroPort` |
| `src/registro/domain/aggregates/atleta.py` | Modificado | `fecha_nacimiento: date \| None = None`; INV-A-04 condicional |
| `src/registro/application/commands/registrar_atleta.py` | Modificado | `fecha_nacimiento: date \| None = None` |
| `src/registro/infrastructure/repositories/sqlite_atleta_repository.py` | Modificado | DDL sin NOT NULL; `save`/`_row_to_atleta` manejan null |
| `src/registro/infrastructure/perfil_registro_adapter.py` | Nuevo | Implementación del puerto — orquesta Atleta/Juez/Organizador handlers; idempotente |
| `src/identidad/application/commands/registrar_usuario.py` | Modificado | `RegistrarUsuarioCommand` con campos opcionales; handler llama `_crear_perfiles` |
| `src/identidad/api/router.py` | Modificado | `RegistroRequest` con campos opcionales; inyecta `perfil_registro` |
| `src/identidad/api/dependencies.py` | Modificado | `_perfil_registro` + `get_perfil_registro()` + `configure_identity_dependencies` ampliado |
| `src/app.py` | Modificado | Instancia `PerfilRegistroAdapter` y lo pasa a `configure_identity_dependencies` |
| `tests/unit/registro/test_perfil_registro_adapter.py` | Nuevo | 6 tests unitarios del adapter |
| `tests/features/steps/perfiles_registro_steps.py` | Nuevo | 6 tests BDD de escenarios |
| `tests/integration/registro/test_sqlite_atleta_repository.py` | Modificado | 2 tests nuevos para `fecha_nacimiento=None` |

---

## Invariantes implementadas

| ID | Invariante | Estado |
|----|------------|--------|
| INV-11.10-01 | ATLETA en roles → perfil Atleta creado | ✅ |
| INV-11.10-02 | JUEZ en roles → perfil Juez creado | ✅ |
| INV-11.10-03 | ORGANIZADOR en roles → perfil Organizador creado | ✅ |
| INV-11.10-04 | Fallo en creación → propagado al handler | ✅ |
| INV-11.10-05 | `fecha_nacimiento` opcional; INV-A-04 solo si presente | ✅ |
| INV-11.10-06 | Perfil ya existente → idempotente, sin error | ✅ |

---

## Quality Gates

| Gate | Resultado |
|------|-----------|
| Tests unitarios (registro + identidad) | ✅ 1016 pasando |
| Tests de integración (sin e2e pre-existente) | ✅ |
| Black + isort | ✅ |
| Import check (`from src.app import app`) | ✅ |

---

## Decisiones técnicas

1. **Puerto en BC Identidad, adapter en BC Registro:** el BC consumidor (Registro) implementa el puerto definido por el BC productor (Identidad). Cumple la regla de comunicación exclusivamente por puertos sin imports cruzados directos.

2. **`perfil_registro: PerfilRegistroPort | None`:** el handler acepta `None` para no romper tests existentes de identidad que no necesitan el adapter.

3. **Idempotencia vía captura de excepciones:** el adapter captura `AtletaYaRegistrado`, `JuezYaRegistrado`, `OrganizadorYaRegistrado` y continúa — compatible con reintentos y con el flujo de "agregar rol" a un usuario existente.

4. **`fecha_nacimiento` nullable en SQLite:** la columna DDL pasa de `NOT NULL` a nullable. Las filas existentes conservan sus valores. El `_ensure_columns` no necesita migración de columna — solo el DDL del `CREATE TABLE IF NOT EXISTS` es relevante para DBs nuevas.

---

*Generado: 2026-05-16 · /implement-us US-ADJ-11.10*
