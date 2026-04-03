# PLAN-SP-ADJ-03 — Sprint de Ajuste Post-SP3

| Campo | Valor |
|-------|-------|
| **Sprint** | SP-ADJ-03 |
| **Contexto** | Ajuste técnico post-SP3 (BL-003) |
| **Fuentes** | HITO-14, HITO-15 · DesignReviewer · Revisión SOLID · Revisión de consistencia SP3 |
| **Branch base** | `develop` (después de cerrar BL-003) |
| **Estado** | 🔄 En ejecucion — 5/8 US cerradas (`US-ADJ-3.1`, `3.6`, `3.4`, `3.8`, `3.2`) |

---

## Objetivo

Cerrar las debilidades de código identificadas durante SP3 a través de cuatro fuentes:
revisión DesignReviewer, análisis manual de aggregates/handlers/infra, revisión SOLID
de BCs nuevos, e HITOs 14 y 15.

El criterio para iniciar SP-ADJ-03 es que todos los incrementos de SP3 estén
mergeados en `develop` y BL-003 esté lista para taggear.

## Progreso

| US | Estado |
|----|--------|
| `US-ADJ-3.1` | ✅ Cerrada |
| `US-ADJ-3.6` | ✅ Cerrada |
| `US-ADJ-3.4` | ✅ Cerrada |
| `US-ADJ-3.8` | ✅ Cerrada |
| `US-ADJ-3.2` | ✅ Cerrada |
| `US-ADJ-3.3` | ⏳ Pendiente |
| `US-ADJ-3.7` | ⏳ Pendiente |
| `US-ADJ-3.5` | ⏳ Pendiente |

---

## US planificadas

### US-ADJ-3.1 — Extraer `GrillaDeSalida` VO + eliminar `_DISCIPLINAS_SP3`
**Prioridad: Alta**
**Capa:** `competencia/domain/`
**Issues:** ADJ-01 + SOLID-01
**Spec:** `docs/specs/sp-adj-03/US-ADJ-3.1.md`

`ajustar_grilla` en `Competencia` tiene 127 líneas. Extraer `GrillaDeSalida` como Value Object
reduce el método a ~50 líneas y baja WMC de 65 a ~34. Al mismo tiempo, eliminar
`_DISCIPLINAS_SP3` de `torneo/domain/aggregates/torneo.py` (líneas 38–44): es un hardcode
de sprint en el dominio, viola OCP.

**Ajuste de umbrales post-implementación:**
```toml
# pyproject.toml — bajar después de implementar US-ADJ-3.1
max_wmc = 45               # bajado de 65
max_god_object_lines = 420 # bajado de 540
```

---

### US-ADJ-3.2 — Extraer `TarjetaAsignacion` VO
**Prioridad: Media**
**Capa:** `competencia/domain/` + `competencia/application/`
**Issues:** ADJ-02
**Spec:** `docs/specs/sp-adj-03/US-ADJ-3.2.md`

`AsignarTarjetaHandler` tiene 46 líneas con data clumps (tarjeta, penalización, razón).
Extraer `TarjetaAsignacion` como VO lo reduce a ~20 líneas y hace explícito el concepto
en el Core Domain.

---

### US-ADJ-3.3 — Refactorizar `app.py` + constante event type
**Prioridad: Media**
**Capa:** `src/app.py` + `resultados/application/`
**Issues:** ADJ-03 + ADJ-04 + SOLID-04
**Spec:** `docs/specs/sp-adj-03/US-ADJ-3.3.md`

Tres problemas agrupados por capa:
- `build_app()` tiene 51 líneas — extraer helpers por BC (`_register_competencia`, `_register_torneo`, etc.)
- `_on_finalizacion` en `_p08_finalizacion.py` tiene 34 líneas — revisar si puede simplificarse
- Literal `"IntervaloOTConfigurado"` hardcodeado en `calcular_overall.py:76` — extraer como constante (OCP)

---

### US-ADJ-3.4 — Mover dependencias de Identidad a `shared/api/`
**Prioridad: Alta**
**Capa:** `*/api/` cross-BC
**Issues:** ADJ-05
**Spec:** `docs/specs/sp-adj-03/US-ADJ-3.4.md`

`competencia/api/router.py`, `registro/api/router.py` y `torneo/api/router.py` importan
`identidad.api.dependencies` directamente. Esto acopla 3 BCs a un BC concreto en capa `api/`.
Mover `OrganizadorDep`, `AtletaDep`, `JuezDep` a `shared/api/dependencies.py`.

---

### US-ADJ-3.5 — Limpiar imports cross-module en ports de Competencia
**Prioridad: Baja**
**Capa:** `competencia/domain/ports/`
**Issues:** ADJ-06
**Spec:** `docs/specs/sp-adj-03/US-ADJ-3.5.md`

`competencia/domain/ports/disciplina_descriptor_port.py` importa desde
`competencia.domain.value_objects.*` en lugar de `shared.domain.value_objects.*`.
Cambio cosmético, sin impacto funcional.

---

### US-ADJ-3.6 — `TokenServicePort` + `PasswordHashingPort` en Identidad
**Prioridad: Alta**
**Capa:** `identidad/domain/ports/` + `identidad/application/`
**Issues:** SOLID-02 + SOLID-03
**Spec:** `docs/specs/sp-adj-03/US-ADJ-3.6.md`

