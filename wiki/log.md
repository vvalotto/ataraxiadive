# Wiki Log — AtaraxiaDive

> Registro cronológico append-only de todas las operaciones del wiki.
> Formato de entrada: `## [YYYY-MM-DD] <tipo> | <descripción>`
> Tipos: ingest | query | lint | init

---

## [2026-05-23] ingest | Fase C plan-trazabilidad-rf-us-si-tu — us_refs: en 8 páginas RF

Script: `poblar_us_refs.py`
Archivos modificados: 8 (`wiki/trazabilidad/RF-*.md`)

- type: trazabilidad → trazabilidad-rf en los 8 archivos
- 7 archivos con us_refs: [...] (total 77 referencias RF→US)
- 1 archivo con us_refs: [] (RF-integracion — sus RF-IG-* no son referenciados por ninguna US)
- Script idempotente: reejecutar → SKIP si ya tiene us_refs:

---

## [2026-05-23] ingest | Schema extendido — campo origen en trazabilidad-us

Archivos actualizados: 2 (`WIKI.md`, `wiki/planes/plan-trazabilidad-rf-us-si-tu.md`)

Motivación: rf: [] no implica que la US carezca de origen — implica que su origen no es
un RF de la elicitación inicial. Para trazabilidad completa (contexto IEDD / IEC 62304),
toda US cerrada debe tener un origen registrado.

Nuevos campos en trazabilidad-us:
  - origen_tipo: rf | adr | calidad | plataforma | setup
  - origen_refs: [ADR-NNN | BL-NNN] (omitido si origen_tipo = rf)

Convención: US con rf: [...] no vacío → origen_tipo: rf automático.
US con rf: [] → origen_tipo debe ser adr | calidad | plataforma | setup + origen_refs cuando aplica.

Fase D actualizada: poblar origen_tipo + origen_refs junto con software_items y test_units.
Fase E actualizada: query de distribución por origen + gap de origen_tipo = null.

---

## [2026-05-23] ingest | Fase B plan-trazabilidad-rf-us-si-tu — campo rf: en 177 US

Script: `poblar_rf.py`
Archivos modificados: 177 (`wiki/trazabilidad/US-*.md`)

- 42 US recibieron `rf: [RF-XX-NN, ...]` (RFs extraídos del body)
- 135 US recibieron `rf: []` (sin RFs en el body: US de setup, ADJs técnicos, SP4+)
- Script idempotente: reejecutar sobre archivos ya procesados → SKIP

---

## [2026-05-23] ingest | Fase A plan-trazabilidad-rf-us-si-tu — schema extendido trazabilidad

Archivos actualizados: 1 (`WIKI.md`)

Cambios:
- `type` enum extendido con `trazabilidad-us` y `trazabilidad-rf` (ya existían en páginas, ahora formalizados en schema)
- Tabla de tipos: agregado `trazabilidad-rf` con ubicación `wiki/trazabilidad/RF-*.md`
- Frontmatter `trazabilidad-us` ampliado con 3 nuevos campos opcionales:
  · `rf: [RF-XX-NN, ...]` — RFs que implementa la US
  · `software_items: [path, ...]` — artefactos de código
  · `test_units: [path, ...]` — tests que verifican la US
- Nuevo bloque `trazabilidad-rf`: campo `us_refs: [US-X.Y.Z, ...]`

---

## [2026-05-23] ingest | Fase D plan-c4-nivel3 — cross-referencias impacto → componentes C4 L3

Páginas actualizadas: 4 en `wiki/impacto/`

| Página | Componentes C4 L3 agregados |
|--------|---------------------------|
| `event-store-port.md` | `[[arquitectura/competencia/event-store-port]]` · `[[arquitectura/notificaciones/sqlite-notificacion-event-store]]` |
| `atleta-nombre-port.md` | `[[arquitectura/competencia/atleta-nombre-port]]` · `[[arquitectura/resultados/resultados-competencia-port]]` · `[[arquitectura/registro/sqlite-repositories]]` |
| `bc-identidad.md` | `[[arquitectura/identidad/router-identidad]]` · `[[arquitectura/identidad/jwt-service]]` · `[[arquitectura/identidad/command-handlers-identidad]]` · `[[arquitectura/identidad/sqlite-usuario-repository]]` |
| `categoria-shared.md` | `[[arquitectura/resultados/resultados-competencia-port]]` · `[[arquitectura/resultados/algoritmo-faas]]` · `[[arquitectura/registro/sqlite-repositories]]` · `[[arquitectura/registro/command-handlers]]` |

