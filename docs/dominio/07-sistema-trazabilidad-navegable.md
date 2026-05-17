# Sistema de Trazabilidad Navegable

> **Tipo**: Documento de diseño — entrada a plan de implementación
> **Estado**: Borrador conceptual — diseño completo, pendiente de piloto
> **Fecha**: 2026-05-17
> **Contexto**: Conversación de diseño Victor Valotto + Claude (Cowork)

---

## 1. El problema

AtaraxiaDive acumula una masa creciente de artefactos documentales: planes de US,
ADRs, especificaciones IEDD, notas de implementación, archivos fuente, tests de
aceptación. Todos existen. Muchos se referencian entre sí. Pero las relaciones son
**implícitas y textuales** — un humano las infiere leyendo, un agente las pierde o
las alucina.

El problema tiene dos dimensiones:

**Para el humano**: navegar desde un archivo de código hacia la decisión arquitectónica
que justifica su forma requiere seguir cadenas de texto prosa dispersas en múltiples
directorios. El tiempo de orientación es alto. El conocimiento está enterrado.

**Para el agente**: sin relaciones explícitas y tipadas, no puede responder preguntas
como "¿qué restricciones debo respetar antes de tocar este archivo?" o "¿qué puede
romperse si modifico este componente?" con precisión. O lee todo (costoso e inexacto)
o actúa con contexto incompleto.

El sistema propuesto resuelve ambas dimensiones desde un modelo unificado.

---

## 2. Principios de diseño

El sistema se apoya en tres ideas conceptuales que convergen:

### 2.1 Trazabilidad como grafo navegable

La trazabilidad clásica es una matriz — una tabla que relaciona requisitos con pruebas,
o decisiones con código. Útil para auditorías, rígida para la exploración. Este sistema
la reemplaza por un **grafo dirigido de artefactos** donde los nodos son los artefactos
reales del proyecto (documentos MD, archivos fuente, tests) y las aristas son relaciones
tipadas y explícitas entre ellos.

La diferencia no es cosmética. Un grafo permite preguntas que una matriz no puede
responder: ¿qué artefactos son alcanzables desde este nodo siguiendo estas relaciones?
¿Cuáles son los backlinks de este artefacto — quién lo referencia? ¿Cuál es la
profundidad de impacto de un cambio?

### 2.2 Vistas de arquitectura

El concepto de vistas de arquitectura (IEEE 42010, modelo 4+1 de Kruchten, C4) establece
que un sistema complejo no puede describirse con una sola representación. Distintos
stakeholders necesitan distintas proyecciones del mismo modelo subyacente.

Este principio se traslada aquí a la documentación misma. El grafo de artefactos es
**único**. Las vistas son **proyecciones nombradas** sobre ese grafo, definidas por el
propósito del navegante. El mismo nodo `ADR-007` es central en una vista arquitectónica,
periférico en una vista de desarrollador, e irrelevante en una vista de cierre de sprint.

### 2.3 Navegación por propósito (segundo cerebro de Karpathy)

Andrej Karpathy usa Obsidian como segundo cerebro: notas enlazadas que forman un grafo
navegable donde el recorrido emerge del interés del momento, no de una jerarquía impuesta.
El valor está en los backlinks — saber qué te referencia es tan valioso como saber qué
referencías.

La diferencia con nuestro sistema es que las vistas tienen **propósito explícito y
nombrado**. No es "explorá el grafo"; es "activá la vista `pre-implementar` sobre esta
US". El propósito guía la navegación tanto para el humano (sabe por dónde entrar) como
para el agente (sabe qué recorrer y por qué).

---

## 3. El modelo en tres capas

```
┌─────────────────────────────────────────────────────────┐
│  CAPA 3: TRACE-INDEX.json                               │
│  Grafo derivado · bidireccional · consumible por agente │
└───────────────────────┬─────────────────────────────────┘
                        │  generado desde
            ┌───────────┴──────────────┐
            ▼                          ▼
┌───────────────────┐    ┌─────────────────────────────┐
│  CAPA 1           │    │  CAPA 2                     │
│  Frontmatter YAML │    │  Anotaciones en código      │
│  en archivos .md  │    │  # @implements US-X.Y.Z     │
│  (agente declara) │    │  (agente declara)           │
└───────────────────┘    └─────────────────────────────┘
            +
┌───────────────────────────────────────────────────────┐
│  ANÁLISIS ESTÁTICO (script derivado)                  │
│  imports Python/TypeScript → dependencias técnicas    │
└───────────────────────────────────────────────────────┘
```

