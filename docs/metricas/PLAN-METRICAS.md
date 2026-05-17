# Plan de Métricas — AtaraxiaDive

> Estado documental: vigente
> Fuente de verdad para: estrategia de medición del producto y del experimento IEDD
> Última actualización: 2026-05-17

---

## 1. Propósito

Este plan define qué métricas levantar, desde qué fuentes, con qué herramientas y cómo almacenar los resultados. El objetivo es producir evidencia cuantitativa para:

1. **Análisis del producto** — calidad técnica del código entregado
2. **Análisis del experimento IEDD** — productividad, overhead y evolución del proceso

---

## 2. Estructura de carpetas

```
docs/metricas/
├── PLAN-METRICAS.md              ← este archivo
├── estructurales/
│   ├── backend-raw.md            ← radon raw + cloc backend
│   ├── backend-cc.md             ← complejidad ciclomática por módulo
│   ├── backend-mi.md             ← índice de mantenibilidad por módulo
│   ├── backend-halstead.md       ← métricas Halstead
│   ├── backend-por-capa.md       ← métricas cruzadas BC × capa hexagonal
│   ├── frontend-raw.md           ← cloc frontend
│   ├── frontend-estructura.md    ← distribución páginas/componentes/hooks
│   └── frontend-duplicacion.md  ← jscpd
├── calidad/
│   ├── designreviewer-evolucion.md  ← WARNING count por INC (SP1→SP7)
│   ├── architectanalyst-d.md        ← métrica D por BC por baseline
│   ├── cobertura-tests.md           ← pytest-cov por BC y por capa
│   └── test-to-code-ratio.md        ← LOC tests / LOC producción
└── productividad/
    ├── velocidad-sp.md              ← US/SP, PRs/SP, commits/SP
    ├── overhead-pipeline.md         ← tiempo por fase IEDD (tracker)
    ├── sp-adj-ratio.md              ← deuda técnica formalizada por SP
    └── cobertura-rf.md              ← RFs implementados por área y SP
```

---

## 3. Categoría A — Métricas Estructurales

### A.1 Backend Python

**Herramienta principal:** `radon` (disponible v6.0.1)  
**Fuente:** `src/`  
**Alcance:** todos los BCs + shared

#### A.1.1 LOC y composición

```bash
# Por archivo y totales
cloc src/ --include-lang=Python --by-file --quiet > docs/metricas/estructurales/backend-raw.md

# Raw metrics por módulo (LOC, SLOC, comentarios, blancos)
python -m radon raw src/ -s > docs/metricas/estructurales/backend-raw-radon.txt
```

**Desglose esperado:** LOC total · SLOC · ratio comentarios · blancos

#### A.1.2 Complejidad Ciclomática (CC)

```bash
# CC por función, ordenado por complejidad descendente
python -m radon cc src/ -s -a -n C > docs/metricas/estructurales/backend-cc.md

# Solo funciones con CC alto (C o superior = CC ≥ 7)
python -m radon cc src/ -s -n C --show-closures
```

**Escala radon:** A (1-5) · B (6-10) · C (11-15) · D (16-20) · E (21-25) · F (≥26)

#### A.1.3 Índice de Mantenibilidad (MI)

```bash
# MI por módulo (-s muestra el ranking A/B/C)
python -m radon mi src/ -s > docs/metricas/estructurales/backend-mi.md
```

**Escala:** A (MI ≥ 20) · B (10 ≤ MI < 20) · C (MI < 10)

#### A.1.4 Halstead

```bash
# Métricas Halstead por función (volumen, dificultad, esfuerzo, tiempo)
python -m radon hal src/ > docs/metricas/estructurales/backend-halstead.md
```

**Métricas de interés:** volumen (V) · dificultad (D) · esfuerzo (E) · tiempo estimado (T)

#### A.1.5 Métricas por capa hexagonal (análisis cruzado)

Script a construir: para cada BC, separar métricas de `domain/`, `application/`, `infrastructure/`, `api/` y comparar CC promedio y MI promedio por capa.

```bash
for bc in competencia torneo registro resultados identidad notificaciones shared; do
  echo "=== $bc ==="
  for capa in domain application infrastructure api; do
    path="src/$bc/$capa"
    [ -d "$path" ] && python -m radon cc "$path" -s -a 2>/dev/null
  done
done > docs/metricas/estructurales/backend-por-capa.md
```

**Hipótesis a verificar:** CC promedio de `domain/` en BC Competencia (ES) > CC promedio de `domain/` en BCs CRUD (Torneo, Registro, Resultados)

### A.2 Frontend TypeScript/React

