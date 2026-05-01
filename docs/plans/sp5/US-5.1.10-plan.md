# Plan de Implementacion - US-5.1.10 Acciones correctas de fase

**Sprint:** SP5
**Incremento:** INC-5.1-ADJ
**Producto:** frontend
**Tipo:** fix funcional post-UAT
**Estimacion:** 2 puntos

## Alcance

Garantizar que `AccionesPanel` reciba estados de torneo canonicos y por eso muestre
acciones correctas para `PREPARACION`, `EJECUCION`, `PREMIACION` y estados terminales.

## Tareas

### 1. Normalizacion de estado

- [x] Agregar normalizacion runtime de `estado` en `frontend/src/api/torneo.ts`.
- [x] Aplicar normalizacion a `fetchTorneo`.
- [x] Aplicar normalizacion a `fetchTorneos`.

### 2. AccionesPanel

- [x] Mantener `ACCIONES_POR_ESTADO` con claves canonicas.
- [x] Evitar fallback silencioso para strings no canonicos.
- [x] Verificar que `EJECUCION` muestra `Iniciar premiacion` y no `Iniciar ejecucion`.

### 3. Validacion

- [x] `npm run build`.
- [x] `npm run lint`.
- [x] Registrar waiver BDD/UI si no existe harness browser automatizado.
- [x] Registrar reporte final en `docs/reports/US-5.1.10-report.md`.

## DoD

- `fetchTorneo` y `fetchTorneos` retornan `EstadoTorneo` canonico.
- `AccionesPanel` con `EJECUCION` muestra `Volver a preparacion` e `Iniciar premiacion`.
- `AccionesPanel` con `PREPARACION` muestra solo `Iniciar ejecucion`.
