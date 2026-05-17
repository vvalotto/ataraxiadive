# US-7.1.1 — Dockerfile + FastAPI estáticos + fly.toml + entorno

> Estado: ⏳ En curso — interrumpida en Fase 3 (implementación parcial)
> Branch: `feature/US-7.1.1-dockerfile-flytom-estaticos`
> Última actualización: 2026-05-17

---

## Descripción

Configurar el entorno de despliegue para Fly.io: imagen Docker multi-stage,
FastAPI sirviendo el frontend compilado como archivos estáticos, configuración
de Fly.io y template de variables de entorno de producción.
Incluye diagrama de despliegue en Mermaid como documento de arquitectura.

---

## Plan de Implementación

| # | Artefacto | Estado | Descripción |
|---|-----------|:------:|-------------|
| 1 | `requirements.txt` | ✅ | Deps producción (espejo de pyproject.toml main) |
| 2 | `Dockerfile` | ✅ | Multi-stage: node (build frontend) + python (runtime) |
| 3 | `.dockerignore` | ⬜ | Excluir dev files del contexto Docker |
| 4 | `fly.toml` | ⬜ | Configuración Fly.io (región gru, volumen data/) |
| 5 | `.env.production.example` | ⬜ | Template de vars de entorno para producción |
| 6 | `.gitignore` | ⬜ | Añadir excepción para `.env.production.example` |
| 7 | `src/app.py` | ⬜ | Mount `StaticFiles` al final para servir `frontend/dist` |
| 8 | `docs/architecture/60-deployment-view.md` | ⬜ | Diagrama Mermaid de despliegue en Fly.io |
| 9 | `docs/adr/ADR-021-fly-io.md` | ⬜ | Supersede ADR-010 (Cloud Run → Fly.io) |
| 10 | `docs/architecture/STATUS.md` | ⬜ | Añadir 60-deployment-view.md |
| 11 | `docs/architecture/README.md` | ⬜ | Añadir a la estructura |

---

## Decisiones técnicas clave

- **PYTHONPATH=/app/src** — necesario para que los imports de dominio (`from competencia.xxx import ...`) funcionen dentro del contenedor. El frontend usa URLs relativas (sin `VITE_API_URL`) en producción.
- **Un solo contenedor** — FastAPI sirve API + frontend estáticos. Sin proxy inverso adicional.
- **Volumen Fly.io en `/app/data`** — los 6 SQLite persisten entre deploys. Sin Litestream.
- **StaticFiles con `html=True`** — FastAPI monta `frontend/dist` al final, después de todos los routers de API. El flag `html=True` sirve `index.html` para rutas de React Router no encontradas en los estáticos.
- **Región `gru`** (São Paulo) — más cercana a Argentina.
- **ADR-021 supersede ADR-010** — se cambia Cloud Run + Litestream por Fly.io + volumen persistente.

---

## Contexto de la interrupción

- `requirements.txt` y `Dockerfile` creados y presentes en el branch.
- Retomar desde ítem 3 (`.dockerignore`).

---

## Fases del proceso IEDD

| Fase | Estado | Nota |
|------|:------:|------|
| 0 — Validación de Contexto | ✅ | |
| 1 — BDD | — | No aplica — US de infraestructura |
| 2 — Plan | ✅ | |
| 3 — Implementación | ⏳ | Interrumpida en ítem 3 |
| 4 — Tests unitarios | — | No aplica |
| 5 — Tests integración | — | No aplica |
| 6 — Validación BDD | — | No aplica |
| 7 — Quality gates | ⬜ | Verificación `docker build` |
| 8 — Documentación | ⬜ | Incluida en ítem 8-11 |
| 9 — Reporte final | ⬜ | |
