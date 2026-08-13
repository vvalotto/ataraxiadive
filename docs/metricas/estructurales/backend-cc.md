# Complejidad Ciclomática (CC) por BC · Capa · Módulo — Backend Python

> Herramienta: `radon cc` v6.0.1
> Fuente: `src/`
> Fecha de ejecución original: 2026-05-18 · **Recálculo Ronda 2: 2026-08-13 (HEAD `main`, post SP7 + SP-ADJ-12 + SP-ADJ-13, tag v1.0.5)**
> **Actualizado post-limpieza: 2026-08-13 — commit `b832d25`, eliminación de código muerto en identidad**

**Escala:** A (1–5) · B (6–10) · C (11–15) · D (16–20) · E (21–25) · F (≥26)

---

## Totales por BC (v1.0.5)

| BC | Bloques | CC prom | CC máx | Rank | Δ vs BL-006 |
|----|:-------:|:-------:|:------:|:----:|:---:|
| competencia | 509 | 1.80 | 9 (B) | A | = idéntico |
| torneo | 142 | 1.68 | — | A | = idéntico |
| registro | 222 | 2.06 | — | A | **+8 bloques** |
| resultados | 160 | 2.53 | — | A | = idéntico |
| identidad | 136 | 2.12 | 11 (C) | A | **+18 bloques (118→136), post-limpieza** |
| notificaciones | 105 | 2.05 | — | A | = idéntico |
| shared | 35 | 1.94 | — | A | = idéntico |
| app | 19 | 3.58 | 11 (C) | A | = idéntico |
| **Total** | **1 328** | **2.02** | | | **+21 bloques** |

> Post-limpieza (commit `b832d25`): identidad tenía 144 bloques antes de eliminar los 8 bloques
> del código muerto (`agregar_rol_usuario.py`/`quitar_rol_usuario.py`). El total del proyecto era
> 1 336 bloques antes de la limpieza.

Ver desglose completo CC × capa por BC en [`backend-por-capa.md §1`](backend-por-capa.md) — la
tabla de allí es la fuente autoritativa para el análisis cruzado por capa hexagonal.

---

## Bloques con CC ≥ C (11+) — funciones/métodos de mayor complejidad

Umbral: `radon cc -n C` (CC ≥ 11). **Verificado 2026-08-13:** son exactamente los mismos dos
bloques que en la medición original, sin cambios:

| Rank | Ubicación | Bloque | CC | Δ vs BL-006 |
|:----:|-----------|--------|:--:|:---:|
| C | `src/app.py:582` | `_obtener_disciplinas_pendientes_ejecucion` | 11 | = idéntico |
| C | `src/identidad/application/commands/registrar_usuario.py:69` | `RegistrarUsuarioHandler.handle` | 11 | = idéntico |

**Ningún bloque nuevo cruzó el umbral C+ desde BL-006**, pese al crecimiento de +258 SLOC/+26
bloques (post-limpieza) en `registro`+`identidad`. El código nuevo de SP-ADJ-12 (comandos de
roles, aceptación de inscripciones) se mantuvo en bloques simples (CC bajo) — coincide con que el
CC promedio de `identidad/application/` bajó de 3.00 a 2.52 con el código muerto todavía presente,
y quedó en 2.71 tras eliminarlo (commit `b832d25`) — ver `backend-por-capa.md §4`.

---

## registro — módulos con mayor CC (v1.0.5)

| Módulo | Capa | Bloques | CC prom | Δ |
|--------|------|:-------:|:-------:|:---:|
| `router.py` | api | +5 | 2.20 | nuevos endpoints de aceptación/adjuntos |
| `inscripcion.py` | domain | = | 2.09 | `estado_aceptacion` agregó bloques pequeños |

## identidad — módulos con mayor CC (v1.0.5)

| Módulo | Capa | Bloques | CC prom | Δ |
|--------|------|:-------:|:-------:|:---:|
| `router.py` | api | +4 | 2.64 | endpoints `POST/DELETE /auth/me/roles` |
| `agregar_rol.py` / `quitar_rol.py` | application | +2 nuevos | bajo (1-2) | comandos simples, realmente usados por el router — bajan el CC promedio de application/ (3.00→2.71) |

> Se eliminaron (commit `b832d25`) los archivos `agregar_rol_usuario.py`/`quitar_rol_usuario.py`
> — una primera versión de estos comandos que quedó como código muerto, nunca conectada al router.

**Nota:** el crecimiento de `identidad` bajó su CC promedio en `application/` (ver
`backend-por-capa.md §4`) porque los métodos nuevos son handlers pequeños y directos, no lógica
densa — el WMC (conteo absoluto de métodos largos) sí subió levemente, según `backend-ck.md`.

---

*Ejecutado: 2026-05-18 — rama doc/metricas — PLAN-METRICAS.md §A.1.2 completado*
*Recalculado: 2026-08-13 — HEAD `main` post SP-ADJ-13 (tag v1.0.5) — PLAN-METRICAS.md §A.1.2 (Ronda 2)*
