# Decisiones de Stack Frontend — AtaraxiaDive

> Artefacto INC-4.0 · Decisiones técnicas que habilitan INC-4.2 (implementación React)
> Fecha: 2026-04-05
> Ver también: ADR-003 (React PWA), ADR-010 (sin Docker)

---

## Contexto

INC-4.0 produjo cinco artefactos de UX validados:

- `prototipo-juez.html` + `wireframes-juez.md` — interfaz mobile-first del juez
- `prototipo-organizador.html` + `wireframes-organizador.md` — panel desktop del organizador en vivo
- `prototipo-atleta.html` + `wireframes-atleta.md` — portal mobile del atleta
- `prototipo-registro-roles.html` + `wireframes-registro-roles.md` — onboarding y gestión multirol
- `prototipo-setup-torneo.html` + `wireframes-setup-torneo.md` — preparación del torneo (pre-ejecución)

Los prototipos son HTML/CSS/JS puros (sin framework) y funcionan como contratos visuales.
INC-4.2 reimplementa esos prototipos como componentes React con lógica real conectada a la API.

Este documento formaliza las decisiones de stack necesarias para iniciar INC-4.2.

---

## Decisiones

### D-01 — Bundler y scaffolding: Vite + React + TypeScript

**Decisión:** `npm create vite@latest frontend -- --template react-ts`

**Justificación:**
- HMR instantáneo — crítico para el ciclo de desarrollo iterativo por US
- Build optimizado por defecto (tree-shaking, code splitting por ruta)
- TypeScript strict desde el arranque, alineado con mypy en el backend
- Alternativa descartada: Create React App (abandonado), Next.js (SSR innecesario para PWA offline-first)

**Estructura generada:**
```
frontend/
├── src/
│   ├── components/   ← componentes compartidos (NavBar, KpiCard, etc.)
│   ├── pages/        ← una carpeta por rol (juez/, organizador/, atleta/)
│   ├── hooks/        ← useConnection, useGrilla, useCompetencia
│   ├── stores/       ← estado global (Zustand)
│   ├── api/          ← clients HTTP por BC
│   └── main.tsx
├── public/
│   └── manifest.json ← PWA
├── vite.config.ts
└── index.html
```

---

### D-02 — Routing: React Router v6

**Decisión:** React Router DOM v6 con `createBrowserRouter`.

**Rutas planificadas:**

| Ruta | Componente | Rol |
|------|-----------|-----|
| `/juez` | `JuezLayout` | Juez |
| `/juez/disciplinas` | `MisDisciplinas` | Juez |
| `/juez/grilla` | `GrillaJuez` | Juez |
| `/juez/performance/:id` | `PasosPerformance` | Juez |
| `/organizador` | `OrgLayout` | Organizador |
| `/organizador/dashboard` | `Dashboard` | Organizador |
| `/organizador/grilla` | `GrillaOrganizador` | Organizador |
| `/organizador/resultados` | `Resultados` | Organizador |
| `/organizador/jueces` | `Jueces` | Organizador |
| `/organizador/torneo` | `GestionTorneo` | Organizador |
| `/organizador/audit` | `AuditLog` | Organizador |
| `/` | redirect según rol | — |

**Guards de ruta:** HOC `<RequireRole role="juez|organizador">` que lee el JWT y redirige a `/login` si no autenticado o rol incorrecto.

---

### D-03 — Estado global: Zustand

**Decisión:** Zustand para estado global de sesión y competencia activa.

**Justificación:**
- API mínima (sin boilerplate Redux)
- Compatible con React Query para datos del servidor
- Persistencia sencilla con `zustand/middleware` (persist)
- Alternativa descartada: Redux Toolkit (overhead innecesario para esta escala), Context API (re-renders)

**Stores planificados:**

| Store | Responsabilidad |
|-------|----------------|
| `useAuthStore` | JWT, rol activo, usuario |
| `useConnectionStore` | estado online/offline, cola de sync |
| `useCompetenciaStore` | disciplina activa, atleta siguiente, alertas |

---

### D-04 — Fetching y cache: TanStack Query (React Query v5)

**Decisión:** TanStack Query para fetching, cache, y mutaciones.

**Justificación:**
- Stale-while-revalidate automático (crítico para grilla en tiempo real)
- Mutations con rollback optimista para el juez (registrar resultado aunque offline)
- `queryClient.invalidateQueries` al recibir eventos SSE del organizador
- Alternativa descartada: SWR (menos features para mutaciones complejas), fetch manual (sin cache)

**Endpoints de ejemplo:**

```typescript
// Grilla del juez
useQuery({ queryKey: ['grilla', disciplinaId], queryFn: fetchGrilla })

// Registrar resultado (mutación)
useMutation({ mutationFn: registrarResultado, onSuccess: () => invalidateQueries(['grilla']) })
```

---

### D-05 — Componentes UI: shadcn/ui + Tailwind CSS

**Decisión:** shadcn/ui sobre Tailwind CSS, con los tokens de color de los prototipos como CSS variables.

**Justificación:**
- shadcn/ui genera componentes accesibles (Radix UI bajo el capó) directamente en el proyecto — sin dependencia de una librería externa
- Tailwind permite replicar exactamente el sistema de tokens del prototipo (`bg-slate-900`, `sky-400`, etc.)
- Alternativa descartada: MUI (theme override costoso), Chakra (bundle pesado), CSS Modules puro (sin componentes accesibles)

**Mapeo tokens → Tailwind:**

