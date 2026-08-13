# Complejidad Ciclomática (CC) por BC · Capa · Módulo — Backend Python

> Herramienta: `radon cc` v6.0.1
> Fuente: `src/`
> Fecha de ejecución original: 2026-05-18 · **Recálculo: 2026-08-13 (HEAD `main`, post SP7 + SP-ADJ-12 + SP-ADJ-13, tag v1.0.5)**

**Escala:** A (1–5) · B (6–10) · C (11–15) · D (16–20) · E (21–25) · F (≥26)

---

## Totales por BC (v1.0.5)

| BC | Bloques | CC prom | CC máx | Rank | Δ vs BL-006 |
|----|:-------:|:-------:|:------:|:----:|:---:|
| competencia | 509 | 1.80 | 9 (B) | A | = idéntico |
| torneo | 142 | 1.68 | — | A | = idéntico |
| registro | 222 | 2.06 | — | A | **+8 bloques** |
| resultados | 160 | 2.53 | — | A | = idéntico |
| identidad | 144 | 2.15 | 11 (C) | A | **+26 bloques (118→144), CC prom bajó** |
| notificaciones | 105 | 2.05 | — | A | = idéntico |
| shared | 35 | 1.94 | — | A | = idéntico |
| app | 19 | 3.58 | 11 (C) | A | = idéntico |
| **Total** | **1 336** | **2.02** | | | **+29 bloques** |

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

**Ningún bloque nuevo cruzó el umbral C+ desde BL-006**, pese al crecimiento de +216 SLOC/+30
bloques en `registro`+`identidad`. El código nuevo de SP-ADJ-12 (comandos de roles, aceptación de
inscripciones) se mantuvo en bloques simples (CC bajo) — coincide con que el CC promedio de
`identidad/application/` bajó (3.00→2.52) pese a crecer en volumen, según `backend-por-capa.md §4`.

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
| `agregar_rol_usuario.py` / `quitar_rol_usuario.py` | application | +2 nuevos | bajo (1-2) | comandos simples — bajan el CC promedio de application/ (3.00→2.52) |

**Nota:** el crecimiento de `identidad` bajó su CC promedio en `application/` (ver
`backend-por-capa.md §4`) porque los métodos nuevos son handlers pequeños y directos, no lógica
densa — el WMC (conteo absoluto de métodos largos) sí subió levemente, según `backend-ck.md`.

---

*Ejecutado: 2026-05-18 — rama doc/metricas — PLAN-METRICAS.md §A.1.2 completado*
*Recalculado: 2026-08-13 — HEAD `main` post SP-ADJ-13 (tag v1.0.5) — PLAN-METRICAS.md §A.1.2 (Ronda 2)*