---

## [2026-05-23] ingest | Fase C plan-c4-nivel3 — vista arquitectura C4 L2+L3

Páginas creadas: 1 (`wiki/vistas/arquitectura.md`)
Páginas actualizadas: 1 (`wiki/index.md`)

Queries Dataview incluidas: C4 L2 (BCs), C4 L3 por BC (6 tablas), componentes por tipo, ports, tabla global. Preguntas características con recorridos de navegación para 6 escenarios clave.

---

## [2026-05-23] ingest | Fase B6 plan-c4-nivel3 — componentes C4 L3 BC Notificaciones

Páginas creadas: 3 en `wiki/arquitectura/notificaciones/`
Páginas actualizadas: 2 (`wiki/arquitectura/notificaciones.md` + `wiki/index.md`)

| Componente | Tipo | Capa |
|-----------|------|------|
| `notificacion-aggregate` | aggregate (ES) | domain |
| `sqlite-notificacion-event-store` | event-store + adapters | infrastructure |
| `command-handlers-notificaciones` | handlers + políticas | application |

Componentes totales documentados: **41 / ~47**

---

## [2026-05-23] ingest | Fase B5 plan-c4-nivel3 — componentes C4 L3 BC Identidad

Páginas creadas: 5 en `wiki/arquitectura/identidad/`
Páginas actualizadas: 2 (`wiki/arquitectura/identidad.md` + `wiki/index.md`)

| Componente | Tipo | Capa |
|-----------|------|------|
| `usuario-aggregate` | aggregate | domain |
| `jwt-service` | adapter ×2 (JWT + bcrypt) | infrastructure |
| `sqlite-usuario-repository` | repository | infrastructure |
| `command-handlers-identidad` | handler ×5 | application |
| `router-identidad` | router + dependencies | api |

---

## [2026-05-23] ingest | Fase B4 plan-c4-nivel3 — componentes C4 L3 BC Resultados

Páginas creadas: 7 en `wiki/arquitectura/resultados/`
Páginas actualizadas: 2 (`wiki/arquitectura/resultados.md` + `wiki/index.md`)

| Componente | Tipo | Capa |
|-----------|------|------|
| `ranking-competencia` | aggregate (ES) | domain |
| `ranking-overall` | aggregate (ES) | domain |
| `resultados-competencia-port` | port + adapters ×2 | domain / infrastructure |
| `algoritmo-faas` | service | domain |
| `command-handlers-resultados` | handler ×2 | application |
| `query-handlers-resultados` | handler ×4 | application |
| `router-resultados` | router | api |

---

## [2026-05-23] ingest | Fase B3 plan-c4-nivel3 — componentes C4 L3 BC Torneo

Páginas creadas: 5 en `wiki/arquitectura/torneo/`
Páginas actualizadas: 2 (`wiki/arquitectura/bc-torneo.md` + `wiki/index.md`)

| Componente | Tipo | Capa |
|-----------|------|------|
| `torneo-aggregate` | aggregate | domain |
| `sqlite-torneo-repository` | repository | infrastructure |
| `command-handlers-torneo` | handler ×9 | application |
| `query-handlers-torneo` | handler ×3 | application |
| `router-torneo` | router | api |

---

## [2026-05-23] ingest | Fase B2 plan-c4-nivel3 — componentes C4 L3 BC Registro

Páginas creadas: 9 en `wiki/arquitectura/registro/`
Páginas actualizadas: 2 (`wiki/arquitectura/registro.md` + `wiki/index.md`)

| Componente | Tipo | Capa |
|-----------|------|------|
| `atleta` | aggregate | domain |
| `inscripcion` | aggregate | domain |
| `juez-organizador` | aggregate | domain |
| `torneo-consulta-port` | port + adapter (ACL) | domain / infrastructure |
| `sqlite-repositories-registro` | repository ×4 | infrastructure |
| `perfil-registro-adapter` | adapter | infrastructure |
| `command-handlers-registro` | handler ×10 | application |
| `query-handlers-registro` | handler ×5 | application |
| `router-registro` | router | api |

