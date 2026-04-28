# US-ADJ-9.2 - Fase 0: Validacion de Contexto

**Fecha:** 2026-04-28
**Producto:** `frontend`
**Sprint:** `SP-ADJ-09`
**Spec canonica:** `docs/specs/sp-adj-09/US-ADJ-9.2.md`

---

## Historia

**US:** US-ADJ-9.2 - Routing primario del organizador

Como **organizador**, quiero que las rutas del panel reflejen la navegacion
primaria aprobada para que cada seccion principal tenga una ubicacion clara y
consistente dentro del sistema.

---

## Fuentes de Verdad Validadas

- `docs/specs/sp-adj-09/US-ADJ-9.2.md`
- `docs/design/ux/wireframes-organizador.md`
- `docs/design/ux/prototipos/prototipo-organizador.html`
- `docs/design/ux/decisiones-frontend.md`
- `docs/plans/sp-adj-09/PLAN-SP-ADJ-09.md`
- `frontend/src/App.tsx`
- `frontend/src/components/organizador/OrganizadorLayout.tsx`
- `frontend/src/pages/organizador/DetalleTorneoPage.tsx`

---

## Contexto Relevante

### Routing actual del rol organizador

- `frontend/src/App.tsx` define rutas independientes y heterogeneas:
  - `/organizador/dashboard`
  - `/organizador/torneos/nuevo`
  - `/organizador/usuarios`
  - `/organizador/torneo/:torneoId`
  - `/organizador/torneos/:torneoId/competencias`
  - `/organizador/competencias/:competenciaId/auditoria`
  - `/organizador/competencias/:competenciaId/auditoria/:atletaId`
  - `/organizador/resultados`
- El redirect inicial del rol organizador sigue cayendo en `/organizador/dashboard`.

### Shell disponible desde US-ADJ-9.1

- `OrganizadorLayout.tsx` ya provee navbar dark y sticky.
- El shell todavia no controla rutas primarias reales:
  - `Grilla`, `Jueces` y `Audit Log` siguen deshabilitadas.
  - `Torneo` y `Panel` reutilizan `dashboard` como destino.
- El estado activo hoy se resuelve por heuristicas de pathname, no por una
  jerarquia de rutas normalizada.

### Navegacion contextual que invade el primer nivel

- `DetalleTorneoPage.tsx` contiene tabs internas `Detalle`, `Inscriptos`, `Grilla`,
  `Jueces` y `Ejecucion`.
- Varias pantallas siguen dependiendo de links a `/organizador/dashboard` como
  mecanismo principal de retorno.
- La home del organizador y el dashboard operativo todavia no estan separados a nivel ruta.

### Restriccion operativa detectada

- En este repo local no se pudieron crear branches con slash (`feature/...`) por
  una limitacion sobre `.git/refs`.
- La branch se creo como `feature-US-ADJ-9.2-routing-organizador`, manteniendo el
  identificador de la US aunque no el separador canonico.

---

## Gaps Detectados

1. El redirect inicial del organizador no aterriza todavia en la home formal del rol.
2. La navbar primaria no esta respaldada por destinos reales para todas sus secciones.
3. Las tabs internas de `DetalleTorneoPage` siguen ocupando el lugar de navegacion
   principal para `Grilla`, `Jueces` y parte de `Torneo`.
4. El patron "Volver al dashboard" sigue apareciendo en varias pantallas del rol.
5. La jerarquia actual mezcla vistas primarias con vistas detalle sin una convención consistente.

---

## Riesgos Detectados

- Reestructurar rutas puede romper links internos existentes si no se dejan redirects.
- Separar home, dashboard operativo y vistas detalle puede requerir ajustes en varias páginas.
- Si esta US absorbe demasiado contenido de las siguientes US, el scope puede crecer.

---

## Quality Gates Esperables

- `npm run build` en `frontend/`
- `npm run lint` en `frontend/`
- validacion UI/manual del flujo de navegacion primaria persistente

---

## Resultado

Contexto validado. La US queda lista para:

1. Fase 1 - Escenarios BDD
2. Fase 2 - Plan de implementacion
3. Espera de aprobacion explicita antes de Fase 3
