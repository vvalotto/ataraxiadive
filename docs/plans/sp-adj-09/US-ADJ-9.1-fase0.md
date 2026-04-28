# US-ADJ-9.1 - Fase 0: Validacion de Contexto

**Fecha:** 2026-04-28
**Producto:** `frontend`
**Sprint:** `SP-ADJ-09`
**Spec canonica:** `docs/specs/sp-adj-09/US-ADJ-9.1.md`

---

## Historia

**US:** US-ADJ-9.1 - Shell del organizador

Como **organizador**, quiero usar un shell de navegacion unico, persistente y alineado
al diseño aprobado para moverme entre las secciones operativas del torneo sin perder
contexto.

---

## Fuentes de Verdad Validadas

- `docs/specs/sp-adj-09/US-ADJ-9.1.md`
- `docs/design/ux/wireframes-organizador.md`
- `docs/design/ux/prototipos/prototipo-organizador.html`
- `docs/design/ux/decisiones-frontend.md`
- `docs/plans/sp-adj-09/PLAN-SP-ADJ-09.md`

---

## Contexto Relevante

### Layout actual

- `frontend/src/components/organizador/OrganizadorLayout.tsx` implementa un contenedor por página.
- El layout actual usa:
  - gradiente beige;
  - header de página aislado;
  - acciones contextuales por pantalla;
  - ausencia de navbar principal persistente.

### Routing actual

- `frontend/src/App.tsx` define rutas independientes para el organizador:
  - `/organizador/dashboard`
  - `/organizador/resultados`
  - `/organizador/torneo/:torneoId`
  - `/organizador/torneos/:torneoId/competencias`
  - `/organizador/competencias/:competenciaId/auditoria`
- No existe un punto de montaje común del rol organizador que comparta shell y navegación.

### Datos ya disponibles para el shell

- `useAuthStore` ya expone:
  - `email`
  - `nombre`
  - `apellido`
  - `rol`
- `HealthCheck` ya resuelve el estado visible del backend como badge reutilizable.

### Gap confirmado

La UX aprobada exige:

- navbar sticky superior;
- tema dark;
- tabs persistentes `Panel`, `Grilla`, `Resultados`, `Jueces`, `Torneo`, `Audit Log`;
- nombre de usuario;
- estado de conexión visible.

Nada de eso existe hoy como shell compartido del organizador.

---

## Gaps Detectados

1. Falta un shell persistente del organizador.
2. Falta navbar primaria con tabs y estado activo.
3. Falta migrar el lenguaje visual a dark/tokens aprobados.
4. El badge de conexión existe, pero está fuera del shell y en un lugar global del `App`.
5. Las pantallas del organizador dependen de headers y botones de vuelta locales.

---

## Riesgos Detectados

- Cambiar el shell puede afectar simultáneamente varias pantallas del organizador.
- Si el shell y el routing se mezclan en la misma US, el scope puede crecer demasiado.
- Algunas rutas detalle pueden requerir quedar temporalmente fuera del shell mientras se normaliza el montaje.

---

## Quality Gates Esperables

- `npm run build` en `frontend/`
- `npm run lint` en `frontend/`
- validacion UI/manual de navbar sticky, active state y tema dark

---

## Resultado

Contexto validado. La US queda lista para:

1. Fase 1 - Escenarios BDD
2. Fase 2 - Plan de implementacion
3. Espera de aprobacion explicita antes de Fase 3
