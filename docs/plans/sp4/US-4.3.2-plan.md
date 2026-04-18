# Plan de Implementación: US-4.3.2 — Flujo de performance

**Patrón:** Full-stack React + FastAPI
**Producto:** frontend + competencia
**Estimación Total:** 4h 30min
**BDD:** validación manual UI sobre `tests/features/US-4.3.2-flujo-performance.feature`

> **Ajuste al código real del repo:** la spec usa nombres de campos y contratos
> algo distintos de los commands existentes. El plan toma como fuente de verdad
> los handlers reales en `src/competencia/application/commands/`.

---

## Componentes a Implementar

### 1. Backend API — endpoints del juez (55 min)

- [ ] `src/competencia/api/router.py` (35 min)
  - `POST /competencia/{competencia_id}/llamar`
  - `POST /competencia/{competencia_id}/registrar-resultado`
  - `POST /competencia/{competencia_id}/asignar-tarjeta`
  - usar `JuezDep`
  - extraer `sub` / `email` desde JWT para `juez_id` y `registrado_por`
- [ ] schemas HTTP del router (20 min)
  - body para llamar
  - body para registrar resultado
  - body para asignar tarjeta
  - mapping correcto a `TipoTarjeta`, `UnidadMedida` y `MotivoDQ? = None`

### 2. Frontend API clients (25 min)

- [ ] `frontend/src/api/competencia.ts` (25 min)
  - `fetchGrilla(competenciaId, disciplina)`
  - `fetchPerformanceActual(competenciaId)`
  - `callAtleta(...)`
  - `registrarResultado(...)`
  - `asignarTarjeta(...)`

### 3. Store de competencia y navegación interna (20 min)

- [ ] `frontend/src/stores/useCompetenciaStore.ts` (20 min)
  - agregar `atletaActivo`
  - agregar `setAtletaActivo` / `limpiarAtletaActivo`

### 4. Grilla del juez real (45 min)

- [ ] `frontend/src/pages/juez/GrillaPage.tsx` (45 min)
  - reemplazar stub por vista S-02
  - cargar grilla desde backend
  - combinar con `performance actual` para destacar SIGUIENTE / EN CURSO
  - tap en fila disponible abre wizard de pasos

### 5. Componentes de flujo (75 min)

- [ ] `frontend/src/components/juez/StepIndicator.tsx` (10 min)
- [ ] `frontend/src/components/juez/AtletaCard.tsx` (10 min)
- [ ] `frontend/src/components/juez/RpSelector.tsx` (20 min)
- [ ] `frontend/src/pages/juez/PerformanceFlowPage.tsx` (35 min)
  - pasos 1 a 6
  - paso 2 y 3 con estado local
  - cronómetro local simple en paso 4

### 6. Routing e integración (15 min)

- [ ] `frontend/src/App.tsx` (15 min)
  - ruta protegida `/juez/performance`

### 7. Validación técnica (25 min)

- [ ] tests focalizados backend de router / handlers impactados (15 min)
- [ ] `frontend`: `npm run build` (5 min)
- [ ] `frontend`: `npm run lint` (5 min)

### 8. Validación manual UI (30 min)

- [ ] flujo feliz completo hasta tarjeta blanca
- [ ] botón de confirmar marca deshabilitado sin RP
- [ ] error backend 409 visible inline
- [ ] regreso a grilla luego de completar performance

---

## Decisiones de implementación

1. **No introducir ACL con Registro en esta US.**
   La UI puede operar con nombres sintéticos ya proyectados por `competencia`
   (`Atleta-xxxxxxxx`) para no abrir scope nuevo cross-BC.

2. **Paso 2 y Paso 3 son local-first.**
   Confirmar presencia, OT y cronómetro se resuelven en frontend.
   Los POST reales ocurren en:
   - Paso 1: llamar atleta
   - Paso 5: registrar resultado
   - Paso 6: asignar tarjeta

3. **La grilla visible se arma con datos actuales disponibles.**
   - `GET /competencia/{id}/grilla`
   - `GET /competencia/{id}/performance/actual`
   - si hace falta enriquecer estado visible, se evaluará extender query o
     derivarlo en frontend con el mínimo cambio posible.

4. **Scope de tarjeta en esta US:**
   solo `Blanca` y `Roja`.
   Penalizaciones y `Amarilla` quedan fuera hasta `US-4.3.3` y `US-4.3.4`.

---

## Riesgos concretos

- El endpoint actual de grilla no trae estado semántico rico por fila.
- Los bodies HTTP deben mapear con precisión a enums del dominio.
- El wizard mobile puede crecer rápido si se intenta resolver diseño final y
  edge cases en la misma pasada.

---

## Estado

**Estado:** 0/13 tareas completadas

*Plan generado: 2026-04-11 — US-4.3.2 INC-4.3 SP4*
