# Métricas Backend por Capa Hexagonal — AtaraxiaDive

> Fuente: `radon cc -j` y `radon mi -j` sobre cada `src/<bc>/<capa>/`
> Herramienta: radon 6.0.1
> Fecha de ejecución original: 2026-05-18 · **Recálculo: 2026-08-13 (HEAD `main`, post SP7 + SP-ADJ-12 + SP-ADJ-13, tag v1.0.5)**
> Referencia: PLAN-METRICAS.md §A.1.5 (Ronda 2)

---

## 1. Tabla principal — CC × MI por BC y capa (v1.0.5)

**Leyenda:** CC = complejidad ciclomática promedio · MI = índice de mantenibilidad promedio · N(CC) = bloques analizados · SLOC = líneas de código fuente
**Escala CC:** A (1–5) · B (6–10) · C (11–15) · D (16–20)
**Escala MI:** A (≥ 20) · B (10–20) · C (< 10)
**Δ** = variación vs. medición 2026-05-18 (BL-006). `=` sin cambio material.

### 1.1 domain/

| BC | Tipo | CC prom | N(CC) | MI prom | SLOC | Δ SLOC |
|----|------|:-------:|:-----:|:-------:|-----:|:---:|
| competencia | ES (Core) | 1.74 | 219 | 87.64 | 2 278 | = |
| notificaciones | ES (Generic) | 1.84 | 50 | 84.75 | 404 | = |
| torneo | CRUD | 1.55 | 44 | 90.85 | 248 | = |
| registro | CRUD | 2.09 | 66 | 83.76 | 336 | **+12** |
| resultados | CRUD | 2.53 | 64 | 88.13 | 613 | = |
| identidad | CRUD | 1.53 | 53 | 94.90 | 162 | **+22** |
| shared | Shared | 1.92 | 26 | 92.29 | 151 | = |
| **Promedio** | | **1.86** | **522** | **88.02** | **4 192** | **+34** |

### 1.2 application/

| BC | Tipo | CC prom | N(CC) | MI prom | SLOC | Δ SLOC |
|----|------|:-------:|:-----:|:-------:|-----:|:---:|
| competencia | ES (Core) | 1.92 | 157 | 83.15 | 1 481 | = |
| notificaciones | ES (Generic) | 2.04 | 26 | 74.53 | 278 | = |
| torneo | CRUD | 1.68 | 47 | 74.82 | 246 | = |
| registro | CRUD | 1.96 | 56 | 66.95 | 382 | **+19** |
| resultados | CRUD | 2.90 | 60 | 66.69 | 734 | = |
| identidad | CRUD | **2.71** | **34** | **56.48** | **338** | **+38** |
| shared | Shared | — | — | — | — | = |
| **Promedio** | | **2.13** | **380** | **73.93** | **3 459** | **+57** |

> Actualizado post-limpieza (commit `b832d25`): identidad/application pasó de 42→34 bloques y
> 378→338 SLOC tras eliminar `agregar_rol_usuario.py`/`quitar_rol_usuario.py` (código muerto). El
> CC promedio subió levemente (2.52→2.71) porque los bloques eliminados eran triviales (CC=1) y
> diluían el promedio hacia abajo.

### 1.3 infrastructure/

| BC | Tipo | CC prom | N(CC) | MI prom | SLOC | Δ SLOC |
|----|------|:-------:|:-----:|:-------:|-----:|:---:|
| competencia | ES (Core) | 2.16 | 37 | 84.62 | 391 | = |
| notificaciones | ES (Generic) | 2.45 | 29 | 81.82 | 354 | = |
| torneo | CRUD | 1.81 | 16 | 74.68 | 154 | = |
| registro | CRUD | 2.18 | 49 | 60.11 | 536 | **+7** |
| resultados | CRUD | 2.24 | 21 | 71.45 | 160 | = |
| identidad | CRUD | 2.00 | 21 | 72.57 | 187 | **+1** |
| shared | Shared | 2.11 | 9 | 55.56 | 153 | = |
| **Promedio** | | **2.17** | **182** | **76.12** | **1 935** | **+8** |

