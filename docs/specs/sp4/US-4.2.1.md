# US-4.2.1: Scaffold Vite + React + PWA — fundación del frontend

**Estado**: `To Do`
**Sprint**: SP4 — La Plataforma
**Incremento**: INC-4.2
**Bounded Context**: `frontend` (nuevo)
**Capas afectadas**: `frontend/` (creación desde cero)

---

## Descripción

Como **equipo de desarrollo**,
quiero **una aplicación React PWA instalada y conectada al backend existente**
para **habilitar la implementación progresiva de todas las interfaces de usuario
de SP4 sobre una base arquitectónica sólida y verificable**.

---

## Contexto del dominio

> US técnica de infraestructura. No involucra aggregates DDD de negocio.
> El "sistema" es la aplicación frontend en sí misma.

### Modelo involucrado

| Elemento | Nombre | Responsabilidad |
|---|---|---|
| Estructura | `frontend/src/` | Organización por rol (pages/) y por tipo (hooks/, stores/, api/, components/) |
| Store (Zustand) | `useConnectionStore` | Estado online/offline del navegador |
| API client | `api/health.ts` | Llamada a `GET /health` del backend |
| Componente | `HealthCheck` | Indicador visual del estado del servidor |
| Config | `vite.config.ts` | Bundler, PWA y proxy al backend |

### Lenguaje ubicuo relevante

- **PWA:** Progressive Web App — la app se instala en el celular del juez y puede
  funcionar sin conexión a internet.
- **Service Worker:** script que el navegador ejecuta en segundo plano; habilita
  cache offline y sincronización en Background.
- **Manifest:** archivo JSON que define nombre, icono y modo de pantalla de la PWA.
- **Health check:** verificación de que el servidor backend está vivo y respondiendo.

---

## Especificación del comportamiento

### Invariantes de la fundación frontend

- **INV-FE-01:** La estructura de `frontend/src/` sigue exactamente el diseño de D-01
  (`pages/juez/`, `pages/organizador/`, `pages/atleta/`, `hooks/`, `stores/`, `api/`, `components/`).
- **INV-FE-02:** TypeScript strict mode activado — `"strict": true` en `tsconfig.json`.
  `npm run build` no produce errores de tipo.
- **INV-FE-03:** La URL del backend es configurable por variable de entorno
  (`VITE_API_URL`). El valor por defecto para desarrollo es `http://localhost:8000`.
- **INV-FE-04:** El manifest PWA define `orientation: "portrait"` y `display: "standalone"`.
- **INV-FE-05:** `npm run build` genera un bundle válido sin errores.
- **INV-FE-06:** El service worker usa estrategia `NetworkFirst` con timeout 3 s para
  rutas `/api/**`. Sin backend, el fallback es la respuesta cacheada más reciente.

### Operación principal

**Nombre**: `scaffold()`  ← acción de creación del proyecto frontend

| | Descripción |
|---|---|
| **Precondición** | El directorio `frontend/` no existe. Node.js ≥ 18 y npm disponibles. Backend corriendo en `VITE_API_URL`. |
| **Postcondición** | `frontend/` existe con la estructura D-01. `npm run dev` levanta la app en `localhost:5173`. El componente `HealthCheck` llama a `GET /health` y muestra estado verde (backend vivo) o rojo (backend inaccesible). |
| **Eventos generados** | N/A — US de infraestructura, sin domain events. |
| **Excepciones** | Build falla si TypeScript strict detecta errores. |

**Ejemplo concreto:**

```
Precondición:  frontend/ no existe. Backend corriendo en localhost:8000.
Operación:     npm run dev
Postcondición: App en localhost:5173. HealthCheck muestra "Backend: ✓ online".
               GET /health respondió {"status": "ok"}.

Precondición:  frontend/ existe. Backend apagado.
Operación:     npm run dev
Postcondición: App en localhost:5173. HealthCheck muestra "Backend: ✗ sin conexión".
```

---

## Criterios de aceptación

> US técnica de infraestructura — sin escenarios BDD. Los criterios son
> verificaciones técnicas que se comprueban manualmente al cerrar la US.

- [ ] `npm run dev` levanta la app en `localhost:5173` sin errores en consola
- [ ] `npm run build` termina con código 0 sin errores de TypeScript
- [ ] El componente `HealthCheck` muestra indicador verde con el backend corriendo
- [ ] El componente `HealthCheck` muestra indicador rojo con el backend apagado
- [ ] El manifest PWA es válido: `display: standalone`, `orientation: portrait`
- [ ] La app aparece como instalable en Chrome/Safari mobile
- [ ] La estructura de `frontend/src/` respeta D-01 (pages/, hooks/, stores/, api/, components/)
- [ ] `tsconfig.json` tiene `"strict": true`
- [ ] `VITE_API_URL` en `.env.example` con valor por defecto `http://localhost:8000`

---

## Impacto arquitectónico

**¿Esta US requiere una decisión arquitectónica?**
- [x] No — las decisiones están formalizadas en `docs/design/ux/decisiones-frontend.md`
  (D-01 a D-06) y en ADR-003.

**Capa(s) afectadas:**
- [x] Infrastructure / Frontend — creación del proyecto Vite + React + TypeScript
- [ ] Domain — no aplica
- [ ] Application — no aplica

---

## Referencias

- Decisiones de stack: `docs/design/ux/decisiones-frontend.md` §D-01, §D-06
- ADR-003: React PWA
- Plan SP4: `docs/plans/sp4/PLAN-SP4.md §INC-4.2`
- Backend health endpoint: `GET /health` → `{"status": "ok"}`

---

## Notas de implementación

- Comando de scaffold: `npm create vite@latest frontend -- --template react-ts`
- Luego instalar dependencias en orden: Tailwind + PostCSS, shadcn/ui init,
  vite-plugin-pwa, React Router DOM v6, Zustand, TanStack Query.
- El proxy del backend va en `vite.config.ts`:
  ```ts
  server: { proxy: { '/api': { target: process.env.VITE_API_URL || 'http://localhost:8000' } } }
  ```
- `HealthCheck` es un componente simple: llama a `GET /health` con un intervalo
  de 30 s usando `useQuery` (TanStack Query). Sin autenticación — es público.
- Esta US no implementa routing de negocio ni autenticación — eso es US-4.2.2.
  Solo el routing base (`/`) que muestra el HealthCheck.
- El directorio `frontend/` va en la raíz del monorepo (al mismo nivel que `src/`).
- **`--skip-bdd`:** US técnica de infraestructura — no genera feature file.
  Los criterios de aceptación se verifican manualmente (checklist en la spec).

---

*Redactado: 2026-04-09 — INC-4.2 Fundación Frontend*
