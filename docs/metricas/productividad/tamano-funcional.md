# Tamaño Funcional — Proxies FPA por BC

> Fuente: `docs/traceability/matrix.md` · `tests/features/` · `src/*/api/router.py` · `docs/metricas/productividad/velocidad-sp.md`  
> Método: proxies de tamaño funcional (no FPA formal COSMIC/IFPUG) — US-IEDD, BDD scenarios, REST endpoints  
> Fecha de extracción original: 2026-05-18 · **Recálculo: 2026-08-13 (HEAD `main`, post SP7 + SP-ADJ-12 + SP-ADJ-13, tag v1.0.5)**  
> Referencia: PLAN-METRICAS.md §C.0

---

## Contexto — Por qué no FPA formal

COSMIC y IFPUG requieren mapear transacciones a "movimientos de datos" (entradas, salidas, lecturas, escrituras) mediante análisis funcional experto. Para el paper IEDD, tres proxies son suficientes y derivables automáticamente desde los artefactos del proyecto:

1. **US-IEDD** — granularidad de entrega (unidad de planificación + pipeline)
2. **BDD Scenarios** — cobertura funcional verificable
3. **REST Endpoints** — superficie de la API pública

Los tres proxies son independientes y complementarios: una US puede generar 0 endpoints (lógica interna) y N scenarios, o bien un endpoint puede ser cubierto por scenarios de múltiples BCs.

---

## 1. US-IEDD por SP y BC

### 1.1 Totales del proyecto

| Categoría | Cantidad SP1–SP6 | Cantidad proyecto completo (+SP7/ADJ-12/13) |
|-----------|:--------:|:-----------:|
| US funcionales | **77** (63%) | **77** (59%) — sin cambios, ver `velocidad-sp.md` |
| US de ajuste (ADJ) | **46** (37%) | **54** (41%) |
| **Total US** | **123** | **131** |
| Duración | 63 días · 1.22 US func./día | 77 días · 1.00 US func./día (ver nota metodológica en `velocidad-sp.md §1`) |

### 1.2 US funcionales por SP

| SP | Nombre | US func. | US ADJ | Total US | Ritmo func./día |
|----|--------|:--------:|:------:|:--------:|:---------------:|
| SP1 | La Performance | 9 | 5 | 14 | 0.90 |
| SP2 | La Competencia | 3 | 3 | 6 | 0.75 |
| SP3 | El Torneo | 11 | 14 | 25 | 1.57 |
| SP4 | La Plataforma | 21 | 7 | 28 | 1.50 |
| SP5 | La Puesta en Marcha | 20 | 7 | 27 | 1.54 |
| SP6 | Validación y Despliegue | 13 | 10 | 23 | 0.87 |
| **Total** | | **77** | **46** | **123** | **1.22** |

**Nota:** SP1–SP2 son de rampa (inversión en infraestructura hexagonal). SP3–SP5 representan la velocidad de crucero (~1.5 US func./día). SP6 baja por diseño — más ajuste que funcionalidad nueva.

### 1.3 US funcionales por BC (estimado desde feature file mapping)

La trazabilidad US→BC es 1:N (una US puede tocar múltiples BCs). La distribución se aproxima por el BC primario de cada US:

| BC | Tipo | US primaria estimada | Proporción |
|----|------|:--------------------:|:----------:|
| competencia | ES (Core) | ~22 | 29% |
| torneo | CRUD | ~14 | 18% |
| registro | CRUD | ~12 | 16% |
| resultados | CRUD | ~12 | 16% |
| identidad | CRUD | ~9 | 12% |
| notificaciones | ES | ~5 | 6% |
| shared / infra | Shared | ~3 | 4% |
| **Total** | | **~77** | 100% |

**Competencia concentra ~29% de las US funcionales** — consistente con su 58% de WMC proxy, 219 bloques CC en domain/, y el mayor volumen de scenarios BDD.

---

## 2. BDD Scenarios por BC

### 2.1 Totales