### 1.4 api/

| BC | Tipo | CC prom | N(CC) | MI prom | SLOC | Δ SLOC |
|----|------|:-------:|:-----:|:-------:|-----:|:---:|
| competencia | ES (Core) | 1.60 | 96 | 82.29 | 1 155 | = |
| notificaciones | ES (Generic) | — | — | — | 0 | = |
| torneo | CRUD | 1.80 | 35 | 78.90 | 408 | = |
| registro | CRUD | 2.20 | 51 | 19.36 | 788 | **+97** |
| resultados | CRUD | 2.33 | 15 | 48.78 | 294 | = |
| identidad | CRUD | 2.64 | 28 | 45.16 | 415 | **+62** |
| shared | Shared | — | — | 100.00 | 2 | = |
| **Promedio** | | **1.95** | **225** | **68.69** | **3 062** | **+161** |

---

## 2. Resumen cruzado por capa (promedio global)

| Capa | CC prom BL-006 | CC prom v1.0.5 | MI prom BL-006 | MI prom v1.0.5 | SLOC BL-006 | SLOC v1.0.5 |
|------|:-------:|:-------:|:-------:|:-------:|-----:|-----:|
| domain/ | 1.89 | **1.86** | 90.07 | **88.02** | 4 158 | **4 192** |
| application/ | 2.25 | **2.13** | 77.15 | **73.93** | 3 402 | **3 459** |
| infrastructure/ | 2.12 | **2.17** | 82.32 | **76.12** | 1 927 | **1 935** |
| api/ | 2.08 | **1.95** | 73.21 | **68.69** | 2 901 | **3 062** |

**El patrón emergente se mantiene idéntico:** `domain/` sigue siendo la capa con menor CC y mayor MI del sistema — el crecimiento post-SP6 (+256 SLOC en total, +6.8%, tras la limpieza de código muerto) no alteró la jerarquía CC/MI entre capas. `api/` sigue siendo la capa con MI más bajo.

**Nota metodológica sobre las variaciones de MI:** los deltas de MI (p. ej. domain 90.07→88.02) son en parte un artefacto de la exclusión de archivos triviales (`__init__.py` vacíos), que puede diferir levemente entre la corrida original y esta — no se debe leer como una caída real de mantenibilidad salvo donde coincide con crecimiento real de SLOC (registro, identidad). Los valores de **CC y SLOC son comparables directamente** porque provienen de una agregación mecánica (suma/promedio de bloques), sin exclusiones.

**Todo el crecimiento estructural post-SP6 se concentra en `registro` e `identidad`**, y dentro de esos dos BCs, específicamente en `application/` y `api/` — exactamente donde SP-ADJ-12 agregó el modelo multi-rol (`agregar_rol`/`quitar_rol`, endpoints `POST/DELETE /auth/me/roles`) y `estado_aceptacion` de inscripciones. `competencia`, `torneo`, `resultados`, `notificaciones` y `shared` no cambiaron en **ninguna** métrica (CC, N(CC), SLOC) desde el 2026-05-18.

---

## 3. Hipótesis A.1.5 — ¿ES más complejo que CRUD en domain/? (revalidación)

**Hipótesis:** CC promedio de `domain/` en BC Competencia (ES) > CC promedio de `domain/` en BCs CRUD

| BC | Tipo | domain/ CC BL-006 | domain/ CC v1.0.5 |
|----|------|:----------:|:----------:|
| competencia | **ES (Core)** | **1.74** | **1.74** = |
| notificaciones | ES (Generic) | 1.84 | 1.84 = |
| torneo | CRUD | 1.55 | 1.55 = |
| **registro** | CRUD | **2.11** | **2.09** ≈ |
| **resultados** | CRUD | **2.53** | **2.53** = |
| identidad | CRUD | 1.51 | 1.53 ≈ |

