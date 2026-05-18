# Ratio SP-ADJ — Deuda Técnica Formalizada por SP

> Fuente: matrix.md (§§ SP-ADJ) · CLAUDE.md §5 · PLAN-METRICAS.md §C.3  
> Definición: ratio = US de ajuste / US funcionales del mismo SP  
> Fecha de extracción: 2026-05-18  
> Referencia: PLAN-METRICAS.md §C.3

---

## 1. Tabla de ratio por SP

| SP | US func. | SP-ADJ | US ajuste | Ratio | % |
|----|:--------:|--------|:---------:|:-----:|:-:|
| SP1 | 9 | ADJ-01 | 5 | 0.56 | **56%** |
| SP2 | 3 | ADJ-02 | 3 | 1.00 | **100%** |
| SP3 | 11 | ADJ-03 + ADJ-04 | 14 | 1.27 | **127%** |
| SP4 | 21 | ADJ-06 | 7 | 0.33 | **33%** |
| SP5 | 20 | ADJ-07 + ADJ-09 | 7 | 0.35 | **35%** |
| SP6 | 13 | ADJ-11 | 10 | 0.77 | **77%** |
| **Total** | **77** | **6 SP-ADJ** | **46** | **0.60** | **60%** |

**Promedio global:** por cada US funcional implementada, el proyecto generó 0.60 US de ajuste técnico.

---

## 2. Tendencia del ratio

```
SP1  ████████████░░░░░░░░░░░  56%
SP2  ████████████████████████  100%
SP3  ████████████████████████████████  127%  ← pico
SP4  ████████░░░░░░░░░░░░░░░░  33%   ← mínimo
SP5  █████████░░░░░░░░░░░░░░░  35%
SP6  ███████████████████░░░░░  77%
```

**Patrón en U invertida con normalización:**
- SP1–SP3: ratio creciente. Los primeros sprints generan deuda técnica acumulada que se liquida en el SP-ADJ siguiente.
- SP4–SP5: ratio mínimo. El equipo ha interiorizado los patrones del proyecto; la deuda técnica se genera a menor ritmo.
- SP6: ratio sube a 77% por SP-ADJ-11 (modelo multi-rol completo — 10 US de ajuste para Juez + Organizador en BC Registro + BC Identidad). No es regresión sino incorporación de complejidad nueva deliberada.

---

## 3. Análisis por SP-ADJ

### SP-ADJ-01 (SP1) — 5 US · ratio 56%

**Contenido:** correcciones de arquitectura hexagonal post-implementación. Muchos SP-ADJ-01 involucraron la separación correcta de capas que en el primer sprint se implementaron mezcladas.

**Causa:** SP1 fue el sprint de aprendizaje del pipeline IEDD. El equipo no tenía aún la inercia del proceso.

### SP-ADJ-02 (SP2) — 3 US · ratio 100%

**Contenido:** refactoring de las 3 US funcionales de SP2 (la más corta en duración: 4 días). Las US de SP2 implementaron funcionalidad nueva pero dejaron deuda en la frontera de los BCs Competencia y Resultados.

**Causa:** SP2 priorizó velocidad de entrega (4 días) sobre calidad técnica. El ratio 1:1 indica que el ajuste fue proporcional a la producción.

### SP-ADJ-03 + SP-ADJ-04 (SP3) — 14 US · ratio 127%

**El único SP con más US de ajuste que US funcionales.** SP3 introdujo BC Torneo, BC Registro, BC Resultados e Identidad básica — cuatro BCs nuevos en 7 días generaron fricción de integración significativa.

**Desglose:**
- ADJ-03 (8 US): correcciones de diseño en aggregates Torneo + Registro, separación ACL Resultados
- ADJ-04 (6 US): discrepancias entre modelo y datos reales del torneo Buenos Aires 2025