---

## [2026-05-23] ingest | Fase B1 plan-c4-nivel3 — componentes C4 L3 BC Competencia

Páginas creadas: 12 en `wiki/arquitectura/competencia/`
Página actualizada: `wiki/arquitectura/competencia.md` (campo `componentes:`)

| Componente | Tipo | Capa |
|-----------|------|------|
| `competencia-aggregate` | aggregate | domain |
| `performance-aggregate` | aggregate | domain |
| `grilla-de-salida` | aggregate (entidad interna) | domain |
| `event-store-port` | port | domain |
| `atleta-nombre-port` | port | domain |
| `performances-ap-port` | port | domain |
| `calculador-hash-competencia` | service | domain |
| `sqlite-event-store` | adapter | infrastructure |
| `handler-utils` | service | application |
| `command-handlers` | handler | application |
| `query-handlers` | handler | application |
| `router-competencia` | router | api |

---

## [2026-05-23] schema | Fase A plan-c4-nivel3 — tipo arquitectura-componente + estructura C4 L3

Páginas actualizadas: 2 (WIKI.md + wiki/index.md)

- `WIKI.md` — nueva estructura de carpetas con `wiki/arquitectura/<bc>/`; nuevo tipo `arquitectura-componente` con frontmatter (bc, capa, tipo_componente, responsabilidad, interfaces_out, adr_refs); campo `componentes:[]` agregado al tipo `arquitectura`; nueva vista `arquitectura` en tabla de vistas; tipo `plan` declarado
- `wiki/index.md` — sección Vistas actualizada con entrada `[[arquitectura]]`; nueva sección Planes con `[[plan-c4-nivel3]]` y `[[plan-trazabilidad-rf-us-si-tu]]`; total de páginas: 238

---

## [2026-05-22] ingest | L3+L4 lint-001 — RFs pendientes clasificados + cobertura BC enriquecida

Páginas actualizadas: 7 (4 RF + 3 BC)

**L3 — RFs pendientes clasificados:**
- `RF-inscripcion-atletas.md` — RF-IN-07 marcado como Indefinido (depende de RF-IG)
- `RF-ejecucion.md` — RF-EJ-04 marcado como Backlog activo (infraestructura lista, faltan códigos config)
- `RF-resultados.md` — RF-PM-01 marcado como Backlog activo (AlgoritmoPuntaje implementado pero no integrado)
- `RF-notificaciones.md` — RF-NT-03 marcado como Backlog activo (P-10/P-11 existen; falta PushAdapter + triggers)

**L4 — Cobertura BC enriquecida:**
- `wiki/arquitectura/torneo.md` — flows UAT F-02/F-05/F-10; nota % pendiente `pytest --cov`
- `wiki/arquitectura/identidad.md` — flows UAT F-01 + cross-cutting; tendencia D positiva documentada
- `wiki/arquitectura/notificaciones.md` — flows UAT F-04/F-09; nota LoggingEmailAdapter para tests sin Resend

---

## [2026-05-22] ingest | L6 lint-001 — 7 conceptos de dominio sin página (resolución de gap menor)

Páginas creadas: 7 | Páginas actualizadas: 1 (index.md)

**Conceptos creados:**
- `wiki/conceptos/inscripcion.md` — aggregate de BC Registro; estados ACTIVA/CANCELADA; invariantes de unicidad y ventana de inscripción
- `wiki/conceptos/categoria.md` — StrEnum en shared/ (ADR-022); usado por Registro, Competencia y Resultados
- `wiki/conceptos/penalizacion.md` — infracción técnica; modelo rp_medido/rp_penalizado; BlancaConPenalizaciones (ADR-014)
- `wiki/conceptos/ranking.md` — dos tipos (competencia + overall); reglas de ordenamiento; separación cálculo/lectura
- `wiki/conceptos/dns.md` — Did Not Start; evento terminal de Performance; posición al final sin número
- `wiki/conceptos/sede.md` — value object embebido en Torneo; nombre, ciudad, país
- `wiki/conceptos/entidad-organizadora.md` — organismo institucional del torneo; distinción con rol Organizador

---

## [2026-05-22] lint | lint-001 — Primera auditoría del wiki (Fase 4)

