# Function Point Analysis (IFPUG) — Conteo manual por BC

> Fuente: `src/*/api/router.py` · `src/*/domain/aggregates/` · `src/*/domain/ports/`
> Método: conteo manual IFPUG (ILF/EIF, EI/EO/EQ, DET/RET/FTR) — no certificado CFPS, pero aplica
> las tablas de complejidad estándar al pie de la letra. UFP (Unadjusted Function Points), sin VAF.
> Fecha de extracción: 2026-08-20 · HEAD `main` post SP-ADJ-13, tag `v1.0.5`
> Referencia: `tamano-funcional.md` (proxies previos) · `BENCHMARK-INDUSTRIA.md §5.1` (comparación de productividad)

---

## 1. Por qué IFPUG FPA (y no solo proxies)

`tamano-funcional.md` mide tamaño con proxies derivables automáticamente (US-IEDD, BDD scenarios,
endpoints REST) — útiles para tendencias internas, pero no comparables contra benchmarks de
industria porque no son una unidad estandarizada. IFPUG FPA sí lo es (ISO/IEC 20926) y es la
unidad que usan ISBSG y Capers Jones para publicar productividad (`BENCHMARK-INDUSTRIA.md §5.1`).

Este documento cuenta manualmente ILF/EIF (funciones de datos) y EI/EO/EQ (funciones
transaccionales) para cada uno de los 6 BCs, siguiendo las tablas de complejidad estándar IFPUG
(DET × RET para datos, DET × FTR para transacciones), sin aplicar VAF (Value Adjustment Factor) —
la práctica ISBSG moderna compara UFP sin ajustar.

**Advertencia de rigor:** este es un conteo manual (asistido por 6 agentes LLM en paralelo, uno
por BC, con la misma metodología pero juicio independiente en casos ambiguos), no un conteo
certificado IFPUG (CFPS). Se documentan las decisiones de clasificación no triviales en cada
sección para que sean auditables.

---

## 2. Conteo por BC

### 2.1 registro (CRUD)

| Función | Tipo | DET | RET | Complejidad | FP |
|---|---|:--:|:--:|:--:|:--:|
| Atleta | ILF | 10 | 1 | Baja | 7 |
| Inscripcion | ILF | 10 | 2 | Baja | 7 |
| Juez | ILF | 4 | 1 | Baja | 7 |
| Organizador | ILF | 3 | 1 | Baja | 7 |
| Torneo (EIF vía `TorneoConsultaPort`) | EIF | 4 | 1 | Baja | 5 |

12 EI (Baja) = 48 FP · 3 EO (2 Media + 1 Baja) = 14 FP · 8 EQ (Baja) = 24 FP — 23 transacciones,
coincide exacto con los 23 endpoints de `tamano-funcional.md §3.1`.

**Datos: 33 FP · Transaccional: 86 FP · UFP: 119**

### 2.2 competencia (ES, Core)

| Función | Tipo | DET | RET | Complejidad | FP |
|---|---|:--:|:--:|:--:|:--:|
| Competencia (aggregate ES) | ILF | 13 | 2 (raíz + grilla) | Baja | 7 |
| Performance (aggregate ES) | ILF | 18 | 2 (raíz + penalizaciones) | Baja | 7 |
| Atleta (nombre, EIF vía `atleta_nombre_port`) | EIF | 3 | 1 | Baja | 5 |
| Inscripción con AP (EIF vía `InscripcionRepositoryPort`) | EIF | 3 | 1 | Baja | 5 |

14 EI = 45 FP · 6 EO (incl. `GET /grilla` única transacción Alta del proyecto, 7 FP) = 30 FP ·
4 EQ = 12 FP — 24 transacciones = 24 endpoints reales.

**Datos: 24 FP · Transaccional: 87 FP · UFP: 111**

### 2.3 torneo (CRUD)

| Función | Tipo | DET | RET | Complejidad | FP |
|---|---|:--:|:--:|:--:|:--:|
| Torneo (aggregate) | ILF | 15 (13 + subgrupo disciplinas) | 2 | Baja | 7 |

Sin EIF — `torneo` no consulta otros BCs. 11 EI = 33 FP · 4 EQ = 12 FP · 0 EO — 15 transacciones =
15 endpoints reales. Todas las transiciones de estado son mutaciones simples de un único ILF.

**Datos: 7 FP · Transaccional: 45 FP · UFP: 52**

### 2.4 resultados (CRUD, solo lectura)

| Función | Tipo | DET | RET | Complejidad | FP |
|---|---|:--:|:--:|:--:|:--:|
| RankingCompetencia | ILF | 12 | 2 | Baja | 7 |
| RankingOverall | ILF | 8 | 2 | Baja | 7 |
| ResultadoFinal (EIF, Competencia) | EIF | 5 | 1 | Baja | 5 |
| Categoría de atleta (EIF, Registro) | EIF | 2 | 1 | Baja | 5 |
| Info de atleta para export (EIF, Registro) | EIF | 4 | 1 | Baja | 5 |

0 EI · 2 EO (`/ranking` Media 5FP, `/export` Alta 7FP) = 12 FP · 1 EQ (`/overall`) = 3 FP —
3 transacciones = 3 endpoints reales (todos GET, confirmado).

**Datos: 29 FP · Transaccional: 15 FP · UFP: 44**

### 2.5 identidad (CRUD, autenticación)

| Función | Tipo | DET | RET | Complejidad | FP |
|---|---|:--:|:--:|:--:|:--:|
| Usuario | ILF | 7 | 2 (raíz + roles) | Baja | 7 |

