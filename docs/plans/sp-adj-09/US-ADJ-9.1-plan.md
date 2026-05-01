# Plan de Implementacion - US-ADJ-9.1: Shell del organizador

**Sprint:** SP-ADJ-09
**Patron:** React/Vite frontend
**Estimacion total:** 110 min

---

## Diagnostico

El rol organizador carece de un shell compartido. Hoy cada pantalla usa un layout aislado,
claro y sin navegación primaria persistente. Esta US debe construir la base visual y
navegacional del rol sin reimplementar todavía el contenido interno de todas las páginas.

## Cambios por componente

### 1. Shell y navbar compartida

- [ ] Crear componente `OrganizadorShell` o equivalente (25 min)
  - marca AtaraxiaDive
  - tabs primarios
  - badge de conexión
  - bloque de usuario
  - sticky top

- [ ] Reconvertir `OrganizadorLayout` para colgar del shell nuevo o sustituirlo (15 min)
  - tema dark
  - header secundario por sección
  - contenedor de contenido consistente

### 2. Estado activo y navegación primaria

- [ ] Definir mapa de tabs por ruta organizador (15 min)
  - `Panel`
  - `Grilla`
  - `Resultados`
  - `Jueces`
  - `Torneo`
  - `Audit Log`

- [ ] Integrar la navegación con `react-router-dom` usando la ruta actual visible (10 min)

### 3. Integración con datos de sesión y conexión

- [ ] Reutilizar `useAuthStore` para nombre/email visible (5 min)
- [ ] Reubicar o adaptar `HealthCheck` dentro del shell del organizador (10 min)

### 4. Montaje en páginas actuales

- [ ] Hacer que las páginas primarias del organizador rendericen dentro del shell nuevo (20 min)
  - sin reescribir aún toda la estructura de contenido
  - priorizando no romper rutas existentes en esta US

### 5. Validación

- [ ] `npm run build` en `frontend/` (3 min)
- [ ] `npm run lint` en `frontend/` (5 min)
- [ ] revisión manual de sticky, tema dark y active state (2 min)

## Decisiones clave

- Esta US no debe resolver todavía la reestructuración completa del routing; solo necesita el montaje suficiente para que el shell exista y se vea en las secciones principales.
- `HealthCheck` puede reutilizarse, pero debe integrarse al shell y no quedar flotando globalmente en `App`.
- El layout antiguo beige debe desaparecer de las páginas primarias del organizador.
- Si alguna página detalle no entra todavía en el shell en esta US, se documentará como excepción temporal y se resolverá en `US-ADJ-9.2` o posteriores.

## Riesgos y mitigaciones

- Riesgo: tocar demasiadas páginas a la vez.
  Mitigación: priorizar shell + layout + montaje mínimo, sin rediseñar todavía cada pantalla.

- Riesgo: el active state por ruta quede ambiguo.
  Mitigación: definir un mapa explícito de secciones primarias y usar matching intencional.

## Criterio de salida

La implementación de esta US termina cuando:

1. existe una navbar sticky compartida del organizador;
2. las secciones principales visibles usan tema dark aprobado;
3. el tab activo se refleja correctamente;
4. build y lint quedan ejecutados.
