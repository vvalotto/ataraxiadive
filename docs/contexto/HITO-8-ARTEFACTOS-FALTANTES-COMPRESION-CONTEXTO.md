# HITO-8 — Artefactos faltantes: degradación silenciosa por compresión de contexto

| Campo | Valor |
|-------|-------|
| **Documento** | HITO-8 — Análisis experimental |
| **Fecha** | 2026-03-23 |
| **Alcance** | US-1.2.4 · US-1.2.5 · US-1.2.6 · US-1.3.1 (revisión post-implementación) |
| **Hipótesis activas** | RQ1 (fricción de ecosistema), RQ2 (fiabilidad AI en protocolos) |
| **Relacionado** | `HITO-7` (H-7.1) · Issue #43 claude-dev-kit |

---

## 1. Hallazgo

Al revisar la estructura de documentación post-Inc 1.3, se detectaron artefactos
de calidad y reporte faltantes que el skill `/implement-us` debía haber generado:

| Artefacto | Faltantes |
|-----------|-----------|
| `docs/reports/{US_ID}-report.md` | US-1.2.4, US-1.2.5, US-1.2.6 |
| `quality/reports/codeguard/{US_ID}-quality.json` | US-1.2.5, US-1.2.6, US-1.3.1 |
| `quality/reports/designreviewer/` | US-1.2.3 a US-1.3.1 (casi todos) |

Los artefactos faltantes corresponden sistemáticamente a fases de **salida**
(Fase 7 — Quality Gates, Fase 9 — Reporte Final), no a fases de implementación.

---

## 2. Causa raíz

**Compresión de contexto + fases de salida sin gate mecánico.**

Cada US implementada agregaba ~2000 líneas al contexto de la sesión.
A partir de US-1.2.4, el contexto era suficientemente largo para que el
sistema comprimiera conversación previa. Bajo esa presión:

1. El AI ejecutaba los comandos (`codeguard`, `designreviewer`) y mostraba
   los resultados en el chat.
2. Omitía el paso de **persistir el artefacto** (escribir el archivo).
3. Continuaba con la siguiente fase sin señal de error, porque estas fases
   no tienen un gate de verificación: no hay tests que fallen, no hay un
   `assert os.path.exists(output_file)`.

El patrón es idéntico al observado en HITO-7 (H-7.1): el AI tiende a
"completar conceptualmente" una fase cuando tiene contexto suficiente para
saber qué viene después, y trata los pasos de materialización de artefactos
como overhead redundante.

**La diferencia respecto a HITO-7:** allí el artefacto faltante era un plan
(Fase 2), detectable porque el usuario revisaba ese output. Aquí los artefactos
son reportes de cierre (Fases 7 y 9), que nadie revisa en tiempo real — la
degradación fue **silenciosa durante 4 US consecutivas**.

---

## 3. Implicancias para el experimento

### Sobre RQ1 — Fricción del ecosistema

El problema no es incompatibilidad entre herramientas. Es que el protocolo
de `/implement-us` tiene **fases con verificación activa** (tests que pasan o
fallan) y **fases con verificación pasiva** (artefactos que se esperan pero
no se comprueban). Las fases pasivas son el punto débil del ecosistema bajo
presión de contexto.

### Sobre la fiabilidad del AI como executor

H-7.1 se refería a pasos de coordinación humana (puntos de aprobación).
Este hallazgo extiende la hipótesis: **también son frágiles los pasos de
materialización de artefactos de salida** cuando no hay verificación mecánica.

**Hipótesis derivada (H-8.1):** En protocolos multi-fase ejecutados por un AI,
la fiabilidad de producción de artefactos es inversamente proporcional a:
(a) la distancia temporal entre la acción y la verificación, y
(b) el nivel de compresión de contexto activo en la sesión.
Las fases de cierre (documentación, reportes) son estructuralmente más
vulnerables que las fases de apertura (implementación, tests).

### Consecuencia para el diseño del skill

Un skill de implementación que no verifica la existencia de sus propios
artefactos de salida no puede garantizar trazabilidad completa. La trazabilidad
del experimento (RQ3 — capitalización de conocimiento) depende de que estos
artefactos existan.

---

## 4. Solución propuesta

Agregar al final de Fase 7 y Fase 9 una verificación explícita de existencia
de artefactos antes de declarar la fase completada:

```markdown
## Gate de cierre (OBLIGATORIO antes de continuar)

Verificar que los siguientes archivos existen en disco:
- [ ] `quality/reports/codeguard/{US_ID}-quality.json`
- [ ] `docs/reports/{US_ID}-report.md`

Si alguno falta → crearlo antes de continuar.
Nunca declarar la fase completa si el artefacto no está en disco.
```

Issue abierto en claude-dev-kit: **#43**

---

## 5. Estado de hipótesis

| Hipótesis | Estado | Evidencia |
|-----------|--------|-----------|
| H-8.1: artefactos de salida son más frágiles bajo compresión | 🔵 Nueva — observada en 4 US consecutivas | Fases 7/9 omitidas sistemáticamente desde US-1.2.4 |
| H-7.1: AI no confiable en pasos de coordinación humana | 🟡 Ampliada | Se extiende a materialización de artefactos de salida |
| RQ3 — capitalización de conocimiento | ⚠️ En riesgo | Sin artefactos completos, la trazabilidad del experimento tiene huecos |

---

*2026-03-23 — HITO-8 — generado tras revisión post-Inc 1.3*