| Token prototipo | Variable CSS | Clase Tailwind aprox. |
|----------------|-------------|----------------------|
| `--bg` #0f172a | `--color-bg` | `bg-slate-950` |
| `--surface` #1e293b | `--color-surface` | `bg-slate-800` |
| `--accent` #38bdf8 | `--color-accent` | `text-sky-400` |
| `--blanca` #22c55e | `--color-blanca` | `text-green-500` |
| `--amarilla` #eab308 | `--color-amarilla` | `text-yellow-500` |
| `--roja` #ef4444 | `--color-roja` | `text-red-500` |

**Tailwind config:** extender `theme.colors` con los tokens exactos para evitar aproximaciones.

---

### D-06 — PWA: vite-plugin-pwa

**Decisión:** `vite-plugin-pwa` con Workbox para service worker y manifest.

**Configuración clave:**

```typescript
// vite.config.ts
VitePWA({
  registerType: 'autoUpdate',
  workbox: {
    globPatterns: ['**/*.{js,css,html,ico,png,svg}'],
    runtimeCaching: [{
      urlPattern: /^https:\/\/.*\/api\//,
      handler: 'NetworkFirst',
      options: { cacheName: 'api-cache', networkTimeoutSeconds: 3 }
    }]
  },
  manifest: {
    name: 'AtaraxiaDive',
    short_name: 'AtaraxiaDive',
    theme_color: '#0f172a',
    display: 'standalone',
    orientation: 'portrait'   // juez siempre portrait
  }
})
```

**Estrategia de cache:**
- Assets estáticos: CacheFirst (versión de build)
- Llamadas API: NetworkFirst con fallback a cache (timeout 3 s)
- Escrituras (POST/PATCH): encolar si offline, sync al reconectar (ver D-07)

---

### D-07 — Persistencia offline: Dexie.js

**Decisión:** Dexie.js (wrapper sobre IndexedDB) para la cola de sincronización offline.

**Justificación:**
- API promesa + TypeScript nativo
- El juez puede operar completamente offline; los resultados se sincronizan al reconectar
- Alternativa descartada: localStorage (síncrono, limitado a 5 MB), PouchDB (overhead CouchDB)

**Esquema mínimo:**

```typescript
class AtaraxiaDiveDB extends Dexie {
  pendingCommands!: Table<PendingCommand>

  constructor() {
    super('ataraxiadive')
    this.version(1).stores({
      pendingCommands: '++id, type, competenciaId, atletaId, createdAt'
    })
  }
}

interface PendingCommand {
  id?: number
  type: 'registrar_resultado' | 'asignar_tarjeta' | 'registrar_dns'
  payload: Record<string, unknown>
  competenciaId: string
  atletaId: string
  createdAt: number
}
```

**Hook `useOfflineSync`:** al detectar reconexión (`navigator.onLine` + event `online`), drena la cola en orden FIFO vía la API del BC Competencia.

---

### D-08 — Comunicación en tiempo real: Server-Sent Events (SSE)

**Decisión:** SSE desde el backend FastAPI para notificaciones en tiempo real al organizador.

**Justificación:**
- Unidireccional servidor → cliente: suficiente para actualizar la grilla y alertas
- Sin overhead de WebSocket (handshake, bidireccionalidad, librería cliente)
- FastAPI soporta SSE nativo con `StreamingResponse`
- El juez no necesita SSE (opera en modo "push → API")

**Endpoint planificado:**

```
GET /api/competencia/{id}/eventos
Content-Type: text/event-stream
```

**Eventos emitidos:**

| Evento | Payload | Receptor |
|--------|---------|---------|
| `resultado_registrado` | `{atletaId, rp, tarjeta}` | Organizador |
| `amarilla_pendiente` | `{atletaId, rp, motivo}` | Organizador |
| `amarilla_resuelta` | `{atletaId, decision, rpFinal}` | Organizador |
| `atleta_dns` | `{atletaId}` | Organizador |

**Hook `useCompetenciaStream`:** abre EventSource, escucha eventos, invalida queries de React Query correspondientes.

---

## Resumen de dependencias

```json
{
  "dependencies": {
    "react": "^18",
    "react-dom": "^18",
    "react-router-dom": "^6",
    "@tanstack/react-query": "^5",
    "zustand": "^4",
    "dexie": "^3",
    "dexie-react-hooks": "^1"
  },
  "devDependencies": {
    "typescript": "^5",
    "vite": "^5",
    "vite-plugin-pwa": "^0.20",
    "tailwindcss": "^3",
    "autoprefixer": "^10",
    "@types/react": "^18"
  }
}
```

**shadcn/ui:** se instala componente a componente con `npx shadcn-ui@latest add <component>` — no es una dependencia de package.json sino código generado.

---

## Criterio de inicio de INC-4.2

INC-4.2 puede iniciarse cuando:

- [x] `wireframes-juez.md` aprobado
- [x] `wireframes-organizador.md` aprobado
- [x] `wireframes-atleta.md` aprobado
- [x] `wireframes-registro-roles.md` aprobado
- [x] `wireframes-setup-torneo.md` aprobado
- [x] `decisiones-frontend.md` aprobado (este documento)
- [ ] INC-4.1 completado (correcciones de dominio CMAS/FAAS — backend)
- [ ] Branch `feature/inc-4.2-frontend-setup` creada desde `develop`
- [ ] Scaffold Vite ejecutado y estructura de carpetas verificada
- [ ] Primera US-IEDD de SP4 especificada en `docs/specs/sp4/`

---

*Artefacto generado: 2026-04-05 — INC-4.0 UX Design*
*Capa IEDD: 3 — Especificación técnica de soporte para implementación*
