# Análisis de Aggregates — Cierre SP3

**Fecha:** 2026-04-02
**Alcance:** aggregates nuevos de SP3 + estado de aggregates pre-existentes

---

## WMC real por aggregate (conteo de métodos via AST)

| Aggregate | BC | WMC | LongMethod (DR) | Tendencia vs SP2 |
|-----------|-----|-----|-----------------|-----------------|
| Competencia | competencia | 25 | ×7 (30–127 líneas) | Estable (SP2: 25 aprox) |
| Performance | competencia | 26 | ×8 (28–54 líneas) | Estable |
| RankingCompetencia | resultados | 13 | ×2 | Estable |
| RankingOverall | resultados | 15 | ×2 (27–32 líneas) | Nuevo SP3 |
| Torneo | torneo | 12 | — | Nuevo SP3 |

> Nota: el WMC de DesignReviewer (umbral=65) usa cyclomatic complexity ponderada.
> El WMC aquí es conteo de métodos (proxy). Competencia tiene threshold=65 de WMC ponderado,
> que no fue excedido — el 0 CRITICAL lo confirma.

---

## Competencia (Core Domain)

**Estado:** estable post-SP3. `torneo_id` fue agregado en INC-3.3 (US-3.3.1) sin degradación.

**Issues conocidos (pre-existentes, candidatos SP-ADJ-03):**
- `ajustar_grilla()`: 127 líneas — candidato a extracción de `GrillaDeSalida` VO (US-ADJ-3.1)
- Métodos `_apply_*` en general: verbosidad aceptable para Event Sourcing

**Acción sugerida:** US-ADJ-3.1 (GrillaDeSalida) es el refactor prioritario. WMC actual en límite del umbral.

---

## Performance (Core Domain)

**Estado:** estable. Múltiples LongMethod son artefactos del patrón `_apply_evento()` en ES.

**Issues conocidos:**
- 8 métodos con LongMethod — no hay uno que domine como en `ajustar_grilla`
- `registrar_ap`, `asignar_tarjeta`, `registrar_resultado` — lógica de validación compleja

**Acción sugerida:** sin urgencia. Candidato SP4 si el aggregate crece.

---

## RankingOverall (nuevo en SP3)

**Estado:** nuevo aggregate implementado en US-3.5.1. WMC=15, 2 LongMethod.

**Observaciones:**
- Método `calcular` (27 líneas) contiene la fórmula posicional completa — cohesivo aunque largo
- Módulo `ranking_overall.py` tiene función auxiliar de 32 líneas — candidato a refactor menor

**Acción sugerida:** sin urgencia. Aggregate simple y bien delimitado.

---

## Torneo (nuevo en SP3)

**Estado:** nuevo aggregate CRUD implementado en SP3. WMC=12, LCOM=3/1.

**LCOM=3 — análisis:**
LCOM alto en un aggregate CRUD indica que los métodos no comparten campos.
En el caso de Torneo, los tres grupos son: (1) ciclo de vida del torneo, (2) gestión de disciplinas, (3) asignación de jueces.
Esto es coherente con el dominio — Torneo es un aggregate con múltiples responsabilidades legítimas.

**Acción sugerida:** aceptar. Si LCOM sube en SP4 (cuando Torneo pueda agregar Sede, EntidadOrganizadora), reconsiderar extracción.

---

## RankingCompetencia (pre-existente SP2)

**Estado:** estable. Sin cambios en SP3. Issues pre-existentes (LCOM=2/1, LongMethod) sin agravamiento.
