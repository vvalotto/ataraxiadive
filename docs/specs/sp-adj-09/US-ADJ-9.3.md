# US-ADJ-9.3: Home del organizador — torneos vigentes e histórico

**Estado**: `To Do`
**Iteracion / Sprint**: SP-ADJ-09
**Tipo**: ajuste funcional + UX frontend
**Agregado principal afectado**: home del organizador
**Bounded Context**: frontend organizador + `torneo`

---

## Descripcion (lenguaje de negocio)

Como **organizador**,
quiero una página inicial que liste los torneos bajo mi responsabilidad, priorizando
los torneos vigentes y permitiendo acceder al histórico
para entrar rápidamente al torneo que estoy operando y consultar anteriores cuando haga falta.

---

## Fuente de verdad UX

- `docs/design/ux/wireframes-organizador.md` — extender el diseño aprobado con una home de torneos explícita
- `docs/design/ux/decisiones-frontend.md §D-02`
- `docs/plans/sp-adj-09/PLAN-SP-ADJ-09.md`

> Nota: esta pantalla no está explicitada en el prototipo original. Esta spec formaliza un caso
> de uso real ya presente en la implementación y lo incorpora al contrato UX del organizador.

---

## Contexto del dominio

### Problema

La implementación actual ya muestra una lista de torneos, pero esa pantalla quedó usando
el nombre y el lugar del dashboard operativo del organizador. Eso mezcla dos conceptos
distintos:

- home de acceso a torneos;
- panel operativo del torneo activo.

Esta US separa ambos conceptos y formaliza la home de torneos como una pantalla válida.

### Modelo involucrado

| Elemento | Nombre | Responsabilidad |
|---|---|---|
| Page | home del organizador | Listado inicial de torneos |
| Query/API | `GET /torneos` | Fuente de torneos visibles para el organizador |
| Filtro frontend | vigentes / histórico | Segmentar torneos activos vs anteriores |

---

## Especificacion del comportamiento

### Precondicion

El organizador está autenticado y el sistema devuelve torneos visibles para ese rol.

### Postcondicion

La home del organizador:

- muestra por defecto torneos vigentes;
- permite alternar a histórico;
- distingue visualmente el estado de cada torneo;
- permite abrir la gestión del torneo seleccionado.

### Definicion de vigencia

Por defecto, un torneo se considera **vigente** si está en alguno de estos estados:

- `INSCRIPCION_ABIERTA`
- `PREPARACION`
- `EJECUCION`
- `PREMIACION`

Un torneo se considera **histórico** si está en:

- `CERRADO`
- `CANCELADO`

### Invariantes

| ID | Invariante |
|----|------------|
| INV-ADJ-9.3-01 | La vista inicial del organizador muestra por defecto torneos vigentes, no el histórico completo. |
| INV-ADJ-9.3-02 | El histórico solo incluye torneos `CERRADO` o `CANCELADO`. |
| INV-ADJ-9.3-03 | La home del organizador no reemplaza al dashboard operativo del torneo. |
| INV-ADJ-9.3-04 | Cada torneo visible ofrece una acción clara para entrar a su gestión. |

---

## Criterios de aceptacion

```gherkin
Feature: Home del organizador con torneos vigentes e histórico

  Scenario: La vista inicial muestra torneos vigentes
    Given existen torneos en INSCRIPCION_ABIERTA, PREPARACION, EJECUCION y CERRADO
    When el organizador entra a la home del organizador
    Then ve los torneos en INSCRIPCION_ABIERTA, PREPARACION y EJECUCION
    And no ve por defecto el torneo CERRADO

  Scenario: El filtro histórico muestra torneos anteriores
    Given existen torneos CERRADO y CANCELADO
    When el organizador activa el filtro de histórico
    Then ve los torneos CERRADO y CANCELADO

  Scenario: Cada torneo permite entrar a su gestión
    Given el organizador ve un torneo vigente
    When selecciona la acción principal del torneo
    Then entra al flujo de gestión de ese torneo

  Scenario: La home no se presenta como dashboard operativo
    Given el organizador está en la página inicial
    Then ve una lista de torneos
    And no ve KPIs operativos ni alertas de disciplina activa como contenido principal
```

---

## Impacto arquitectonico

**Esta US requiere una decision arquitectonica?**
- [x] Sí — separa formalmente home del organizador y dashboard operativo.

**Capa(s) afectadas:**
- [x] Frontend — página inicial del organizador.
- [ ] Backend.
- [ ] Dominio.

---

## Artefactos a modificar

| Artefacto | Cambio |
|-----------|--------|
| `frontend/src/pages/organizador/DashboardPage.tsx` o nueva page home | Formalizar listado de torneos vigentes/histórico. |
| Shell/routing del organizador | Definir esta vista como entrada principal del rol. |
| Tipos/helpers de estado torneo | Definir claramente la clasificación vigente/histórico. |

---

## Notas de implementacion

1. Esta pantalla puede reutilizar parte de la implementación actual, pero debe quedar renombrada y reposicionada correctamente.
2. Si el backend hoy devuelve todos los torneos, el filtro puede resolverse en frontend en esta US.
3. El dashboard operativo del torneo activo queda explicitamente diferido a `US-ADJ-9.4`.

---

*Spec creada: 2026-04-28 — formalización de la home del organizador ya insinuada por la implementación actual*
