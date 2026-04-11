# Reporte de Implementación: US-4.2.1

**US:** US-4.2.1 — Scaffold Vite + React + PWA — fundación del frontend
**Incremento:** INC-4.2
**Sprint:** SP4 — La Plataforma
**Fecha:** 2026-04-11
**Branch:** `feature/US-4.2.1-scaffold-vite-react`
**Commit:** `6a079ad`
**Modo:** `--skip-bdd`

---

## Resumen de Implementación

### Artefactos creados

| Artefacto | Path | Descripción |
|-----------|------|-------------|
| Proyecto Vite | `frontend/` | Scaffold React + TypeScript |
| Config bundler | `frontend/vite.config.ts` | Proxy backend + PWA + Tailwind v4 |
| TS config | `frontend/tsconfig.app.json` | `strict: true` activado |
| CSS base | `frontend/src/index.css` | `@import "tailwindcss"` (v4) |
| API client | `frontend/src/api/health.ts` | `fetchHealth() → GET /health` |
| Store | `frontend/src/stores/useConnectionStore.ts` | Zustand + `navigator.onLine` |
| Componente | `frontend/src/components/HealthCheck.tsx` | TanStack Query, refetch 30s |
| App entry | `frontend/src/App.tsx` | `<HealthCheck />` + `useConnectionSync()` |
| Main entry | `frontend/src/main.tsx` | `QueryClientProvider` wrapper |
| Env example | `frontend/.env.example` | `VITE_API_URL=http://localhost:8000` |
| Iconos PWA | `frontend/public/pwa-192x192.png` + `512x512.png` | Placeholder azul |
| Estructura D-01 | `pages/juez|organizador|atleta/`, `hooks/`, `stores/`, `api/`, `components/` | INV-FE-01 ✅ |
| Plan | `docs/plans/sp4/US-4.2.1-plan.md` | Marcado como completado |
| Matrix | `docs/traceability/matrix.md` | v1.12 — §13 INC-4.2 agregado |

### Stack instalado

| Dependencia | Versión | Rol |
|-------------|---------|-----|
| Vite | 6.4.2 | Bundler (downgradeado de v8 — incompatibilidad vite-plugin-pwa) |
| React | 19.2.4 | Framework UI |
| TypeScript | 6.0.2 | Tipado estático, strict mode |
| Tailwind CSS | 4.2.2 | Estilos (v4, CSS-first, sin config JS) |
| @tailwindcss/vite | 4.2.2 | Plugin Vite para Tailwind v4 |
| vite-plugin-pwa | 1.2.0 | PWA + Service Worker + manifest |
| React Router DOM | 6.30.3 | Routing (base para US-4.2.2) |
| Zustand | 5.0.12 | State management |
| TanStack Query | 5.97.0 | Data fetching + cache |
| @vitejs/plugin-react | 5.2.0 | Plugin React (downgradeado de v6 — requería Vite 8) |

### Invariantes verificados

| Invariante | Descripción | Estado |
|-----------|-------------|--------|
| INV-FE-01 | Estructura D-01 respetada | ✅ |
| INV-FE-02 | TypeScript strict mode | ✅ `tsconfig.app.json` |
| INV-FE-03 | `VITE_API_URL` configurable | ✅ `.env.example` + proxy |
| INV-FE-04 | Manifest: `portrait` + `standalone` | ✅ `vite.config.ts` |
| INV-FE-05 | `npm run build` sin errores | ✅ exitcode 0 |
| INV-FE-06 | Service Worker NetworkFirst timeout 3s para `/api/**` | ✅ Workbox config |

---

## Quality Gates

| Gate | Resultado |
|------|-----------|
| `npm run build` (TypeScript strict) | ✅ exitcode 0 — 82 módulos, 235KB bundle |
| PWA generada | ✅ `dist/sw.js` + `dist/workbox-*.js` + `dist/manifest.webmanifest` |
| Estructura D-01 | ✅ |
| Verificación manual (`npm run dev` + HealthCheck) | ⏳ Pendiente — verificar con backend corriendo |

---

## Decisiones técnicas

1. **Vite 6 en lugar de v8:** `npm create vite@latest` instaló Vite 8, pero `vite-plugin-pwa@1.2.0` requiere ≤ v7. Se downgradeó a Vite 6 + `@vitejs/plugin-react@5.2.0`.

2. **Tailwind v4 en lugar de v3:** npm instaló v4.2.2. La configuración difiere de v3: usa `@import "tailwindcss"` en CSS en lugar de las tres directivas, y `@tailwindcss/vite` como plugin (sin PostCSS config separado ni `tailwind.config.js`).

3. **Proxy dual `/api` y `/health`:** el endpoint de health del backend vive en `/health`, no en `/api/health`. Se agregó ambos al proxy para cubrir ambas rutas.

4. **Iconos PWA placeholder:** PNGs mínimos válidos (cuadrado azul sólido). Deben reemplazarse por iconos reales en INC-4.5 (diseño visual).

---

## Pendiente para verificación manual

- [ ] `npm run dev` levanta sin errores en consola del navegador
- [ ] HealthCheck muestra verde con `uv run fastapi dev src/app.py` corriendo
- [ ] HealthCheck muestra rojo con el backend apagado
- [ ] Manifest PWA verificado en Chrome DevTools → Application → Manifest
- [ ] App aparece como instalable (botón "Instalar" en Chrome)

---

## Siguiente US

**US-4.2.2** — Autenticación JWT: `useAuthStore` + `LoginPage` + `RequireRole` HOC + routing `/juez/*` `/organizador/*`
Branch: `feature/US-4.2.2-autenticacion-jwt`

---

*Generado: 2026-04-11 — `/implement-us US-4.2.1`*