**Herramienta principal:** `cloc` + `jscpd` + conteos estructurales  
**Fuente:** `frontend/src/`  
**Limitación:** CC no disponible sin herramienta adicional (lizard no soporta TS en este entorno)

#### A.2.1 LOC y composición

```bash
cloc frontend/src/ --include-lang=TypeScript,TSX --by-file --quiet \
  > docs/metricas/estructurales/frontend-raw.md
```

#### A.2.2 Distribución estructural

```bash
# Conteo por tipo de artefacto
echo "Páginas:" && find frontend/src -name "*Page.tsx" | wc -l
echo "Componentes:" && find frontend/src -name "*.tsx" | grep -v Page | grep -v ".d." | wc -l
echo "Hooks custom:" && find frontend/src -name "use*.ts" -o -name "use*.tsx" | wc -l
echo "Stores:" && find frontend/src -name "*store*" -o -name "*Store*" | wc -l
echo "API clients:" && find frontend/src -path "*/api/*.ts" | wc -l

# LOC promedio por tipo (proxy de SRP)
# Páginas
find frontend/src -name "*Page.tsx" -exec wc -l {} \; | sort -n | awk '{sum+=$1; n++} END {print "Prom:", sum/n, "Max:", max} {if($1>max)max=$1}'
```

#### A.2.3 Duplicación de código

```bash
npx jscpd frontend/src/ --min-lines 5 --min-tokens 50 \
  --reporters "markdown" \
  --output docs/metricas/estructurales/ 2>/dev/null
```

#### A.2.4 Bundle size

```bash
ls -la frontend/dist/assets/*.js | awk '{print $5, $9}' | sort -n
du -sh frontend/dist/
```

---

## 4. Categoría B — Métricas de Calidad de Producto

### B.1 Evolución DesignReviewer

**Fuente:** `quality/reports/designreviewer/` + anotaciones en `matrix.md`  
**Método:** extracción manual de WARNING count por INC desde los reportes existentes

| INC | WARNINGs | Δ vs anterior | Fuente |
|-----|----------|---------------|--------|
| INC-4.2 | 142 | baseline | INC-4.2-report.txt |
| INC-4.3 | 158 | +16 | INC-4.3-report.txt |
| INC-4.4 | 158 | 0 | INC-4.4-report.txt |
| INC-4.5 | 174 | +16 | INC-4.5-report.txt |
| INC-5.1 | 208 | +34 | INC-5.1-report.txt |
| INC-5.2 | 215 | +7 | INC-5.2-report.txt |
| INC-5.3 | 215 | 0 | INC-5.3-report.txt |
| INC-5.4 | 222 | +7 | INC-5.4-report.txt |
| INC-5.5 | 227 | +5 | INC-5.5-report.txt |
| INC-5.6 | 252 | +25 | INC-5.6-report.txt |
| INC-5.7 | 256 | +4 | INC-5.7-report.txt |
| INC-6.3 | 258 | +2 | INC-6.3-report.txt |
| INC-6.4 | 253 | −5 | INC-6.4-report.txt |
| SP-ADJ-11 | 287 | +34 | SP-ADJ-11-report.txt |

**Análisis:** tendencia, picos por INC, correlación con tipo de incremento (frontend vs backend)

### B.2 ArchitectAnalyst — Métrica D por BC

**Fuente:** `.cm/baselines/BL-*.md`  
**Método:** extracción de la tabla D por BC en cada baseline

```bash
grep -A 20 "ArchitectAnalyst\|Distancia\|should_block\|D=" .cm/baselines/BL-*.md \
  > docs/metricas/calidad/architectanalyst-d.md
```

**Métricas:** D por BC · tendencia por SP · `should_block` triggers

### B.3 Cobertura de Tests

```bash
# Cobertura por BC y capa
python -m pytest tests/ \
  --cov=src \
  --cov-report=term-missing \
  --cov-report=json:docs/metricas/calidad/coverage.json \
  -q 2>/dev/null

# Resumen por BC
python -m pytest tests/unit/ tests/integration/ \
  --cov=src --cov-report=term -q 2>/dev/null \
  > docs/metricas/calidad/cobertura-tests.md
```

### B.4 Test-to-Code Ratio

```bash
# LOC producción
cloc src/ --include-lang=Python --quiet | tail -3

# LOC tests
cloc tests/ --include-lang=Python --quiet | tail -3

# Ratio = LOC tests / LOC src
```

**Hipótesis a verificar:** ratio > 1.0 en `domain/` (dominio más testeado que infraestructura)

### B.5 BDD Waiver Rate

**Fuente:** `docs/reports/` — contar archivos `*bdd-waiver*`  
**Método:**

