# Traceability Matrix — AtaraxiaDive

> Estado documental: vigente  
> Fuente de verdad para: trazabilidad RF → BC → incremento → US-IEDD · estados de implementación  
> Última actualización: 2026-05-02  
> Jerarquía de autoridad: [FUENTES-DE-VERDAD-DOCUMENTAL.md](../inventario/FUENTES-DE-VERDAD-DOCUMENTAL.md)

| Campo | Valor |
|-------|-------|
| **Documento** | matrix.md |
| **Capa IEDD** | Capa 3 — Especificación (puente con Implementación) |
| **Fecha** | 2026-05-01 |
| **Fuentes** | `05-requerimientos_funcionales.md` · Context Map v1.1 · `estrategia-desarrollo-bc.md` · ES Competencia |
| **Estado** | ✅ v1.34 — SP6 INC-6.1 en curso · US-6.1.1 ✅ · US-6.1.2 ✅ · US-6.1.3 ✅ · US-6.1.4 ✅ |

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
- Los RFs marcados como `parcial` tienen definición o soporte técnico previo,
  pero todavía no están expuestos como producto final en el incremento vigente.

### Estados normalizados en esta matriz

| Estado | Significado | Autoridad |
|--------|------------|-----------|
| **Planificado** | Existe intención en plan, sin especificación formal | Planes (docs/plans/) |
| **Especificado** | Tiene US-IEDD con criterios de aceptación | US-IEDD en docs/specs/ |
| **Implementado** | Código integrado en rama principal | Tests unitarios pass + revisión código |
| **Validado** | Tests + UAT + baseline de cierre | Baselines (.cm/baselines/) |
| `✅ definido` | Especificado (equivalente a "Especificado") | US-IEDD |
| `✅ completado` / `✅ implementado` | Implementado + validado en SP cerrado | Baseline del SP |
| `🟡` (naranja) | Especificado pero parcialmente implementado | US-IEDD + rama de trabajo |
| `— fuera de alcance v1` | Planificado para SP futuro o descartado | Planes o decisión formal |

---

## 2. Cobertura por Subproyecto

| SP | BCs activos | RFs cubiertos |
|----|-------------|---------------|
| SP1 | Competencia (núcleo) | RF-PR-01/02/03, RF-EJ-02/05/07/08/10 |
| SP2 | Competencia (completo) + Resultados (núcleo) | RF-PR-04/05/06/07/08, RF-EJ-01, RF-PM-03 |
| SP3 | Torneo + Registro + Identidad + Resultados | RF-GT-01..07, RF-IN-01..06/08/09, RF-US-01..05, RF-PM-01/02/05/06 |
| SP-ADJ-04 | Ajustes de Shared + Registro + Resultados + Competencia | RF-GT-02, RF-IN-10, RF-PR-05, RF-PM-05 |
| SP4 INC-4.1 | Competencia + Torneo + Resultados (correcciones CMAS/FAAS) | RF-GT-02 (variantes SPE), RF-PR-05 (orden SPE), brechas reglamento (ver §3) |
| SP4 INC-4.2/4.3 | Frontend (scaffold + juez) | RF-EJ-01..10 (UI juez completa) |
| SP4 INC-4.4 | Frontend (offline-first) | RF-EJ-03 (tarjetas), RF-EJ-06 (corrección con ventana) — operación sin red |
| SP4 INC-4.5/4.6 | Notificaciones + Auditoría + Exportación | RF-NT-01..04, RF-EJ-06 |
| SP-ADJ-06 | FAZ→FAAS (código + docs) + refactoring técnico + UAT SP4 | — (deuda técnica + validación) |
| SP5 INC-5.1 / INC-5.1-ADJ | Frontend organizador (panel completo) | RF-GT-01..07, RF-PR-04..08, RF-EJ-01..10 (UI organizador) |
| SP5 INC-5.2 / SP-ADJ-08 | Frontend organizador + Competencia | Ejecución por disciplina, cierre manual, cancelación fuerte |
| SP5 INC-5.3 | Identidad + Frontend | RF-US-01..05 (gestión UI de usuarios/roles + vista atleta con inscripción básica) |
| SP5 INC-5.4 | Identidad + Frontend | RF-IN-05/06 y flujo UI de inscripción/APs — auto-registro, cambiar/olvidé pw (US-5.4.1..5.4.3) — PRs #112–#114 |
| SP5 INC-5.5 | Registro + Competencia + Frontend | Portal atleta completo (shell dark, wizard inscripción, declarar AP) + vista organizador con inscriptos y estado AP (US-5.5.1..5.5.2) — PRs #120, #121, #122 |
| SP5 INC-5.6 | Resultados + Torneo + Frontend | Algoritmo FAAS + TipoReglamento + ranking por categoría/género con puntos + UI tabla ejecución + podios 6 divisiones (US-5.6.1..5.6.6) — PRs #123–#128 |
| SP5 SP-ADJ-09 | Frontend organizador | Refactoring UX organizador: shell dark, routing, home, dashboard, resultados, arquitectura + declarar AP en inscripción (US-ADJ-9.1..9.7) — PRs #129–#136 |
| SP5 INC-5.7 | Portal Atleta + Resultados | Portal del atleta: mis torneos, mi grilla, mis resultados, rankings/podios + fix resultados provisionales (US-5.7.1..5.7.4) — PRs #137–#140 |
| SP5 INC-5.8 | — | Desestimado — contenido absorbido en SP6 |
| Futuro / fuera de scope SP5 | Integración externa | RF-IG-01..04, RF-IN-07 |

---

## 3. Matriz Completa

### 3.1 RF-GT — Gestión del Torneo → BC Torneo

| RF | Descripción | BC | SP | Inc. | US-IEDD candidata | Estado |
|----|-------------|----|----|------|-------------------|--------|
| RF-GT-01 | Un torneo tiene una sola sede | Torneo | SP3 | 3.1 | US-3.1.x | ✅ definido |
| RF-GT-02 | Disciplinas configurables (STA, DNF, DBF, DYN, SPE y variantes) | Torneo | SP3/SP4 | 3.1 / 4.1 | US-3.1.x / US-4.1.3 | ✅ completado — acrónimos corregidos en SP-ADJ-04; variantes SPE_2X50/4X50/8X50/16X50 agregadas en INC-4.1 |
| RF-GT-03 | Múltiples torneos activos simultáneamente | Torneo | SP3 | 3.1 | US-3.1.x | ✅ definido |
| RF-GT-04 | Cancelar = estado Cancelado, datos preservados | Torneo | SP3 | 3.1 | US-3.1.x | ✅ definido |
| RF-GT-05 | Restricciones de transición entre fases (con retroceso Ejecución → Preparación) | Torneo | SP3 | 3.1 | US-3.1.x | ✅ definido |
| RF-GT-06 | Cierre no implica exportación automática | Torneo | SP3 | 3.5 | US-3.5.x | ✅ definido |
| RF-GT-07 | Registrar EntidadOrganizadora (federación/club) | Torneo | SP3 | 3.1 | US-3.1.x | ✅ definido |

---

### 3.2 RF-IN — Inscripción de Atletas → BC Registro

| RF | Descripción | BC | SP | Inc. | US-IEDD candidata | Estado |
|----|-------------|----|----|------|-------------------|--------|
| RF-IN-01 | Categorías configurables por edad y género | Registro / Torneo | SP3/SP4 | 3.2 / 4.3 | US-3.2.2 | ✅ implementado |
| RF-IN-02 | Brevet no obligatorio | Registro | SP3 | 3.2 | US-3.2.2 | ✅ implementado |
| RF-IN-03 | Sin límite de atletas por torneo o disciplina | Registro | SP3 | 3.2 | US-3.2.3 | ✅ implementado |
| RF-IN-04 | Cancelar inscripción hasta el día anterior | Registro | SP3 | 3.2 | US-3.2.3 | ✅ implementado |
| RF-IN-05 | Apto médico como requisito de inscripción | Registro | SP5 | 5.4 | US-5.4.1 | ⏳ Deuda técnica — UI implementado (frontend/src/pages/atleta/AtletaInscripcionPage.tsx step 3); persistencia backend pendiente. Evidencia: tests/features/US-5.5.1-inscripcion-atleta-ap.feature; docs/reports/US-5.5.1-report.md; docs/plans/sp5/US-5.5.1-implementation-notes.md; PRs #120–#122. Aceptación: adjuntos son validados en UI; almacenamiento backend pospuesto a SP6. |
| RF-IN-06 | Constancia de pago como requisito | Registro | SP5 | 5.4 | US-5.4.1 | ⏳ Deuda técnica — UI implementado (frontend/src/pages/atleta/AtletaInscripcionPage.tsx step 3); persistencia backend pendiente. Evidencia: tests/features/US-5.5.1-inscripcion-atleta-ap.feature; docs/reports/US-5.5.1-report.md; docs/plans/sp5/US-5.5.1-implementation-notes.md; PRs #120–#122. Aceptación: adjuntos son validados en UI; almacenamiento backend pospuesto a SP6. |
| RF-IN-07 | Conflicto de datos con BD FAAS | Registro | Futuro | — | — | — fuera de scope SP5/v1.0; depende de integración FAAS |
| RF-IN-08 | Género solo para categorización — sin otro efecto | Registro | SP3 | 3.2 | US-3.2.2 | ✅ implementado |
| RF-IN-09 | Atleta no puede cambiar categoría por disciplina | Registro | SP3 | 3.2 | US-3.2.2 | ✅ implementado |
| RF-IN-10 | Club obligatorio del atleta y visible en grillas/reportes | Registro | SP-ADJ-04 | — | US-ADJ-4.4 | ✅ implementado |

