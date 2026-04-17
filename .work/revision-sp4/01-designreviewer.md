# Revisión de Calidad — Cierre SP4
## DesignReviewer — Hallazgos y Análisis

**Fecha:** 2026-04-16
**Comando:** `designreviewer src/ --config pyproject.toml`
**Resultado:** 0 CRITICAL · 196 WARNING · 0 INFO
**Reporte fuente:** `quality/reports/designreviewer/INC-4.6-report.txt`

---

## Resultado global

**0 CRITICAL** — no hay bloqueantes. El cierre formal de BL-004 no está impedido.

Thresholds vigentes en `pyproject.toml` (calibrados en SP2/INC-3.3, sin cambios en SP4):

| Parámetro | Valor | Justificación registrada |
|-----------|-------|--------------------------|
| `max_cbo` | 25 | Performance/Competencia crecen legítimamente con cada US |
| `max_wmc` | 65 | Competencia WMC=64 al cerrar INC-3.3 |
| `max_god_object_lines` | 540 | Competencia.py ~535 líneas al cierre SP2 |
| `max_god_object_methods` | 28 | Performance 22 métodos al cierre INC-2.1 |

---

## Distribución de warnings por paquete

| Paquete | Warnings | Tendencia vs SP3 |
|---------|:--------:|-----------------|
| commands | 44 | ↑ +8 (nuevos handlers INC-4.5 y INC-4.6) |
| aggregates | 41 | ↑ +5 (Notificacion nuevo) |
| api | 31 | ↑ +12 (endpoints nuevos INC-4.3/4.6) |
| queries | 22 | ↑ +12 (ObtenerAuditLog, ExportarResultados nuevos) |
| repositories | 19 | → estable |
| event_store | 8 | ↑ +2 (SQLiteNotificacionEventStore nuevo) |
| entities | 6 | → estable (GrillaDeSalida) |
| src | 6 | ↑ +3 (app.py creció con Notificaciones) |
| policies | 4 | ↑ +4 (P-10, P-11 nuevos — paquete antes vacío) |
| email | 3 | ↑ +3 (ResendEmailAdapter, LoggingEmailAdapter nuevos) |
| events | 3 | → estable |
| templates | 3 | ↑ +3 (templates email nuevos — paquete antes vacío) |
| value_objects | 4 | → estable |
| ports | 1 | → estable |
| application | 1 | → estable |

**SP3 → SP4: 111 → 196 warnings (+85).** El incremento es proporcional al código nuevo:
BC Notificaciones completo (aggregate + políticas + templates + adaptadores) + INC-4.6
(audit log, exportación) suman ~15 clases nuevas. Muchos warnings corresponden a esas
clases nuevas, no a degradación de código pre-existente.

---

## Patrones de warnings — clasificación

### Patrón A — Falsos positivos estructurales (no requieren acción)

| Analyzer | Clases afectadas | Por qué es falso positivo |
|----------|-----------------|--------------------------|
| FeatureEnvy en commands/ | Todos los handlers | Patrón CQRS: el handler delega al aggregate por diseño |
| FeatureEnvy en queries/ | Todos los handlers | Ídem |
| FeatureEnvy en repositories/ | SQLiteInscripcionRepository, SQLiteAtletaRepository, etc. | Patrón Repository: accede a campos del aggregate por definición |
| FeatureEnvy en `Notificacion` | aggregate accede a sus propios VOs | El aggregate en ES aplica VOs que él mismo contiene |
| FeatureEnvy en templates/ | InscripcionConfirmadaTemplate, ResultadosPublicadosTemplate | Template accede a campos del DTO del evento — patrón Template Method |
| FeatureEnvy en `TorneoResponse` (api) | DTO de response | DTO que proyecta campos del aggregate — patrón DTO/Response |
| LongMethod en SQLiteEventStore | 5 métodos SQL | SQL verboso, pre-existente, aceptado desde SP1 |
| LongMethod en router.py | 19 métodos | Endpoints FastAPI: validación + inyección + handler + respuesta = verboso por diseño |
| FanOut en app.py | 11/7 | Composition root importa todos los BCs — esperado y correcto |
| FanOut en routers | 8-11/7 | FastAPI inyecta múltiples dependencias en cada router |