```bash
echo "Total US:" && ls docs/reports/ | grep -v "/" | wc -l
echo "BDD waivers:" && find docs/reports -name "*waiver*" | wc -l
echo "BDD waivers frontend:" && find docs/reports -name "*waiver*" -exec grep -l "frontend" {} \;
```

---

## 5. Categoría C — Métricas de Productividad

### C.1 Velocidad por SP

**Fuente:** `matrix.md` + `git log` + `.cm/baselines/`

```bash
# PRs por SP
gh pr list --limit 200 --state merged --json number,title,mergedAt \
  | jq '.[] | {number, title, mergedAt}' \
  > docs/metricas/productividad/prs-por-sp.json

# Commits por SP (por tag)
for tag in v0.2.0 v0.3.0 v0.4.0 v0.5.0 v0.6.0 v1.0.0 v1.0.1; do
  echo "=== $tag ===" && git log --oneline $prev..$tag 2>/dev/null | wc -l
  prev=$tag
done
```

**Métricas:** US/SP · PRs/SP · commits/SP · días/SP

### C.2 Overhead del Pipeline IEDD (tiempo por fase)

**Fuente:** archivos de tracker en `docs/reports/*/tracker-*.md` o `.cm/tracking/`

```bash
find docs/reports -name "*tracker*" -o -name "*time*" | head -20
find .cm -name "*tracker*" | head -20
```

**Métricas:** tiempo promedio por fase (0-10) · US más rápida · US más lenta · evolución del overhead por SP

### C.3 Ratio SP-ADJ

**Fuente:** `matrix.md` §§ de SP-ADJ

| SP | US funcionales | US de ajuste (SP-ADJ) | Ratio ajuste |
|----|:--------------:|:---------------------:|:------------:|
| SP1 | 9 | 5 (ADJ-01) | 55% |
| SP2 | 3 | 3 (ADJ-02) | 100% |
| SP3 | 11 | 8 (ADJ-03) + 6 (ADJ-04) | 127% |
| SP4 | 21 | 7 (ADJ-06) | 33% |
| SP5 | 20 | 7 (ADJ-09) | 35% |
| SP6 | 13 | 10 (ADJ-11) | 77% |

**Análisis:** tendencia de deuda formalizada · correlación con tipo de SP

### C.4 Cobertura Funcional RF

**Fuente:** `matrix.md` §35

| Área | Total RFs | Implementados | % |
|------|:---------:|:-------------:|:-:|
| RF-GT | 7 | 7 | 100% |
| RF-IN | 10 | 9 | 90% |
| RF-PR | 8 | 8 | 100% |
| RF-EJ | 10 | 8 | 80% |
| RF-PM | 6 | 5 | 83% |
| RF-US | 5 | 5 | 100% |
| RF-NT | 4 | 2 | 50% |
| RF-IG | 4 | 0 | 0% (fuera scope) |
| **Total** | **54** | **44** | **81%** |

---

## 6. Orden de ejecución

| Prioridad | Categoría | Tiempo estimado | Resultado |
|-----------|-----------|:---------------:|-----------|
| 1 | A.1.1 a A.1.4 — Backend raw/CC/MI/Halstead | 30 min | 4 archivos en `estructurales/` |
| 2 | A.1.5 — Backend por capa hexagonal | 30 min | análisis cruzado BC × capa |
| 3 | B.3/B.4 — Cobertura y ratio tests | 20 min | pytest-cov ejecutado |
| 4 | B.1/B.2 — DesignReviewer + ArchitectAnalyst | 30 min | serie temporal extraída |
| 5 | A.2 — Frontend LOC + duplicación | 20 min | cloc + jscpd ejecutados |
| 6 | C.1/C.3 — Velocidad SP + ratio ADJ | 30 min | datos de git + matrix |
| 7 | C.2 — Overhead pipeline (tracker) | 45 min | requiere localizar archivos tracker |
| 8 | Síntesis | 60 min | reporte integrado `REPORTE-METRICAS.md` |

---

## 7. Reporte final

Al completar todas las categorías, generar `docs/metricas/REPORTE-METRICAS.md` con:

1. Resumen ejecutivo (tablas y valores clave)
2. Análisis estructural backend: CC/MI por BC y por capa
3. Análisis estructural frontend: LOC y distribución
4. Calidad: evolución DesignReviewer + cobertura tests
5. Productividad: velocidad + overhead + ratio SP-ADJ
6. Conclusiones para el paper IEDD

---

*Creado: 2026-05-17 — SP7 INC-7.2 (adecuación documental)*
*Ejecutar en orden de §6 para construir evidencia incremental*
