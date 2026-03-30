# Traceability Matrix — AtaraxiaDive

| Campo | Valor |
|-------|-------|
| **Documento** | matrix.md |
| **Capa IEDD** | Capa 3 — Especificación (puente con Implementación) |
| **Fecha** | 2026-03-19 |
| **Fuentes** | `05-requerimientos_funcionales.md` · Context Map v1.1 · `estrategia-desarrollo-bc.md` · ES Competencia |
| **Estado** | ✅ v1.0 — Fase 0 |

---

## 1. Propósito

Esta matriz conecta cada Requerimiento Funcional (RF) con el BC responsable,
el incremento donde se implementa y la US-IEDD candidata que lo especifica.

**Lectura:**
- Un RF puede mapearse a más de un incremento si su implementación es incremental.
- Los RFs marcados `⏳ pendiente` tienen respuesta incompleta en el cuestionario
  de elicitación — deben resolverse antes del SP que los involucra.
- Los RFs marcados `— fuera de alcance v1` están documentados pero excluidos
  del horizonte actual del proyecto.

---

## 2. Cobertura por Subproyecto

| SP | BCs activos | RFs cubiertos |
|----|-------------|---------------|
| SP1 | Competencia (núcleo) | RF-PR-01/02/03, RF-EJ-02/05/07/08/10 |
| SP2 | Competencia (completo) + Resultados (núcleo) | RF-PR-04/05/06/07/08, RF-EJ-01, RF-PM-03 |
| SP3 | Torneo + Registro + Identidad + Resultados | RF-GT-01..07, RF-IN-01..06/08/09, RF-US-01..05, RF-PM-01/02/05/06 |
| SP4 | Notificaciones + extensiones | RF-EJ-03/06, RF-IN-05/06, RF-NT-01..04, RF-PM-05 |
| SP5 | Integración externa | RF-IG-01..04, RF-IN-07 |

---

## 3. Matriz Completa

### 3.1 RF-GT — Gestión del Torneo → BC Torneo

| RF | Descripción | BC | SP | Inc. | US-IEDD candidata | Estado |
|----|-------------|----|----|------|-------------------|--------|
| RF-GT-01 | Un torneo tiene una sola sede | Torneo | SP3 | 3.1 | US-3.1.x | ✅ definido |
| RF-GT-02 | Disciplinas configurables (STA, DNF, DBF, DYN, SPE2X50) | Torneo | SP3/SP4 | 3.1 / 4.3 | US-3.1.x | ✅ definido |
| RF-GT-03 | Múltiples torneos activos simultáneamente | Torneo | SP3 | 3.1 | US-3.1.x | ✅ definido |
| RF-GT-04 | Cancelar = estado Cancelado, datos preservados | Torneo | SP3 | 3.1 | US-3.1.x | ✅ definido |
| RF-GT-05 | Restricciones de transición entre fases (con retroceso Ejecución → Preparación) | Torneo | SP3 | 3.1 | US-3.1.x | ✅ definido |
| RF-GT-06 | Cierre no implica exportación automática | Torneo | SP3 | 3.5 | US-3.5.x | ✅ definido |
| RF-GT-07 | Registrar EntidadOrganizadora (federación/club) | Torneo | SP3 | 3.1 | US-3.1.x | ✅ definido |

---

### 3.2 RF-IN — Inscripción de Atletas → BC Registro