**Resultado: hipótesis sigue NO confirmada, sin cambios desde BL-006.** El ranking relativo de CC en domain/ es idéntico. `competencia/domain/` sigue con 219 bloques inmutables desde SP6 — 3 meses de trabajo posterior no tocaron el dominio ES Core.

---

## 4. Módulos de riesgo por capa (v1.0.5)

### application/ — puntos de complejidad elevada

| BC | CC prom application/ | Observación |
|----|:--------------------:|-------------|
| resultados | 2.90 | Sin cambios — queries complejos de ranking |
| identidad | 2.71 | **Bajó desde 3.00, después subió levemente tras la limpieza** — el crecimiento neto (+38 SLOC, `agregar_rol.py`/`quitar_rol.py`, los comandos realmente usados) son handlers pequeños y simples, no lógica densa. Los dos archivos huérfanos (`agregar_rol_usuario.py`/`quitar_rol_usuario.py`) se eliminaron en commit `b832d25` por ser código muerto |
| notificaciones | 2.04 | Sin cambios |

### api/ — MI bajo (mantenibilidad reducida)

| BC | SLOC api/ v1.0.5 | Δ vs BL-006 | Observación |
|----|-----------------:|:---:|-------------|
| registro | 788 | **+97** | `router.py` pasó a 788 SLOC — nuevos endpoints de aceptación de inscripción y adjuntos (SP-ADJ-12) |
| identidad | 415 | **+62** | `router.py` (385 SLOC) + `dependencies.py` — endpoints `POST/DELETE /auth/me/roles` |
| resultados | 294 | = | Sin cambios |

**Router `registro/api/router.py` y `identidad/api/router.py` son los módulos que más crecieron en todo el backend post-SP6** — coherente con el hallazgo de `backend-ck.md` (FanOut de `registro/api/router.py` subió de 11 a 12).

---

## 5. Distribución SLOC por capa (v1.0.5)

```
domain/         4 192 SLOC  (33%)  ████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░
application/    3 459 SLOC  (28%)  █████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
api/            3 062 SLOC  (24%)  ████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
infrastructure/ 1 935 SLOC  (15%)  ████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
```

Total backend por capa: 12 648 SLOC (de 13 219 SLOC totales, post-limpieza — la diferencia son
módulos raíz sin capa asignada: `src/app.py` y `src/*/domain/` sueltos). Distribución porcentual
prácticamente idéntica a BL-006 (33/27/23/15 → 33/28/24/15).

---

## 6. Conclusiones para el experimento IEDD (revalidadas 2026-08-13, post-limpieza de código muerto)

1. **La arquitectura hexagonal sigue cumpliendo su promesa de dominio limpio** tres meses y ~256 SLOC netos después: `domain/` mantiene la menor CC (1.86) y mayor MI (88.02) de todas las capas.

2. **El paradigma ES sigue sin elevar la CC en domain/, y ahora con evidencia temporal:** `competencia/domain/` no cambió ni un bloque desde SP6 — es la parte del sistema más estable de todo el proyecto en un sentido literal, no solo relativo.

3. **El crecimiento post-SP6 fue 100% localizado:** de +258 SLOC totales de backend (post-limpieza), +123 SLOC (48%) están en `identidad` y +135 SLOC (52%) en `registro` — los dos BCs con el modelo multi-rol de SP-ADJ-12. Ningún otro BC creció. Esto es evidencia de que SP7/SP-ADJ-12/13 fueron incrementos quirúrgicos, no expansión de dominio.

4. **api/ sigue siendo la capa de menor mantenibilidad**, y el nuevo código (routers de registro e identidad) empeoró levemente esa tendencia — sigue siendo el candidato más claro a refactoring si el proyecto continuara.

---

*Ejecutado: 2026-05-18 — rama doc/metricas — PLAN-METRICAS.md Prioridad 2 completada*
*Recalculado: 2026-08-13 — HEAD `main` post SP-ADJ-13 (tag v1.0.5) — PLAN-METRICAS.md §A.1.5 (Ronda 2)*
*Actualizado post-limpieza: 2026-08-13 — commit `b832d25` (eliminación de código muerto en identidad/application)*
