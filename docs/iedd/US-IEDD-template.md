# US-NNN: [Título de la Historia de Usuario]

**Estado**: `Pendiente` | `En progreso` | `Implementada` | `Verificada`
**Iteración / Sprint**: S-NNN
**Agregado principal afectado**: [nombre del agregado DDD]
**Bounded Context**: [nombre del contexto delimitado]

---

## Descripción (lenguaje de negocio)

Como **[actor/rol]**,
quiero **[acción o capacidad]**
para **[beneficio o valor de negocio]**.

---

## Contexto del dominio

### Modelo involucrado

| Elemento DDD | Nombre | Responsabilidad |
|---|---|---|
| Entidad / Agregado | [nombre] | [qué representa] |
| Objeto de valor | [nombre] | [qué encapsula] |
| Evento de dominio | [nombre] | [qué señala] |

### Lenguaje ubicuo relevante

> Definir aquí los términos del dominio que aparecen en esta US,
> tal como los usaría un experto del dominio (no términos técnicos).

- **[Término]**: [definición en lenguaje del dominio]
- **[Término]**: [definición en lenguaje del dominio]

---

## Especificación del comportamiento

### Invariantes del agregado

> Condiciones que deben ser verdaderas SIEMPRE, antes y después de
> cualquier operación sobre este agregado. Si se viola una invariante,
> la operación debe rechazarse.

- INV-1: [condición que nunca puede violarse]
- INV-2: [condición que nunca puede violarse]

### Operación principal

**Nombre de la operación**: `[nombreOperacion(parámetros)]`

| | Descripción |
|---|---|
| **Precondición** | Estado que debe existir para que la operación sea válida |
| **Postcondición** | Estado garantizado si la operación se ejecutó correctamente |
| **Eventos generados** | Eventos de dominio que se disparan al completarse |
| **Excepciones** | Condiciones bajo las cuales la operación se rechaza |

**Ejemplo concreto:**

```
Precondición:  [descripción de estado inicial con valores ejemplo]
Operación:     [nombreOperacion(valor1, valor2)]
Postcondición: [descripción de estado final con valores ejemplo]
Evento:        [NombreEvento{datos relevantes}]
```

---

## Criterios de aceptación (BDD)

> Los escenarios BDD son la traducción de las pre/postcondiciones al
> lenguaje del negocio. Cada escenario debe poder derivarse de la
> especificación formal de arriba.

```gherkin
Feature: [título de la funcionalidad]

  Background:
    Given [contexto base común a todos los escenarios]

  Scenario: [caso principal — camino feliz]
    Given [precondición en lenguaje de negocio]
    When  [acción del actor]
    Then  [resultado esperado — refleja la postcondición]
    And   [evento generado o estado secundario]

  Scenario: [caso de rechazo — invariante o precondición violada]
    Given [estado que viola una precondición o invariante]
    When  [misma acción del actor]
    Then  [el sistema rechaza la operación con [mensaje/razón]]

  Scenario: [caso borde — si aplica]
    Given [condición límite]
    When  [acción]
    Then  [comportamiento esperado en el límite]
```

---

## Impacto arquitectónico

**¿Esta US requiere una decisión arquitectónica?**
- [ ] No — se implementa con la arquitectura existente
- [ ] Sí → crear `ADR-NNN` antes de implementar

**Capa(s) afectadas:**
- [ ] Domain (entidades, value objects, servicios de dominio)
- [ ] Application (casos de uso, comandos, consultas)
- [ ] Infrastructure (persistencia, APIs externas, adaptadores)

---

## Referencias

- Relacionada con: `US-NNN`, `ADR-NNN`, `RFC-NNN`
- Modelo de dominio: `docs/design/domain-model.md` (sección: [nombre])
- Especificación de arquitectura: `docs/design/architecture.md`

---

## Notas de implementación

> [Campo opcional — completar solo si hay decisiones técnicas relevantes
> que el desarrollador / Claude Code debe conocer antes de implementar.
> NO es el lugar para describir código, sino para aclarar restricciones
> o contexto que la especificación no cubre.]

---

*Template versión 1.0 — IEDD + claude-dev-kitc — Marzo 2026*
