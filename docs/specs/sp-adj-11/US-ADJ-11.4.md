# US-ADJ-11.4: BC Registro — entidad Juez

**Estado**: `Especificada`
**Iteracion / Sprint**: SP-ADJ-11
**Tipo**: nueva entidad backend
**Agregado principal afectado**: `Juez` (nuevo)
**Bounded Context**: `registro`
**Dependencia**: US-ADJ-11.1 (JWT con rol JUEZ); paralela a US-ADJ-11.3 y 11.5

---

## Descripcion (lenguaje de negocio)

Como **usuario con rol JUEZ**,
quiero poder crear mi perfil de juez con mis datos de licencia
para que el organizador los tenga disponibles al asignarme a un torneo.

Como **usuario con rol JUEZ**,
quiero poder actualizar mi número de licencia y federación desde "Mis Datos"
para mantener mi información al día.

---

## Contexto del dominio

### Problema

El BC Registro solo modela al `Atleta`. Un usuario con rol JUEZ (post US-ADJ-11.1) no tiene dónde persistir sus datos específicos: número de licencia y federación a la que pertenece. El organizador necesita estos datos al validar a los jueces de un torneo.

### Modelo involucrado

| Elemento | Nombre | Responsabilidad |
|---|---|---|
| Aggregate | `Juez` | Datos de perfil del juez: licencia y federación |
| Port | `JuezRepositoryPort` | Contrato de persistencia |
| Infra | `SQLiteJuezRepository` | Tabla `jueces` en `registro.db` |
| Command | `RegistrarJuezCommand` | Crea el perfil Juez para un usuario con rol JUEZ |
| Command | `ActualizarJuezCommand` | Actualiza `numero_licencia` y `federacion` |
| Query | `ObtenerJuezHandler` | Recupera el perfil Juez por email |
| API | `router.py` | Tres endpoints bajo `/registro/jueces` |

---

## Especificacion del comportamiento

### Precondicion

- El usuario está autenticado con JWT que incluye `"rol": "JUEZ"`.
- Para `POST /registro/jueces`: no existe aún un perfil Juez para ese email.

### Postcondicion

- Existe un registro en la tabla `jueces` asociado al email del usuario.
- `numero_licencia` y `federacion` pueden ser `None` — el perfil es válido sin ellos.

### Invariantes

| ID | Invariante |
|----|------------|
| INV-11.4-01 | `email` debe tener formato válido — no puede ser vacío. |
| INV-11.4-02 | No pueden existir dos perfiles Juez con el mismo `email`. |
| INV-11.4-03 | Si `numero_licencia` se provee, no puede ser string vacío. |
| INV-11.4-04 | Si `federacion` se provee, no puede ser string vacío. |
| INV-11.4-05 | Solo usuarios con JWT válido y rol JUEZ pueden crear o modificar su perfil. |

---

## Criterios de aceptacion

```gherkin
Feature: Perfil Juez — creación y actualización

  Scenario: Crear perfil Juez con datos mínimos
    Given existe un usuario autenticado con rol JUEZ y email "juez@test.com"
    And no existe perfil Juez para "juez@test.com"
    When hace POST /registro/jueces con {} (body vacío)
    Then el sistema crea el perfil Juez con numero_licencia=null y federacion=null
    And retorna 201 con el juez_id generado

  Scenario: Crear perfil Juez con datos completos
    Given existe un usuario autenticado con rol JUEZ y email "juez2@test.com"
    When hace POST /registro/jueces con {"numero_licencia": "ARG-001", "federacion": "AIDA"}
    Then el sistema crea el perfil con los datos informados
    And retorna 201

  Scenario: Intentar crear perfil Juez cuando ya existe uno
    Given existe un perfil Juez para "juez@test.com"
    When hace POST /registro/jueces
    Then el sistema retorna 409 con detalle "Perfil de juez ya registrado"

  Scenario: Obtener perfil Juez propio
    Given existe un perfil Juez para "juez@test.com"
    When hace GET /registro/jueces/me
    Then el sistema retorna 200 con los datos del perfil Juez

  Scenario: Obtener perfil Juez cuando no existe
    Given no existe perfil Juez para "juez@test.com"
    When hace GET /registro/jueces/me
    Then el sistema retorna 404 con detalle "Juez no encontrado"

  Scenario: Actualizar numero de licencia
    Given existe un perfil Juez para "juez@test.com" con numero_licencia=null
    When hace PATCH /registro/jueces/me con {"numero_licencia": "ARG-042"}
    Then el perfil queda con numero_licencia="ARG-042"
    And retorna 200 con el perfil actualizado

  Scenario: Usuario sin rol JUEZ no puede crear perfil Juez
    Given existe un usuario autenticado con rol ATLETA
    When hace POST /registro/jueces
    Then el sistema retorna 403
```

