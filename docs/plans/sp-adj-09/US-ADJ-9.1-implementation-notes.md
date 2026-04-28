# US-ADJ-9.1 - Implementation Notes

**Fecha:** 2026-04-28
**Producto:** `frontend`
**Historia:** `US-ADJ-9.1`

---

## Resumen

Se implemento la primera capa del shell del organizador sobre el layout compartido:

- navbar dark y sticky;
- tabs primarios visibles;
- badge de conexion integrado al shell;
- identidad del usuario visible;
- desaparicion del layout beige en las pantallas del organizador que ya usan `OrganizadorLayout`.

---

## Cambios principales

### `OrganizadorLayout.tsx`

- deja de ser solo un header por página;
- pasa a renderizar:
  - marca `AtaraxiaDive`;
  - tabs primarios del organizador;
  - `HealthCheck` compacto;
  - etiqueta de usuario autenticado;
  - encabezado secundario de la sección activa.

### `HealthCheck.tsx`

- agrega variante `compact`;
- permite reutilizar el estado de backend dentro del shell oscuro del organizador.

### `App.tsx`

- el badge global flotante se oculta en rutas del organizador;
- evita duplicar el estado de conexión cuando el shell del organizador ya lo muestra.

### `DashboardPage.tsx`

- adapta estilos de acciones y cards al nuevo shell dark;
- se mantiene funcionalmente como home/listado actual mientras `US-ADJ-9.3` redefine esa pantalla.

---

## Decisiones tecnicas

1. No se reestructuro todavía el routing del organizador.
   Esta US construye el shell base; la reorganizacion de rutas queda para `US-ADJ-9.2`.

2. Los tabs sin ruta primaria establecida aun quedaron visibles pero deshabilitados.
   Esto permite materializar el contrato visual del shell sin inventar destinos incorrectos en esta US.

3. Se reutilizo `useAuthStore` para mostrar el usuario.
   No fue necesario introducir otra fuente de sesión.

4. Se reutilizo `HealthCheck` en modo compacto.
   Evita duplicar lógica de conectividad dentro del shell.

---

## Limitaciones temporales declaradas

- `Grilla`, `Jueces` y `Audit Log` aparecen como tabs visibles pero todavía no tienen
  navegación primaria dedicada desde el shell.
- El active state hoy cubre de forma útil:
  - `Panel`
  - `Resultados`
  - `Torneo`
  - `Audit Log` en rutas de auditoría
- La cobertura completa de navegación queda a cargo de `US-ADJ-9.2`.

---

## Validacion ejecutada

- `npm run build` en `frontend/`: OK
- `npm run lint` en `frontend/`: FAIL por error preexistente ajeno a esta US

Error residual:

- `frontend/src/pages/atleta/portalData.ts:120`
  - `_userId` definido y no usado (`@typescript-eslint/no-unused-vars`)

Observacion:

- El build de Vite sigue reportando warning de chunk grande preexistente; no bloquea esta US.