| RF | Descripción | BC | SP | Inc. | US-IEDD candidata | Estado |
|----|-------------|----|----|------|-------------------|--------|
| RF-IN-01 | Categorías configurables por edad y género | Registro / Torneo | SP3/SP4 | 3.2 / 4.3 | US-3.2.x | ✅ definido |
| RF-IN-02 | Brevet no obligatorio | Registro | SP3 | 3.2 | US-3.2.x | ✅ definido |
| RF-IN-03 | Sin límite de atletas por torneo o disciplina | Registro | SP3 | 3.2 | US-3.2.x | ✅ definido |
| RF-IN-04 | Cancelar inscripción hasta el día anterior | Registro | SP3 | 3.2 | US-3.2.x | ✅ definido |
| RF-IN-05 | Apto médico como requisito de inscripción | Registro | SP4 | 4.5 | US-4.5.x | ✅ definido |
| RF-IN-06 | Constancia de pago como requisito | Registro | SP4 | 4.5 | US-4.5.x | ✅ definido |
| RF-IN-07 | Conflicto de datos con BD FAAS | Registro | SP5 | 5.1 | US-5.1.x | ⏳ pendiente |
| RF-IN-08 | Género solo para categorización — sin otro efecto | Registro | SP3 | 3.2 | US-3.2.x | ✅ definido |
| RF-IN-09 | Atleta no puede cambiar categoría por disciplina | Registro | SP3 | 3.2 | US-3.2.x | ✅ definido |

---

### 3.3 RF-PR — Preparación de Competencias → BC Competencia

| RF | Descripción | BC | SP | Inc. | US-IEDD candidata | Estado |
|----|-------------|----|----|------|-------------------|--------|
| RF-PR-01 | AP = marca declarada por el atleta | Competencia | SP1 | 1.2 | US-P-01 | ✅ definido |
| RF-PR-02 | AP > 0, sin negativos ni cero (INV-P-01) | Competencia | SP1 | 1.2 | US-P-01 | ✅ definido |
| RF-PR-03 | AP no modificable una vez registrado (INV-P-02) | Competencia | SP1 | 1.2 | US-P-01 | ✅ definido |
| RF-PR-04 | Atleta sin AP no compite — no aparece en grilla (P-05) | Competencia | SP2 | 2.1 | US-C-02 | ✅ definido |
| RF-PR-05 | Orden de grilla: metros menor→mayor / tiempo mayor→menor (P-01) | Competencia | SP2 | 2.1 | US-C-02 | ✅ definido |
| RF-PR-06 | Andariveles simultáneos — varios atletas compiten en paralelo | Competencia | SP2 | 2.3 | US-C-02 | ✅ definido |
| RF-PR-07 | Organizador puede ajustar manualmente el orden de la grilla | Competencia | SP2 | 2.1 | US-C-03 | ✅ definido |
| RF-PR-08 | Intervalo entre OTs configurable por competencia (P-02) | Competencia | SP2 | 2.1 | US-C-01 | ✅ definido |

---

### 3.4 RF-EJ — Ejecución de Competencias → BC Competencia

| RF | Descripción | BC | SP | Inc. | US-IEDD candidata | Estado |
|----|-------------|----|----|------|-------------------|--------|
| RF-EJ-01 | Más de un juez asignado a una disciplina | Identidad / Torneo | SP3 | 3.4 | US-3.4.x | ✅ definido |
| RF-EJ-02 | DNS = descalificación inmediata, sin espera (P-07, INV-P-08) | Competencia | SP1 | 1.4 | US-P-05 | ✅ definido |
| RF-EJ-03 | Tarjetas amarillas con penalizaciones configurables | Competencia | SP4 | 4.4 | US-4.4.x | ✅ definido |
| RF-EJ-04 | Códigos de penalización (AIDA/CMAS) | Competencia | SP4 | 4.4 | US-4.4.x | ⏳ pendiente |
| RF-EJ-05 | Cronometraje manual — juez ingresa el tiempo | Competencia | SP1 | 1.4 | US-P-03 | ✅ definido |
| RF-EJ-06 | Corrección con ventana de impugnación (INV-P-15, HS-P2 ✅) | Competencia | SP4 | 4.4 | US-P-06 | ✅ definido |
| RF-EJ-07 | Black-out registra el hecho y la distancia alcanzada | Competencia | SP1 | 1.4 | US-P-04 | ✅ definido |
| RF-EJ-08 | Distancia con decimales (metros) | Competencia | SP1/SP2 | 1.2 / 2.2 | US-P-01 / US-P-03 | ✅ definido |
| RF-EJ-09 | Protocolo de superficie no evaluado por el sistema | — | — | — | — | — fuera de alcance v1 |
| RF-EJ-10 | Solo se registra resultado de tarjeta (no el SP en sí) | Competencia | SP1 | 1.4 | US-P-04 | ✅ definido |