Estos 100+ warnings (~55%) son ruido estructural conocido desde SP2. No generan candidatos a SP-ADJ.

---

### Patrón B — Señales reales (merecen análisis posterior)

#### B-1. LCOM en `Torneo` — tendencia degradante

| SP | LCOM Torneo | Observación |
|----|:-----------:|-------------|
| SP3 cierre | 3/1 | Primer aviso |
| SP4 cierre | **6/1** | Dobló — señal de crecimiento desordenado |

`Torneo` acumula métodos para disciplinas, jueces, sede y ciclo de vida del torneo.
Con LCOM=6, los grupos de métodos que comparten estado interno se están separando.
**Si supera 8 en BL-005 → evaluar separar responsabilidades del aggregate.**

#### B-2. LCOM en entidades/VOs extraídos en SP-ADJ-03

| Clase | LCOM | Tipo | Observación |
|-------|:----:|------|-------------|
| `GrillaDeSalida` | 3/1 | Entidad | Extraída en SP-ADJ-03, ya tiene cohesión baja. Sus 3 métodos largos (24/20, 24/20, 38/20) sugieren que agrupa lógica heterogénea |
| `TarjetaAsignacion` | 2/1 | Value Object | Extraído en SP-ADJ-03. LCOM=2 desde el inicio — posible extracción incompleta |

Candidatos a revisión en paso `02-analisis-aggregates`.

#### B-3. LongMethod en `Performance` — persistencia del método más largo

`Performance` tiene 8 LongMethod, el peor siendo **65/20**. Es el método más largo del
codebase en este SP. Los `_apply_*` en ES son verbosos por diseño, pero 65 líneas sugiere
que hay un método que hace más de una cosa. Candidato a identificación en paso 02.

#### B-4. `_p08_finalizacion.py` — crecimiento continuo

| SP | LongMethod | Observación |
|----|:----------:|-------------|
| SP3 cierre | 53/20 | Candidato anotado |
| SP4 cierre | **62/20** | Creció +9 líneas — la política P-08 acumula lógica con cada INC |

Si sigue creciendo en SP5 → extraer responsabilidades de P-08 (ranking, hash, notificación).

#### B-5. DataClumps en `performance_events.py`

3 factories de eventos reciben siempre los mismos 4 parámetros:
`(performance_id, participante_id, disciplina, competencia_id)`.
Candidato a VO `PerformanceContext` que agrupe el contexto de creación.
**Señal real de moderada prioridad** — no bloquea pero es complejidad accidental.

#### B-6. `ExportarResultadosHandler` + `exportar_resultados.py` — nuevo con alta complejidad

El handler de exportación nuevo (INC-4.6) ya acumula:
- FanOut 11/7 en `exportar_resultados.py`
- DataClumps 2/2
- 4 LongMethod (35/20, 31/20, 38/20, 24/20)
- LongParameterList 6/5

Para ser una US reciente, tiene densidad de warnings alta. Candidato a revisión en paso 02.

#### B-7. `AndarivelesActivosAdapter` LongMethod 52/20

Pre-existente desde SP2, candidato anotado en SP3 y no atacado. Ahora sigue igual.
Si no se ataca en SP-ADJ-06, documentar explícitamente por qué se acepta.

---

## Nuevos en SP4 — señal de calidad del código agregado

