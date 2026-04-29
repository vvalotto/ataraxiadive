# Plan de Implementacion: US-ADJ-9.7 - Declarar AP durante inscripcion como precondicion de preparacion

**Patron:** hexagonal-ddd-bc
**Producto:** ataraxiadive
**Estimacion total:** 4h 30min

## Diagnostico tecnico

- `registro/api/router.py` hoy expone `inscriptos-detalle` resolviendo AP desde `competencia` por lectura del Event Store.
- `competencia/application/commands/generar_grilla.py` consume `PerformancesAPPort`, cuya implementacion actual (`PerformancesAPAdapter`) solo ve performances en estado `AnunciadaAP`.
- `torneo/application/commands/transicionar_torneo.py` no valida completitud de AP antes de `INSCRIPCION_ABIERTA -> PREPARACION`.
- `registro/domain/aggregates/inscripcion.py` y `sqlite_inscripcion_repository.py` no persisten AP por disciplina como parte de la inscripcion.
- `frontend/src/components/organizador/InscriptosPanel.tsx` muestra estados, pero no permite editar AP ni comunicar readiness para cierre/preparacion.

## Componentes a Implementar

### 1. Registro como fuente primaria del AP

- [ ] `src/registro/domain/aggregates/inscripcion.py` (25 min)
  - Incorporar AP por disciplina como dato propio de la inscripcion.
  - Exponer operaciones de declaracion/actualizacion y consulta por disciplina.
- [ ] `src/registro/domain/value_objects/` (20 min)
  - Crear VO(s) para representar AP declarado de forma valida y tipada.
- [ ] `src/registro/domain/exceptions.py` (10 min)
  - Agregar errores de AP invalido o disciplina no inscripta si hacen falta.
- [ ] `src/registro/domain/ports/inscripcion_repository_port.py` (10 min)
  - Extender contrato si se requieren lecturas enfocadas en completitud AP.
- [ ] `src/registro/infrastructure/repositories/sqlite_inscripcion_repository.py` (35 min)
  - Persistir AP por disciplina.
  - Resolver migracion compatible con registros existentes sin columna/campo previo.

### 2. Casos de uso y API de Registro

- [ ] `src/registro/application/commands/` (30 min)
  - Crear comando/handler para declarar o actualizar AP por atleta, torneo y disciplina.
- [ ] `src/registro/application/queries/listar_inscriptos.py` o query nueva (20 min)
  - Exponer detalle de inscriptos usando AP desde registro, no desde competencia.
- [ ] `src/registro/api/router.py` (35 min)
  - Reemplazar la lectura de AP desde `competencia`.
  - Agregar endpoint de escritura de AP para el flujo organizador.
  - Mantener compatibilidad de payload para `Inscriptos`.

### 3. Precondicion de cierre de inscripcion en Torneo

- [ ] `src/torneo/application/commands/transicionar_torneo.py` (30 min)
  - Inyectar una validacion externa de completitud AP antes de cerrar inscripcion.
  - Rechazar `INSCRIPCION_ABIERTA -> PREPARACION` cuando existan faltantes.
- [ ] `src/torneo/api/router.py` (20 min)
  - Cablear la precondicion desde `registro`.
  - Mapear error de negocio a respuesta HTTP clara para frontend.

### 4. Consumo de AP desde la fuente correcta en Competencia

- [ ] `src/competencia/domain/ports/performances_ap_port.py` (20 min)
  - Redefinir el puerto para obtener AP operativos desde inscripcion, no desde performances event-sourced.
- [ ] `src/competencia/infrastructure/repositories/performances_ap_adapter.py` o nuevo adapter ACL (35 min)
  - Leer AP desde `registro` usando la relacion torneo/competencia/disciplina.
  - Decidir compatibilidad para torneos ya preparados con datos historicos.
- [ ] `src/competencia/application/commands/generar_grilla.py` (20 min)
  - Mantener el contrato de negocio pero usando el origen nuevo de datos.

### 5. Frontend organizador

- [ ] `frontend/src/api/registro.ts` (20 min)
  - Agregar contrato para editar AP desde la vista de inscriptos.
- [ ] `frontend/src/components/organizador/InscriptosPanel.tsx` (35 min)
  - Habilitar visualizacion y edicion de AP por atleta y disciplina.
  - Refrescar estados luego de guardar.
- [ ] `frontend/src/components/organizador/TablaInscriptos.tsx` y relacionados (35 min)
  - Incorporar accion editable en `INSCRIPCION_ABIERTA`.
  - Mantener solo lectura fuera de esa fase y señalizar pendientes.
- [ ] `frontend/src/components/organizador/GrillaPanel.tsx` (20 min)
  - Comunicar que la grilla depende de AP completos y mostrar estado vacio mas informativo si falta preparacion.

### 6. Migracion y compatibilidad

- [ ] Resolver estrategia de fallback para datos historicos (25 min)
  - Si existen AP solo en `competencia`, decidir si se copian al leer, al cerrar o via migracion lazy.
  - Mantener operativos torneos ya preparados bajo el esquema anterior.

### 7. Tests

- [ ] `tests/unit/registro/` (30 min)
  - Cobertura de aggregate/VO/handler de AP en inscripcion.
- [ ] `tests/unit/torneo/` (20 min)
  - Cobertura del bloqueo de cierre de inscripcion por AP faltante.
- [ ] `tests/unit/competencia/` (20 min)
  - Ajustar tests de `GenerarGrillaHandler` al nuevo puerto/fuente.
- [ ] `tests/integration/registro/` (30 min)
  - Endpoint detalle + endpoint escritura AP + persistencia/migracion.
- [ ] `tests/integration/torneo/` o `tests/integration/app/` (25 min)
  - Cierre de inscripcion rechazado/aceptado segun completitud AP.
- [ ] `tests/features/steps/` (20 min)
  - Steps minimos o validacion manual si no conviene automatizar full BDD de UI.

### 8. Validacion

- [ ] Ejecutar pytest focalizado backend (15 min)
- [ ] Ejecutar `npm run build` y `npm run lint` en `frontend/` si el cambio toca React (15 min)
- [ ] Generar reporte de quality gates y documentacion final (15 min)

## Riesgos y decisiones a resolver en implementacion

- Si el frontend del atleta sigue declarando AP via `competencia`, habra que decidir si se migra tambien ese flujo en esta US o se deja un puente transitorio.
- Hay que evitar imports cruzados entre dominios; la validacion de cierre debe entrar por puerto/ACL o por wiring de capa de aplicacion.
- La migracion historica puede requerir fallback dual de lectura: primero `registro`, luego `competencia` si el torneo ya estaba preparado bajo el modelo anterior.

## Criterio de completitud

- `Inscriptos` lee y escribe AP desde `registro`.
- `cerrar-inscripcion` falla con mensaje claro cuando faltan AP.
- `generar-grilla` usa AP provenientes de inscripcion.
- Existe cobertura automatizada para backend y validacion del frontend.
