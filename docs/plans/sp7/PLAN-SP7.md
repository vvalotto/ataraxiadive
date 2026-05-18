# PLAN-SP7 — Despliegue y Documentación

> Estado documental: vigente
> Última actualización: 2026-05-17
> Baseline objetivo: `v1.0.1` (BL-007)

---

## 1. Contexto y Objetivos

SP7 es el subproyecto final de AtaraxiaDive. Sus dos ejes son:

1. **Despliegue** — publicar la aplicación en Fly.io, accesible vía URL pública con SSL
2. **Manual de usuario** — documentar los flujos principales para los tres roles

SP7 parte de `v1.0.0` taggeado en `main` (BL-006, 2026-05-16). No incluye nuevas funcionalidades.

---

## 2. Estructura

```
SP7
├── INC-7.1  Despliegue en Fly.io
└── INC-7.2  Manual de usuario
```

---

## 3. Incrementos

### INC-7.1 — Despliegue en Fly.io

**Decisiones de arquitectura:**
- Plataforma: Fly.io (volúmenes persistentes para SQLite multi-BC, SSL automático)
- Contenedor único: FastAPI sirve la API en `/api/*` y el frontend compilado como estáticos en `/`
- Persistencia: volumen Fly.io montado en `/app/data` (6 archivos `.db`)
- Variables de entorno: `JWT_SECRET` (obligatorio) · `RESEND_API_KEY` (opcional — fallback a log)
- Frontend: `VITE_API_URL` apunta a la misma URL de Fly.io (mismo origen)

**DoD:** URL pública accesible con SSL · login funcional · flujo organizador → juez → atleta verificado.

| US | Descripción |
|----|-------------|
| US-7.1.1 | Dockerfile + FastAPI sirve `frontend/dist` como estáticos + `fly.toml` + `.env.production` |
| US-7.1.2 | `fly deploy` + verificación de flujos críticos (login, crear torneo, grilla) + tag `v1.0.1` |

### INC-7.2 — Manual de Usuario

**Estructura de salida:** `docs/manual/`

**DoD:** tres documentos Markdown con capturas de pantalla de los flujos verificados en UAT SP6;
índice general en `docs/manual/README.md`.

| US | Descripción |
|----|-------------|
| US-7.2.1 | Manual organizador — crear torneo · inscripciones · grilla · ejecución · cierre y podios |
| US-7.2.2 | Manual juez — acceso al panel · flujo de performance (6 pasos) · tarjetas blanca/roja/amarilla |
| US-7.2.3 | Manual atleta — registro · inscripción · declarar AP · consulta de resultados |

---

## 4. Criterio de Cierre SP7 (BL-007 / v1.0.1)

- [ ] INC-7.1: URL pública Fly.io accesible con SSL
- [ ] INC-7.1: login de los tres roles funcional en producción
- [ ] INC-7.1: flujo organizador → juez → atleta verificado end-to-end en producción
- [ ] INC-7.2: `docs/manual/README.md` + 3 manuales por rol completos
- [ ] `v1.0.1` tageado en `main` · BL-007 registrado

---

## 5. Fuera de Scope SP7

| Ítem | Motivo |
|------|--------|
| CI/CD pipeline (GitHub Actions) | Overhead no justificado para demo IEDD |
| Litestream / backup continuo | Volumen Fly.io suficiente para demo |
| Dominio personalizado | Se usa dominio `.fly.dev` gratuito |
| Nuevas funcionalidades | SP7 es solo despliegue y documentación |
