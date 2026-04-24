# Plan de Implementacion: US-5.4.2 - Cambiar contrasena

**Historia:** US-5.4.2 - Cambiar contraseña
**Incremento:** INC-5.4 - Identidad Extendida
**Producto:** identidad + frontend
**Patron:** Hexagonal DDD BC-first + React/Vite frontend
**Estimacion:** 3 puntos
**Estado:** EN PLANIFICACION

---

## Alcance

Implementar cambio de contraseña para usuarios autenticados:

- Agregar command y handler para verificar password actual y persistir el nuevo hash.
- Exponer `POST /auth/cambiar-password` autenticado por JWT.
- Crear pantalla frontend con password actual, nueva y confirmacion.
- Redirigir al home correcto segun rol tras cambio exitoso.

Fuera de alcance: invalidacion de JWT vigente, politicas de password compleja, recuperacion de password.

---

## Componentes a Modificar

### Dominio identidad

- [ ] `src/identidad/domain/exceptions.py` (10 min)
  - Agregar `PasswordActualIncorrecto`.

### Aplicacion identidad

- [ ] `src/identidad/application/commands/cambiar_password.py` (35 min)
  - Crear `CambiarPasswordCommand`.
  - Crear `CambiarPasswordHandler`.
  - Buscar usuario por `usuario_id`, verificar bcrypt actual y persistir hash nuevo.
  - Rechazar password nueva menor a 8 caracteres.

### API identidad

- [ ] `src/identidad/api/router.py` (35 min)
  - Crear schema `CambiarPasswordRequest`.
  - Agregar endpoint `POST /auth/cambiar-password`.
  - Obtener `usuario_id` desde `get_current_user`.
  - Mapear `PasswordActualIncorrecto` a `401` y password corta a `422`.

### Frontend API

- [ ] `frontend/src/api/identidad.ts` (20 min)
  - Agregar `cambiarPassword(passwordActual, passwordNueva)`.
  - Reusar `ApiError`.

### Frontend paginas y routing

- [ ] `frontend/src/pages/CambiarPasswordPage.tsx` (75 min)
  - Crear formulario con password actual, nueva y confirmacion.
  - Validar longitud minima y coincidencia de confirmacion.
  - Mostrar errores inline y redirigir al home del rol al exito.

- [ ] `frontend/src/App.tsx` (20 min)
  - Agregar ruta protegida para usuarios autenticados.
  - Resolver acceso transversal a los tres roles sin duplicar pantallas.

- [ ] `frontend/src/pages/atleta/AtletaDashboardPage.tsx` y/o layouts existentes (25 min)
  - Exponer un acceso navegable a la pantalla de cambio de password desde una vista ya accesible para cada rol.

---

## Tests

### Unitarios backend

- [ ] `tests/unit/identidad/application/test_cambiar_password.py` o ampliar `test_handlers.py` (35 min)
  - Cubrir exito, password actual incorrecta y password nueva corta.

- [ ] `tests/unit/identidad/api/test_cambiar_password.py` (30 min)
  - Cubrir `204`, `401` y `422`.
  - Cubrir requisito de autenticacion JWT.

### Integracion backend

- [ ] `tests/integration/identidad/test_sqlite_usuario_repository.py` o nuevo test de flujo (20 min)
  - Verificar que luego del cambio el hash persistido ya no valida la password anterior y si la nueva.

### Frontend

- [ ] Validacion TypeScript/build (20 min)
  - Ejecutar `npm run build` en `frontend/`.
  - Ejecutar `npm run lint` en `frontend/`.

### BDD

- [ ] `tests/features/US-5.4.2-cambiar-password.feature` (10 min)
  - Feature creada en Fase 1.
  - Validacion UI/manual documentada si no hay harness browser automatizado.

---

## Quality Gates

- [ ] `./.venv/bin/pytest tests/unit/identidad tests/integration/identidad`
- [ ] `npm run build` en `frontend/`
- [ ] `npm run lint` en `frontend/`
- [ ] `codeguard src/identidad/ --format json > quality/reports/codeguard/US-5.4.2-codeguard-raw.json`

---

## Riesgos y Decisiones

- El body del endpoint no debe aceptar `usuario_id`; el origen de verdad es el JWT.
- La pantalla debe ser alcanzable por organizador, juez y atleta sin crear tres implementaciones paralelas.
- El cambio de password no invalida el JWT actual; ese comportamiento debe quedar documentado.
- El repositorio ya persiste `Usuario` completo, por lo que el update puede resolverse como re-save del aggregate modificado.

---

## Criterios de Aceptacion Cubiertos

- [ ] Cambio de password exitoso.
- [ ] Password actual incorrecta se rechaza.
- [ ] Password nueva corta se rechaza antes de enviar.
- [ ] Confirmacion distinta se rechaza en frontend.

**Estado:** 0/9 tareas completadas
