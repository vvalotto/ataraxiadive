# Análisis de Infraestructura y Cross-BC — Cierre SP3

**Fecha:** 2026-04-02
**Alcance:** repositories/, event_store/, app.py, cross-BC imports

---

## Cross-BC imports — mapa completo

```
app.py (composition root — LEGÍTIMO):
  ← competencia.api.*, competencia.application.queries.*
  ← identidad.api.router
  ← registro.api.router
  ← resultados.api.router, resultados.application.commands.*, resultados.infrastructure.*
  ← torneo.api.*,torneo.infrastructure.*

competencia/api/router.py:
  ← identidad.api.dependencies (OrganizadorDep)               ⚠ VER ABAJO

registro/api/router.py:
  ← identidad.api.dependencies (AtletaDep, OrganizadorDep)    ⚠ VER ABAJO

torneo/api/router.py:
  ← identidad.api.dependencies (OrganizadorDep)               ⚠ VER ABAJO

resultados/infrastructure/repositories/disciplina_descriptor_adapter.py:
  ← competencia.domain.ports.disciplina_descriptor_port       ✅ VER ABAJO

resultados/infrastructure/repositories/resultados_competencia_adapter.py:
  ← competencia.domain.aggregates.performance (Performance)   ⚠ VER ABAJO
  ← competencia.domain.value_objects.estado_performance       ⚠ VER ABAJO
```

---

## Análisis de cada caso

### CASO 1 — Routers importan `identidad.api.dependencies`

**Archivos:** `competencia/api/router.py:67`, `registro/api/router.py:9`, `torneo/api/router.py:10`

**Import:** `from identidad.api.dependencies import OrganizadorDep, AtletaDep`

**Evaluación:** violación de la regla "no imports directos entre BCs".
La capa API de un BC no debería importar de la capa API de otro BC.

**Contexto práctico:** `OrganizadorDep` y `AtletaDep` son tipos `Annotated[dict, Depends(...)]` de FastAPI.
Moverlos a `shared/api/dependencies.py` resolvería la violación sin cambiar la lógica.

**Severidad:** 🟡 Moderada — funciona, pero viola la arquitectura formal.
**Impacto:** si `identidad.api.dependencies` cambia su firma, rompe 3 routers.

**Corrección sugerida (D-06-nuevo):** crear `shared/api/dependencies.py` como re-export de las deps de identidad,
o mover las deps directamente a shared si no tienen lógica específica del BC.

---

### CASO 2 — `disciplina_descriptor_adapter.py` importa de `competencia.domain.ports`

**Import:** `from competencia.domain.ports.disciplina_descriptor_port import DisciplinaDescriptorPort`

**Evaluación:** ✅ ACEPTABLE.
`competencia/domain/ports/disciplina_descriptor_port.py` importa desde `competencia.domain.value_objects.disciplina`
que a su vez es un re-export de `shared.domain.value_objects.disciplina`.
El port está en el BC correcto (Competencia define el contrato de descriptores de disciplina).
El adapter en Resultados implementa ese port — patrón ACL correcto.

**Sin acción requerida.**

---

### CASO 3 — `resultados_competencia_adapter.py` importa `Performance` del aggregate

**Imports:**
```python
from competencia.domain.aggregates.performance import Performance
from competencia.domain.value_objects.estado_performance import EstadoPerformance
```

**Evaluación:** ⚠ ACEPTADO COMO ACL, pero con deuda documentada.

El adaptador está documentado como "ACL que lee resultados de BC Competencia". En el patrón ACL,
el adaptador en la infraestructura del BC consumidor puede conocer el modelo del BC productor
para realizar la traducción.

Sin embargo, importar el *aggregate* (no solo VOs o eventos) es agresivo.
Una alternativa más limpia sería leer solo los domain events del event store y reconstruir
localmente sin usar la clase `Performance` — pero eso duplicaría lógica de replay.

**Decisión:** aceptar en SP3. Registrar como deuda D-07 para SP4 (separar replay en shared/).
La funcionalidad es correcta y está probada (756 tests passing).

---

## app.py — Composition Root

**FanOut: 10/7** — `app.py` importa de 5 BCs + shared. Es el composition root, este es su rol.

**LongMethod `build_app` (51/20):** ensambla todos los routers, suscripciones y políticas.
Ya identificado como D-05 en SP-ADJ-03 (dividir en funciones auxiliares por BC).

**LongMethod `_on_finalizacion` (34/20):** callback de política P-09 completa en una función.

**Candidato SP-ADJ-03:** D-05 — refactorizar `build_app` en helpers, mejorar legibilidad.

---

## Repositories — Análisis

### SQLiteTorneoRepository (nuevo SP3)
- FeatureEnvy 3/0 y 12/2 — repositorio que accede al aggregate Torneo: patrón esperado.
- LongMethod 34/20 — método de persistencia con múltiples columnas. Aceptable para CRUD.

### SQLiteInscripcionRepository / SQLiteAtletaRepository (nuevos SP3)
- FeatureEnvy moderado — patrón Repository.
- `sqlite_inscripcion_repository.py` FanOut 8/7 — importa varios tipos. Moderado.

### AndarivelesActivosAdapter (pre-existente)
- LongMethod 52/20 y 29/20 — adapters SQL complejos. Pre-existente, sin agravamiento.

### ResultadosCompetenciaAdapter
- LongMethod 46/20 — replica de eventos del event store. Verbosidad inherente al ES.

---

## SQLiteEventStore (shared/infrastructure)

5 LongMethod (22–30 líneas) — métodos SQL con queries complejas. Pre-existente, aceptado.
