# Plan de Implementacion - US-5.7.4: Rankings y podios del atleta

**Incremento:** INC-5.7 | **Sprint:** SP5
**Producto:** frontend
**Patron:** extension de AtletaResultadosPage existente
**Estimacion total:** 100 min

---

## Diagnostico

`AtletaResultadosPage` (US-5.7.3) ya carga snapshot + rankings. Esta US agrega:
1. `RankingCard` + `RankingRow`: ranking de categoria propia debajo de cada ResultHero
2. `OverallCard`: seccion overall al pie de la pagina
3. Carga de grilla por competencia para resolver nombres (join atleta_id → nombre)
4. Queries de overall por torneo via `fetchOverall`

La categoria del atleta se obtiene de `entry.inscripcion.categoria`.
El ranking se filtra por la categoria que coincide con `inscripcion.categoria`.

## Cambios por componente

### 1. RankingRow.tsx (20 min)
- props: posicion, nombre, rp, puntos, tarjeta, esDns, isSelf
- chip tarjeta: BLANCA (verde), ROJA (rojo), DNS (gris)
- top 3: icono 🥇🥈🥉
- isSelf: fondo sky-500/10 + texto "Vos"

### 2. RankingCard.tsx (20 min)
- props: categoria, entradas, nombresPorId, atletaId, calculado, unidad
- filtrar entradas por categoriaAtleta (ya viene filtrado desde la pagina)
- pie: "Ranking final" / "Ranking parcial"

### 3. OverallCard.tsx (20 min)
- props: overall (OverallDto | null), atletaId, nombresPorId, categoriaAtleta
- estado vacio si !overall?.calculado o rankings vacios
- solo mostrar categoria propia

### 4. AtletaResultadosPage.tsx — extension (30 min)
- agregar queries de grilla por competencia (useQueries)
- agregar queries de overall por torneo (useQueries, uno por torneo distinto)
- construir Map<competenciaId, Map<atleta_id, nombre>>
- pasar ranking filtrado por categoria a RankingCard
- agregar OverallCard al final de cada seccion de torneo

### 5. Validacion (10 min)
- npm run build
- tsc --noEmit
- eslint sobre archivos nuevos/modificados

## Decisiones clave

- La grilla se carga por competencia (no por torneo) para mapear nombres.
- Si la grilla falla, fallback: truncar atleta_id a 8 chars.
- La categoria del ranking se determina buscando en `ranking.rankings` la categoria
  que contiene la entrada del atleta propio (no se asume que el string de categoria
  en el ranking coincide exactamente con el de la inscripcion).
- Overall: una query por torneo_id unico entre todas las entries.
