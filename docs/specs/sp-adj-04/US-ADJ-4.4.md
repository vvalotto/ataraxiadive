# US-ADJ-4.4: Agregar campo `club` al aggregate Atleta

**Estado**: `Pendiente`
**Iteración / Sprint**: SP-ADJ-04
**Agregado principal afectado**: `Atleta`
**Bounded Context**: `registro`

---

## Descripción (lenguaje de negocio)

Como **organizador de un torneo de apnea**,
quiero que cada atleta tenga registrado su club o escuela de freediving
para que los documentos oficiales del torneo (grilla, resultados, reportes, diplomas)
incluyan esa información tal como lo requiere la federación.

---

## Contexto del dominio

### Modelo involucrado

| Elemento DDD | Nombre | Responsabilidad |
|---|---|---|
| Aggregate | `Atleta` | Datos de identidad competitiva del participante |
| Comando | `RegistrarAtleta` | Crea un nuevo perfil de atleta en el sistema |

### Lenguaje ubicuo relevante

- **Club / Escuela**: organización deportiva a la que pertenece el atleta. Aparece en todos los documentos oficiales de competencia: grilla de salida, tabla de resultados, certificados. Es un dato de identidad competitiva, no una relación de membresía con ciclo de vida propio.

### Origen de la brecha

El campo `club` aparece en el 100% de los atletas del dataset Buenos Aires 2025. No estaba
modelado en `Atleta` porque fue omitido en la especificación inicial de BC Registro (HITO-17,
DISC-05). No es una feature nueva — es un dato del dominio que faltaba.

---

## Especificación del comportamiento

### Invariantes del agregado

- INV-A-05: `club` no puede ser vacío ni solo espacios en blanco.

### Operación principal

**`RegistrarAtleta(nombre, apellido, email, fecha_nacimiento, categoria, club, brevet?)`**

| | Descripción |
|---|---|
| **Precondición** | No existe un atleta con el mismo email. `club` es un string no vacío. |
| **Postcondición** | El atleta queda registrado con `club` persistido. `GET /atletas/{id}` incluye el campo `club` en la respuesta. El dato queda disponible para grillas y reportes oficiales. |
| **Eventos generados** | `AtletaRegistrado` (sin cambio — `club` se agrega al payload) |
| **Excepciones** | `club` vacío o solo espacios → `ValueError("INV-A-05: club no puede ser vacío")` |

**Ejemplo concreto:**

```
Precondición:  no existe atleta con email="valotto@mail.com"
Operación:     RegistrarAtleta(nombre="Víctor", apellido="Valotto",
                               email="valotto@mail.com",
                               fecha_nacimiento=date(1975,1,1),
                               categoria=Categoria.MASTER_MASCULINO,
                               club="Regatas Santa Fe",
                               brevet="AIDA3")
Postcondición: atleta creado con club="Regatas Santa Fe"
```

---

## Criterios de aceptación (BDD)

```gherkin
Feature: Club del atleta

  Scenario: Registrar atleta con club válido
    Given no existe un atleta con email "valotto@mail.com"
    When se registra el atleta con club "Regatas Santa Fe"
    Then el atleta queda registrado exitosamente
    And GET /atletas/{id} retorna club="Regatas Santa Fe"

  Scenario: Club se expone en documentos operativos
    Given existe un atleta registrado con club "Regatas Santa Fe"
    When se genera una grilla o un reporte oficial que incluye al atleta
    Then el documento muestra el club "Regatas Santa Fe"

  Scenario: Club vacío es rechazado
    Given los datos del atleta son válidos
    When se intenta registrar con club=""
    Then el sistema rechaza el registro con error INV-A-05

  Scenario: Club con solo espacios es rechazado
    Given los datos del atleta son válidos
    When se intenta registrar con club="   "
    Then el sistema rechaza el registro con error INV-A-05
```

---

## Impacto arquitectónico

**¿Esta US requiere una decisión arquitectónica?**
- [x] No — extensión del aggregate existente con un campo nuevo

**Capa(s) afectadas:**
- [x] Domain (`Atleta` dataclass — agregar campo `club: str`, validar en `__post_init__`)
- [x] Application (`RegistrarAtletaCommand` — agregar `club: str`)
- [x] Infrastructure (`SqliteAtletaRepository` — agregar columna `club` en `CREATE TABLE` y en queries)
- [x] API (`RegistrarAtletaRequest` schema — agregar `club: str`; `AtletaResponse` — incluir `club`)
- [x] Read models / reportes (`grillas` y salidas oficiales que consuman datos de atleta)

---

## Documentación a actualizar

| Documento | Sección | Cambio requerido |
|-----------|---------|-----------------|
| `docs/design/domain-model.md` | BC Registro — diagrama de `Atleta` | Agregar `+String club` al diagrama Mermaid y a la descripción del aggregate |
| `docs/dominio/05-requerimientos_funcionales.md` | RF-IN (Registro e Inscripción) | Agregar o marcar RF que especifique el club como dato obligatorio del atleta |
| `docs/specs/sp-adj-04/US-ADJ-4.4.md` | Alcance de exposición | Mantener explícito que `club` se usa también en grillas y reportes |

---

## Notas de implementación

1. `club` es un string libre — no es un enum ni un aggregate separado. En este dominio el club es solo un nombre, no tiene ciclo de vida propio en el sistema.
2. La columna `club TEXT NOT NULL` debe agregarse al `CREATE TABLE` de `atletas` en `SqliteAtletaRepository`. Todos los tests que crean atletas deben incluir `club`.
3. Además de persistirse en Registro, `club` debe propagarse a los datos usados por grillas y reportes oficiales.
4. No hay migración de datos real (SQLite en memoria en tests).

---

*Spec creada: 2026-04-03 — derivada de DISC-05 del análisis HITO-17*