Páginas auditadas: 232 | Hallazgos: 8 categorías

**Resultados:**
- L1 (PostgreSQL vigente): ✅ LIMPIO
- L2 (ADRs contradictorios): ✅ LIMPIO
- L3 (RFs sin US): 🟡 8 RFs pendientes (4 backlog real + 4 integración indefinida)
- L4 (BCs sin cobertura numérica): 🟡 torneo/identidad/notificaciones solo tienen cobertura en prosa
- L5 (impacto vacío): 🔴 wiki/impacto/ tiene 0 páginas — prioridad 1
- L6 (conceptos sin página): 🟡 7 conceptos (inscripcion y categoria, prioritarios)
- L7 (páginas huérfanas): 🟡 14 páginas sin wikilink en index (SP6-INC-6.6, SP-ADJ-10, SP7, proyecto)
- L8 (inconsistencias estructurales): 🔴 directorio arquitectura/ vs bounded-contexts/ + index desactualizado

**Páginas creadas:** `wiki/salud/lint-001.md`

---

## [2026-05-21] ingest | Fase 3 — snapshot de calidad BL-006 (wiki/salud/)

Páginas creadas: 1

- `wiki/salud/calidad-BL-006.md` — síntesis de los 3 quality gates al cierre de SP6/v1.0.0
  - DesignReviewer: 0 CRITICAL · 287 WARNING · evolución BL-002→BL-006
  - ArchitectAnalyst: 3 CRITICAL (Zone of Pain) · 62 WARNING (falsos positivos hexagonales) · D por BC
  - UAT: 10/10 flows PASS (F-09/F-10 con waiver)
  - Decisiones de aceptación de deuda: DR-01, AA-02, AA-04, ARCH-03, ADP-01

---

## [2026-05-21] ingest | Fase 3 — métricas de salud en páginas de BC (quality/reports/)

Páginas actualizadas: 6

**Sección `## Salud` agregada a:**
- `wiki/arquitectura/competencia.md` — D=0.459 WARNING · 130W (LongMethod/FeatureEnvy) · DependencyCycle aceptado
- `wiki/arquitectura/torneo.md` — D=0.479 WARNING · 15W (FeatureEnvy/LongMethod)
- `wiki/arquitectura/registro.md` — D=0.583 CRITICAL↑ · 37W (LongMethod/FeatureEnvy) · degradación por SP-ADJ-11
- `wiki/arquitectura/resultados.md` — D < umbral alerta · 40W (LongMethod) · DR-01 aceptado
- `wiki/arquitectura/identidad.md` — D=0.652 CRITICAL↓ · 21W (LongMethod/FeatureEnvy) · AA-02 diferido
- `wiki/arquitectura/notificaciones.md` — D=0.450 WARNING · 18W (LongMethod/FeatureEnvy)

**Fuentes:** `quality/reports/architectanalyst/BL-005-report.json` · `.cm/baselines/BL-006-report.json` · `quality/reports/designreviewer/current-report.json` (2026-05-18, 287W total)

---

## [2026-05-21] ingest | Fase 3 — estado del proyecto (baselines BL-000..BL-006)

Páginas creadas: 1

**Página creada:**
- `wiki/estado/proyecto.md` — síntesis de los 7 baselines cerrados (BL-000 a BL-006) + SP7 en curso

**Contenido sintetizado:**
- Situación actual: BL-006 vigente · v1.0.0 · 2026-05-16 · SP7 en curso
- Historia de todos los baselines con métricas: tests, DesignReviewer, ArchitectAnalyst
- Estado de BCs con valores D de DistanceAnalyzer al cierre de SP6
- Evolución DesignReviewer (0 CRITICAL en todos los SPs)
- UAT por SP (SP1–SP6)
- Cobertura RF por área
- Deuda técnica conocida post-v1.0.0
- Progreso SP7: US-7.1.1 ✅ · US-7.1.2 y US-7.2.x ⏳

**Solución a D-02** (múltiples fuentes de verdad para el estado del proyecto): esta página unifica en un único documento navegable el estado que antes estaba disperso en README, CLAUDE.md, matrix.md, planes y reportes.

---

## [2026-05-21] ingest | Fase 3 — páginas US SP7 (INC-7.1 + INC-7.2)

Páginas creadas: 5