**Causa:** SP3 es el sprint de mayor ambición relativa (4 BCs en 7 días). El alto ratio es el costo de integrar muchos contextos simultáneamente. El descubrimiento de datos reales (torneo BA 2025) generó un SP-ADJ extra no anticipado.

### SP-ADJ-06/07/09 (SP4–SP5) — 7+7 US · ratios 33%/35%

**Mínimo histórico del proyecto.** SP4 y SP5 tienen los ratios más bajos porque:
1. Los patrones arquitectónicos están establecidos — no hay fricción de aprendizaje
2. Los BCs base están estables — la deuda nueva es incremental
3. El pipeline IEDD está interiorizado — las US se implementan con mayor calidad desde el inicio

### SP-ADJ-11 (SP6) — 10 US · ratio 77%

**El SP-ADJ más grande en US absolutas.** Incorporó el modelo multi-rol completo (Juez + Organizador), que implicó:
- BC Registro: 2 nuevas entidades (Juez + Organizador) con stack completo
- BC Identidad: refactoring del domain/ para soporte multi-rol
- Frontend: RegistroPage multi-rol, portales Juez y Organizador, creación automática de perfiles

**Causa:** la decisión de implementar multi-rol vino de UAT SP6 (retroalimentación de usuarios reales). Es deuda técnica formalizada por cambio de requisitos, no por mala implementación inicial.

---

## 4. Distribución acumulada de US

| Tipo | Cantidad | % |
|------|:--------:|:-:|
| US funcionales (features nuevas) | 77 | 63% |
| US de ajuste SP-ADJ | 46 | 37% |
| **Total** | **123** | **100%** |

El 37% de la capacidad total del proyecto se destinó a ajuste técnico formalizado. Esto incluye refactoring, corrección de diseño, mejoras de UX y adaptación a datos reales — trabajo que en proyectos tradicionales quedaría invisible o se acumularía como deuda silenciosa.

---

## 5. Correlación ratio SP-ADJ ↔ DesignReviewer Δ

| SP | Ratio ADJ | Δ DesignReviewer |
|----|:---------:|:----------------:|
| SP1 | 56% | +11 |
| SP2 | 100% | +53 |
| SP3 | 127% | +55 |
| SP4 | 33% | +89 |
| SP5 | 35% | +48 |
| SP6 | 77% | +31 |

**Correlación inversa parcial:** los SPs con menor ratio ADJ (SP4, SP5) tienen Δ DesignReviewer variado — SP4 tuvo el mayor Δ (+89) pero el menor ratio. Esto indica que el Δ DesignReviewer captura código nuevo (features), no calidad del proceso. El ratio SP-ADJ captura la deuda técnica *formalizada* como US, que es independiente del volumen de code smells acumulado.

---

## 6. Interpretación para el experimento IEDD

1. **SP-ADJ como mecanismo de liquidación de deuda:** el proyecto nunca acumuló deuda técnica silenciosa. Cada ciclo terminó con un SP-ADJ que convirtió la deuda en US-IEDD formales con precondición, postcondición e invariantes. Esta formalización es una característica del método IEDD, no un overhead.

2. **El ratio 60% global es un benchmark para proyectos IEDD similares.** Proyectos de alta complejidad arquitectónica (hexagonal + ES + PWA offline) con equipo de 1 persona y método incremental pueden esperar ≈ 0.6 US de ajuste por US funcional.

3. **Los ratios bajos (SP4–SP5) coinciden con la madurez del pipeline:** cuando el método IEDD está interiorizado, la deuda técnica se genera a menor tasa. El ratio puede usarse como proxy de madurez del proceso.

4. **SP3 como punto de inflexión:** el ratio 127% en SP3 señala el momento de máxima tensión del proyecto — muchos BCs nuevos en poco tiempo. El hecho de que SP4 baje al 33% inmediatamente indica resiliencia del método.

---

*Extraído: 2026-05-18 — rama doc/metricas — PLAN-METRICAS.md §C.3 completado*
