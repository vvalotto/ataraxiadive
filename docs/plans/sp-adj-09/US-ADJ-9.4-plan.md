# Plan de Implementacion - US-ADJ-9.4: Dashboard operativo del organizador

**Sprint:** SP-ADJ-09
**Patron:** React/Vite frontend
**Estimacion total:** 150 min

---

## Diagnostico

La ruta primaria `Panel` ya existe en el shell del organizador, pero hoy renderiza
`DetalleTorneoPage`, una vista centrada en detalle de torneo, tabs locales y acciones
de fase. La spec `US-ADJ-9.4` exige separar ese comportamiento e introducir un
dashboard ejecutivo alineado al wireframe `S-01`, manteniendo la home de torneos en
`/organizador/torneo` definida por `US-ADJ-9.3`.

La implementacion puede apoyarse en queries ya existentes del frontend:

- `fetchTorneo`
- `fetchCompetenciasPorTorneo`
- `fetchEstadoCompetencia`
- `fetchGrillaCompetencia`
- `TorneoRouteSelector`

No hay, por ahora, una API dedicada para alertas operativas; por eso el plan debe
explicitar una estrategia de composicion UI consistente con datos disponibles.

---

## Cambios por area

### 1. Separacion de la ruta `Panel`

- [ ] Crear una page dedicada para el dashboard operativo del organizador (25 min)
  - nueva page enfocada en la ruta `/organizador/panel`
  - conservar seleccion de torneo cuando no hay `torneo_id`
  - dejar `DetalleTorneoPage` para flujos de detalle/contexto y no como panel principal

- [ ] Ajustar `frontend/src/App.tsx` para montar la nueva page en `Panel` (10 min)
  - mantener compatibilidad con el shell y la navegación primaria
  - evitar mezclar el panel con la home de torneos

### 2. View model operativo del dashboard

- [ ] Definir helpers para identificar disciplina activa y disciplinas informativas (20 min)
  - prioridad para estado `EnEjecucion`
  - fallback controlado si no hay competencia en ejecución
  - distinguir disciplina principal de las restantes

- [ ] Componer KPIs operativos a partir de grilla/estado/torneo (20 min)
  - atletas totales
  - completados
  - en revisión
  - tiempo estimado o mensaje equivalente si no puede calcularse con los datos actuales

- [ ] Derivar alertas visibles y próximos atletas desde la grilla activa (20 min)
  - alertas basadas en estados en revisión o bloqueos observables
  - empty state explícito `Sin alertas`
  - próximos atletas con destaque del siguiente

### 3. Componentes UI del dashboard `S-01`

- [ ] Implementar el layout operativo de `Panel` (25 min)
  - KPI strip de 4 columnas
  - columna izquierda con disciplina activa
  - columna derecha con alertas y próximos
  - sección de otras disciplinas del torneo

- [ ] Crear componentes livianos y reutilizables si la page queda demasiado densa (15 min)
  - cards KPI
  - card de alerta
  - tabla/lista de próximos
  - resumen de disciplina informativa

### 4. Validacion

- [ ] Crear escenario BDD físico de `US-ADJ-9.4` y mantenerlo alineado con la implementación (5 min)
- [ ] `npm run build` en `frontend/` (5 min)
- [ ] `npm run lint` en `frontend/` (5 min)
- [ ] Validación manual de:
  - selector de torneo
  - KPI strip
  - empty state de alertas
  - próximos atletas
  - separación entre `Panel` y `/organizador/torneo` (15 min)

---

## Decisiones clave

- `Panel` deja de renderizar `DetalleTorneoPage` como contenido principal.
- La selección del torneo operativo seguirá viviendo en la propia ruta `Panel` cuando
  no exista `torneo_id`.
- Las alertas se modelarán inicialmente con datos observables del frontend actual,
  sin inventar backend nuevo en esta US.
- Si no se puede calcular un ETA preciso con los datos existentes, se mostrará una
  variante operativa informativa consistente con el wireframe.

---

## Riesgos y mitigaciones

- Riesgo: acoplar demasiado la page nueva con `DetalleTorneoPage`.
  Mitigacion: separar la ruta y limitar la reutilización a utilidades y selector.

- Riesgo: datos insuficientes para alertas/ETA exactos.
  Mitigacion: derivar un modelo visible y explícito con empty states claros, sin
  simular precisión inexistente.

- Riesgo: regresión visual respecto del shell dark ya estabilizado en `US-ADJ-9.1`.
  Mitigacion: mantener `OrganizadorLayout` y seguir los tokens ya presentes.

---

## Criterio de salida

La implementación de esta US termina cuando:

1. la ruta `/organizador/panel` renderiza un dashboard operativo real;
2. el contenido principal muestra KPIs, disciplina activa, alertas y próximos atletas;
3. la home de torneos sigue separada en `/organizador/torneo`;
4. build y lint quedan ejecutados;
5. el artefacto de documentación y el reporte final quedan creados antes del commit.
