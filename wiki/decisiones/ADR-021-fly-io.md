---
title: "ADR-021: Plataforma de despliegue — Fly.io + volumen persistente"
type: decision
last_updated: "2026-05-20"
sources:
  - docs/adr/ADR-021-fly-io.md
estado: Aceptada
fecha: 2026-05-17
bcs_afectados: [todos]
supersede: ADR-010-docker-cloud-run
---

# ADR-021: Plataforma de despliegue — Fly.io + volumen persistente

## Decisión

Fly.io + volumen persistente para los 6 archivos SQLite. Supersede [[ADR-010-docker-cloud-run]] (Cloud Run + Litestream).

## Por qué

Al llegar al momento concreto de desplegar (SP7), el objetivo es una **demo para el experimento IEDD**, no un sistema productivo con alta disponibilidad. El criterio dominante es simplicidad operativa y velocidad de entrega.

Cloud Run + Litestream requería: cuenta GCP con billing, Artifact Registry, bucket GCS, proceso sidecar Litestream, credenciales de servicio. Ese overhead no se justifica para la escala del experimento.

Fly.io: `fly deploy` desde el repo local. SSL y dominio `.fly.dev` automáticos. Scale-to-zero. Free tier adecuado.

## Configuración vigente

```
Dockerfile (multi-stage)
    Stage 1: node:20-alpine  →  npm run build  →  frontend/dist/
    Stage 2: python:3.11-slim  →  pip install  →  API + estáticos

fly.toml
    app: ataraxiadive
    region: gru (São Paulo)
    vm: 512 MB · 1 CPU shared
    volume: ataraxiadive_data → /app/data (6 SQLite)
    http_service: port 8000 · force_https · scale-to-zero
```

## Estrategia frontend

FastAPI monta `frontend/dist/` como `StaticFiles` al final del composition root, después de todos los routers de API. Flag `html=True` habilita routing de React Router. El frontend usa URLs relativas — sin `VITE_API_URL` en producción.

## Consecuencias vigentes

- Deploy manual con `fly deploy` — sin CI/CD automatizado.
- Sin backup externo de los SQLite: pérdida de datos si el volumen falla. Aceptable para demo; inaceptable para producción real.
- Un solo nodo — SQLite no escala horizontalmente.
- Si se requiere producción real: migrar a Cloud Run + Litestream (ADR-010) o PostgreSQL sigue siendo la ruta natural.

## ADRs relacionados

- [[ADR-010-docker-cloud-run]] — decisión anterior supersedida
- [[ADR-007-sqlite-persistencia-bc]] — los 6 archivos SQLite que este volumen aloja
