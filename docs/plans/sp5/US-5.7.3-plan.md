# Plan de Implementacion - US-5.7.3: Mis resultados del atleta

**Incremento:** INC-5.7 | **Sprint:** SP5  
**Producto:** frontend  
**Patron:** React/Vite frontend sobre pagina existente  
**Estimacion total:** 130 min

---

## Diagnostico

`AtletaResultadosPage` existe pero es un placeholder. El portal atleta ya tiene
`loadAtletaPortalSnapshot()`, que entrega atleta, inscripciones, torneos, competencias,
AP, OT, andarivel y posicion. Esta US debe enriquecer ese snapshot con rankings para
mostrar solo el resultado propio del atleta.

## Cambios por componente

### 1. Componentes de resultado

- [ ] `frontend/src/components/atleta/ResultHero.tsx` (25 min)
  - mostrar disciplina, estado visual, RP, AP, diferencia AP-RP, puntos y chip `EN PODIO`
  - soportar estados BLANCA, ROJA, DNS y PENDIENTE
  - aplicar border/color segun estado

- [ ] `frontend/src/components/atleta/DisciplinaPendienteCard.tsx` (20 min)
  - mostrar disciplina pendiente, OT, AP y andarivel si existen
  - mostrar texto "Resultado disponible al cierre de la disciplina"

### 2. Composicion de datos

- [ ] `frontend/src/pages/atleta/AtletaResultadosPage.tsx` (45 min)
  - reemplazar placeholder
  - cargar `loadAtletaPortalSnapshot()`
  - para cada entry con `competenciaId`, cargar `fetchRankingCompetencia`
  - tratar errores de ranking como pendiente
  - buscar entrada propia por `entrada.atleta_id === snapshot.atleta.atleta_id`
  - agrupar resultados por torneo

### 3. Helpers de presentacion

- [ ] `frontend/src/pages/atleta/AtletaResultadosPage.tsx` o helper local (15 min)
  - formatear RP con `formatMarca`
  - calcular diferencia AP-RP con signo cuando ambos valores son numericos
  - mapear tarjeta/DNS a estado visual

### 4. Validacion

- [ ] `npm run build` en `frontend/` (5 min)
- [ ] ESLint focalizado sobre archivos modificados (5 min)
- [ ] Smoke manual con atleta del torneo en ejecucion (10 min)
- [ ] documentacion y reporte final (10 min)

## Decisiones clave

- No se agrega backend: se consume `fetchRankingCompetencia`.
- Si `fetchRankingCompetencia` falla o `ranking.calculado === false`, la disciplina queda pendiente.
- La pagina muestra solo el resultado del atleta autenticado, no rankings completos. US-5.7.4 agrega rankings/podios.
- La diferencia AP-RP se calcula solo si AP y RP son numericos y no hay DNS.
- Para disciplinas de tiempo se reutiliza `formatMarca(value, unidad)`; la diferencia se deja en segundos si la unidad es `Segundos`.

## Riesgos y mitigaciones

- Rankings no existentes pueden devolver error HTTP: se capturan como pendiente.
- Una disciplina inscripta puede no tener `competenciaId`: se muestra pendiente con datos disponibles.
- El payload de tarjeta puede venir null: se muestra `PENDIENTE` salvo `es_dns=true`.

## Criterio de salida

La implementacion termina cuando:

1. `/atleta/resultados` deja de ser placeholder.
2. Las disciplinas con ranking calculado muestran resultado propio, RP, tarjeta y puntos.
3. Las disciplinas sin ranking muestran card pendiente.
4. DNS muestra RP y puntos como `-`.
5. `EN PODIO` aparece solo para `en_podio=true`.
6. El build y lint focalizado pasan.
