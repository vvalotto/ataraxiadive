# US-5.5.2: Vista del organizador de inscriptos con estado AP

**Estado**: `To Do`
**Sprint**: SP5 — La Puesta en Marcha
**Incremento**: INC-5.5
**Bounded Context**: `registro` + `competencia` + `frontend`
**Capas afectadas**: `frontend/src/pages/organizador/`, `frontend/src/components/organizador/`, `registro/api/`, `competencia/api/`

---

## Descripcion

Como **organizador**,
quiero **ver a los inscriptos con sus datos completos, disciplinas y estado de AP dentro de la navegación UX aprobada del panel organizador**,
para **controlar quién terminó su inscripción y quién está listo para pasar a grilla antes de cerrar el período de anuncios**.

---

## Fuente de verdad UX

Esta US se redefine tomando como contrato primario:

- `docs/design/ux/flujos-por-rol.md`
- `docs/design/ux/wireframes-organizador.md`
- `docs/design/ux/prototipos/prototipo-organizador.html`
- `docs/design/ux/wireframes-atleta.md` y `.work/revision-sp5/04-hallazgos-ux-portal-atleta.md` como fuente complementaria para el significado visible de los estados `AP pendiente` / `AP cerrado`

---

## Contexto de diseño

El panel del organizador es desktop-first con navbar superior persistente y navegación por secciones. Esta US no debe introducir una experiencia aislada o ajena a ese patrón.

El diseño UX no define una pantalla independiente llamada "Inscriptos" como primario; por lo tanto, esta historia debe integrarse dentro del área de gestión del torneo conservando:

- navbar superior sticky
- layout desktop-first
- cards/tablas consistentes con `wireframes-organizador.md`

**Inferencia desde la UX aprobada:** la vista de inscriptos pertenece al área `Torneo` o a una subvista de gestión del torneo, no a una UI separada que rompa la navegación principal.

---

## Alcance funcional

### A. Vista de inscriptos dentro del panel organizador

El organizador debe contar con una vista de consulta de inscriptos del torneo donde cada fila muestre:

- apellido y nombre
- categoría
- club
- disciplinas inscriptas
- estado de AP por disciplina
- estado general de la inscripción cuando corresponda

### B. Estados visibles por disciplina

La vista debe reflejar, al menos, estos estados UX:

- `AP pendiente`
- `AP declarado`
- `AP cerrado`

Cuando aplique, el estado visible debe ser consistente con lo que ve el atleta en `S-05 Mis inscripciones`.

### C. Uso operativo

La vista debe permitir al organizador responder preguntas operativas previas a la grilla:

- quién completó la inscripción
- quién todavía no cargó AP
- qué disciplinas ya tienen AP listo
- cuándo el período está cerrado y ya no se aceptan anuncios

---

## Invariantes

- **INV-5.5.2-01:** la vista respeta la navegación desktop del organizador con navbar superior persistente.
- **INV-5.5.2-02:** solo el organizador autenticado puede acceder.
- **INV-5.5.2-03:** la información visible del atleta usa nombre y apellido, no solo email.
- **INV-5.5.2-04:** el estado de AP mostrado al organizador debe ser consistente con el flujo del atleta en `S-05/S-06`.
- **INV-5.5.2-05:** una inscripción cancelada no aparece como participante operativo para generar grilla.
- **INV-5.5.2-06:** al cerrar el período de anuncios, la vista cambia a estado de solo lectura respecto de AP y muestra `AP cerrado` donde corresponda.

---

## Especificacion del comportamiento

### Operacion principal — listar inscriptos del torneo con estado AP

**Flujo UX esperado:**

```text
Panel organizador
  -> sección Torneo / gestión
      -> vista de inscriptos del torneo
```

**Comportamiento esperado:**

- el organizador selecciona un torneo
- la vista lista inscripciones activas del torneo
- por cada atleta se muestran sus disciplinas y el estado AP correspondiente
- la vista prioriza legibilidad operativa sobre detalles técnicos internos

### Construccion del estado AP

El estado AP es un dato de producto visible para el organizador. La implementación puede resolverlo con el backend, el frontend o una combinación, pero la spec no fija una solución interna como contrato.

Lo obligatorio es el resultado visible:

- si la disciplina no tiene AP y el período sigue abierto -> `AP pendiente`
- si la disciplina tiene AP cargado y el período sigue abierto -> `AP declarado`
- si el período de anuncios cerró -> `AP cerrado`

### Presentacion

La vista debe seguir el lenguaje visual del organizador:

- tabla o lista desktop-first
- uso de chips/badges para estado
- consistencia de color con tokens del panel organizador

No debe degradarse a una simple respuesta técnica de endpoint ni a una experiencia separada de la navbar principal.

---

## Criterios de aceptacion (BDD)

```gherkin
Feature: US-5.5.2 — Vista del organizador de inscriptos con estado AP

  Background:
    Given existe el torneo "BA Open 2026"
    And el organizador está autenticado
    And hay inscripciones activas de Ana García y Carlos López

  Scenario: organizador ve inscriptos con datos completos
    When abre la vista de inscriptos del torneo
    Then ve apellido y nombre de cada atleta
    And ve categoría y club
    And ve las disciplinas inscriptas por atleta

  Scenario: organizador distingue AP pendiente y AP declarado
    Given Ana declaró AP para DNF
    And Carlos todavía no declaró AP para DYN
    When el organizador consulta la vista
    Then Ana aparece con estado "AP declarado" en DNF
    And Carlos aparece con estado "AP pendiente" en DYN

  Scenario: cierre del período bloquea nuevos anuncios y cambia el estado visible
    Given el organizador cerró el período de anuncios del torneo
    When consulta la vista de inscriptos
    Then las disciplinas muestran estado "AP cerrado" donde corresponda
    And la vista queda en solo lectura respecto del AP

  Scenario: inscripciones canceladas no aparecen como operativas
    Given existe una inscripción cancelada para "pepe@email.com"
    When el organizador consulta la vista
    Then Pepe no aparece en la lista operativa de inscriptos

  Scenario: acceso con rol atleta es rechazado
    Given un usuario autenticado con rol ATLETA
    When intenta abrir la vista de inscriptos del organizador
    Then el sistema rechaza el acceso
```

---

## Impacto arquitectonico

- [x] Sí — la historia define comportamiento visible del panel organizador y puede requerir composición de datos entre BC Registro y BC Competencia.

### Capas afectadas

- `frontend/src/pages/organizador/` — integración de la vista en la navegación del organizador
- `frontend/src/components/organizador/` — tabla/lista de inscriptos y badges de AP
- `registro/api/` — datos enriquecidos de inscripción y perfil del atleta
- `competencia/api/` — estado operativo de AP o cierre del período de anuncios

### Nota de especificacion

La spec no fija que el contrato sea un endpoint específico tipo `inscriptos-detalle` ni obliga a una solución N+1/anti-N+1. Eso pertenece al diseño técnico posterior. La fuente de verdad acá es la UX visible y el dato de negocio que el organizador necesita.

---

## Referencias

- `docs/design/ux/flujos-por-rol.md §2 Rol: Organizador`
- `docs/design/ux/wireframes-organizador.md §Navegación principal y S-06 Gestión del Torneo`
- `docs/design/ux/wireframes-atleta.md §S-05 Mis inscripciones`
- `.work/revision-sp5/04-hallazgos-ux-portal-atleta.md`

---

*Redefinido: 2026-04-25 — INC-5.5 reiniciado desde UX aprobada*
