---
title: "US-4.2.2 — Auth store + login + routing + guards de rol"
type: trazabilidad-us
sp: SP4
inc: INC-4.2
bc: frontend
estado: completado
fecha_cierre: "2026-04-11"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §13
---

# US-4.2.2 — Auth store + login + routing + guards de rol

## Descripción

Implementa la capa de autenticación en el frontend: store Zustand, página de login, decodificación JWT y guards de ruta por rol.

## Decisiones cubiertas

D-02 (routing + guards) · D-03 (Zustand)

## Contenido implementado

- `useAuthStore` (Zustand, sin persistencia) — estado de sesión en memoria
- `loginApi()` — `POST /auth/login`
- `decodeJwtPayload()` — decodificación via `atob()` sin librería externa
- `LoginPage` — formulario con TanStack Query mutation + error inline
- `RequireRole` HOC — guard de ruta por rol
- `BrowserRouter` con rutas: `/login`, `/juez/disciplinas`, `/organizador/dashboard`

## Tests

`npm run build` exitcode 0. UAT INC-4.2 aprobada 2026-04-11.

## Estado

✅ Completado — 2026-04-11
