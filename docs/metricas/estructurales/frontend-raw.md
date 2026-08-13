# Métricas Frontend — LOC y Composición

> Fuente: `cloc frontend/src/`
> Herramienta: cloc 2.08
> Fecha de ejecución original: 2026-05-18 · **Recálculo: 2026-08-13 (HEAD `main`, post SP7 + SP-ADJ-12 + SP-ADJ-13, tag v1.0.5)**
> Referencia: PLAN-METRICAS.md §A.2.1

---

## 1. Resumen global

| Lenguaje | Archivos BL-006 | SLOC BL-006 | Archivos v1.0.5 | SLOC v1.0.5 | Δ SLOC |
|----------|:--------:|-----:|:--------:|-----:|:---:|
| TypeScript / TSX | 115 | 15 623 | **116** | **15 754** | +131 |
| CSS | 1 | 14 | 1 | 14 | = |
| **Total** | **116** | **15 637** | **117** | **15 768** | **+131** |

**Crecimiento del frontend en 3 meses: +131 SLOC (+0.8%), +1 archivo.** Prácticamente estable —
consistente con que SP7 (despliegue + manual) no tocó código de frontend, y SP-ADJ-12/13 fueron
fixes puntuales de UI, no features nuevas de superficie grande.

**Relación comentarios/código:** sin cambios significativos — el código sigue prácticamente sin
comentarios, auto-documentado por nombres descriptivos.

---

## 2. LOC por subdirectorio funcional (cloc directo, v1.0.5)

| Directorio | Archivos BL-006 | SLOC BL-006 (aprox.) | Archivos v1.0.5 | SLOC v1.0.5 |
|------------|:--------:|-----:|:--------:|-----:|
| `pages/` | 37 + estructura | ~8 999 | 37 | **8 134** |
| `components/` | ~50 | ~4 356 | 48 | **4 375** |
| `hooks/` | 9 | ~1 254 | 9 | **1 133** |
| `api/` | 8 | 1 469 | 8 | **1 329** |
| `stores/` | 3 | 174 | 3 | **159** |

> **Nota metodológica:** los valores BL-006 de esta tabla ya venían marcados como aproximados
> (`~`) en el documento original, y su suma (16 252) no cerraba contra el total reportado
> (15 637) — inconsistencia preexistente, no introducida en este recálculo. Los valores v1.0.5 son
> mediciones exactas de `cloc` sobre cada subdirectorio. **El conteo de archivos por carpeta es
> prácticamente idéntico** (pages 37=37, components 50≈48, hooks 9=9, api 8=8, stores 3=3) — no
> hubo reestructuración de directorios. Las pequeñas variaciones de SLOC entre BL-006 y v1.0.5
> están dentro del margen de error de la aproximación original, no representan un cambio
> estructural real.

---

## 3. Distribución estructural (v1.0.5)

| Artefacto | Archivos | SLOC | Promedio |
|-----------|:--------:|:----:|:--------:|
| Páginas (`pages/*Page.tsx`) | 36 | 8 134* | 226/página |
| Componentes (`components/*.tsx`) | 48 | 4 375 | 91/componente |
| Hooks custom (`hooks/use*.ts`) | 9 | 1 133 | 126/hook |
| API clients (`api/*.ts`) | 8 | 1 329 | 166/cliente |
| Stores | 3 | 159 | 53/store |

\* Incluye `pages/atleta/portalData.ts` (1 archivo no-Page dentro de `pages/`).

---

## 4. Confirmación cruzada con backend-por-capa.md

El frontend, igual que el backend, no muestra evidencia de crecimiento generalizado: el `+117
SLOC` total es consistente con fixes puntuales (SP-ADJ-13: Audit Log, spacing de Resultados, nav
móvil hamburguesa — PR #217) más que con nueva funcionalidad de superficie amplia. Esto refuerza
la conclusión ya establecida en el backend (`backend-raw.md §Confirmación cruzada`): **SP7 y
SP-ADJ-13 fueron incrementos de infraestructura/UI acotados, no expansión de producto.**

---

---

## 5. Bundle size (A.2.4)

| Métrica | v1.0.5 (2026-08-13, rebuild) | Build anterior (dist/, 2026-05-24) |
|---------|:---:|:---:|
| JS principal | 673.74 kB (gzip 180.99 kB) | 674.82 kB (idéntico) |
| CSS | 68.17 kB (gzip 10.75 kB) | — |
| `dist/` total | 780 KB | 784 KB |

El bundle JS es **prácticamente idéntico** al build de referencia previo a SP-ADJ-13 (674.8 kB vs
673.7 kB) — confirma que el crecimiento de +131 SLOC no impactó el peso de la aplicación. Vite
sigue advirtiendo sobre el chunk único > 500 kB (sin code-splitting) — observación preexistente,
no una regresión de esta ronda.

---

*Ejecutado: 2026-05-18 — rama doc/metricas — PLAN-METRICAS.md §A.2.1 completado*
*Recalculado: 2026-08-13 — HEAD `main` post SP-ADJ-13 (tag v1.0.5) — PLAN-METRICAS.md §A.2.1/§A.2.2/§A.2.4 (Ronda 2)*
