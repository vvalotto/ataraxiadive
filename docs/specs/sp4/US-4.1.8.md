# US-4.1.8: Limpiar `Torneo`, `SQLiteTorneoRepository` y objetos de soporte

**Estado**: `To Do`
**Sprint**: SP4 — La Plataforma
**Incremento**: INC-4.1
**Bounded Context**: `torneo`, `competencia`
**Capas afectadas**: `torneo/domain/`, `torneo/infrastructure/`, `competencia/domain/value_objects/`

---

## Descripción

Como **desarrollador del sistema**,
quiero **reducir la complejidad accidental en `Torneo`, su repositorio y los objetos
de soporte `TarjetaAsignacion`, `TarjetaAsignada` y `DisciplinaDescriptor`**
para **que cada clase tenga una responsabilidad única y los warnings del DesignReviewer
de baja prioridad no se acumulen hacia el siguiente incremento**.

---

## Contexto del dominio

### Modelo involucrado

| Elemento DDD | Nombre | Responsabilidad actual (problema) |
|---|---|---|
| Aggregate (sobrecargado) | `Torneo` | Mezcla lógica de negocio del torneo con responsabilidades de validación de disciplinas y gestión de estado que podrían delegarse |
| Repositorio (sobrecargado) | `SQLiteTorneoRepository` | Queries SQL expandidas + transformación de datos + lógica condicional mezcladas |
| Value Object (sobredesarrollado) | `TarjetaAsignacion` | Validaciones de negocio muy extensas dentro del VO |
| Value Object (sobredesarrollado) | `TarjetaAsignada` | Lógica incidental de compatibilidad y transformación |
| Value Object (sobredesarrollado) | `DisciplinaDescriptor` | Demasiada lógica de resolución de subdisciplinas inline |

### Lenguaje ubicuo relevante

- **DisciplinaDescriptor:** objeto de soporte que describe una disciplina y sus subdisciplinas válidas
- **TarjetaAsignacion:** VO que encapsula los datos de una asignación de tarjeta al momento de ejecutar el comando

---

## Especificación del comportamiento

### Invariantes de refactoring

- **INV-R-01:** ningún test unitario ni de integración existente puede fallar tras el refactoring.
- **INV-R-02:** la interfaz pública de `Torneo` no cambia (comandos y eventos idénticos).
- **INV-R-03:** la interfaz pública del repositorio (métodos de `TorneoRepository`) no cambia.
- **INV-R-04:** los warnings del DesignReviewer para los elementos afectados se reducen.

### Operación principal

**Nombre**: `refactoring de complejidad accidental en torneo y objetos de soporte`

| | Descripción |
|---|---|
| **Precondición** | `Torneo`, su repositorio y los VOs de soporte tienen advertencias de LongMethod / DataClass / responsabilidad expandida en el DesignReviewer |
| **Postcondición** | Cada clase tiene una única responsabilidad clara; la lógica de validación delegable está en helpers o métodos privados con nombres descriptivos |
| **Eventos generados** | (ninguno — refactoring puro) |
| **Excepciones** | (sin cambio) |

**Ejemplo concreto:**

```
Precondición:  SQLiteTorneoRepository tiene 3 métodos con transformación de datos inline de 30+ líneas
Operación:     extraer _row_to_torneo(row) → Torneo; _disciplina_row_to_descriptor(row) → DisciplinaDescriptor
Postcondición: cada método de repositorio orquesta sin transformar — delega en helpers privados
Verificación:  DesignReviewer no reporta LongMethod para los métodos afectados
```

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-4.1.8 — Torneo y objetos de soporte sin complejidad accidental

  Background:
    Given Torneo, su repositorio y los VOs de soporte están operativos

  Scenario: todos los tests de torneo pasan sin modificación
    Given el refactoring está completo
    When se ejecutan los tests de torneo (unit + integration)
    Then todos los tests pasan sin cambios en los test files

  Scenario: los endpoints de Torneo responden igual que antes
    Given el refactoring está completo
    When se ejecutan los tests de integración de la API de torneo
    Then todas las respuestas son idénticas a las anteriores al refactoring

  Scenario: DisciplinaDescriptor resuelve subdisciplinas correctamente
    Given DisciplinaDescriptor refactorizado
    When se consulta la subdisciplina de una disciplina SPE
    Then devuelve las mismas subdisciplinas que antes del refactoring
```

---

## Impacto arquitectónico

**¿Esta US requiere una decisión arquitectónica?**
- [x] No — se implementa con la arquitectura existente

**Capa(s) afectadas:**
- [x] Domain (`torneo/domain/aggregates/`, `competencia/domain/value_objects/`)
- [x] Infrastructure (`torneo/infrastructure/repositories/`)

---

## Referencias

- HITO: `docs/contexto/HITO-19-INC-4-1-HALLAZGOS-DISENO-CIERRE.md §AJ-INC-4.1.4`

---

## Notas de implementación

- Empezar por `SQLiteTorneoRepository` — es el más aislado y el cambio tiene menor riesgo.
- `DisciplinaDescriptor` en `shared/`: si la lógica de subdisciplinas ya está centralizada tras US-4.1.3, revisar si hay duplicación que se pueda eliminar.
- `TarjetaAsignacion` y `TarjetaAsignada`: evaluar si la lógica de validación puede moverse al aggregate `Performance` donde tiene más contexto, o si un método privado del VO es suficiente.
- Priorizar la reducción de líneas en los métodos, no la creación de nuevas clases.

---

*Redactado: 2026-04-08 — INC-4.1 ajustes DesignReviewer (HITO-19)*
