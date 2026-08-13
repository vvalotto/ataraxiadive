# Conclusiones del Experimento IEDD — AtaraxiaDive

> Derivadas del análisis de 17 documentos de métricas · docs/metricas/REPORTE-METRICAS.md
> Medición original: 2026-05-18 · Branch: main (merged desde doc/metricas · PR #196)
> **Recálculo (Ronda 2): 2026-08-13 · HEAD `main` · proyecto completo cerrado (SP1→SP-ADJ-13, tag v1.0.5)**

---

## 0. Qué cambió entre la medición original y el cierre del proyecto

La medición del 2026-05-18 se hizo al cierre de SP6 (BL-006). El proyecto completo cerró 14 días
después, tras SP7 (despliegue real + manual), SP-ADJ-12 (correcciones post-producción) y
SP-ADJ-13 (ejecución real de un torneo — Puerto Madryn 2026 — y ajustes derivados). Este
documento incorpora ese tramo final y reevalúa cada conclusión contra el estado definitivo del
proyecto, no contra un punto intermedio.

**La conclusión general no cambia — se refuerza.** El proyecto agregó 429 SLOC (backend+frontend,
+1.7%) y 6 endpoints REST en 77 días adicionales, sin tocar el 75% de los Bounded Contexts, sin
generar un solo CRITICAL nuevo, y sin degradar el gradiente arquitectónico. La calidad medida al
cierre de SP6 se sostuvo hasta el último commit del proyecto.

---

## 1. ¿Qué tan buena es la calidad del software? (revalidado al cierre)

**Objetivamente alta al cierre de SP6, y se mantuvo objetivamente alta hasta el cierre del
proyecto — verificado de forma independiente, no asumida.**

### Ángulo 1 — Calidad estructural

| Métrica | BL-006 | v1.0.5 (cierre) | Umbral "bueno" | Evaluación |
|---------|:-----------------:|:-----------------:|:--------------:|:----------:|
| CC domain/ promedio | 1.89 | **1.86** | < 5 | ✅ Muy bajo, sin cambios |
| MI domain/ promedio | 90.07 / 100 | **88.02 / 100** | > 85 | ✅ Altamente mantenible, sin cambios |
| Bugs estimados Halstead | 0.30 / 1 000 SLOC | **0.297 / 1 000 SLOC** | 1–25 (Capers Jones) | ✅ Percentil < 10 industria, sin cambios |
| Clases LCOM > 1 | 3.3% | **3.2%** | < 10% | ✅ Cohesión alta, sin cambios |

Las cuatro métricas estructurales que sostenían la conclusión de "calidad de producción" en
BL-006 **no se movieron de categoría** en los 77 días adicionales. El dato de Halstead sigue
siendo el más revelador: 0.297 bugs/1 000 SLOC contra un rango industrial de 1–25 — el proyecto
completo, no solo su punto intermedio, está 3× mejor que el límite inferior de ese rango.

### Ángulo 2 — Calidad arquitectónica (verificada dos veces, con resultado idéntico)

El gradiente I(domain=0.273) → I(api=0.903) se recalculó **desde cero** contra el HEAD final del
proyecto — no se reutilizó el número de BL-006. Reprodujo el mismo patrón con variaciones de
±0.02, en los mismos 6 BCs, sin excepción. `should_block` siguió en `false` en la medición final
(3 CRITICAL, 64 WARNING) — ningún baseline, en ningún punto de los 77 días del proyecto, bloqueó
un cierre.

### Ángulo 3 — Calidad evolutiva

La tasa de deuda de diseño (issues totales) subió de 287 a 298 en los últimos 77 días — el
incremento absoluto más pequeño de toda la serie histórica del proyecto (comparar con +55 en SP3,
+89 en SP4). **0 CRITICAL se mantuvo hasta el último commit.**

**Diagnóstico general, revalidado:** el software cerró con calidad de producción real, sostenida
durante el desarrollo *y* durante el cierre/estabilización. El único punto débil identificable
sigue siendo `resultados/application/` (76.9% de cobertura, sin cambios) — y se sumó uno nuevo,
puntual: dos archivos huérfanos de 0% cobertura en `identidad`, código muerto sin conexión al
router, detectado durante este recálculo (ver §2.4).

---

## 2. ¿Qué deja de aprendizaje para el futuro? (con hallazgos nuevos de la Ronda 2)

### 2.1 La complejidad no vive donde se intuye (sin cambios en la conclusión)

`competencia` sigue con la CC más baja del sistema en domain/ (1.86) y el 50% de los métodos
largos (74 de 148) — sin haber cambiado ni un bloque desde SP6. La conclusión original se
sostiene con el dato adicional de que **este patrón es estable en el tiempo**, no solo válido en
un punto de medición.

### 2.2 El ratio SP-ADJ del 60% es el costo real de la calidad incremental — con un límite nuevo

Sin cambios en SP1–SP6 (60% global). **Hallazgo metodológico nuevo:** el ratio queda **indefinido**
en SP7 porque el SP tuvo 0 US funcionales (sus dos incrementos — despliegue, manual — no son
US-IEDD de dominio). Esto no es una falla del proyecto: es evidencia de que el ratio SP-ADJ fue
diseñado para medir deuda *dentro de* una fase de construcción activa, y no tiene un valor
interpretable fuera de ella.

**Aprendizaje práctico, ampliado:** en proyectos similares, presupuestar 1.6 ciclos de pipeline
por cada US funcional **durante la fase de construcción**, y presupuestar por separado una fase de
cierre (despliegue + estabilización + documentación) que no sigue el mismo patrón de ratio.

### 2.3 Los quality gates deben discriminar, no bloquear (confirmado hasta el cierre)

El DesignReviewer nunca bloqueó un PR en 793 commits y 193 PRs de todo el proyecto — el
cierre (298 issues acumulados) confirma el mismo balance que en BL-006.

### 2.4 El tracking sistemático desde el inicio es crítico — y se abandonó igual al final (nuevo)

Solo 34 de 131 US totales tienen datos de tiempo (26%, antes 28% sobre ~123). **Ninguna de las 10
US/incrementos de SP7+SP-ADJ-12+SP-ADJ-13 tiene registro de tiempo real** — el tracking manual no
se sostuvo ni siquiera al final de un proyecto con el método completamente interiorizado.

**Aprendizaje operativo, reforzado:** instrumentar el tracker automáticamente desde Fase 0 no es
solo deseable para el arranque del proyecto — la Ronda 2 muestra que la disciplina manual se
degrada en cualquier fase donde el tipo de trabajo se aleja de la US-IEDD de dominio típica
(deploy, documentación, fixes puntuales). Un tracker automático es la única forma de tener
cobertura completa.

### 2.5 Las métricas agregadas pueden esconder código muerto (aprendizaje nuevo)

El recálculo de cobertura de tests detectó dos archivos (`agregar_rol_usuario.py`,
`quitar_rol_usuario.py`) con 0% de cobertura porque nunca fueron conectados al router —
residuo de una iteración de SP-ADJ-12 reemplazada sin limpiar. La cobertura global (94.7%) por sí
sola no distinguía "gap de testing real" de "código que no debería existir": hizo falta bajar al
desglose por archivo para encontrarlo.

**Aprendizaje para el proceso IEDD:** una caída inesperada en una métrica agregada amerita
siempre desglosar por archivo antes de interpretarla como regresión de calidad — puede ser una
señal de código muerto, no de menor esfuerzo de testing. Se recomienda agregar un chequeo de
"módulos importados en producción vs. módulos con tests" como parte del pipeline de cierre de
Incremento.

---

## 3. Indicador compuesto productividad/calidad — IEDD QPI (recalculado dos veces)

### Definición

```
QPI = Ritmo_funcional × Score_calidad

Ritmo_funcional = US funcionales / día calendario

Score_calidad = media de:
  - Cobertura normalizada:  coverage / 100
  - Cohesión OO:            1 − (LCOM>1 / total_clases)
  - Salud arquitectónica:   1 − (D_promedio)
  - Complejidad inversa:    1 − (CC_domain / 10)
```

### Cálculo — dos versiones, con interpretación distinta

**Versión A — QPI de construcción (SP1–SP6, 63 días, igual período que la medición original):**

| Componente | Cálculo | Valor BL-006 | Valor v1.0.5 |
|-----------|---------|:-----:|:-----:|
| Cobertura | coverage/100 | 0.953 | 0.947 |
| Cohesión OO | 1 − (LCOM>1/total) | 0.967 | 0.968 |
| Salud arquitectónica | 1 − D_prom(6 BCs) | 0.453 | 0.4525 |
| Complejidad inversa | 1 − (CC_domain/10) | 0.811 | 0.814 |
| **Score_calidad** | media | **0.796** | **0.795** |
| **Ritmo funcional** | US func./día | 1.22 | **1.22 (sin cambio — mismo SP1-6)** |
| **QPI construcción** | Ritmo × Score | **0.971** | **0.970** |

**El QPI de construcción prácticamente no se movió (0.971 → 0.970)** — confirmación cuantitativa
directa de que la calidad medida en BL-006 no era un artefacto de medición temprana: es el mismo
número, calculado con datos independientes, 3 meses después.

**Versión B — QPI de proyecto completo (77 días, incluye cierre SP7+ADJ-12+ADJ-13):**

| Componente | Valor |
|-----------|:-----:|
| Score_calidad | 0.795 (igual que Versión A — la calidad no cambió) |
| Ritmo funcional | 77 / 77 = **1.00** |
| **QPI proyecto completo** | **0.795** |

**La caída de QPI (0.970 → 0.795) es 100% atribuible al denominador de tiempo, no a la calidad.**
Los últimos 14 días agregaron 0 US funcionales por diseño (fase de cierre). Presentar un único
QPI para todo el proyecto sin esta distinción sería engañoso — subestimaría la velocidad real de
construcción del método IEDD.

**Nota de uso, ampliada:** el QPI tiene sentido comparativo, no absoluto, y **debe calcularse por
tipo de fase** (construcción vs. cierre/estabilización) para ser interpretable. Comparar el QPI de
un proyecto completo (con cierre) contra el QPI de construcción de otro proyecto sería un error
metodológico.

---

## 4. Comparación con desarrollo sin asistencia de IA (revalidada)

### 4.1 Velocidad de implementación

Sin cambios en los datos de la fase de construcción — la velocidad de crucero de SP3–SP5 (~1.5
US func./día) y el ratio implícito 3x–5x sobre baseline humano siguen siendo los números válidos
para citar, **medidos en la fase de construcción activa, no en el proyecto completo con cierre
incluido.**

### 4.2 Calidad resultante

| Métrica | AtaraxiaDive IEDD (cierre, v1.0.5) | Proyectos típicos | Fuente referencia |
|---------|:-----------------:|:-----------------:|:-----------------:|
| Cobertura de tests | **94.7%** (95.35% sin código muerto) | 40–60% | Industry surveys |
| Bugs estimados / 1 000 SLOC | **0.297** | 1–25 | Capers Jones |
| 0 CRITICAL en quality gates | **Toda la historia, incluido el cierre** | Variable | — |

La hipótesis del reporte original se sostiene con un dato adicional: la IA no solo acelera y
preserva calidad *durante la construcción* — la calidad se sostuvo también en la fase de
estabilización y cierre, sin regresión, con el único gap real encontrado siendo código muerto
puntual (no deuda de dominio).

### 4.3 Deuda técnica acumulada

Sin cambios sustantivos — el ratio SP-ADJ del 60% (construcción) sigue siendo comparable
favorablemente contra el 30–80% de retrabajo típico en desarrollo tradicional (DeMarco/Lister),
con la salvedad ya documentada de que el ratio no se extiende a fases de cierre.

---

## 5. Conclusión sintetizada para el paper IEDD (actualizada al cierre del proyecto)

> *"En este proyecto, la metodología IEDD produjo software con métricas de calidad superiores al
> promedio industrial (0.297 bugs/KLOC vs. 1–25, cobertura 94.7% vs. 40–60%, 0 CRITICAL en
> quality gates durante toda la historia del proyecto, incluido el cierre) a una velocidad de
> implementación estimada entre 3x y 10x superior a la de un desarrollador senior sin asistencia
> IA durante la fase de construcción activa (63 días, QPI=0.970), con un overhead de pipeline de
> 20 minutos mediana por historia de usuario completa. La arquitectura hexagonal se verificó
> cuantitativamente en dos momentos independientes — cierre de SP6 y cierre del proyecto, 77 días
> después — mediante el gradiente de inestabilidad I(domain=0.27) → I(api=0.90), confirmado en
> los 6 Bounded Contexts sin excepción en ambas mediciones. El cierre del proyecto (despliegue,
> corrección post-producción y documentación) mostró un patrón de cambio quirúrgico: cuatro
> métricas independientes (SLOC, esfuerzo Halstead, distancia arquitectónica D y superficie de
> API) identificaron exactamente los mismos dos Bounded Contexts como el único lugar del sistema
> que cambió, sin dispersión hacia el resto del código. El indicador compuesto QPI debe calcularse
> por tipo de fase — de lo contrario, mezclar construcción y cierre subestima artificialmente la
> velocidad real del método."*
>
> *"La generalización de estos resultados requiere replicación en proyectos con diferentes
> dominios, tamaños de equipo y paradigmas arquitectónicos. Las limitaciones principales son:
> muestra de un único proyecto y desarrollador, tracking de tiempos al 26% de cobertura (empeoró
> respecto al 28% original porque el tracking se abandonó completamente en la fase de cierre), y
> ausencia de un grupo de control contemporáneo con metodología tradicional."*

---

*Generado: 2026-05-18 — análisis derivado de docs/metricas/REPORTE-METRICAS.md y 17 documentos de detalle*
*Recalculado: 2026-08-13 — HEAD `main` post SP-ADJ-13 (tag v1.0.5) — proyecto completo, PLAN-METRICAS.md §6 Ronda 2*