---

### 3.5 RF-PM — Premiación y Resultados → BC Resultados

| RF | Descripción | BC | SP | Inc. | US-IEDD candidata | Estado |
|----|-------------|----|----|------|-------------------|--------|
| RF-PM-01 | Fórmula de puntos configurable por torneo (HS-19 ✅) | Resultados / Torneo | SP3 | 3.5 | US-3.5.x | ✅ definido |
| RF-PM-02 | Overall = ranking general multi-disciplina por categoría | Resultados | SP3 | 3.5 | US-3.5.x | ✅ definido |
| RF-PM-03 | Empates = mismo puesto y mismos puntos | Resultados | SP2 | 2.4 | US-2.4.2 | ✅ Implementado |
| RF-PM-04 | Certificados/diplomas | — | — | — | — | — fuera de alcance v1 |
| RF-PM-05 | Rankings por categoría y género | Resultados | SP4 | 4.4 | US-4.4.x | ✅ definido |
| RF-PM-06 | Publicación en plataforma + descarga | Resultados | SP3 | 3.5 | US-3.5.x | ✅ definido |

---

### 3.6 RF-US — Usuarios, Roles y Permisos → BC Identidad

| RF | Descripción | BC | SP | Inc. | US-IEDD candidata | Estado |
|----|-------------|----|----|------|-------------------|--------|
| RF-US-01 | Un organizador por torneo (no multi-organizador) | Identidad / Torneo | SP3 | 3.1 | US-3.1.x | ✅ definido |
| RF-US-02 | Un usuario puede tener múltiples roles | Identidad | SP3 | 3.1 | US-3.1.x | ✅ definido |
| RF-US-03 | Autenticación mail + contraseña | Identidad | SP3 | 3.1 | US-3.1.x | ✅ definido |
| RF-US-04 | Juez asignado a disciplina específica por el organizador | Identidad / Torneo | SP3 | 3.4 | US-3.4.x | ✅ definido |
| RF-US-05 | Atletas solo ven resultados finales (no resultados en curso) | Identidad / Resultados | SP3 | 3.5 | US-3.5.x | ✅ definido |

---

### 3.7 RF-NT — Notificaciones → BC Notificaciones

| RF | Descripción | BC | SP | Inc. | US-IEDD candidata | Estado |
|----|-------------|----|----|------|-------------------|--------|
| RF-NT-01 | Notificaciones por email y push | Notificaciones | SP4 | 4.2 | US-4.2.x | ✅ definido |
| RF-NT-02 | Recordatorio al atleta cuando se acerca el plazo de AP | Notificaciones | SP4 | 4.2 | US-4.2.x | ✅ definido |
| RF-NT-03 | Notificaciones a juez u organizador durante ejecución | Notificaciones | — | — | — | ⏳ pendiente |
| RF-NT-04 | Notificar a atletas cuando se publican resultados finales | Notificaciones | SP4 | 4.2 | US-4.2.x | ✅ definido |

---

### 3.8 RF-IG — Integración con Sistemas Externos → BC Registro / SP5

| RF | Descripción | BC | SP | Inc. | US-IEDD candidata | Estado |
|----|-------------|----|----|------|-------------------|--------|
| RF-IG-01 | Integración con BD FAAS (protocolo/formato) | Registro | SP5 | 5.1 | US-5.1.x | ⏳ pendiente |
| RF-IG-02 | Consulta a BD externa: solo lectura o lectura/escritura | Registro | SP5 | 5.1 | US-5.1.x | ⏳ pendiente |
| RF-IG-03 | BD externa no disponible al inscribir atleta | Registro | SP5 | 5.1 | US-5.1.x | ⏳ pendiente |
| RF-IG-04 | Exportación a sistemas de rankings (AIDA, CMAS) | Resultados | SP5 | 5.1 | US-5.1.x | ⏳ pendiente |

---

## 4. RFs Pendientes de Definición

Deben resolverse antes del SP que los involucra. No bloquean SP1 ni SP2.

