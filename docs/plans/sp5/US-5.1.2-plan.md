# Plan de Implementacion — US-5.1.2 Gestion de Fases del Torneo

**Sprint:** SP5  
**Incremento:** INC-5.1  
**Producto:** frontend  
**Patron:** React/Vite PWA consumiendo BC `torneo` existente  
**Estimacion:** 3 puntos

## Alcance

Extender el detalle del torneo para que el organizador pueda ver la fase actual y ejecutar
las transiciones validas del ciclo de vida.

## Tareas

### 1. API Frontend

- [ ] Extender `frontend/src/api/torneo.ts` con tipo `EstadoTorneo`.
- [ ] Implementar `transicionarTorneo(torneoId, endpoint)`.
- [ ] Exponer funciones:
  - `abrirInscripcion`
  - `cerrarInscripcion`
  - `iniciarEjecucion`
  - `volverPreparacion`
  - `iniciarPremiacion`
  - `cerrarTorneo`
  - `cancelarTorneo`

### 2. Componentes de Fase

- [ ] Crear `frontend/src/components/organizador/FaseBadge.tsx`.
- [ ] Crear `frontend/src/components/organizador/AccionesPanel.tsx`.
- [ ] Mostrar acciones segun estado actual.
- [ ] Mostrar cancelacion para estados activos.
- [ ] Usar confirmacion explicita para cancelacion.

### 3. Detalle del Torneo

- [ ] Integrar `FaseBadge` en `DetalleTorneoPage`.
- [ ] Integrar `AccionesPanel`.
- [ ] Refrescar `GET /torneos/{id}` despues de transicion exitosa.
- [ ] Mostrar errores backend inline sin mutar estado local.
- [ ] Agregar tabs base: Detalle, Inscriptos, Grilla, Jueces, Ejecucion.

### 4. Validacion

- [ ] `npm run build`.
- [ ] `npx eslint src`.
- [ ] Documentar limitaciones de `npm run lint` global por `.vite/deps` generado.

## Riesgos

- La UI define el mapa de acciones visible, pero el backend sigue siendo la autoridad:
  cualquier rechazo `409` se muestra inline y no se fuerza cambio local de estado.
- Los tabs de futuras US se implementan como placeholders navegables dentro del detalle,
  sin introducir funcionalidad de inscriptos/grilla/jueces/ejecucion.

## DoD

- El badge refleja la fase actual.
- Solo aparecen acciones coherentes con el estado.
- Las transiciones exitosas refrescan el torneo.
- Los errores backend se muestran sin recargar.
- Estados terminales no muestran acciones.
