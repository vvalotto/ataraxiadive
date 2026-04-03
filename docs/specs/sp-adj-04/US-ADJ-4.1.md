# US-ADJ-4.1: Corregir acrónimos de disciplinas DBF y SPE en el lenguaje ubicuo

**Estado**: `Pendiente`
**Iteración / Sprint**: SP-ADJ-04
**Agregado principal afectado**: `Disciplina` (Value Object compartido)
**Bounded Context**: `shared/domain` · `competencia` · `torneo` · `registro`

---

## Descripción (lenguaje de negocio)

Como **organizador de un torneo de apnea**,
quiero que el sistema use los acrónimos oficiales AIDA para las disciplinas (`DBF`, `SPE`)
para que la terminología del sistema coincida con la documentación oficial de la federación
y no genere confusión al cargar datos reales.

---

## Contexto del dominio

### Modelo involucrado

| Elemento DDD | Nombre | Responsabilidad |
|---|---|---|
| Value Object | `Disciplina` | Enumeración de disciplinas de apnea reconocidas por AIDA/CMAS |

### Lenguaje ubicuo relevante

- **DBF** (Dynamic Bi-Fins): disciplina de apnea dinámica con aletas bípodas. Acrónimo oficial AIDA. La app usaba `DYNB` — incorrecto.
- **SPE** (Speed Endurance): disciplina de velocidad en apnea. Acrónimo oficial. La app usaba `SPE2X50` — incorrecto.

### Origen del error

El error fue detectado al contrastar el modelo con el dataset real "Apnea Indoor Buenos
Aires 2025" (HITO-17). Ambos acrónimos incorrectos sobrevivieron al proceso IEDD porque
los documentos de dominio (`05-requerimientos_funcionales.md`, `domain-model.md`) también
contenían los nombres erróneos, y el Event Storming no verificó contra datos reales.

---

## Especificación del comportamiento

### Invariantes del agregado

- INV-D-01: Los valores del enum `Disciplina` deben coincidir exactamente con los acrónimos oficiales AIDA/CMAS usados en la documentación de competencias reales.

### Operación principal

Esta US es un refactor de lenguaje ubicuo, no un cambio de comportamiento. No hay
comandos ni eventos nuevos. La operación consiste en renombrar dos valores del enum
y actualizar todas sus referencias.

**Cambio en `shared/domain/value_objects/disciplina.py`:**

```python
# Antes
DYNB    = "DYNB"     # Dynamic Bi-Fins — INCORRECTO
SPE2X50 = "SPE2X50"  # Speed Endurance — INCORRECTO

# Después
DBF = "DBF"  # Dynamic Bi-Fins — acrónimo oficial AIDA
SPE = "SPE"  # Speed Endurance — acrónimo oficial
```

**Precondición:** el enum `Disciplina` existe con los valores `DYNB` y `SPE2X50`.
**Postcondición:** el enum `Disciplina` contiene `DBF` y `SPE`. Todos los archivos que
referenciaban `Disciplina.DYNB` o `Disciplina.SPE2X50` usan los nuevos nombres.
Ningún test falla. Las DBs de test son recreadas (SQLite en memoria — sin migración real).

---

## Criterios de aceptación (BDD)

```gherkin
Feature: Disciplinas con acrónimos AIDA correctos

  Scenario: DBF es una disciplina de distancia válida
    Given el sistema conoce las disciplinas AIDA
    When se consulta la disciplina "DBF"
    Then el sistema la reconoce como disciplina de distancia (metros)
    And su orden de grilla es ascendente (menor AP primero)

  Scenario: SPE es una disciplina de distancia válida
    Given el sistema conoce las disciplinas AIDA
    When se consulta la disciplina "SPE"
    Then el sistema la reconoce como disciplina de distancia (metros)

  Scenario: Los acrónimos obsoletos no son reconocidos
    Given el sistema conoce las disciplinas AIDA
    When se intenta usar "DYNB" o "SPE2X50" como disciplina
    Then el sistema rechaza el valor como disciplina desconocida
```

---

## Impacto arquitectónico

**¿Esta US requiere una decisión arquitectónica?**
- [x] No — se implementa con la arquitectura existente

**Capa(s) afectadas:**
- [x] Domain (value object `Disciplina`)
- [x] Application (cualquier handler que referencie los valores por nombre)
- [x] Infrastructure (tests, seeds, fixtures que usen `"DYNB"` o `"SPE2X50"` como strings)

---

## Documentación a actualizar

| Documento | Sección | Cambio requerido |
|-----------|---------|-----------------|
| `docs/dominio/05-requerimientos_funcionales.md` | RF-GT-02 | `"DBF, SPE2X50"` → `"DBF, SPE"` |
| `docs/design/domain-model.md` | Tabla de Value Objects — `Disciplina` | `DYNB, SPE2X50` → `DBF, SPE` |
| `CLAUDE.md` | §8 Lenguaje Ubicuo | No aplica directamente — disciplinas no están listadas |

---

## Notas de implementación

1. Buscar todas las ocurrencias de `DYNB` y `SPE2X50` en `src/` y `tests/` con grep antes de cambiar.
2. Las DBs de test son SQLite en memoria — no requieren migración de datos.
3. Si hay archivos `.feature` con strings `"DYNB"` o `"SPE2X50"`, actualizarlos también.
4. Verificar que `Disciplina.es_tiempo()` y `Disciplina.es_distancia()` sigan funcionando correctamente para DBF y SPE (ambas son distancia).

---

*Spec creada: 2026-04-03 — derivada de DISC-02 y DISC-03 del análisis HITO-17*