| RF | Descripción | Bloquea | Resolver antes de |
|----|-------------|---------|-------------------|
| RF-IN-07 | ¿Qué pasa si los datos del atleta difieren de la BD FAAS? | SP5 inc. 5.1 | SP5 |
| RF-EJ-04 | Códigos de penalización (AIDA/CMAS u otra federación) | SP4 inc. 4.4 | SP4 |
| RF-NT-03 | ¿Juez u organizador reciben notificaciones durante ejecución? | SP4 inc. 4.2 | SP4 |
| RF-IG-01..04 | Integración completa con BD FAAS / exportación a rankings | SP5 inc. 5.1 | SP5 |

---

## 5. US-IEDD Candidatas para SP2

| US candidata | Inc. | RFs cubiertos | Comando/Contenido principal | Invariantes clave | Estado |
|-------------|------|---------------|-----------------------------|------------------|--------|
| INC-2.0 | — | — | Exception management: `domain/exceptions.py` + `exception_handlers.py` (ADR-013) | — | ✅ Done |
| US-2.1.1 | 2.1 | RF-PR-08 | `ConfigurarIntervaloOT` + scaffold aggregate Competencia + deuda SOLID SP1 | INV-C-01 | ✅ Done |
| US-2.1.2 | 2.1 | RF-PR-04, RF-PR-05 | `GenerarGrilla` / `RegenerarGrilla` | INV-C-01, P-01, P-02 | ✅ Done |
| US-2.1.3 | 2.1 | RF-PR-07 | `AjustarGrilla` | INV-C-02 (parcial) | ✅ Done |
| US-2.1.4 | 2.1 | — | `ConfirmarGrilla` + `IniciarCompetencia` + reemplazar stub `CompetenciaEstadoPort` | INV-C-02/03 | ✅ Done |
| US-2.2.1 | 2.2 | RF-EJ-08 | `DisciplinaDescriptor` value object + port (STA/tiempo, DNF/distancia) | — | ✅ Done |
| US-2.2.2 | 2.2 | RF-EJ-08 | API disciplina-aware + validación de unidades + ordenamiento por grilla | P-06 | ✅ Done |
| US-2.3.1 | 2.3 | RF-PR-06 | Ejecución multi-andarivel — distribución en grilla + sin conflicto entre andariveles | INV-C-05 | ✅ Done |
| US-2.4.1 | 2.4 | — | `CompetenciaFinalizada` automático (política P-08) | INV-C-04 | ✅ Done |
| US-2.4.2 | 2.4 | RF-PM-03 | `CalcularRanking` — BC Resultados núcleo · empates · podio | RF-PM-03 | ✅ Done |

---

## 6. US-IEDD SP1 — Implementadas

| US | Inc. | RFs cubiertos | Comando principal | Invariantes clave | Estado |
|----|------|---------------|------------------|------------------|--------|
| US-1.1.1 | 1.1 | — | Setup: esqueleto BC Competencia (BC-first) + tabla `events` + health-check | — | ✅ 2026-03-21 |
| US-1.2.1 | 1.2 | RF-PR-01/02/03, RF-EJ-08 | `RegistrarAP` | INV-P-01..04 | ✅ 2026-03-21 |
| US-1.2.2 | 1.2 | RF-EJ-02 | `LlamarAtleta` | INV-P-05 | ✅ 2026-03-22 |
| US-1.2.3 | 1.2 | RF-EJ-05 | `RegistrarResultado` | INV-P-06, INV-P-09 | ✅ 2026-03-22 |
| US-1.2.4 | 1.2 | RF-EJ-10 | `AsignarTarjeta` (blanca/roja) | INV-P-07, INV-P-10, INV-P-11 | ✅ 2026-03-22 |
| US-1.2.5 | 1.2 | RF-EJ-02 | `RegistrarDNS` | INV-P-08, INV-P-09 | ✅ 2026-03-23 |
| US-1.2.6 | 1.2 | RF-EJ-06 | `CorregirResultado` | INV-P-12, INV-P-13 | ✅ 2026-03-23 |
| US-1.3.1 | 1.3 | RF-EJ-05 | Read Models: `PerformanceActual`, `ProximosAtletas`, `ProgresoCompetencia` | — | ✅ 2026-03-23 |
| US-1.4.1 | 1.4 | RF-EJ-07 | `AsignarTarjeta` roja + black-out con distancia | INV-P-07, INV-P-11 | ✅ 2026-03-23 |
| US-1.4.2 | 1.4 | RF-EJ-05/10 | Flujo E2E + `GET /events` audit log | INV-P-05..10 | ✅ 2026-03-23 |

