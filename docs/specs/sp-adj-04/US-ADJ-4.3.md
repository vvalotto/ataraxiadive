# US-ADJ-4.3: Corregir nombre de categoría JUVENIL → JUNIOR en lenguaje ubicuo

**Estado**: `Pendiente`
**Iteración / Sprint**: SP-ADJ-04
**Agregado principal afectado**: `Categoria` (Value Object) · `Atleta`
**Bounded Context**: `registro`

---

## Descripción (lenguaje de negocio)

Como **organizador de un torneo de apnea**,
quiero que el sistema use el término `JUNIOR` para la categoría juvenil
para que coincida con la nomenclatura oficial AIDA y con los documentos reales
de inscripción y resultados.

---

## Contexto del dominio

### Modelo involucrado

| Elemento DDD | Nombre | Responsabilidad |
|---|---|---|
| Value Object | `Categoria` | Categoría competitiva del atleta (combina grupo etario + sexo) |
| Aggregate | `Atleta` | Tiene una `Categoria` como atributo de identidad competitiva |

### Lenguaje ubicuo relevante

- **JUNIOR**: categoría para atletas jóvenes según estándar AIDA. La app usaba `JUVENIL` — término castellanizado no utilizado en el dominio real.
- **Categoría competitiva**: combinación de grupo etario (JUNIOR, SENIOR, MASTER) y sexo (MASCULINO, FEMENINO), que determina en qué tabla de ranking compite el atleta.

### Origen del error

Mismo patrón que DISC-02/03: el nombre fue elegido en castellano durante la especificación
sin verificar contra la terminología real de la federación. Los documentos del torneo
Buenos Aires 2025 usan `JUNIOR` sin excepción (HITO-17, DISC-07).

---

## Especificación del comportamiento

### Invariantes del agregado

- INV-C-01: Los nombres de los grupos etarios en `Categoria` deben coincidir con la nomenclatura AIDA: `JUNIOR`, `SENIOR`, `MASTER`.

### Operación principal

**Cambio en `registro/domain/value_objects/categoria.py`:**

```python
# Antes
JUVENIL_MASCULINO = "JUVENIL_MASCULINO"
JUVENIL_FEMENINO  = "JUVENIL_FEMENINO"

# Después
JUNIOR_MASCULINO = "JUNIOR_MASCULINO"
JUNIOR_FEMENINO  = "JUNIOR_FEMENINO"
```

**Precondición:** el enum `Categoria` tiene los valores `JUVENIL_MASCULINO` y `JUVENIL_FEMENINO`.
**Postcondición:** el enum `Categoria` tiene los valores `JUNIOR_MASCULINO` y `JUNIOR_FEMENINO`.
Todos los archivos que referencian los valores obsoletos usan los nuevos nombres.

---

## Criterios de aceptación (BDD)

```gherkin
Feature: Categoría JUNIOR en el lenguaje del dominio

  Scenario: Registrar un atleta con categoría JUNIOR masculino
    Given un atleta menor de edad que compite en categoría JUNIOR masculino
    When se registra el atleta con categoria="JUNIOR_MASCULINO"
    Then el atleta queda registrado con la categoría correcta
    And aparece en los rankings de la categoría JUNIOR masculino

  Scenario: El valor obsoleto JUVENIL no es aceptado
    Given el sistema de registro de atletas
    When se intenta registrar un atleta con categoria="JUVENIL_MASCULINO"
    Then el sistema rechaza el valor como categoría inválida
```

---

## Impacto arquitectónico

**¿Esta US requiere una decisión arquitectónica?**
- [x] No — refactor de lenguaje ubicuo, sin cambio de comportamiento

**Capa(s) afectadas:**
- [x] Domain (`Categoria` value object)
- [x] Infrastructure (repositorio SQLite si almacena el string del enum)
- [x] Tests y fixtures que usen `JUVENIL_MASCULINO` / `JUVENIL_FEMENINO`

---

## Documentación a actualizar

| Documento | Sección | Cambio requerido |
|-----------|---------|-----------------|
| `docs/design/domain-model.md` | BC Registro — `Categoria` | `JUVENIL_MASCULINO/FEMENINO` → `JUNIOR_MASCULINO/FEMENINO` |
| `docs/dominio/05-requerimientos_funcionales.md` | RF-IN-01 | Verificar si menciona "juvenil" y corregir a "JUNIOR" |
| `CLAUDE.md` | §8 Lenguaje Ubicuo | Agregar entrada: **JUNIOR**: categoría etaria juvenil según estándar AIDA |

---

## Notas de implementación

1. Buscar todas las ocurrencias de `JUVENIL` en `src/` y `tests/` antes de cambiar.
2. Las DBs SQLite de test son en memoria — sin migración real de datos.
3. Verificar si el repositorio almacena el string del enum directamente. Si usa `categoria.value`, el rename del string value es suficiente.

---

*Spec creada: 2026-04-03 — derivada de DISC-07 del análisis HITO-17*
