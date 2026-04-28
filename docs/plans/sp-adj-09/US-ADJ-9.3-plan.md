# Plan de Implementacion - US-ADJ-9.3: Home del organizador

**Sprint:** SP-ADJ-09
**Patron:** React/Vite frontend
**Estimacion total:** 90 min

---

## Diagnostico

La base estructural ya existe desde `US-ADJ-9.2`: la ruta principal del organizador
ya aterriza en una home de torneos. El ajuste de `9.3` consiste en formalizar esa
pantalla como home del rol, alineando la clasificación funcional de estados, el copy
y el filtro principal con la spec aprobada.

## Cambios por area

### 1. Clasificacion de torneos

- [ ] Definir helpers explícitos para `vigentes` e `historico` (15 min)
  - vigentes:
    - `INSCRIPCION_ABIERTA`
    - `PREPARACION`
    - `EJECUCION`
    - `PREMIACION`
  - historico:
    - `CERRADO`
    - `CANCELADO`

- [ ] Excluir `CREADO` del set de vigentes por defecto, salvo decisión contraria en la UI (10 min)

### 2. Home del organizador

- [ ] Ajustar `DashboardPage.tsx` para presentar explícitamente:
  - torneos vigentes
  - acceso a histórico
  - copy de home de torneos, no dashboard operativo (20 min)

- [ ] Renombrar filtros heredados (`abiertos`, `todos`, etc.) a la semántica aprobada (10 min)

### 3. Claridad visual y navegación

- [ ] Mantener la acción principal de cada torneo hacia su gestión (5 min)
- [ ] Refinar empty states para vigentes e histórico (10 min)

### 4. Validación

- [ ] `npm run build` en `frontend/` (5 min)
- [ ] `npm run lint` en `frontend/` (5 min)
- [ ] validación manual del filtro default y del histórico (10 min)

## Decisiones clave

- Esta US no implementa todavía el dashboard operativo del torneo activo.
- La pantalla debe seguir siendo una lista de torneos, pero con semántica formalizada.
- Si `CREADO` no entra en vigencia según spec, no debe contaminar el listado default.

## Riesgos y mitigaciones

- Riesgo: perder acceso visible a torneos en `CREADO`.
  Mitigacion: decidir un fallback controlado en la UI sin romper la definición principal de vigencia.

- Riesgo: cambios demasiado cosméticos y no funcionales.
  Mitigacion: centrar la implementación en clasificación, filtro y semántica observable.

## Criterio de salida

La implementación de esta US termina cuando:

1. la home del organizador muestra por defecto torneos vigentes;
2. el histórico queda disponible con un filtro explícito;
3. la pantalla se presenta como home de torneos y no como dashboard operativo;
4. build y lint quedan ejecutados.