---

## 7. US-IEDD SP-ADJ-01 — Implementadas (refactoring post-SP2)

| US | Issues | Capas | Descripción | Estado |
|----|--------|-------|-------------|--------|
| US-ADJ-1.1 | ADJ-03/06/08 | `domain/` | `@property ot_programado` + `_event_handlers` en `__init__` + snake_case `registrar_ap` | ✅ 2026-03-28 |
| US-ADJ-1.2 | ADJ-01/02 | `domain/` | Helpers `_recalcular_ots` + `_aplicar_swap_posicion` en Competencia (OCP/SRP) | ✅ 2026-03-28 |
| US-ADJ-1.3 | ADJ-09 | `application/` | `_stream_ids.py` — fuente única, 11 duplicados DRY eliminados | ✅ 2026-03-28 |
| US-ADJ-1.4 | ADJ-04/05 | `api/` | DIP en router: `EventStoreDep: EventStorePort` + P-08 a composition root | ✅ 2026-03-28 |
| US-ADJ-1.5 | ADJ-07 | `api/` | SRP router: `schemas.py` + `dependencies.py` + `router.py` solo endpoints | ✅ 2026-03-28 |

---

## 8. US-IEDD SP-ADJ-02-code — Implementadas (refactoring arquitectónico cross-BC)

| US | Issues | Capas | Descripción | Estado |
|----|--------|-------|-------------|--------|
| US-ADJ-2.6 | B-01, B-02, B-04 | `shared/domain/`, `shared/infrastructure/`, `resultados/`, `competencia/domain/` | `Disciplina`, `DisciplinaDescriptor`, `UnidadMedida` → `shared/domain/value_objects/`. `EventStorePort`, `SQLiteEventStore` → `shared/`. `DisciplinaDescriptorAdapter` creado en `resultados/infrastructure/`. | ✅ 2026-03-28 |
| US-ADJ-2.7 | B-03 | `competencia/api/router.py` · `src/app.py` | Eliminado código muerto `get_on_finalizada_callback` del router. `build_on_finalizada_callback` (P-08 composition root) vive en `src/app.py`. | ✅ 2026-03-28 |
| US-ADJ-2.8 | B-05, D-04 | `competencia/api/router.py` | DIP fix: `get_event_store() -> EventStorePort` + `EventStoreDep = Annotated[EventStorePort, ...]`. | ✅ 2026-03-28 |

---

## 9. US-IEDD SP3 — Implementadas

| US | Inc. | RFs cubiertos | Contenido principal | Estado |
|----|------|---------------|---------------------|--------|
| US-3.1.1 | 3.1 | RF-GT-01/03/04/05/07 | Aggregate `Torneo` — máquina de estados, value objects, puerto abstracto | ✅ 2026-03-29 |
| US-3.1.2 | 3.1 | RF-GT-01/02/03/04/05/07 | API REST Torneo — CRUD + 7 endpoints de transición + SQLiteTorneoRepository | ✅ 2026-03-30 |

---

## 10. Cobertura Total

| Área | Total RFs | Definidos | Pendientes | Fuera de alcance v1 |
|------|:---------:|:---------:|:----------:|:-------------------:|
| Gestión del Torneo (RF-GT) | 7 | 7 | 0 | 0 |
| Inscripción (RF-IN) | 9 | 8 | 1 | 0 |
| Preparación (RF-PR) | 8 | 8 | 0 | 0 |
| Ejecución (RF-EJ) | 10 | 9 | 1 | 1 |
| Resultados (RF-PM) | 6 | 5 | 0 | 1 |
| Usuarios (RF-US) | 5 | 5 | 0 | 0 |
| Notificaciones (RF-NT) | 4 | 3 | 1 | 0 |
| Integración (RF-IG) | 4 | 0 | 4 | 0 |
| **Total** | **53** | **45** | **7** | **2** |