---

### 3.3 RF-PR — Preparación de Competencias → BC Competencia

| RF | Descripción | BC | SP | Inc. | US-IEDD candidata | Estado |
|----|-------------|----|----|------|-------------------|--------|
| RF-PR-01 | AP = marca declarada por el atleta | Competencia | SP1 | 1.2 | US-P-01 | ✅ definido |
| RF-PR-02 | AP > 0, sin negativos ni cero (INV-P-01) | Competencia | SP1 | 1.2 | US-P-01 | ✅ definido |
| RF-PR-03 | AP no modificable una vez registrado (INV-P-02) | Competencia | SP1 | 1.2 | US-P-01 | ✅ definido |
| RF-PR-04 | Atleta sin AP no compite — no aparece en grilla (P-05) | Competencia | SP2 | 2.1 | US-C-02 | ✅ definido |
| RF-PR-05 | Orden de grilla: AP ascendente (DNF/DYN/DBF/STA) o descendente (SPE) | Competencia | SP2 / SP-ADJ-04 / SP4 | 2.1 / — / 4.1 | US-C-02 / US-ADJ-4.2 / US-4.1.4 | ✅ completado en INC-4.1 — SPE usa orden descendente (mayor AP primero) per reglamento CMAS/FAAS |
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
| RF-EJ-04 | Códigos de penalización (AIDA/CMAS) | Competencia | SP4 | 4.4 | US-4.4.x | ✅ implementado — dominio: competencia/domain/value_objects/tipo_penalizacion.py; spec US-4.1.2 |
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
| RF-PM-01 | Fórmula de puntos configurable por torneo (HS-19 ✅) | Resultados / Torneo | SP3/SP5 | 3.5 / 5.5 | US-3.5.x / US-5.5.1..5.5.2 | ✅ completado (implementado en INC-5.6) |
| RF-PM-02 | Overall = ranking general multi-disciplina por categoría | Resultados | SP3/SP5 | 3.5 / 5.5 | US-3.5.x / US-5.5.4 | ✅ completado (implementado en INC-5.6) |
| RF-PM-03 | Empates = mismo puesto y mismos puntos | Resultados | SP2 | 2.4 | US-2.4.2 | ✅ Implementado |
| RF-PM-04 | Certificados/diplomas | — | — | — | — | — fuera de alcance v1 |
| RF-PM-05 | Rankings por categoría y género | Resultados | SP-ADJ-04/SP5 | — / 5.5 | US-ADJ-4.5 / US-5.5.3..5.5.6 | ✅ completado (implementado en INC-5.6) |
| RF-PM-06 | Publicación en plataforma + descarga | Resultados | SP3/SP5 | 3.5 / 5.5 | US-3.5.x / US-5.5.5..5.5.6 | ✅ completado (implementado en INC-5.7) |

---

### 3.6 RF-US — Usuarios, Roles y Permisos → BC Identidad

| RF | Descripción | BC | SP | Inc. | US-IEDD candidata | Estado |
|----|-------------|----|----|------|-------------------|--------|
| RF-US-01 | Un organizador por torneo (no multi-organizador) | Identidad / Torneo | SP3 | 3.2 | US-3.2.1 | ✅ implementado |
| RF-US-02 | Un usuario puede tener múltiples roles | Identidad | SP3 | 3.2 | US-3.2.1 | ✅ implementado |
| RF-US-03 | Autenticación mail + contraseña | Identidad | SP3 | 3.2 | US-3.2.1 | ✅ implementado |
| RF-US-04 | Juez asignado a disciplina específica por el organizador | Identidad / Torneo | SP3 | 3.4 | US-3.4.x | ✅ definido |
| RF-US-05 | Atletas solo ven resultados finales (no resultados en curso) | Identidad / Resultados | SP3 | 3.5 | US-3.5.x | ✅ definido |

---

### 3.7 RF-NT — Notificaciones → BC Notificaciones

| RF | Descripción | BC | SP | Inc. | US-IEDD candidata | Estado |
|----|-------------|----|----|------|-------------------|--------|
| RF-NT-01 | Notificaciones por email y push | Notificaciones | SP4 | 4.5 | US-4.5.x | 🟡 email implementado y cableado para P-10/P-11 (`US-4.5.1`..`US-4.5.5`); push pendiente |
| RF-NT-02 | Recordatorio al atleta cuando se acerca el plazo de AP | Notificaciones | SP4 | 4.5 | US-4.5.x | ✅ definido · pendiente de implementación |
| RF-NT-03 | Notificaciones a juez u organizador durante ejecución | Notificaciones | — | — | — | ⏳ pendiente |
| RF-NT-04 | Notificar a atletas cuando se publican resultados finales | Notificaciones | SP4 | 4.5 | US-4.5.x | ✅ implementado (`US-4.5.4`) |

---

### 3.8 RF-IG — Integración con Sistemas Externos → Futuro / fuera de scope SP5

| RF | Descripción | BC | SP | Inc. | US-IEDD candidata | Estado |
|----|-------------|----|----|------|-------------------|--------|
| RF-IG-01 | Integración con BD FAAS (protocolo/formato) | Registro | Futuro | — | — | — fuera de scope SP5/v1.0 |
| RF-IG-02 | Consulta a BD externa: solo lectura o lectura/escritura | Registro | Futuro | — | — | — fuera de scope SP5/v1.0 |
| RF-IG-03 | BD externa no disponible al inscribir atleta | Registro | Futuro | — | — | — fuera de scope SP5/v1.0 |
| RF-IG-04 | Exportación a sistemas de rankings (AIDA, CMAS) | Resultados | Futuro | — | — | — fuera de scope SP5/v1.0 |

---

## 4. RFs Pendientes de Definición

Deben resolverse antes del incremento futuro que los involucre. No bloquean el
alcance vigente de SP5 salvo que se reabra explícitamente el scope.

| RF | Descripción | Bloquea | Resolver antes de |
|----|-------------|---------|-------------------|
| RF-IN-07 | ¿Qué pasa si los datos del atleta difieren de la BD FAAS? | Futuro | Post-SP5 |
| RF-EJ-04 | Códigos de penalización (AIDA/CMAS u otra federación) | — | Resuelto (implementado) |
| RF-NT-03 | ¿Juez u organizador reciben notificaciones durante ejecución? | Futuro | Post-SP5 |
| RF-IG-01..04 | Integración completa con BD FAAS / exportación a rankings | Futuro | Post-SP5 |

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
| US-3.2.1 | 3.2 | RF-US-01..05 | BC Identidad — `Usuario` + JWT mínimo + `/auth` | ✅ 2026-03-30 |
| US-3.2.2 | 3.2 | RF-IN-01/02/08/09 | Aggregate `Atleta` + registro/consulta + repositorio SQLite | ✅ 2026-03-31 |
| US-3.2.3 | 3.2 | RF-IN-03/04 | Aggregate `Inscripcion` + inscribir/cancelar + listar inscriptos | ✅ 2026-03-31 |
| US-3.3.1 | 3.3 | RF-PM-01/02/05 | `torneo_id` opcional en `Competencia` para habilitar overall por torneo | ✅ 2026-03-31 |
| US-3.3.2 | 3.3 | RF-IN-01..04, RF-GT-02/03 | ACL Torneo/Registro → Competencia para crear competencias por disciplina | ✅ 2026-03-31 |
| US-3.4.1 | 3.4 | RF-EJ-01 | `AsignarDisciplinas` + `AsignarJuez` en Torneo | ✅ 2026-04-01 |
| US-3.4.2 | 3.4 | RF-US-02/03/04 | Auth por rol en APIs escribibles con JWT middleware | ✅ 2026-04-01 |
| US-3.5.1 | 3.5 | RF-PM-01/02 | Aggregate `RankingOverall` + `CalcularOverallHandler` | ✅ 2026-04-02 |
| US-3.5.2 | 3.5 | RF-PM-05 | Política `P-09`: cálculo automático del overall al cerrar el torneo | ✅ 2026-04-02 |
| US-3.5.3 | 3.5 | RF-PM-06 | API `GET /resultados/{torneo_id}/overall` | ✅ 2026-04-02 |

---

## 10. US-IEDD SP-ADJ-03 — Implementadas (ajuste técnico post-SP3)

