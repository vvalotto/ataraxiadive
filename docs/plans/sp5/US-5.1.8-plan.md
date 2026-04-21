# Plan de Implementacion - US-5.1.8 Componer disciplinas y competencias

**Sprint:** SP5
**Incremento:** INC-5.1-ADJ
**Producto:** frontend
**Tipo:** fix funcional post-UAT
**Estimacion:** 2 puntos

## Alcance

Corregir `TorneoCompetenciasPage` para que use las disciplinas configuradas del
torneo como fuente primaria y las competencias existentes solo como enriquecimiento.

## Tareas

### 1. Queries frontend

- [x] Reutilizar `listarDisciplinasTorneo(torneoId)`.
- [x] Mantener `fetchCompetenciasPorTorneo(torneoId)` como fuente secundaria.
- [x] Manejar loading/error de ambas queries.

### 2. Composicion

- [x] Cruzar disciplinas y competencias por `disciplina`.
- [x] Renderizar una card por disciplina configurada.
- [x] Marcar card como `Competencia pendiente` si no existe `competencia_id`.

### 3. Acciones UI

- [x] Habilitar `Ver auditoria` solo con `competencia_id`.
- [x] Mostrar indicacion de usar el tab `Grilla` si la competencia esta pendiente.
- [x] Conservar estado vacio solo cuando el torneo no tiene disciplinas configuradas.

### 4. Validacion

- [x] `npm run build`.
- [x] `npm run lint`.
- [x] Registrar waiver BDD/UI si no existe harness browser automatizado.
- [x] Registrar reporte final en `docs/reports/US-5.1.8-report.md`.

## DoD

- En estados tempranos, `Ver competencias` muestra disciplinas configuradas aunque no existan competencias.
- `Ver auditoria` queda deshabilitado para disciplinas sin competencia materializada.
- El mensaje de pantalla vacia solo aparece si no hay disciplinas configuradas.