**Páginas creadas (wiki/trazabilidad/):**

*INC-7.1 — Despliegue en Fly.io (2 US):*
- `US-7.1.1` — Dockerfile multi-stage + fly.toml + FastAPI estáticos + ADR-021 ✅ completada 2026-05-17
- `US-7.1.2` — `fly deploy` + verificación flujos críticos + tag `v1.0.1` ⏳ planificada

*INC-7.2 — Manual de Usuario (3 US):*
- `US-7.2.1` — Manual organizador ⏳ planificada
- `US-7.2.2` — Manual juez ⏳ planificada
- `US-7.2.3` — Manual atleta ⏳ planificada

**Estado del wiki:** SP7 ingresado. US-7.1.1 completada; US-7.1.2 y US-7.2.x pendientes de implementación. Fase 3 completa (SP1–SP7 + SP-ADJ-01 a SP-ADJ-11). Próximo: Fase 4 (primer lint) o actualizar páginas SP7 cuando se completen INC-7.1.2 e INC-7.2.

---

## [2026-05-21] ingest | Fase 3 — páginas US SP6 completo (INC-6.1 a INC-6.4 + SP-ADJ-11)

Páginas creadas: 29

**Páginas creadas (wiki/trazabilidad/):**

*INC-6.1 — Ajustes Juez (5 US):*
- `US-6.1.1` — fix `canSubmitBko` + reorden flujo juez (tarjeta → marca)
- `US-6.1.2` — colores tarjeta outline/filled + heading corregido
- `US-6.1.3` — grilla ordenada por estado + keypad visible móvil
- `US-6.1.4` — rediseño inicio juez + STA mm:ss + tarjeta amarilla
- `US-6.1.5` — `AtletaCard` variante compact en paso de RpSelector

*INC-6.2 — Ajustes Organizador (6 US):*
- `US-6.2.1` a `US-6.2.6` — torneos por fecha, categoría legible, resultados sin PTS, alertas, grupos etarios, PodiosPage

*INC-6.3 — Ajustes Atleta (2 US):*
- `US-6.3.1` — inicio atleta: indicador En línea + disciplinas por OT
- `US-6.3.2` — inscripción: AP inline + apto médico + constancia de pago

*INC-6.4 — Deuda Técnica Sistema (6 US):*
- `US-6.4.1` — romper ciclo ADP en `competencia/domain/aggregates` (AA-01 CRITICAL)
- `US-6.4.2` — proyección `competencias_por_torneo` materializada (ARCH-01)
- `US-6.4.3` — corregir imports cross-BC en `resultados/api` y `competencia/api`
- `US-6.4.4` — `AlgoritmoPuntajeFAAS` dispatch explícito + CodeGuard
- `US-6.4.5` — `DeclararAPInscripcionHandler` + `from_row()` refactoring
- `US-6.4.6` — cierre ARCH-03 + SRP `RankingCompetencia` + BL-006

*SP-ADJ-11 — Modelo multi-rol (10 US):*
- `US-ADJ-11.1` a `US-ADJ-11.10` — `Usuario.roles: list[Rol]`, JWT `rol_activo`, login condicional, entidades `Juez`/`Organizador` en BC Registro, frontend multi-rol, creación automática de perfiles

**Hito DesignReviewer SP6:** Post-INC-6.4: 0 CRITICAL · 253 WARNING (−5 por refactoring). Post-SP-ADJ-11: 0 CRITICAL · 287 WARNING (+34, complejidad multi-rol).

**Estado del wiki:** SP6 + SP-ADJ-11 completos. Próximo: SP7 y SP-ADJ-10.

---

## [2026-05-21] ingest | Fase 3 — páginas US SP5 (INC-5.1 a INC-5.7 + SP-ADJ-08 y SP-ADJ-09)

Páginas creadas: 39

**Páginas creadas (wiki/trazabilidad/):**

*INC-5.1 — Panel del Organizador (6 US + 4 ADJ post-UAT):*
- `US-5.1.1` a `US-5.1.6` — `CrearTorneoPage`, `DetalleTorneoPage` + tabs, `InscriptosPanel`, `GrillaPanel`, `JuecesPanel`, `EjecucionPanel`
- `US-5.1.7` a `US-5.1.10` — ajustes post-UAT: política de tabs por fase, `TorneoCompetenciasPage` composición, precondición grilla para juez, normalización `estado` en `fetchTorneo`

