# Plan de Implementacion: US-5.5.2 - Vista del organizador de inscriptos con estado AP

**Historia:** US-5.5.2
**Incremento:** INC-5.5
**Producto:** `frontend` + `registro` + `competencia`
**Estado:** PENDIENTE DE APROBACION

---

## Alcance

Implementar la vista operativa de inscriptos del torneo para organizador, integrada en la navegacion existente del area de torneo, con:

- listado de inscripciones activas;
- nombre y apellido visibles;
- categoria y club;
- disciplinas por atleta;
- estado AP visible por disciplina con semantica UX:
  - `AP pendiente`
  - `AP declarado`
  - `AP cerrado`
- solo lectura visible respecto de AP cuando el torneo ya no esta en `INSCRIPCION_ABIERTA`.

Fuera de alcance de esta US:

- rehacer todas las pantallas del organizador segun el prototipo completo;
- crear una pantalla primaria nueva separada de la gestion del torneo;
- habilitar acciones de editar AP desde la vista del organizador;
- cambios sobre grilla, jueces o resultados mas alla de lo necesario para no romper integracion visual.

---

## Decision Tecnica Propuesta

### 1. Composicion backend dedicada para inscriptos operativos

Agregar una consulta/backend response enfocada en la necesidad operativa del organizador, en lugar de seguir componiendo AP desde la grilla en el frontend.

Objetivo del contrato:

- devolver solo inscripciones activas;
- incluir nombre, apellido, categoria y club del atleta;
- devolver disciplinas inscriptas;
- devolver, por disciplina, si existe AP y cual es su unidad/valor;
- permitir al frontend derivar o recibir el estado visible `pendiente/declarado/cerrado`.

### 2. Semantica de AP alineada con atleta

Usar la misma regla visible ya aplicada en el portal atleta:

- torneo `INSCRIPCION_ABIERTA` + sin AP -> `AP pendiente`
- torneo `INSCRIPCION_ABIERTA` + con AP -> `AP declarado`
- torneo en cualquier otro estado -> `AP cerrado`

### 3. Integracion UX acotada al area tocada

Mantener la vista dentro de `DetalleTorneoPage` tab `Inscriptos`, pero mejorar:

- encabezado operativo;
- copy de solo lectura cuando el periodo ya esta cerrado;
- badges/chips con labels correctas;
- consistencia visual con el patron desktop del organizador.

No propongo rehacer todo `DashboardPage` en esta US. Si durante la implementacion aparece una dependencia fuerte de shell global, se acota a `OrganizadorLayout` sin expandir alcance funcional.

---

## Componentes a Modificar

### Registro

- `src/registro/application/queries/listar_inscriptos.py`
  - evaluar si conviene mantenerlo simple y delegar enriquecimiento a router/query nueva.

- `src/registro/infrastructure/repositories/sqlite_inscripcion_repository.py`
  - excluir `CANCELADA` de la consulta operativa del torneo o agregar una consulta dedicada para inscripciones activas.

- `src/registro/api/router.py`
  - exponer un endpoint enriquecido o extender el actual para la vista operativa del organizador.

### Competencia

- `src/competencia/...`
  - sumar una consulta/adaptador para obtener AP por atleta y disciplina sin depender de la grilla visible.
  - si el camino mas corto reutiliza adapters existentes, evitar introducir complejidad innecesaria.

### Frontend organizador

- `frontend/src/api/registro.ts`
  - consumir el contrato enriquecido nuevo o actualizado.

- `frontend/src/components/organizador/InscriptosPanel.tsx`
  - dejar de componer AP a partir de multiples llamadas ad hoc desde frontend.

- `frontend/src/components/organizador/TablaInscriptos.tsx`
  - mostrar nombre completo, categoria, club, disciplinas y badges AP visibles.
  - agregar estado general de inscripcion si aporta claridad operativa.

- `frontend/src/components/organizador/EstadoAPBadge.tsx`
  - reemplazar `Sin AP` / `AP registrado` por `AP pendiente` / `AP declarado` / `AP cerrado`.

- `frontend/src/pages/organizador/DetalleTorneoPage.tsx`
  - reforzar el area `Inscriptos` con contexto de solo lectura cuando el torneo ya no esta en inscripcion abierta.

- `frontend/src/components/organizador/OrganizadorLayout.tsx`
  - ajustar lo minimo necesario si hace falta acercar la seccion intervenida al patron desktop del organizador.

---

## Tareas Propuestas

1. Corregir la consulta operativa para que no incluya inscripciones canceladas.
2. Implementar una composicion de backend para inscriptos enriquecidos con AP por disciplina.
3. Actualizar el cliente frontend para consumir esa composicion.
4. Rehacer la tabla/panel con estados AP visibles correctos y mensaje de solo lectura.
5. Agregar tests focalizados de backend y validacion de build/lint frontend.

---

## Riesgos y Waivers

- **Riesgo de alcance UX:** el shell del organizador global sigue desalineado respecto del prototipo. Esta US corrige la seccion de torneo/inscriptos, no todo el panel.
- **Riesgo de fuente AP:** si la infraestructura actual no expone AP por disciplina sin recorrer eventos/performance, puede requerir una adaptacion pequena en Competencia.
- **Waiver browser:** no hay harness browser end-to-end consolidado para validar toda la UX del organizador.

---

## Quality Gates

- [ ] `npm run build` en `frontend/`
- [ ] `npm run lint` en `frontend/`
- [ ] tests focalizados de Registro para inscriptos activos
- [ ] tests focalizados de API/composicion de vista de inscriptos
- [ ] reporte de validacion BDD
- [ ] reporte final `docs/reports/US-5.5.2-report.md`
