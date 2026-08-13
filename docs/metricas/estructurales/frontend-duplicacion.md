# Duplicación de Código Frontend — jscpd

> Fuente: `npx jscpd frontend/src/ --min-lines 5 --min-tokens 50`
> Herramienta: jscpd
> Fecha de ejecución original: 2026-05-18 · **Recálculo: 2026-08-13 (HEAD `main`, post SP7 + SP-ADJ-12 + SP-ADJ-13, tag v1.0.5)**
> Referencia: PLAN-METRICAS.md §A.2.3

---

## 1. Resumen global

| Tipo | Archivos BL-006 | Líneas BL-006 | Clones BL-006 | Dup. BL-006 | % BL-006 | Archivos v1.0.5 | Líneas v1.0.5 | Clones v1.0.5 | Dup. v1.0.5 | % v1.0.5 |
|------|:--------:|:--------------:|:------:|:-----:|:-------:|:--------:|:--------------:|:------:|:-----:|:-------:|
| TSX | 85 | 13 521 | 43 | 609 | 4.5% | 86 | 13 609 | 41 | 646 | **4.75%** |
| TypeScript (.ts) | 29 | 3 462 | 10 | 193 | 5.6% | 29 | 3 527 | 10 | 193 | **5.47%** |
| JavaScript | 76 | 5 811 | 2 | 73 | 1.3% | 78 | 5 862 | 3 | 93 | **1.59%** |
| CSS | 1 | 16 | 0 | 0 | 0% | 1 | 16 | 0 | 0 | **0%** |
| **Total** | **191** | **22 810** | **55** | **875** | **3.8%** | **194** | **23 014** | **54** | **932** | **4.05%** |

**Umbral de referencia:** < 5% duplicación es considerado aceptable en proyectos de tamaño medio.
El frontend de AtaraxiaDive subió de **3.8% a 4.05%** — sigue **dentro del rango saludable**, con
un margen menor pero sin cruzar el umbral.

**Lectura del delta:** el conteo de archivos (.ts) y clones es **idéntico** a BL-006 (29 archivos,
10 clones, 193 líneas duplicadas, sin cambios). El movimiento está en `.tsx` (+37 líneas
duplicadas, 43→41 clones — algunos clones existentes crecieron o se fusionaron) y en la categoría
`javascript` de jscpd (+1 clone, +20 líneas). No hay evidencia de un patrón de duplicación nuevo:
es crecimiento marginal sobre los mismos focos ya identificados en BL-006.

---

## 2. Focos de duplicación identificados (verificados 2026-08-13)

### 2.1 Capa API clients — sin cambios

Los mismos 3 clones documentados en BL-006 siguen presentes, en las mismas líneas relativas:

| Archivos | Líneas | Descripción |
|----------|:------:|-------------|
| `api/identidad.ts` ↔ `api/registro.ts` | 16 | Patrón de fetch con JWT idéntico |
| `api/competencia.ts` ↔ `api/identidad.ts` | 13 | Función de request helper duplicada |
| `api/competencia.ts` ↔ `api/registro.ts` | 24 | Bloque de manejo de error HTTP repetido |

**Registro creció (+133 SLOC backend, según `backend-por-capa.md`) pero `api/registro.ts` no
generó clones nuevos** — los nuevos endpoints de aceptación/adjuntos se integraron sin repetir el
patrón de fetch existente.

### 2.2 App.tsx — routing duplicado (sin cambios)

| Archivo | Líneas | Descripción |
|---------|:------:|-------------|
| `App.tsx` (líneas 256–288) | 24 | Dos bloques de rutas con estructura idéntica (portal organizador vs portal juez) |

Mismo clone, mismas líneas (offset ±1 por edición menor), sin cambios estructurales.

### 2.3 TSX pages — patrones de UI repetidos (41 clones, antes 43)

El foco principal de duplicación sigue siendo el mismo: patrones de tabla de datos, estados de
carga/error, y formularios con estructura similar entre páginas. La composición del proyecto
(`backend-por-capa.md` §5, `frontend-raw.md` §1) muestra que **`components/` creció de 37 a 48
archivos (+1 659 SLOC)** en el mismo período — parte de ese crecimiento pudo absorber duplicación
de páginas hacia componentes reutilizables, lo que explica que el número de clones bajara (43→41)
pese al crecimiento general del código.

---

## 3. Distribución de clones por zona (v1.0.5)

```
API clients (.ts):     10 clones · 193 líneas  ██████░░░░░░░░░░░░░░  21%
Pages (.tsx):          41 clones · 646 líneas  █████████████████░░░  69%
App.tsx (routing):      3 clones ·  93 líneas  ███░░░░░░░░░░░░░░░░░  10%
```

Distribución porcentual prácticamente idéntica a BL-006 (22%/70%/8% → 21%/69%/10%).

---

## 4. Interpretación para el experimento IEDD (revalidada)

- **4.05% de duplicación en 194 archivos y 23 014 líneas** sigue siendo un resultado saludable
  tres meses después, con margen frente al umbral del 5%.
- La duplicación sigue concentrada en **patrones técnicos** (fetch, layouts de UI), no en lógica
  de negocio — sin cambios en esta conclusión.
- **0 clones de lógica de dominio entre hooks**, sin cambios.
- El crecimiento del período (SP7 + SP-ADJ-12 + SP-ADJ-13) **no introdujo duplicación nueva de
  peso** — el foco de API clients se mantuvo estable pese a que `registro.ts` recibió nuevos
  endpoints, y el crecimiento de `components/` parece haber compensado, no agravado, la
  duplicación de páginas.

---

*Ejecutado: 2026-05-18 — rama doc/metricas — PLAN-METRICAS.md §A.2.3 completado*
*Recalculado: 2026-08-13 — HEAD `main` post SP-ADJ-13 (tag v1.0.5) — PLAN-METRICAS.md §A.2.3 (Ronda 2). Snapshot: `docs/metricas/estructurales/jscpd-report.json`.*
