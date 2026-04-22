# US-ADJ-8.3: Fortalecer cancelacion de torneo — UAT-5.2 accion destructiva

**Estado**: `Pendiente`
**Iteracion / Sprint**: SP-ADJ-08
**Tipo**: hardening UX de accion destructiva
**Agregado principal afectado**: `Torneo`
**Bounded Context**: frontend organizador + `torneo`

---

## Descripcion (lenguaje de negocio)

Como **organizador**,
quiero que cancelar un torneo requiera una confirmacion fuerte
para evitar una cancelacion accidental de alto impacto.

---

## Contexto del dominio

### Problema

`UAT-5.2-08` detecto que la accion `Cancelar torneo` esta visualmente cerca de acciones
operativas de fase. Cancelar un torneo es destructivo o de alto impacto, por lo que no
debe ejecutarse con un click accidental.

### Modelo involucrado

| Elemento | Nombre | Responsabilidad |
|---|---|---|
| Aggregate | `Torneo` | Estado y cancelacion del torneo |
| Command/API | Cancelar torneo | Ejecuta la transicion a `CANCELADO` |
| Componente | `AccionesPanel` o zona de acciones | Expone acciones operativas y destructivas |
| Componente | Modal/confirmacion | Solicita confirmacion fuerte |

---

## Especificacion del comportamiento

### Precondicion

El organizador tiene permisos para cancelar el torneo.

### Postcondicion

La cancelacion solo se ejecuta si el organizador confirma escribiendo exactamente el
nombre del torneo.

### Invariantes

| ID | Invariante |
|----|------------|
| INV-ADJ-8.3-01 | `Cancelar torneo` debe estar separado visualmente de las acciones normales de fase. |
| INV-ADJ-8.3-02 | La confirmacion requiere ingresar el nombre exacto del torneo. |
| INV-ADJ-8.3-03 | Mientras el texto no coincida exactamente, la accion destructiva final permanece deshabilitada. |
| INV-ADJ-8.3-04 | Cancelar desde el modal debe conservar la semantica/API existente de cancelacion. |
| INV-ADJ-8.3-05 | Cerrar el modal o cancelar la confirmacion no debe modificar el estado del torneo. |

---

## Criterios de aceptacion

```gherkin
Feature: Cancelacion fuerte de torneo

  Background:
    Given el organizador esta autenticado
    And existe el torneo "BA 2026"

  Scenario: Cancelar torneo esta en una zona de peligro
    When el organizador abre el panel de acciones
    Then la accion "Cancelar torneo" esta separada de las acciones normales de fase
    And usa tratamiento visual de accion destructiva

  Scenario: No se puede cancelar con un click accidental
    When el organizador toca "Cancelar torneo"
    Then se abre una confirmacion fuerte
    And no se cancela el torneo todavia

  Scenario: Confirmacion incorrecta mantiene accion bloqueada
    When el organizador toca "Cancelar torneo"
    And escribe "BA"
    Then la accion final de cancelacion permanece deshabilitada
    And el torneo sigue en su estado actual

  Scenario: Confirmacion exacta permite cancelar
    When el organizador toca "Cancelar torneo"
    And escribe "BA 2026"
    Then la accion final de cancelacion queda habilitada
    When confirma la cancelacion
    Then el frontend ejecuta la cancelacion del torneo
    And el torneo queda en estado CANCELADO

  Scenario: Cerrar confirmacion no cancela
    When el organizador toca "Cancelar torneo"
    And cierra el modal de confirmacion
    Then no se envia la solicitud de cancelacion
    And el torneo mantiene su estado actual
```

---

## Impacto arquitectonico

**Esta US requiere una decision arquitectonica?**
- [x] No — fortalece el flujo frontend de una accion existente.

**Capa(s) afectadas:**
- [x] Frontend — acciones del organizador y modal/confirmacion.
- [ ] Backend.
- [ ] Dominio.

---

## Artefactos a modificar

| Artefacto | Cambio |
|-----------|--------|
| `frontend/src/components/organizador/AccionesPanel.tsx` | Separar zona de peligro y abrir confirmacion fuerte. |
| Componente modal existente o nuevo | Input de nombre exacto y boton destructivo habilitado solo con match exacto. |
| Tests frontend | Validar bloqueo, confirmacion exacta y cancelacion de modal. |

---

## Notas de implementacion

1. La comparacion debe ser exacta contra el nombre mostrado del torneo; no usar coincidencia parcial.
2. Mantener accesibilidad basica del modal: foco inicial, cierre por cancelar y labels claros.
3. Evitar que Enter confirme si el texto todavia no coincide.

---

*Spec creada: 2026-04-22 — hallazgo UAT-5.2-08*
