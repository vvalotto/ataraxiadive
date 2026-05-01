# US-ADJ-9.2: Reestructurar routing del organizador según navegación primaria aprobada

**Estado**: `To Do`
**Iteracion / Sprint**: SP-ADJ-09
**Tipo**: refactor estructural frontend
**Agregado principal afectado**: routing organizador
**Bounded Context**: frontend organizador

---

## Descripcion (lenguaje de negocio)

Como **organizador**,
quiero que las rutas del panel reflejen la navegación primaria aprobada
para que cada sección principal tenga una ubicación clara y consistente dentro del sistema.

---

## Fuente de verdad UX

- `docs/design/ux/wireframes-organizador.md §Navegación principal`
- `docs/design/ux/wireframes-organizador.md §Pantallas S-01..S-07`
- `docs/design/ux/prototipos/prototipo-organizador.html`
- `docs/design/ux/decisiones-frontend.md §D-02`

---

## Contexto del dominio

### Problema

Hoy el organizador navega entre páginas dispersas (`dashboard`, `torneo/:id`,
`resultados`, `competencias/:id/auditoria`, etc.) y parte de la navegación primaria
queda mezclada con tabs locales en vistas de detalle.

La UX aprobada distingue claramente:

- navegación primaria persistente;
- pantallas principales del rol;
- vistas detalle/contextuales como derivaciones del flujo, no como reemplazo del shell.

### Modelo involucrado

| Elemento | Nombre | Responsabilidad |
|---|---|---|
| Router | `App.tsx` / configuración de rutas | Definir destinos del organizador |
| Shell | shell organizador | Punto de montaje común |
| Pages | páginas primarias y páginas detalle | Separar navegación principal de navegación contextual |

---

## Especificacion del comportamiento

### Precondicion

Existe un shell del organizador definido o en proceso de definición (`US-ADJ-9.1`).

### Postcondicion

Las secciones primarias del organizador quedan montadas de forma consistente bajo el shell
y las rutas secundarias/detalle dejan de asumir el rol de navegación principal.

### Invariantes

| ID | Invariante |
|----|------------|
| INV-ADJ-9.2-01 | Las secciones `Panel`, `Grilla`, `Resultados`, `Jueces`, `Torneo` y `Audit Log` son destinos primarios del organizador. |
| INV-ADJ-9.2-02 | Las vistas detalle no reemplazan a la navegación principal persistente. |
| INV-ADJ-9.2-03 | La acción “volver al dashboard” deja de ser el patrón dominante para moverse entre secciones primarias. |
| INV-ADJ-9.2-04 | El redirect inicial del organizador aterriza en la home definida para el rol. |

---

## Criterios de aceptacion

```gherkin
Feature: Routing primario del organizador

  Scenario: El organizador aterriza en una home clara
    Given un usuario autenticado con rol ORGANIZADOR
    When entra a la aplicacion
    Then el sistema lo redirige a la home del organizador
    And no a una pantalla detalle de torneo

  Scenario: Las secciones primarias cuelgan del shell
    Given el organizador esta dentro del panel
    When navega a Grilla, Resultados, Jueces, Torneo y Audit Log
    Then cada seccion se abre dentro del shell compartido

  Scenario: Las vistas detalle no reemplazan la navegación principal
    Given el organizador abre una vista contextual o detalle
    Then la navegación primaria sigue disponible
    And puede volver a otra sección principal sin depender de botones "Volver al dashboard"
```

---

## Impacto arquitectonico

**Esta US requiere una decision arquitectonica?**
- [x] Sí — reorganiza el modelo de routing del rol organizador.

**Capa(s) afectadas:**
- [x] Frontend — rutas, shell y jerarquía de páginas.
- [ ] Backend.
- [ ] Dominio.

---

## Artefactos a modificar

| Artefacto | Cambio |
|-----------|--------|
| `frontend/src/App.tsx` | Reestructurar rutas del organizador. |
| Páginas organizador principales | Adaptarse al nuevo montaje dentro del shell. |
| Links internos del rol | Reemplazar dependencias a “Volver al dashboard” por navegación primaria consistente. |

---

## Notas de implementacion

1. No eliminar vistas detalle útiles; reubicarlas bajo el shell.
2. Si alguna ruta histórica debe mantenerse por compatibilidad, puede redirigir a la nueva ubicación.
3. Esta US debe implementarse inmediatamente después del shell para evitar doble retrabajo.

---

*Spec creada: 2026-04-28 — derivada del hallazgo UAT funcional post-US-5.6.6*
