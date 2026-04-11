# Plan de Implementación: US-4.2.1 — Scaffold Vite + React + PWA

**Patrón:** Frontend React (Vite + TypeScript + PWA)
**Producto:** frontend (nuevo directorio en raíz del monorepo)
**Estimación Total:** 1h 45min
**Modo:** `--skip-bdd` — criterios de aceptación verificados manualmente

---

## Componentes a Implementar

### 1. Scaffold base (15 min)
- [ ] `npm create vite@latest frontend -- --template react-ts` (5 min)
  - Genera estructura base: `frontend/` con `src/main.tsx`, `src/App.tsx`, `tsconfig.json`, `vite.config.ts`
- [ ] Validar `tsconfig.json`: `"strict": true` (2 min)
- [ ] Crear `.env.example` con `VITE_API_URL=http://localhost:8000` (3 min)
- [ ] Crear `.env` local (no commiteado) con el mismo valor (2 min)
- [ ] Agregar `frontend/.env` a `.gitignore` (3 min)

### 2. Dependencias de producción (15 min)
- [ ] Tailwind CSS + PostCSS: `npm install -D tailwindcss postcss autoprefixer` + `npx tailwindcss init -p` (5 min)
- [ ] React Router DOM v6: `npm install react-router-dom@6` (3 min)
- [ ] Zustand: `npm install zustand` (2 min)
- [ ] TanStack Query v5: `npm install @tanstack/react-query` (3 min)
- [ ] vite-plugin-pwa: `npm install -D vite-plugin-pwa` (2 min)

### 3. Configuración vite.config.ts (15 min)
- [ ] Proxy al backend: `/api → VITE_API_URL` (5 min)
- [ ] Plugin PWA: manifest + workbox `NetworkFirst` con timeout 3s para `/api/**` (10 min)
  - `display: "standalone"`, `orientation: "portrait"`
  - Nombre: `AtaraxiaDive`, short_name: `AtaraxiaDive`
  - Iconos placeholder (192x192 y 512x512)

### 4. Estructura de directorios D-01 (10 min)
- [ ] Crear directorios vacíos con `.gitkeep`:
  - `frontend/src/pages/juez/`
  - `frontend/src/pages/organizador/`
  - `frontend/src/pages/atleta/`
  - `frontend/src/hooks/`
  - `frontend/src/stores/`
  - `frontend/src/api/`
  - `frontend/src/components/`
- [ ] Limpiar archivos de ejemplo de Vite: `App.css`, `assets/react.svg`, `vite.svg` (2 min)

### 5. Configuración Tailwind (5 min)
- [ ] `tailwind.config.js`: content paths apuntando a `./src/**/*.{ts,tsx}` (3 min)
- [ ] `src/index.css`: directivas `@tailwind base/components/utilities` (2 min)

### 6. API client: `src/api/health.ts` (10 min)
- [ ] Función `fetchHealth()` → `GET /api/health` (o `GET /health` directo)
  - Retorna `{ status: "ok" }` o lanza error
- [ ] Tipar respuesta: `interface HealthResponse { status: string }`

### 7. Store: `src/stores/useConnectionStore.ts` (10 min)
- [ ] Zustand store con `{ isOnline: boolean }` inicializado con `navigator.onLine`
- [ ] `useEffect` que subscribe a eventos `online`/`offline` del window

### 8. Componente: `src/components/HealthCheck.tsx` (15 min)
- [ ] Usa TanStack Query: `useQuery({ queryKey: ['health'], queryFn: fetchHealth, refetchInterval: 30_000 })`
- [ ] Muestra indicador verde si `status === "ok"`, rojo si error/loading-failed
- [ ] Texto: `"Backend: ✓ online"` / `"Backend: ✗ sin conexión"`

### 9. App.tsx y main.tsx (10 min)
- [ ] `main.tsx`: wrappear con `QueryClientProvider` (TanStack Query)
- [ ] `App.tsx`: renderizar `<HealthCheck />` en ruta `/` como placeholder inicial
  - Routing se expande en US-4.2.2 — aquí solo ruta base

### 10. Validación manual (checklist) (10 min)
- [ ] `npm run dev` levanta sin errores en consola
- [ ] `npm run build` termina con código 0 sin errores TypeScript
- [ ] `HealthCheck` muestra verde con backend corriendo
- [ ] `HealthCheck` muestra rojo con backend apagado
- [ ] Manifest PWA válido: `display: standalone`, `orientation: portrait`
- [ ] App aparece como instalable en Chrome/Safari mobile (o Chrome DevTools simula)
- [ ] Estructura `frontend/src/` respeta D-01
- [ ] `tsconfig.json` tiene `"strict": true`
- [ ] `.env.example` con `VITE_API_URL=http://localhost:8000`

---

## Integración con monorepo

- [ ] Agregar `frontend/node_modules/` y `frontend/dist/` a `.gitignore` raíz (3 min)
- [ ] Verificar que `src/app.py` tiene endpoint `GET /health` → `{"status": "ok"}` (ya existe desde SP1) (2 min)

---

## Quality gates

> US de infraestructura frontend — no aplican las métricas Python (Pylint, mypy, pytest).
> Los quality gates son los criterios de aceptación del checklist de la spec.

- [ ] `npm run build` sin errores TypeScript (strict) ← equivalente a mypy
- [ ] Todos los ítems del checklist de la US aprobados manualmente

---

**Estado:** 0/10 secciones completadas

*Plan generado: 2026-04-11 — US-4.2.1 INC-4.2 SP4*
