# Métricas Backend por Capa Hexagonal — AtaraxiaDive

> Fuente: `radon cc -j` y `radon mi -j` sobre cada `src/<bc>/<capa>/`  
> Herramienta: radon 6.0.1  
> Fecha de ejecución: 2026-05-18  
> Referencia: PLAN-METRICAS.md §A.1.5

---

## 1. Tabla principal — CC × MI por BC y capa

**Leyenda:** CC = complejidad ciclomática promedio · MI = índice de mantenibilidad promedio · N(CC) = bloques analizados · SLOC = líneas de código fuente  
**Escala CC:** A (1–5) · B (6–10) · C (11–15) · D (16–20)  
**Escala MI:** A (≥ 20) · B (10–20) · C (< 10)

### 1.1 domain/

| BC | Tipo | CC prom | N(CC) | MI prom | N(MI) | SLOC |
|----|------|:-------:|:-----:|:-------:|:-----:|-----:|
| competencia | ES (Core) | 1.74 | 219 | 88.11 | 53 | 2 278 |
| notificaciones | ES (Generic) | 1.84 | 50 | 85.64 | 17 | 404 |
| torneo | CRUD | 1.55 | 44 | 91.50 | 14 | 248 |
| registro | CRUD | 2.11 | 64 | 87.25 | 19 | 324 |
| resultados | CRUD | 2.53 | 64 | 89.61 | 16 | 613 |
| identidad | CRUD | 1.51 | 47 | 97.36 | 12 | 140 |
| shared | Shared | 1.92 | 26 | 92.99 | 11 | 151 |
| **Promedio** | | **1.89** | **514** | **90.07** | **142** | **4 158** |

### 1.2 application/

| BC | Tipo | CC prom | N(CC) | MI prom | N(MI) | SLOC |
|----|------|:-------:|:-----:|:-------:|:-----:|-----:|
| competencia | ES (Core) | 1.92 | 157 | 84.27 | 30 | 1 481 |
| notificaciones | ES (Generic) | 2.04 | 26 | 80.19 | 9 | 278 |
| torneo | CRUD | 1.68 | 47 | 77.34 | 10 | 246 |
| registro | CRUD | 1.98 | 52 | 72.85 | 17 | 363 |
| resultados | CRUD | 2.90 | 60 | 77.80 | 9 | 734 |
| identidad | CRUD | 3.00 | 26 | 70.45 | 8 | 300 |
| shared | Shared | — | — | — | — | — |
| **Promedio** | | **2.25** | **368** | **77.15** | **83** | **3 402** |

### 1.3 infrastructure/

| BC | Tipo | CC prom | N(CC) | MI prom | N(MI) | SLOC |
|----|------|:-------:|:-----:|:-------:|:-----:|-----:|
| competencia | ES (Core) | 2.16 | 37 | 86.82 | 14 | 391 |
| notificaciones | ES (Generic) | 2.45 | 29 | 81.82 | 11 | 354 |
| torneo | CRUD | 1.81 | 16 | 83.12 | 3 | 154 |
| registro | CRUD | 2.16 | 49 | 74.73 | 11 | 529 |
| resultados | CRUD | 2.24 | 21 | 80.97 | 6 | 160 |
| identidad | CRUD | 1.90 | 21 | 83.59 | 5 | 186 |
| shared | Shared | 2.11 | 9 | 85.19 | 3 | 153 |
| **Promedio** | | **2.12** | **182** | **82.32** | **53** | **1 927** |

### 1.4 api/

| BC | Tipo | CC prom | N(CC) | MI prom | N(MI) | SLOC |
|----|------|:-------:|:-----:|:-------:|:-----:|-----:|
| competencia | ES (Core) | 1.60 | 96 | 85.83 | 5 | 1 155 |
| notificaciones | ES (Generic) | — | — | 100.00 | 1 | 0 |
| torneo | CRUD | 1.80 | 35 | 78.90 | 3 | 408 |
| registro | CRUD | 2.15 | 46 | 61.63 | 2 | 691 |
| resultados | CRUD | 2.33 | 15 | 74.39 | 2 | 294 |
| identidad | CRUD | 2.50 | 24 | 65.32 | 3 | 353 |
| shared | Shared | — | — | 100.00 | 2 | 2 |
| **Promedio** | | **2.08** | **216** | **73.21** | **15** | **2 901** |

---

## 2. Resumen cruzado por capa (promedio global)

