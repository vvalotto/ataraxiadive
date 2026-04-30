# Smoke Test - US-5.7.1

**Fecha:** 2026-04-30  
**Branch:** `feature/US-5.7.1-mis-torneos`  
**Objetivo:** validar que la pantalla Torneos del atleta puede cargar la nueva seccion
"Mis torneos" con datos reales locales.

## Entorno

- Backend: `http://127.0.0.1:8000`
- Frontend: `http://127.0.0.1:5173`
- Atleta usado para smoke no mutativo: `vvalotto@gmail.com`

> Nota: `ana@email.com / apnea123` autentica correctamente, pero el dataset local no tiene
> `registro.atletas` asociado a ese email. Para evitar mutar la base local, se uso un token
> local generado para `vvalotto@gmail.com`, que si tiene atleta e inscripcion existente.

## Verificaciones

| Check | Resultado |
|-------|-----------|
| `GET /health` | PASS — `{"status":"ok"}` |
| `GET http://127.0.0.1:5173/atleta/torneos` | PASS — HTTP 200 |
| `GET /registro/atletas/me` | PASS — `vvalotto@gmail.com` |
| `GET /registro/atletas/{id}/inscripciones` | PASS — 1 inscripcion activa |
| Cruce `torneos ∩ inscripciones` | PASS — `PM2026`, estado `PREPARACION` |
| Chips esperados desde inscripcion | PASS — `DNF`, `DBF`, `DYN` |
| Torneos inscriptos excluidos de abiertas | PASS — no hay duplicacion en el set derivado |

## Resultado

Smoke test PASS para la carga integrada de datos de US-5.7.1.

## Riesgo residual

No se realizo verificacion visual automatizada en navegador porque el repo no tiene
Playwright/testing-library instalado. La ruta queda disponible para validacion manual:

- `http://127.0.0.1:5173/atleta/torneos`
