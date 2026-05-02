# ArchitectAnalyst — BL-002

**Fecha:** 2026-03-28
**Comando:** `architectanalyst src/ --sprint-id BL-002 --format json`
**Resultado:** 0 CRITICAL · 26 WARNINGS · should_block: false
**Todos los trends:** = (estable) — sin degradación respecto a BL-001

---

## Warnings — Dos tipos

### Tipo 1: InstabilityAnalyzer (23 warnings) — Falso positivo sistemático

Todos los módulos de commands, queries, adapters, domain/events, domain/value_objects
muestran I > 0.8.

Fórmula: `I = Ce / (Ca + Ce)` — alta cuando un módulo depende de muchos otros y pocos
dependen de él.

En CQRS/ES, los handlers y adapters son hojas del grafo de dependencias: dependen de
ports, aggregates y VOs, pero nada depende de ellos directamente. I=1.0 es el valor
esperado y correcto para estas clases.

Módulos con mayor Ce (más dependencias):
- `competencia/api/router`: Ce=19, I=0.95
- `competencia/domain/events`: Ce=8, I=1.00
- `competencia/domain/value_objects`: Ce=8, I=1.00

Nota: `competencia/domain/aggregates` con I=1.00, Ca=0 — el analyzer mide el paquete
como unidad, no los archivos individuales. Los aggregates tienen alta Ca real (muchos
handlers los importan), pero a nivel de paquete __init__ Ca=0.

**Veredicto: falso positivo. No requiere acción.**

### Tipo 2: DistanceAnalyzer (3 warnings) — Señal genuina

| Paquete | A (abstractness) | I (instability) | D (distancia) | Zona |
|---|---|---|---|---|
| `competencia` | 0.05 | 0.50 | 0.45 | Zona del dolor |
| `resultados` | 0.07 | 0.50 | 0.43 | Zona del dolor |
| `shared` | 0.50 | 0.00 | 0.50 | Zona del dolor |

D = |A + I - 1|. Main Sequence: A+I=1 (D=0).
Un paquete debe ser: abstracto+estable (A≈1, I≈0) O concreto+inestable (A≈0, I≈1).
Los tres BCs caen en zona intermedia.

**`competencia` y `resultados` (A≈0.05):**
Casi sin abstracciones visibles a nivel de paquete. Los ports (las abstracciones)
viven dentro del BC en `domain/ports/`, pero el analyzer mide el paquete BC completo.
La arquitectura hexagonal crea una lectura mixta: el paquete tiene layers muy abstractas
(ports) y muy concretas (infrastructure), promediando en zona intermedia.

**`shared` (I=0.00, A=0.50):**
Muy estable (nada fluye hacia afuera) pero solo mitad abstracto.
Contiene tanto `AggregateRoot` (clase base concreta) como algunos tipos abstractos.
En la Main Sequence, I=0 debería ir con A≈1 — `shared` es demasiado concreto
para su nivel de estabilidad.

---

## Sin coverage, sin dependency violations

- `CoverageAnalyzer`: sin resultados — requiere configuración de path adicional
- `DependencyRuleAnalyzer`: 0 violations — consistente con DesignReviewer
  (las violaciones son de diseño interno, no de fronteras entre BCs)

---

## Hallazgos para el Experimento

### H-P — InstabilityAnalyzer I>0.8 es falso positivo universal en CQRS/ES
El umbral de inestabilidad no está calibrado para arquitecturas de handlers/adapters.
En proyectos IEDD con CQRS, los 23 warnings de instabilidad son ruido puro.
Igual que FeatureEnvy y CBO, es una métrica diseñada para OOP clásico que no
sobrevive el contacto con patrones DDD/CQRS.

### H-Q — DistanceAnalyzer no ve la arquitectura hexagonal por capas
Los BCs muestran D≈0.45 porque el analyzer promedia ports (abstractos) e infrastructure
(concretos) en un solo número de abstractness. La arquitectura hexagonal tiene sentido
por capas — medirla por paquete BC completo aplana información valiosa.
Implicancia: el metric correcto sería DistanceAnalyzer aplicado por capa (domain/ports,
domain/aggregates, infrastructure/) en lugar de por BC completo.

### H-R — Todos los trends estables: SP2 no degradó la arquitectura
La señal más valiosa del architectanalyst no es ningún warning individual sino
que todos los trends son "=" — SP2 agregó 2 BCs nuevos (resultados) y varias USs
sin empeorar las métricas de acoplamiento, abstracción ni distancia respecto a BL-001.
Eso valida que el proceso IEDD + Dev Kit mantuvo la coherencia arquitectural
al escalar el proyecto.