---

## Impacto arquitectonico

**Esta US requiere una decision arquitectonica?**
- [x] No — sigue el mismo patrón que `Atleta`: aggregate + port + repo SQLite + commands + query + endpoints.

**Capa(s) afectadas:**
- [x] Domain — nuevo aggregate `Juez` + nuevo port `JuezRepositoryPort`
- [x] Infrastructure — `SQLiteJuezRepository` (tabla `jueces` en `registro.db`)
- [x] Application — `RegistrarJuezCommand/Handler` · `ActualizarJuezCommand/Handler` · `ObtenerJuezHandler`
- [x] API — tres endpoints en `router.py` de BC Registro

---

## Artefactos a crear / modificar

| Artefacto | Cambio |
|-----------|--------|
| `src/registro/domain/aggregates/juez.py` | Nuevo. `Juez(juez_id: UUID, email: str, numero_licencia: str \| None, federacion: str \| None)`. `__post_init__` valida email y que campos opcionales no sean string vacío. `actualizar(numero_licencia, federacion)` con lógica de patch parcial. |
| `src/registro/domain/ports/juez_repository_port.py` | Nuevo. `JuezRepositoryPort` (ABC): `save(juez)`, `find_by_email(email) -> Juez \| None`, `find_by_id(juez_id) -> Juez \| None`. |
| `src/registro/domain/exceptions.py` | Agregar `JuezNoEncontrado`, `JuezYaRegistrado`. |
| `src/registro/infrastructure/repositories/sqlite_juez_repository.py` | Nuevo. Tabla `jueces(juez_id TEXT PK, email TEXT UNIQUE, numero_licencia TEXT, federacion TEXT)`. `_ensure_table(conn)`. Implementa `JuezRepositoryPort`. |
| `src/registro/application/commands/registrar_juez.py` | Nuevo. `RegistrarJuezCommand(email, numero_licencia, federacion)`. Handler genera `juez_id = uuid4()`, lanza `JuezYaRegistrado` si ya existe. |
| `src/registro/application/commands/actualizar_juez.py` | Nuevo. `ActualizarJuezCommand(email, numero_licencia, federacion)`. Handler: load por email, llama `actualizar()`, guarda. Lanza `JuezNoEncontrado`. |
| `src/registro/application/queries/obtener_juez.py` | Nuevo. `ObtenerJuezHandler(repo)`: `handle(email) -> Juez`. Lanza `JuezNoEncontrado`. |
| `src/registro/api/router.py` | Agregar schemas `RegistrarJuezRequest`, `JuezResponse`, `ActualizarJuezMeRequest`. Agregar tres endpoints: `POST /registro/jueces` (JuezDep), `GET /registro/jueces/me` (JuezDep), `PATCH /registro/jueces/me` (JuezDep). |

---

## Notas de implementacion

1. **`JuezDep`:** usar el patrón de `AtletaDep` en `shared/api/dependencies.py`. Agregar `JuezDep = Annotated[dict, Depends(require_rol(Rol.JUEZ))]`. Verificar si `require_rol` ya existe en `shared/api/dependencies.py` o si está en `identidad/api/dependencies.py` — importar desde donde corresponda sin violar la arquitectura hexagonal.

2. **DB compartida:** `SQLiteJuezRepository` usa la misma `registro.db` que `SQLiteAtletaRepository` — variable de entorno `REGISTRO_DB_PATH`. No crear una DB separada.

3. **`juez_id` generado por backend:** igual que la decisión tomada en US-ADJ-11.3 para `atleta_id`. El cliente no envía el UUID.

4. **DesignReviewer CBO:** agregar `Juez`, su repo, commands y query al router aumenta el CBO de `router.py`. Ajustar `max_cbo` en `pyproject.toml` al iniciar esta US para el total combinado de 11.4 + 11.5.

5. **Tests:** cobertura ≥ 90% en `domain/aggregates/juez.py` y `application/commands/` + `application/queries/` nuevos. Tests BDD opcionales (la cobertura unitaria es suficiente para un CRUD simple).

---

*Spec creada: 2026-05-16 — ADR-020 · PLAN-SP-ADJ-11*