**Sin EIF** — `perfil_registro_port` se descartó explícitamente: es una *escritura saliente* hacia
Registro (Identidad empuja el perfil), no una lectura de un ILF externo; IFPUG exige que un EIF
sea referenciado (leído), no solo invocado. `password_hashing_port`/`token_service_port` son
infraestructura técnica, no datos de negocio.

7 EI = 21 FP · 0 EO · 2 EQ = 6 FP — 9 transacciones = 9 endpoints reales (2 GET, 6 POST, 1 DELETE).

**Datos: 7 FP · Transaccional: 27 FP · UFP: 34**

### 2.6 notificaciones (ES, sin API REST)

| Función | Tipo | DET | RET | Complejidad | FP |
|---|---|:--:|:--:|:--:|:--:|
| Notificacion | ILF | 11 | 1 | Baja | 7 |

**Nota metodológica:** este BC no expone endpoints HTTP — es reactivo a eventos de otros BCs vía
políticas P-10/P-11. La frontera funcional IFPUG se tomó en los **comandos de aplicación**
(`SolicitarEnvioCommand`, `EnviarNotificacionCommand`), no en un endpoint, porque son los procesos
elementales que cruzan el boundary del BC.

2 EI (Baja) = 6 FP · 0 EO · 0 EQ.

**Datos: 7 FP · Transaccional: 6 FP · UFP: 13**

---

## 3. Consolidado

| BC | Tipo | ILF | EIF | EI | EO | EQ | Datos FP | Transac. FP | **UFP** |
|---|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| registro | CRUD | 4 | 1 | 12 | 3 | 8 | 33 | 86 | **119** |
| competencia | ES (Core) | 2 | 2 | 14 | 6 | 4 | 24 | 87 | **111** |
| torneo | CRUD | 1 | 0 | 11 | 0 | 4 | 7 | 45 | **52** |
| resultados | CRUD | 2 | 3 | 0 | 2 | 1 | 29 | 15 | **44** |
| identidad | CRUD | 1 | 0 | 7 | 0 | 2 | 7 | 27 | **34** |
| notificaciones | ES | 1 | 0 | 2 | 0 | 0 | 7 | 6 | **13** |
| **Total (por-BC, con EIF)** | | **11** | **6** | **46** | **11** | **19** | **107** | **266** | **373** |

**Chequeo de consistencia:** 74 de las 76 transacciones contadas corresponden 1:1 a los 74
endpoints REST reales del proyecto (`tamano-funcional.md §3.1`); las 2 restantes son los comandos
internos de `notificaciones` (sin endpoint, justificado en §2.6).

### 3.1 Total deduplicado (vista de sistema único)

El total de 373 FP cuenta cada BC como si fuera una aplicación independiente — el mismo dato
aparece como ILF en el BC que lo mantiene y como EIF en cada BC que lo consulta (ej. `Atleta` es
ILF en `registro` y EIF en `competencia`/`resultados`). Es una práctica válida en IFPUG cuando se
mide cada BC como límite de aplicación (común en arquitecturas de microservicios/BCs), pero **no
es el tamaño funcional del sistema completo visto como una sola aplicación**.

Para esa vista, se eliminan los 6 EIF (43 FP) porque a nivel de sistema son datos internos, no
interfaces externas — el FTR de cada transacción no cambia (sigue tocando la misma cantidad de
archivos lógicos), solo cambia su clasificación de EIF a ILF, así que la FP transaccional (266)
no varía.

| Componente | FP (vista sistema único) |
|---|:--:|
| Datos (solo ILF, 11 agregados) | 77 |
| Transaccional (sin cambio) | 266 |
| **UFP total del sistema** | **343** |

---

## 4. Hallazgos y salvedades

1. **Competencia concentra la única transacción de complejidad Alta** (`GET /{id}/grilla`, 7 FP) —
   consistente con ser el BC Core, y con los hallazgos previos de SLOC/CC/Halstead que ya
   señalaban a `competencia` como el BC de mayor complejidad interna.
2. **Asimetría identidad↔registro:** `identidad` no cuenta `perfil_registro_port` como EIF porque
   es escritura saliente, no lectura — decisión correcta bajo IFPUG estricto, pero rompe la
   simetría si se quisiera usar FP como proxy de "acoplamiento total" entre BCs.
3. **notificaciones es la única excepción real de método** (transacciones derivadas de comandos
   internos, no de endpoints) — necesario porque el BC no expone API REST por diseño (P-10/P-11).
4. **373 FP (por-BC) vs. 343 FP (sistema deduplicado)** — usar el primero para comparar BCs entre
   sí; usar el segundo para comparar el proyecto completo contra un benchmark de industria que
   mide "una aplicación" (ver `BENCHMARK-INDUSTRIA.md §5.1.D`).

---

## 5. Comparación contra ISBSG — ver `BENCHMARK-INDUSTRIA.md §5.1.D`

El intento de convertir este conteo a FP/persona-mes y compararlo contra ISBSG se documenta en
`BENCHMARK-INDUSTRIA.md §5.1.D`, junto con el motivo por el que **tampoco se recomienda citarlo**
— no por el conteo de FP en sí (que es sustancialmente más riguroso que el backfiring SLOC→FP de
§5.1.B), sino porque el denominador de esfuerzo del proyecto (persona-meses derivados de días
calendario) no es comparable con el PDR de ISBSG (horas de esfuerzo efectivamente registradas por
fase). Ver esa sección para el detalle.

---

*Extraído: 2026-08-20 — conteo manual IFPUG asistido por 6 agentes en paralelo, un BC cada uno,
misma metodología (tablas de complejidad estándar DET×RET / DET×FTR, sin VAF).*
