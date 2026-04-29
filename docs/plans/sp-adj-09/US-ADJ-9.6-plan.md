# Plan de Implementacion - US-ADJ-9.6

## Objetivo

Reubicar `Grilla`, `Jueces`, `Torneo` y `Audit Log` dentro de una arquitectura UX consistente del organizador, manteniendo el shell dark persistente y separando con claridad la navegacion primaria de las vistas contextuales.

## Hallazgos que el plan resuelve

1. La navbar superior no preserva el `torneo_id`, por lo que el shell pierde contexto al cambiar de seccion.
2. `DetalleTorneoPage` todavia concentra accesos primarios y tabs locales que compiten con la navbar global.
3. `Grilla`, `Jueces`, `Audit Log` y las auditorias internas no comparten del todo el mismo lenguaje visual dark del shell.
4. Las vistas contextuales mantienen botones de retorno redundantes que refuerzan una jerarquia vieja basada en "volver".

## Estrategia

### 1. Normalizar el shell con contexto de torneo persistente

- Ajustar `OrganizadorLayout` para detectar y propagar el torneo activo cuando exista.
- Hacer que los links de la navbar superior mantengan `torneo_id` en las secciones primarias del organizador.
- Mantener el comportamiento actual sin navbar para home y selectores sin torneo elegido.

### 2. Redefinir el rol de la seccion Torneo

- Reducir `DetalleTorneoPage` a una vista contextual de gestion del torneo activo.
- Eliminar tabs o accesos locales equivalentes a `Grilla`, `Jueces`, `Resultados` y `Audit Log`.
- Conservar solo la informacion y acciones propias del torneo dentro de esa vista.

### 3. Alinear secciones primarias al shell dark aprobado

- Revisar `OrganizadorGrillaPage`, `OrganizadorJuecesPage` y `TorneoCompetenciasPage` para que usen un lenguaje visual consistente con `Panel` y `Resultados`.
- Reencuadrar la seccion `Audit Log` como pagina primaria del shell, con copy, titulos y acciones acordes.

### 4. Mantener shell persistente en vistas detalle

- Ajustar `AuditoriaCompetenciaPage` y `AuditoriaPerformancePage` para que conserven la navbar principal visible y reduzcan acciones redundantes.
- Verificar que la navegacion contextual siga disponible sin reemplazar el shell.

## Archivos objetivo

- `frontend/src/components/organizador/OrganizadorLayout.tsx`
- `frontend/src/pages/organizador/DetalleTorneoPage.tsx`
- `frontend/src/pages/organizador/OrganizadorGrillaPage.tsx`
- `frontend/src/pages/organizador/OrganizadorJuecesPage.tsx`
- `frontend/src/pages/organizador/TorneoCompetenciasPage.tsx`
- `frontend/src/pages/organizador/AuditoriaCompetenciaPage.tsx`
- `frontend/src/pages/organizador/AuditoriaPerformancePage.tsx`
- `frontend/src/App.tsx` si hace falta normalizar rutas o integracion final

## Validacion prevista

- `npm run build` en `frontend/`
- `npm run lint` en `frontend/`
- chequeo manual de:
  - persistencia de `torneo_id` al navegar por la navbar
  - ausencia de tabs primarios redundantes en `DetalleTorneoPage`
  - navbar visible en auditorias de competencia y performance
  - coherencia visual dark en `Grilla`, `Jueces`, `Torneo` y `Audit Log`

## Criterio de salida

- El organizador cambia entre `Panel / Grilla / Resultados / Jueces / Torneo / Audit Log` sin perder el torneo activo.
- `DetalleTorneoPage` deja de funcionar como concentrador de navegacion primaria.
- Las auditorias siguen siendo contextuales, pero el shell principal permanece visible.
