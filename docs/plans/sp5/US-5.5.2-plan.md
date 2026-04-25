# Plan de Implementación: US-5.5.2 — Vista del organizador con inscriptos y estado AP

**Patrón:** hexagonal-ddd-bc
**BC principal:** `registro` (backend) + `frontend`
**Estimación Total:** 1h 50min

---

## Componentes a Implementar

### 1. Query handler (Application Layer — BC Registro)

- [ ] `src/registro/application/queries/listar_inscriptos_detalle.py` (20 min)
  - `InscriptoDetalleDto`: dataclass con `inscripcion_id`, `atleta_id`, `nombre`, `apellido`, `categoria`, `club`, `disciplinas`, `estado`
  - `ListarInscriptosDetalleHandler`: recibe `InscripcionRepositoryPort` + `AtletaRepositoryPort`
  - Carga todas las inscripciones del torneo, filtra `estado == ACTIVA` en memoria
  - Para cada inscripción, busca el atleta por `atleta_id` — atleta no encontrado → skip con log

### 2. Endpoint REST (API Layer — BC Registro)

- [ ] Agregar schema `InscriptoDetalleResponse` en `src/registro/api/router.py` (10 min)
  - Pydantic BaseModel: `inscripcion_id`, `atleta_id`, `nombre`, `apellido`, `categoria`, `club`, `disciplinas`, `estado`
- [ ] Agregar endpoint `GET /torneos/{torneo_id}/inscriptos-detalle` en `src/registro/api/router.py` (10 min)
  - Auth: `OrganizadorDep` — responde 403 si rol != organizador
  - Instancia `ListarInscriptosDetalleHandler(_inscripcion_repo(), _repo())`
  - Serializa con `InscriptoDetalleResponse`

### 3. API client frontend

- [ ] `frontend/src/api/registro.ts` — agregar `InscriptoDetalleDto` + `listarInscriptosDetalle` (10 min)
  - Interface `InscriptoDetalleDto`: `inscripcion_id`, `atleta_id`, `nombre`, `apellido`, `categoria`, `club`, `disciplinas`, `estado`
  - Función `listarInscriptosDetalle(torneoId: string): Promise<InscriptoDetalleDto[]>`

### 4. Actualizar InscriptosPanel (Frontend)

- [ ] `frontend/src/components/organizador/InscriptosPanel.tsx` (20 min)
  - Reemplazar `listarInscriptos` + N×`fetchAtleta` por `listarInscriptosDetalle` (1 llamada)
  - Eliminar import de `fetchAtleta` si ya no se usa
  - Mantener lógica de cruce con grillas para estado AP (sin cambios)
  - `rows` se construye directamente desde `InscriptoDetalleDto` (nombre, apellido, categoria, club ya vienen del backend)

### 5. Tests unitarios

- [ ] `tests/unit/registro/test_listar_inscriptos_detalle.py` (20 min)
  - Handler devuelve solo inscripciones ACTIVAS
  - Handler enriquece con datos del atleta
  - Atleta no encontrado → inscripción skipeada (o error de integridad — decidir en impl.)
  - Torneo sin inscripciones activas → lista vacía

### 6. Tests de integración

- [ ] `tests/integration/registro/test_inscriptos_detalle_endpoint.py` (15 min)
  - 200 con inscripciones ACTIVAS enriquecidas
  - 200 con lista vacía si no hay inscripciones activas
  - CANCELADA no aparece en la respuesta
  - 403 con rol ATLETA

### 7. BDD Steps

- [ ] `tests/features/steps/US-5.5.2-vista-organizador-inscriptos-steps.py` (10 min)
  - Steps para los 4 escenarios del `.feature`

### 8. Validación

- [ ] Ejecutar tests + BDD (5 min)
- [ ] Quality gates: CodeGuard (5 min)

---

**Estado:** 0/12 tareas completadas
