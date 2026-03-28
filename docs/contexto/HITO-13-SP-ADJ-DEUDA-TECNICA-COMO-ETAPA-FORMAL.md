# HITO-13 — El Sprint de Ajuste Técnico como etapa formal del ciclo IEDD

| Campo | Valor |
|-------|-------|
| **Documento** | HITO-13 — Decisión metodológica de alto impacto |
| **Fecha** | 2026-03-28 |
| **Sprint** | Cierre SP2 — Revisión de calidad |
| **Relacionado** | `.work/revision-sp2/` · `vvalotto/software_limpio#45` |

---

## Contexto

Al cerrar SP2 (La Competencia), la revisión formal de calidad con DesignReviewer,
análisis manual de aggregates, revisión SOLID y ArchitectAnalyst produjo 8 issues
de refactoring concretos. Ninguno bloquea la funcionalidad, todos afectan la
mantenibilidad y la coherencia del diseño.

La pregunta emergente: **¿dónde vive este trabajo dentro del ciclo IEDD?**

Las opciones consideradas:
1. Ignorarlo y acumularlo como deuda silenciosa
2. Resolverlo dentro del siguiente SP (SP3) como trabajo paralelo
3. Formalizarlo como una etapa propia entre SPs

---

## La decisión

Se instituye el **Sprint de Ajuste Técnico (SP-ADJ)** como etapa formal del ciclo IEDD,
ejecutada entre subproyectos cuando la revisión de cierre detecta deuda significativa.

Nomenclatura: `SP-ADJ-01`, `SP-ADJ-02`, etc. — secuencial e independiente de SP1–SP5.
El primer sprint de ajuste, `SP-ADJ-01`, ocurre entre SP2 y SP3.

---

## Por qué es un hallazgo experimental

IEDD fue diseñado para modelar features: US-IEDD con precondición, postcondición e
invariantes de negocio. El experimento reveló que el marco necesita un segundo modo:
**US de refactoring técnico**, donde:

- La precondición es el smell o deuda detectada (métrica, patrón, violación)
- La postcondición es la métrica mejorada o el patrón corregido
- El invariante es que los tests no regresionan y el DesignReviewer no empeora

Este modo ya es compatible con `/implement-us` — las fases de tests, CodeGuard y
DesignReviewer aplican igual. La diferencia está en la especificación, no en la
implementación.

---

## El ciclo completo emergente

```
SP-N (features)
  └── BL-N (baseline + retrospectiva)
        └── Revisión de calidad (DesignReviewer + SOLID + ArchitectAnalyst)
              └── SP-ADJ-N (si hay deuda significativa)
                    └── BL-ADJ-N (baseline de ajuste)
                          └── SP-N+1 (features)
```

Este ciclo no estaba en el diseño original de IEDD. Emergió naturalmente del contacto
con un proyecto real. La evidencia empírica que lo justifica:

- SP2 cerró con 11 CRITICAL en DesignReviewer (todos pre-existentes o estructurales)
- 8 issues de refactoring identificados en revisión manual
- Ninguno es bloqueante, todos son degradantes si se ignoran a largo plazo
- Resolverlos dentro de SP3 crea ruido: mezcla features con refactoring, complica el DoD

---

## Implicancias para el experimento

**Hipótesis que esto toca:** H-4.1 (overhead del ecosistema) y la pregunta 1 del experimento
("¿el ecosistema CM + Dev Kit + Software Limpio funciona integrado?").

La respuesta parcial: el ecosistema funciona para detectar la deuda (quality gates operativos),
pero no provee un mecanismo formal para resolverla dentro del mismo marco metodológico.
El SP-ADJ formaliza ese mecanismo.

**Para el paper IEDD:** el SP-ADJ es un candidato a sección en el paper como extensión
del marco para proyectos que usan quality gates automatizados. La evidencia cuantitativa
(número de issues por SP, tiempo de resolución, impacto en métricas) se irá acumulando
en los BL-ADJ correspondientes.

---

## Qué NO es el SP-ADJ

- No es un "sprint de deuda" sin criterio de entrada — requiere revisión formal de cierre de SP
- No reemplaza el DoD de los SPs regulares — la deuda acumulada es señal de que el DoD
  de features fue suficiente pero no el único criterio de calidad
- No es obligatorio después de cada SP — solo cuando la revisión detecta deuda que
  degradaría el siguiente SP si se ignora
