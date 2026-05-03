# Plan: Fase 0 — Diseño Estratégico

> Estado documental: histórico
> Conservado como evidencia de planificación inicial pre-SP1.
> No usar como fuente de verdad para el ciclo de desarrollo actual.
> Fuente vigente relacionada: `docs/plans/WORKFLOW-DESARROLLO.md`

| Campo | Valor |
|-------|-------|
| **Fase** | 0 — Semana 0 / Arquitectura Estratégica |
| **Objetivo** | Completar las Capas 1-4 de IEDD antes de iniciar SP1 |
| **Responsable** | Claude Cowork (documentación) + Claude Code (commits) |
| **DoD de Fase** | Todos los artefactos creados, BL-000 actualizada, CLAUDE.md vigente |
| **Fecha inicio** | 2026-03-15 |
| **Fecha cierre** | Pendiente — 6/11 artefactos completados al 2026-03-18 |

---

## Propósito de esta Fase

La Fase 0 no produce código. Produce **especificaciones verificables**.

Cada artefacto generado aquí es un dato del experimento: demuestra que recorrer
las capas IEDD antes de implementar produce diseños más coherentes y reduce la
ambigüedad que llega al código. Al cerrar esta fase con una baseline, tenemos
un punto de comparación objetivo para medir la fidelidad del código respecto al
modelo cuando llegue SP1.

El orden de los artefactos no es opcional. Cada capa depende de la anterior.

---

## Estado Inicial (al abrir esta Fase)

### Documentación

| Artefacto | Estado | Observación |
|-----------|--------|-------------|
| docs/adr/ADR-001 a ADR-004 | ✅ Completos | Con contexto, decisión y consecuencias |
| docs/contexto/ (5 archivos) | ✅ Completos | ANALISIS + PLAN-EXPERIMENTO |
| docs/dominio/ (5 archivos) | ✅ Completos | Dominio, arquitectura, calidad, estrategia, RFs |
| docs/iedd/ (4 archivos) | ✅ Completos | Marco conceptual + template US-IEDD |
| CLAUDE.md | ✅ Actualizado | Incluye contexto experimental completo |
| .cm/baselines/BL-000-pre-codigo.md | ⚠️ Desactualizado | Referencia docs externos; debe incorporar los CIs nuevos |
| docs/requirements/vision.md | ❌ Faltante | Capa 1 IEDD |
| docs/design/context-map.md | ❌ Faltante | Capa 2 IEDD — diseño estratégico |
| docs/design/domain-model.md | ❌ Faltante | Capa 2 IEDD — diseño táctico |
| docs/design/architecture.md | ❌ Faltante | Capa 4 IEDD |
| docs/adr/ADR-005-bounded-contexts.md | ❌ Faltante | Decisión de diseño estratégico DDD |
| docs/design/estrategia-desarrollo-bc.md | ❌ Faltante | Mapeo SP/Incrementos → Bounded Contexts |
| docs/traceability/matrix.md | ⚠️ Template vacío | Inicializar con CIs de Fase 0 |

### Herramientas (prerequisito para SP1)

| Herramienta | Estado | Observación |
|-------------|--------|-------------|
| Claude Dev Kit (`/implement-us`) | ❌ No instalado | `skills/` vacío — instalar antes de SP1 |
| software_limpio / quality-agents | ❌ No instalado | Paquete no está en dependencias del proyecto |
| CodeGuard (pre-commit hook) | ⚠️ Configurado, no funcional | `.pre-commit-config.yaml` tiene el hook pero `codeguard` no existe en el entorno |
| DesignReviewer | ⚠️ Configurado, no funcional | `pyproject.toml` tiene `[tool.designreviewer]` pero sin paquete instalado |
| ArchitectAnalyst | ⚠️ Configurado, no funcional | `pyproject.toml` tiene `[tool.architectanalyst]`, `quality/` no existe |

**Qué hay que hacer antes de SP1 (lo hace Claude Code):**

```bash
# 1. Instalar quality-agents (software_limpio)
pip install quality-agents  # o el nombre real del paquete publicado en PyPI

# 2. Agregar quality-agents a pyproject.toml [project.optional-dependencies] dev
# 3. Crear carpeta quality/reports/
mkdir -p quality/reports

# 4. Instalar Claude Dev Kit en skills/
python ~/.claude-dev-kit/install/installer.py --profile fastapi-hexagonal
# (o el perfil más cercano disponible)

# 5. Verificar que pre-commit funciona
pre-commit install
pre-commit run --all-files
```

