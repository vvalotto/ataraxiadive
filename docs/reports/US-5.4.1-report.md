# Reporte de Implementacion: US-5.4.1

## Resumen Ejecutivo

- **Historia de Usuario:** US-5.4.1 - Auto-registro de usuario
- **Puntos estimados:** 5
- **Estado:** COMPLETADO
- **Fecha completado:** 2026-04-24
- **Branch de trabajo:** `feature/US-5.4.1-auto-registro`

## Componentes Implementados

- [x] Extension de `Usuario` con `nombre` y `apellido`.
- [x] Nueva excepcion `RolNoPermitido` y validacion de campos requeridos.
- [x] `RegistrarUsuarioCommand` y `RegistrarUsuarioHandler` extendidos para auto-registro publico.
- [x] Migracion idempotente de `SQLiteUsuarioRepository` para columnas `nombre` y `apellido`.
- [x] `POST /auth/registro` con payload extendido y rechazo de `ADMIN`.
- [x] `GET /auth/usuarios` ahora expone `nombre` y `apellido`.
- [x] Cliente frontend de identidad actualizado al nuevo contrato.
- [x] Nueva pagina publica `frontend/src/pages/RegistroPage.tsx`.
- [x] `LoginPage` con CTA a `/registro` y mensaje post-registro.
- [x] `UsuariosPage` ajustada para nombre/apellido y nuevo payload.

## Comportamiento Entregado

- Una persona sin cuenta puede registrarse con nombre, apellido, email, password y rol.
- El backend rechaza `rol=ADMIN` con `403` aunque el cliente no lo exponga.
- La persistencia de identidad migra bases SQLite existentes sin recrear la tabla.
- La pagina de login ahora permite navegar a `/registro`.
- La lista de usuarios del organizador muestra nombre y apellido ademas de email, rol y estado.

## Validacion Ejecutada

| Gate | Resultado |
|------|-----------|
| `./.venv/bin/pytest tests/unit/identidad tests/integration/identidad` | OK |
| `npm run build` | OK |
| `npm run lint` | OK |
| Validacion BDD/UI en navegador | Pendiente manual |

## Riesgos y Observaciones

- La advertencia de chunk >500 kB en Vite sigue presente, pero no bloquea el build de esta US.
- Los tests de JWT siguen emitiendo `InsecureKeyLengthWarning` por el secret corto del fixture de prueba existente.
- La migracion deja usuarios legacy con `nombre` y `apellido` vacios si ya existian en la base local; los nuevos registros no permiten ese estado.

## Archivos Relevantes

- `src/identidad/domain/aggregates/usuario.py`
- `src/identidad/application/commands/registrar_usuario.py`
- `src/identidad/infrastructure/repositories/sqlite_usuario_repository.py`
- `src/identidad/api/router.py`
- `frontend/src/pages/RegistroPage.tsx`
- `frontend/src/pages/LoginPage.tsx`
- `frontend/src/pages/organizador/UsuariosPage.tsx`
- `tests/unit/identidad/api/test_registro_usuario.py`
- `tests/integration/identidad/test_sqlite_usuario_repository.py`

## Criterios de Aceptacion

- [x] Auto-registro exitoso como atleta.
- [x] Nombre o apellido vacios se rechazan antes de enviar.
- [x] Email duplicado muestra error inline.
- [x] Rol `ADMIN` se rechaza en backend.
- [x] Rol `ADMIN` no aparece en selector.
- [x] Login muestra link a registro.
