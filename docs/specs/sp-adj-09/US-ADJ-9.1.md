# US-ADJ-9.1: Shell del organizador — navbar sticky + tema dark + estado activo

**Estado**: `To Do`
**Iteracion / Sprint**: SP-ADJ-09
**Tipo**: refactor UX estructural frontend
**Agregado principal afectado**: shell del organizador
**Bounded Context**: frontend organizador

---

## Descripcion (lenguaje de negocio)

Como **organizador**,
quiero usar un shell de navegacion unico, persistente y alineado al diseño aprobado
para moverme entre las secciones operativas del torneo sin perder contexto.

---

## Fuente de verdad UX

- `docs/design/ux/wireframes-organizador.md §Navegación principal`
- `docs/design/ux/wireframes-organizador.md §Principios de diseño`
- `docs/design/ux/prototipos/prototipo-organizador.html`
- `docs/design/ux/decisiones-frontend.md §D-02, §D-05`

---

## Contexto del dominio

### Problema

La implementación actual del organizador usa páginas separadas con encabezados por vista
y un layout claro/beige. La UX aprobada define, en cambio:

- navbar superior sticky;
- tema dark;
- tabs persistentes de primer nivel;
- badge de conexión;
- nombre del usuario visible;
- item activo según la sección en pantalla.

El gap es estructural: sin este shell, todas las pantallas del organizador quedan fuera
del contrato visual y de navegación aprobado.

### Modelo involucrado

| Elemento | Nombre | Responsabilidad |
|---|---|---|
| Layout | `OrganizadorShell` o equivalente | Shell persistente del rol organizador |
| Componente | navbar organizador | Navegación primaria + estado activo |
| Store/hook | auth + conexión | Nombre de usuario y badge online/offline |
| Router | rutas organizador | Montaje de secciones dentro del shell |

---

## Especificacion del comportamiento

### Precondicion

Existe un usuario autenticado con rol `ORGANIZADOR`.

### Postcondicion

Todas las pantallas primarias del organizador comparten un shell único con:

- marca `AtaraxiaDive`;
- tabs `Panel`, `Grilla`, `Resultados`, `Jueces`, `Torneo`, `Audit Log`;
- badge `En línea` / `Sin conexión`;
- nombre del usuario;
- tema dark y navbar sticky.

### Invariantes

| ID | Invariante |
|----|------------|
| INV-ADJ-9.1-01 | La navbar del organizador permanece visible al hacer scroll. |
| INV-ADJ-9.1-02 | Todas las secciones primarias del organizador reutilizan el mismo shell. |
| INV-ADJ-9.1-03 | El item activo de la navbar se corresponde con la sección/ruta visible. |
| INV-ADJ-9.1-04 | El shell usa el lenguaje visual dark aprobado por `docs/design/ux/`. |
| INV-ADJ-9.1-05 | El nombre del usuario y el badge de conexión son visibles sin ocupar el espacio de navegación principal. |

---

## Criterios de aceptacion

```gherkin
Feature: Shell unificado del organizador

  Scenario: Navbar persistente en todas las secciones primarias
    Given un organizador autenticado
    When navega entre Panel, Grilla, Resultados, Jueces, Torneo y Audit Log
    Then ve la misma navbar superior en todas las pantallas
    And el item activo cambia segun la seccion visible

  Scenario: Navbar permanece sticky
    Given el organizador esta en una pantalla con scroll
    When hace scroll vertical
    Then la navbar sigue visible en la parte superior

  Scenario: Shell muestra estado de conexion y usuario
    Given el organizador esta autenticado
    Then ve el badge de conexion
    And ve el nombre o email del usuario autenticado

  Scenario: Shell usa tema dark aprobado
    Given el organizador abre cualquier seccion principal
    Then el fondo general y la navbar usan el tema dark aprobado
    And no se muestra el layout claro/beige anterior
```

---

## Impacto arquitectonico

**Esta US requiere una decision arquitectonica?**
- [x] Sí — define el shell base del rol organizador.

**Capa(s) afectadas:**
- [x] Frontend — layout compartido, navegación y routing.
- [ ] Backend.
- [ ] Dominio.

---

## Artefactos a modificar

| Artefacto | Cambio |
|-----------|--------|
| `frontend/src/components/organizador/OrganizadorLayout.tsx` | Reemplazar o reconvertir al shell aprobado. |
| Nuevo componente de navbar organizador | Implementar tabs persistentes y estado activo. |
| `frontend/src/App.tsx` | Montar rutas del organizador dentro del shell común. |
| Hooks/store de auth y conexión | Exponer datos visibles al shell. |

---

## Notas de implementacion

1. No rehacer el contenido de todas las pantallas en esta US; el foco es shell y navegación compartida.
2. El shell debe servir de base para las siguientes US de `SP-ADJ-09`.
3. Si alguna pantalla secundaria no entra todavía al shell, debe documentarse explícitamente como excepción temporal.

---

*Spec creada: 2026-04-28 — derivada del hallazgo UAT funcional post-US-5.6.6*
