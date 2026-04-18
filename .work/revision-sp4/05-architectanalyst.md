# Revisión de Calidad — Cierre SP4
## ArchitectAnalyst — BL-004

**Fecha:** 2026-04-16
**Comando:** `architectanalyst src/ --sprint-id BL-004 --format json`
**Resultado:** 6 CRITICAL · 56 WARNING · `should_block: false`
**Reporte guardado:** `quality/reports/architectanalyst/BL-004-pre-close.json`

---

## Resultado global

**`should_block: false`** — el cierre formal de BL-004 no está impedido.

---

## Comparación BL-003 → BL-004

| Métrica | BL-003 (post-ADJ) | BL-004 | Δ |
|---------|:-----------------:|:------:|:--:|
| Archivos analizados | 221 | 266 | +45 |
| CRITICAL | 4 | **6** | +2 |
| WARNING | 44 | 56 | +12 |
| should_block | false | false | = |

El incremento en warnings (+12) es proporcional al código nuevo: BC Notificaciones
y los nuevos handlers de exportación añaden módulos con alta instabilidad estructural
(esperado en capas internas de hexagonal). No hay degradación del código pre-existente.

Los dos CRITICAL nuevos son los hallazgos de interés.

---

## Análisis de CRITICAL

### CRITICAL pre-existentes (4 — heredados de BL-003, estables)

| BC | Analyzer | BL-003 | BL-004 | Tendencia |
|----|----------|:------:|:------:|:---------:|
| `competencia` | DistanceAnalyzer | D=0.616 | D=0.62 | → estable |
| `identidad` | DistanceAnalyzer | D=0.87 | D=0.87 | = sin cambio |
| `registro` | DistanceAnalyzer | D=0.563 | D=0.56 | ↓ leve mejora |
| `shared` | DistanceAnalyzer | D=0.611 | D=0.63 | ↑ leve degradación |

Los cuatro CRITICAL de DistanceAnalyzer son conocidos desde BL-003 y están
aceptados: representan BCs de zona CRUD (alta Ca, baja abstractness) cuya distancia
a la Main Sequence es estructuralmente alta por diseño, no por deuda técnica.
`competencia` persiste en D≈0.62 — no superó el umbral de 0.70 establecido en BL-003
como trigger de acción.

---

### CRITICAL nuevo 1 — `torneo`: DistanceAnalyzer D=0.64

`torneo` no era CRITICAL en BL-003. En BL-004 supera el umbral (D=0.64).

```
A=0.03, I=0.33 → D = |A + I - 1| = |0.03 + 0.33 - 1| = 0.64
```

El BC Torneo tiene muy poca abstractness (0.03 — casi sin interfaces/abstracciones)
e instabilidad moderada (I=0.33 — muchos módulos lo usan). El resultado es el mismo
patrón que `identidad` y `registro`: BC CRUD estable pero concreto.

**Causa:** torneo recibió extensión funcional en SP4 (INC-4.1 + nuevos endpoints).
Cada US nueva en un BC CRUD sube Ca sin subir A, moviendo el módulo hacia Zone of Pain.

**Evaluación:** mismo patrón que los otros BCs CRUD. No es degradación inesperada.
**Acción:** ninguna en SP5 — documentar como comportamiento esperado para BCs CRUD
en esta arquitectura.

---

### CRITICAL nuevo 2 — `competencia/domain/aggregates/performance`: ciclo ADP

```
competencia.domain.aggregates.performance
  → competencia.domain.aggregates.performance_state
    → competencia.domain.aggregates.performance   ← ciclo
```

**Severidad real:** media — el runtime no falla, pero el ciclo es arquitectónico.

**Análisis del ciclo:**

```python
# performance.py — import a nivel de módulo
from competencia.domain.aggregates import performance_state

# performance_state.py — lazy import DENTRO de función
def reconstituir_performance(events: list[...]) -> "Performance":
    ...
    from competencia.domain.aggregates.performance import Performance  # línea 33
    performance = Performance(...)
```

