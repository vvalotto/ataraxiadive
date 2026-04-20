# Plan de Implementacion — US-5.1.1 Crear Torneo desde UI

**Sprint:** SP5  
**Incremento:** INC-5.1  
**Producto:** frontend  
**Patron:** React/Vite PWA consumiendo BC `torneo` existente  
**Estimacion:** 3 puntos

## Alcance

Implementar el alta de torneo desde el panel del organizador:

- Ruta protegida `/organizador/torneos/nuevo`.
- Formulario con nombre, descripcion, sede, fechas, entidad organizadora y disciplinas.
- Validaciones frontend para nombre, fechas y seleccion de disciplinas.
- API client para `POST /torneos` y `PUT /torneos/{torneo_id}/disciplinas`.
- Navegacion a `/organizador/torneo/{torneo_id}` tras exito.
- Ruta de detalle minima para que la navegacion post-creacion no quede rota.

## Tareas

### 1. API Frontend

- [ ] Extender `frontend/src/api/torneo.ts`.
- [ ] Agregar helper de headers con bearer token usando `getToken`.
- [ ] Agregar `ApiError` reutilizable para errores con `detail` del backend.
- [ ] Agregar tipos `CrearTorneoPayload` y `CrearTorneoResponse`.
- [ ] Implementar `crearTorneo(payload)`.
- [ ] Implementar `asignarDisciplinas(torneoId, disciplinas)`.
- [ ] Implementar `fetchTorneo(torneoId)` para detalle minimo.

### 2. Componentes UI

- [ ] Crear `frontend/src/components/organizador/DisciplinaSelector.tsx`.
- [ ] Mostrar 8 disciplinas FAAS: `STA`, `DNF`, `DYN`, `DBF`, `SPE_2X50`, `SPE_4X50`, `SPE_8X50`, `SPE_16X50`.
- [ ] Mantener dimensiones estables y labels legibles.

### 3. Paginas

- [ ] Crear `frontend/src/pages/organizador/CrearTorneoPage.tsx`.
- [ ] Validar en frontend:
  - nombre obligatorio
  - fecha fin igual o posterior a inicio
  - al menos una disciplina
- [ ] Ejecutar flujo en dos pasos: crear torneo y asignar disciplinas.
- [ ] Mostrar error inline sin perder datos si falla backend.
- [ ] Crear `frontend/src/pages/organizador/DetalleTorneoPage.tsx` minimo para destino post-creacion.

### 4. Rutas e Integracion

- [ ] Registrar ruta `/organizador/torneos/nuevo` en `frontend/src/App.tsx`.
- [ ] Registrar ruta `/organizador/torneo/:torneoId` en `frontend/src/App.tsx`.
- [ ] Agregar accion visible desde `DashboardPage` para crear torneo.
- [ ] Mantener guardia `RequireRole role="organizador"`.

### 5. Validacion

- [ ] Ejecutar `npm run build` en `frontend`.
- [ ] Ejecutar `npm run lint` en `frontend` si el build pasa.
- [ ] Registrar evidencia en reporte final.

## Riesgos

- La spec navega a una pagina de detalle que formalmente pertenece a `US-5.1.2`; se implementa una version minima solo para no romper el flujo de `US-5.1.1`.
- El backend exige autenticacion de organizador en POST/PUT, por lo que el API client debe enviar bearer token.

## DoD

- El organizador puede crear un torneo desde UI.
- El torneo queda creado con disciplinas asignadas.
- Los errores de validacion frontend no llaman al backend.
- Los errores backend se muestran inline y conservan el formulario.
- La navegacion post-creacion lleva a un detalle observable del torneo.
