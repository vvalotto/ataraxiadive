# Issues Consolidados — Revisión Cierre SP3
## Candidatos a SP-ADJ-03 y Cierre Formal

**Fecha:** 2026-04-02
**Fuente:** DesignReviewer + análisis manual + revisión de consistencia + ArchitectAnalyst

---

## Parte I — Issues de Código (SP-ADJ-03)

| ID | Área | Issue | Severidad | Origen |
|----|------|-------|-----------|--------|
| ADJ-01 | `competencia/domain/aggregates/competencia.py` | Extraer `GrillaDeSalida` VO — `ajustar_grilla` 127 líneas → ~50 | Alta | LongMethod DR + US-ADJ-3.1 pre-planificada |
| ADJ-02 | `competencia/domain/aggregates/competencia.py` | Extraer `TarjetaAsignacion` VO — reduce `AsignarTarjetaHandler` 46→~20 líneas | Media | LongMethod DR + US-ADJ-3.2 pre-planificada |
| ADJ-03 | `src/app.py` | Refactorizar `build_app()` (51 líneas) en helpers por BC | Media | LongMethod DR + D-05 pre-planificado |
| ADJ-04 | `src/app.py` + `competencia/application/_p08_finalizacion.py` | `_on_finalizacion` (34 líneas) — revisar si puede simplificarse | Baja | LongMethod DR |
| ADJ-05 | `competencia/api/router.py`, `registro/api/router.py`, `torneo/api/router.py` | Routers importan `identidad.api.dependencies` directamente — mover deps a `shared/api/` | Media | B-01 revisión consistencia |
| ADJ-06 | `competencia/domain/ports/disciplina_descriptor_port.py` | Imports de `competencia.domain.value_objects.*` → cambiar a `shared.domain.value_objects.*` | Baja | B-03 revisión consistencia |

---

## Parte II — Issues Documentales (cierre formal + post-cierre)

| ID | Área | Issue | Prioridad | Momento |
|----|------|-------|-----------|---------|
| D-01 | `CLAUDE.md §14` | Actualizar "Estado Actual" con SP3 completo y BCs nuevos | Alta | **Pre-tag** |
| D-02 | `CLAUDE.md §9` | Tabla baselines: SP3 a estado real | Alta | **Pre-tag** |
| D-03 | `docs/traceability/matrix.md` | 13 RFs SP3: `✅ definido` → `✅ implementado` | Alta | **Pre-tag** |
| D-04 | `.cm/baselines/BL-003.md` | Crear BL-003 con retrospectiva SP3 | Alta | **Cierre formal** |
| D-05 | `docs/design/domain-model.md §4, §5` | Actualizar notas ES Resultados/Registro | Baja | Post-tag |
| D-06 | `docs/design/context-map.md` | Actualizar Torneo con detalle actual | Baja | Post-tag |
| D-07 | `docs/contexto/INDICE-HITOS.md` | Evaluar HITO-17 para hipótesis human-in-the-loop | Baja | Post-tag |
| D-08 | `pyproject.toml` comentarios | Agregar nota de confirmación SP3 en thresholds | Baja | Post-tag |
| D-09 | `memory/project_sp_adj_03_pendiente.md` | Actualizar con ADJ-05 y D-07 nuevos | Media | Pre-SP-ADJ-03 |

---

## Issues adicionales — Revisión SOLID

| ID | Área | Issue | Severidad | Principio |
|----|------|-------|-----------|-----------|
| SOLID-01 | `torneo/domain/aggregates/torneo.py:38-44` | Eliminar `_DISCIPLINAS_SP3` — hardcode de sprint en dominio | Alta | OCP |
| SOLID-02 | `identidad/domain/ports/` (nuevo) | Crear `TokenServicePort` + `PasswordHashingPort` — application depende de `JWTService` y `bcrypt` concretos | Alta | DIP |
| SOLID-03 | `identidad/api/dependencies.py:15-16` | `JWTService()` instanciado inline por request | Media | DIP |
| SOLID-04 | `resultados/application/commands/calcular_overall.py:76` | Literal `"IntervaloOTConfigurado"` hardcodeado | Baja | OCP |
| SOLID-05 | `registro/infrastructure/acl/sqlite_torneo_consulta.py:55` | `obtener_disciplinas` devuelve todas las disciplinas (incumple contrato) | Media | LSP — completar en SP4 |

---

## Agrupación en US-IEDD para SP-ADJ-03

| US | Issues | Descripción | Capa |
|----|--------|-------------|------|
| US-ADJ-3.1 | ADJ-01 + SOLID-01 | Extraer `GrillaDeSalida` VO + eliminar `_DISCIPLINAS_SP3` de `Torneo` | domain/ |
| US-ADJ-3.2 | ADJ-02 | Extraer `TarjetaAsignacion` VO — reducir `AsignarTarjetaHandler` | domain/ + application/ |
| US-ADJ-3.3 | ADJ-03 + ADJ-04 + SOLID-04 | Refactorizar `app.py` + constante event type en `calcular_overall.py` | src/ + resultados/application/ |
| US-ADJ-3.4 | ADJ-05 | Mover `OrganizadorDep/AtletaDep/JuezDep` a `shared/api/dependencies.py` | api/ cross-BC |
| US-ADJ-3.5 | ADJ-06 | Limpiar imports `competencia.domain.value_objects.*` → `shared.domain.*` en ports | domain/ports/ |
| US-ADJ-3.6 | SOLID-02 + SOLID-03 | `TokenServicePort` + `PasswordHashingPort` en Identidad | identidad/domain/ports/ + application/ |

**Criterio de agrupación:** misma capa arquitectural + pueden testearse sin interferencia entre sí.

---

## Priorización SP-ADJ-03

| Prioridad | US | Razón |
|-----------|-----|-------|
| 1 (ALTA) | US-ADJ-3.1 | WMC Competencia en límite umbral 65 + OCP violation `_DISCIPLINAS_SP3` |
| 2 (ALTA) | US-ADJ-3.6 | DIP violation en Identidad: application depende de infra concreta |
| 3 (ALTA) | US-ADJ-3.4 | 3 BCs acoplados a `identidad.api` directamente |
| 4 (MEDIA) | US-ADJ-3.2 | Reduce complejidad de handler crítico del Core Domain |
| 5 (MEDIA) | US-ADJ-3.3 | Legibilidad composition root + OCP en resultados |
| 6 (BAJA) | US-ADJ-3.5 | Cosmético, sin impacto funcional |

---

## Comparación SP-ADJ-02 vs SP-ADJ-03

| Aspecto | SP-ADJ-02 | SP-ADJ-03 |
|---------|-----------|-----------|
| Issues críticos de código | 3 (B-01, B-02, B-05) | 2 (SOLID-01, SOLID-02) |
| Issues moderados de código | 2 | 4 (B-01, SOLID-03, SOLID-05, ADJ-03) |
| US planificadas | 3 (ADJ-2.6, 2.7, 2.8) | 5 (ADJ-3.1..3.5) |
| Issues documentales | 6 críticos+moderados | 2 críticos (ambos documentales) |
| Bloqueantes para tag | Sí (violaciones arquitecturales) | No |

**Conclusión:** SP-ADJ-03 es menos urgente que SP-ADJ-02. Puede ejecutarse post-tag sin riesgo.
La única excepción es US-ADJ-3.1 (WMC) que conviene hacer antes de que SP4 sume métodos a Competencia.

---

*Creado: 2026-04-02 — Issues consolidados pre-BL-003*
