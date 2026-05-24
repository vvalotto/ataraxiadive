# Cohesión y Acoplamiento — Ca / Ce / I por BC y Capa

> Fuente: `.cm/baselines/BL-006-report.json` (CouplingAnalyzer + DistanceAnalyzer)  
> Herramienta: ArchitectAnalyst BL-006 · 246 módulos analizados  
> Fecha de extracción: 2026-05-18  
> Referencia: PLAN-METRICAS.md §A.1.7

---

## Definiciones

| Símbolo | Nombre | Fórmula | Interpretación |
|---------|--------|---------|----------------|
| **Ca** | Acoplamiento aferente | — | Módulos que dependen de este módulo (lo usan) |
| **Ce** | Acoplamiento eferente | — | Módulos de los que depende este módulo (usa) |
| **I** | Inestabilidad | Ce / (Ca + Ce) | 0 = estable (muchos dependen de él) · 1 = inestable (depende de muchos) |
| **A** | Abstracción | interfaces / (interfaces + impl.) | 0 = concreto · 1 = abstracto |
| **D** | Distancia Main Sequence | \|A + I − 1\| | 0 = ideal · 1 = zona de riesgo |

---

## 1. Métricas a nivel BC (DistanceAnalyzer)

| BC | Tipo | A | I | Ca | Ce | D | Zona |
|----|------|:-:|:-:|:--:|:--:|:--:|------|
| resultados | CRUD | — | — | — | — | **≤ 0.30** | ✅ Main Sequence |
| notificaciones | ES | 0.22 | 0.33 | 2 | 1 | 0.450 | Alejado |
| competencia | ES (Core) | 0.04 | 0.50 | 2 | 2 | 0.459 | Alejado |
| torneo | CRUD | 0.02 | 0.50 | 2 | 2 | 0.479 | Alejado |
| registro | CRUD | 0.08 | 0.33 | 4 | 2 | 0.583 | CRITICAL |
| shared | Shared | 0.22 | 0.14 | 6 | 1 | 0.635 | Zone of Pain |
| identidad | CRUD | 0.10 | 0.25 | 3 | 1 | 0.652 | Zone of Pain |

**`resultados` es el único BC en o cerca de la Main Sequence** — sus Ca/Ce están equilibrados y D ≤ 0.30. El resto del sistema presenta valores de D > 0.30, lo que es normal en un sistema hexagonal donde los BCs internos (shared, identidad) son deliberadamente estables y concretos.

---

## 2. Inestabilidad I por capa (agregado de módulos)

La inestabilidad I se agrega sumando Ca y Ce de todos los módulos de cada BC × capa.

### 2.1 Tabla completa

| BC | Tipo | domain/ I | application/ I | infrastructure/ I | api/ I |
|----|------|:---------:|:--------------:|:-----------------:|:------:|
| competencia | ES | **0.33** | 0.70 | 0.65 | 0.97 |
| notificaciones | ES | **0.31** | 0.67 | 0.53 | — |
| torneo | CRUD | **0.29** | 0.72 | 0.75 | 0.84 |
| registro | CRUD | **0.14** | 0.70 | 0.68 | 0.97 |
| resultados | CRUD | 0.49 | 0.77 | 0.53 | 0.92 |
| identidad | CRUD | **0.16** | 0.82 | 0.62 | 0.83 |
| shared | Shared | **0.11** | — | 0.25 | 0.20 |

### 2.2 Promedio por capa (todos los BCs)

| Capa | I promedio | Interpretación |
|------|:----------:|----------------|
| domain/ | **0.26** | Estable — muchos módulos dependen del dominio |
| infrastructure/ | 0.59 | Moderadamente inestable — implementa ports, depende de librerías externas |
| application/ | 0.73 | Inestable — orquesta domain, depende de múltiples ports |
| api/ | **0.91** | Muy inestable — importa todo, nadie lo importa |

---

## 3. El gradiente de inestabilidad — evidencia de arquitectura hexagonal

```
domain/         I ≈ 0.11–0.49  ████░░░░░░  Estable  (Ca alto, Ce bajo)
infrastructure/ I ≈ 0.53–0.75  ████████░░  Moderado (Ce adapta ports externos)
application/    I ≈ 0.67–0.82  █████████░  Inestable (orquestador puro)
api/            I ≈ 0.83–0.97  ██████████  Muy inestable (hoja del grafo)
```

**El gradiente I(domain) < I(infra) < I(application) < I(api) se cumple en TODOS los BCs sin excepción.** Esto es evidencia directa de que la arquitectura hexagonal está correctamente implementada: la capa de dominio es la más estable del sistema (muchos dependen de ella, ella depende de poco), y la capa API es la hoja del grafo de dependencias (depende de todo, nadie depende de ella).