Las capas 1 y 2 son **fuentes de verdad** — declaradas por el agente al crear o modificar
artefactos. La capa 3 es **derivada** — generada por un script, nunca editada a mano.

### 3.1 Frontmatter YAML en documentos MD

Cada artefacto documental (.md) lleva un bloque frontmatter que declara sus relaciones:

```yaml
---
id: US-1.2.3
type: user-story
title: Registrar Resultado (RP)
bc: competencia
status: Implementada
baseline: BL-001
traces:
  part_of: INC-1.2
  constrained_by: [ADR-001, ADR-007, ADR-008]
  requires: [US-1.2.1]
  implemented_by: [competencia/application/commands/registrar_resultado.py]
  verified_by: [tests/features/US-1.2.3.feature]
---
```

Para los ADRs:

```yaml
---
id: ADR-007
type: adr
title: SQLite persistencia por BC
status: Aceptada
fecha: 2026-03-18
traces:
  related_to: [ADR-001]
  constrains: [US-1.2.3, US-2.1.1, US-3.1.1]
---
```

### 3.2 Anotaciones en código fuente

Los archivos Python y TypeScript declaran su relación con las USs en el docstring o
comentario de cabecera. La convención ya existe en el proyecto de forma implícita;
este sistema la formaliza:

```python
"""RegistrarResultado — @implements US-1.2.3"""
```

La anotación es parseable con una expresión regular simple:
`@implements\s+(US-[\d.]+|US-ADJ-[\d.]+)`.

### 3.3 Análisis estático de imports

Las dependencias técnicas entre archivos fuente se derivan automáticamente sin declaración
manual. El script usa el módulo `ast` de Python para analizar imports y filtra solo
aquellos que apuntan al propio proyecto (excluye bibliotecas externas).

Para TypeScript se aplica análisis de imports relativos (`from '../'`, `from './'`).

---

## 4. Vocabulario de relaciones

Las aristas del grafo tienen tipo explícito. El vocabulario es bidireccional — cada
relación tiene su inversa, lo que permite recorrer el grafo en cualquier dirección.

### Relaciones semánticas (declaradas)

| Arista | Inversa | Significado |
|--------|---------|-------------|
| `implements` | `implemented_by` | Este código realiza esta US |
| `constrained_by` | `constrains` | Esta US debe respetar este ADR |
| `verified_by` | `verifies` | Este test verifica esta US |
| `part_of` | `contains` | Esta US pertenece a este Incremento |
| `requires` | `required_by` | Esta US necesita que otra esté hecha |
| `supersedes` | `superseded_by` | Este ADR reemplaza a otro |
| `related_to` | (simétrica) | Relación semántica sin dirección dominante |

### Relaciones técnicas (derivadas)

| Arista | Inversa | Significado |
|--------|---------|-------------|
| `depends_on` | `depended_by` | Este archivo importa o usa aquel |

---

## 5. TRACE-INDEX.json — el grafo derivado

El archivo central del sistema. Se genera a partir de las tres fuentes y nunca se edita
manualmente. Su estructura es un grafo de nodos y aristas compatible con las principales
bibliotecas de visualización (D3.js, Vis.js, Cytoscape.js).

```json
{
  "version": "1.0",
  "generated_at": "2026-05-17T...",
  "nodes": {
    "US-1.2.3": {
      "type": "user-story",
      "file": "docs/plans/sp1/US-1.2.3-plan.md",
      "title": "Registrar Resultado (RP)",
      "bc": "competencia",
      "status": "Implementada",
      "baseline": "BL-001"
    },
    "ADR-007": {
      "type": "adr",
      "file": "docs/adr/ADR-007-sqlite-persistencia-bc.md",
      "title": "SQLite persistencia por BC"
    },
    "competencia/application/commands/registrar_resultado.py": {
      "type": "source",
      "bc": "competencia"
    }
  },
  "edges": [
    { "from": "competencia/application/commands/registrar_resultado.py",
      "to": "US-1.2.3", "type": "implements" },
    { "from": "US-1.2.3", "to": "ADR-007", "type": "constrained_by" },
    { "from": "competencia/application/commands/registrar_resultado.py",
      "to": "competencia/domain/aggregates/performance.py", "type": "depends_on" }
  ]
}
```

