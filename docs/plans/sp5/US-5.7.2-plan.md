# Plan de Implementacion - US-5.7.2: Mi Grilla del atleta

**Incremento:** INC-5.7 | **Sprint:** SP5  
**Producto:** frontend  
**Patron:** React/Vite frontend con pagina nueva del portal atleta  
**Estimacion total:** 120 min

---

## Diagnostico

El portal atleta ya compone inscripciones, competencias, AP y grilla parcial mediante
`loadAtletaPortalSnapshot()`. La pantalla S-07 no existe. Los links actuales mandan a
`/atleta/mis-inscripciones`, por lo que el atleta no puede abrir la grilla completa de una
disciplina concreta.

La API necesaria existe:

- `fetchAtletaMe()` para obtener `atleta_id` real.
- `fetchGrillaCompetencia(competenciaId, disciplina)` para filas de grilla.
- `fetchEstadoCompetencia(competenciaId, disciplina)` para `grilla_confirmada`.

## Cambios por componente

### 1. Componentes de UI

- [ ] `frontend/src/components/atleta/OtHero.tsx` (20 min)
  - renderizar label "Tu Tiempo Oficial"
  - mostrar OT destacado
  - mostrar andarivel, posicion, torneo/disciplina y AP
  - soportar estado sin AP

- [ ] `frontend/src/components/atleta/GrillaRow.tsx` (20 min)
  - renderizar posicion, nombre, OT y andarivel
  - resaltar `isSelf` con fondo accent y borde izquierdo
  - mostrar chip `TU` para la fila propia

### 2. Pagina Mi Grilla

- [ ] `frontend/src/pages/atleta/AtletaMiGrillaPage.tsx` (35 min)
  - leer `competenciaId` de params y `disciplina` de query string
  - cargar `fetchAtletaMe`, `fetchGrillaCompetencia` y `fetchEstadoCompetencia`
  - ordenar grilla por `posicion`
  - detectar `miEntrada` por `entry.atleta_id === atleta.atleta_id`
  - renderizar aviso de grilla provisional si `grilla_confirmada === false`
  - renderizar estado vacio si no hay grilla o no existe fila del atleta
  - agregar CTA `Ver mis resultados` a `/atleta/resultados?competenciaId=...&disciplina=...`

### 3. Routing

- [ ] `frontend/src/App.tsx` (5 min)
  - registrar `/atleta/grilla/:competenciaId` protegido por rol atleta

### 4. Links de entrada

- [ ] `frontend/src/pages/atleta/AtletaHomePage.tsx` (10 min)
  - cambiar "Ver grilla" para apuntar a `/atleta/grilla/:competenciaId?disciplina=...`
  - mantener fallback si no hay `competenciaId`

- [ ] `frontend/src/pages/atleta/AtletaMisInscripcionesPage.tsx` (15 min)
  - agregar accion "Ver grilla" en disciplinas con `competenciaId`
  - deshabilitar/ocultar accion si no hay competencia asociada

### 5. Validacion

- [ ] `npm run build` en `frontend/` (5 min)
- [ ] ESLint focalizado sobre archivos modificados (5 min)
- [ ] Smoke manual con atleta inscripto en torneo en ejecucion (10 min)
- [ ] documentacion y reporte final (10 min)

## Decisiones clave

- No se usa `useAuthStore().userId` para identificar la fila propia porque ese valor es
  `usuario_id`, no `atleta_id`.
- La pagina carga `fetchAtletaMe()` y compara contra `GrillaAtletaDto.atleta_id`.
- `grilla_confirmada` se obtiene desde `fetchEstadoCompetencia`; no se infiere desde la grilla.
- La lista se ordena por `posicion`, no por OT.
- Los componentes quedan en `frontend/src/components/atleta/` porque S-08 tambien necesitara
  patrones visuales similares para filas resaltadas.

## Riesgos y mitigaciones

- Si `fetchEstadoCompetencia` falla pero la grilla carga, la pagina debe seguir mostrando la
  grilla sin bloquear toda la experiencia; el aviso provisional queda condicionado al dato disponible.
- Si el atleta autenticado no aparece en la grilla, se muestra estado vacio en vez de una hero
  incompleta.
- Si `competenciaId` o `disciplina` faltan en la URL, se muestra error de datos incompletos.

## Criterio de salida

La implementacion termina cuando:

1. `/atleta/grilla/:competenciaId?disciplina=...` carga sin errores.
2. La hero muestra OT, andarivel, posicion, AP, torneo/disciplina.
3. La grilla completa aparece ordenada por posicion.
4. La fila propia se resalta con chip `TU`.
5. El CTA de resultados conserva `competenciaId` y `disciplina`.
6. Los links desde Home y Mis inscripciones apuntan a la nueva pantalla.