> **85% de RFs completamente definidos.** Los 7 pendientes están en SP4+ — no bloquean SP1/SP2.

---

## 10. US → Tests

| US-IEDD | Suite de tests | Estado |
|---------|---------------|--------|
| US-1.2.1 | unit/competencia/domain + unit/competencia/application + unit/competencia/infrastructure + integration/competencia + features/US-1.2.1 | ✅ 34 tests (92%) |
| US-1.2.2 | unit/competencia/domain + unit/competencia/application + unit/competencia/infrastructure + integration/competencia + features/US-1.2.2 | ✅ 41 tests (92%) |
| US-1.2.3 | unit/competencia/domain + unit/competencia/application + integration/competencia + features/US-1.2.3 | ✅ 65 tests (98%) |
| US-1.2.4 | unit/competencia/domain + unit/competencia/application + integration/competencia + features/US-1.2.4 | ✅ 92 tests (98%) |
| US-1.2.5 | unit/competencia/domain + unit/competencia/application + integration/competencia + features/US-1.2.5 | ✅ 108 tests (98.51%) |
| US-1.2.6 | unit/competencia/domain + unit/competencia/application + integration/competencia + features/US-1.2.6 | ✅ 128 tests (98.51%) |
| US-1.3.1 | unit/competencia/application + integration/competencia + features/US-1.3.1 | ✅ 174 tests (97.53%) |
| US-1.4.1 | unit/competencia/domain + unit/competencia/application + integration/competencia + features/US-1.4.1 | ✅ 189 tests (97.57%) |
| US-1.4.2 | unit/competencia/application + integration/competencia + features/US-1.4.2 | ✅ 207 tests (98%) |
| US-3.1.1 | unit/torneo/domain/test_torneo + integration/torneo/test_torneo_domain_integration + features/US-3.1.1-aggregate-torneo | ✅ 36 tests (100%) |
| US-3.1.2 | unit/torneo/application/test_crear_torneo + test_transiciones_handlers + test_obtener_torneo + integration/torneo/test_sqlite_torneo_repository + features/US-3.1.2-api-rest-torneo | ✅ 33 tests (100%) |

---

## 11. US → ADR

| US-IEDD | ADR relacionado | Relación |
|---------|----------------|---------|
| US-1.1.1 | ADR-001..004 | Stack tecnológico y arquitectura hexagonal |
| US-1.1.1 | ADR-006 | Estructura BC-first — esqueleto de `src/competencia/` |
| US-1.1.1 | ADR-007 | SQLite como motor de persistencia — `data/competencia.db` |
| US-1.1.1 | ADR-008 | Event Store como tabla `events` append-only en SQLite |
| US-1.1.1 | ADR-009 | Migraciones Alembic en `competencia/infrastructure/migrations/` |
| US-1.2.x | ADR-005 | Event Sourcing en BC Competencia |

---

*Documento creado: 2026-03-19 — Semana 0, Fase 0*
*v1.1 — 2026-03-20: US-1.1.1 actualizada a BC-first · ADR-006 agregado · FAZ → FAAS*
*v1.2 — 2026-03-28: SP-ADJ-01 agregado (§7) · secciones SP1 renumeradas · numeración de §§ corregida*
*v1.3 — 2026-03-28: SP-ADJ-02-code agregado (§8) · US-ADJ-2.6/2.7/2.8 documentadas*
*v1.4 — 2026-03-29: SP3 §9 agregado · US-3.1.1 implementada*
*v1.5 — 2026-03-30: US-3.1.2 implementada — API REST Torneo completa*
*Fuentes: 05-requerimientos_funcionales.md · Context Map v1.1 · estrategia-desarrollo-bc.md · ES Competencia*
*Mantenido por: Claude Cowork + Victor Valotto*