El script generador ejecuta cuatro pasos:
1. Parsear frontmatter YAML en todos los `.md` → aristas semánticas
2. Parsear anotaciones `@implements` en `.py` y `.ts` → aristas código→US
3. Analizar imports con `ast` (Python) y regex (TypeScript) → aristas técnicas
4. Construir grafo bidireccional y escribir `TRACE-INDEX.json`

---

## 6. Vistas con propósito

Una vista no es una receta de traversal. Es un **propósito nombrado** que el agente
interpreta para decidir qué recorrer según el grafo real que encuentra. Esto permite
que la navegación sea adaptativa — si una US tiene siete ADRs, el agente los resume;
si tiene uno, lo carga completo.

El archivo `TRACE-VIEWS.json` declara las vistas disponibles:

```json
{
  "views": [
    {
      "id": "vista:preimplementar",
      "proposito": "Reunir el contexto completo que un implementador necesita antes de tocar código: restricciones arquitectónicas, contratos formales IEDD (precondiciones, postcondiciones, invariantes), dependencias existentes y estado actual de implementación.",
      "entrada": ["user-story", "increment"],
      "stakeholder": "desarrollador o agente-implementador"
    },
    {
      "id": "vista:impacto",
      "proposito": "Determinar qué artefactos pueden verse afectados por un cambio en un archivo fuente: USs implementadas, invariantes a respetar, archivos que dependen del modificado, ADRs que gobiernan esa zona del código.",
      "entrada": ["source"],
      "stakeholder": "revisor o agente-verificador"
    },
    {
      "id": "vista:arquitecto",
      "proposito": "Entender las decisiones arquitectónicas del sistema, sus relaciones entre sí y qué áreas del código gobiernan. Sin detalle de implementación.",
      "entrada": ["adr", "sprint"],
      "stakeholder": "arquitecto, tech lead"
    },
    {
      "id": "vista:cierre-sp",
      "proposito": "Verificar qué entregó un Subproyecto: incrementos completados, USs implementadas, código producido y baselines registradas.",
      "entrada": ["sprint"],
      "stakeholder": "gestor de proyecto, revisión de baseline"
    },
    {
      "id": "vista:dominio",
      "proposito": "Explorar la lógica de dominio de un BC: aggregates, value objects, eventos de dominio y las USs que los pusieron en juego.",
      "entrada": ["domain", "user-story"],
      "stakeholder": "experto de dominio, diseñador DDD"
    }
  ]
}
```

---

## 7. Navegación humana vs. navegación de agente

El modelo sirve a ambos navegantes desde la misma estructura. Lo que cambia es la
interfaz y el nivel de automatización.

### Navegación humana

Para el humano, el sistema no introduce herramientas obligatorias. El frontmatter YAML
en los archivos `.md` es legible y los links son clickeables en cualquier editor de
markdown (VS Code, Obsidian, GitHub). La navegación es manual, pero los links están
**donde se necesitan** y son **explícitos**.

El documento `TRACE-VIEWS.md` actúa como guía de entrada:

```
Si tu pregunta es…                    Empezá por…
────────────────────────────────────────────────────────────
¿Por qué este código tiene esta forma? Archivo → @implements → US → ADR
¿Qué entregó el SP5?                  CLAUDE.md → BL-005 → Incrementos → USs
¿Qué restricciones aplican a esta US? US → constrained_by → ADRs
¿Qué puede romper este cambio?        Archivo → depended_by → dependientes
```

Para una experiencia visual completa, el proyecto incluye `docs/TRACE-GRAPH-DEMO.html`
— un grafo interactivo con D3.js que carga `TRACE-INDEX.json` y permite filtrar por
vista, explorar vecindarios de nodos y seguir backlinks.

