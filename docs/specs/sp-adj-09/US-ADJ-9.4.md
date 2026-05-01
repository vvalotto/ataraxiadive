# US-ADJ-9.4: Dashboard operativo del organizador alineado a S-01

**Estado**: `To Do`
**Iteracion / Sprint**: SP-ADJ-09
**Tipo**: ajuste funcional + UX frontend
**Agregado principal afectado**: dashboard operativo del organizador
**Bounded Context**: frontend organizador

---

## Descripcion (lenguaje de negocio)

Como **organizador**,
quiero un dashboard operativo del torneo activo con KPIs, disciplina en ejecución, alertas
y próximos atletas
para supervisar la operación en vivo desde un único lugar.

---

## Fuente de verdad UX

- `docs/design/ux/wireframes-organizador.md §S-01 Dashboard`
- `docs/design/ux/prototipos/prototipo-organizador.html`
- `docs/design/ux/decisiones-frontend.md §D-02, §D-05`

---

## Contexto del dominio

### Problema

El `DashboardPage` actual funciona como catálogo de torneos, no como el panel operativo
definido por la UX aprobada. Esta US implementa el dashboard verdadero y lo separa de la
home de torneos formalizada en `US-ADJ-9.3`.

### Modelo involucrado

| Elemento | Nombre | Responsabilidad |
|---|---|---|
| Page | dashboard operativo | Supervisión en vivo del torneo activo |
| Queries | progreso / competencias / alertas / próximos | Alimentar KPIs y secciones del dashboard |
| Shell | organizador | Montar la pantalla como sección primaria |

---

## Especificacion del comportamiento

### Precondicion

Existe un torneo activo o seleccionado por el organizador para operar.

### Postcondicion

El dashboard operativo muestra:

- KPI strip;
- disciplina en ejecución;
- alertas activas o empty state;
- próximos atletas;
- otras disciplinas del torneo en estado informativo.

### Invariantes

| ID | Invariante |
|----|------------|
| INV-ADJ-9.4-01 | El dashboard operativo no se usa como listado general de torneos. |
| INV-ADJ-9.4-02 | Si no hay alertas activas, se comunica explícitamente el empty state. |
| INV-ADJ-9.4-03 | La disciplina activa se distingue claramente de otras disciplinas del torneo. |
| INV-ADJ-9.4-04 | Los KPIs visibles son operativos, no administrativos. |

---

## Criterios de aceptacion

```gherkin
Feature: Dashboard operativo del organizador

  Scenario: El dashboard muestra KPIs y disciplina activa
    Given el organizador opera un torneo con una disciplina en ejecución
    When abre la sección Panel
    Then ve KPIs operativos
    And ve la disciplina en ejecución destacada

  Scenario: El dashboard muestra alertas activas
    Given existe al menos una alerta operativa
    When el organizador abre el Panel
    Then ve una sección de alertas activas

  Scenario: El dashboard muestra empty state si no hay alertas
    Given no existen alertas activas
    When el organizador abre el Panel
    Then ve el mensaje "Sin alertas"

  Scenario: El dashboard muestra próximos atletas
    Given existe una disciplina con grilla en curso
    When el organizador abre el Panel
    Then ve la lista de próximos atletas de la disciplina activa
```

---

## Impacto arquitectonico

**Esta US requiere una decision arquitectonica?**
- [x] Sí — introduce o redefine una pantalla primaria del organizador.

**Capa(s) afectadas:**
- [x] Frontend — dashboard, queries y composición de datos.
- [ ] Backend.
- [ ] Dominio.

---

## Artefactos a modificar

| Artefacto | Cambio |
|-----------|--------|
| Nueva page o page reorganizada del dashboard operativo | Implementar contenido de `S-01`. |
| Componentes organizador | KPI cards, alertas, próximos, disciplina activa. |
| Routing/shell | Montar esta sección como `Panel`. |

---

## Notas de implementacion

1. Esta US puede requerir seleccionar un torneo activo en contexto o resolver cómo se define el “torneo operativo” visible.
2. Si existen múltiples torneos vigentes, la UX concreta debe explicitar cómo el organizador elige cuál está operando.
3. No mezclar este dashboard con la home de torneos de `US-ADJ-9.3`.

---

*Spec creada: 2026-04-28 — derivada del wireframe S-01 del organizador*
