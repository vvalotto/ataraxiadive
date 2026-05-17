# US-ADJ-11.3: BC Registro — refactor Atleta (campos opcionales + BT-002: dni, telefono)

**Estado**: `Implementada`
**Iteracion / Sprint**: SP-ADJ-11
**Tipo**: refactor backend + migración DB
**Agregado principal afectado**: `Atleta`
**Bounded Context**: `registro`
**Dependencia**: US-ADJ-11.1 (no bloquea técnicamente, puede ejecutarse en paralelo con 11.4/11.5)

---

## Descripcion (lenguaje de negocio)

Como **atleta que se registra en la plataforma**,
quiero poder crear mi perfil sin necesidad de informar club ni categoría en el momento inicial
para completar esos datos después, cuando los tenga disponibles.

Como **atleta registrado**,
quiero poder guardar mi DNI y teléfono en mi perfil
para que el organizador los tenga disponibles si los necesita.

---

## Contexto del dominio

### Problema

`Atleta.club` y `Atleta.categoria` son campos obligatorios en el modelo actual (INV-A-05 valida que `club` no sea vacío; `categoria` no tiene default). Un atleta recién llegado a la plataforma puede no saber en qué categoría compite, o competir sin club. Además, BT-002 identificó que `dni` y `telefono` no se persisten, bloqueando el flujo de comunicación con el organizador.

### Modelo involucrado

| Elemento | Nombre | Responsabilidad |
|---|---|---|
| Aggregate | `Atleta` | Datos de perfil del atleta; `club` y `categoria` pasan a opcionales; se agregan `dni` y `telefono` |
| Infra | `SQLiteAtletaRepository` | Persiste las nuevas columnas; migración automática |
| Command | `RegistrarAtletaCommand` | Acepta campos opcionales; `atleta_id` lo genera el backend |
| Command | `ActualizarAtletaCommand` | Incluye `dni` y `telefono` |
| API | `router.py` | Schemas actualizados; `POST /registro/atletas` genera `atleta_id` internamente |

---

## Especificacion del comportamiento

### Precondicion

- El sistema tiene atletas existentes con columnas `categoria TEXT NOT NULL` y `club TEXT NOT NULL`.
- La migración se ejecuta automáticamente al arrancar (`_ensure_column`).

### Postcondicion

- `Atleta.club` y `Atleta.categoria` pueden ser `None`.
- `Atleta.dni` y `Atleta.telefono` son persistidos (pueden ser `None`).
- Los atletas existentes en DB conservan sus valores de `categoria` y `club` — la migración solo agrega columnas nuevas, no modifica datos existentes.
- El backend genera `atleta_id` internamente; el cliente no lo envía.

### Invariantes

| ID | Invariante |
|----|------------|
| INV-11.3-01 | `nombre` y `apellido` no pueden ser vacíos (INV-A-01 se mantiene). |
| INV-11.3-02 | `email` debe tener formato válido (INV-A-02 se mantiene). |
| INV-11.3-03 | `fecha_nacimiento` debe ser en el pasado (INV-A-04 se mantiene). |
| INV-11.3-04 | Si `club` se provee (no `None`), no puede ser string vacío o sólo espacios. |
| INV-11.3-05 | `dni` y `telefono`, si se proveen, no pueden ser strings vacíos. |
| INV-11.3-06 | No pueden existir dos atletas con el mismo `email`. |

---

## Criterios de aceptacion

```gherkin
Feature: Perfil Atleta con campos opcionales y datos BT-002

  Scenario: Registrar atleta sin club ni categoria
    Given no existe ningún atleta con email "nuevo@test.com"
    When se registra un atleta con nombre "Laura", apellido "Pérez", email "nuevo@test.com",
         fecha_nacimiento "2000-01-01", sin club ni categoria
    Then el sistema crea el atleta con club=null y categoria=null
    And retorna 201 con el atleta_id generado por el backend

  Scenario: Registrar atleta con todos los campos
    Given no existe ningún atleta con email "completo@test.com"
    When se registra un atleta con nombre, apellido, email, fecha_nacimiento,
         club="Club Apnea BA", categoria="SENIOR", dni="30123456", telefono="1155559999"
    Then el sistema crea el atleta con todos los campos persistidos
    And retorna 201 con el atleta_id generado por el backend

  Scenario: Actualizar atleta agregando DNI y telefono
    Given existe un atleta con email "existente@test.com" sin dni ni telefono
    When hace PATCH /registro/atletas/me con {"dni": "28888999", "telefono": "1133334444"}
    Then el atleta queda con dni="28888999" y telefono="1133334444"
    And retorna 200 con el perfil actualizado

  Scenario: Actualizar atleta limpiando club
    Given existe un atleta con email "existente@test.com" con club="Club Viejo"
    When hace PATCH /registro/atletas/me con {"club": null}
    Then el atleta queda con club=null
    And retorna 200

  Scenario: Registrar atleta con email ya existente
    Given existe un atleta con email "doble@test.com"
    When se intenta registrar otro atleta con email "doble@test.com"
    Then el sistema retorna 409

  Scenario: Registrar atleta con club vacío (string vacío)
    When se registra un atleta con club=""
    Then el sistema retorna 422 con detalle sobre club inválido

  Scenario: Atletas existentes en DB migran correctamente
    Given la DB tiene un atleta con columnas "categoria" y "club" pero sin "dni" ni "telefono"
    When el repositorio accede al atleta por email
    Then el atleta es reconstituido con dni=null y telefono=null
    And categoria y club conservan sus valores originales
```