| US | Issues | Capas | Descripción | Estado |
|----|--------|-------|-------------|--------|
| US-ADJ-3.1 | ADJ-01, SOLID-01 | `competencia/domain/`, `torneo/domain/` | Extraer `GrillaDeSalida` VO + eliminar `_DISCIPLINAS_SP3` (OCP) | ✅ 2026-04-03 |
| US-ADJ-3.2 | ADJ-02 | `competencia/domain/`, `competencia/application/` | Extraer `TarjetaAsignacion` VO | ✅ 2026-04-03 |
| US-ADJ-3.3 | ADJ-03/04, SOLID-04 | `src/app.py`, `resultados/application/` | Refactorizar `build_app()` + constante event type | ✅ 2026-04-03 |
| US-ADJ-3.4 | ADJ-05 | `shared/api/`, `*/api/router.py` | Mover deps auth a `shared/api/dependencies.py` (DIP cross-BC) | ✅ 2026-04-03 |
| US-ADJ-3.5 | ADJ-06 | `competencia/domain/ports/` | Limpiar imports cross-module en ports | ✅ 2026-04-03 |
| US-ADJ-3.6 | SOLID-02/03 | `identidad/domain/ports/`, `identidad/application/` | `TokenServicePort` + `PasswordHashingPort` (DIP en Identidad) | ✅ 2026-04-03 |
| US-ADJ-3.7 | HITO-15 | `competencia/infrastructure/`, `competencia/application/queries/` | Proyección `competencias_por_torneo` O(n)→O(1) | ✅ 2026-04-03 |
| US-ADJ-3.8 | HITO-14 D-06 | `resultados/infrastructure/` | Desacoplar ACL resultados de BC Competencia | ✅ 2026-04-03 |

---

## 11. US-IEDD SP-ADJ-04 — Completadas (discrepancias de dominio real — pre-cierre BL-003)

| US | DISC | RFs corregidos | Descripción | Estado |
|----|------|----------------|-------------|--------|
| US-ADJ-4.1 | DISC-02, DISC-03 | RF-GT-02 | Renombrar `DYNB→DBF` y `SPE2X50→SPE` en enum `Disciplina` | ✅ 2026-04-03 |
| US-ADJ-4.2 | DISC-04 | RF-PR-05 | Corregir orden grilla STA: `orden_ascendente=True` (ascendente) | ✅ 2026-04-03 |
| US-ADJ-4.3 | DISC-07 | — | Renombrar `JUVENIL→JUNIOR` en enum `Categoria` | ✅ 2026-04-03 |
| US-ADJ-4.4 | DISC-05 | RF-IN-10 | Agregar campo `club` a aggregate `Atleta` | ✅ 2026-04-03 |
| US-ADJ-4.5 | DISC-01 | RF-PM-05 | Ranking por (disciplina, categoría) en BC Resultados | ✅ 2026-04-03 |
| US-ADJ-4.6 | DISC-06 | — | Value Object `TiempoAP` — parsear `MM:SS → segundos` | ✅ 2026-04-03 |

---

## 12. US-IEDD SP4 INC-4.1 — Implementadas (correcciones de dominio CMAS/FAAS)

| US | Inc. | RFs / Brechas cubiertos | Contenido principal | Estado |
|----|------|-------------------------|---------------------|--------|
| US-4.1.1 | 4.1 | Brecha CMAS #1 — motivos DQ | `MotivoDQ` StrEnum (BKO_SUPERFICIE, BKO_SUBACUATICO, NO_PROTOCOLO, INFRACCION_TECNICA, NO_INICIO_VENTANA, SALIDA_FALSO) · `TarjetaAsignacion` VO extendido · tests 102 passed | ✅ 2026-04-08 |
| US-4.1.2 | 4.1 | Brecha CMAS #2 — tarjeta blanca con penalizaciones | `TipoTarjeta.BlancaConPenalizaciones` · `PenalizacionTecnica` VO · RP = medido − Σ deducciones · tests 107 passed | ✅ 2026-04-08 |
| US-4.1.3 | 4.1 | RF-GT-02 — variantes SPE | Subdisciplinas `SPE_2X50`, `SPE_4X50`, `SPE_8X50`, `SPE_16X50` en `shared/domain/` · tests 73 passed | ✅ 2026-04-08 |
| US-4.1.4 | 4.1 | RF-PR-05 — orden SPE descendente | `GrillaDeSalida.generar()` usa orden descendente para SPE (AP mayor→menor) · tests 68 passed | ✅ 2026-04-08 |
| US-4.1.5 | 4.1 | — (refactoring técnico) | Descomponer aggregate `Performance` → `performance.py` + `performance_state.py` + `performance_events.py` + VOs `ResolucionTarjeta` y `RPFinal` · tests 82 passed | ✅ 2026-04-08 |
| US-4.1.6 | 4.1 | — (refactoring técnico) | `_handler_utils.py` — helpers comunes; alivia `AsignarTarjetaHandler`, `GenerarGrillaHandler`, `LlamarAtletaHandler`, `RegistrarAPHandler` · tests 36 passed | ✅ 2026-04-08 |
| US-4.1.7 | 4.1 | — (refactoring técnico) | `GrillaDeSalida.ajustar()` partido en submétodos · `RankingCompetencia` descompuesto · tests 32 passed | ✅ 2026-04-08 |
| US-4.1.8 | 4.1 | — (refactoring técnico) | `Torneo` limpiado · `SQLiteTorneoRepository` simplificado · `DisciplinaDescriptor` y `TarjetaAsignacion` aliviados · tests 91 passed | ✅ 2026-04-08 |

> **US-4.1.5 a US-4.1.8:** ajustes técnicos derivados del DesignReviewer al cierre del incremento funcional (HITO-19).
> Patrón acordado: los quality gate issues del DesignReviewer se resuelven como US-IEDD dentro del mismo INC, no como SP-ADJ.

---

## 13. US-IEDD SP4 INC-4.2 — Fundación Frontend

> Estado del incremento al 2026-04-11: ambas US están mergeadas a `develop` y el
> `DesignReviewer` manual consolidado dio `0 CRITICAL · 142 WARNING`
> (`quality/reports/designreviewer/INC-4.2-report.txt`). Queda pendiente la
> validación manual en browser con backend corriendo para considerar el cierre
> funcional completo del incremento.

| US | Inc. | RFs / Decisiones cubiertos | Contenido principal | Estado |
|----|------|----------------------------|---------------------|--------|
| US-4.2.1 | 4.2 | D-01..D-06 (decisiones-frontend.md) · ADR-003 | Scaffold Vite 6 + React 19 + TypeScript strict · Tailwind v4 · vite-plugin-pwa (manifest standalone+portrait, Workbox NetworkFirst) · HealthCheck (TanStack Query) · useConnectionStore (Zustand) · estructura D-01 · npm run build exitcode 0 | ✅ 2026-04-11 |
| US-4.2.2 | 4.2 | D-02 (routing+guards) · D-03 (Zustand) | useAuthStore (Zustand, sin persistencia) · loginApi() POST /auth/login · decodeJwtPayload() atob() · LoginPage (TanStack Query mutation, error inline) · RequireRole HOC · BrowserRouter + rutas /login /juez/disciplinas /organizador/dashboard · npm run build exitcode 0 | ✅ 2026-04-11 |

---

## 14. US-IEDD SP4 INC-4.3 — Interfaz del Juez

> UAT completado 2026-04-12 con datos reales BA 2025. 5/5 US implementadas. DesignReviewer post-merge: 0 CRITICAL, 158 WARNING.
> PR #75 (fix UX INC-4.3): 8 issues UX (MUX-01..08) + BUG-01 (INV-DQ-01 condicionado por `es_disciplina_tiempo` en STA).
> Deuda UX residual: `docs/design/ux/mejoras-ux.md`. HITO-20: invariantes de dominio que no cubren todas las variantes.

| US | Inc. | RFs / Decisiones cubiertos | Contenido principal | Estado |
|----|------|----------------------------|---------------------|--------|
| US-4.3.1 | 4.3 | D-02, D-03 · wireframes-juez S-01 | MisDisciplinas real en React · `api/torneo.ts` + `api/competencia.ts` · `useCompetenciaStore` · `DisciplinaCard` · `JuezLayout` · ruta `/juez/grilla` stub · `npm run build` y `npm run lint` OK | ✅ 2026-04-12 |
| US-4.3.2 | 4.3 | RF-EJ-05, RF-EJ-06 · wireframes-juez S-02 a S-09 | router `competencia` con `POST /llamar`, `POST /registrar-resultado`, `POST /asignar-tarjeta` · grilla enriquecida con estado/AP · `GrillaPage` operativa · wizard móvil `/juez/performance` · `StepIndicator`, `AtletaCard`, `RpSelector` · `npm run build`, `npm run lint`, `compileall` y smoke test `TestClient` OK | ✅ 2026-04-11 |
| US-4.3.3 | 4.3 | RF-EJ-07, RF-EJ-08 · wireframes-juez S-12 a S-14 | router `competencia` con `POST /registrar-dns` · wizard extendido con DNS, BKO, roja con `MotivoDQ` y `BlancaConPenalizaciones` · `MotivoDqSelector` · `PenalizacionesSelector` · fixture `STA` + `DNF` · `npm run build`, `npm run lint`, `compileall` y smoke test `TestClient` OK | ✅ 2026-04-12 |
| US-4.3.4 | 4.3 | wireframes-juez S-10, S-15 | nuevo estado `EnRevision` en `Performance` · `ResolverRevisionCommand` + `ResolverRevisionHandler` · evento `RevisionResuelta` · `POST /competencia/{id}/resolver-revision` · `ResultadoAmarilla` (S-10) + `RevisionDesdeGrilla` (S-15) + `AlertaRevision` · timer informativo 3 min · BUG-01: `es_disciplina_tiempo` condiciona `INV-DQ-01` en `TarjetaAsignacion` | ✅ 2026-04-12 |
| US-4.3.5 | 4.3 | wireframes-juez STA · RF-EJ-02 | Paso 3 del wizard adaptado para STA — botón "Vías respiratorias en agua" en lugar de "Atleta inicia" · BKO en STA registra `valor_rp=0` automáticamente · UI móvil ajustada | ✅ 2026-04-12 |

