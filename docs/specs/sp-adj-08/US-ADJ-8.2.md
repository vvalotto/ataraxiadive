# US-ADJ-8.2: Restringir operaciones por torneo y fase — UAT-5.2 reglas operativas

**Estado**: `Pendiente`
**Iteracion / Sprint**: SP-ADJ-08
**Tipo**: fix de regla funcional frontend + validacion de fase
**Agregado principal afectado**: `Torneo` / `Competencia`
**Bounded Context**: frontend organizador + `torneo` + `competencia`

---

## Descripcion (lenguaje de negocio)

Como **organizador**,
quiero que el sistema solo me permita operar disciplinas del torneo actual y pasar a
premiacion cuando todas sus competencias esten finalizadas
para evitar estados incoherentes del torneo.

---

## Contexto del dominio

### Problema

La UAT de cierre de INC-5.2 detecto dos riesgos funcionales:

- `UAT-5.2-02`: el selector de disciplinas para grilla puede mostrar disciplinas fuera del torneo.
- `UAT-5.2-05`: la transicion `EJECUCION -> PREMIACION` puede estar disponible aunque
  existan competencias pendientes o en ejecucion.

Ambos problemas son restricciones de operacion: el organizador no debe poder actuar sobre
datos fuera del torneo ni avanzar de fase si el torneo todavia no termino su ejecucion.

### Modelo involucrado

| Elemento | Nombre | Responsabilidad |
|---|---|---|
| Aggregate | `Torneo` | Ciclo de vida del torneo y disciplinas configuradas |
| Aggregate | `Competencia` | Estado operativo de cada disciplina |
| Query | `GET /torneos/{torneo_id}/disciplinas` | Fuente primaria de disciplinas configuradas |
| Query | `GET /competencia?torneo_id=...` | Competencias materializadas por torneo |
| Componente | Panel de grilla | Genera grilla para disciplinas del torneo |
| Componente | `AccionesPanel` | Dispara transiciones de fase |

---

## Especificacion del comportamiento

### Precondicion

El organizador opera un torneo especifico en el panel organizador.

### Postcondicion

- El selector de grilla contiene solo disciplinas configuradas en ese torneo.
- La accion `Pasar a premiacion` solo esta habilitada si todas las competencias
  esperadas del torneo estan en `Finalizada`.
- Si hay competencias pendientes, sin crear, en preparacion, confirmadas o en ejecucion,
  la accion queda bloqueada con motivo visible.

### Invariantes

| ID | Invariante |
|----|------------|
| INV-ADJ-8.2-01 | La fuente primaria del selector de grilla es la lista de disciplinas del torneo actual. |
| INV-ADJ-8.2-02 | El selector de grilla no debe incluir disciplinas globales no configuradas para el torneo. |
| INV-ADJ-8.2-03 | `Pasar a premiacion` requiere que todas las disciplinas configuradas tengan competencia finalizada o una regla explicita de no participacion. |
| INV-ADJ-8.2-04 | Una competencia `EnEjecucion`, `Confirmada`, `Preparacion` o ausente bloquea la transicion a `PREMIACION`. |
| INV-ADJ-8.2-05 | El bloqueo debe indicar cuantas disciplinas faltan cerrar y, si es posible, sus nombres. |

---

## Criterios de aceptacion

```gherkin
Feature: Restricciones operativas por torneo y fase

  Scenario: Selector de grilla usa solo disciplinas del torneo
    Given el torneo T1 tiene disciplinas STA y DNF
    And el sistema conoce tambien CWT y FIM
    When el organizador abre el selector de disciplinas para generar grilla de T1
    Then el selector muestra STA y DNF
    And no muestra CWT
    And no muestra FIM

  Scenario: No se puede pasar a premiacion con una competencia en ejecucion
    Given el torneo T1 esta en EJECUCION
    And DNF tiene competencia C1 en estado Finalizada
    And STA tiene competencia C2 en estado EnEjecucion
    When el organizador ve las acciones de fase
    Then la accion "Pasar a premiacion" esta deshabilitada u oculta
    And el panel indica que falta cerrar STA
    And no se ejecuta la transicion a PREMIACION

  Scenario: No se puede pasar a premiacion si falta crear una competencia esperada
    Given el torneo T1 esta en EJECUCION
    And T1 tiene disciplinas DNF y STA
    And solo DNF tiene competencia Finalizada
    When el organizador ve las acciones de fase
    Then la accion "Pasar a premiacion" esta bloqueada
    And el panel indica que falta cerrar STA

  Scenario: Se puede pasar a premiacion con todas las competencias finalizadas
    Given el torneo T1 esta en EJECUCION
    And DNF tiene competencia C1 en estado Finalizada
    And STA tiene competencia C2 en estado Finalizada
    When el organizador ve las acciones de fase
    Then la accion "Pasar a premiacion" esta habilitada
    When ejecuta la accion
    Then el frontend solicita la transicion a PREMIACION
```

---

## Impacto arquitectonico

**Esta US requiere una decision arquitectonica?**
- [x] Posiblemente — si la regla de avance a premiacion no existe en backend, definir si queda solo como bloqueo frontend o se agrega validacion de aplicacion.

**Capa(s) afectadas:**
- [x] Frontend — selector de grilla y acciones de fase.
- [x] Application/API — validar precondicion de fase si el endpoint actual permite avanzar sin control.
- [x] Dominio — solo si se formaliza la invariante en `Torneo`.

---

## Artefactos a modificar

| Artefacto | Cambio |
|-----------|--------|
| Panel/componente de generacion de grilla | Poblar selector desde disciplinas del torneo actual. |
| `frontend/src/components/organizador/AccionesPanel.tsx` | Bloquear `Pasar a premiacion` segun competencias finalizadas. |
| `frontend/src/api/torneo.ts` / `competencia.ts` | Reutilizar o agregar consultas necesarias para evaluar cierre por torneo. |
| `src/torneo/` o endpoint de fase | Agregar validacion backend si hoy acepta `PREMIACION` prematuramente. |
| Tests frontend/backend focalizados | Cubrir selector filtrado y bloqueo de fase. |

---

## Notas de implementacion

1. La validacion frontend mejora UX, pero la regla de fase idealmente debe estar protegida por backend.
2. Usar `GET /torneos/{torneo_id}/disciplinas` como fuente de verdad de disciplinas esperadas.
3. Cruzar contra `GET /competencia?torneo_id=...` para determinar estado por disciplina.
4. Si existen disciplinas configuradas sin participantes y se decide excluirlas del cierre, documentar la regla explicitamente antes de implementarla.

---

*Spec creada: 2026-04-22 — hallazgos UAT-5.2-02, 05 y 07*
