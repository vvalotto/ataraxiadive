# HITO-33 — LCOM como falso positivo estructural en aggregates Event Sourcing

| Campo | Valor |
|-------|-------|
| **Documento** | HITO-33 — Hallazgo de quality gate en SP6 |
| **Fecha** | 2026-05-10 |
| **Sprint** | SP6 — Validación, Ajustes y Despliegue · INC-6.4 |
| **Relacionado** | HITO-11 · HITO-7 · `RankingCompetencia` · DR-01 (BL-006) · DesignReviewer |

---

## Contexto

Durante INC-6.4 (Deuda Técnica Sistema), el análisis del reporte DesignReviewer sobre `RankingCompetencia` mostró LCOM=2 (Lack of Cohesion of Methods). La métrica indica que la clase tiene dos grupos de métodos sin acceso compartido a atributos de instancia — señal habitual de una clase que hace demasiado y debería dividirse.

El análisis reveló que el flag no era un defecto de diseño sino una consecuencia estructural del patrón **Aggregate con Event Sourcing**.

---

## El falso positivo

`RankingCompetencia` tiene dos grupos de métodos con responsabilidades distintas:

**Grupo 1 — Comando de dominio:**
- `calcular()` → emite eventos, actualiza `_entries` y `_calculado`

**Grupo 2 — Reconstitución Event Sourcing:**
- `reconstitute()`, `_apply_stored()`, `_rehidratar_resultados_calculados()`

LCOM=2 detecta correctamente que estos dos grupos no comparten acceso a los mismos atributos de instancia en su flujo principal. Pero la separación **es semánticamente necesaria e imposible de eliminar** en el patrón ES:

- `calcular()` produce eventos y escribe estado
- `reconstitute()` lee eventos del store y reconstruye el estado sin ejecutar lógica de negocio

Separar en dos clases haría que `reconstitute()` no pueda mutar el estado interno del aggregate, violando el patrón. Los helpers de cálculo (`_calcular_entries`, `_agrupar_por_categoria`, `_crear_entry_*`, etc.) ya estaban extraídos correctamente como funciones de módulo — fuera de la clase.

**Decisión registrada en DR-01 (BL-006):** LCOM=2 en aggregates ES es un **falso positivo documentado y aceptado**. El código no cambia.

---

## Generalización del hallazgo

El patrón se extiende a todos los aggregates con Event Sourcing del proyecto. Cualquier aggregate que implemente:
1. Métodos de comando (producen eventos, mutan estado)
2. Métodos de reconstitución (consumen eventos, reconstruyen estado)

...producirá inevitablemente LCOM≥2 en una métrica de cohesión OO clásica, porque los dos grupos operan sobre el aggregate en distintas fases de su ciclo de vida y no necesitan acceso simultáneo a los mismos campos.

La métrica fue diseñada para detectar clases que mezclan responsabilidades no relacionadas. En el caso de ES, las dos responsabilidades están relacionadas (son el mismo aggregate) pero son estructuralmente distintas por diseño.

---

## Relación con HITO-11 y HITO-7

HITO-11 documentó que una métrica automatizada (CBO elevado) derivó en una decisión de diseño no anticipada. HITO-7 cuestionó si CBO/WMC capturan calidad DDD.

HITO-33 agrega evidencia en la dirección contraria: **las métricas OO clásicas pueden producir señales de alerta que son estructuralmente necesarias en arquitecturas DDD+ES**, no defectos. La implicación para el experimento es doble:

1. Los quality gates automatizados necesitan un mecanismo de **clasificación de falsos positivos documentados** — no solo thresholds numéricos
2. La evaluación de calidad en un proyecto DDD+ES requiere conocimiento del dominio arquitectónico para distinguir deuda real de artefactos del patrón

---

## Pregunta experimental respondida

> ¿Las métricas de diseño OO producen falsos positivos sistemáticos en patrones DDD+ES?

**Evidencia:** Sí, al menos LCOM lo hace cuando el aggregate implementa el patrón Event Sourcing con reconstitución desde el event store. El falso positivo es predecible y reproducible — todo aggregate ES con reconstitución explícita producirá LCOM≥2.

**Implicación para IEDD:** El marco metodológico necesita incorporar una categoría de "falso positivo documentado" en los reportes de quality gate, análoga a un `noqa` semántico con justificación explícita. El registro en BL-006 (DR-01) es el primer ejemplo de este mecanismo operando.

---

## Resultado

- DR-01 cerrado como "ACL falso positivo de LCOM en aggregate ES — sin intervención"
- Patrón documentado en BL-006 como referencia para aggregates futuros
- DesignReviewer: 0 CRITICAL · 253 WARNING · `should_block=false`

---

*Creado: 2026-05-10 — SP6 INC-6.4 · decisión DR-01 BL-006*
*Mantenido por: Victor Valotto + Claude Cowork*
