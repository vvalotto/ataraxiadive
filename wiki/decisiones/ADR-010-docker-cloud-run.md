---
title: "ADR-010: Docker + Cloud Run + Litestream (SUPERSEDIDA)"
type: decision
last_updated: "2026-05-20"
sources:
  - docs/adr/ADR-010-docker-produccion-cloud-run.md
estado: Supersedida por ADR-021
fecha: 2026-03-20
bcs_afectados: []
---

# ADR-010: Docker + Cloud Run + Litestream ⚠️ SUPERSEDIDA

> **Esta decisión fue reemplazada por [[ADR-021-fly-io]].**
> Se conserva como evidencia histórica del razonamiento original.

## Decisión original

Sin Docker en desarrollo, Docker solo para producción en GCP Cloud Run. Litestream para replicar SQLite a Google Cloud Storage.

## Por qué fue reemplazada

Al llegar al momento concreto de desplegar (SP7), el objetivo cambió: se trata de una **demo para el experimento IEDD**, no de un sistema productivo. Cloud Run + Litestream implica demasiado overhead operativo (cuenta GCP, Artifact Registry, bucket GCS, credenciales) para ese objetivo.

## Decisión vigente

Ver [[ADR-021-fly-io]]: Fly.io con volumen persistente — un solo comando de deploy.