`performance_state.py` fue extraído de `performance.py` para separar la lógica de
replay de eventos del aggregate raíz. El módulo helper contiene las funciones
`apply_*` y `reconstituir_performance`. El problema: `reconstituir_performance`
necesita instanciar `Performance`, creando una dependencia de vuelta al módulo padre.

La solución actual usa dos mecanismos:
1. `TYPE_CHECKING` guard para las anotaciones de tipo — correcto, no genera ciclo real
2. Lazy import dentro del cuerpo de la función — el ciclo existe pero no explota al
   cargar el módulo

El ArchitectAnalyst detecta correctamente el ciclo porque existe a nivel de código,
aunque el runtime lo resuelve con el lazy import.

**Raíz del problema de diseño:**
`reconstituir_performance` es una función factory que crea instancias de `Performance`.
Una función factory del aggregate debería ser un `@classmethod` del aggregate, no
una función en un módulo helper que importa de vuelta al aggregate.

**Fix recomendado para SP-ADJ-06:**
Mover `reconstituir_performance` como `Performance.reconstituir(events)` classmethod.
`performance_state.py` quedaría solo con las funciones `apply_*` que reciben
`performance: Performance` — sin necesidad de instanciar, sin ciclo:

```python
# performance.py
@classmethod
def reconstituir(cls, events: list[dict]) -> "Performance":
    from competencia.domain.aggregates import performance_state
    # ... usa performance_state.apply_* pero no hay ciclo inverso
```

**Candidato SP-ADJ-06:** Sí — fix de diseño que elimina el CRITICAL.

---

## Análisis de warnings

Los 56 warnings son todos `InstabilityAnalyzer` con I > 0.8.

En una arquitectura hexagonal, la alta instabilidad en capas internas es estructural:
- `domain/` tiene I≈1.0 porque nadie importa de allí hacia afuera (solo hacia adentro)
- `application/` tiene I≈0.9-1.0 por el mismo motivo
- Los routers FastAPI tienen I≈0.9-1.0 porque son hojas del grafo de dependencias

Este patrón se repite desde BL-001. Los 56 warnings de BL-004 vs 44 de BL-003 reflejan
los 12 módulos nuevos de BC Notificaciones, todos con el mismo perfil de instabilidad.

**No hay señal nueva en los warnings.** Son ruido estructural conocido.

---

## Tendencias históricas

| Baseline | Archivos | CRITICAL | WARNING | Ciclos | should_block |
|----------|:--------:|:--------:|:-------:|:------:|:------------:|
| BL-001 (SP1) | ~80 | 0 | ~20 | 0 | false |
| BL-002 (SP2 post-ADJ) | ~150 | 0 | 28 | 0 | false |
| BL-003 (SP3 post-ADJ) | 221 | 4 | 44 | 0 | false |
| **BL-004 (SP4 pre-close)** | **266** | **6** | **56** | **1** | **false** |

La aparición de un ciclo ADP en BL-004 es la señal nueva más relevante.
En BL-001 a BL-003 no hubo ninguno. El ciclo se introdujo con la extracción de
`performance_state.py` (probablemente en SP-ADJ-03) y no fue detectado hasta ahora.

---

## Candidatos a SP-ADJ-06 desde este análisis

| ID | Módulo | Issue | Severidad |
|----|--------|-------|-----------|
| AA-01 | `competencia/domain/aggregates/performance_state.py` | Ciclo ADP — `reconstituir_performance` debería ser `@classmethod` de `Performance` | Alta |
| AA-02 | `torneo` | D=0.64 CRITICAL — aceptado como patrón CRUD; documentar umbral de acción | Info |

---

## Recomendación pre-BL-004

El `should_block: false` habilita el cierre. Sin embargo, antes de ejecutar el merge
`develop → main`, conviene investigar AA-01 y confirmar que el ciclo de dependencias
no es más amplio (en particular, verificar la relación entre `resultados/application/`
y `competencia/domain/` por el lazy import detectado en LAZY-01 del paso 04).

Si el lazy import en `exportar_resultados.py` crea un segundo ciclo cross-BC, eso sí
sería un bloqueante arquitectónico que debería resolverse antes del tag `v0.5.0`.

---

*Creado: 2026-04-16 — Revisión pre-BL-004*
