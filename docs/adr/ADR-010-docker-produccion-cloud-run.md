# ADR-010: Docker solo para producción — Cloud Run (GCP) + Litestream

> Estado documental: histórico
> Conservado como evidencia de planificación o decisión previa.
> No usar como fuente de verdad para el estado actual.
> Fuente vigente relacionada: `docs/adr/ADR-021-fly-io.md`

| Campo | Valor |
|-------|-------|
| **Estado** | Supersedida por ADR-021 |
| **Fecha** | 2026-03-20 |
| **Autores** | Victor Valotto |
| **Relacionado** | ADR-007 (SQLite por BC) |

---

## Contexto

El proyecto necesita una estrategia de entorno para dos contextos:
desarrollo local y despliegue en producción.

La restricción concreta: el desarrollador no tiene Docker Desktop instalado
en la máquina de desarrollo (limitación de espacio en disco). El stack
elegido (SQLite + FastAPI + Python) no requiere servicios de infraestructura
en desarrollo, lo que hace viable un entorno local sin Docker.

Para producción se evaluó GCP como plataforma de hosting, dado el requisito
de disponibilidad en la nube (AC-DS-01) y la escala modesta del sistema
(4 torneos/año, 50 usuarios concurrentes).

## Opciones Consideradas

**Opción A — Docker para dev y prod:**
`docker-compose.yml` para desarrollo + `Dockerfile` para producción.
Descartada: Docker Desktop no está disponible en el entorno de desarrollo.

**Opción B — Sin Docker (solo local + deploy directo):**
`uv run` local para dev, deploy directo a un servidor sin contenedor.
Menos reproducible en producción.

**Opción C — Sin Docker en dev, Docker solo para prod:**
`uv run` local para dev, `Dockerfile` → Cloud Run para producción.
Separa claramente los contextos sin imponer Docker en el entorno de desarrollo.

## Decisión

Se adopta **Opción C**: sin Docker en desarrollo, Docker solo para producción.

### Desarrollo local

```bash
# Backend
uv run fastapi dev src/app.py

# Frontend (SP4 en adelante)
cd frontend && npm run dev
```

Los archivos SQLite viven en `data/` dentro del repositorio (excluidos de git).

### Producción

```
Dockerfile  ←  imagen de producción optimizada
    ↓
Google Artifact Registry
    ↓
Cloud Run  ←  instancia stateless
    ↓
Litestream  ←  replica data/*.db → Google Cloud Storage (GCS)
```

**Litestream** resuelve la restricción de Cloud Run (filesystem stateless):
replica los archivos SQLite a un bucket GCS en tiempo real. Al arrancar
una nueva instancia, restaura los `.db` desde GCS antes de servir tráfico.

## Consecuencias

**Positivas:**
- Desarrollo sin fricción: `uv run` es suficiente, sin Docker Desktop
- Cloud Run escala a cero cuando no hay torneos — costo casi nulo
- Litestream provee backup continuo sin infraestructura adicional
- Un solo `Dockerfile` para producción, sin `docker-compose.yml`

**Negativas / trade-offs:**
- El entorno de dev y prod no son idénticos (riesgo de "funciona en mi máquina")
  — mitigado porque SQLite es el mismo motor en ambos contextos
- Litestream agrega una dependencia en el proceso de arranque de producción
- `docker-compose.yml` se agrega en SP5 si se necesita para CI/CD o staging

**Pendiente para SP5:**
- Configuración concreta de Cloud Run (región, memoria, concurrencia)
- Bucket GCS para Litestream
- Pipeline CI/CD (GitHub Actions → Artifact Registry → Cloud Run)