---

## 15. US-IEDD SP4 INC-4.4 — Offline-first

| US | Inc. | RFs / Decisiones cubiertos | Contenido principal | Estado |
|----|------|----------------------------|---------------------|--------|
| US-4.4.1 | 4.4 | PLAN-SP4 §INC-4.4 · ADR-015 (Dexie.js) | Instalar Dexie.js · `AtaraxiaDiveDB` schema (`grilla_cache`, `comando_queue`) · hook `usePrecarga` · `GrillaPage` con lectura offline · expiración 24h · label de antigüedad | ✅ Done (PR #77) |
| US-4.4.2 | 4.4 | PLAN-SP4 §INC-4.4 | Hook `useComandoQueue` · `PerformanceFlowPage` intercepta comandos (envía directo si online, encola si offline) · estado optimista en grilla (badge ⏳) · `useConnectionStore.pendingCount` | ✅ Done (PR #77) |
| US-4.4.3 | 4.4 | PLAN-SP4 §INC-4.4 | Migración SW a `injectManifest` · `sw.ts` con precache + NetworkFirst + Background Sync · hook `useSyncQueue` (FIFO, backoff, fallback online event) · `SyncStatusBadge` en `JuezLayout` | ✅ Done (PR #77) |

> DesignReviewer post-INC-4.4: 0 CRITICAL, 158 WARNING. Fix robustez offline mergeado en `dfb6ec3` (timeout 5s fetchWithTimeout + AbortController en postCommand).

---

## 16. US-IEDD SP4 INC-4.5 — BC Notificaciones

| US | Inc. | RFs / Decisiones cubiertos | Contenido principal | Estado |
|----|------|----------------------------|---------------------|--------|
| US-4.5.1 | 4.5 | RF-NT-01 · PLAN-SP4 §INC-4.5 | Aggregate `Notificacion` · ciclo de vida (Solicitada → Enviada / Fallida) · event store SQLite · idempotencia exactly-once (`evento_fuente_id`) | ✅ Done (PR #79) |
| US-4.5.2 | 4.5 | RF-NT-01 · ADR-016 (Resend) | Puerto `EmailPort` · adaptador `ResendEmailAdapter` · integración HTTP con Resend API | ✅ Done (PR #80) |
| US-4.5.3 | 4.5 | RF-NT-01 · RF-NT-03 | Política P-10 — `InscripcionConfirmada` → `SolicitarNotificacion` → email al atleta · template `inscripcion_confirmada` | ✅ Done (PR #81) |
| US-4.5.4 | 4.5 | RF-NT-04 | Política P-11 — `ResultadosPublicados` → email a todos los atletas de la disciplina · template `resultados_publicados` · `evento_fuente_id` compuesto `"{evento.id}:{atleta_id}"` | ✅ Done (PR #82) |
| US-4.5.5 | 4.5 | RF-NT-01 | Cableado P-10 al endpoint `POST /registro/inscripciones` · enrichment `Inscripcion` → `InscripcionConfirmada` en `src/app.py` · idempotencia por `inscripcion_id` | ✅ Done (PR #83) |

> DesignReviewer post-INC-4.5: 0 CRITICAL, 174 WARNING (+16 vs INC-4.4 — patrones ES/hexagonal esperados en BC Notificaciones).
> Reporte: `quality/reports/designreviewer/INC-4.5-report.txt`

---

## 17. US-IEDD SP4 INC-4.6 — Auditoría y Exportación

| US | Inc. | RFs / Decisiones cubiertos | Contenido principal | Estado |
|----|------|----------------------------|---------------------|--------|
| US-4.6.1 | 4.6 | PLAN-SP4 §INC-4.6 · ADR-001 · ADR-008 | Query `ObtenerAuditLog` por performance · endpoint `GET /competencia/{competencia_id}/performances/{atleta_id}/audit-log` · respuesta cronológica con `sequence`, `tipo`, `timestamp`, `datos` · acceso restringido a `organizador/admin` | ✅ Done |
| US-4.6.2 | 4.6 | PLAN-SP4 §INC-4.6 · ADR-001 · ADR-008 | Servicio `CalculadorHashCompetencia` · `CompetenciaFinalizada.hash_sha256` persistido en event store · cálculo canónico en política `P-08` antes del cierre · hash vacío conocido para disciplina sin performances | ✅ Done |
| US-4.6.3 | 4.6 | PLAN-SP4 §INC-4.6 · US-4.6.1 · US-4.6.2 | Rutas y pantallas de organizador para auditoría · lista de atletas por competencia · timeline puntual por performance · visibilidad y copia de `hash_sha256` cuando la disciplina está finalizada | ✅ Done |
| US-4.6.4 | 4.6 | PLAN-SP4 §INC-4.6 · US-4.6.2 · US-4.6.3 | Query `ExportarResultados` consolidada · endpoint `GET /resultados/{torneo_id}/export` · descarga `csv`/`json` con `Content-Disposition` · ACLs a Torneo, Registro y Competencia para torneo, atletas, estado e integridad | ✅ Done |

---

## 18. US-IEDD SP-ADJ-06 — Ajuste técnico y documental post-SP4 (pre-BL-004)

| US | Issues | Área | Descripción | Estado |
|----|--------|------|-------------|--------|
| US-ADJ-6.1 | FAZ→FAAS | `shared/`, `notificaciones/`, `competencia/` código | Renombrar acrónimo FAZ → FAAS en código (enum `Disciplina`, eventos, handlers, ports) | ✅ 2026-04-18 |
| US-ADJ-6.2 | FAZ→FAAS | `tests/` | Renombrar FAZ → FAAS en todos los tests y fixtures | ✅ 2026-04-18 |
| US-ADJ-6.3 | SOLID | `competencia/application/` | Eliminar `inspect.signature`; callback `on_finalizada` unificado en composition root | ✅ 2026-04-18 |
| US-ADJ-6.4 | DRY | `notificaciones/application/` | Eliminar duplicación P-10/P-11 y `@staticmethod` innecesario | ✅ 2026-04-18 |
| US-ADJ-6.5 | Arq. capas | `frontend/` | Corregir violaciones de capa en `GrillaPage` (imports directos API → hooks) | ✅ 2026-04-18 |
| US-ADJ-6.6 | FAZ→FAAS | `docs/` | Corrección acrónimo en 8 archivos de documentación (ubiquitous language) | ✅ 2026-04-18 (PR #90) |
| US-ADJ-6.7 | UAT | `tests/uat/`, `src/shared/`, `frontend/` | UAT SP4 (INC-4.4/4.5/4.6) · BUG-SP4-001/002 resueltos · UX fixes organizador | ✅ 2026-04-18 (PR #91) |

---

## 19. US-IEDD SP5 INC-5.1 — Panel del Organizador

> Estado al 2026-04-21: 6/6 US mergeadas a `develop`. UAT funcional ejecutada — 5 hallazgos resueltos en INC-5.1-ADJ.
> DesignReviewer consolidado INC-5.1: **0 CRITICAL · 208 WARNING** (`quality/reports/designreviewer/INC-5.1-report.txt`).

| US | Inc. | Contenido principal | Estado |
|----|------|---------------------|--------|
| US-5.1.1 | 5.1 | `CrearTorneoPage` + formulario + `POST /torneos` + `useAuthStore` organizador | ✅ Done (PR #95) |
| US-5.1.2 | 5.1 | `DetalleTorneoPage` + tabs (`Detalle`, `Inscriptos`, `Grilla`, `Jueces`, `Ejecucion`) + `AccionesPanel` (transiciones de fase) + `FaseBadge` | ✅ Done (PR #96) |
| US-5.1.3 | 5.1 | `InscriptosPanel` — lista de atletas inscriptos con estado AP (`AnunciadaAP` / `NoCompite`) | ✅ Done (PR #97) |
| US-5.1.4 | 5.1 | `GrillaPanel` — lista de disciplinas con botón generar/confirmar grilla por disciplina + estado `GrillaGenerada` / `GrillaConfirmada` | ✅ Done (PR #98) |
| US-5.1.5 | 5.1 | `JuecesPanel` + `TablaJueces` + `JuezSelector` — asignación de juez por disciplina (`PUT /torneos/{id}/disciplinas/{disc}/juez`) | ✅ Done (PR #99) |
| US-5.1.6 | 5.1 | `EjecucionPanel` — monitor de competencias activas con estado por disciplina + `GET /competencia?torneo_id={id}` | ✅ Done (PR #100) |

---

## 20. US-IEDD INC-5.1-ADJ — Ajuste post-UAT Panel del Organizador

> INC-5.1-ADJ resuelve 5 hallazgos funcionales detectados en la UAT de INC-5.1.
> Patrón SP-ADJ: plan en `docs/plans/inc-5.1-adj/PLAN-INC-5.1-ADJ.md`.
> HITO-26: cobertura asimétrica del Event Storming como causa de los hallazgos.

| US | Hallazgo UAT | Área | Descripción | Estado |
|----|-------------|------|-------------|--------|
| US-5.1.7 | UAT-5.1-03, UAT-5.1-05 | `DetalleTorneoPage` | Política de tabs por fase: `CREADO`→solo Detalle, `INSCRIPCION_ABIERTA`→+Inscriptos, `PREPARACION`→+Grilla+Jueces, `EJECUCION/PREMIACION/CERRADO`→todas; `CANCELADO`→resumen + mensaje, sin tabs operativas | ✅ Done (PR #101) |
| US-5.1.8 | UAT-5.1-01 | `TorneoCompetenciasPage` | Composición disciplinas + competencias: `GET /torneos/{id}/disciplinas` como fuente primaria; cruzar con competencias materializadas; card por disciplina aunque no exista `competencia_id` | ✅ Done (PR #102) |
| US-5.1.9 | UAT-5.1-02 | `JuecesPanel`, `TablaJueces` | Precondición grilla en asignación de jueces: selector habilitado solo si disciplina tiene `Competencia` en estado `GrillaGenerada`, `GrillaConfirmada`, `EnEjecucion` o `Finalizada` | ✅ Done (PR #103) |
| US-5.1.10 | UAT-5.1-04 | `AccionesPanel` | Normalización del campo `estado` en `fetchTorneo` — fix mismatch entre valor HTTP y enum `EstadoTorneo`; `EJECUCION` muestra `Iniciar premiacion`, nunca `Iniciar ejecucion` | ✅ Done (PR #104) |

---

## 21. US-IEDD SP5 INC-5.2 — Ejecución por Disciplina

> Estado al 2026-04-22: 2/2 US mergeadas a `develop`. SP-ADJ-08 resuelve hallazgos UAT.
> DesignReviewer consolidado INC-5.2: **0 CRITICAL · 215 WARNING** (`quality/reports/designreviewer/INC-5.2-report.txt`).

| US | Inc. | Contenido principal | Estado |
|----|------|---------------------|--------|
| US-5.2.1 | 5.2 | `TorneoCompetenciasPage` — vista maestro-detalle: lista todas las disciplinas del torneo con estado, juez asignado y progreso; al seleccionar una disciplina, abre detalle con acción `Habilitar disciplina` (`POST /competencia/{id}/iniciar`) | ✅ Done (PR #105) |
| US-5.2.2 | 5.2 | Acción `Finalizar prueba` por disciplina — habilitada solo si no hay performances pendientes; `PATCH /competencia/{id}/finalizar`; distingue cierre manual vs. automático (P-08) | ✅ Done (PR #106) |

---

## 22. SP-ADJ-08 — Ajuste post-UAT INC-5.2

> SP-ADJ-08 resuelve 8 hallazgos (UAT-5.2-01..08) detectados en la UAT de cierre de INC-5.2.
> Plan: `docs/plans/sp-adj-08/PLAN-SP-ADJ-08.md`.

| US | Hallazgo UAT | Área | Descripción | Estado |
|----|-------------|------|-------------|--------|
| US-ADJ-8.2 | UAT-5.2-02, UAT-5.2-05, UAT-5.2-07 | `TorneoCompetenciasPage`, `AccionesPanel` | Selector de grilla filtrado por `GET /torneos/{id}/disciplinas`; `Pasar a premiacion` habilitado solo si todas las competencias esperadas están `Finalizada` | ✅ Done (PR #107) |
| US-ADJ-8.1 | UAT-5.2-01, UAT-5.2-03, UAT-5.2-04, UAT-5.2-06, UAT-5.2-07 | Paneles del organizador | Estados vacío/loading/error claros; mensajes de ejecución accionables; disciplina seleccionada destacada; lenguaje de fase preciso (`Pasar a premiacion` / `Cerrar torneo`) | ✅ Done (PR #108) |
| US-ADJ-8.3 | UAT-5.2-08 | `AccionesPanel` | Cancelar torneo en zona de peligro con modal de confirmación fuerte — habilita acción solo si el usuario escribe el nombre exacto del torneo | ✅ Done (PR #109) |

---

## 23. US-IEDD SP5 INC-5.3 — Gestión de usuarios y roles

> Estado al 2026-04-23: 2/2 US mergeadas a `develop`.
> DesignReviewer INC-5.3: **0 CRITICAL · 215 WARNING** (`quality/reports/designreviewer/INC-5.3-report.txt`).
> Nota: US-5.3.2 adelantó scope de INC-5.4 — `InscripcionPanel` con mutación implementado dentro de `AtletaDashboardPage`.

| US | Inc. | Contenido principal | Estado |
|----|------|---------------------|--------|
| US-5.3.1 | 5.3 | `UsuariosPage` (organizador) — listar todos los usuarios del sistema + formulario de creación con rol; backend: `GET /auth/usuarios` con `rol` opcional | ✅ Done (PR #110) |
| US-5.3.2 | 5.3 | `AtletaDashboardPage` — perfil (email/rol del JWT) + torneos en `INSCRIPCION_ABIERTA` + `InscripcionPanel` con selección de disciplinas (`POST /registro/inscripciones`) | ✅ Done (PR #111) |

---

## 24. US-IEDD SP5 INC-5.4 — Identidad Extendida

> Estado al 2026-04-24: 3/3 US mergeadas a `develop`.
> DesignReviewer INC-5.4: **0 CRITICAL · 222 WARNING** (`quality/reports/designreviewer/INC-5.4-report.txt`).
> +7 WARNING respecto a INC-5.3 (215→222), atribuidos a nuevos endpoints en `identidad/api/router.py`.

| US | Inc. | Contenido principal | Estado |
|----|------|---------------------|--------|
| US-5.4.1 | 5.4 | Auto-registro público — extensión modelo `Usuario` (nombre/apellido) + `POST /auth/registro` (rol ≠ ADMIN) + página `/registro` en frontend | ✅ Done (PR #112) |
| US-5.4.2 | 5.4 | Cambiar contraseña — `POST /auth/cambiar-password` (usuario autenticado) + handler `CambiarPasswordHandler` | ✅ Done (PR #113) |
| US-5.4.3 | 5.4 | Recuperar contraseña — `TokenServicePort` + JWT firmado exp 1h + `POST /auth/forgot-password` + `POST /auth/reset-password` + email Resend + páginas `/recuperar-password` y `/reset-password` | ✅ Done (PR #114) |

---

## 25. US-IEDD SP5 INC-5.5 — Portal Atleta e Inscripción con AP

> Estado al 2026-04-26: 2/2 US mergeadas a `develop` + fix UAT (PR #122).
> Scope redefinido post-reversión 2026-04-25: US-5.5.1/US-5.5.2 cubren portal atleta completo y vista del organizador (inscriptos + estado AP), no rankings/FAAS.
> DesignReviewer INC-5.5: **0 CRITICAL · 227 WARNING** (`quality/reports/designreviewer/INC-5.5-report.txt`).
> +5 WARNING respecto a INC-5.4 (222→227); todos son WARNING estructurales conocidos (LongMethod, DataClumps, LCOM).

| US | Inc. | Contenido principal | Estado |
|----|------|---------------------|--------|
| US-5.5.1 | 5.5 | Portal atleta completo: shell dark + bottom tab bar + wizard inscripción 3 pasos + S-05 Mis inscripciones + S-06 Declarar/Modificar AP por disciplina | ✅ Done (PR #120) |
| US-5.5.2 | 5.5 | Vista del organizador — inscriptos con datos completos (nombre, disciplinas, estado AP) integrada en la navegación UX aprobada del panel organizador | ✅ Done (PR #121) |
| fix/uat-portal-atleta-ap | 5.5 | 13 hallazgos UAT corregidos: cross-BC identity (nombre/apellido desde identidad), AP flow (fechas, estados, carga/consulta), sync frontend | ✅ Done (PR #122) |

---

## 26. US-IEDD SP5 INC-5.6 — Algoritmo de Puntaje y Rankings por Categoría/Género

> Estado al 2026-04-28: 6/6 US mergeadas a `develop`.
> DesignReviewer INC-5.6 + SP-ADJ-09: **0 CRITICAL · 252 WARNING** (+25 vs INC-5.5 · `quality/reports/designreviewer/INC-5.6-report.txt`).
> +25 WARNING: LCOM/FanOut en RankingCompetencia/RankingOverall/AlgoritmoPuntajeFAAS (INC-5.6) + FeatureEnvy DeclararAPInscripcionHandler (SP-ADJ-09). Hallazgos en `.work/revision-sp5/designreviewer-hallazgos-pendientes.md`.

| US | Inc. | Contenido principal | Estado |
|----|------|---------------------|--------|
| US-5.6.1 | 5.6 | Puerto `AlgoritmoPuntaje` (ABC) + `AlgoritmoPuntajeFAAS` con fórmulas FAAS para distancia (DNF/DYN/DBF) y tiempo (STA/SPE) — 23 tests | ✅ Done (PR #123) |
| US-5.6.2 | 5.6 | `TipoReglamento` VO (FAAS/CMAS/AIDA) en `Torneo` + migración SQLite + DI en `CalcularRankingHandler` — 15 tests | ✅ Done (PR #124) |
| US-5.6.3 | 5.6 | `RankingCompetencia` extendido: calcula y almacena `puntos: Decimal` por atleta usando `AlgoritmoPuntaje`, agrupado por `Categoria` — 84 tests | ✅ Done (PR #125) |
| US-5.6.4 | 5.6 | `RankingOverall` por categoría/género — `puntos_overall = Σ puntos_disciplina`; `penalizacion_ausente=0` (FAAS) — 91 tests | ✅ Done (PR #126) |
| US-5.6.5 | 5.6 | UI `ResultadosPage` (`/organizador/resultados`): selector torneo/disciplina + tabla por OT con género, categoría, AP, RP, tarjeta y puntos | ✅ Done (PR #127) |
| US-5.6.6 | 5.6 | UI podios — 6 divisiones fijas (SENIOR M/F, MASTER M/F, JUNIOR M/F); overall bloqueado hasta cerrar todas las disciplinas | ✅ Done (PR #128) |

---

## 27. SP-ADJ-09 — Refactoring UX Organizador

> SP-ADJ-09 resuelve gaps de navegación y consistencia visual del portal organizador post-INC-5.6.
> Plan: `docs/plans/sp-adj-09/PLAN-SP-ADJ-09.md`.
> DesignReviewer SP-ADJ-09: ⏳ pendiente.

| US | Área | Descripción | Estado |
|----|------|-------------|--------|
| US-ADJ-9.1 | `frontend/` | Shell dark del organizador — layout base con sidebar y header consistente | ✅ Done (PR #129) |
| US-ADJ-9.2 | `frontend/` | Routing organizador reestructurado — rutas anidadas y navegación coherente entre secciones | ✅ Done (PR #130) |
| US-ADJ-9.3 | `frontend/` | Home del organizador formalizado — vista de entrada con acceso a torneos activos | ✅ Done (PR #131) |
| US-ADJ-9.4 | `frontend/` | Dashboard operativo — resumen de estado del torneo en ejecución | ✅ Done (PR #132) |
| US-ADJ-9.5 | `frontend/` | Resultados y shell organizador reencuadrados — integración de `ResultadosPage` en la navegación del panel | ✅ Done (PR #133) |
| US-ADJ-9.6 | `frontend/` | Arquitectura UX organizador formalizada — separación de shell, layout y páginas | ✅ Done (develop) |
| US-ADJ-9.7 | `registro/`, `frontend/` | Declarar AP en inscripción — atleta puede declarar/modificar AP desde el wizard de inscripción | ✅ Done (PR #136) |

---

## 28. US-IEDD SP5 INC-5.7 — Portal del Atleta

> Estado al 2026-05-01: 4/4 US mergeadas a `develop`. UAT visual aprobado.
> DesignReviewer INC-5.7: **0 CRITICAL · 256 WARNING** (+4 vs INC-5.6 · `quality/reports/designreviewer/INC-5.7-report.txt`).
> +4 WARNING: complejidad `_rankear_categoria` en `ObtenerRankingProvisionalHandler` — aceptado como conocido.
> Fix incluido: resultados provisionales via fallback en `GET /resultados/{id}/ranking` — lee `competencia.db` en tiempo real cuando `resultados.db` está vacío.
> INC-5.8 desestimado — contenido absorbido en SP6.

| US | Inc. | Contenido principal | Estado |
|----|------|---------------------|--------|
| US-5.7.1 | 5.7 | Mis torneos — lista de torneos inscriptos del atleta con estado actual + fix inscripción condicional | ✅ Done (PR #137) |
| US-5.7.2 | 5.7 | Mi grilla — posición del atleta (OT + línea) por disciplina inscripta | ✅ Done (PR #138) |
| US-5.7.3 | 5.7 | Mis resultados — ResultHero (RP, tarjeta, puntos) + DisciplinaPendienteCard por disciplina | ✅ Done (PR #139) |
| US-5.7.4 | 5.7 | Rankings y podios — tabla de ejecución + podio por disciplina en la que participó el atleta | ✅ Done (PR #140) |

---

## 29. US-IEDD SP6 INC-6.1 — Ajustes Juez

> Estado al 2026-05-04: 4/5 US mergeadas a `develop`. INC-6.1 en curso.
> Quality gates: frontend-only · CodeGuard N/A (sin cambios Python) · DesignReviewer al cierre del INC.

| US | Inc. | Contenido principal | Estado |
|----|------|---------------------|--------|
| US-6.1.1 | 6.1 | Fix `canSubmitBko` (limpieza remanente) + reorden flujo juez: tarjeta (paso 5) → marca (paso 6) · `usePerformanceFlow.ts` + `PerformanceFlowPage.tsx` | ✅ Done (PR #143) |
| US-6.1.2 | 6.1 | Colores tarjeta outline/filled (MUX-02) + heading paso 5 corregido · MUX-05 ya estaba resuelto en PerformanceFlowPage · `StepTarjeta.tsx` | ✅ Done (PR #144) |
| US-6.1.3 | 6.1 | Grilla ordenada por estado + keypad visible móvil · MUX-03 ya resuelto · MUX-01: `RpSelector.tsx` space-y-2 + py-2 en keypad | ✅ Done (PR #145) |
| US-6.1.4 | 6.1 | Rediseño inicio juez + STA mm:ss + tarjeta amarilla (UI-JUE-01 + MUX-08 + MUX-07) · `DisciplinasPage.tsx`: "Mis asignaciones" + sin Password · `utils/marca.ts`: " min" suffix · `StepRevision.tsx`: labels BLANCA/ROJA | ✅ Done (PR #146) |
| US-6.1.5 | 6.1 | AtletaCard compacta en paso 5 (MUX-06) | ⏳ Pendiente |

---

## 30. Trazabilidad: Discrepancias → US → Documentos a actualizar

Hallazgos del análisis HITO-17 sobre dataset real "Apnea Indoor Buenos Aires 2025".

| DISC | Descripción | Severidad | US-ADJ | Docs a actualizar |
|------|-------------|-----------|--------|-------------------|
| DISC-01 | Ranking flat vs. por (disciplina, categoría, sexo) | CRÍTICO | US-ADJ-4.5 | `domain-model.md` §Resultados · `context-map.md` §ACLs · `05-requerimientos_funcionales.md` RF-PM-05 |
| DISC-02 | `DYNB` ≠ `DBF` — acrónimo incorrecto | CRÍTICO | US-ADJ-4.1 | `domain-model.md` §Disciplina · `05-requerimientos_funcionales.md` RF-GT-02 |
| DISC-03 | `SPE2X50` ≠ `SPE` — acrónimo incorrecto | CRÍTICO | US-ADJ-4.1 | `domain-model.md` §Disciplina · `05-requerimientos_funcionales.md` RF-GT-02 |
| DISC-04 | Orden grilla STA invertido (`orden_ascendente=False`) | CRÍTICO | US-ADJ-4.2 | `event-storming-competencia.md` §P-01 · `domain-model.md` §DisciplinaDescriptor |
| DISC-05 | `Atleta` sin campo `club` | MEDIO | US-ADJ-4.4 | `domain-model.md` §Registro diagrama `Atleta` · `05-requerimientos_funcionales.md` RF-IN |
| DISC-06 | APs de tiempo en `MM:SS` sin conversión en dominio | MEDIO | US-ADJ-4.6 | `domain-model.md` §Shared VOs · `CLAUDE.md` §8 |
| DISC-07 | `JUVENIL` ≠ `JUNIOR` — nomenclatura AIDA | MEDIO | US-ADJ-4.3 | `domain-model.md` §Registro `Categoria` · `CLAUDE.md` §8 |
| DISC-08 | RP > AP sin documentar como invariante permitido | BAJO | — (docstring) | `event-storming-competencia.md` §INV-P · specs US-1.2.3 |
| DISC-09 | Coma decimal en PDFs de la federación | BAJO | — | seed UAT / scripts de ingesta |
| DISC-10 | Intervalo OT real difiere de valores en tests | BAJO | — | tests SP2 UAT (seed) |

---

## 31. Cobertura Total

| Área | Total RFs | Definidos | Pendientes | Fuera de alcance v1 |
|------|:---------:|:---------:|:----------:|:-------------------:|
| Gestión del Torneo (RF-GT) | 7 | 7 | 0 | 0 |
| Inscripción (RF-IN) | 10 | 9 | 0 | 1 |
| Preparación (RF-PR) | 8 | 8 | 0 | 0 |
| Ejecución (RF-EJ) | 10 | 9 | 1 | 1 |
| Resultados (RF-PM) | 6 | 5 | 0 | 1 |
| Usuarios (RF-US) | 5 | 5 | 0 | 0 |
| Notificaciones (RF-NT) | 4 | 3 | 1 | 0 |
| Integración (RF-IG) | 4 | 0 | 0 | 4 |
| **Total** | **54** | **45** | **2** | **7** |

> **85% de RFs completamente definidos.** Los pendientes reales son decisiones
> funcionales abiertas. La integración FAAS/importación CSV está diferida fuera
> de SP5/v1.0 según `docs/plans/sp5/PLAN-SP5.md`.

---

## 32. US → Tests

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
| US-3.2.1 | unit/identidad/domain + unit/identidad/application + integration/identidad + features/US-3.2.1 | ✅ 36 tests (100%) |
| US-3.2.2 | unit/registro + integration/registro + features/US-3.2.2 | ✅ 27 tests (100%) |
| US-3.2.3 | unit/registro + integration/registro + features/US-3.2.3 | ✅ 31 tests |
| US-3.3.1 | unit/competencia/domain + unit/competencia/application + integration/competencia + features/US-3.3.1 | ✅ implementada |
| US-3.3.2 | unit/competencia/application + integration cross-BC + features/US-3.3.2 | ✅ implementada |
| US-3.4.1 | unit/torneo/domain + integration/torneo + features/US-3.4.1-asignar-disciplinas-juez | ✅ 35 tests |
| US-3.4.2 | unit/identidad/api + features/US-3.4.2-auth-jwt-middleware | ✅ 15 tests |
| US-3.5.1 | unit/resultados/domain + unit/resultados/application + integration/resultados + features/US-3.5.1-ranking-overall | ✅ implementada |
| US-3.5.2 | unit/app + integration/p09 + features/US-3.5.2-politica-p09 | ✅ 17 tests |
| US-3.5.3 | unit/resultados/application + unit/resultados/api + integration/resultados + features/US-3.5.3-api-overall | ✅ 10 tests focalizados |
| US-4.1.1 | unit/competencia/domain + unit/competencia/application + integration/competencia + features/US-4.1.1 | ✅ 102 passed |
| US-4.1.2 | unit/competencia/domain + unit/competencia/application + unit/resultados + integration/resultados + features/US-4.1.2 | ✅ 107 passed |
| US-4.1.3 | unit/shared + unit/torneo + integration/torneo + features/US-4.1.3 | ✅ 73 passed |
| US-4.1.4 | unit/competencia/domain + integration/competencia + features/US-4.1.4 | ✅ 68 passed |
| US-4.1.5 | unit/competencia/domain + integration/competencia | ✅ 82 passed (BDD waiver — refactoring interno sin comportamiento nuevo) |
| US-4.1.6 | unit/competencia/application | ✅ 36 passed (BDD waiver — refactoring handlers) |
| US-4.1.7 | unit/competencia/domain + unit/resultados/domain | ✅ 32 passed (BDD waiver — refactoring estructural) |
| US-4.1.8 | unit/torneo/domain + unit/competencia/domain + unit/competencia/infrastructure | ✅ 91 passed (BDD waiver — refactoring estructural) |
| US-4.3.1 | frontend (build + lint) · validación manual navegador | ✅ UAT INC-4.3 2026-04-12 |
| US-4.3.2 | integration/competencia (smoke TestClient) · frontend (build + lint) · validación manual navegador | ✅ UAT INC-4.3 2026-04-12 |
| US-4.3.3 | integration/competencia (smoke TestClient) · frontend (build + lint) · validación manual navegador | ✅ UAT INC-4.3 2026-04-12 |
| US-4.3.4 | unit/competencia/domain (EnRevision + ResolverRevision) · integration/competencia · frontend (build + lint) · validación manual navegador | ✅ UAT INC-4.3 2026-04-12 |
| US-4.3.5 | frontend (build + lint) · validación manual navegador (BDD waiver — frontend solo) | ✅ UAT INC-4.3 2026-04-12 |
| US-4.4.1 | frontend (build + lint) · UAT INC-4.4 iPhone (BDD waiver — frontend offline-first) | ✅ UAT SP4 2026-04-18 |
| US-4.4.2 | frontend (build + lint) · UAT INC-4.4 iPhone | ✅ UAT SP4 2026-04-18 |
| US-4.4.3 | frontend (build + lint) · UAT INC-4.4 iPhone (Background Sync) | ✅ UAT SP4 2026-04-18 |
| US-4.5.1 | unit/notificaciones/domain + integration/notificaciones | ✅ Done (PR #79) |
| US-4.5.2 | unit/notificaciones/infrastructure (ResendEmailAdapter) | ✅ Done (PR #80) |
| US-4.5.3 | unit/notificaciones/application (P-10) + UAT SP4 email real | ✅ UAT SP4 2026-04-18 |
| US-4.5.4 | unit/notificaciones/application (P-11) | ✅ Done (PR #82) |
| US-4.5.5 | integration (cableado P-10 en composition root) | ✅ Done (PR #83) |
| US-4.6.1 | unit/competencia/application (ObtenerAuditLog) + integration/competencia | ✅ Done |
| US-4.6.2 | unit/competencia/domain (CalculadorHashCompetencia) + integration/competencia | ✅ Done |
| US-4.6.3 | frontend (build + lint) · UAT INC-4.6 iPad organizador | ✅ UAT SP4 2026-04-18 |
| US-4.6.4 | unit/resultados/application (ExportarResultados) + integration/resultados · UAT INC-4.6 | ✅ UAT SP4 2026-04-18 |
| US-5.1.1 | frontend (build + eslint src) · UAT INC-5.1 2026-04-21 | ✅ Done (PR #95) |
| US-5.1.2 | frontend (build + eslint src) · UAT INC-5.1 2026-04-21 | ✅ Done (PR #96) |
| US-5.1.3 | frontend (build + eslint src) · UAT INC-5.1 2026-04-21 | ✅ Done (PR #97) |
| US-5.1.4 | frontend (build + eslint src) · UAT INC-5.1 2026-04-21 | ✅ Done (PR #98) |
| US-5.1.5 | frontend (build + eslint src) · UAT INC-5.1 2026-04-21 | ✅ Done (PR #99) |
| US-5.1.6 | frontend (build + eslint src) · UAT INC-5.1 2026-04-21 | ✅ Done (PR #100) |
| US-5.1.7 | frontend (build + eslint src) · UAT regresión INC-5.1-ADJ 2026-04-22 (BDD waiver — frontend) | ✅ Done (PR #101) |
| US-5.1.8 | frontend (build + eslint src) · UAT regresión INC-5.1-ADJ 2026-04-22 (BDD waiver — frontend) | ✅ Done (PR #102) |
| US-5.1.9 | frontend (build + eslint src) · UAT regresión INC-5.1-ADJ 2026-04-22 (BDD waiver — frontend) | ✅ Done (PR #103) |
| US-5.1.10 | frontend (build + eslint src) · UAT regresión INC-5.1-ADJ 2026-04-22 (BDD waiver — frontend) | ✅ Done (PR #104) |
| US-5.2.1 | frontend (build + eslint src) · integration/competencia (`GET /competencia?torneo_id`) · UAT INC-5.2 2026-04-22 (BDD waiver — frontend) | ✅ Done (PR #105) |
| US-5.2.2 | frontend (build + eslint src) · integration/competencia (`PATCH /competencia/{id}/finalizar`) · UAT INC-5.2 2026-04-22 (BDD waiver — frontend) | ✅ Done (PR #106) |
| US-ADJ-8.2 | frontend (build + eslint src) · UAT regresión SP-ADJ-08 2026-04-22 (BDD waiver — frontend) | ✅ Done (PR #107) |
| US-ADJ-8.1 | frontend (build + eslint src) · UAT regresión SP-ADJ-08 2026-04-22 (BDD waiver — frontend) | ✅ Done (PR #108) |
| US-ADJ-8.3 | frontend (build + eslint src) · UAT regresión SP-ADJ-08 2026-04-22 (BDD waiver — frontend) | ✅ Done (PR #109) |
| US-5.3.1 | unit/identidad/api (`test_listar_usuarios.py`) · integration/identidad (`test_sqlite_usuario_repository.py`) · `tests/features/US-5.3.1-gestion-usuarios.feature` · frontend (build + eslint) | ✅ Done (PR #110) |
| US-5.3.2 | `tests/features/US-5.3.2-vista-atleta.feature` · frontend (build + eslint) · BDD waiver — frontend puro | ✅ Done (PR #111) |
| US-5.4.1 | unit/identidad/application (`registrar_usuario`) · integration/identidad · `tests/features/US-5.4.1` · frontend (build + eslint) | ✅ Done (PR #112) |
| US-5.4.2 | unit/identidad/application (`test_handlers.py` CambiarPassword) · integration/identidad · `tests/features/US-5.4.2` | ✅ Done (PR #113) |
| US-5.4.3 | unit/identidad/api (`test_reset_password.py`) · unit/identidad/application (`test_handlers.py` Reset) · `tests/features/US-5.4.3-recuperar-password.feature` · frontend (build + eslint) | ✅ Done (PR #114) |
| US-5.5.1 | frontend (build + eslint) · UAT funcional INC-5.5 2026-04-26 (BDD waiver — frontend puro) | ✅ Done (PR #120) |
| US-5.5.2 | unit/registro/application (`inscriptos_detalle`) · integration/registro · frontend (build + eslint) · UAT INC-5.5 2026-04-26 | ✅ Done (PR #121) |
| US-5.6.1 | unit/resultados/domain (`AlgoritmoPuntajeFAAS`) · integration/resultados · 23 tests | ✅ Done (PR #123) |
| US-5.6.2 | unit/torneo/domain (`TipoReglamento`) · integration/torneo (migración SQLite) · `tests/features/US-5.6.2` · 15 tests | ✅ Done (PR #124) |
| US-5.6.3 | unit/resultados/domain + unit/resultados/application + integration/resultados + `tests/features/US-5.6.3` · 84 tests | ✅ Done (PR #125) |
| US-5.6.4 | unit/resultados/domain + unit/resultados/application + integration/resultados + `tests/features/US-5.6.4` · 91 tests | ✅ Done (PR #126) |
| US-5.6.5 | frontend (build + eslint) · UAT INC-5.6 (BDD waiver — frontend puro) | ✅ Done (PR #127) |
| US-5.6.6 | frontend (build + eslint) · UAT INC-5.6 (BDD waiver — frontend puro) | ✅ Done (PR #128) |
| US-ADJ-9.1..9.6 | frontend (build + eslint) · UAT regresión SP-ADJ-09 (BDD waiver — frontend puro) | ✅ Done (PRs #129–#133, develop) |
| US-ADJ-9.7 | unit/registro/application + integration/registro · frontend (build + eslint) | ✅ Done (PR #136) |
| US-5.7.1 | frontend (build + eslint) · UAT visual INC-5.7 (BDD waiver — frontend puro) | ✅ Done (PR #137) |
| US-5.7.2 | frontend (build + eslint) · UAT visual INC-5.7 (BDD waiver — frontend puro) | ✅ Done (PR #138) |
| US-5.7.3 | frontend (build + eslint) · UAT visual INC-5.7 (BDD waiver — frontend puro) | ✅ Done (PR #139) |
| US-5.7.4 | frontend (build + eslint) · UAT visual INC-5.7 (BDD waiver — frontend puro) | ✅ Done (PR #140) |
| US-6.1.1 | frontend (build) · `tests/features/US-6.1.1-flow-juez.feature` · 362 unit/competencia sin regresiones (BDD waiver — frontend puro) | ✅ Done (PR #143) |
| US-6.1.2 | frontend (build + eslint) · BDD waiver — frontend puro | ✅ Done (PR #144) |
| US-6.1.3 | frontend (build + eslint) · BDD waiver — frontend puro | ✅ Done (PR #145) |
| US-6.1.4 | frontend (build + eslint) · BDD waiver — frontend puro | ✅ Done (PR #146) |

---

## 33. US → ADR

| US-IEDD | ADR relacionado | Relación |
|---------|----------------|---------|
| US-1.1.1 | ADR-001..004 | Stack tecnológico y arquitectura hexagonal |
| US-1.1.1 | ADR-006 | Estructura BC-first — esqueleto de `src/competencia/` |
| US-1.1.1 | ADR-007 | SQLite como motor de persistencia — `data/competencia.db` |
| US-1.1.1 | ADR-008 | Event Store como tabla `events` append-only en SQLite |
| US-1.1.1 | ADR-009 | Migraciones Alembic en `competencia/infrastructure/migrations/` |
| US-1.2.x | ADR-005 | Event Sourcing en BC Competencia |
| US-4.1.2 | ADR-014 | Penalizaciones acumulables — modelo de deducción N×3m en tarjeta blanca |
| US-4.5.2 | ADR-016 | Resend como proveedor email — puerto `EmailPort` + adaptador `ResendEmailAdapter` |

---

*v1.34 — 2026-05-04: US-6.1.4 ✅ (PR #146) · §29 y US→Tests actualizados*
*v1.33 — 2026-05-04: US-6.1.3 ✅ (PR #145) · §29 y US→Tests actualizados*
*v1.32 — 2026-05-03: US-6.1.2 ✅ (PR #144) · §29 y US→Tests actualizados*
*v1.31 — 2026-05-03: SP6 iniciado · §29 INC-6.1 agregado · US-6.1.1 ✅ (PR #143) · US→Tests US-6.1.1 agregado · header actualizado*
*v1.30 — 2026-05-01: INC-5.7 cerrado (§28 nuevo · 4/4 US ✅ · PRs #137–#140 · DesignReviewer 0 CRITICAL · 256 WARNING) · INC-5.8 desestimado (absorbido SP6) · §§ renumerados 29..33 · US→Tests US-5.7.x · §2 cobertura actualizada*
*v1.29 — 2026-04-29: INC-5.6 cerrado (§26 nuevo · 6/6 US ✅ · PRs #123–#128 · DesignReviewer 0 CRITICAL · 252 WARNING) · SP-ADJ-09 cerrado (§27 nuevo · 7/7 US ✅ · PRs #129–#136) · §§ renumerados 28..31 · US→Tests US-5.5.x + US-5.6.x + US-ADJ-9.x · §2 cobertura actualizada*
*v1.27 — 2026-04-26: INC-5.5 cerrado (§25 nuevo · 2/2 US ✅ + fix UAT · PRs #120–#122 · DesignReviewer 0 CRITICAL · 227 WARNING)*
*Documento creado: 2026-03-19 — Semana 0, Fase 0*
*v1.1 — 2026-03-20: US-1.1.1 actualizada a BC-first · ADR-006 agregado · FAZ → FAAS*
*v1.2 — 2026-03-28: SP-ADJ-01 agregado (§7) · secciones SP1 renumeradas · numeración de §§ corregida*
*v1.3 — 2026-03-28: SP-ADJ-02-code agregado (§8) · US-ADJ-2.6/2.7/2.8 documentadas*
*v1.4 — 2026-03-29: SP3 §9 agregado · US-3.1.1 implementada*
*v1.5 — 2026-03-30: US-3.1.2 implementada — API REST Torneo completa*
*v1.6 — 2026-04-02: SP3 completado a nivel US — §9 y tabla US→Tests actualizadas hasta US-3.5.3*
*v1.10 — 2026-04-03: SP-ADJ-04 completado (§2, §11), US-ADJ-4.6 implementada, RF-IN-10 incorporado a cobertura total (§14)*
*v1.16 — 2026-04-15: INC-4.4 ✅ (US-4.4.1..3 Done · fix robustez) · INC-4.5 ✅ §16 agregado (4 US · PRs #79–82) · §§ renumerados 17..20 · US→ADR ADR-016*
*v1.17 — 2026-04-18: SP4 cerrado (v0.5.0 · BL-004) · SP-ADJ-06 §18 agregado (7 US) · US→Tests completado (INC-4.4/4.5/4.6) · §§ renumerados 18..22 · §2 cobertura actualizada*
*v1.18 — 2026-04-20: SP5 iniciado · US-5.1.1 implementada · trazabilidad frontend de creacion de torneo agregada*
*v1.19 — 2026-04-20: US-5.1.2 implementada · trazabilidad frontend de gestion de fases agregada*
*v1.20 — 2026-04-20: US-5.1.3 implementada · trazabilidad frontend de inscriptos/AP agregada*
*v1.22 — 2026-04-22: INC-5.2 cerrado (§21 nuevo · DesignReviewer 0 CRITICAL · 215 WARNING) · SP-ADJ-08 §22 · §§ renumerados 23..26 · US→Tests US-5.2.1..5.2.2 · US-ADJ-8.1..8.3*
*v1.25 — 2026-04-24: INC-5.4 cerrado (§24 nuevo · DesignReviewer 0 CRITICAL · 222 WARNING) · §§ renumerados 25..28 · US→Tests US-5.4.1..5.4.3 · PRs #112..#114*
*v1.24 — 2026-04-23: INC-5.3 cerrado (§23 nuevo · DesignReviewer 0 CRITICAL · 215 WARNING) · §§ renumerados 24..27 · US→Tests US-5.3.1..5.3.2 · nota scope adelantado INC-5.4 en US-5.3.2*
*v1.23 — 2026-04-23: matriz reconciliada contra PLAN-SP5 vigente · RF-IG/RF-IN-07 movidos a futuro fuera de scope SP5 · RF-PM y RF-IN-05/06 marcados como parciales con exposición final en INC-5.4/5.5*
*v1.21 — 2026-04-22: INC-5.1 cerrado (§19 nuevo · DesignReviewer 0 CRITICAL · 208 WARNING) · INC-5.1-ADJ §20 · §§ renumerados 21..24 · US→Tests US-5.1.1..5.1.10 · §2 cobertura actualizada · HITO-26*
*v1.15 — 2026-04-13: INC-4.4 especificado (§15 nuevo — 3 US offline-first) · §§ renumerados 16..19 · §2 cobertura actualizada*
*v1.14 — 2026-04-13: INC-4.3 completado (§14 — 5/5 US ✅, UAT BA 2025) · RF-NT §3.7 INC corregido (4.2→4.5) · US-4.3.x en §18*
*v1.13 — 2026-04-11: US-4.2.2 implementada y mergeada · DesignReviewer consolidado INC-4.2 OK · validación manual pendiente*
*v1.12 — 2026-04-11: SP4 INC-4.2 §13 agregado · US-4.2.1 implementada (scaffold frontend) · §§ renumerados*
*v1.11 — 2026-04-09: SP4 INC-4.1 agregado (§12 nuevo) · RF-GT-02 y RF-PR-05 actualizados · §13-§16 renumerados · US-4.1.x en §15 y §16*
*Fuentes: 05-requerimientos_funcionales.md · Context Map v1.1 · estrategia-desarrollo-bc.md · ES Competencia*
*Mantenido por: Claude Cowork + Victor Valotto*