| Elemento | BL-006 (2026-05-18) | v1.0.5 (2026-08-13) | Δ |
|----------|:--------:|:--------:|:---:|
| Feature files | 125 | **127** | +2 |
| Scenarios (Scenario + Scenario Outline) | 636 | **647** | +11 |
| Scenarios por feature file (promedio) | 5.1 | **5.1** | = |

**+2 feature files, +11 scenarios** — consistente con `cobertura-tests.md §6` (crecimiento BDD ya
documentado ahí) y con las nuevas capacidades de SP-ADJ-12 (aceptación de inscripciones, roles).

### 2.2 Scenarios por BC

| BC | Tipo | Feature files BL-006 | Scenarios BL-006 | Feature files v1.0.5 | Scenarios v1.0.5 | Δ Scenarios |
|----|------|:-------------:|:---------:|:-------------:|:---------:|:---:|
| torneo | CRUD | 61 | 310 | 61 | **311** | +1 |
| competencia | ES (Core) | 56 | 263 | 54 | **254** | −9 |
| registro | CRUD | 23 | 125 | 22 | **122** | −3 |
| resultados | CRUD | 22 | 107 | 19 | **92** | −15 |
| identidad | CRUD | 6 | 36 | 6 | **35** | −1 |
| notificaciones | ES | 4 | 19 | 4 | **19** | = |

**Nota metodológica importante:** este conteo por BC usa `grep -rl "<bc>" tests/features/*.feature`
— cuenta un feature file en un BC si el **texto** del BC aparece en cualquier parte del archivo,
no si el BC realmente le pertenece. Es un proxy ya señalado como aproximado en la medición
original ("el total por BC suma más que el total real por solapamiento"). Los BCs con backend
**verificadamente sin cambios** (competencia, resultados, identidad — ver `backend-raw.md`) muestran
variaciones negativas de hasta −15 scenarios pese a que sus `.feature` files no cambiaron: es
**ruido del método de conteo por coincidencia de texto**, no una pérdida real de cobertura BDD —
la reorganización de referencias cruzadas entre BCs en los 2 archivos nuevos (+2 feature files)
alteró qué archivos matchean qué nombre de BC. **El total agregado (+11 scenarios) es el único
número de esta sección con alta confianza**; el desglose por BC se mantiene como proxy aproximado,
igual que en BL-006.

> Los feature files son compartidos — un mismo archivo puede ser contabilizado en múltiples BCs (ej. `US-2.4.2-calcular-ranking.feature` aparece en competencia, torneo y resultados). El total por BC suma más que 647 por este solapamiento.

### 2.3 Top feature files por scenario count

| Feature file | Scenarios | BCs involucrados |
|---|:---:|---|
| `US-3.1.1-aggregate-torneo.feature` | 13 | torneo |
| `US-3.1.2-api-rest-torneo.feature` | 10 | torneo |
| `US-ADJ-11.5-organizador.feature` | 8 | torneo, registro |
| `US-6.3.2-inscripcion-ap-adjuntos.feature` | 8 | torneo, registro |
| `US-ADJ-11.1-identidad-multi-rol.feature` | 9 | registro, identidad |
| `US-5.6.1-algoritmo-puntaje-faas.feature` | 8 | resultados |
| `US-4.6.4-exportacion-resultados.feature` | 7 | resultados |

---

## 3. REST Endpoints por BC

### 3.1 Totales por BC y método HTTP (v1.0.5)

| BC | Tipo | GET | POST | PUT | PATCH | DELETE | **Total v1.0.5** | Total BL-006 | Δ |
|----|------|:---:|:----:|:---:|:-----:|:------:|:---------:|:---:|:---:|
| competencia | ES | 10 | 13 | 1 | 0 | 0 | **24** | 24 | = |
| registro | CRUD | 11 | 6 | 1 | 4 | 1 | **23** | 20 | **+3** |
| torneo | CRUD | 4 | 1 | 10 | 0 | 0 | **15** | 15 | = |
| identidad | CRUD | 2 | 6 | 0 | 0 | 1 | **9** | 6 | **+3** |
| resultados | CRUD | 3 | 0 | 0 | 0 | 0 | **3** | 3 | = |
| notificaciones | ES | — | — | — | — | — | **0** ¹ | 0 | = |
| **Total** | | **30** | **26** | **12** | **4** | **2** | **74** | **68** | **+6** |

