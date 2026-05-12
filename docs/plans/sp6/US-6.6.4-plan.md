# Plan de Implementación: US-6.6.4 — Página pública de torneo en ejecución

**Patrón:** React + TanStack Query (frontend puro — sin cambios de backend)
**Producto:** frontend
**Estimación Total:** 1h 25min

---

## Componentes a Implementar

### 1. Fix en PublicTorneosPage.tsx (5 min)
- [ ] `frontend/src/pages/PublicTorneosPage.tsx` línea 52
  - Cambiar destino "Ver panel" para visitante:
    `/portalapnea/${torneo.torneo_id}/panel` → `/portalapnea/${torneo.torneo_id}`
  - Tarea 3 de la spec — precondición de la navegación

### 2. Nueva página PublicTorneoDetallePage.tsx (50 min)
- [ ] `frontend/src/pages/PublicTorneoDetallePage.tsx` (nuevo)
  - Header idéntico al de `PublicTorneosPage` (AtaraxiaDive + Mi portal / Iniciar sesión)
  - Link "← Volver a torneos" → `/portalapnea`
  - Info del torneo: nombre, fecha, sede, entidad organizadora, badge de estado
  - Fetch de competencias via `fetchCompetenciasPorTorneo(torneoId)`
  - Por cada competencia: fetch de grilla via `fetchGrillaCompetencia(competenciaId, disciplina)`
  - Polling `refetchInterval: 30_000` en todos los queries
  - Estados de performance:
    - `AnunciadaAP` → gris, sin tarjeta ("Pendiente")
    - `Llamada` → badge resaltado "En curso"
    - `ResultadoRegistrado` / `EnRevision` / `Ejecutada` / `DNS` → muestra tarjeta asignada
  - Columnas grilla: Pos · Atleta · AP · OT · Estado · Tarjeta
  - Manejo de loading / error / sin competencias
  - Si torneo en `CREADO` / `CANCELADO`: mensaje "No disponible"

### 3. Registro de ruta en App.tsx (5 min)
- [ ] `frontend/src/App.tsx`
  - Agregar `<Route path="/portalapnea/:torneoId" element={<PublicTorneoDetallePage />} />`
  - Sin `RequireAuth` ni `RequireRole`

### 4. TypeScript build (5 min)
- [ ] `cd frontend && npm run build` — sin errores de tipos

---

**Estado:** 0/6 tareas completadas

---

*Generado: 2026-05-10 — US-6.6.4 INC-6.6*
