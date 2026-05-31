---
title: "Resultados — AlgoritmoPuntajeFAAS"
type: arquitectura-componente
bc: resultados
capa: domain
tipo_componente: service
responsabilidad: "Implementa el reglamento FAAS para calcular puntos por disciplina — 3 fórmulas según tipo (distancia, tiempo STA, tiempo SPE)"
interfaces_out: []
adr_refs: [ADR-014]
last_updated: "2026-05-23"
sources:
  - src/resultados/domain/services/algoritmo_faas.py
  - src/resultados/domain/ports/algoritmo_puntaje.py
us_origen:
  - US-5.6.1-puerto-algoritmo-puntaje-implementacion-faas
  - US-6.4.4-refactoring-algoritmo-puntaje-faas-correcciones-code
tests:
  - tests/features/US-5.6.1-algoritmo-puntaje-faas.feature
  - tests/features/US-6.4.4-refactor-faas-codeguard.feature
---

# AlgoritmoPuntajeFAAS — Servicio de Dominio

## Puerto: AlgoritmoPuntaje (ABC)

```python
class AlgoritmoPuntaje(ABC):
    def calcular(
        self,
        resultados: list[ResultadoFinal],
        disciplina: Disciplina,
    ) -> dict[UUID, Decimal]: ...
```

Retorna un mapa `atleta_id → puntos`.

---

## Implementación: AlgoritmoPuntajeFAAS

Tres fórmulas según el tipo de disciplina:

### Distancia (DNF, DYN, DBF, …)

```
P_i = (d_i / d_max) × 100
```

- `d_max` = mayor RP entre atletas con tarjeta válida en la misma categoría
- DNS y roja → 0 puntos; excluidos del cálculo de `d_max`

### Tiempo resistencia (STA)

```
P_i = (t_i - t_min) / (t_max - t_min) × 100
```

- Mayor tiempo = mejor: `t_max → 100 pts`, `t_min → 0 pts`

### Tiempo velocidad (SPE_*)

```
P_i = (t_max - t_i) / (t_max - t_min) × 100
```

- Menor tiempo = mejor: `t_min → 100 pts`, `t_max → 0 pts`
- Caso borde `t_max == t_min`: todos reciben 100 pts

### Redondeo

Todos los puntos se redondean a 2 decimales con `ROUND_HALF_UP`.

### Agrupamiento por categoría

El cálculo se realiza **independientemente por categoría**. `d_max` / `t_min` / `t_max` se calculan solo entre los atletas de la misma categoría.

---

## Dispatch

```python
def calcular(self, resultados, disciplina):
    if disciplina.es_tiempo():
        return _calcular_tiempo(..., mayor_es_mejor=disciplina.tiempo_mayor_es_mejor())
    return _calcular_distancia(resultados)
```

`disciplina.es_tiempo()` y `disciplina.tiempo_mayor_es_mejor()` son métodos del VO `Disciplina` en `shared/`.

---

## Relaciones

**Contenedor:** [[arquitectura/resultados]]

- Implementa `AlgoritmoPuntaje` de `domain/ports/`
- Inyectado en [[command-handlers-resultados]] (CalcularRankingHandler) via el router
- Consumido por [[ranking-competencia]] en el método `calcular(resultados, algoritmo)`
- La disciplina `STA` usa `mayor_es_mejor=True`; `SPE_*` usa `mayor_es_mejor=False`

## Código fuente

| Archivo | Descripción |
|---|---|
| `src/resultados/domain/services/algoritmo_faas.py` | Servicio FAAS — 3 fórmulas de puntuación por tipo de disciplina |
| `src/resultados/domain/ports/algoritmo_puntaje.py` | Puerto abstracto AlgoritmoPuntaje |