> **Nota:** La instalación de herramientas es responsabilidad de Claude Code,
> no de Cowork. Cowork verifica el estado; Code ejecuta la instalación.
> Esto se hace como parte del cierre de Fase 0 / apertura de SP1.

---

## Artefactos a Producir

### Artefacto 1 — `docs/requirements/vision.md`
**Capa IEDD:** 1 — Dominio
**Propósito:** Declarar el propósito del sistema, sus usuarios, sus fronteras y lo
que NO hace. Es el contrato de alcance. Sin este documento, las US no tienen anclaje.

**Contenido mínimo:**
- Problema que resuelve AtaraxiaDive (una oración)
- Usuarios del sistema con sus objetivos (Organizador, Juez, Atleta, Admin)
- Alcance del sistema v1 (qué está dentro, qué queda fuera)
- Criterios de éxito del producto (derivados de los atributos de calidad AC-XX-NN)
- Relación con el experimento IEDD (por qué este proyecto como sandbox)

**Insumos:** `docs/dominio/01-dominio_torneos_apnea.md`, `docs/dominio/03-atributos_calidad.md`
**Produce:** Punto de partida formal para el Context Map

---

### Artefacto 2 — `docs/design/event-storming-big-picture.md`
**Capa IEDD:** Entre Capa 1 y Capa 2 — exploración estratégica del dominio
**Tipo ES:** Big Picture Event Storming
**Propósito:** Explorar el dominio completo del torneo de apnea — todas sus fases,
desde la apertura hasta el cierre — sin asumir BC previos. Los Bounded Contexts
emergen de este ES cuando el lenguaje cambia en la línea de eventos. Este artefacto
es la base empírica del Context Map.

Esta sesión es de modalidad **solo-asincrónica** (Victor como único experto del dominio),
ejecutada con asistencia de Claude. La limitación de no tener equipo se compensa con la
profundidad del dominio ya documentado en `docs/dominio/`. Es también un dato del experimento:
¿qué pierde y qué gana un ES sin la dinámica colaborativa grupal?

**Contenido mínimo:**
- Alcance: dominio completo — Apertura → Inscripción → Preparación → Ejecución → Premiación → Cierre
- Línea de eventos (naranja): todos los domain events del dominio en orden temporal
- Comandos (azul): acciones que disparan cada evento
- Actores (amarillo): roles que ejecutan los comandos
- Políticas (rosa): reglas automáticas de negocio identificadas
- Hot Spots (rojo): incertidumbres, conflictos y ambigüedades detectadas
- Candidatos a BCs: zonas donde el lenguaje cambia o hay consistencia transaccional natural
- Derivación: tabla de eventos → candidatos a Bounded Context

**Insumos:** `docs/requirements/vision.md`, `docs/dominio/01-dominio_torneos_apnea.md`, `docs/dominio/05-requerimientos_funcionales.md`
**Produce:** Evidencia empírica para `context-map.md` — BCs identificados desde el dominio, no impuestos

> **Nota del experimento:** La hipótesis es que los BCs que emergen del Big Picture ES
> son más coherentes que los 7 BCs identificados preliminarmente en `CLAUDE.md`. Las
> diferencias entre ambos son un dato experimental valioso.
> Ver: `docs/contexto/DECISION-EVENT-STORMING.md`

---

### Artefacto 4 — `docs/design/context-map.md`
**Capa IEDD:** 2 — Modelo (estratégico)
**Propósito:** Identificar los Bounded Contexts, su tipo (Core/Supporting/Generic),
y los patrones de integración entre ellos. Este es el artefacto central de la Fase 0.
Sin él, los aggregates flotan sin contexto y el Dev Kit no puede respetar fronteras.

**Contenido mínimo:**
- Mapa visual de los 7 BCs identificados (diagrama de texto o Mermaid)
- Por cada BC: nombre, tipo, responsabilidad, aggregates principales
- Patrones de integración entre BCs (ACL, Customer/Supplier, OHS, etc.)
- Integración con sistemas externos (BD FAAS, AIDA/CMAS) — aunque quede como pendiente
- Justificación de por qué Competencia es el Core Domain

