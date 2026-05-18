# Tamaño Funcional — Proxies FPA por BC

> Fuente: `docs/traceability/matrix.md` · `tests/features/` · `src/*/api/router.py` · `docs/metricas/productividad/velocidad-sp.md`  
> Método: proxies de tamaño funcional (no FPA formal COSMIC/IFPUG) — US-IEDD, BDD scenarios, REST endpoints  
> Fecha de extracción: 2026-05-18  
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

| Categoría | Cantidad | % del total |
|-----------|:--------:|:-----------:|
| US funcionales | **77** | 63% |
| US de ajuste (ADJ) | **46** | 37% |
| **Total US** | **123** | 100% |
| Duración | 63 días | 1.22 US func./día |

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

| Elemento | Cantidad |
|----------|:--------:|
| Feature files | **125** |
| Scenarios (Scenario + Scenario Outline) | **636** |
| Scenarios por feature file (promedio) | **5.1** |

### 2.2 Scenarios por BC

| BC | Tipo | Feature files | Scenarios | % del total | Scenarios/feature |
|----|------|:-------------:|:---------:|:-----------:|:-----------------:|
| torneo | CRUD | 61 | **310** | 48.7% | 5.1 |
| competencia | ES (Core) | 56 | **263** | 41.4% | 4.7 |
| registro | CRUD | 23 | **125** | 19.7% | 5.4 |
| resultados | CRUD | 22 | **107** | 16.8% | 4.9 |
| identidad | CRUD | 6 | **36** | 5.7% | 6.0 |
| notificaciones | ES | 4 | **19** | 3.0% | 4.8 |

> Los feature files son compartidos — un mismo archivo puede ser contabilizado en múltiples BCs (ej. `US-2.4.2-calcular-ranking.feature` aparece en competencia, torneo y resultados). El total por BC suma más que 636 por este solapamiento.

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

### 3.1 Totales por BC y método HTTP

| BC | Tipo | GET | POST | PUT | PATCH | DELETE | **Total** |
|----|------|:---:|:----:|:---:|:-----:|:------:|:---------:|
| competencia | ES | 10 | 13 | 1 | 0 | 0 | **24** |
| registro | CRUD | 9 | 6 | 1 | 3 | 1 | **20** |
| torneo | CRUD | 4 | 1 | 10 | 0 | 0 | **15** |
| identidad | CRUD | 1 | 5 | 0 | 0 | 0 | **6** |
| resultados | CRUD | 3 | 0 | 0 | 0 | 0 | **3** |
| notificaciones | ES | — | — | — | — | — | **0** ¹ |
| **Total** | | **27** | **25** | **12** | **3** | **1** | **68** |

¹ Notificaciones no expone API REST — es un BC completamente interno, orientado a eventos (política P-10/P-11). Su superficie funcional se mide exclusivamente por sus policies y event handlers, no por endpoints.

### 3.2 Distribución por método

| Método | Cantidad | % | Interpretación |
|--------|:--------:|:-:|----------------|
| GET | 27 | 40% | Consultas — read models, rankings, grillas |
| POST | 25 | 37% | Comandos — crear torneo, registrar AP, emitir tarjeta |
| PUT | 12 | 18% | Actualizaciones — estados de torneo, edición completa |
| PATCH | 3 | 4% | Actualizaciones parciales — perfil, documentos adjuntos |
| DELETE | 1 | 1% | Cancelación de inscripción |

**El sistema es mayoritariamente orientado a comandos y consultas** (POST + GET = 77%), coherente con la arquitectura CQRS/ES en el BC Core (Competencia tiene 13 POST — uno por cada comando del aggregate).

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

| Proxy | Valor total | BC dominante | Hallazgo principal |
|-------|:-----------:|:------------:|-------------------|
| US funcionales | **77** | competencia (~29%) | 1.22 US func./día — ritmo estable en SP3–SP5 |
| BDD Scenarios | **636** | torneo (49%) | 5.1 scenarios/feature — cobertura granular |
| REST Endpoints | **68** | competencia (35%) | GET+POST = 77% — sistema CQRS/orientado a comandos |
| Scenarios/Endpoint | — | resultados (35.7) | Complejidad en dominio, no en superficie API |

**El tamaño funcional no se distribuye uniformemente por paradigma:**
- ES (competencia + notificaciones) contribuye ~35% de las US funcionales pero el 100% del event store y las políticas
- CRUD (torneo + registro + resultados + identidad) concentra el mayor número de scenarios BDD porque los flujos CRUD tienen más paths alternativos visibles (validaciones, estados, permisos por rol)
- La baja superficie API de resultados (3 endpoints) y notificaciones (0 endpoints) contrasta con su alta complejidad interna — evidencia de que el proxy "endpoints" subestima el tamaño funcional de los BCs con lógica de dominio rica

---

*Extraído: 2026-05-18 — rama doc/metricas — PLAN-METRICAS.md §C.0 (Prioridad 10) completada*