### Navegación de agente

El agente opera sobre `TRACE-INDEX.json` mediante consultas programáticas:

**Pre-implementación** — contexto antes de actuar:
```
entrada: US-4.3.1
→ constrained_by  → cargar ADRs relevantes (contexto arquitectónico)
→ part_of         → cargar Incremento y Baseline (contexto de entrega)
→ requires        → verificar USs precondición (dependencias de negocio)
→ implemented_by  → verificar si ya existe código parcial
→ verified_by     → cargar tests de aceptación (contrato formal)
```

**Post-implementación** — verificación después de actuar:
```
entrada: competencia/application/commands/registrar_resultado.py
→ implements      → cargar US-1.2.3 (postcondiciones e invariantes)
→ constrained_by  → verificar respeto de ADRs
→ depended_by     → identificar archivos que pueden haber sido afectados
```

---

## 8. Estado actual del proyecto respecto al sistema

El proyecto ya tiene la semántica latente. Los cambios necesarios son de formalización,
no de creación desde cero.

| Artefacto | Estado actual | Cambio requerido |
|-----------|--------------|-----------------|
| Archivos `.py` de application | Docstring menciona US en prosa libre | Estandarizar a `@implements US-X.Y.Z` |
| Planes de US (`.md`) | Referencias a INC, ADRs en texto | Agregar frontmatter YAML con `traces:` |
| ADRs (`.md`) | Campo `Relacionado` en tabla markdown | Migrar a frontmatter YAML |
| IEDD template | Sección "Referencias" en prosa | Agregar frontmatter YAML |
| `TRACE-INDEX.json` | No existe | Crear mediante script generador |
| `TRACE-VIEWS.json` | No existe | Crear con las 5 vistas definidas |
| `TRACE-VIEWS.md` | No existe | Crear como guía de entrada para humanos |

---

## 9. Alcance del piloto propuesto

Para validar el modelo antes de instrumentar todo el proyecto, se propone un piloto
acotado sobre un Incremento completo con cadena documental conocida.

**Criterios de selección del Incremento piloto:**
- Tiene USs con ADRs asociados documentados
- El código de application service existe y tiene docstring con referencia a US
- Tiene tests de aceptación

**Candidato**: INC-1.2 (Resultados) — cadena `US-1.2.3` → `ADR-001/007/008` →
`registrar_resultado.py` → `Performance` (aggregate). Todos los artefactos existen
y fueron inspeccionados durante el diseño.

**Pasos del piloto:**

1. Agregar frontmatter YAML a los planes de US del INC-1.2
2. Agregar frontmatter YAML a ADR-001, ADR-007 y ADR-008
3. Estandarizar docstrings con `@implements` en los application commands de INC-1.2
4. Escribir el script generador de `TRACE-INDEX.json`
5. Crear `TRACE-VIEWS.json` con las 5 vistas definidas
6. Ejecutar las dos consultas de navegación (pre-implementar, impacto) sobre el subgrafo
7. Evaluar completitud y utilidad → decidir extensión al proyecto completo

---

## 10. Decisiones de diseño y sus fundamentos

| Decisión | Alternativa descartada | Fundamento |
|----------|----------------------|------------|
| Frontmatter YAML en MD | Sección "Referencias" en prosa | Parseable por agente; clickeable para humano; sin herramienta adicional |
| `@implements` en docstring | Archivo sidecar `.trace.json` | Menos archivos; la convención ya existe en el proyecto |
| Dependencias técnicas por análisis estático | Declaración manual | Los imports son la fuente de verdad; la declaración manual generaría divergencia |
| Vistas con propósito (no receta) | Traversal prescripto en JSON | El agente adapta la profundidad según el grafo real; más robusto ante grafo incompleto |
| TRACE-INDEX.json derivado, nunca editado | Edición manual del índice | Evita divergencia entre fuentes; el índice siempre refleja el estado real |
| Un grafo + múltiples vistas | Múltiples grafos por stakeholder | Consistencia garantizada; una sola fuente de verdad |

---

*Documento generado: 2026-05-17*
*Próximo artefacto: PLAN-TRAZA-PILOTO.md — plan de implementación del piloto sobre INC-1.2*
