# Plan de Implementacion - US-ADJ-9.2: Routing primario del organizador

**Sprint:** SP-ADJ-09
**Patron:** React/Vite frontend
**Estimacion total:** 140 min

---

## Diagnostico

`US-ADJ-9.1` resolvio el shell visual, pero la navegacion del organizador sigue
apoyada en rutas dispersas y en tabs locales dentro de vistas detalle. Esta US debe
normalizar el primer nivel del rol para que la navbar primaria represente destinos
reales y persistentes, sin rehacer todavia todo el contenido de las secciones futuras.

## Cambios por area

### 1. Reestructuracion de rutas base

- [ ] Normalizar las rutas primarias del organizador en `App.tsx` (20 min)
  - home del organizador
  - panel
  - grilla
  - resultados
  - jueces
  - torneo
  - audit log

- [ ] Ajustar `RootRedirect` para que el organizador aterrice en la home formal (10 min)

- [ ] Definir redirects de compatibilidad para rutas historicas que sigan siendo referenciadas (10 min)

### 2. Integracion con el shell

- [ ] Actualizar `OrganizadorLayout` para que todos los tabs primarios apunten a destinos reales (15 min)
- [ ] Refinar la deteccion de seccion activa con el nuevo mapa de rutas (10 min)

### 3. Separacion entre vistas primarias y vistas detalle

- [ ] Reubicar `DetalleTorneoPage` para que deje de concentrar tabs de navegacion primaria (25 min)
  - mantener detalle/contexto del torneo
  - sacar dependencias a `Grilla` y `Jueces` como tabs internas

- [ ] Ajustar paginas del rol que hoy dependen de `Volver al dashboard` como retorno principal (20 min)
  - `CrearTorneoPage`
  - `UsuariosPage`
  - `TorneoCompetenciasPage`
  - `AuditoriaCompetenciaPage`
  - `ResultadosPage`

### 4. Compatibilidad y contenido minimo

- [ ] Si alguna seccion primaria todavia no tiene pantalla final, montar un contenedor transitorio dentro del shell (10 min)
  - debe preservar la navegacion correcta
  - no debe volver a tabs deshabilitadas

### 5. Validacion

- [ ] `npm run build` en `frontend/` (5 min)
- [ ] `npm run lint` en `frontend/` (5 min)
- [ ] validacion manual del flujo de navegacion primaria y rutas historicas (10 min)

## Decisiones clave

- Esta US debe resolver routing, no el diseño final del contenido de cada seccion.
- Las rutas primarias deben existir aunque alguna pantalla use contenido transitorio.
- Las vistas detalle se mantienen, pero dejan de ser sustituto del primer nivel.
- Los redirects de compatibilidad son preferibles a romper deep-links existentes.

## Riesgos y mitigaciones

- Riesgo: romper navegacion existente desde botones internos.
  Mitigacion: conservar aliases y redirects mientras se normaliza el shell.

- Riesgo: mover demasiada funcionalidad de `DetalleTorneoPage` en una sola pasada.
  Mitigacion: separar rutas primarias de detalle sin reescribir aun todos los paneles.

- Riesgo: superponer scope con `US-ADJ-9.3` y `US-ADJ-9.4`.
  Mitigacion: limitar esta US a estructura de rutas y montaje, no al rediseño del contenido.

## Criterio de salida

La implementacion de esta US termina cuando:

1. el organizador aterriza en una home clara del rol;
2. cada tab primario visible del shell apunta a una ruta real;
3. las vistas detalle conservan la navbar primaria y dejan de depender del patron
   dominante "Volver al dashboard";
4. build y lint quedan ejecutados.
