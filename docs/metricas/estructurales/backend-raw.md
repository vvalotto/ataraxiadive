# Métricas RAW por BC · Capa · Módulo — Backend Python

> Herramienta: `radon raw` v6.0.1
> Fuente: `src/`
> Fecha de ejecución original: 2026-05-18 · **Recálculo Ronda 2: 2026-08-13 (HEAD `main`, post SP7 + SP-ADJ-12 + SP-ADJ-13, tag v1.0.5)**
> **Actualizado post-limpieza: 2026-08-13 — commit `b832d25`, eliminación de código muerto en identidad**
> Referencia: PLAN-METRICAS.md §A.1.1 (Ronda 2)

---

## Totales por BC — BL-006 vs v1.0.5 (post-limpieza)

| BC | LOC BL-006 | LOC v1.0.5 | SLOC BL-006 | SLOC v1.0.5 | Archivos BL-006 | Archivos v1.0.5 | Δ SLOC |
|----|-----:|-----:|-----:|-----:|:---:|:---:|:---:|
| competencia | 8 346 | 8 346 | 5 305 | 5 305 | 103 | 103 | = |
| torneo | 1 334¹ | 1 334 | 1 056¹ | 1 056 | 31 | 31 | = |
| registro | 2 353 | **2 509** | 1 907 | **2 042** | 50 | **52** | **+135** |
| resultados | 2 662 | 2 662 | 1 801 | 1 801 | 34 | 34 | = |
| identidad | 1 227 | **1 378** | 979 | **1 102** | 29 | **31** | **+123** |
| notificaciones | 1 279 | 1 279 | 1 036 | 1 036 | 39 | 39 | = |
| shared | 534 | 534 | 306 | 306 | 17 | 17 | = |
| app (raíz) | 694 | 694 | 571 | 571 | 1 | 1 | = |
| **Total backend** | **18 429** | **18 736** | **12 961** | **13 219** | **304** | **307** | **+258** |

¹ El archivo original (commit `fa02f82`, 2026-05-18) registró `torneo: 19760 LOC · 14015 SLOC` — un
error evidente de generación (el propio `backend-por-capa.md` de esa fecha usaba el total correcto
de 12 961 SLOC para el backend, que solo cierra con torneo≈1 056 SLOC, no 14 015). Se usa aquí el
valor recalculado con `radon raw -j`, confirmado idéntico al de v1.0.5 — `torneo` no cambió.

**Confirmación cruzada:** el delta total (+258 SLOC, +3 archivos) coincide **exactamente** con la
suma de `registro` (+135) e `identidad` (+123) — ningún otro BC tuvo un solo archivo o línea de
diferencia desde el 2026-05-18. Esto es consistente con `backend-por-capa.md`, `backend-halstead.md`
y `backend-ck.md`: **todo el trabajo de SP7 + SP-ADJ-12 + SP-ADJ-13 sobre el backend se concentró
en esos dos BCs** (modelo multi-rol + aceptación de inscripciones); el resto del código no se tocó.

> **Nota de la limpieza (2026-08-13, commit `b832d25`):** los valores v1.0.5 de esta tabla ya
> reflejan la eliminación de `agregar_rol_usuario.py`/`quitar_rol_usuario.py` (40 SLOC de código
> muerto en `identidad/application/`, ver `cobertura-tests.md §3`). Antes de la limpieza, identidad
> mostraba +163 SLOC (1 142) y el total backend +298 SLOC (13 259) — esos números quedaron
> registrados en el historial de commits de este archivo para trazabilidad, pero ya no son el
> estado actual.

---

## Módulos nuevos o modificados — `registro`

| Módulo | Capa | LOC | SLOC | Origen |
|--------|------|----:|-----:|--------|
| `router.py` | api | 935 | 788 | Endpoints de aceptación de inscripción + descarga de adjuntos (SP-ADJ-12) |
| `inscripcion.py` | domain | 91 | 75 | `estado_aceptacion` (ACEPTADO/RECHAZADO) en el aggregate |
| `adjunto_storage_port.py` | domain | 16 | 13 | Puerto nuevo para descarga de adjuntos con auth |
| `local_adjunto_storage.py` | infrastructure | 26 | 21 | Adaptador de storage de adjuntos |

## Módulos nuevos o modificados — `identidad`

| Módulo | Capa | LOC | SLOC | Origen |
|--------|------|----:|-----:|--------|
| `router.py` | api | 385 | 335 | Endpoints `POST/DELETE /auth/me/roles` |
| `agregar_rol.py` | application | 26 | 19 | `AgregarRolCommand`/`AgregarRolHandler` — usado por el router |
| `quitar_rol.py` | application | ~26 | ~19 | `QuitarRolCommand`/`QuitarRolHandler` — usado por el router |
| ~~`agregar_rol_usuario.py`~~ | ~~application~~ | ~~27~~ | ~~20~~ | **Eliminado (commit `b832d25`)** — código muerto, nunca importado |
| ~~`quitar_rol_usuario.py`~~ | ~~application~~ | ~~27~~ | ~~20~~ | **Eliminado (commit `b832d25`)** — código muerto, nunca importado |

---

## BCs sin cambios desde 2026-05-18

`competencia`, `torneo`, `resultados`, `notificaciones`, `shared` y `app` (raíz) tienen **exactamente** el mismo LOC, SLOC y cantidad de archivos que en la medición BL-006. El detalle módulo por módulo de esos BCs sigue siendo válido tal como está documentado en la versión histórica de este archivo (commit `fa02f82`, 2026-05-18) — no se reproduce aquí para evitar duplicación.

Para el desglose completo por capa (domain/application/infrastructure/api) de todos los BCs, ver `backend-por-capa.md §1`.

---

*Ejecutado: 2026-05-18 — rama doc/metricas — PLAN-METRICAS.md §A.1.1 completado*
*Recalculado: 2026-08-13 — HEAD `main` post SP-ADJ-13 (tag v1.0.5) — PLAN-METRICAS.md §A.1.1 (Ronda 2)*
