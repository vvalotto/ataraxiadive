# Plan de Implementacion: US-5.3.1 - UI de gestion de usuarios

**Historia:** US-5.3.1 - UI de gestion de usuarios
**Incremento:** INC-5.3 - Gestion de usuarios y roles
**Producto:** identidad + frontend
**Patron:** Hexagonal DDD BC-first + React/Vite frontend
**Estimacion:** 3 puntos
**Estado:** EN PLANIFICACION

---

## Alcance

Implementar la pantalla de gestion de usuarios para organizador:

- Listar todos los usuarios del sistema desde `GET /auth/usuarios`.
- Mantener el filtro existente `GET /auth/usuarios?rol=JUEZ`.
- Crear usuarios con email, password y rol desde `POST /auth/registro`.
- Validar password corta en frontend antes de enviar.
- Mostrar error inline para email duplicado.
- Exponer solo roles `JUEZ`, `ATLETA` y `ORGANIZADOR` en el formulario.

Fuera de alcance: edicion, desactivacion, rol `ADMIN` desde UI.

---

## Componentes a Modificar

### Backend identidad

- [ ] `src/identidad/domain/ports/usuario_repository_port.py` (10 min)
  - Agregar contrato `list_all() -> list[Usuario]`.
  - Mantener `list_by_rol(rol)` para compatibilidad.

- [ ] `src/identidad/infrastructure/repositories/sqlite_usuario_repository.py` (20 min)
  - Implementar `list_all()`.
  - Ordenar por `rol`, luego `email`.
  - Conservar `list_by_rol()` ordenado por email.

- [ ] `src/identidad/api/router.py` (25 min)
  - Hacer `rol` opcional en `GET /auth/usuarios`.
  - Si `rol` viene informado, usar `list_by_rol(rol)`.
  - Si `rol` no viene informado, usar `list_all()`.
  - Mantener `OrganizadorDep`.
  - Serializar `usuario_id`, `email`, `rol`, `activo`.

### Frontend

- [ ] `frontend/src/api/identidad.ts` (25 min)
  - Agregar tipo `RolGestionUsuario = 'JUEZ' | 'ATLETA' | 'ORGANIZADOR'`.
  - Agregar `CrearUsuarioRequest`.
  - Agregar `listarTodosLosUsuarios()`.
  - Conservar `listarUsuariosPorRol()`.
  - Agregar `crearUsuario()`.

- [ ] `frontend/src/pages/organizador/UsuariosPage.tsx` (90 min)
  - Crear pagina con `OrganizadorLayout`.
  - Cargar usuarios con React Query.
  - Mostrar tabla/lista con email, rol y estado.
  - Formulario email/password/rol.
  - Validar email requerido y password minimo 8 caracteres.
  - En exito: limpiar formulario e invalidar/refrescar lista.
  - En 409: mostrar "Este email ya esta registrado" inline y conservar datos.
  - No exponer `ADMIN` en selector.

- [ ] `frontend/src/App.tsx` (15 min)
  - Importar `UsuariosPage`.
  - Agregar ruta `/organizador/usuarios` protegida con `RequireRole role="organizador"`.

- [ ] `frontend/src/pages/organizador/DashboardPage.tsx` (15 min)
  - Agregar acceso navegable a gestion de usuarios desde acciones del panel.

---

## Tests

### Unitarios backend

- [ ] `tests/unit/identidad/api/test_listar_usuarios.py` (25 min)
  - Agregar caso `GET /auth/usuarios` sin rol devuelve todos.
  - Validar orden por rol/email.
  - Mantener caso existente `?rol=JUEZ`.
  - Mantener rechazo 403 si no es organizador.

### Integracion backend

- [ ] `tests/integration/identidad/test_sqlite_usuario_repository.py` (20 min)
  - Agregar cobertura para `list_all()`.
  - Validar que incluye roles mixtos y ordena por rol/email.

### Frontend

- [ ] Validacion TypeScript/build (20 min)
  - Ejecutar `npm run build` en `frontend/`.
  - Ejecutar `npm run lint` si el estado base lo permite.

### BDD

- [ ] `tests/features/US-5.3.1-gestion-usuarios.feature` (15 min)
  - Feature creado en Fase 1.
  - Validacion BDD/UI manual documentada si no existe harness browser automatizado.

---

## Quality Gates

- [ ] `pytest tests/unit/identidad/api/test_listar_usuarios.py`
- [ ] `pytest tests/integration/identidad/test_sqlite_usuario_repository.py`
- [ ] `npm run build` en `frontend/`
- [ ] `npm run lint` en `frontend/` si no falla por deuda previa ajena
- [ ] `codeguard src/identidad/ --format json > quality/reports/codeguard/US-5.3.1-codeguard-raw.json`
- [ ] `codeguard src/identidad/`
- [ ] Crear resumen `quality/reports/codeguard/US-5.3.1-quality.json`

Nota: la cobertura formal de `domain/` + `application/` no cambia por esta US; el cambio backend toca puerto, repositorio y API. Si el comando de coverage del perfil no aplica por ausencia de cambios en handlers/domain, se documentara en Fase 7 con evidencia de tests especificos.

---

## Riesgos y Decisiones

- `GET /auth/usuarios` actualmente exige `rol`; el cambio debe conservar compatibilidad con clientes existentes.
- `RolIdentidad` incluye `ADMIN`, pero la UI de gestion debe usar un tipo acotado para no exponerlo.
- El formulario debe preservar datos ante 409 y limpiar solo en 201.
- Hay cambios locales no relacionados en el worktree; esta US no debe tocarlos.

---

## Criterios de Aceptacion Cubiertos

- [ ] Organizador ve la lista completa de usuarios.
- [ ] Organizador crea usuario juez exitosamente.
- [ ] Email duplicado muestra error inline.
- [ ] Password corta se rechaza antes de enviar.
- [ ] Selector de rol no muestra `ADMIN`.

**Estado:** 0/15 tareas completadas
