# US-4.1.7: Simplificar `GrillaDeSalida` y `RankingCompetencia`

**Estado**: `To Do`
**Sprint**: SP4 — La Plataforma
**Incremento**: INC-4.1
**Bounded Context**: `competencia`, `resultados`
**Capas afectadas**: `competencia/domain/`, `resultados/domain/`, `resultados/infrastructure/`

---

## Descripción

Como **desarrollador del Core Domain**,
quiero **partir la lógica de ajuste de grilla y simplificar el aggregate de ranking**
para **que métodos largos con múltiples responsabilidades sean reemplazados por
colaboradores cohesivos y fáciles de testear de forma aislada**.

---

## Contexto del dominio

### Modelo involucrado

| Elemento DDD | Nombre | Responsabilidad actual (problema) |
|---|---|---|
| Aggregate (sobrecargado) | `GrillaDeSalida` | `ajustar()` concentra múltiples criterios de ajuste de orden (AP, andarivel, DNS) en un método largo |
| Aggregate (sobrecargado) | `RankingCompetencia` | Cálculo de posición, empate, podio y validación de estado mezclados |
| Adaptador (sobrecargado) | `ResultadosCompetenciaAdapter` | Responsabilidades de transformación de datos + consultas SQL expandidas |

### Lenguaje ubicuo relevante

- **Ajuste de grilla:** modificación del orden de salida de atletas respetando reglas reglamentarias (DNS, cambio de AP, conflicto de andarivel)
- **Empate en ranking:** dos atletas con igual RP — el reglamento define el criterio de desempate (AP mayor gana)
- **Podio:** posiciones 1°, 2°, 3° del ranking final de la disciplina

---

## Especificación del comportamiento

### Invariantes de refactoring

- **INV-R-01:** ningún test unitario ni de integración existente puede fallar tras el refactoring.
- **INV-R-02:** el orden de salida generado por `GrillaDeSalida.ajustar()` es idéntico antes y después del refactoring para cualquier combinación de entradas.
- **INV-R-03:** el ranking calculado por `RankingCompetencia` es idéntico antes y después del refactoring.
- **INV-R-04:** los warnings LongMethod de los métodos afectados deben reducirse en el DesignReviewer.

### Operación principal

**Nombre**: `refactoring de métodos largos en GrillaDeSalida y RankingCompetencia`

| | Descripción |
|---|---|
| **Precondición** | `GrillaDeSalida.ajustar()` tiene múltiples responsabilidades inline; `RankingCompetencia` mezcla cálculo con validación |
| **Postcondición** | `ajustar()` delega en submétodos por criterio; `RankingCompetencia` separa cálculo de posición de validación de estado |
| **Eventos generados** | (ninguno — refactoring puro) |
| **Excepciones** | (sin cambio) |

**Ejemplo concreto:**

```
Precondición:  GrillaDeSalida.ajustar() maneja DNS + cambio de AP + conflicto de andarivel en 80+ líneas
Operación:     extraer _reordenar_por_ap(), _gestionar_dns(), _resolver_conflictos_andarivel()
Postcondición: ajustar() orquesta los tres submétodos; cada uno es testeable de forma aislada
Verificación:  DesignReviewer no reporta LongMethod para ajustar()
```

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-4.1.7 — GrillaDeSalida y RankingCompetencia sin LongMethod

  Background:
    Given GrillaDeSalida y RankingCompetencia implementan sus invariantes actuales

  Scenario: el orden de grilla se preserva para una grilla con DNS y cambio de AP
    Given una grilla con un atleta DNS y otro que bajó su AP
    When se ejecuta ajustar() tras el refactoring
    Then el orden resultante es idéntico al orden anterior al refactoring

  Scenario: el ranking con empate se resuelve igual que antes
    Given dos atletas con RP idéntico
    When se calcula el ranking
    Then el atleta con AP mayor ocupa la posición superior
    And el resultado es idéntico al calculado antes del refactoring

  Scenario: todos los tests de grilla y ranking pasan sin modificación
    Given el refactoring está completo
    When se ejecutan los tests de GrillaDeSalida y RankingCompetencia
    Then todos los tests pasan sin cambios en los test files
```

---

## Impacto arquitectónico

**¿Esta US requiere una decisión arquitectónica?**
- [x] No — se implementa con la arquitectura existente

**Capa(s) afectadas:**
- [x] Domain (`competencia/domain/aggregates/grilla_de_salida.py`, `resultados/domain/aggregates/ranking_competencia.py`)
- [x] Infrastructure (`resultados/infrastructure/adapters/resultados_competencia_adapter.py`)

---

## Referencias

- HITO: `docs/contexto/HITO-19-INC-4-1-HALLAZGOS-DISENO-CIERRE.md §AJ-INC-4.1.3`

---

## Notas de implementación

- Leer `GrillaDeSalida.ajustar()` completo antes de decidir la estrategia de extracción.
- Los submétodos extraídos son métodos privados del mismo aggregate — no servicios de dominio independientes, a menos que la lógica sea reutilizable entre BCs.
- `ResultadosCompetenciaAdapter`: revisar si las queries SQL se pueden encapsular en métodos privados con nombres descriptivos; no reescribir la lógica de acceso a datos, solo reorganizar la estructura del adaptador.

---

*Redactado: 2026-04-08 — INC-4.1 ajustes DesignReviewer (HITO-19)*