*INC-5.2 — Ejecución por Disciplina (2 US):*
- `US-5.2.1` — maestro-detalle por disciplina con `Habilitar disciplina`
- `US-5.2.2` — acción `Finalizar prueba` con distinción cierre manual/automático

*SP-ADJ-08 — Ajuste post-UAT INC-5.2 (3 US):*
- `US-ADJ-8.1` a `US-ADJ-8.3` — UX paneles, selector grilla filtrado, cancelar torneo con confirmación fuerte

*INC-5.3 — Gestión de Usuarios (2 US):*
- `US-5.3.1` — `UsuariosPage` organizador
- `US-5.3.2` — `AtletaDashboardPage` con inscripción

*INC-5.4 — Identidad Extendida (3 US):*
- `US-5.4.1` — auto-registro público
- `US-5.4.2` — cambiar contraseña
- `US-5.4.3` — recuperar contraseña vía JWT

*INC-5.5 — Portal Atleta e Inscripción con AP (2 US):*
- `US-5.5.1` — portal atleta completo: shell dark + wizard inscripción 3 pasos + AP
- `US-5.5.2` — vista organizador: inscriptos con datos completos

*INC-5.6 — Algoritmo de Puntaje y Rankings (6 US):*
- `US-5.6.1` a `US-5.6.6` — puerto `AlgoritmoPuntaje`, `TipoReglamento`, `RankingCompetencia` con puntos, `RankingOverall`, `ResultadosPage`, podios por división

*SP-ADJ-09 — Refactoring UX Organizador (7 US):*
- `US-ADJ-9.1` a `US-ADJ-9.7` — shell dark organizador, routing reestructurado, home, dashboard operativo, `ResultadosPage` integrada, arquitectura UX formalizada, declarar AP en wizard

*INC-5.7 — Portal del Atleta (4 US):*
- `US-5.7.1` a `US-5.7.4` — Mis torneos, Mi grilla, Mis resultados, Rankings y podios

**Hitos DesignReviewer acumulados a fin de SP5:**
- Post-INC-5.1: 0 CRITICAL · 208 WARNING
- Post-INC-5.2: 0 CRITICAL · 215 WARNING
- Post-INC-5.3: 0 CRITICAL · 215 WARNING
- Post-INC-5.4: 0 CRITICAL · 222 WARNING (+7 endpoints identidad)
- Post-INC-5.5: 0 CRITICAL · 227 WARNING (+5 LongMethod/DataClumps/LCOM)
- Post-INC-5.6 + SP-ADJ-09: 0 CRITICAL · 252 WARNING (+25 LCOM/FanOut ranking)
- Post-INC-5.7: 0 CRITICAL · 256 WARNING (+4 `_rankear_categoria` aceptado)

**Estado del wiki:** SP5 completo. Próximo: SP6 (INC-6.1 a INC-6.4) + SP-ADJ-11.

---

## [2026-05-21] vistas | Fase 2 — 6 vistas operativas construidas

Páginas actualizadas: 6

**Vistas completadas (wiki/vistas/):**
- `dominio.md` — 6 preguntas + recorridos + tabla de BCs + glosario del lenguaje ubicuo
- `decisiones.md` — 7 preguntas + tabla de ADRs por área + ADR-010 supersedido documentado
- `trazabilidad.md` — 7 preguntas + tabla de pendientes RF + mapa RF→BC + remisión a matrix.md
- `salud.md` — 7 preguntas + tabla D-02/D-03/D-05/D-06/D-09 + instrucción para primer lint
- `impacto.md` — 7 preguntas + mapa de dependencias reales + tabla de interfaces críticas
- `investigacion.md` — 7 preguntas + HITOs para el paper + capitalización por producto intelectual

**Estado del wiki:** H-2 completado. Próximo paso: Fase 3 (ingest de estado).

---

## [2026-05-20] ingest | docs/contexto/ (ANALISIS-*.md, INDICE-HITOS.md, PLAN-EXPERIMENTO.md)

Páginas creadas: 2 | Páginas actualizadas: 1

