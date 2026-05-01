# HITO-27 — Deriva Documental y Gates de Consistencia

**Fecha:** 2026-04-23
**SP:** SP5 — La Puesta en Marcha
**Incremento de referencia:** INC-5.2 (post-cierre)
**Autor:** Victor Valotto + Claude Code

---

## Observación

Al cerrar INC-5.2, se realizó un commit de reconciliación documental
(`docs: reconcile documentation consistency`) que tocó 17 archivos en
`docs/architecture/`, `docs/design/`, `docs/dominio/`, `docs/specs/`,
`docs/traceability/matrix.md` y `README.md`.

Ese volumen —17 archivos tras un único incremento cerrado correctamente—
es evidencia de **deriva documental acumulada**, no de un evento puntual.
La documentación arquitectural y de diseño se redacta en un momento y
queda desactualizada a medida que el código avanza US por US.

---

## Hipótesis

La deriva documental es una consecuencia estructural del proceso:
los quality gates actuales (CodeGuard, DesignReviewer, ArchitectAnalyst)
miden calidad del código y del diseño, pero **ninguno verifica coherencia
entre artefactos documentales**.

Sin un gate explícito, la consistencia documental se convierte en deuda
silenciosa que crece hasta que alguien la percibe y hace una reconciliación
manual de gran tamaño.

---

## Patrón establecido: dos niveles de gate

### Gate 1 — Trigger preciso: cierre de INC con ADR nuevo

**Cuándo:** al cerrar cualquier incremento que haya producido uno o más ADRs.

**Señal:** un ADR nuevo es la evidencia más precisa de una decisión
arquitectural que puede invalidar texto existente en otros artefactos.
Las áreas de impacto son predecibles y acotadas:

| Si el ADR toca... | Verificar coherencia en... |
|-------------------|---------------------------|
| Nuevo BC o integración | `docs/architecture/20-context-map-integrations.md`, `context-map.md` |
| Decisión de persistencia | `docs/architecture/10-bc-*.md`, `domain-model.md` |
| Decisión de stack/infra | `README.md`, `docs/design/architecture.md` |
| Lenguaje ubicuo / términos | `CLAUDE.md §8`, `event-storming-*.md` |
| Nuevo patrón de runtime | `docs/architecture/30-runtime-interactions.md` |

**Costo:** ~15 min por ocurrencia. Scope acotado por el ADR.

**No aplica** a incrementos sin ADRs nuevos (ej: US de frontend puro,
refactoring interno sin decisión arquitectural nueva).

### Gate 2 — Cadencia mínima: SP-ADJ pre-baseline

**Cuándo:** en el SP-ADJ que precede al cierre de cada Baseline.

**Qué incluye:** barrido completo de todos los artefactos contra el
estado actual del código y los ADRs del SP. Checklist:

- `docs/architecture/` alineada con la estructura real de `src/`
- `docs/design/` refleja decisiones del período
- `CLAUDE.md §14` actualizado con el estado del SP
- `docs/traceability/matrix.md` sin US sin cerrar
- `README.md` apuntando a los documentos correctos
- `docs/dominio/` sin referencias a conceptos renombrados o eliminados

**Costo:** 30–60 min si el Gate 1 funcionó bien durante el SP.

---

## Relación con el experimento IEDD

Este patrón confirma una tensión inherente a IEDD + desarrollo incremental:
la Capa 2 (Modelo DDD) y la Capa 4 (Arquitectura) se documentan al inicio
de un SP pero el código de la Capa 5 (Implementación) las modifica
incremento a incremento. Sin gates explícitos de sincronización,
la documentación se desacopla del código que supuestamente describe.

Los dos gates descritos son la respuesta operativa a esa tensión.
No eliminan la deriva —que es inevitable en desarrollo iterativo—
sino que la controlan con puntos de reconvergencia predecibles.

---

## Impacto en el proceso

Formalizado en `docs/plans/WORKFLOW-DESARROLLO.md` v1.6:
- §6 Cierre de Incremento: paso condicional de consistencia documental si hay ADRs nuevos
- §7 Ciclo por SP: SP-ADJ incluye barrido documental como paso explícito
- §8 Quality Gates: nueva fila "Consistencia documental" en dos niveles
