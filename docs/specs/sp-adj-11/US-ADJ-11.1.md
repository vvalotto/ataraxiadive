# US-ADJ-11.1: BC Identidad — aggregate Usuario multi-rol + JWT + login/registro

**Estado**: `Especificada`
**Iteracion / Sprint**: SP-ADJ-11
**Tipo**: refactor backend + migración DB
**Agregado principal afectado**: `Usuario`
**Bounded Context**: `identidad`

---

## Descripcion (lenguaje de negocio)

Como **persona que participa en el mundo del apnea en múltiples roles**,
quiero poder registrarme con más de un rol en una única cuenta
para no necesitar dos emails distintos cuando soy juez y también compito.

---

## Contexto del dominio

### Problema

`Usuario.rol` es un campo de valor único. Un juez que compite necesita dos cuentas.
El login no tiene selector de rol. El JWT lleva `"rol"` asumiendo que hay uno solo.

### Modelo involucrado

| Elemento | Nombre | Responsabilidad |
|---|---|---|
| Aggregate | `Usuario` | Credenciales + lista de roles |
| Port | `TokenServicePort` | Genera JWT con el rol activo elegido |
| Infra | `JWTService` | Implementa generación con `rol_activo` explícito |
| Infra | `SQLiteUsuarioRepository` | Persiste `roles` como JSON; migración desde `rol` |
| Command | `RegistrarUsuarioCommand` | Acepta `roles: list[Rol]`; si email existe, agrega roles |
| Command | `AutenticarUsuarioCommand` | Acepta `rol_elegido: Rol \| None`; respuesta condicional |

---

## Especificacion del comportamiento

### Precondicion

- El sistema tiene usuarios existentes con columna `rol TEXT` en la DB.
- La migración se ejecuta automáticamente al arrancar (patrón `_ensure_column`).

### Postcondicion

- Todo `Usuario` tiene `roles: list[Rol]` con al menos un elemento.
- El JWT mantiene la estructura actual: `"rol": "<ROL_ACTIVO>"` — sin cambio en guards.
- Los usuarios existentes en DB tienen su `rol` original migrado a `roles: ["<ROL>"]`.

### Invariantes

| ID | Invariante |
|----|------------|
| INV-11.1-01 | `roles` no puede estar vacío — un usuario tiene al menos un rol. |
| INV-11.1-02 | Un usuario no puede tener el mismo rol más de una vez. |
| INV-11.1-03 | `ADMIN` no puede asignarse desde el endpoint de registro público. |
| INV-11.1-04 | El JWT lleva un único `"rol"` correspondiente al rol activo de la sesión. |
| INV-11.1-05 | Si `rol_elegido` se provee en el login, debe pertenecer a los roles del usuario. |
| INV-11.1-06 | Si el email ya existe en registro, se valida la contraseña antes de agregar roles. |

---

## Criterios de aceptacion

```gherkin
Feature: Registro y login con múltiples roles

  Scenario: Registro con un único rol — acceso directo al portal
    Given no existe ningún usuario con email "maria@test.com"
    When se registra con email "maria@test.com" y roles ["ATLETA"]
    Then el sistema crea el usuario con roles ["ATLETA"]
    And devuelve un token con "rol": "ATLETA"

  Scenario: Registro con múltiples roles — se requiere selección de rol al login
    Given no existe ningún usuario con email "carlos@test.com"
    When se registra con email "carlos@test.com" y roles ["JUEZ", "ATLETA"]
    Then el sistema crea el usuario con roles ["JUEZ", "ATLETA"]
    And la respuesta incluye "requires_role_selection": true y la lista de roles
    And no incluye access_token

  Scenario: Login con usuario de un único rol
    Given existe un usuario "ana@test.com" con roles ["ORGANIZADOR"]
    When hace login con email y contraseña correctos sin rol_elegido
    Then el sistema devuelve un token con "rol": "ORGANIZADOR"

  Scenario: Login con múltiples roles sin especificar rol_elegido
    Given existe un usuario "pedro@test.com" con roles ["JUEZ", "ATLETA"]
    When hace login con email y contraseña correctos sin rol_elegido
    Then la respuesta incluye "requires_role_selection": true
    And la respuesta incluye "roles": ["JUEZ", "ATLETA"]
    And no incluye access_token

  Scenario: Login con múltiples roles especificando rol_elegido
    Given existe un usuario "pedro@test.com" con roles ["JUEZ", "ATLETA"]
    When hace login con email, contraseña y rol_elegido "ATLETA"
    Then el sistema devuelve un token con "rol": "ATLETA"

  Scenario: Login con rol_elegido que el usuario no posee
    Given existe un usuario "pedro@test.com" con roles ["ATLETA"]
    When hace login con rol_elegido "JUEZ"
    Then el sistema retorna 401 con detalle "Credenciales inválidas"

  Scenario: Registro con email existente agrega roles nuevos
    Given existe un usuario "lucia@test.com" con roles ["ATLETA"] y contraseña "Apnea2024!"
    When se intenta registrar "lucia@test.com" con contraseña "Apnea2024!" y roles ["JUEZ"]
    Then el sistema agrega JUEZ al usuario existente — roles quedan ["ATLETA", "JUEZ"]
    And la respuesta incluye "requires_role_selection": true

  Scenario: Registro con email existente y contraseña incorrecta
    Given existe un usuario "lucia@test.com" con contraseña "Apnea2024!"
    When se intenta registrar "lucia@test.com" con contraseña "OtraClave1!" y roles ["JUEZ"]
    Then el sistema retorna 401 con detalle "Credenciales inválidas"

  Scenario: Registro con email existente y rol que ya posee
    Given existe un usuario "lucia@test.com" con roles ["ATLETA"]
    When se intenta registrar "lucia@test.com" con contraseña correcta y roles ["ATLETA"]
    Then el sistema retorna 409 con detalle "El usuario ya posee el rol ATLETA"

  Scenario: Migración de usuarios existentes con rol único
    Given la DB tiene un usuario con columna "rol" = "ORGANIZADOR"
    When el repositorio accede al usuario por primera vez
    Then el usuario es reconstituido con roles = ["ORGANIZADOR"]
```