---

## Impacto arquitectonico

**Esta US requiere una decision arquitectonica?**
- [x] No — extiende el aggregate y repositorio existentes con campos opcionales.

**Decision tomada: `atleta_id` generado por el backend**
El `POST /registro/atletas` actual exige que el cliente envíe `atleta_id`. Este diseño expone un detalle de implementación (UUIDs) y no es idiomatic REST. En esta US se elimina `atleta_id` del request; el handler crea el UUID internamente con `uuid4()`. El cliente recibe el id en la respuesta 201.

**Capa(s) afectadas:**
- [x] Domain — `Atleta.club: str | None`, `Atleta.categoria: Categoria | None`, campos `dni` y `telefono`
- [x] Infrastructure — `SQLiteAtletaRepository` (columnas nuevas + migración + `_row_to_atleta` actualizado)
- [x] Application — `RegistrarAtletaCommand` (sin `atleta_id`, `club`/`categoria` opcionales, `dni`/`telefono` nuevos) · `ActualizarAtletaCommand` (agrega `dni`/`telefono`)
- [x] API — `RegistrarAtletaRequest` (sin `atleta_id`), `AtletaResponse` (con `dni`/`telefono`), `ActualizarAtletaMeRequest` (con `dni`/`telefono`)

---

## Artefactos a modificar

| Artefacto | Cambio |
|-----------|--------|
| `src/registro/domain/aggregates/atleta.py` | `club: str \| None = None`, `categoria: Categoria \| None = None`, agregar `dni: str \| None = None`, `telefono: str \| None = None`. Eliminar la validación `INV-A-05` de club vacío en `__post_init__` y en `actualizar()` — reemplazar por: si se provee y no es `None`, no puede ser vacío. Mismo patrón para `dni` y `telefono`. |
| `src/registro/infrastructure/repositories/sqlite_atleta_repository.py` | `_CREATE_TABLE`: `categoria TEXT`, `club TEXT` sin `NOT NULL`. Agregar `_ensure_columns(conn)` que añade `dni TEXT` y `telefono TEXT` si no existen. Actualizar `save`, `find_by_id`, `find_by_email`, `_row_to_atleta` para incluir los 4 campos opcionales. |
| `src/registro/application/commands/registrar_atleta.py` | `RegistrarAtletaCommand`: eliminar `atleta_id`, `club`/`categoria` opcionales (`None` por defecto), agregar `dni: str \| None = None` y `telefono: str \| None = None`. Handler: genera `atleta_id = uuid4()` internamente. |
| `src/registro/application/commands/actualizar_atleta.py` | `ActualizarAtletaCommand`: agregar `dni: str \| None = None`, `telefono: str \| None = None`. Handler: pasa ambos campos a `atleta.actualizar()`. |
| `src/registro/domain/aggregates/atleta.py` | `actualizar()`: agregar parámetros `dni: str \| None = None`, `telefono: str \| None = None` con misma lógica de actualización parcial. |
| `src/registro/api/router.py` | `RegistrarAtletaRequest`: eliminar `atleta_id`, `club`/`categoria` opcionales, agregar `dni`/`telefono`. `AtletaResponse`: agregar `dni: str \| None` y `telefono: str \| None`. `ActualizarAtletaMeRequest`: agregar `dni: str \| None = None`, `telefono: str \| None = None`. Endpoint `registrar_atleta`: pasar `atleta_id` eliminado del body; recibe el id generado. |

---

## Notas de implementacion

1. **Migración DB:** La tabla `atletas` existente tiene `categoria TEXT NOT NULL` y `club TEXT NOT NULL`. La migración consiste en añadir columnas nuevas (`_ensure_columns`) — no se modifica el esquema de columnas existentes porque SQLite no permite `ALTER COLUMN`. Los atletas existentes tendrán `club` y `categoria` con valores reales (no nulos), lo que es correcto.

2. **`_row_to_atleta`:** El índice de columnas cambia al agregar `dni` y `telefono`. Usar SELECT con nombres de columna explícitos para evitar errores por posición.

3. **`InscriptoDetalleResponse`:** El campo `categoria: Categoria` pasa a `categoria: Categoria | None` en la respuesta de `listar_inscriptos_detalle`. Verificar que el serializer lo maneje (Pydantic serializa `None` correctamente).

4. **Tests a actualizar:** Los tests de `RegistrarAtletaHandler` que crean `RegistrarAtletaCommand` con `atleta_id` explícito deben eliminarlo. Los tests de `Atleta.__post_init__` con `club=""` deben actualizarse — ya no lanza error en el constructor si `club=None`; sí lanza si `club=""`.

---

*Spec creada: 2026-05-16 — BT-002 · ADR-020 · PLAN-SP-ADJ-11*
