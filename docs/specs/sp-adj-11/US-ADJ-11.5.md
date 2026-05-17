# US-ADJ-11.5: BC Registro — entidad Organizador

**Estado**: `Especificada`
**Iteracion / Sprint**: SP-ADJ-11
**Tipo**: nueva entidad backend
**Agregado principal afectado**: `Organizador` (nuevo)
**Bounded Context**: `registro`
**Dependencia**: US-ADJ-11.1 (JWT con rol ORGANIZADOR); paralela a US-ADJ-11.3 y 11.4

---

## Descripcion (lenguaje de negocio)

Como **usuario con rol ORGANIZADOR**,
quiero poder crear mi perfil con el nombre de mi organización
para que los atletas sepan quién organiza los torneos que publico.

Como **usuario con rol ORGANIZADOR**,
quiero poder actualizar el nombre de mi organización desde "Mis Datos"
para reflejar cambios en mi asociación o club.

---

## Contexto del dominio

### Problema

El BC Registro no modela al `Organizador` como entidad propia. Un usuario con rol ORGANIZADOR (post US-ADJ-11.1) puede crear torneos, pero no tiene dónde persistir el nombre de su organización. La página "Mis Datos" del portal organizador no tiene backend que la soporte.

### Modelo involucrado

| Elemento | Nombre | Responsabilidad |
|---|---|---|
| Aggregate | `Organizador` | Datos de perfil del organizador: nombre de organización |
| Port | `OrganizadorRepositoryPort` | Contrato de persistencia |
| Infra | `SQLiteOrganizadorRepository` | Tabla `organizadores` en `registro.db` |
| Command | `RegistrarOrganizadorCommand` | Crea el perfil Organizador para un usuario con rol ORGANIZADOR |
| Command | `ActualizarOrganizadorCommand` | Actualiza `nombre_organizacion` |
| Query | `ObtenerOrganizadorHandler` | Recupera el perfil Organizador por email |
| API | `router.py` | Tres endpoints bajo `/registro/organizadores` |

---

## Especificacion del comportamiento

### Precondicion

- El usuario está autenticado con JWT que incluye `"rol": "ORGANIZADOR"`.
- Para `POST /registro/organizadores`: no existe aún un perfil Organizador para ese email.

### Postcondicion

- Existe un registro en la tabla `organizadores` asociado al email del usuario.
- `nombre_organizacion` puede ser `None` — el perfil es válido sin él.

### Invariantes

| ID | Invariante |
|----|------------|
| INV-11.5-01 | `email` debe tener formato válido — no puede ser vacío. |
| INV-11.5-02 | No pueden existir dos perfiles Organizador con el mismo `email`. |
| INV-11.5-03 | Si `nombre_organizacion` se provee, no puede ser string vacío. |
| INV-11.5-04 | Solo usuarios con JWT válido y rol ORGANIZADOR pueden crear o modificar su perfil. |

---

## Criterios de aceptacion

```gherkin
Feature: Perfil Organizador — creación y actualización

  Scenario: Crear perfil Organizador con datos mínimos
    Given existe un usuario autenticado con rol ORGANIZADOR y email "org@test.com"
    And no existe perfil Organizador para "org@test.com"
    When hace POST /registro/organizadores con {} (body vacío)
    Then el sistema crea el perfil con nombre_organizacion=null
    And retorna 201 con el organizador_id generado

  Scenario: Crear perfil Organizador con nombre
    Given existe un usuario autenticado con rol ORGANIZADOR y email "org2@test.com"
    When hace POST /registro/organizadores con {"nombre_organizacion": "Club Apnea Buenos Aires"}
    Then el sistema crea el perfil con el nombre informado
    And retorna 201

  Scenario: Intentar crear perfil Organizador cuando ya existe uno
    Given existe un perfil Organizador para "org@test.com"
    When hace POST /registro/organizadores
    Then el sistema retorna 409 con detalle "Perfil de organizador ya registrado"

  Scenario: Obtener perfil Organizador propio
    Given existe un perfil Organizador para "org@test.com"
    When hace GET /registro/organizadores/me
    Then el sistema retorna 200 con los datos del perfil Organizador

  Scenario: Obtener perfil Organizador cuando no existe
    Given no existe perfil Organizador para "org@test.com"
    When hace GET /registro/organizadores/me
    Then el sistema retorna 404 con detalle "Organizador no encontrado"

  Scenario: Actualizar nombre de organizacion
    Given existe un perfil Organizador para "org@test.com" con nombre_organizacion=null
    When hace PATCH /registro/organizadores/me con {"nombre_organizacion": "Federación Apnea Sur"}
    Then el perfil queda con nombre_organizacion="Federación Apnea Sur"
    And retorna 200 con el perfil actualizado

  Scenario: Actualizar nombre a null (limpiar)
    Given existe un perfil Organizador para "org@test.com" con nombre_organizacion="Club Viejo"
    When hace PATCH /registro/organizadores/me con {"nombre_organizacion": null}
    Then el perfil queda con nombre_organizacion=null
    And retorna 200

  Scenario: Usuario sin rol ORGANIZADOR no puede crear perfil Organizador
    Given existe un usuario autenticado con rol ATLETA
    When hace POST /registro/organizadores
    Then el sistema retorna 403
```

