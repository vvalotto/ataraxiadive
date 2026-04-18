# US-4.1.6: Aliviar handlers de `competencia` — reducir FeatureEnvy y LongMethod

**Estado**: `To Do`
**Sprint**: SP4 — La Plataforma
**Incremento**: INC-4.1
**Bounded Context**: `competencia`
**Capas afectadas**: `competencia/application/`

---

## Descripción

Como **desarrollador del Core Domain**,
quiero **extraer orquestación repetida de los handlers de application de `competencia`**
para **que cada handler tenga una única responsabilidad clara y sea fácil de extender
sin romper comportamiento existente**.

---

## Contexto del dominio

### Modelo involucrado

| Elemento DDD | Nombre | Responsabilidad actual (problema) |
|---|---|---|
| Handler (sobrecargado) | `AsignarTarjetaHandler` | Valida estado, obtiene aggregate, llama comando, persiste y reconstruye payload — todo inline |
| Handler (sobrecargado) | `GenerarGrillaHandler` | Orquesta múltiples adaptadores y transforma respuestas — lógica incidental mezclada |
| Handler (sobrecargado) | `RegistrarAPHandler` | Validación de unidad + obtención de aggregate + persistencia colapsadas |
| Handler (sobrecargado) | `LlamarAtletaHandler` | Coordinación de estado y notificación mezclada con orquestación de repositorio |
| Helper (a crear) | `CompetenciaLoader` | Responsabilidad única: obtener aggregate del repositorio y validar precondición de existencia |

### Lenguaje ubicuo relevante

- **FeatureEnvy:** handler que conoce y manipula demasiado la estructura interna de otro objeto
- **LongMethod:** método que concentra pasos de validación, orquestación y construcción de respuesta sin separación

---

## Especificación del comportamiento

### Invariantes de refactoring

- **INV-R-01:** ningún test unitario ni de integración existente puede fallar tras el refactoring.
- **INV-R-02:** la interfaz pública de los handlers (firma de `handle()`, tipo de retorno, excepciones) no cambia.
- **INV-R-03:** los warnings FeatureEnvy y LongMethod de los handlers afectados deben reducirse o desaparecer en el DesignReviewer.
- **INV-R-04:** los helpers extraídos no introducen dependencias circulares ni violaciones hexagonales.

### Operación principal

**Nombre**: `refactoring de orquestación en handlers de application`

| | Descripción |
|---|---|
| **Precondición** | Handlers con métodos `handle()` que mezclan validación, carga de aggregate, ejecución de comando y construcción de respuesta en un único bloque lineal |
| **Postcondición** | Cada `handle()` delega en helpers de carga/validación extraídos; la lógica de construcción de respuesta está separada de la lógica de negocio |
| **Eventos generados** | (ninguno — refactoring puro) |
| **Excepciones** | (sin cambio — las mismas excepciones, lanzadas con la misma semántica) |

**Ejemplo concreto:**

```
Precondición:  AsignarTarjetaHandler.handle() tiene 60+ líneas con validación inline
Operación:     extraer _cargar_performance(id) → Performance; _construir_respuesta(perf) → dict
Postcondición: handle() tiene 10-15 líneas de orquestación clara
Verificación:  DesignReviewer no reporta LongMethod ni FeatureEnvy para los handlers afectados
```

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-4.1.6 — Handlers de competencia sin FeatureEnvy ni LongMethod

  Background:
    Given los handlers de competencia implementan los casos de uso del BC

  Scenario: todos los tests de handlers de competencia pasan sin modificación
    Given el refactoring de handlers está completo
    When se ejecutan todos los tests de application/competencia
    Then todos los tests pasan sin cambios en los test files

  Scenario: AsignarTarjetaHandler delega carga y respuesta en helpers
    Given el refactoring está completo
    When se inspecciona AsignarTarjetaHandler.handle()
    Then el método tiene menos de 20 líneas de orquestación
    And la carga del aggregate y la validación están en métodos/helpers separados

  Scenario: GenerarGrillaHandler no mezcla adaptación de datos con orquestación
    Given el refactoring está completo
    When se ejecuta la generación de grilla con parámetros válidos
    Then el resultado es idéntico al anterior al refactoring
    And la transformación de datos no está inline en handle()
```

---

## Impacto arquitectónico

**¿Esta US requiere una decisión arquitectónica?**
- [x] No — se implementa con la arquitectura existente

**Capa(s) afectadas:**
- [x] Application (`competencia/application/commands/`, handlers afectados)

---

## Referencias

- HITO: `docs/contexto/HITO-19-INC-4-1-HALLAZGOS-DISENO-CIERRE.md §AJ-INC-4.1.2`

---

## Notas de implementación

- Handlers a revisar con prioridad: `AsignarTarjetaHandler`, `GenerarGrillaHandler`, `RegistrarAPHandler`, `LlamarAtletaHandler`, `CalcularRankingHandler`.
- Los helpers extraídos son métodos privados del mismo handler o funciones en un módulo `_helpers.py` del mismo paquete — no deben ser servicios de aplicación independientes (no son casos de uso).
- No crear clases nuevas a menos que el helper sea compartido entre ≥ 2 handlers.

---

*Redactado: 2026-04-08 — INC-4.1 ajustes DesignReviewer (HITO-19)*