| Clase nueva | Warnings | Clasificación |
|-------------|:--------:|--------------|
| `Notificacion` aggregate | 4 (3 LongMethod + 1 FeatureEnvy) | LongMethod: `_apply` methods verbosos (ES normal); FeatureEnvy: falso positivo |
| `SQLiteNotificacionEventStore` | 2 (LongMethod + FeatureEnvy) | Ambos falsos positivos — mismo patrón que SQLiteEventStore |
| `SolicitarEnvioHandler` | 1 (FeatureEnvy) | Falso positivo CQRS |
| `PoliticaP10Handler` | 2 (FeatureEnvy + LongMethod 22/20) | FeatureEnvy: falso positivo; LongMethod: método `handle` orquesta 3 pasos — aceptable |
| `PoliticaP11Handler` | 2 (LCOM 2/1 + LongMethod 26/20) | LCOM: política con dos responsabilidades (solicitar + enviar) — candidato a revisión |
| `ResendEmailAdapter` | 1 (LongMethod 36/20) | `enviar()` más `_post()` con manejo httpx — verboso pero cohesivo |
| `LoggingEmailAdapter` | 2 (FeatureEnvy + LongMethod 26/20) | FeatureEnvy: falso positivo; LongMethod: aceptable |
| `ObtenerAuditLogHandler` | 2 (FeatureEnvy + LongMethod 24/20) | Ambos aceptables — query handler con carga y proyección |
| `ExportarResultadosHandler` | múltiples | **Ver B-6** — señal real |
| templates (InscripcionConfirmada, ResultadosPublicados) | 3 | FeatureEnvy: falso positivo; LongMethod: template con HTML — aceptable |

---

## Comparación histórica de warnings

| Baseline | CRITICAL | WARNING | Código nuevo en el SP |
|----------|:--------:|:-------:|----------------------|
| BL-001 (SP1) | 0 | ~40 | BC Competencia (Performance) |
| BL-002 (SP2) | 0 | 78→0 post-ADJ | BC Competencia (Competencia) + Resultados |
| BL-003 (SP3) | 0 | 111 | Torneo + Registro + Identidad + extensiones |
| **BL-004 (SP4)** | **0** | **196** | Notificaciones + frontend (no analizado por DR) + INC-4.1/4.6 |

El incremento SP3→SP4 (+85) es el mayor entre SPs. Atribuible principalmente a:
1. BC Notificaciones completo (~25 warnings en clases nuevas)
2. Endpoints nuevos en api/ (~12 warnings LongMethod)
3. Handlers nuevos de exportación y audit (~10 warnings)
4. DataClumps acumulados en `performance_events.py`

---

## Candidatos preliminares a SP-ADJ-06

| ID | Clase | Issue | Severidad |
|----|-------|-------|-----------|
| DR-01 | `Torneo` aggregate | LCOM=6 — crecimiento de cohesión preocupante | Alta (monitorear) |
| DR-02 | `Performance` | LongMethod 65/20 — identificar cuál método y si tiene complejidad accidental | Media |
| DR-03 | `_p08_finalizacion.py` | LongMethod 62/20 — creció SP3→SP4, tendencia continua | Media |
| DR-04 | `performance_events.py` | DataClumps ×3 — VO `PerformanceContext` candidato | Media |
| DR-05 | `ExportarResultadosHandler` | FanOut + DataClumps + 4 LongMethod — alta densidad para código nuevo | Media |
| DR-06 | `GrillaDeSalida` | LCOM=3/1 + 3 LongMethod — entidad con cohesión baja desde su creación | Baja |
| DR-07 | `AndarivelesActivosAdapter` | LongMethod 52/20 — pre-existente sin atacar, 3er SP consecutivo | Baja |

---

## Pendiente de investigación (próximos pasos)

- [ ] **02-analisis-aggregates**: abrir `Performance` (LongMethod 65/20) y `GrillaDeSalida` (LCOM=3); verificar `Torneo` con LCOM=6
- [ ] **02-analisis-aggregates**: abrir `ExportarResultadosHandler` — ¿tiene complejidad accidental?
- [ ] **04-revision-solid**: revisar `PoliticaP11Handler` (LCOM=2) — ¿sus dos responsabilidades son separables?

*Creado: 2026-04-16 — Revisión pre-BL-004*
