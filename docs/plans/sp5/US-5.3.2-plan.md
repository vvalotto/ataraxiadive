# Plan de Implementacion: US-5.3.2 - Vista del atleta

**Historia:** US-5.3.2 - Vista del atleta
**Incremento:** INC-5.3 - Gestion de usuarios y roles
**Producto:** frontend
**Patron:** React/Vite frontend sobre arquitectura BC-first del repo
**Estimacion operativa:** 2 puntos
**Estado:** COMPLETADO
**Fecha completado:** 2026-04-23

---

## Alcance

Implementar la vista inicial del atleta:

- Extender el tipo `RolUsuario` con `atleta`.
- Redirigir al atleta autenticado desde `/` hacia `/atleta/dashboard`.
- Proteger `/atleta/dashboard` con `RequireRole role="atleta"`.
- Mostrar perfil del atleta usando `email` y `rol` del `authStore`.
- Listar solo torneos con estado de inscripcion abierta.
- Mostrar mensaje vacio si no hay torneos disponibles.

Fuera de alcance:

- Accion de inscripcion a torneo.
- Formularios del atleta.
- Cambios backend o endpoints nuevos.

---

## Contexto validado

- `frontend/src/stores/useAuthStore.ts` ya convierte el claim JWT `rol` a minusculas, por lo que `ATLETA` pasa a `atleta`.
- `frontend/src/components/RequireRole.tsx` solo necesita extender `RolUsuario` y `HOME_BY_ROL`.
- `frontend/src/api/torneo.ts` ya expone `fetchTorneos()` y normaliza estados a `EstadoTorneo`.
- El estado canonico actual del frontend para inscripcion abierta es `INSCRIPCION_ABIERTA`, no `INSCRIPCION`.

Decision de plan:

- La implementacion filtrara por `INSCRIPCION_ABIERTA`, alineada con el codigo real del frontend y con la normalizacion existente en `frontend/src/api/torneo.ts`.

---

## Componentes a Modificar

### Routing y auth

- [x] `frontend/src/types/auth.ts` (5 min)
  - Agregar `'atleta'` a `RolUsuario`.

- [x] `frontend/src/components/RequireRole.tsx` (10 min)
  - Agregar home por rol para `atleta`.
  - Mantener redireccion consistente para accesos cruzados.

- [x] `frontend/src/App.tsx` (15 min)
  - Importar `AtletaDashboardPage`.
  - Extender `RootRedirect()` para atleta.
  - Agregar ruta protegida `/atleta/dashboard`.

### Vista atleta

- [x] `frontend/src/pages/atleta/AtletaDashboardPage.tsx` (75 min)
  - Crear pagina reutilizando el lenguaje visual actual del frontend.
  - Leer `email`, `rol` y `logout` desde `useAuthStore`.
  - Consultar torneos con React Query usando `fetchTorneos()`.
  - Filtrar client-side por `estado === "INSCRIPCION_ABIERTA"`.
  - Renderizar perfil y lista de torneos disponibles.
  - Renderizar estado vacio y error de carga.

### Tests y artefactos

- [x] `tests/features/US-5.3.2-vista-atleta.feature` (15 min)
  - Documentar redireccion, perfil, filtro de torneos y restricciones por rol.

- [x] Validacion TypeScript/build (20 min)
  - Ejecutar `npm run build` en `frontend/`.
  - Ejecutar `npm run lint` solo si el estado base lo permite.

---

## Quality Gates

- [x] `npm run build` en `frontend/`
- [x] `npm run lint` en `frontend/`
- [x] Validacion manual de la navegacion por roles:
  - `/` redirige a `/atleta/dashboard` si el rol es `atleta`
  - `/organizador/*` y `/juez/*` redirigen de vuelta al home del atleta

---

## Riesgos y Decisiones

- La spec menciona `INSCRIPCION`, pero el frontend actual trabaja con `INSCRIPCION_ABIERTA`; usar `INSCRIPCION` romperia el filtro.
- `OrganizadorLayout` muestra el encabezado fijo "Organizador"; si se reutiliza sin adaptacion, la vista del atleta quedaria semanticamente incorrecta.
- No hay harness browser automatizado en el repo para esta vista; la validacion BDD/UI sera manual.

---

## Criterios de Aceptacion Cubiertos

- [x] Atleta autenticado es redirigido a su dashboard.
- [x] Dashboard muestra email y rol del atleta.
- [x] Solo se muestran torneos con inscripcion abierta.
- [x] Si no hay torneos disponibles, se muestra mensaje informativo.
- [x] El atleta no puede acceder a rutas del organizador ni del juez.

## Metricas de Tiempo

- **Tiempo estimado:** 140 min
- **Tiempo real registrado:** 162 s
- **Observacion:** el tracking refleja solo esta sesion de implementacion y no tiempo de espera externo.

## Lecciones Aprendidas

- El guard de rol existente ya soportaba la logica necesaria; el cambio real fue extender el mapa de home por rol.
- La spec debio aterrizarse al estado frontend real `INSCRIPCION_ABIERTA` para evitar un filtro inconsistente.
- Reutilizar el layout del organizador sin cambios hubiese dejado una semantica incorrecta para el atleta.

**Estado:** 9/9 tareas completadas
