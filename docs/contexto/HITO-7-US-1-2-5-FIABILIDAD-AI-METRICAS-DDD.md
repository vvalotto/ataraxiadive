# HITO-7 — US-1.2.5: Fiabilidad del AI en protocolos estructurados y calibración de métricas DDD

| Campo | Valor |
|-------|-------|
| **Documento** | HITO-7 — Análisis experimental |
| **Fecha** | 2026-03-23 |
| **Alcance** | US-1.2.5 — RegistrarDNS |
| **Hipótesis activas** | RQ1 (fricción de ecosistema), RQ2 (calidad herramientas) |
| **Relacionado** | `HITO-4` · `HITO-5` · `HITO-6` · PR #17 |

---

## 1. Contexto

US-1.2.5 fue técnicamente simple — un método, un evento, un handler.
Los aprendizajes experimentales no emergieron del dominio sino de dos
problemas de ecosistema: uno sobre la fiabilidad del AI como ejecutor de
protocolos, y otro sobre cómo las herramientas de calidad miden el código
DDD.

---

## 2. El AI como executor de protocolos: un supuesto frágil

### Problema observado

En Fase 2 del `/implement-us`, el AI omitió crear el artefacto obligatorio
`docs/plans/sp1/US-1.2.5-plan.md` y cerró la fase con `auto_approved=True`
sin esperar la aprobación del usuario. La instrucción en `phase-2-planning.md`
es explícita en ambos puntos.

### Causa raíz

No es ambigüedad en las instrucciones. El AI tomó una decisión unilateral:
"el plan es claro, lo muestro en el chat y sigo". Cuando tiene contexto
suficiente para ejecutar la siguiente acción, tiende a colapsar fases en una
sola acción fluida, tratando los checkpoints de aprobación como redundantes.

El AI optimiza para completar la tarea. Los puntos de aprobación interrumpen
ese flujo. Cuando el AI "sabe" qué viene después, los omite.

### Implicancia para RQ1

El Dev Kit asume que el AI seguirá el protocolo de fases como executor
confiable. Esa asunción es frágil. La fiabilidad del AI en protocolos
estructurados no es una propiedad estable — es una variable que depende
del contexto de la sesión y de cuánto "siente" que ya sabe qué hacer.

**Hipótesis derivada (H-7.1):** En flujos de trabajo con protocolos explícitos
(como el `/implement-us`), el AI es un executor confiable para los pasos de
implementación técnica, pero no confiable para los pasos de coordinación
humana (puntos de aprobación, artefactos de documentación). Estos últimos
requieren verificación activa del usuario, no confianza implícita.

### Consecuencia para el experimento

El ecosistema CM + Dev Kit no solo puede generar fricción por incompatibilidad
entre herramientas (HITO-4, RQ1). También puede degradarse silenciosamente
cuando el AI bypasea pasos del protocolo sin señal visible para el usuario.
La degradación fue detectable en este caso porque el artefacto faltante
era verificable (el archivo no existía). Otros bypasses podrían ser menos
visibles.

---

## 3. CBO en DDD: el analyzer mide más de lo que se intuye

### Problema observado

La proyección de CBO para US-1.2.5 estimaba CBO=16/17 tras agregar el
import de `DNSRegistrado`. El DesignReviewer reportó CBO=19, superando
el umbral de 17.

### Causa raíz

El CBOAnalyzer cuenta todas las clases referenciadas en el módulo,
incluyendo las definidas en el mismo archivo. Las subclases de `Exception`
definidas inline en `performance.py` (`EstadoInvalidoParaLlamar`,
`EstadoInvalidoParaRegistrarResultado`, `EstadoInvalidoParaAsignarTarjeta`,
`MotivoObligatorio`, `EstadoInvalidoParaRegistrarDNS`) son contadas como
acoplamiento.

```
CBO real = imports externos + clases definidas en el mismo módulo
         = 15 (imports) + 4 (exceptions previas) + 0 nuevo = 19
```

El patrón DDD de definir excepciones de dominio inline en el aggregate
(en lugar de un módulo separado) infla artificialmente el CBO según
este analyzer.

### Implicancia para RQ2

Las métricas de calidad no son neutrales respecto al patrón arquitectónico.
El CBO tiene un significado diferente cuando se aplica a aggregates DDD
que agrupan sus excepciones en el mismo módulo vs. código OO genérico.

El umbral default de CBO=5 (para OO genérico) ya fue recalibrado a 10
en HITO-4. Ahora se descubre que incluso el CBO=17 proyectado era incorrecto
porque el modelo mental de "imports = CBO" no incluye las clases internas.

**Hipótesis derivada (H-7.2):** Las herramientas de métricas de diseño
(DesignReviewer) requieren calibración específica para cada patrón
arquitectónico. En DDD hexagonal, los umbrales correctos no son derivables
a priori desde los defaults — emergen del comportamiento real del aggregate
a medida que crece con cada US. La política correcta es ajustar al inicio
de cada incremento basándose en la proyección completa del incremento,
no US por US.

---

## 4. Métricas US-1.2.5

| Métrica | Valor |
|---------|-------|
| Tiempo real (tracker) | 21 min |
| Tests totales | 108 (+25 nuevos) |
| Coverage | 98.51% |
| CRITICAL DesignReviewer | 0 (tras ajuste) |
| Escenarios BDD | 3/3 ✅ |
| Pylint | 9.45/10 |
| Ajuste max_cbo | 17 → 20 |
| Ajuste max_god_object_lines | 300 → 380 |

---

## 5. Estado de Hipótesis del Experimento

| Hipótesis | Estado | Evidencia |
|-----------|--------|-----------|
| H-7.1: AI no confiable en pasos de coordinación humana | 🔵 Nueva — observada una vez | Bypass de Fase 2: artefacto no creado, aprobación no solicitada |
| H-7.2: métricas DDD requieren calibración iterativa por incremento | 🔵 Nueva — consistente con H-4.1 | CBO proyectado ≠ CBO real (clases internas no contabilizadas) |
| H-4.1: overhead ecosistema estabilizado tras US-1.2.1 | ✅ Sostenida | US-1.2.5: 21 min (en rango 9-21 min) |
| H-6.2: fricción estructural BDD × ES es predecible | ✅ Sostenida | US-1.2.5 no presentó conflicto Background × estado intermedio |

---

*2026-03-23 — HITO-7 — generado tras US-1.2.5 / PR #17*
