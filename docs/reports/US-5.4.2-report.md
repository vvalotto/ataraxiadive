# Reporte de Implementacion: US-5.4.2

## Resumen Ejecutivo

- **Historia de Usuario:** US-5.4.2 - Cambiar contraseña
- **Puntos estimados:** 3
- **Estado:** COMPLETADO
- **Fecha completado:** 2026-04-24
- **Branch de trabajo:** `feature/US-5.4.2-cambiar-password`

## Componentes Implementados

- [x] Nueva excepcion `PasswordActualIncorrecto`.
- [x] Nuevo command/handler `CambiarPasswordCommand` + `CambiarPasswordHandler`.
- [x] Nuevo endpoint autenticado `POST /auth/cambiar-password`.
- [x] Cliente frontend `cambiarPassword()` sin redireccion automatica en `401` de negocio.
- [x] Nueva pagina `frontend/src/pages/CambiarPasswordPage.tsx`.
- [x] Nueva proteccion transversal `RequireAuth`.
- [x] Navegacion a cambio de password desde juez, organizador y atleta.
- [x] Mensaje de exito al volver al home del rol.

## Comportamiento Entregado

- Un usuario autenticado puede cambiar su contraseña con password actual y nueva.
- El backend verifica la password actual con bcrypt antes de persistir el nuevo hash.
- La nueva password debe tener al menos 8 caracteres.
- La confirmacion de password se valida en frontend y no se envía al backend.
- El usuario vuelve al home de su rol luego del cambio exitoso.

## Validacion Ejecutada

| Gate | Resultado |
|------|-----------|
| `./.venv/bin/pytest tests/unit/identidad tests/integration/identidad` | OK |
| `npm run build` | OK |
| `npm run lint` | OK |
| Validacion BDD/UI en navegador | Pendiente manual |

## Riesgos y Observaciones

- `401` en `/auth/cambiar-password` es un error de negocio y ya no expulsa al usuario al login.
- La advertencia de chunk >500 kB en Vite sigue presente, pero no bloquea el build.
- Los tests JWT siguen emitiendo `InsecureKeyLengthWarning` por el fixture existente de secret corto.
- El JWT vigente no se invalida tras el cambio de password; queda documentado como comportamiento actual.

## Archivos Relevantes

- `src/identidad/application/commands/cambiar_password.py`
- `src/identidad/api/router.py`
- `src/identidad/domain/exceptions.py`
- `frontend/src/api/identidad.ts`
- `frontend/src/components/RequireAuth.tsx`
- `frontend/src/pages/CambiarPasswordPage.tsx`
- `frontend/src/pages/juez/DisciplinasPage.tsx`
- `frontend/src/pages/organizador/DashboardPage.tsx`
- `frontend/src/pages/atleta/AtletaDashboardPage.tsx`
- `tests/unit/identidad/api/test_cambiar_password.py`

## Criterios de Aceptacion

- [x] Cambio de password exitoso.
- [x] Password actual incorrecta se rechaza.
- [x] Password nueva corta se rechaza antes de enviar.
- [x] Confirmacion distinta se rechaza en frontend.
