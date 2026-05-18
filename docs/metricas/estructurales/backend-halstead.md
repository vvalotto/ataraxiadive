# Métricas Halstead — Backend Python

> Herramienta: `radon hal` v6.0.1  
> Fuente: `src/`  
> Fecha: 2026-05-18  
> Branch: `doc/metricas`

---

## Conceptos Halstead

| Símbolo | Significado |
|---------|-------------|
| h1 | Operadores únicos |
| h2 | Operandos únicos |
| N1 | Total operadores |
| N2 | Total operandos |
| V (Volumen) | (N1+N2) × log2(h1+h2) — tamaño del programa |
| D (Dificultad) | (h1/2) × (N2/h2) — esfuerzo de comprensión |
| E (Esfuerzo) | V × D — esfuerzo de implementación |
| T (Tiempo) | E / 18 segundos — tiempo estimado |
| B (Bugs) | V / 3000 — errores estimados |

---

## Totales globales

| Métrica | Valor |
|---------|------:|
| Volumen total (V) | 11 381 |
| Esfuerzo total (E) | 58 975 |
| Tiempo estimado | 0.9 h (~54 min) |
| Bugs estimados (B) | 3.79 |
| Módulos no vacíos | 128 |
| Dificultad promedio (D) | 0.88 |

> Nota: el tiempo Halstead es una estimación teórica de escritura pura de código; no incluye diseño, testing ni revisión.

---

## Desglose por Bounded Context

| BC | Módulos | Volumen | Esfuerzo | Bugs est. |
|----|:-------:|--------:|---------:|----------:|
| competencia | 47 | 3 170 | 13 838 | 1.06 |
| resultados | 14 | 2 637 | 18 513 | 0.88 |
| registro | 26 | 2 330 | 15 751 | 0.78 |
| app | 1 | 842 | 3 626 | 0.28 |
| notificaciones | 15 | 857 | 2 042 | 0.29 |
| identidad | 10 | 773 | 2 512 | 0.26 |
| torneo | 11 | 477 | 1 537 | 0.16 |
| shared | 4 | 296 | 1 156 | 0.10 |
| **TOTAL** | **128** | **11 382** | **58 975** | **3.81** |

---

## Observaciones

- `competencia` tiene el mayor volumen absoluto (3 170), coherente con su tamaño (45 % del SLOC total).
- `resultados` tiene el mayor esfuerzo a pesar de menor volumen que `competencia`: su D (dificultad) es más alta, indicando código más denso operacionalmente (algoritmos de ranking con múltiples operadores por función).
- `registro` ocupa el tercer lugar en esfuerzo por la lógica multi-rol (atleta/juez/organizador) en sus aggregates.
- Los 3.81 bugs estimados totales son una cota teórica (V/3000); la cobertura real de bugs se mide en `calidad/cobertura-tests.md`.
- `shared` y `torneo` tienen los valores más bajos en todas las métricas — consistente con su naturaleza de CRUD simple e interfaces de puerto.
