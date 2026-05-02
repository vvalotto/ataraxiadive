# Análisis: software_limpio y sus Sub-productos

> Estado documental: histórico
> Análisis técnico de dependencies externas realizado en Marzo 2026.
> Conservado como evidencia del contexto de herramientas disponibles.
> Fuente vigente relacionada: `pyproject.toml`, `frontend/package.json`

**Fecha:** Marzo 2026
**Versión analizada:** quality_agents v0.3.1

---

## 1. Naturaleza del proyecto: más que un paquete Python

A diferencia de `claude-dev-kitc` —que es una herramienta de automatización de
procesos— `software_limpio` es un **ecosistema intelectual con cuatro dimensiones
entrelazadas**. Entenderlo solo como código es perder la mayor parte de su valor.

| Dimensión | Artefacto | Estado |
|-----------|-----------|--------|
| **Paquete Python** | `quality-agents` v0.3.1 (.whl + .tar.gz publicados) | ✅ Producción |
| **Marco conceptual** | "La Trilogía Limpia" (libro / compendio) | 🟡 En desarrollo |
| **Investigación académica** | Documentos de trabajo (pedagogía, IA, métricas) | 🟡 En desarrollo |
| **Propuesta de curso** | Capacitación para empresas y uso académico (FIUNER) | 🟡 En desarrollo |

El código es la **implementación práctica** del marco conceptual.
El marco conceptual es el **fundamento filosófico** del código.
Son inseparables.

---

## 2. El paquete: sistema de calidad en tres niveles

`quality_agents` implementa tres agentes con momentos, duraciones y comportamientos
distintos en el pipeline de desarrollo:

```
Pre-commit             PR Review              Fin de Sprint / Baseline
(< 5 segundos)         (2-5 minutos)          (10-30 minutos)
      ↓                      ↓                        ↓
  CodeGuard           DesignReviewer           ArchitectAnalyst
  Solo advierte       Bloquea si CRITICAL      Solo informa, persiste tendencias
```

### CodeGuard (v0.1.0) — 6 checks
PEP8 (flake8) · Seguridad (bandit) · Complejidad ciclomática (radon) ·
Calidad general (pylint) · Tipos estáticos (mypy) · Imports sin usar.

**Filosofía:** Nunca paraliza. Es un espejo, no un juez. El desarrollador decide.

### DesignReviewer (v0.2.0) — 12 analyzers AST

Acoplamiento: CBO, Fan-Out, Importaciones Circulares.
Cohesión y herencia: LCOM, WMC, DIT, NOP.
Code Smells / SOLID: God Object, Long Method, Long Parameter List,
Feature Envy, Data Clumps.

**Filosofía:** Aquí sí hay consecuencias. Exit code 1 si hay CRITICAL — bloquea el merge.
El diseño se defiende antes de entrar a la base de código.

### ArchitectAnalyst (v0.3.0) — 7 métricas cross-module

Métricas de Robert Martin: Ca, Ce, Inestabilidad (I), Abstracción (A),
Distancia al Main Sequence (D).
Estructurales: Ciclos de dependencia (algoritmo de Tarjan),
Violaciones de capas.

**Filosofía:** Perspectiva de sprint, no de commit. Muestra tendencias entre ejecuciones.
Persiste snapshots en SQLite (`.quality_control/architecture.db`).
Nunca bloquea — informa para que el equipo decida.

---

## 3. La arquitectura interna: patrón Verifiable

Todos los checks, analyzers y métricas heredan de `Verifiable`:

```python
class Verifiable:
    name: str
    category: str
    estimated_duration: float
    priority: int            # 1 = mayor prioridad

    def should_run(context: ExecutionContext) -> bool
    def execute(file_path: Path) -> List[CheckResult]
```

Un `Orchestrator` hace auto-discovery de todos los `Verifiable` disponibles,
los selecciona según contexto y presupuesto de tiempo, y los ejecuta en orden
de prioridad. **Agregar un nuevo check = crear un archivo, heredar de Verifiable.**

Esto es software limpio enseñando con el ejemplo: el propio framework aplica
los principios que verifica.

---

## 4. El marco conceptual: "La Trilogía Limpia"

Este es el núcleo intelectual del proyecto. Victor propone completar la trilogía
de Robert C. Martin añadiendo el nivel intermedio que está ausente:

| Nivel | Obra de Martin | Propuesta Victor | Pregunta ética |
|-------|---------------|------------------|----------------|
| Micro | Clean Code (2008) | ✅ Código Limpio | ¿Puede otro humano entender esto? |
| **Medio** | **— (vacío)** | **🆕 Diseño Limpio** | **¿Puede otro humano modificar esto?** |
| Macro | Clean Architecture (2017) | ✅ Arquitectura Limpia | ¿Puede el sistema evolucionar? |

### Los 6 fundamentos universales del Diseño Limpio

La contribución original de Victor: estos principios son **anteriores a OOP**,
agnósticos al paradigma, y pueden verificarse con métricas objetivas.

