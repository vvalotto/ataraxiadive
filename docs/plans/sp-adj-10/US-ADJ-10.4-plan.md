# Plan de Implementación — US-ADJ-10.4

**US:** Vista post-torneo en portal del atleta  
**Branch:** `feature/US-ADJ-10.4-vista-post-torneo`  
**Estimación total:** 60 min  
**Tipo:** Frontend puro — sin cambios en `src/`

---

## Análisis del estado actual

| Elemento | Estado | Problema |
|---|---|---|
| `AtletaHomePage` | Muestra solo PREPARACION/EJECUCION | CERRADO invisible para el atleta |
| `AtletaTorneoDetallePage` | CERRADO = badge + info básica | Sin resultados finales |
| `AtletaResultadosPage` | Ya maneja CERRADO correctamente | Punto de entrada no natural |
| `GrupoResultados` | Definido localmente en ResultadosPage | No reutilizable |

---

## Tareas

### T1 — Extraer `GrupoResultados` a componente compartido (15 min)

**Archivo nuevo:** `frontend/src/components/atleta/GrupoResultados.tsx`

Extraer de `AtletaResultadosPage.tsx`:
- Interface `ResultadoEntry`
- Funciones helpers: `findMiResultado`, `findMiCategoriaEntradas`, `groupByTorneo`, `getEstadoResultado`, `formatResultado`, `calcularDiferencia`
- Componente `GrupoResultados` (con sus tipos y props)

Exportar todo desde el nuevo archivo.

**Archivo modificado:** `frontend/src/pages/atleta/AtletaResultadosPage.tsx`

Reemplazar definiciones locales con imports del nuevo componente.

**INV cubierto:** INV-ADJ-10.4-04 — reutiliza sin duplicar lógica.

---

### T2 — `AtletaHomePage.tsx`: sección "Torneos finalizados" (25 min)

**Lógica:**
1. Filtrar `entries` donde `torneo.estado === 'CERRADO'` → `entriesCerradas`
2. Agrupar por torneo → máx. 3 torneos más recientes (INV-ADJ-10.4-05)
3. Cargar ranking queries con `useQueries` para esas entries (para mostrar resultado rápido)
4. Renderizar sección nueva después de "Torneos vinculados":

```tsx
<section>
  <header>
    <p>Torneos finalizados</p>
    <Link to="/atleta/resultados">Ver todos</Link>
  </header>
  {torneosCerrados.map(({ torneo, disciplinas }) => (
    <Link to={`/atleta/torneos/${torneo.torneo_id}`}>
      {/* nombre del torneo + chips por disciplina con tarjeta+RP */}
    </Link>
  ))}
</section>
```

**Tarjeta rápida por disciplina:** chip que muestra `formatDisciplina` + tarjeta (color) + RP + badge podio.  
**Sin componente nuevo:** inline dentro del map, no justifica extraer `ResultadoRapidoCard`.

**INV cubiertos:** INV-ADJ-10.4-01, 03, 05.

---

### T3 — `AtletaTorneoDetallePage.tsx`: resultados para CERRADO (20 min)

**Lógica cuando `torneo.estado === 'CERRADO'` y `inscripcion !== null`:**

1. Agregar query para `loadAtletaPortalSnapshot` (enabled: CERRADO + tiene inscripcion)
2. Filtrar `snapshot.entries` por `torneoId`
3. Cargar `useQueries` para:
   - ranking por entry (fetchRankingCompetencia)
   - grilla por entry (fetchGrillaCompetencia — para nombres)
   - overall del torneo (fetchOverall)
4. Construir `ResultadoEntry[]` y `overallPorTorneo`
5. Renderizar `<GrupoResultados>` en lugar del bloque "Ya estás inscripto" estático

El bloque "Ya estás inscripto" se mantiene para estados no-CERRADO.

**INV cubiertos:** INV-ADJ-10.4-02 (estado vacío si DNS), 04.

---

## Archivos a modificar/crear

| Archivo | Acción |
|---|---|
| `frontend/src/components/atleta/GrupoResultados.tsx` | CREAR — extraer de ResultadosPage |
| `frontend/src/pages/atleta/AtletaResultadosPage.tsx` | MODIFICAR — importar desde componente |
| `frontend/src/pages/atleta/AtletaHomePage.tsx` | MODIFICAR — sección Torneos finalizados |
| `frontend/src/pages/atleta/AtletaTorneoDetallePage.tsx` | MODIFICAR — resultados para CERRADO |

## Validación

- `npx tsc --noEmit` — 0 errores
- `npm run build` — build exitoso
- Validación visual manual (servidores ya corriendo en :5173)

---

*Estimación: T1 15min + T2 25min + T3 20min = 60 min*