---

## Impacto arquitectonico

**Esta US requiere una decision arquitectonica?**
- [x] No — sigue el mismo patrón que `Atleta` y `Juez` (US-ADJ-11.4): aggregate + port + repo SQLite + commands + query + endpoints.

**Capa(s) afectadas:**
- [x] Domain — nuevo aggregate `Organizador` + nuevo port `OrganizadorRepositoryPort`
- [x] Infrastructure — `SQLiteOrganizadorRepository` (tabla `organizadores` en `registro.db`)
- [x] Application — `RegistrarOrganizadorCommand/Handler` · `ActualizarOrganizadorCommand/Handler` · `ObtenerOrganizadorHandler`
- [x] API — tres endpoints en `router.py` de BC Registro

---

## Artefactos a crear / modificar

| Artefacto | Cambio |
|-----------|--------|
| `src/registro/domain/aggregates/organizador.py` | Nuevo. `Organizador(organizador_id: UUID, email: str, nombre_organizacion: str \| None)`. `__post_init__` valida email y que `nombre_organizacion` no sea string vacío si se provee. `actualizar(nombre_organizacion: str \| None)` — acepta `None` para limpiar el valor. |
| `src/registro/domain/ports/organizador_repository_port.py` | Nuevo. `OrganizadorRepositoryPort` (ABC): `save(org)`, `find_by_email(email) -> Organizador \| None`, `find_by_id(org_id) -> Organizador \| None`. |
| `src/registro/domain/exceptions.py` | Agregar `OrganizadorNoEncontrado`, `OrganizadorYaRegistrado`. |
| `src/registro/infrastructure/repositories/sqlite_organizador_repository.py` | Nuevo. Tabla `organizadores(organizador_id TEXT PK, email TEXT UNIQUE, nombre_organizacion TEXT)`. `_ensure_table(conn)`. Implementa `OrganizadorRepositoryPort`. |
| `src/registro/application/commands/registrar_organizador.py` | Nuevo. `RegistrarOrganizadorCommand(email, nombre_organizacion)`. Handler genera `organizador_id = uuid4()`, lanza `OrganizadorYaRegistrado` si ya existe. |
| `src/registro/application/commands/actualizar_organizador.py` | Nuevo. `ActualizarOrganizadorCommand(email, nombre_organizacion)`. Handler: load por email, llama `actualizar()`, guarda. Lanza `OrganizadorNoEncontrado`. |
| `src/registro/application/queries/obtener_organizador.py` | Nuevo. `ObtenerOrganizadorHandler(repo)`: `handle(email) -> Organizador`. Lanza `OrganizadorNoEncontrado`. |
| `src/registro/api/router.py` | Agregar schemas `RegistrarOrganizadorRequest`, `OrganizadorResponse`, `ActualizarOrganizadorMeRequest`. Agregar tres endpoints: `POST /registro/organizadores` (OrganizadorDep), `GET /registro/organizadores/me` (OrganizadorDep), `PATCH /registro/organizadores/me` (OrganizadorDep). |

---

## Notas de implementacion

1. **`OrganizadorDep`:** agregar a `shared/api/dependencies.py` siguiendo el patrón de `AtletaDep`. Verificar que `require_rol(Rol.ORGANIZADOR)` ya exista — si no, crearlo junto con `JuezDep` de US-ADJ-11.4.

2. **DB compartida:** `SQLiteOrganizadorRepository` usa la misma `registro.db` (`REGISTRO_DB_PATH`). No crear DB separada.

3. **`organizador_id` generado por backend:** el cliente no envía el UUID en el request.

4. **`actualizar()` con `None` explícito:** a diferencia de `Juez.actualizar()` donde `None` significa "no cambiar", para `Organizador.actualizar(nombre_organizacion)` si el cliente envía `null` en JSON, debe limpiar el campo. Usar un sentinel `UNSET` o distinguir `None` (limpiar) de campo ausente (no cambiar). Implementación sugerida: el command siempre lleva el valor final; el router mapea campo ausente en JSON al valor actual (patch parcial en capa API, no en domain).

5. **DesignReviewer CBO:** ajustar `max_cbo` junto con US-ADJ-11.4 — los dos incrementan el mismo router. Hacer el ajuste al iniciar la primera de las dos USs.

6. **Tests:** cobertura ≥ 90% en `domain/aggregates/organizador.py` y archivos de application nuevos. Escenario del `actualizar()` con `None` debe tener test unitario explícito.

---

*Spec creada: 2026-05-16 — ADR-020 · PLAN-SP-ADJ-11*
