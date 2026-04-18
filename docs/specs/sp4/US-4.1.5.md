# US-4.1.5: Descomponer aggregate `Performance` — eliminar GodObject

**Estado**: `To Do`
**Sprint**: SP4 — La Plataforma
**Incremento**: INC-4.1
**Bounded Context**: `competencia`
**Capas afectadas**: `competencia/domain/`

---

## Descripción

Como **desarrollador del Core Domain**,
quiero **extraer responsabilidades secundarias del aggregate `Performance`**
para **que el aggregate sea cohesivo y mantenible, y el DesignReviewer no lo marque
como GodObject al cerrar futuros incrementos**.

---

## Contexto del dominio

### Modelo involucrado

| Elemento DDD | Nombre | Responsabilidad actual (problema) |
|---|---|---|
| Aggregate (sobrecargado) | `Performance` | Concentra cálculo de RP, resolución de tarjeta, lógica de penalización, compatibilidad de payload legacy y orquestación de estado |
| Value Object (a crear) | `ResolucionTarjeta` | Encapsula la lógica de determinar el resultado final (tarjeta + penalizaciones) dado un tipo de tarjeta y motivo |
| Value Object (a crear) | `RPFinal` | Encapsula el cálculo del RP penalizado separado del aggregate |

### Lenguaje ubicuo relevante

- **GodObject:** clase que acumula demasiadas responsabilidades; métrica GodObjectAnalyzer ≥ 28
- **RP penalizado:** marca realizada ajustada por penalizaciones de tarjeta amarilla — lógica de dominio pura, candidata a VO
- **Resolución de tarjeta:** decisión de si la performance es válida, penalizada o descalificada según tipo de tarjeta

---

## Especificación del comportamiento

### Invariantes de refactoring

- **INV-R-01:** ningún test unitario ni de integración existente puede fallar tras el refactoring.
- **INV-R-02:** la interfaz pública de `Performance` — comandos aceptados, eventos generados, excepciones lanzadas — no cambia.
- **INV-R-03:** la métrica GodObjectAnalyzer de `Performance` debe quedar por debajo de 28 tras el refactoring.
- **INV-R-04:** el comportamiento observable (AP, RP, tarjeta, estado) del aggregate se mantiene idéntico.

### Operación principal

**Nombre**: `refactoring de responsabilidades de Performance`

| | Descripción |
|---|---|
| **Precondición** | `Performance` tiene métrica GodObject = 31; `asignar_tarjeta()` concentra cálculo RP penalizado + resolución tarjeta + compatibilidad legacy |
| **Postcondición** | Lógica de cálculo RP extraída a VO; resolución de tarjeta extraída a helper/VO; `Performance.asignar_tarjeta()` delega en los nuevos componentes |
| **Eventos generados** | (ninguno — refactoring puro, no cambia eventos de dominio) |
| **Excepciones** | (sin cambio — las mismas excepciones existentes, lanzadas desde el mismo contexto) |

**Ejemplo concreto:**

```
Precondición:  Performance con asignar_tarjeta() de 80+ líneas que calcula RP y tarjeta inline
Operación:     extraer TarjetaResolucion.calcular(tipo, penalizacion, ap) → RPFinal
Postcondición: asignar_tarjeta() orquesta sin calcular — delega en el VO
Verificación:  DesignReviewer GodObjectAnalyzer(Performance) < 28
```

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-4.1.5 — Performance deja de ser GodObject

  Background:
    Given el aggregate Performance implementa los invariantes INV-P-01 a INV-P-11

  Scenario: todos los tests de Performance pasan sin modificación
    Given el refactoring de Performance está completo
    When se ejecutan todos los tests unitarios de performance
    Then todos los tests pasan sin cambios en los test files

  Scenario: DesignReviewer no detecta GodObject en Performance
    Given el refactoring de Performance está completo
    When se ejecuta designreviewer sobre src/competencia
    Then Performance no aparece como GodObject (métrica < 28)

  Scenario: el comportamiento de asignar_tarjeta Blanca con penalización se preserva
    Given una Performance en estado ResultadoRegistrado
    When se asigna tarjeta Blanca con penalización de 5 puntos
    Then el RP final queda correcto (AP - penalización)
    And el evento TarjetaAsignada tiene los mismos campos que antes del refactoring

  Scenario: el comportamiento de asignar_tarjeta Roja se preserva
    Given una Performance en estado ResultadoRegistrado
    When se asigna tarjeta Roja con motivo BKO_SUPERFICIE y distancia_blackout=45
    Then el estado es Ejecutada, tarjeta=Roja, motivo registrado
    And los eventos son idénticos a los generados antes del refactoring
```

---

## Impacto arquitectónico

**¿Esta US requiere una decisión arquitectónica?**
- [x] No — se implementa con la arquitectura existente (extracción de helpers/VO dentro del mismo BC)

**Capa(s) afectadas:**
- [x] Domain (`competencia/domain/aggregates/performance.py`, `competencia/domain/value_objects/`)

---

## Referencias

- HITO: `docs/contexto/HITO-19-INC-4-1-HALLAZGOS-DISENO-CIERRE.md §AJ-INC-4.1.1`
- Report DesignReviewer: `quality/reports/codeguard/US-4.1.1-quality.json`

---

## Notas de implementación

- Leer `src/competencia/domain/aggregates/performance.py` completo antes de diseñar la extracción.
- El problema central está en `asignar_tarjeta()`: cálculo de RP penalizado + resolución de tarjeta final + compatibilidad con payload legacy pueden separarse.
- La compatibilidad legacy (reconstitución de eventos antiguos) puede moverse a los handlers de infraestructura, no es responsabilidad del aggregate.
- Los nuevos VOs viven en `competencia/domain/value_objects/` y son importados por el aggregate (no al revés).
- No agregar nuevos tests de los VOs extraídos si los tests del aggregate ya cubren el comportamiento.

---

*Redactado: 2026-04-08 — INC-4.1 ajustes DesignReviewer (HITO-19)*
