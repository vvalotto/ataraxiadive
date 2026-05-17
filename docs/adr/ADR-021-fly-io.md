# ADR-021: Plataforma de despliegue — Fly.io + volumen persistente

| Campo | Valor |
|-------|-------|
| **Estado** | Aceptada |
| **Fecha** | 2026-05-17 |
| **Autores** | Victor Valotto |
| **Supersede** | ADR-010 (Cloud Run + Litestream) |
| **Relacionado** | ADR-007 (SQLite por BC) |

---

## Contexto

ADR-010 eligió Google Cloud Run + Litestream para producción. Al llegar al
momento concreto de desplegar (SP7), el objetivo cambió: se trata de una
**demo para el experimento IEDD**, no de un sistema productivo con requisitos
de alta disponibilidad. El criterio dominante pasa a ser simplicidad operativa
y velocidad de entrega.

Cloud Run + Litestream implica:
- cuenta GCP con billing habilitado;
- Artifact Registry para la imagen Docker;
- bucket GCS para la réplica de Litestream;
- configuración de Litestream como proceso sidecar;
- gestión de credenciales de servicio GCP.

Ese overhead no se justifica para el objetivo actual.

## Opciones Consideradas

**Opción A — Mantener ADR-010 (Cloud Run + Litestream):**
Stack robusto y escalable. Demasiado overhead para una demo IEDD.

**Opción B — Railway / Render:**
Más simples en setup inicial. Soporte de SQLite multi-archivo en volúmenes
menos predecible; documentación menos clara para este caso.

**Opción C — Fly.io + volumen persistente:**
Un solo comando de deploy (`fly deploy`). Volúmenes persistentes nativos para
SQLite. SSL y dominio `.fly.dev` automáticos. Scale-to-zero sin costo en
inactividad. Free tier adecuado para la escala del experimento.

**Opción D — VPS (Hetzner / DigitalOcean):**
Control total. Requiere configuración manual de SSL (Caddy/nginx) y backup.
Más friction inicial que Fly.io.

## Decisión

Se adopta **Opción C: Fly.io + volumen persistente**.

### Configuración

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

### Estrategia de persistencia

Los 6 archivos SQLite (`data/*.db`) viven en el volumen `ataraxiadive_data`
montado en `/app/data`. El volumen sobrevive a deploys y reinicios del
contenedor. No se usa Litestream ni backup externo para la demo.

### Frontend

FastAPI monta `frontend/dist/` como `StaticFiles` al final del composition
root, después de registrar todos los routers de API. El flag `html=True`
habilita routing de React Router (sirve `index.html` para rutas desconocidas).
El frontend usa URLs relativas, sin `VITE_API_URL` en producción.

## Consecuencias

**Positivas:**
- Deploy con `fly deploy` desde el repo local, sin pipelines adicionales.
- SSL y dominio `ataraxiadive.fly.dev` sin configuración de DNS.
- Costo casi nulo (scale-to-zero cuando no hay torneos activos).
- No hay dependencia de GCP, Litestream ni bucket externo.

**Negativas / trade-offs:**
- Sin CI/CD automatizado — deploy manual (`fly deploy`).
- Sin backup externo de los SQLite — pérdida de datos si el volumen falla.
  Aceptable para demo; inaceptable para producción real.
- Fly.io volumen: un solo nodo. No escala horizontalmente (SQLite no es
  adecuado para múltiples réplicas escribiendo).
- Si en el futuro se requiere producción real, migrar a Cloud Run + Litestream
  (ADR-010) o a Postgres sigue siendo la ruta natural.