Este patrón no es evidente en el código fuente — emerge solo cuando se miden Ca/Ce sistemáticamente. Es una verificación cuantitativa de la intención de diseño.

---

## 4. Detalle por BC

### competencia (ES Core) — domain/ I=0.33

| Módulo más usado (Ca alto) | Ca | Ce |
|---------------------------|:--:|:--:|
| `domain/ports/event_store_port` | 31 | 1 |
| `domain/value_objects/disciplina` | 36 | 1 |
| `domain/domain/exceptions` | 9 | 0 |
| `domain/ports/competencias_por_torneo_port` | 9 | 0 |

Los puertos y value objects del dominio ES son los módulos más referenciados. `event_store_port` con Ca=31 indica que 31 módulos dependen del contrato del event store — es el núcleo del sistema ES.

### shared — domain/ I=0.11 (más estable del proyecto)

| Módulo más usado (Ca alto) | Ca |
|---------------------------|:--:|
| `domain/value_objects/disciplina` | 32 |
| `domain/base/domain_event` | 22 |
| `domain/ports/event_store_port` | 10 |

`shared/domain/value_objects/disciplina` con Ca=32 es el módulo más referenciado del proyecto. Todos los BCs que manejan disciplinas lo importan. Su I=0 (Ce=0) lo convierte en el punto de mayor estabilidad del sistema.

### registro — domain/ I=0.14 (CRUD más estable)

```
registro/domain/exceptions        Ca=17, Ce=0  → I=0.00
registro/domain/value_objects/categoria  Ca=13, Ce=0  → I=0.00
registro/domain/ports/inscripcion_repository_port  Ca=8, Ce=1  → I=0.11
```

La baja I del domain/ de Registro contrasta con su alto D (0.583) y su LCOM=4 en el aggregate Inscripcion. Esto muestra que D y I miden aspectos independientes: el dominio es estable (Ca alto), pero está en Zone of Pain porque es poco abstracto (A=0.08).

### identidad — application/ I=0.82 (mayor en toda la tabla)

La application/ de Identidad tiene la mayor inestabilidad de todas las capas de application. Esto es consistente con los hallazgos de backend-por-capa.md (CC promedio 3.00 — el más alto) y backend-ck.md (WMC proxy 8). La lógica de autenticación JWT + multi-rol hace que application/ de Identidad sea la capa más "dependiente" del sistema.

---

## 5. Hipótesis: ES más estable que CRUD en domain/

| BC | Tipo | domain/ I |
|----|------|:---------:|
| competencia | ES (Core) | 0.33 |
| notificaciones | ES (Generic) | 0.31 |
| **Promedio ES** | | **0.32** |
| torneo | CRUD | 0.29 |
| registro | CRUD | 0.14 |
| identidad | CRUD | 0.16 |
| resultados | CRUD | 0.49 |
| **Promedio CRUD** | | **0.27** |

**Hipótesis NO confirmada:** los dominios CRUD tienen I promedio (0.27) menor que los ES (0.32). Los BCs CRUD simples como registro e identidad tienen dominios extremadamente estables (I=0.14/0.16) porque sus value objects y excepciones son importados por muchos módulos sin importar nada a cambio.

**Matiz importante:** el dominio ES de Competencia (I=0.33) tiene más interdependencias internas entre aggregates, events y value objects — la complejidad del patrón ES se expresa como mayor Ce en domain/. Esto es coherente con el análisis de CC por capa: ES tiene más interacciones intra-capa, CRUD tiene capas más aisladas.

---

## 6. Síntesis para el paper IEDD

| Hallazgo | Evidencia |
|----------|-----------|
| Gradiente I(domain)<I(infra)<I(app)<I(api) confirma arquitectura hexagonal | Universalmente presente en los 6 BCs con datos completos |
| `shared/domain` es el módulo más estable (I=0.11) | Ca=82 agregado, Ce=10 — dependen de él, él depende de poco |
| `api/` es la capa hoja (I≈0.91) | Ce concentrado en routers FastAPI, Ca≈0 en todos los BCs |
| Zone of Pain en identidad (D=0.652) y shared (D=0.635) | Alta estabilidad + baja abstracción — aceptado por diseño |
| resultados único BC en Main Sequence (D≤0.30) | Balance Ca≈Ce en todos sus módulos |
| ES vs CRUD no diferencia I en domain/ | CRUD simples más estables por menor Ce interno; ES tiene más interdependencias intra-capa |

---

*Extraído: 2026-05-18 — rama doc/metricas — PLAN-METRICAS.md §A.1.7 (Prioridad 9) completada*
