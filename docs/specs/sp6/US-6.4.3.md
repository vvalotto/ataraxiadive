# US-6.4.3: Corregir violación hexagonal D-05 — routers con imports cross-BC de infraestructura

**Estado**: `Done`
**Incremento**: INC-6.4 — Deuda Técnica Sistema
**Hallazgos**: ARCH-02 · AA-03
**Bounded Contexts**: `resultados` · `competencia` · `registro`
**Capas afectadas**:
- `resultados/api/router.py`
- `competencia/api/router.py`
- Aplicación/handlers afectados

---

## Descripción

Como **desarrollador manteniendo la arquitectura hexagonal**,
quiero **que los routers no importen infraestructura de otros BCs directamente**
para **respetar D-05 y evitar que el acoplamiento de infraestructura escale con cada BC que reutilice la misma dependencia**.

---

## Contexto de los Hallazgos

### ARCH-02 — Imports cross-BC de infraestructura en routers

**Violación 1 — `resultados/api/router.py`**

```python
# línea 25 — import directo de torneo/infrastructure desde resultados/api
from torneo.infrastructure.repositories.sqlite_torneo_repository import SQLiteTorneoRepository
```

El router de `resultados` instancia `SQLiteTorneoRepository` para inyectarla en `ExportarResultadosHandler`. El port `TorneoRepositoryPort` ya existe en `torneo/domain/ports/`.

**Violación 2 — `competencia/api/router.py`**

```python
# línea 167 — import directo de registro/infrastructure desde competencia/api
from registro.infrastructure.repositories.sqlite_inscripcion_repository import SQLiteInscripcionRepository
```

El router de `competencia` instancia `SQLiteInscripcionRepository` para construir `PerformancesAPAdapter`. El port `InscripcionRepositoryPort` ya existe en `registro/domain/ports/`.

### AA-03 — `registro` D=0.59 degradando

Tras INC-6.3 (RF-IN-05/06), el BC `registro` incorporó nuevas dependencias concretas (upload de archivos, `Path`, `UploadFile`) en el router y el repositorio. Esto eleva el fan-out de `registro/infrastructure/` y contribuye a aumentar D.

---

## Especificación

### Tarea 1 — Corregir violación en `resultados/api/router.py`

| | |
|---|---|
| **Precondición** | `router.py` importa `SQLiteTorneoRepository` y la instancia en `get_torneo_repository()` |
| **Postcondición** | `router.py` usa `TorneoRepositoryPort` (tipo abstracto) como tipo de inyección; la instancia concreta se construye en `app.py` |
| **Invariante** | El comportamiento del endpoint de exportación es idéntico |

```python
# resultados/api/router.py — reemplazar:
from torneo.infrastructure.repositories.sqlite_torneo_repository import SQLiteTorneoRepository

def get_torneo_repository() -> SQLiteTorneoRepository:
    return SQLiteTorneoRepository()

# por:
from torneo.domain.ports.torneo_repository_port import TorneoRepositoryPort

# Eliminar get_torneo_repository() del router.
# El tipo de la dependencia en el endpoint cambia a TorneoRepositoryPort.
```

En `app.py`, asegurar que la instancia concreta `SQLiteTorneoRepository()` se inyecta donde corresponde (composition root).

### Tarea 2 — Corregir violación en `competencia/api/router.py`

| | |
|---|---|
| **Precondición** | `router.py` importa `SQLiteInscripcionRepository` y la instancia directamente en `get_generar_grilla_handler()` |
| **Postcondición** | `PerformancesAPAdapter` recibe `InscripcionRepositoryPort` como tipo; la instancia concreta viene de `app.py` |
| **Invariante** | El flujo de generación de grilla (GenerarGrillaHandler → PerformancesAPAdapter) funciona igual |

```python
# competencia/api/router.py — reemplazar:
from registro.infrastructure.repositories.sqlite_inscripcion_repository import SQLiteInscripcionRepository

# en get_generar_grilla_handler():
PerformancesAPAdapter(
    event_store,
    SQLiteCompetenciasPorTorneo(),
    SQLiteInscripcionRepository(os.getenv("REGISTRO_DB_PATH", "data/registro.db")),
)

# por:
# El router NO importa SQLiteInscripcionRepository.
# Se recibe como dependencia inyectada (InscripcionRepositoryPort) desde app.py.
```

Si FastAPI Depends no permite inyectar el adapter ya construido limpiamente, mover la construcción de `PerformancesAPAdapter` al composition root (`app.py`) y exponerlo como singleton.

### Tarea 3 — Auditar y reducir D en `registro`

| | |
|---|---|
| **Precondición** | `registro` D=0.59 tras INC-6.3, tendencia ascendente |
| **Postcondición** | D de `registro` no aumenta respecto a BL-005; idealmente ≤ 0.59 |
| **Invariante** | La funcionalidad de upload (RF-IN-05/06) no se degrada |

Acciones:
1. Revisar `registro/api/router.py` — verificar que el upload de archivos no haya introducido imports de infraestructura de otros BCs
2. Verificar que `Path` y `UploadFile` (dependencias nuevas de INC-6.3) estén solo en el router/adapter, no propagadas al domain o application
3. Ejecutar DesignReviewer tras las correcciones y comparar D con BL-005

```bash
designreviewer src/ --config pyproject.toml 2>&1 | grep "registro"
```

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-6.4.3 — Routers sin imports cross-BC de infraestructura

  Scenario: resultados/api/router.py no importa torneo.infrastructure
    Given el archivo resultados/api/router.py tras esta US
    When se busca "from torneo.infrastructure" en el archivo
    Then no hay coincidencias

  Scenario: competencia/api/router.py no importa registro.infrastructure
    Given el archivo competencia/api/router.py tras esta US
    When se busca "from registro.infrastructure" en el archivo
    Then no hay coincidencias

  Scenario: Endpoint de exportación de resultados sigue funcionando
    Given un torneo con resultados calculados
    When se llama al endpoint de exportación
    Then retorna los resultados correctamente

  Scenario: Generación de grilla sigue funcionando
    Given una competencia con atletas inscritos y APs declarados
    When se genera la grilla
    Then la grilla refleja los APs correctamente

  Scenario: D de registro no aumenta respecto a BL-005
    Given los cambios de esta US aplicados
    When se ejecuta DesignReviewer
    Then D(registro) <= 0.59
```

---

## Notas de implementación

- La inyección en FastAPI con `Depends` puede usar una función lambda o un factory en `app.py` — revisar el patrón existente en `competencia/api/router.py` para otros adapters
- `TorneoRepositoryPort` ya tiene el método `find_by_id(UUID)` que usa `ExportarResultadosHandler` — verificar la firma antes de cambiar el tipo
- `InscripcionRepositoryPort` tiene `find_by_id` y `listar_por_atleta` — verificar qué métodos usa `PerformancesAPAdapter`
- El import `from competencia.infrastructure.repositories.sqlite_competencias_por_torneo import SQLiteCompetenciasPorTorneo` en `resultados/api/router.py` (línea 14) también puede ser una violación D-05 — evaluar si se puede reemplazar por el port `CompetenciasPorTorneoPort`

---

## Referencias

- Hallazgos: `docs/plans/sp6/PLAN-SP6.md` — ARCH-02 · AA-03
- Ports existentes: `src/torneo/domain/ports/torneo_repository_port.py` · `src/registro/domain/ports/inscripcion_repository_port.py`
- Routers afectados: `src/resultados/api/router.py` · `src/competencia/api/router.py`

---

*Redactado: 2026-05-09 — SP6 INC-6.4*
