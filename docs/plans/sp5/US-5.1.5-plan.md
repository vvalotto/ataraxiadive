# Plan de Implementacion — US-5.1.5 Asignacion de jueces desde UI

**Sprint:** SP5
**Incremento:** INC-5.1
**Producto:** frontend + endpoint de consulta en `identidad/api`
**Patron:** React/Vite PWA consumiendo APIs existentes, con extension minima de Identidad
**Estimacion:** 3 puntos

## Alcance

Implementar el tab `Jueces` del detalle de torneo para que el organizador vea las
disciplinas del torneo, seleccione un usuario con rol `JUEZ` por disciplina y persista
la asignacion contra `torneo/api`.

## Contratos Disponibles

- `GET /torneos/{torneo_id}/disciplinas` retorna `{ disciplina, juez_id }[]`.
- `PUT /torneos/{torneo_id}/disciplinas/{disciplina}/juez` persiste `{ juez_id }`.
- `GET /torneos/{torneo_id}/jueces/{juez_id}/disciplinas` existe para UI de juez.

## Brecha Detectada

No existe endpoint para listar usuarios por rol. La spec menciona
`GET /identidad/usuarios?rol=JUEZ`, pero el router real de Identidad usa prefijo `/auth`.

**Decision propuesta:** agregar `GET /auth/usuarios?rol=JUEZ` protegido por rol
ORGANIZADOR/ADMIN, con respuesta minima `{ usuario_id, email, rol, activo }[]`.

## Tareas

### 1. Identidad API

- [ ] Extender repositorio de usuarios con consulta `list_by_rol(rol)`.
- [ ] Agregar schema `UsuarioResponse`.
- [ ] Agregar endpoint `GET /auth/usuarios?rol=JUEZ`.
- [ ] Proteger endpoint con `OrganizadorDep`.
- [ ] Agregar test unitario/API focalizado del endpoint.

### 2. API Frontend

- [ ] Crear `frontend/src/api/identidad.ts`.
- [ ] Implementar `listarUsuariosPorRol('JUEZ')`.
- [ ] Extender `frontend/src/api/torneo.ts` con:
  - `listarDisciplinasTorneo(torneoId)`.
  - `asignarJuez(torneoId, disciplina, juezId)`.

### 3. Componentes UI

- [ ] Crear `JuezSelector`.
  - Recibe jueces, valor actual, loading y error.
  - Placeholder `Sin juez asignado`.
  - Solo muestra usuarios con rol `JUEZ`.
- [ ] Crear `TablaJueces`.
  - Una fila por disciplina del torneo.
  - Selector de juez por fila.
  - Estado visual de guardado por fila.
  - Reversión al valor anterior si backend devuelve error.
- [ ] Crear `JuecesPanel`.
  - Carga disciplinas y jueces en paralelo.
  - Muestra error inline.
  - Muestra indicador si todas las disciplinas tienen juez asignado.

### 4. Integracion en DetalleTorneo

- [ ] Reemplazar placeholder del tab `Jueces`.
- [ ] Pasar `torneoId` a `JuecesPanel`.
- [ ] Mantener consistencia visual con `InscriptosPanel` y `GrillaPanel`.

### 5. Validacion

- [ ] `npm run build`.
- [ ] `npx eslint src vite.config.ts`.
- [ ] `python3 -m py_compile` de archivos backend/test nuevos.
- [ ] Ejecutar pytest focalizado si el entorno tiene dependencias Python disponibles.
- [ ] Registrar evidencia en `docs/reports/US-5.1.5-report.md`.

## Riesgos y Decisiones

- El endpoint de usuarios vive bajo `/auth` por compatibilidad con el router existente,
  aunque la spec lo nombre como `/identidad`.
- La validacion de que `juez_id` tenga rol JUEZ no existe en `torneo/api`, porque Torneo no
  depende de Identidad. La UI filtra jueces; una validacion cross-BC estricta requeriria
  puerto/ACL adicional y queda fuera del alcance de frontend.
- Si el torneo no esta en `Preparacion`, el backend devolvera 409 y la UI debe mostrar
  el mensaje sin dejar el selector en estado optimista incorrecto.

## DoD

- El organizador ve todas las disciplinas del torneo en el tab `Jueces`.
- Cada fila muestra el juez asignado o `Sin juez asignado`.
- Puede asignar y reasignar jueces.
- Solo aparecen usuarios con rol `JUEZ`.
- Errores del backend se muestran inline y no corrompen el estado visual.