**Páginas creadas (wiki/investigacion/):**
- `hitos-catalog.md` — catálogo de los 32 HITOs; tabla por SP; agrupación por tema (ecosistema, DDD/ES, calidad, validación, arquitectura emergente)
- `experimento-plan.md` — el objetivo real del experimento (no construir software sino demostrar factibilidad empírica); 3 horizontes; jerarquía de trabajo; tabla de capitalización de conocimiento

**Página enriquecida:**
- `iedd-hipotesis-experimento.md` — tabla completa de 22 hipótesis con estado (✅/🔄) y HITOs de evidencia; links a nuevas páginas

**Hallazgo:** 20 hipótesis confirmadas de 22 a mayo 2026 (SP6 en curso). Las dos en evaluación son las más amplias: RQ1 (fricción de coordinación) y RQ2 (IEDD mejora calidad de specs).

---

## [2026-05-20] ingest | docs/architecture/ (14 archivos)

Páginas creadas: 7 | Páginas actualizadas: 0

**Páginas creadas (wiki/arquitectura/):**
- `context-map.md` — 6 BCs, 11 integraciones, principios de cruce de fronteras, tabla resumen
- `competencia.md` — Core Domain; ES; aggregates Competencia y Performance; integración Registro/Resultados/Notificaciones
- `torneo.md` — Supporting; CRUD; máquina de estados EstadoTorneo (7 estados); integración Registro/Resultados/Notificaciones
- `registro.md` — Supporting; CRUD; aggregates Atleta e Inscripcion; ACL read-only a Torneo; upstream de Competencia
- `resultados.md` — Supporting; stream propio; RankingCompetencia; deuda técnica cross-BC (ranking provisional)
- `identidad.md` — Generic; CRUD; JWT cross-cutting; multi-rol desde ADR-020; política contraseñas ADR-019
- `notificaciones.md` — Generic; ES por idempotencia; P-10 y P-11 implementadas; ResendEmailAdapter + LoggingEmailAdapter

**Hallazgo:** Resultados usa Event Sourcing (stream propio) aunque clasificado como CRUD en diseño general.
**Deuda técnica documentada:** `ObtenerRankingProvisionalHandler` lee `competencia.db` directamente — lectura cross-BC fuera de ACL formal.

---

## [2026-05-20] ingest | docs/adr/ (22 archivos — ADR-001 a ADR-022)

Páginas creadas: 22 | Páginas actualizadas: 0

**Páginas creadas (wiki/decisiones/):**
- ADR-001 a ADR-016: creadas en sesión anterior
- ADR-017: Event Sourcing en BC Notificaciones (exactly-once delivery)
- ADR-018: Hash SHA-256 para integridad de resultados — `CalculadorHashCompetencia`
- ADR-019: Política de contraseñas (10+, mayúscula, número) + `PasswordStrengthBar.tsx`
- ADR-020: `Usuario.roles: list[Rol]` + perfiles Juez y Organizador en BC Registro
- ADR-021: Fly.io + volumen persistente (supersede ADR-010 Cloud Run + Litestream)
- ADR-022: `Categoria` StrEnum movida a `shared/domain/value_objects/`

**ADR-010 marcada como SUPERSEDIDA por ADR-021.**
**Cobertura de decisiones:** 22/22 ADRs del proyecto. Vista Decisiones completa.

---

## [2026-05-20] ingest | docs/iedd/ (6 archivos)

Páginas creadas: 3 | Páginas actualizadas: 0

**Páginas creadas:**
- `wiki/investigacion/iedd-marco-conceptual.md` — modelo de 5 capas, tesis central, rol de DDD e IA
- `wiki/investigacion/iedd-hipotesis-experimento.md` — hipótesis del ensayo, 5 puntos confirmados, tesis provisional, qué sigue abierto
- `wiki/investigacion/uat-metodologia.md` — política UAT: principios, proceso 5 pasos, vibe coding, datos reales como oráculo

**Fuentes ingresadas:** 01, 02, 03 (marco conceptual 5 capas), 04 (hipótesis), UAT-POLITICA-CONTROLADA.md, US-IEDD-template.md (referenciado, no creado como página propia)

**Hallazgo metodológico:** el framework IEDD se auto-documenta al usarse en AtaraxiaDive — el proyecto es simultáneamente laboratorio del experimento y producto del mismo.

---