| # | Fundamento | Origen histórico |
|---|-----------|-----------------|
| 1 | Modularidad | Parnas, 1972 |
| 2 | Ocultamiento de información | Parnas, 1972 |
| 3 | Alta cohesión | Constantine, 1968 |
| 4 | Bajo acoplamiento | Constantine, 1968 |
| 5 | Separación de concerns | Dijkstra, 1974 |
| 6 | Abstracción | Liskov, 1974 |

SOLID no es el fundamento — es la reinterpretación de estos principios en OO.
El Diseño Limpio es más profundo y más general.

### La tesis central

> *"En la era de la IA generativa, enseñar a programar es enseñar una habilidad
> que las máquinas ya dominan. La formación del profesional del software debe
> centrarse en lo que las máquinas no pueden hacer: juzgar éticamente, diseñar
> con principios, verificar objetivamente, y asumir responsabilidad."*

El desarrollador no es quien escribe código. Es quien **dirige, evalúa, refina y
decide**. `software_limpio` es la herramienta que le da objetividad a ese rol.

---

## 5. El roadmap v0.4.0: IA como agente orquestador

El backlog tiene una evolución muy significativa planeada: integración opt-in de
Claude como orquestador de los checks vía Anthropic API (tool use):

```
Modo actual:
  orquestador Python → ejecuta todos los checks → formato output

Modo v0.4.0 (Plan B — Agente):
  Claude recibe tarea "revisá este archivo"
  → decide qué tools (checks) activar según contexto
  → los ejecuta en múltiples turnos
  → interpreta resultados de forma holística
  → emite veredicto integrado
```

Esto es arquitectónicamente elegante: los checks de calidad se exponen como
**tools de la API de Anthropic**, y Claude razona sobre qué checks son relevantes
para cada archivo en particular. El agente es activo, no pasivo.

Esta capacidad, al activarse, convierte a `software_limpio` en un sistema donde
**la IA no solo genera código sino que evalúa la calidad del código que genera**.
Cierra el loop de manera notable.

---

## 6. Integración en el ecosistema completo

### El encaje de las tres herramientas

```
┌─────────────────────────────────────────────────────────────────────┐
│       ENTORNO-IA-DEV (Marco de CM) — nivel estratégico              │
│   ADRs · RFCs · Líneas base · Trazabilidad · Memoria del producto   │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
        ┌──────────────────┴──────────────────┐
        ▼                                     ▼
┌───────────────────┐               ┌─────────────────────────┐
│  CLAUDE-DEV-KITC  │               │   SOFTWARE LIMPIO        │
│  nivel táctico    │               │   nivel de medición      │
│                   │               │                          │
│  /implement-us    │               │  codeguard (pre-commit)  │
│  10 fases         │──────────────►│  designreviewer (PR)     │
│  BDD→Code→Tests   │               │  architectanalyst (BL)   │
└───────────────────┘               └─────────────────────────┘
```

`claude-dev-kitc` **implementa**. `software_limpio` **mide**.
El marco de CM **recuerda y decide**.

### Integración punto a punto

**CodeGuard ↔ pre-commit hook del repositorio**

```yaml
# .pre-commit-config.yaml en cada proyecto gestionado
repos:
  - repo: https://github.com/vvalotto/software_limpio
    rev: v0.3.1
    hooks:
      - id: codeguard
        args: ['--analysis-type', 'pre-commit']
```

Esto hace que cada `git commit` del desarrollador o de Claude Code dispare
CodeGuard automáticamente. El costo es mínimo (~5 segundos), nunca bloquea.

**DesignReviewer ↔ política de merge a main**

Nuestro `CLAUDE.md` ya tiene el checklist "antes de mergear a main".
Agregar: `designreviewer src/` como condición bloqueante.
Si hay violaciones CRITICAL, el merge no puede proceder. Punto.

**ArchitectAnalyst ↔ establecimiento de Baselines**

Este es el punto de integración más valioso y original:

```
Flujo de baseline enriquecido:

[COWORK]  Decidir establecer BL-NNN
[CODE]    architectanalyst src/ --sprint-id BL-NNN --format json
[CODE]    Guardar resultado en .cm/baselines/BL-NNN-arquitectura.json
[COWORK]  Incorporar métricas en BL-NNN.md:
          - Inestabilidad promedio
          - Módulos en zona de peligro (D > threshold)
          - Ciclos de dependencia detectados
          - Tendencias respecto a BL anterior
```

Esto transforma las líneas base de documentos cualitativos a registros con
**evidencia cuantitativa** de la salud arquitectónica en ese momento del tiempo.
La "deuda técnica observable" deja de ser una estimación y se convierte en datos.

**v0.4.0 ↔ Cowork como director de calidad**

Cuando la integración IA esté activa en `software_limpio`, el ciclo completo
de Cowork → Code → medición se vuelve más cerrado:

