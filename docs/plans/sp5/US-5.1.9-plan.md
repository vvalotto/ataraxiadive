# Plan de Implementacion - US-5.1.9 Precondicion grilla en jueces

**Sprint:** SP5
**Incremento:** INC-5.1-ADJ
**Producto:** frontend
**Tipo:** fix funcional post-UAT
**Estimacion:** 2 puntos

## Alcance

Bloquear la asignacion de jueces para disciplinas que aun no tienen competencia con
grilla generada, manteniendo visible cualquier asignacion existente.

## Tareas

### 1. Queries frontend

- [x] Reutilizar `listarDisciplinasTorneo(torneoId)`.
- [x] Agregar `fetchCompetenciasPorTorneo(torneoId)` en `JuecesPanel`.
- [x] Manejar loading/error combinado de disciplinas, jueces y competencias.

### 2. Politica de habilitacion

- [x] Definir estados de competencia con grilla generada.
- [x] Cruzar competencias por `disciplina`.
- [x] Calcular `puedeAsignarJuez` por fila.

### 3. Tabla de jueces

- [x] Pasar estado de habilitacion a `TablaJueces`.
- [x] Deshabilitar `JuezSelector` si no hay grilla.
- [x] Mostrar `Generar grilla antes de asignar juez`.
- [x] Mantener visible juez asignado existente.

### 4. Validacion

- [x] `npm run build`.
- [x] `npm run lint`.
- [x] Registrar waiver BDD/UI si no existe harness browser automatizado.
- [x] Registrar reporte final en `docs/reports/US-5.1.9-report.md`.

## DoD

- Disciplina con competencia en estado de grilla generada permite asignar juez.
- Disciplina sin competencia bloquea selector y muestra mensaje operativo.
- Asignacion existente permanece visible aunque el selector este bloqueado.