Dos violaciones DIP en Identidad:
- `application/` depende de `JWTService` (infraestructura concreta), no de un puerto
- `JWTService()` se instancia inline en `identidad/api/dependencies.py:15-16` por request

Crear `TokenServicePort` y `PasswordHashingPort` en `identidad/domain/ports/`.
`application/` depende de los puertos. La implementación concreta vive en
`identidad/infrastructure/` y se inyecta desde `app.py`.

---

### US-ADJ-3.7 — Proyección `competencias_por_torneo`
**Prioridad: Media**
**Capa:** `competencia/infrastructure/` + `competencia/application/queries/`
**Issues:** HITO-15 — acción pendiente marcada explícitamente
**Spec:** `docs/specs/sp-adj-03/US-ADJ-3.7.md`

`ObtenerCompetenciasPorTorneoHandler` carga todos los streams con prefijo `"competencia-"`
y filtra en memoria (O(n) donde n = total de competencias históricas en el sistema).
Para SP3 con datos de prueba es aceptable. En SP4 con torneos reales el volumen
lo va a justificar.

Materializar una tabla de proyección actualizada por evento:
```sql
CREATE TABLE competencias_por_torneo (
    competencia_id TEXT PRIMARY KEY,
    torneo_id      TEXT NOT NULL,
    disciplina     TEXT NOT NULL
);
-- Se actualiza al procesar cada IntervaloOTConfigurado con torneo_id
```

El handler pasa de O(n) a O(1). El projector corre de forma síncrona dentro del
command handler (patrón SP3, suficiente antes de SP4).

---

### US-ADJ-3.8 — Auditoría y corrección cross-BC en `resultados`
**Prioridad: Media-Alta**
**Capa:** `resultados/infrastructure/`
**Issues:** HITO-14 D-06
**Spec:** `docs/specs/sp-adj-03/US-ADJ-3.8.md`

`resultados/infrastructure/repositories/resultados_competencia_adapter.py` importa
tipos concretos del BC `competencia` directamente. La regla del proyecto prohíbe
imports directos entre BCs — la comunicación debe ir por puertos/ACLs.

Dos preguntas a responder antes de implementar:
1. ¿El adapter importa el aggregate concreto o solo un DTO/valor primitivo?
2. ¿Es un ACL legítimo (la infra del consumidor traduce) o una violación estructural?

**Acción:** auditar el adapter, clasificar cada import como `aceptable` / `temporal` /
`corregir`, y ejecutar la corrección si corresponde (crear contrato delgado de lectura
en `resultados/domain/ports/`).

---

## Priorización

| Prioridad | US | Razón |
|-----------|-----|-------|
| 1 (Alta) | US-ADJ-3.1 | WMC Competencia en límite + OCP violation en Torneo |
| 2 (Alta) | US-ADJ-3.6 | DIP violation: application depende de infra concreta |
| 3 (Alta) | US-ADJ-3.4 | 3 BCs acoplados a `identidad.api` directamente |
| 4 (Media-Alta) | US-ADJ-3.8 | Import cross-BC sin clasificar — riesgo de acoplamiento silencioso |
| 5 (Media) | US-ADJ-3.2 | Reduce complejidad de handler crítico del Core Domain |
| 6 (Media) | US-ADJ-3.3 | Legibilidad composition root + OCP en resultados |
| 7 (Media) | US-ADJ-3.7 | Proyección O(n) → O(1) — necesaria antes de SP4 |
| 8 (Baja) | US-ADJ-3.5 | Cosmético, sin impacto funcional |

---

## Secuencia recomendada

```
1. US-ADJ-3.1          ← domain/ Competencia + domain/ Torneo
2. US-ADJ-3.6          ← identidad/domain/ports/ + application/ (DIP)
3. US-ADJ-3.4          ← shared/api/ + routers cross-BC
4. US-ADJ-3.8          ← auditoría resultados/infrastructure/ (puede quedar en observación si es aceptable)
5. US-ADJ-3.2          ← domain/ Competencia (puede ir junto con 3.1 si hay capacidad)
6. US-ADJ-3.3          ← src/app.py + resultados/application/
7. US-ADJ-3.7          ← competencia/infrastructure/ + queries/
8. US-ADJ-3.5          ← competencia/domain/ports/ (cosmético)
```

---

## Descartado por ahora

- **D-01/D-07/D-08/D-09/D-10 (HITO-14):** documentales, tooling, metodología — fuera del scope
- **SOLID-05** (`registro/infrastructure/acl/sqlite_torneo_consulta.py:55` devuelve todas las disciplinas):
  LSP moderado — completar en SP4 cuando se defina la consulta real
- **D-04 (HITO-14)** (`/implement-us` no ajustado al proyecto): no prioritario hasta tener más evidencia de fricción sistemática

---

*Iniciado: 2026-03-31 — basado en HITO-14*
*Actualizado: 2026-04-01 — US-ADJ-3.1/3.2 post-análisis WMC*
*Actualizado: 2026-04-03 — avance de ejecucion: cerradas US-ADJ-3.1, 3.6, 3.4, 3.8 y 3.2*
