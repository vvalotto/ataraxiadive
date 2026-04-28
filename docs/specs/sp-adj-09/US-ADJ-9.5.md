# US-ADJ-9.5: Reencuadrar Resultados dentro del shell aprobado — S-04

**Estado**: `To Do`
**Iteracion / Sprint**: SP-ADJ-09
**Tipo**: ajuste UX + composición frontend
**Agregado principal afectado**: `ResultadosPage`
**Bounded Context**: frontend organizador + resultados

---

## Descripcion (lenguaje de negocio)

Como **organizador**,
quiero que la pantalla de resultados respete el shell y el layout aprobados
para leer la disciplina activa y el overall del torneo dentro de una experiencia coherente con el panel.

---

## Fuente de verdad UX

- `docs/design/ux/wireframes-organizador.md §S-04 Resultados`
- `docs/design/ux/prototipos/prototipo-organizador.html`
- `docs/design/ux/decisiones-frontend.md §D-02, §D-05`
- `docs/specs/sp5/US-5.6.5.md`
- `docs/specs/sp5/US-5.6.6.md`

---

## Contexto del dominio

### Problema

`US-5.6.5` y `US-5.6.6` quedaron implementadas sobre un shell que no respeta la UX
del organizador. Aunque la lógica de resultados existe, la pantalla sigue divergida en:

- shell;
- header;
- layout;
- relación visual entre ranking de disciplina y overall;
- integración con la navegación primaria del rol.

### Modelo involucrado

| Elemento | Nombre | Responsabilidad |
|---|---|---|
| Page | `ResultadosPage` | Vista de resultados del organizador |
| Componentes | tabla, podios, overall | Presentación de resultados por disciplina y torneo |
| Shell | organizador | Montar `Resultados` como sección primaria consistente |

---

## Especificacion del comportamiento

### Precondicion

Existe al menos un torneo con competencias visibles para el organizador.

### Postcondicion

La pantalla `Resultados`:

- vive dentro del shell aprobado del organizador;
- usa header y subtítulo acordes a `S-04`;
- organiza el ranking de disciplina y overall con la jerarquía visual correcta;
- conserva la funcionalidad ya implementada de tabla, podios y disponibilidad de overall.

### Invariantes

| ID | Invariante |
|----|------------|
| INV-ADJ-9.5-01 | `Resultados` se navega desde la navbar primaria del organizador. |
| INV-ADJ-9.5-02 | La pantalla respeta el lenguaje visual dark del organizador. |
| INV-ADJ-9.5-03 | La refactorización no elimina las capacidades entregadas por `US-5.6.5` y `US-5.6.6`. |
| INV-ADJ-9.5-04 | La relación entre ranking de disciplina y overall debe ser visualmente clara y coherente con `S-04`. |

---

## Criterios de aceptacion

```gherkin
Feature: Resultados del organizador alineados a S-04

  Scenario: Resultados vive dentro del shell aprobado
    Given un organizador autenticado
    When abre la sección Resultados
    Then ve la pantalla dentro del shell dark del organizador
    And el item Resultados está activo en la navbar

  Scenario: La pantalla conserva tabla y podios por disciplina
    Given existe una disciplina finalizada con ranking calculado
    When el organizador abre Resultados
    Then puede ver la tabla de ejecución
    And puede ver los podios por categoría y género

  Scenario: El overall mantiene su comportamiento de disponibilidad
    Given no todas las disciplinas están cerradas
    When el organizador ve Resultados
    Then el overall se muestra bloqueado
    Given todas las disciplinas están cerradas
    Then el overall se muestra disponible
```

---

## Impacto arquitectonico

**Esta US requiere una decision arquitectonica?**
- [x] Sí — reubica una pantalla ya implementada dentro del shell y la composición UX correctos.

**Capa(s) afectadas:**
- [x] Frontend — `ResultadosPage` y sus componentes.
- [ ] Backend.
- [ ] Dominio.

---

## Artefactos a modificar

| Artefacto | Cambio |
|-----------|--------|
| `frontend/src/pages/organizador/ResultadosPage.tsx` | Reencuadrar visual y navegacionalmente la pantalla. |
| Componentes de resultados/podios | Ajustar composición visual al layout aprobado. |
| Shell/routing del organizador | Integrar `Resultados` como sección primaria. |

---

## Notas de implementacion

1. Reutilizar la lógica de datos existente siempre que sea correcta; el ajuste es principalmente de shell y composición UX.
2. Si el layout exacto del prototipo entra en tensión con la tabla implementada, priorizar el contrato UX con adaptación razonada y explícita.
3. No tocar algoritmo ni reglas de dominio en esta US.

---

*Spec creada: 2026-04-28 — reencuadre UX de `US-5.6.5` y `US-5.6.6`*
