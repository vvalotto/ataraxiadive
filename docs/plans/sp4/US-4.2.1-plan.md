# Plan de Implementación: US-4.2.1 — Scaffold Vite + React + PWA

**Patrón:** Frontend React (Vite + TypeScript + PWA)
**Producto:** frontend (nuevo directorio en raíz del monorepo)
**Estimación Total:** 1h 45min
**Modo:** `--skip-bdd` — criterios de aceptación verificados manualmente

> **Nota de implementación:** Vite 8 (default de `npm create vite@latest`) no era compatible con
> `vite-plugin-pwa@1.2.0` (requiere ≤ v7). Se downgradeó a Vite 6 + `@vitejs/plugin-react@5.2.0`.
> Tailwind v4 instalada (npm instaló v4.2.2 en lugar de v3) — usa `@tailwindcss/vite` y `@import "tailwindcss"` en CSS.

---

## Componentes a Implementar

### 1. Scaffold base (15 min)
- [x] `npm create vite@latest frontend -- --template react-ts` (5 min)
- [x] `tsconfig.app.json`: `"strict": true` agregado (2 min)
- [x] `.env.example` con `VITE_API_URL=http://localhost:8000` (3 min)
- [x] `.env` local (no commiteado) — cubierto por `.gitignore` raíz (2 min)

### 2. Dependencias instaladas
- [x] Tailwind v4 + `@tailwindcss/vite` (en lugar de PostCSS — Tailwind v4 usa plugin Vite)
- [x] React Router DOM v6: `npm install react-router-dom@6`
- [x] Zustand v5: `npm install zustand`
- [x] TanStack Query v5: `npm install @tanstack/react-query`
- [x] vite-plugin-pwa v1.2.0: `npm install -D vite-plugin-pwa` (con Vite 6)

### 3. Configuración vite.config.ts
- [x] Proxy: `/api → VITE_API_URL`, `/health → VITE_API_URL`
- [x] Plugin PWA: manifest (standalone + portrait + iconos 192/512) + Workbox NetworkFirst /api/** timeout 3s
- [x] Plugin Tailwind v4 (`@tailwindcss/vite`)

### 4. Estructura de directorios D-01
- [x] `frontend/src/pages/juez/` `.gitkeep`
- [x] `frontend/src/pages/organizador/` `.gitkeep`
- [x] `frontend/src/pages/atleta/` `.gitkeep`
- [x] `frontend/src/hooks/` `.gitkeep`
- [x] `frontend/src/stores/` (con `useConnectionStore.ts`)
- [x] `frontend/src/api/` (con `health.ts`)
- [x] `frontend/src/components/` (con `HealthCheck.tsx`)
- [x] Archivos de ejemplo de Vite eliminados (`App.css`, `assets/`)

### 5. Configuración Tailwind v4
- [x] `src/index.css`: `@import "tailwindcss"` (directiva v4)
- [x] Sin `tailwind.config.js` — v4 usa CSS-first, no requiere config file

### 6. API client: `src/api/health.ts`
- [x] `fetchHealth()` → `GET /health`
- [x] `interface HealthResponse { status: string }`

### 7. Store: `src/stores/useConnectionStore.ts`
- [x] Zustand store `{ isOnline: boolean }`
- [x] `useConnectionSync()` hook — suscripción a eventos `online`/`offline`

### 8. Componente: `src/components/HealthCheck.tsx`
- [x] `useQuery({ queryKey: ['health'], queryFn: fetchHealth, refetchInterval: 30_000 })`
- [x] Indicador verde `"Backend: ✓ online"` / rojo `"Backend: ✗ sin conexión"`

### 9. App.tsx y main.tsx
- [x] `main.tsx`: `QueryClientProvider` wrappea `<App />`
- [x] `App.tsx`: `useConnectionSync()` + `<HealthCheck />` en ruta base

### 10. Validación — `npm run build`
- [x] `npm run build` → exitcode 0, sin errores TypeScript strict
- [x] PWA generada: `dist/sw.js`, `dist/workbox-*.js`, `dist/manifest.webmanifest`
- [ ] `npm run dev` — verificación manual pendiente (online/offline HealthCheck)
- [ ] Manifest PWA verificado en Chrome DevTools
- [ ] App aparece como instalable

---

## Integración con monorepo

- [x] `.gitignore` raíz ya tenía `frontend/node_modules/`, `frontend/dist/`, patrón `.env`
- [x] `GET /health` existe desde SP1

---

## Quality gates

- [x] `npm run build` sin errores TypeScript (strict) — ✅ exitcode 0
- [ ] Checklist manual completo (pendiente verificación con backend corriendo)

---

**Estado:** 9/10 secciones completadas — verificación manual pendiente

*Plan generado: 2026-04-11 — US-4.2.1 INC-4.2 SP4*
*Implementado: 2026-04-11*