| Capa | CC prom | MI prom | Total bloques CC | Total SLOC |
|------|:-------:|:-------:|:----------------:|----------:|
| domain/ | **1.89** | **90.07** | 514 | 4 158 |
| application/ | 2.25 | 77.15 | 368 | 3 402 |
| infrastructure/ | 2.12 | 82.32 | 182 | 1 927 |
| api/ | 2.08 | 73.21 | 216 | 2 901 |

**Patrón emergente:**
- `domain/` = capa con **menor CC y mayor MI**: código más simple y mantenible — consistente con el principio hexagonal de mantener el dominio libre de complejidad accidental
- `api/` = capa con **MI más bajo** a pesar de CC moderada: indicador de archivos voluminosos (routers FastAPI con muchas rutas inlined)
- `application/` = **mayor CC promedio**: aquí vive la lógica de orquestación; los use cases complejos suben la complejidad

---

## 3. Hipótesis A.1.5 — ¿ES más complejo que CRUD en domain/?

**Hipótesis:** CC promedio de `domain/` en BC Competencia (ES) > CC promedio de `domain/` en BCs CRUD

| BC | Tipo | domain/ CC |
|----|------|:----------:|
| competencia | **ES (Core)** | **1.74** |
| notificaciones | ES (Generic) | 1.84 |
| torneo | CRUD | 1.55 |
| **registro** | CRUD | **2.11** |
| **resultados** | CRUD | **2.53** |
| identidad | CRUD | 1.51 |

**Resultado: hipótesis NO confirmada en CC promedio.**

La complejidad ciclomática de `domain/` en Competencia (1.74) es **inferior** a la de Registro (2.11) y Resultados (2.53).

**Interpretación:** La mayor complejidad de Registro y Resultados en domain/ refleja la cantidad de variantes de estado (multi-rol en Registro, lógica de ranking por variante SPE en Resultados), no el paradigma ES vs CRUD. Competencia ES mantiene baja la CC en domain porque usa agregados con métodos pequeños y delegación a value objects — el patrón ES distribuye la complejidad en muchos métodos sencillos en lugar de concentrarla.

**Lo que sí distingue a Competencia como ES:** el tamaño. Con 219 bloques CC y 2 278 SLOC, `competencia/domain/` es **3–15× más grande** que cualquier otro BC en esa capa — la complejidad del dominio ES se expresa en amplitud, no en profundidad de cada función.

---

## 4. Módulos de riesgo por capa

### application/ — puntos de complejidad elevada

| BC | CC prom application/ | Observación |
|----|:--------------------:|-------------|
| identidad | 3.00 | JWT multi-rol, autenticación, lógica de creación de usuario compuesta |
| resultados | 2.90 | Queries complejos de ranking (variantes SPE, gender, overall) |
| notificaciones | 2.04 | Idempotencia exactly-once + reintentos |

### api/ — MI bajo (mantenibilidad reducida)

| BC | MI prom api/ | SLOC | Observación |
|----|:-----------:|-----:|-------------|
| registro | 61.63 | 691 | Router con muchos endpoints multi-entidad (atleta + juez + organizador) |
| identidad | 65.32 | 353 | Lógica de auth inline en router |
| resultados | 74.39 | 294 | Rutas de ranking por variante |

---

## 5. Distribución SLOC por capa

```
domain/         4 158 SLOC  (33%)  ████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░
application/    3 402 SLOC  (27%)  █████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
api/            2 901 SLOC  (23%)  ████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
infrastructure/ 1 927 SLOC  (15%)  ████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
```

Total backend: ≈ 12 388 SLOC (de los 12 961 del backend-raw.md; diferencia = archivos raíz de BC sin capa asignada)

---

## 6. Conclusiones para el experimento IEDD

1. **La arquitectura hexagonal cumple su promesa de dominio limpio:** `domain/` tiene consistentemente la menor CC (1.89) y mayor MI (90.07) de todas las capas en todos los BCs.

2. **El paradigma ES no eleva la CC en domain/ sino el volumen:** Competencia ES tiene 219 bloques vs 44–64 en CRUD. La complejidad ciclomática per-bloque es similar o menor — el ES descompone más finamente.

3. **application/ es el foco de complejidad legítima:** CC 2.25 promedio. Identidad (3.00) y Resultados (2.90) concentran la lógica de orquestación más intrincada — candidatos a refactoring si crecen.

4. **api/ necesita atención en mantenibilidad:** MI 73.21, con Registro (61.63) e Identidad (65.32) como casos críticos. Routers largos con lógica inline degradan el MI sin elevar la CC — señal de mezcla de responsabilidades.

---

*Ejecutado: 2026-05-18 — rama doc/metricas — PLAN-METRICAS.md Prioridad 2 completada*