**BCs identificados preliminarmente:**

| Bounded Context | Tipo | Justificación |
|----------------|------|---------------|
| Competencia | Core Domain | Lógica no trivial, invariantes duros, Event Sourcing |
| Gestión de Torneo | Supporting | Ciclo de vida del torneo, máquina de estados |
| Registro | Supporting | Atleta, inscripción, anuncios, integra FAAS |
| Resultados | Supporting | Rankings, podios, publicación |
| Configuración | Generic | Disciplinas, categorías, reglas (datos, no lógica) |
| Identidad | Generic | Usuarios, roles, autenticación |
| Notificaciones | Generic | Email/push (servicio, no aggregate) |

**Insumos:** `docs/requirements/vision.md`, `docs/design/event-storming-big-picture.md`, `docs/dominio/05-requerimientos_funcionales.md`
**Produce:** Estructura de módulos del proyecto en `src/` — BCs con evidencia empírica del ES

---

### Artefacto 5 — `docs/design/event-storming-competencia.md`
**Capa IEDD:** Entre Capa 2 y Capa 3 — profundización táctica del Core Domain
**Tipo ES:** Process Modeling + Software Design Event Storming
**Propósito:** Profundizar el BC Competencia — ya identificado y formalizado en el
Context Map — modelando en detalle el flujo de ejecución de una performance.
A diferencia del Big Picture, este ES asume los límites del BC y se enfoca en
descubrir aggregates, invariantes y domain events con semántica precisa.

El resultado alimenta directamente el `domain-model.md` y los primeros US-IEDD de SP1.

**Contenido mínimo:**
- Alcance: BC Competencia — desde llamado del atleta hasta asignación de tarjeta
- Línea de eventos (naranja): domain events del BC con semántica precisa
- Comandos (azul): operaciones del aggregate con sus pre/post condiciones implícitas
- Actores y Agregados (amarillo): Juez, Performance, DisciplinaEnEjecucion
- Políticas (rosa): reglas automáticas — black-out → tarjeta roja, DNS, etc.
- Hot Spots (rojo): invariantes complejos, casos borde, puntos de riesgo
- Read Models (verde): información que Juez necesita para ejecutar comandos
- Derivación: tabla de pares Comando → Evento → candidato a US-IEDD (con precondición/postcondición)

**Insumos:** `docs/design/context-map.md`, `docs/design/event-storming-big-picture.md`, `docs/dominio/05-requerimientos_funcionales.md`
**Produce:** Insumos directos para `domain-model.md` y US-IEDD de SP1

> **Nota del experimento:** Este es el ES que produce las US-IEDD. La calidad y
> completitud de los invariantes aquí se compara con lo que hubiera surgido del
> análisis directo de los RF-EJ-* del cuestionario. Ver: `docs/contexto/DECISION-EVENT-STORMING.md`

---

### Artefacto 6 — `docs/design/domain-model.md`
**Capa IEDD:** 2 — Modelo (táctico)
**Propósito:** Definir los aggregates, value objects y domain events por BC.
Cada invariante documentado aquí es un candidato directo a criterio de aceptación
en la US-IEDD correspondiente.

**Contenido mínimo por BC (al menos Competencia y Gestión de Torneo para SP1/SP2):**
- Aggregates con sus invariantes formales
- Value Objects (tipos con identidad vs. tipos por valor)
- Domain Events con su semántica (qué ocurrió, qué datos lleva)
- Lenguaje ubicuo refinado por BC (puede diferir entre contextos)

**Aggregates identificados preliminarmente:**

| BC | Aggregate Root | Invariantes clave |
|----|----------------|-------------------|
| Competencia | Performance | AP > 0; tarjeta asignable solo una vez; black-out → roja automática |
| Competencia | DisciplinaEnEjecucion | Solo un atleta activo por andarivel en un momento |
| Gestión de Torneo | Torneo | Transición de estados irreversible salvo excepciones |
| Registro | Inscripcion | Atleta no compite sin anuncio; anuncio inmutable una vez registrado |
| Configuración | Disciplina | Las reglas son datos, no código |

**Insumos:** `docs/design/context-map.md`, `docs/design/event-storming-competencia.md`, `docs/dominio/05-requerimientos_funcionales.md`
**Produce:** Insumo directo para US-IEDD en SP1

---

