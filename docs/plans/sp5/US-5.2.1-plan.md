# Plan de Implementacion: US-5.2.1 — Vista maestro-detalle de disciplinas en ejecucion

**Patron:** React/Vite frontend consumiendo APIs hexagonales existentes
**Producto:** `frontend`
**Branch:** `feature/US-5.2.1-ejecucion-disciplinas`
**Estimacion total:** 3h 20min
**Estado:** 0/12 tareas completadas

---

## Objetivo Tecnico

Convertir `EjecucionPanel` de un monitor de competencias ya activas a una vista maestro-detalle
que compone disciplinas configuradas del torneo, competencias materializadas, estado de grilla,
juez asignado y progreso. Desde el detalle, el organizador puede habilitar una disciplina lista
para iniciar usando `POST /competencia/{competencia_id}/iniciar`.

---

## Componentes a Implementar

### 1. API frontend

- [ ] `frontend/src/api/competencia.ts` — agregar `iniciarCompetencia()` (10 min)
  - Payload: `{ competenciaId, disciplina, juezId }`
  - Endpoint: `POST /competencia/{competencia_id}/iniciar`
  - Body: `{ disciplina, juez_id }`
  - Reutilizar `buildHeaders()` y `parseResponse<void>()`

### 2. Modelo de vista local para ejecucion

- [ ] `frontend/src/components/organizador/EjecucionPanel.tsx` — definir tipos internos (20 min)
  - `DisciplinaEjecucionItem`
  - `EstadoOperativoDisciplina`
  - `DetalleDisciplinaData`
  - Evitar exponer estos tipos fuera del componente salvo necesidad real.

- [ ] Implementar helpers de estado operativo (25 min)
  - Derivar estados: `sin_competencia`, `sin_grilla`, `sin_juez`, `lista_para_iniciar`, `en_ejecucion`, `finalizada`.
  - Reutilizar la regla `estado.grilla_confirmada`.
  - Considerar estados backend actuales: `Preparacion`, `Confirmada`, `EnEjecucion`, `Finalizada`.

### 3. Carga compuesta maestro-detalle

- [ ] Reemplazar `loadMonitorData()` por `loadEjecucionData()` (35 min)
  - `listarDisciplinasTorneo(torneoId)` como fuente primaria.
  - `fetchCompetenciasPorTorneo(torneoId)` como enrichment opcional.
  - Para cada competencia, cargar `fetchEstadoCompetencia()` y `fetchProgresoCompetencia()`.
  - El maestro debe renderizar disciplinas aunque no tengan competencia.

- [ ] Implementar carga de detalle para disciplina seleccionada (25 min)
  - Si no hay `competencia_id`, no llamar endpoints de competencia.
  - Si hay competencia, cargar grilla, performance actual, proximas y progreso.
  - Mantener refetch cada 30s para datos vivos.

### 4. UI maestro

- [ ] Construir lista/card maestro por disciplina (35 min)
  - Mostrar disciplina, juez asignado o bloqueo, estado operativo y progreso resumido.
  - Permitir seleccionar disciplina.
  - Seleccionar por defecto la primera disciplina disponible.
  - Mantener layout estable en mobile/desktop.

- [ ] Estados vacio/error/cargando (15 min)
  - Sin disciplinas configuradas.
  - Error al cargar disciplinas/competencias.
  - Loading inicial.

### 5. UI detalle operativo

- [ ] Adaptar/reutilizar `MonitorDisciplina` para detalle seleccionado (35 min)
  - Mostrar grilla, progreso, atleta actual y proximos.
  - Mostrar estado `Finalizada` con hash si existe.
  - Mostrar bloqueos cuando falte competencia, grilla o juez.

- [ ] Agregar accion `Habilitar disciplina` (25 min)
  - Habilitada solo con competencia, grilla confirmada, juez asignado y estado `Confirmada`.
  - Mutacion llama `iniciarCompetencia()`.
  - En success, invalidar queries de ejecucion y recargar detalle.
  - Mostrar error inline si backend devuelve 409/404.

### 6. Tests

- [ ] Tests unitarios frontend para helpers de estado operativo si se extraen a modulo testeable (20 min)
  - Si los helpers quedan internos al componente, cubrir mediante build/lint y BDD manual.

- [ ] Validacion BDD/manual de escenarios `US-5.2.1-ejecucion-disciplinas.feature` (20 min)
  - Maestro con todas las disciplinas.
  - Detalle operativo.
  - Habilitacion exitosa.
  - Bloqueos por falta de juez/grilla.
  - Finalizada en modo lectura.

### 7. Quality gates

- [ ] `npm run build` en `frontend/` (10 min)
- [ ] `npm run lint` en `frontend/` si no hay deuda previa bloqueante (10 min)
- [ ] Registrar resultado en reporte final (10 min)

---

## Dependencias y Restricciones

- Backend no cambia en esta US.
- `POST /competencia/{competencia_id}/iniciar` ya existe.
- `listarDisciplinasTorneo()` devuelve `disciplina` y `juez_id`; es la fuente para asignacion de juez.
- `fetchCompetenciasPorTorneo()` puede devolver menos filas que disciplinas configuradas.
- No implementar cierre manual en esta US; reservar accion/espacio para US-5.2.2 si el diseño lo permite sin acoplar.

---

## Riesgos y Mitigaciones

- **Riesgo:** duplicar logica de composicion usada en `JuecesPanel`.
  - **Mitigacion:** reutilizar patrones simples, pero no extraer abstraccion compartida hasta ver duplicacion estable.

- **Riesgo:** estado operativo incorrecto por mismatch de strings backend.
  - **Mitigacion:** centralizar sets de estado en helpers locales y cubrir casos actuales (`Confirmada`, `EnEjecucion`, `Finalizada`).

- **Riesgo:** UI demasiado densa en mobile.
  - **Mitigacion:** maestro en columna, detalle debajo; evitar tablas anchas para el maestro.

---

## Orden de Ejecucion

1. Agregar wrapper `iniciarCompetencia()`.
2. Reescribir carga compuesta de `EjecucionPanel`.
3. Implementar maestro y seleccion.
4. Implementar detalle y accion de habilitacion.
5. Ajustar estados visuales y mensajes de bloqueo.
6. Ejecutar build/lint.
7. Documentar resultados.
