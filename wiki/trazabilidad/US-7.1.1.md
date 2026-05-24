---
title: "US-7.1.1 — Dockerfile + FastAPI estáticos + fly.toml + entorno producción"
type: trazabilidad-us
sp: SP7
inc: INC-7.1
bc: infraestructura
estado: cerrada
fecha_cierre: "2026-05-17"
last_updated: "2026-05-21"
sources:
  - docs/plans/sp7/US-7.1.1-plan.md
  - docs/adr/ADR-021-fly-io.md
  - docs/architecture/60-deployment-view.md
us_id: US-7.1.1
tests_count: null
rf: []
---

# US-7.1.1 — Dockerfile + FastAPI estáticos + fly.toml + entorno producción

## Descripción

Configura el entorno de despliegue para Fly.io. Imagen Docker multi-stage (node:20-alpine para build del frontend + python:3.11-slim para runtime), FastAPI sirviendo el frontend compilado como estáticos, configuración de Fly.io y template de variables de entorno de producción. Incluye diagrama de despliegue Mermaid y ADR-021 que supersede ADR-010.

## Contenido implementado

- `Dockerfile` — multi-stage: node build frontend → python runtime; `PYTHONPATH=/app/src`
- `requirements.txt` — dependencias de producción (sin dev extras)
- `.dockerignore` — excluye tests, docs, data/ y cache
- `fly.toml` — región `gru` (São Paulo), volumen `/app/data`, scale-to-zero, 512 MB
- `.env.production.example` — template con `JWT_SECRET` (obligatorio) y `RESEND_API_KEY` (opcional)
- `src/app.py` — `StaticFiles` montado en `frontend/dist` con `html=True` (sirve `index.html` para rutas React Router)
- `docs/architecture/60-deployment-view.md` — diagrama Mermaid de la arquitectura de despliegue en Fly.io
- `docs/adr/ADR-021-fly-io.md` — decisión Fly.io + volumen persistente; supersede ADR-010 (Cloud Run + Litestream)

## Decisiones técnicas clave

- **Un contenedor único** — FastAPI sirve API (`/api/*`) + frontend estáticos (`/`), sin proxy inverso
- **Volumen Fly.io en `/app/data`** — los 6 SQLite (uno por BC) persisten entre deploys sin Litestream
- **Frontend con URLs relativas** — `VITE_API_URL` no se usa en producción; mismo origen
- **Región `gru`** — São Paulo, más cercana a Argentina

## Estado

✅ Completado — 2026-05-17 · PR #194
