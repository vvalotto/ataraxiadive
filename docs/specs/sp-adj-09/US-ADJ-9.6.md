# US-ADJ-9.6: Reubicar Grilla, Jueces, Torneo y Audit Log en la arquitectura UX correcta

**Estado**: `To Do`
**Iteracion / Sprint**: SP-ADJ-09
**Tipo**: ajuste transversal frontend
**Agregado principal afectado**: secciones primarias del organizador
**Bounded Context**: frontend organizador

---

## Descripcion (lenguaje de negocio)

Como **organizador**,
quiero que las secciones Grilla, Jueces, Torneo y Audit Log vivan dentro de la misma
arquitectura UX del panel
para operar el torneo con una navegación coherente y sin saltos entre pantallas desconectadas.

---

## Fuente de verdad UX

- `docs/design/ux/wireframes-organizador.md §S-02 Grilla`
- `docs/design/ux/wireframes-organizador.md §S-05 Jueces`
- `docs/design/ux/wireframes-organizador.md §S-06 Torneo`
- `docs/design/ux/wireframes-organizador.md §S-07 Audit Log`
- `docs/design/ux/prototipos/prototipo-organizador.html`
- `docs/design/ux/decisiones-frontend.md §D-02, §D-05`

---

## Contexto del dominio

### Problema

Parte importante del organizador hoy está repartida entre:

- páginas primarias;
- tabs locales en `DetalleTorneoPage`;
- rutas de auditoría separadas;
- links de retorno al dashboard.

Esto rompe la continuidad del panel y vuelve difusa la jerarquía entre secciones
primarias y vistas detalle.

### Modelo involucrado

| Elemento | Nombre | Responsabilidad |
|---|---|---|
| Pages | Grilla / Jueces / Torneo / Audit Log | Secciones primarias del organizador |
| Vistas detalle | auditoría de competencia / performance / detalle de torneo | Navegación contextual |
| Shell | organizador | Montaje persistente y activo |

---

## Especificacion del comportamiento

### Precondicion

Existe un shell y routing primario del organizador definidos por `US-ADJ-9.1` y `US-ADJ-9.2`.

### Postcondicion

Las secciones `Grilla`, `Jueces`, `Torneo` y `Audit Log`:

- quedan integradas al shell principal;
- respetan el lenguaje visual aprobado;
- separan navegación primaria de detalle contextual;
- dejan de depender de `DetalleTorneoPage` como contenedor híbrido de múltiples responsabilidades.

### Invariantes

| ID | Invariante |
|----|------------|
| INV-ADJ-9.6-01 | Las secciones primarias del organizador se acceden desde la navbar superior, no desde tabs locales equivalentes. |
| INV-ADJ-9.6-02 | Las vistas detalle/contextuales no reemplazan la navegación principal persistente. |
| INV-ADJ-9.6-03 | `DetalleTorneoPage` no debe seguir concentrando navegación primaria que pertenece al shell. |
| INV-ADJ-9.6-04 | Grilla, Jueces, Torneo y Audit Log deben compartir el mismo lenguaje visual dark del shell. |

---

## Criterios de aceptacion

```gherkin
Feature: Secciones primarias del organizador dentro de la arquitectura UX correcta

  Scenario: Grilla se navega como sección primaria
    Given un organizador autenticado
    When abre Grilla desde la navbar
    Then ve la sección Grilla dentro del shell del organizador

  Scenario: Jueces se navega como sección primaria
    Given un organizador autenticado
    When abre Jueces desde la navbar
    Then ve la sección Jueces dentro del shell del organizador

  Scenario: Torneo se navega como sección primaria
    Given un organizador autenticado
    When abre Torneo desde la navbar
    Then ve la sección Torneo dentro del shell del organizador

  Scenario: Audit Log se navega como sección primaria
    Given un organizador autenticado
    When abre Audit Log desde la navbar
    Then ve la sección Audit Log dentro del shell del organizador

  Scenario: Las vistas detalle mantienen navegación principal disponible
    Given el organizador entra a una vista contextual de auditoría o detalle
    Then la navegación principal del organizador sigue visible
```

---

## Impacto arquitectonico

**Esta US requiere una decision arquitectonica?**
- [x] Sí — cierra la migración de las secciones primarias al modelo UX correcto.

**Capa(s) afectadas:**
- [x] Frontend — páginas organizador, layout y links internos.
- [ ] Backend.
- [ ] Dominio.

---

## Artefactos a modificar

| Artefacto | Cambio |
|-----------|--------|
| `frontend/src/pages/organizador/DetalleTorneoPage.tsx` | Reducir o redefinir su responsabilidad. |
| Páginas de Grilla / Jueces / Torneo / Audit Log | Reubicarlas en la arquitectura UX correcta. |
| Shell/routing del organizador | Integración final de secciones primarias y detalles. |

---

## Notas de implementacion

1. Esta US debe ir al final del ajuste porque depende del shell y del routing ya estabilizados.
2. Si alguna pantalla necesita permanecer temporalmente como vista de detalle, documentar claramente esa decisión.
3. El objetivo no es borrar vistas útiles, sino reasignar correctamente su jerarquía dentro de la UX del organizador.

---

*Spec creada: 2026-04-28 — cierre transversal del ajuste UX del organizador*