---

## Impacto arquitectonico

**Esta US requiere una decision arquitectonica?**
- [x] No — ADR-020 ya documenta la decisión. Esta US implementa lo allí decidido.

**Capa(s) afectadas:**
- [x] Domain — `Usuario.roles: list[Rol]`
- [x] Infrastructure — `SQLiteUsuarioRepository` (migración + serialización JSON) · `JWTService`
- [x] Application — `RegistrarUsuarioCommand/Handler` · `AutenticarUsuarioCommand/Handler`
- [x] API — `router.py`: schemas `RegistroRequest.roles`, `LoginRequest.rol_elegido`, respuesta condicional

---

## Artefactos a modificar

| Artefacto | Cambio |
|-----------|--------|
| `src/identidad/domain/aggregates/usuario.py` | `rol: Rol` → `roles: list[Rol]`. Validar: no vacío, sin duplicados. |
| `src/identidad/domain/ports/token_service_port.py` | `generate(usuario, rol_activo: Rol) -> str` — agrega parámetro. |
| `src/identidad/infrastructure/jwt_service.py` | `generate(usuario, rol_activo)` usa `rol_activo.value` en el payload. |
| `src/identidad/infrastructure/repositories/sqlite_usuario_repository.py` | Columna `roles TEXT NOT NULL DEFAULT '["ATLETA"]'`. Migración: UPDATE existentes. `save`/`find` serializan/deserializan JSON. `list_by_rol` usa `JSON_EACH` o filtro Python. |
| `src/identidad/application/commands/registrar_usuario.py` | `RegistrarUsuarioCommand.roles: list[Rol]`. Handler: si email existe, valida password y agrega roles; si rol ya existe, lanza `RolYaAsignado`. |
| `src/identidad/application/commands/autenticar_usuario.py` | `AutenticarUsuarioCommand.rol_elegido: Rol \| None`. Handler: si 1 rol → genera token; si N roles y no hay `rol_elegido` → devuelve `RoleSelectionRequired`; si `rol_elegido` no está en roles → lanza `CredencialesInvalidas`. |
| `src/identidad/domain/exceptions.py` | Agregar `RolYaAsignado`, `RolNoEncontrado`. |
| `src/identidad/api/router.py` | `RegistroRequest.roles: list[Rol]`. `LoginRequest.rol_elegido: Rol \| None`. Respuesta login: `{"access_token":...}` o `{"requires_role_selection": true, "roles": [...]}`. `UsuarioResponse.roles`. `listar_usuarios` serializa lista. |

---

## Notas de implementacion

1. **Migración DB:** usar el patrón `_ensure_column` existente. Agregar una función `_migrate_rol_to_roles(conn)` que ejecuta `UPDATE usuarios SET roles = json_array(rol) WHERE roles IS NULL` solo si la columna nueva existe y `rol` también existe. Luego el `_ensure_column` de `rol` queda como legacy read-only — no eliminar la columna para no romper la migración incremental.

2. **Serialización JSON:** `json.dumps([r.value for r in usuario.roles])` al guardar. `[Rol(r) for r in json.loads(roles_str)]` al leer.

3. **`list_by_rol`:** SQLite no tiene `JSON_CONTAINS` nativo en versiones antiguas. Usar `WHERE roles LIKE '%"ATLETA"%'` como fallback simple — la cardinalidad es baja y no hay riesgo de falsos positivos dado que los valores del enum no son substrings entre sí.

4. **Respuesta condicional del login:** el handler devuelve una union type. El router la discrimina y elige el status/body apropiado. HTTP 200 en ambos casos — el frontend discrimina por presencia de `access_token`.

5. **Tests a actualizar:** todos los tests de `RegistrarUsuarioHandler` y `AutenticarUsuarioHandler` que usan `rol=Rol.ATLETA` deben actualizarse a `roles=[Rol.ATLETA]`.

---

*Spec creada: 2026-05-16 — BT-001 · ADR-020 · PLAN-SP-ADJ-11*