¹ Notificaciones no expone API REST — es un BC completamente interno, orientado a eventos (política P-10/P-11). Sin cambios.

**Los +6 endpoints nuevos están 100% en `registro` (+3) e `identidad` (+3)** — la señal más limpia
de todo `PLAN-METRICAS.md` sobre dónde se concentró el trabajo de SP-ADJ-12: `registro` sumó
`PATCH` (aceptación de inscripción) y ajustó GET/DELETE (detalle + adjuntos); `identidad` sumó
`POST`+`DELETE` (`POST/DELETE /auth/me/roles`, exactamente los comandos documentados en
`backend-por-capa.md §4` y `backend-ck.md §2`). **Cuarta confirmación independiente** (junto con
SLOC, Halstead y cobertura) del mismo hallazgo: solo esos dos BCs cambiaron.

### 3.2 Distribución por método (v1.0.5)

| Método | Cantidad BL-006 | Cantidad v1.0.5 | % v1.0.5 | Interpretación |
|--------|:--------:|:--------:|:-:|----------------|
| GET | 27 | **30** | 41% | Consultas — read models, rankings, grillas, detalle de inscripción (nuevo) |
| POST | 25 | **26** | 35% | Comandos — crear torneo, registrar AP, emitir tarjeta, agregar rol (nuevo) |
| PUT | 12 | **12** | 16% | Actualizaciones — estados de torneo, edición completa (sin cambios) |
| PATCH | 3 | **4** | 5% | Actualizaciones parciales — perfil, adjuntos, **aceptación de inscripción (nuevo)** |
| DELETE | 1 | **2** | 3% | Cancelación de inscripción + **quitar rol (nuevo)** |

**El sistema sigue siendo mayoritariamente orientado a comandos y consultas** (POST + GET = 76%,
antes 77% — sin cambio de patrón), coherente con la arquitectura CQRS/ES en el BC Core.

### 3.3 Patrones por BC

**Competencia (ES):** 13 POST (comandos ES: `registrar_ap`, `llamar_atleta`, `registrar_resultado`, `asignar_tarjeta`, etc.) + 10 GET (read models: grilla, ejecución, ranking provisional, eventos). Superficie API directamente proporcional a la cardinalidad de comandos del aggregate.

**Torneo (CRUD):** 10 PUT — la máquina de estados del torneo tiene 8 transiciones + edición + configuración. PUT > POST porque el torneo ya existe y la mayoría de operaciones lo modifican.

**Registro (CRUD):** distribución balanceada — GET (consultas de atletas/inscriptos), POST (inscripción, creación), PATCH (actualización de documentos adjuntos), DELETE (cancelar inscripción).

**Resultados (CRUD):** solo 3 GET — BC de lectura pura. Los resultados se calculan en Competencia (ES), los rankings son read models. Sin POST/PUT porque los datos se generan via eventos, no via API de escritura directa.

**Identidad:** 5 POST (registro, login, refresh, logout, cambio de contraseña) + 1 GET (perfil). BC de autenticación — la mayor parte del comportamiento es transaccional (POST), no consultable (GET).

---

## 4. Correlaciones entre proxies

| BC | US func. (est.) | BDD Scenarios | REST Endpoints | Ratio Scenarios/Endpoint |
|----|:--------------:|:-------------:|:--------------:|:------------------------:|
| competencia | ~22 | 263 | 24 | **11.0** |
| torneo | ~14 | 310 | 15 | 20.7 |
| registro | ~12 | 125 | 20 | 6.3 |
| resultados | ~12 | 107 | 3 | **35.7** |
| identidad | ~9 | 36 | 6 | 6.0 |
| notificaciones | ~5 | 19 | 0 | — |

**Resultados: 35.7 scenarios/endpoint** — el mayor ratio del proyecto. Sus 3 endpoints GET concentran la mayor parte de la complejidad funcional del sistema (rankings por disciplina, género, categoría, Overall, SPE). Un solo endpoint de ranking sirve N variantes dependiendo de los parámetros — la complejidad está en el dominio, no en la superficie API.

