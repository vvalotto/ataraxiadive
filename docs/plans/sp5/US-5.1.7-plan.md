# Plan de Implementacion - US-5.1.7 Politica de tabs por fase

**Sprint:** SP5
**Incremento:** INC-5.1-ADJ
**Producto:** frontend
**Tipo:** fix funcional post-UAT
**Estimacion:** 2 puntos

## Alcance

Corregir `DetalleTorneoPage` para que las tabs del panel organizador respeten el
estado real del torneo y para que `CANCELADO` se muestre como estado terminal sin
paneles operativos.

## Tareas

### 1. Politica de tabs

- [x] Tipar `TabTorneo` a partir de `TABS`.
- [x] Definir `TABS_POR_ESTADO: Record<EstadoTorneo, readonly TabTorneo[]>`.
- [x] Calcular si cada tab esta habilitada antes de permitir click.

### 2. Reset de activeTab

- [x] Encapsular tabs en panel operativo con `key={estado}`.
- [x] Resetear a `Detalle` cuando cambia el estado del torneo.

### 3. Estado CANCELADO

- [x] Reemplazar tabs y paneles por resumen basico de cancelacion.
- [x] Evitar render de paneles hijos operativos.
- [x] Evitar mostrar `Ver competencias` para torneo cancelado.
- [x] Mantener `AccionesPanel` fuera de la vista cancelada.

### 4. Validacion

- [x] `npm run build`.
- [x] `npm run lint`.
- [x] Registrar waiver BDD/UI si no existe harness browser automatizado.
- [x] Registrar reporte final en `docs/reports/US-5.1.7-report.md`.

## DoD

- En `INSCRIPCION_ABIERTA`, solo `Detalle` e `Inscriptos` son clickeables.
- En `PREPARACION`, `Ejecucion` permanece visible pero deshabilitada.
- En `CANCELADO`, no se renderizan `InscriptosPanel`, `GrillaPanel`, `JuecesPanel` ni `EjecucionPanel`.
- `activeTab` nunca conserva una tab incompatible tras recargar el torneo.