### Artefacto 7 — `docs/design/architecture.md`
**Capa IEDD:** 4 — Arquitectura
**Propósito:** Documento vivo que describe la organización del sistema como
consecuencia del modelo. No es la arquitectura de referencia v1 (que ya existe en
`docs/dominio/02-arquitectura_referencia.md`) — es la arquitectura formal del
proyecto, que evolucionará con cada baseline.

**Contenido mínimo:**
- Estilo arquitectónico: Hexagonal + Event Sourcing (con justificación por BC)
- Estructura de módulos mapeada a BCs: `src/<bc>/domain/`, `src/<bc>/application/`, etc.
- Reglas de dependencia (el dominio no importa infraestructura)
- Tecnologías por capa (FastAPI, PostgreSQL, React PWA, IndexedDB)
- Decisiones de integración entre BCs dentro del sistema (eventos de dominio como contratos)
- Referencia a los ADRs que sustentan cada decisión

**Insumos:** `docs/design/context-map.md`, `docs/adr/ADR-001 a ADR-004`
**Produce:** Guía para Claude Code al implementar cada US

---

### Artefacto 8 — `docs/adr/ADR-005-bounded-contexts-ddd-estrategico.md`
**Capa IEDD:** 4 — Arquitectura (decisión)
**Propósito:** Los ADR-001 a 004 cubren decisiones técnicas (Event Sourcing, FastAPI,
offline-first, reglas como datos). Ninguno documenta la decisión arquitectónica más
importante de toda la Fase 0: usar Bounded Contexts como unidad de organización
del sistema, e identificar Competencia como Core Domain.

Esta decisión tiene consecuencias directas en la estructura de `src/`, en el modo
en que el Dev Kit genera código, y en cómo Software Limpio verifica las dependencias.

**Contenido mínimo:**
- Contexto: por qué el diseño táctico sin diseño estratégico genera problemas
- Opciones: módulos por capa (domain/application/infra) vs. módulos por BC
- Decisión: organización por BC con arquitectura hexagonal interna en cada uno
- Consecuencias: estructura de `src/`, impacto en DesignReviewer

---

### Artefacto 9 — `docs/design/estrategia-desarrollo-bc.md`
**Capa:** Estratégica — cruce entre diseño y planificación
**Propósito:** El documento `docs/dominio/04-estrategia_desarrollo.md` define
5 subproyectos y 22 incrementos desde la perspectiva del producto (funcionalidades).
Este nuevo documento mapea esa estrategia a los Bounded Contexts: qué BC se construye
en qué SP, en qué orden y por qué. Es el puente entre el diseño DDD y el backlog.

**Contenido mínimo:**
- Tabla: SP → BCs involucrados → Justificación
- Criterio de secuenciación (Core Domain primero, Supporting después, Generic cuando bloquea)
- Dependencias entre BCs que determinan el orden

**Mapeo preliminar:**

| SP | Nombre | BCs involucrados | Foco |
|----|--------|------------------|------|
| SP1 | La Performance | Competencia (core) | Aggregate Performance + Event Sourcing |
| SP2 | La Competencia | Competencia (ampliado) | Flujo completo de disciplina |
| SP3 | El Torneo | Gestión de Torneo + Registro | Ciclo de vida completo |
| SP4 | La Plataforma | Configuración + Identidad + Notificaciones | Atributos de calidad |
| SP5 | La Puesta en Marcha | Todos + Resultados | Integración total + FAAS |

---

### Artefacto 10 — `docs/traceability/matrix.md` (inicialización)
**Propósito:** Inicializar la matriz con los CIs de Fase 0. Esto establece el
hábito de trazabilidad desde el primer artefacto, no desde el primer commit de código.

**CIs iniciales a registrar:**
- Todos los documentos de `docs/contexto/`, `docs/dominio/`, `docs/iedd/`
- Los 4 ADRs existentes + ADR-005
- Los nuevos documentos de `docs/design/` y `docs/requirements/`

---

### Artefacto 11 — `.cm/baselines/BL-000-pre-codigo.md` (actualización)
**Propósito:** La BL-000 actual referencia documentos externos al repo. Ahora que
todos los documentos fundacionales están en `docs/`, la BL-000 debe actualizarse
para reflejar el estado real del repositorio y cerrar formalmente la Semana 0.