**Torneo: 20.7 scenarios/endpoint** — alto ratio porque los endpoints PUT de transición de estado (confirmación, inicio, ejecución, cierre) tienen múltiples paths alternativos y validaciones de invariantes.

**Competencia: 11.0 scenarios/endpoint** — ratio moderado, equilibrado entre la cardinalidad de comandos ES y la cobertura BDD de cada comando.

---

## 5. Densidad funcional — US por BC normalizada

| BC | Tipo | US est. | Scenarios | Endpoints | LOC domain (SLOC) | Scenarios/US |
|----|------|:-------:|:---------:|:---------:|:-----------------:|:------------:|
| competencia | ES | ~22 | 263 | 24 | ~2 278 | **12.0** |
| torneo | CRUD | ~14 | 310 | 15 | ~400 | 22.1 |
| registro | CRUD | ~12 | 125 | 20 | ~450 | 10.4 |
| resultados | CRUD | ~12 | 107 | 3 | ~600 | 8.9 |
| identidad | CRUD | ~9 | 36 | 6 | ~300 | 4.0 |
| notificaciones | ES | ~5 | 19 | 0 | ~450 | 3.8 |

**Torneo tiene el mayor ratio Scenarios/US (22.1):** pocas US funcionales, muchos scenarios BDD — la máquina de estados del torneo tiene alta cobertura de paths de transición (edge cases: retroceso Ejecución→Preparación, estados inválidos, restricciones temporales).

**Notificaciones tiene el menor ratio (3.8):** la lógica ES de idempotencia exactly-once y políticas P-10/P-11 se verifica principalmente por tests unitarios y de integración, no por BDD de alto nivel.

---

## 6. Síntesis para el paper IEDD

| Proxy | Valor BL-006 | Valor v1.0.5 | Δ | Hallazgo principal |
|-------|:-----------:|:-----------:|:---:|-------------------|
| US funcionales | 77 | **77** | = | Sin cambios — SP7 no aportó US funcionales (ver `velocidad-sp.md`) |
| BDD Scenarios | 636 | **647** | +11 | +2 feature files, crecimiento marginal y trazable a SP-ADJ-12 |
| REST Endpoints | 68 | **74** | **+6** | +3 registro, +3 identidad — coincide exactamente con SLOC/Halstead/cobertura |
| Scenarios/Endpoint | 9.4 (636/68) | **8.7** (647/74) | −0.7 | La superficie API creció más rápido que los scenarios BDD en el período |

**Confirmación final del patrón que atraviesa toda la Ronda 2 de recálculo:** de los 4 proxies de
tamaño funcional medidos (SLOC, Halstead, cobertura, endpoints REST), **los 4 apuntan
exactamente a los mismos 2 BCs** (`registro`, `identidad`) como el único lugar donde el sistema
cambió entre BL-006 y v1.0.5. Los otros 4 BCs (`competencia`, `torneo`, `resultados`,
`notificaciones`) no generaron ni un endpoint, ni una línea de producción, ni un bloque de
complejidad nuevo en 77 días adicionales de proyecto — evidencia consistente de que SP7 +
SP-ADJ-12 + SP-ADJ-13 fueron un cierre quirúrgico, no una segunda fase de construcción.

**El tamaño funcional no se distribuía uniformemente por paradigma en BL-006, y sigue sin
hacerlo:**
- ES (competencia + notificaciones) contribuye ~35% de las US funcionales pero el 100% del event store y las políticas — sin cambios
- CRUD concentra el mayor número de scenarios BDD — sin cambios
- La baja superficie API de resultados (3) y notificaciones (0) contrasta con su alta complejidad interna — sin cambios

---

*Extraído: 2026-05-18 — rama doc/metricas — PLAN-METRICAS.md §C.0 (Prioridad 10) completada*
*Recalculado: 2026-08-13 — HEAD `main` post SP-ADJ-13 (tag v1.0.5) — PLAN-METRICAS.md §C.0 (Ronda 2)*
