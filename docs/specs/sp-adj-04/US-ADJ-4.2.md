# US-ADJ-4.2: Corregir orden de grilla STA — ascendente (menor AP primero)

**Estado**: `Pendiente`
**Iteración / Sprint**: SP-ADJ-04
**Agregado principal afectado**: `DisciplinaDescriptor` (Value Object compartido) · `Competencia`
**Bounded Context**: `shared/domain` · `competencia`

---

## Descripción (lenguaje de negocio)

Como **juez de una competencia de apnea**,
quiero que la grilla STA coloque primero a los atletas con menor AP (menor tiempo anunciado)
para que la competencia siga el protocolo real: los atletas más débiles compiten primero
y los mejores cierran la sesión.

---

## Contexto del dominio

### Modelo involucrado

| Elemento DDD | Nombre | Responsabilidad |
|---|---|---|
| Value Object | `DisciplinaDescriptor` | Reglas de medición y orden de grilla por disciplina (política P-01) |
| Aggregate | `Competencia` | Usa `DisciplinaDescriptor` para generar la grilla de salida |

### Lenguaje ubicuo relevante

- **Grilla de salida**: orden de presentación de los atletas en una disciplina, del primer OT al último.
- **Orden ascendente** (menor AP primero): atletas con menor AP declarado compiten primero. Se aplica en **todas** las disciplinas, incluyendo STA.
- **P-01**: política de ordenamiento de grilla. Actualmente documenta un error: dice "STA → mayor AP primero".

### Origen del error

**El error estaba documentado en `event-storming-competencia.md`** (P-01, línea 133):

> "Orden grilla: disciplinas de distancia (DNF, DYN, DYNB) → AP menor a mayor; tiempo (STA) → AP **mayor a menor**"

Esta política fue especificada incorrectamente en el Event Storming y propagada a la
implementación. El dataset real Buenos Aires 2025 confirma que STA usa el mismo orden
que las disciplinas de distancia: **menor AP primero** (HITO-17, DISC-04).

---

## Especificación del comportamiento

### Invariantes del agregado

- INV-P-01 (corregido): `orden_ascendente = True` para **todas** las disciplinas — tanto tiempo como distancia. Menor AP primero en todos los casos.

### Operación principal

**Cambio en `shared/domain/value_objects/disciplina_descriptor.py`:**

```python
# Antes — DisciplinaDescriptor.para()
if disciplina.es_tiempo():
    return cls(
        disciplina=disciplina,
        unidad_esperada=UnidadMedida.Segundos,
        orden_ascendente=False,   # INCORRECTO: mayor AP primero
    )

# Después
if disciplina.es_tiempo():
    return cls(
        disciplina=disciplina,
        unidad_esperada=UnidadMedida.Segundos,
        orden_ascendente=True,    # CORRECTO: menor AP primero (igual que distancia)
    )
```

**Precondición:** `DisciplinaDescriptor.para(Disciplina.STA)` retorna `orden_ascendente=False`.
**Postcondición:** `DisciplinaDescriptor.para(Disciplina.STA)` retorna `orden_ascendente=True`.
La grilla STA generada por `Competencia.generar_grilla()` coloca al atleta con menor AP en
posición 1 y al de mayor AP en la última posición.

**Ejemplo concreto (datos reales Buenos Aires 2025):**

```
Precondición:  5 atletas STA con AP: 30s, 120s, 150s, 240s, 330s
Operación:     Competencia.generar_grilla(performances, descriptor_STA)
Postcondición: grilla = [30s → pos.1, 120s → pos.2, 150s → pos.3, 240s → pos.4, 330s → pos.5]
```

---

## Criterios de aceptación (BDD)

```gherkin
Feature: Orden de grilla STA — menor AP primero

  Scenario: Grilla STA ordena de menor a mayor AP
    Given una competencia STA con atletas de AP [330s, 150s, 240s, 30s, 120s]
    When el juez genera la grilla
    Then el atleta con AP=30s queda en posición 1
    And el atleta con AP=120s queda en posición 2
    And el atleta con AP=330s queda en la última posición

  Scenario: Atletas con mismo AP en STA comparten bloque de OT
    Given una competencia STA con dos atletas de AP=120s y un atleta de AP=150s
    When el juez genera la grilla
    Then los dos atletas con AP=120s tienen OTs del mismo bloque (menor)
    And el atleta con AP=150s tiene un OT de bloque posterior

  Scenario: Orden STA coincide con el orden de distancia (menor primero)
    Given una competencia STA y una competencia DBF con los mismos APs relativos
    When se generan ambas grillas
    Then el atleta con menor AP está en posición 1 en ambas competencias
```

---

## Impacto arquitectónico

**¿Esta US requiere una decisión arquitectónica?**
- [x] No — corrección de una política de dominio incorrectamente especificada

**Capa(s) afectadas:**
- [x] Domain (`DisciplinaDescriptor.para()` — una línea)
- [x] Tests (todos los tests de grilla STA que asuman orden descendente deben invertirse)

---

## Documentación a actualizar

| Documento | Sección | Cambio requerido |
|-----------|---------|-----------------|
| `docs/design/event-storming-competencia.md` | P-01 (línea 133) | Corregir: `"tiempo (STA) → AP mayor a menor"` → `"tiempo (STA) → AP menor a mayor (igual que distancia)"` |
| `docs/design/domain-model.md` | Descripción de `DisciplinaDescriptor` / P-01 | Actualizar la descripción del orden para STA |
| `docs/dominio/05-requerimientos_funcionales.md` | Si hay mención del orden de grilla | Verificar y corregir si hay referencias al orden STA |

**Nota:** `event-storming-competencia.md` es el documento donde el error fue originalmente
cometido. Es el más importante de actualizar, ya que es fuente de verdad del diseño.

---

## Notas de implementación

1. El cambio de código es una sola línea en `disciplina_descriptor.py`.
2. El impacto mayor está en los tests: buscar con grep todos los tests que construyen grillas STA y verifican posiciones — necesitan invertir el orden esperado.
3. Verificar que `test_grilla_generada_con_orden_correcto_sta` (usado en UAT SP2) refleje el orden correcto post-cambio.
4. SPE también es distancia (`es_distancia()=True`), ya tenía `orden_ascendente=True` — sin cambio.

---

*Spec creada: 2026-04-03 — derivada de DISC-04 del análisis HITO-17*