```
[COWORK]  Aprueba plan de implementación de US-NNN
[CODE]    /implement-us US-NNN → genera código
[CODE]    CodeGuard en cada commit (feedback inmediato)
[CODE]    DesignReviewer en PR (gate de diseño)
[CODE]    DesignReviewer IA: "además de las violaciones detectadas, el
          acoplamiento entre X e Y sugiere revisar la responsabilidad de Z"
[COWORK]  Incorpora observación en ADR o RFC si corresponde
```

La IA cierra el loop de feedback desde la medición hacia la decisión.

---

## 7. Cambios necesarios en el entorno-ia-dev

### 7.1 CLAUDE.md — agregar sección de quality agents

```markdown
## Quality Agents (software_limpio)

Este proyecto tiene quality-agents v0.3.1 instalado (pre-commit configurado).

Pre-commit (automático, < 5s):
  codeguard src/          # Solo advierte, nunca bloquea

Antes de mergear a main (obligatorio):
  designreviewer src/     # Bloquea si hay CRITICAL
  # Exit code 0 → merge permitido
  # Exit code 1 → corregir antes de mergear

Al establecer una baseline:
  architectanalyst src/ --sprint-id BL-NNN --format json
  # Guardar output en .cm/baselines/BL-NNN-arquitectura.json
```

### 7.2 Template BL-000 — agregar sección de métricas arquitectónicas

```markdown
## Métricas Arquitectónicas (ArchitectAnalyst)

Sprint ID: BL-NNN
Ejecutado: YYYY-MM-DD

| Módulo      | Inestabilidad (I) | Abstracción (A) | D (distancia) | Estado  |
|-------------|-------------------|-----------------|---------------|---------|
| domain      | 0.1               | 0.8             | 0.1           | ✅ Sano |
| application | 0.5               | 0.4             | 0.1           | ✅ Sano |
| infra       | 0.9               | 0.1             | 0.0           | ✅ Sano |

Ciclos de dependencia detectados: N
Violaciones de capas: N
Tendencia vs BL anterior: ↑↓=
```

### 7.3 Estructura del repositorio — agregar carpeta de snapshots

```
.cm/
├── cm-plan.md
├── baselines/
│   ├── BL-001-inception.md
│   └── BL-001-arquitectura.json    ← output de ArchitectAnalyst
└── changes/
```

---

## 8. La dimensión académica: lo que el código sostiene

Los "Documentos de Trabajo local" revelan que el proyecto tiene un alcance
mucho mayor que un paquete PyPI. Victor está construyendo simultáneamente:

- Una **investigación sobre la enseñanza de IS en la era de la IA** (revisión de
  literatura 2023-2025, con meta-análisis sobre CS1/CS2 y herramientas de IA)
- Una **propuesta de capacitación para empresas** (docs/curso/propuesta-empresas.md)
- Un **compendio/libro** que integra filosofía, ética, métricas y práctica

`software_limpio` no es solo una herramienta — es la **demostración empírica
de la tesis**: que el desarrollador en la era de la IA es un director de calidad
que usa métricas objetivas como lenguaje de evaluación. El código demuestra que
esa visión es implementable, no solo teórica.

---

## 9. Valoración general y síntesis

`software_limpio` es el **proyecto más cohesionado y filosóficamente fundado**
del ecosistema. Mientras que `claude-dev-kitc` resuelve el "cómo implementar",
`software_limpio` responde "cómo saber si lo que implementamos es bueno".

Lo que aporta al framework de CM que los otros no tienen:
- **Objetividad cuantitativa**: métricas con umbrales, no opiniones
- **Evolución en el tiempo**: las tendencias del ArchitectAnalyst hacen visible
  cómo la arquitectura envejece o mejora entre baselines
- **Consecuencias reales**: el DesignReviewer bloquea merges — no es decorativo
- **Fundamentación filosófica**: los 6 principios universales del Diseño Limpio
  dan coherencia conceptual a lo que las métricas miden

La integración recomendada es **inmediata y sin fricciones**: instalar
`quality-agents` como dependencia de desarrollo en el proyecto sandbox,
configurar el pre-commit hook, y agregar `designreviewer` y `architectanalyst`
a los protocolos de merge y baseline del marco de CM.

---

## 10. El ecosistema completo: una visión unificada

Con los tres proyectos analizados, emerge una arquitectura coherente:

```
"La Trilogía Limpia" (marco filosófico)
        │ operacionalizado por
        ▼
software_limpio (mide la calidad con objetividad)
        │ integrado con
        ▼
entorno-ia-dev (CM: memoria estratégica del producto)
        │ ejecutado mediante
        ▼
claude-dev-kitc (automatización táctica US a US)
```

No hay redundancias. Cada herramienta resuelve un problema que las otras no
abordan. Y el conjunto responde a una pregunta muy precisa:

> *¿Cómo construir software de calidad, de forma sostenible, usando la IA como
> amplificador del juicio profesional y no como reemplazante del mismo?*

Esa pregunta — que es también la tesis del libro — tiene ahora una respuesta
práctica, implementada, medible y evolucionable.

---

*Análisis generado con Claude Cowork — Marzo 2026*