**Cambios necesarios:**
- Actualizar inventario de CIs con los nuevos documentos en repo
- Actualizar sección "Próximos pasos" con el resultado de Fase 0
- Mantener fecha original (2026-03-14) como fecha de apertura; agregar fecha de cierre real

---

## Secuencia de Ejecución

```
Sesión 1 (Cowork ~60 min)
  → vision.md
  → Revisión y ajuste con Victor

Sesión 2 (Cowork ~90 min)
  → event-storming-big-picture.md
    (Big Picture ES — dominio completo, descubre candidatos a BC)
  → Revisión con Victor: ¿los BCs emergentes coinciden con los preliminares?

Sesión 3 (Cowork ~90 min)
  → context-map.md  (BCs formalizados con evidencia del Big Picture ES)
  → ADR-005         (decisión de organización por BC)

Sesión 4 (Cowork ~90 min)
  → event-storming-competencia.md
    (Process Modeling ES — BC Competencia, profundiza Core Domain)
  → Revisión con Victor: hot spots, invariantes, candidatos a US-IEDD

Sesión 5 (Cowork ~90 min)
  → domain-model.md  (aggregates con invariantes, insumo del ES Competencia)

Sesión 6 (Cowork ~60 min)
  → architecture.md             (depende de domain-model.md + ADRs)
  → estrategia-desarrollo-bc.md (depende de context-map.md)

Sesión 7 (Cowork ~45 min)
  → traceability/matrix.md inicializada
  → BL-000 actualizada
  → CLAUDE.md — ajuste final si es necesario

Sesión 7 → Cowork entrega a Code
  → Code: git commit + git tag v0.1.0 (cierre Fase 0)
```

---

## Definition of Done — Fase 0

Esta fase está terminada cuando:

- [x] `docs/requirements/vision.md` creado y aprobado por Victor
- [x] `docs/design/event-storming-big-picture.md` con línea de eventos del dominio completo, candidatos a BCs y hot spots globales
- [x] `docs/design/context-map.md` con BCs formalizados a partir del Big Picture ES
- [x] `docs/design/event-storming-competencia.md` con Process Modeling de Competencia, políticas, invariantes y candidatos a US-IEDD
- [x] `docs/design/domain-model.md` con aggregates e invariantes de SP1 y SP2 al menos
- [x] `docs/adr/ADR-005-bounded-contexts-ddd-estrategico.md` aceptado
- [ ] `docs/design/architecture.md` con estructura de módulos y reglas de dependencia
- [ ] `docs/design/estrategia-desarrollo-bc.md` con mapeo SP → BC
- [ ] `docs/traceability/matrix.md` inicializada con CIs de Fase 0
- [ ] `BL-000` actualizada con inventario completo de CIs
- [ ] `CLAUDE.md` refleja todos los artefactos nuevos con estado ✅
- [ ] Commit en `main` con tag `v0.1.0`

---

## Lo que esta Fase Produce para el Experimento

Cada artefacto de Fase 0 es también un dato del experimento:

| Artefacto | Evidencia que genera |
|-----------|---------------------|
| vision.md | ¿El dominio está suficientemente claro antes de modelar? |
| event-storming-big-picture.md | ¿Los BCs emergentes del ES coinciden con los 7 identificados preliminarmente? ¿Cuántas diferencias hay y cuán significativas son? |
| context-map.md | ¿La identificación de BCs con evidencia ES es más confiable que sin ella? ¿Qué ambigüedades en los RFs reveló el ES? |
| event-storming-competencia.md | ¿El ES produce más invariantes y hot spots que el análisis directo de los RF-EJ-*? ¿Qué pierde un ES sin equipo presencial? |
| domain-model.md | ¿Los invariantes formalizados coinciden con las respuestas del cuestionario RF? ¿El ES aportó invariantes no visibles en los RFs? |
| architecture.md | ¿La arquitectura es consecuencia del modelo o una imposición tecnológica? |
| ADR-005 | ¿La decisión de BCs habría sido distinta sin pasar por vision.md + context-map.md? |
| estrategia-desarrollo-bc.md | ¿El orden de desarrollo por Core/Supporting/Generic difiere del orden intuitivo? |

Estas preguntas se documentan en la retrospectiva de Semana 0 dentro de BL-000.

---

*Documento creado: 2026-03-15 — Semana 0*
*Mantenido por: Claude Cowork*