## [2026-05-20] ingest | docs/dominio/03-atributos_calidad.md

Páginas creadas: 1 | Páginas actualizadas: 0

**Página creada:**
- `wiki/conceptos/atributos-calidad.md` — 8 atributos de calidad con valores concretos, drivers y mapa hacia ADRs

**Valores clave capturados:**
- Latencia máxima juez: 500 ms | Atletas simultáneos: 3 | Usuarios concurrentes: 50
- Modo offline requerido (conectividad precaria confirmada)
- Flujo juez: máximo 6 acciones; dispositivo principal: celular
- Log de auditoría inalterable requerido (→ ADR-018)
- Confiabilidad: performance es evento único e irrepetible (→ ADR-001 Event Sourcing)
- Reglas de negocio configurables sin desarrollador (→ ADR-004)
- Exportación de resultados requerida (CSV/JSON/AIDA-CMAS)

---

## [2026-05-20] ingest | docs/dominio/05-requerimientos_funcionales.md

Páginas creadas: 8 | Páginas actualizadas: 3 (performance, grilla, anuncio)

**Semilla de trazabilidad por área funcional:**
- `wiki/trazabilidad/RF-gestion-torneo.md` — 7 RFs; disciplinas: STA, DNF, DBF, DYN, SPE (configurable)
- `wiki/trazabilidad/RF-inscripcion-atletas.md` — 10 RFs; brevet no obligatorio; club obligatorio
- `wiki/trazabilidad/RF-preparacion.md` — 8 RFs; orden grilla: distancia=menor→mayor, tiempo=mayor→menor; OT definido por juez
- `wiki/trazabilidad/RF-ejecucion.md` — 10 RFs; black-out (no back-out); cronómetro manual; DNS = DQ inmediata
- `wiki/trazabilidad/RF-resultados.md` — 6 RFs; existe ranking "Overall"; empates → mismo puesto
- `wiki/trazabilidad/RF-usuarios-roles.md` — 5 RFs; 1 organizador por torneo; juez asignado por disciplina
- `wiki/trazabilidad/RF-notificaciones.md` — 4 RFs; mail + push; pendiente: notif. durante ejecución
- `wiki/trazabilidad/RF-integracion.md` — área completa pendiente de definición

**Enriquecimientos en conceptos existentes:**
- `performance`: black-out con distancia, cronómetro manual, DNS
- `grilla`: orden por tipo de disciplina, OT, atleta sin anuncio=no compite
- `anuncio`: definitivo (no modificable), valor > 0

**Pendientes globales detectados:** RF-IN-07, RF-EJ-04, RF-PM-01, RF-NT-03, RF-IG-01..04

---

## [2026-05-20] ingest | docs/dominio/01-dominio_torneos_apnea.md

Páginas creadas: 8 | Páginas actualizadas: 0

**Conceptos creados:**
- `wiki/conceptos/torneo.md` — ciclo de vida del torneo, etapas, datos
- `wiki/conceptos/disciplina.md` — modalidades de prueba (tiempo/distancia)
- `wiki/conceptos/grilla.md` — planilla de salida por disciplina
- `wiki/conceptos/performance.md` — actuación del atleta; tipos de finalización
- `wiki/conceptos/tarjeta.md` — validez de performance (blanca/roja); código de penalización
- `wiki/conceptos/anuncio.md` — marca declarada en Preparación; input para grilla
- `wiki/conceptos/atleta.md` — participante; datos deportivos; categoría; brevet
- `wiki/conceptos/roles.md` — Organizador, Juez, Atleta, Administrador

**Nota:** Fuente marcada como referencia histórica (elicitación feb 2026). Conceptos base
del dominio capturados. Arquitectura vigente (BCs) pendiente de fuentes 4-5 (ADRs + architecture/).

---

## [2026-05-20] init | Inicialización del wiki

Branch huérfano `wiki` creado.
Estructura de directorios y archivos base inicializados.
WIKI.md (schema) creado con convenciones, tipos de páginas y vistas.
Páginas de vistas (6) creadas con propósito, stakeholders y recorridos.

**Próximo paso:** Fase 0 — Preparación (resolver gaps G-01, G-02, G-03 en branch develop)
**Luego:** Fase 1 — Ingest fundacional (docs/dominio/, docs/adr/, docs/architecture/)
