# Plan de Implementacion: US-5.4.1 - Auto-registro de usuario

**Historia:** US-5.4.1 - Auto-registro de usuario
**Incremento:** INC-5.4 - Identidad Extendida
**Producto:** identidad + frontend
**Patron:** Hexagonal DDD BC-first + React/Vite frontend
**Estimacion:** 5 puntos
**Estado:** EN PLANIFICACION

---

## Alcance

Implementar auto-registro publico con extension del aggregate `Usuario`:

- Extender `Usuario` con `nombre` y `apellido`.
- Extender `POST /auth/registro` para aceptar esos campos.
- Rechazar `rol=ADMIN` en backend con `403`.
- Migrar SQLite para agregar columnas `nombre` y `apellido` sin romper DBs existentes.
- Crear pagina publica `/registro` y link desde `LoginPage`.
- Actualizar `UsuariosPage` y `GET /auth/usuarios` para mostrar `nombre` y `apellido`.

Fuera de alcance: login automatico post-registro, recuperacion de password, cambio de password, edicion de perfil.

---

## Componentes a Modificar

### Dominio identidad

- [ ] `src/identidad/domain/aggregates/usuario.py` (20 min)
  - Agregar `nombre` y `apellido` al aggregate.
  - Validar que no sean vacios o solo espacios.

- [ ] `src/identidad/domain/exceptions.py` (10 min)
  - Agregar `RolNoPermitido`.
  - Reutilizar mensaje especificado por la US.

### Aplicacion identidad

- [ ] `src/identidad/application/commands/registrar_usuario.py` (25 min)
  - Extender `RegistrarUsuarioCommand` con `nombre` y `apellido`.
  - Rechazar `Rol.ADMIN` antes de persistir.
  - Construir `Usuario` con los nuevos campos.

### Infraestructura identidad

- [ ] `src/identidad/infrastructure/repositories/sqlite_usuario_repository.py` (40 min)
  - Extender esquema `usuarios` con `nombre` y `apellido`.
  - Hacer migracion idempotente en `_ensure_table`.
  - Actualizar `save`, `find_by_id`, `find_by_email`, `list_by_rol` y `list_all`.

### API identidad

- [ ] `src/identidad/api/router.py` (35 min)
  - Extender `RegistroRequest` con `nombre` y `apellido`.
  - Validar password como hoy y mapear `RolNoPermitido` a `403`.
  - Extender `UsuarioResponse` y el listado `/auth/usuarios`.

### Frontend API

- [ ] `frontend/src/api/identidad.ts` (25 min)
  - Extender `CrearUsuarioRequest` con `nombre` y `apellido`.
  - Extender `UsuarioDto` con `nombre` y `apellido`.
  - Mantener compatibilidad con `listarTodosLosUsuarios()` y `crearUsuario()`.

### Frontend paginas y routing

- [ ] `frontend/src/pages/RegistroPage.tsx` (90 min)
  - Crear pagina publica con campos nombre, apellido, email, password y rol.
  - Validar nombre/apellido requeridos y password minima.
  - Mostrar errores inline por `409`, `422` y `403`.
  - Redirigir a `/login` tras alta exitosa con mensaje visible.

- [ ] `frontend/src/pages/LoginPage.tsx` (15 min)
  - Agregar CTA hacia `/registro`.
  - Mantener redirect por sesion activa.

- [ ] `frontend/src/App.tsx` (15 min)
  - Registrar ruta publica `/registro`.

- [ ] `frontend/src/pages/organizador/UsuariosPage.tsx` (30 min)
  - Mostrar nombre y apellido junto al email en la lista.
  - Ajustar formulario existente al nuevo payload.

---

## Tests

### Unitarios backend

- [ ] `tests/unit/identidad/application/test_registrar_usuario.py` (35 min)
  - Cubrir nombre/apellido requeridos.
  - Cubrir rechazo de `ADMIN`.
  - Mantener email unico y password minima.

- [ ] `tests/unit/identidad/api/test_registro_usuario.py` (35 min)
  - Cubrir `201`, `403`, `409` y `422`.
  - Verificar que el payload requiere `nombre` y `apellido`.

### Integracion backend

- [ ] `tests/integration/identidad/test_sqlite_usuario_repository.py` (30 min)
  - Cubrir persistencia y lectura de `nombre`/`apellido`.
  - Cubrir upgrade sobre DB existente con tabla sin columnas nuevas.

### Frontend

- [ ] Validacion TypeScript/build (20 min)
  - Ejecutar `npm run build` en `frontend/`.
  - Ejecutar `npm run lint` en `frontend/` si el baseline local lo permite.

### BDD

- [ ] `tests/features/US-5.4.1-auto-registro.feature` (15 min)
  - Feature creada en Fase 1.
  - Validacion UI/manual documentada si no hay harness browser automatizado.

---

## Quality Gates

- [ ] `pytest` sobre tests unitarios de identidad afectados
- [ ] `pytest` sobre tests de integracion de identidad afectados
- [ ] `npm run build` en `frontend/`
- [ ] `npm run lint` en `frontend/` si no falla por deuda previa ajena
- [ ] `codeguard src/identidad/ --format json > quality/reports/codeguard/US-5.4.1-codeguard-raw.json`
- [ ] Resumen `quality/reports/codeguard/US-5.4.1-quality.json`

---

## Riesgos y Decisiones

- La decision de dejar `nombre` y `apellido` vacios para usuarios legacy queda acotada a la migracion; los nuevos registros no pueden crearse vacios.
- El selector del frontend no expone `ADMIN`, pero la garantia real vive en el handler/backend.
- La pantalla `UsuariosPage` ya existe y no puede romperse mientras entra la pagina publica.
- El mensaje post-registro debe sobrevivir al redirect a `/login` sin requerir autenticacion previa.

---

## Criterios de Aceptacion Cubiertos

- [ ] Auto-registro exitoso como atleta.
- [ ] Nombre o apellido vacios se rechazan antes de enviar.
- [ ] Email duplicado muestra error inline.
- [ ] Rol `ADMIN` se rechaza en backend.
- [ ] Rol `ADMIN` no aparece en selector.
- [ ] Login muestra link publico a registro.

**Estado:** 0/13 tareas completadas
