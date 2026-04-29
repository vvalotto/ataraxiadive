# US-ADJ-9.7: Declarar AP durante inscripción como precondición de preparación

**Estado**: `To Do`
**Iteracion / Sprint**: SP-ADJ-09
**Tipo**: ajuste transversal de dominio + backend + frontend
**Agregado principal afectado**: flujo organizador `Inscriptos -> cierre de inscripción -> preparación`
**Bounded Context**: registro + torneo + competencia + frontend organizador

---

## Descripcion (lenguaje de negocio)

Como **organizador**,
quiero que los AP se declaren durante la inscripción por atleta y disciplina
para poder cerrar la inscripción solo cuando el torneo tenga la información
necesaria para preparar la competencia y generar la grilla.

---

## Fuente de verdad UX

- `docs/design/ux/wireframes-organizador.md §S-03 Inscriptos`
- `docs/design/ux/wireframes-organizador.md §S-02 Grilla`
- `docs/design/ux/prototipos/prototipo-organizador.html`
- `.work/revision-sp5/03-hallazgos-logica-inscripcion-ap.md`
- `docs/specs/sp5/US-5.5.1.md`
- `docs/specs/sp5/US-5.5.2.md`

---

## Contexto del dominio

### Problema

La implementación actual deja el AP del atleta dentro del circuito de
`competencia`, como parte de los eventos de `performance`.

Eso produce una secuencia incorrecta:

- la inscripción se puede cerrar sin AP;
- la pantalla `Inscriptos` no administra el AP como dato propio de la fase;
- la preparación y generación de grilla requieren AP ya existentes;
- pero esos AP hoy dependen de una competencia previamente creada.

El resultado es una contradicción operativa: el sistema exige para `PREPARACION`
un dato que no obliga a capturar durante `INSCRIPCION_ABIERTA`.

### Modelo involucrado

| Elemento | Nombre | Responsabilidad |
|---|---|---|
| Registro | inscripción por atleta y disciplina | fuente primaria del estado de inscripción y AP declarados |
| Torneo | transición `INSCRIPCION_ABIERTA -> PREPARACION` | validar completitud antes de cerrar inscripción |
| Competencia | generación de grilla | consumir AP ya declarados para ordenar atletas |
| Frontend | `Inscriptos`, `Grilla` | capturar AP y reflejar el readiness operativo del torneo |

---

## Especificacion del comportamiento

### Precondicion

Existe un torneo en `INSCRIPCION_ABIERTA` con una o más inscripciones activas por
disciplina.

### Postcondicion

El sistema trata el AP como dato del flujo de inscripción:

- `Inscriptos` permite visualizar y completar AP por atleta y disciplina;
- no se puede cerrar la inscripción si faltan AP obligatorios;
- al pasar a `PREPARACION`, la competencia utiliza esos AP ya declarados;
- la generación de grilla no depende de performances cargadas manualmente antes.

### Invariantes

| ID | Invariante |
|----|------------|
| INV-ADJ-9.7-01 | El AP pertenece al flujo de inscripción del torneo y debe existir antes de `PREPARACION`. |
| INV-ADJ-9.7-02 | No se permite `INSCRIPCION_ABIERTA -> PREPARACION` si hay inscripciones activas sin AP requerido. |
| INV-ADJ-9.7-03 | `Inscriptos` debe mostrar el estado real del AP sin depender de competencias ya creadas. |
| INV-ADJ-9.7-04 | `Generar grilla` consume AP declarados en inscripción y no exige performances preexistentes como fuente primaria. |
| INV-ADJ-9.7-05 | Si el BC `competencia` replica AP por necesidades operativas, esa réplica no reemplaza la fuente primaria en `registro`. |

---

## Criterios de aceptacion

```gherkin
Feature: AP declarados durante inscripción como requisito de preparación

  Scenario: El organizador ve atletas inscriptos con AP pendientes
    Given un torneo en INSCRIPCION_ABIERTA
    And existen atletas inscriptos en una disciplina
    When el organizador abre la sección Inscriptos
    Then puede ver el estado AP por atleta y disciplina
    And los faltantes se muestran como pendientes

  Scenario: No se puede cerrar inscripción con AP faltantes
    Given un torneo en INSCRIPCION_ABIERTA
    And existe al menos una inscripción activa sin AP requerido
    When el organizador intenta cerrar la inscripción
    Then el sistema rechaza la transición a PREPARACION
    And informa que faltan AP por completar

  Scenario: Se puede cerrar inscripción cuando todos los AP están completos
    Given un torneo en INSCRIPCION_ABIERTA
    And todas las inscripciones activas tienen AP válido
    When el organizador cierra la inscripción
    Then el torneo puede pasar a PREPARACION

  Scenario: La grilla usa AP ya declarados
    Given un torneo en PREPARACION
    And existen inscripciones activas con AP declarado
    When el organizador genera la grilla de una disciplina
    Then la grilla se calcula usando esos AP
    And no requiere performances preexistentes cargadas manualmente
```

---

## Impacto arquitectonico

**Esta US requiere una decision arquitectonica?**
- [x] Sí — redefine la fuente primaria del AP y el contrato entre `registro`, `torneo` y `competencia`.

**Capa(s) afectadas:**
- [x] Frontend — `Inscriptos` y estados operativos del shell del organizador.
- [x] Backend — handlers, read models y endpoints de inscripción/preparación.
- [x] Dominio — invariantes de transición de torneo y fuente del AP.

---

## Artefactos a modificar

| Artefacto | Cambio |
|-----------|--------|
| `src/registro/` | Persistir AP por atleta, torneo y disciplina como dato de inscripción. |
| `src/torneo/application/commands/transicionar_torneo.py` | Validar AP completos antes de cerrar inscripción. |
| `src/competencia/application/commands/generar_grilla.py` | Consumir AP desde la fuente correcta de inscripción. |
| `src/registro/api/router.py` | Exponer lectura/escritura coherente del AP en `Inscriptos`. |
| `frontend/src/components/organizador/InscriptosPanel.tsx` | Mostrar y editar AP como parte de la inscripción. |
| `frontend/src/components/organizador/GrillaPanel.tsx` | Reflejar que la preparación depende de AP completos. |

---

## Notas de implementacion

1. Este ajuste no es cosmético: corrige una inversión de modelo que hoy bloquea la secuencia correcta `inscripción -> AP -> preparación -> grilla`.
2. Si se mantiene una proyección de AP en `competencia`, debe quedar explícito que es derivada y no fuente primaria.
3. La migración debe contemplar datos existentes para no romper torneos ya preparados bajo el esquema anterior.
4. La UX de `Inscriptos` debe soportar el estado intermedio `pendiente` de forma clara antes del cierre de inscripción.

---

*Spec creada: 2026-04-29 — formalización del hallazgo de lógica AP/inscripción en SP-ADJ-09*
