# AtaraxiaDive como Caso de Estudio del Entorno IA-Dev

**Fecha:** 2026-03-14
**Estado:** Borrador inicial
**Versión:** 1.0
**Contexto:** Análisis de AtaraxiaDive como sandbox para experimentar el entorno completo: CM Framework + Claude Dev Kit + Software Limpio + IEDD

---

## 1. El Proyecto en Síntesis

AtaraxiaDive es una plataforma web para gestión de torneos de apnea (freediving). Su dominio es pequeño pero técnicamente rico: tiene un ciclo de vida de torneo bien definido, reglas de negocio configurables, integridad de datos crítica, y una interfaz de usuario con restricciones severas (juez con celular, posiblemente sin conexión, bajo presión).

Cuatro documentos forman la base actual:

| Documento | Contenido | Estado |
|-----------|-----------|--------|
| Torneos de Apnea | Descripción del dominio: fases, roles, flujos | Completo |
| Arquitectura de Referencia v1 | Hexagonal, Event Sourcing, offline-first, 6 aggregates | Completo |
| Atributos de Calidad v1 | 9 áreas con IDs AC-XX-NN, métricas específicas | Completo |
| Estrategia de Desarrollo v2 | 5 subproyectos, 22 incrementos con DoD binaria | Completo |
| Requerimientos Funcionales v1 | Cuestionario de elicitación con 48 preguntas/respuestas | ~60% definido |

El sistema tiene un desarrollador: Victor. Horizonte: 2026, sin fecha fija.

---

## 2. Riqueza del Dominio para el Experimento

AtaraxiaDive es un caso de estudio excepcionalmente bueno. Estos son los motivos:

### 2.1 El dominio es conocido de primera mano

Victor practica apnea. Conoce las reglas, los roles, la dinámica de una competencia. Esto elimina la ambigüedad de dominio — el riesgo más frecuente en proyectos académicos donde el desarrollador especula sobre el negocio. Aquí hay un experto de dominio que también es el desarrollador.

### 2.2 Tiene lógica de negocio real y no trivial

El dominio no es CRUD. Tiene:
- Máquina de estados con restricciones (7 estados, transiciones con reglas, incluyendo retroceso)
- Reglas de negocio configurables como datos (no hardcoded): disciplinas, categorías, penalizaciones
- Invariantes de agregado verificables: un atleta no puede competir sin anuncio; un anuncio no puede modificarse una vez registrado; el cierre de disciplina es irreversible
- Integridad criptográfica: SHA-256 al cerrar disciplina para prevenir manipulación de resultados

Esto lo convierte en terreno fértil para IEDD: hay un lenguaje ubicuo real, invariantes formalizables, y eventos de dominio significativos.

### 2.3 Los atributos de calidad son exigentes y medibles

No son aspiracionales. Están especificados con IDs y criterios concretos:

- **AC-DS-01:** Respuesta ≤ 500ms en tiempo de competencia
- **AC-DS-02:** 50 usuarios concurrentes (20 atletas + jueces + organizador)
- **AC-DS-03:** Offline obligatorio para la interfaz del juez
- **AC-US-01:** Flujo del juez en máximo 6 toques
- **AC-SG-04:** Hash SHA-256 al cerrar disciplina

Estos criterios se pueden automatizar con software_limpio en las fases adecuadas.

### 2.4 El modelo de desarrollo ya está alineado con el entorno

La estrategia de desarrollo v2 es naturalmente compatible con el framework sin adaptaciones forzadas:
- Subproyectos = Baselines (BL-001 a BL-005)
- Incrementos = Historias de Usuario implementadas con `/implement-us`
- DoD binaria = criterio de merge en DesignReviewer
- Mini-retrospectiva al cerrar incremento = ArchitectAnalyst snapshot

---

## 3. Mapa de Integración con el Entorno Completo

### 3.1 CM Framework → AtaraxiaDive

```
CM Artifact          ↔  AtaraxiaDive Concepto
──────────────────────────────────────────────
BL-001               ↔  SP1 completo: La Performance
BL-002               ↔  SP2 completo: La Competencia
BL-003               ↔  SP3 completo: El Torneo
BL-004               ↔  SP4 completo: La Plataforma
BL-005               ↔  SP5 completo: La Puesta en Marcha

RFC-NNN              ↔  Cambio a un incremento en curso o reorder de backlog
ADR-001              ↔  Decisión de Event Sourcing (ya tomada, documentar)
ADR-002              ↔  Decisión de stack (React PWA + PostgreSQL + Node/FastAPI)
ADR-003              ↔  Decisión de offline-first con IndexedDB
ADR-004              ↔  Disciplinas como datos configurables (vs código)

Traceability Matrix:
  RF-EJ-01 → Incremento 2.3 (andariveles) → test_competencia_andariveles.feature
  AC-SG-04 → Incremento 4.5 (hash) → test_integridad_disciplina.feature
```

La estructura de 5 subproyectos ya anticipó la granularidad de baselines. No hay que inventar nada: cada subproyecto cerrado ES una baseline.

### 3.2 Claude Dev Kit → AtaraxiaDive

El skill `/implement-us` trabaja con un perfil que define el stack. AtaraxiaDive tiene un stack no cubierto directamente por los perfiles actuales (React + FastAPI/Node + PostgreSQL), pero el análisis de integración previo identificó esto:

**Perfil recomendado para usar: `fastapi-rest`** (si el backend es Python/FastAPI) o `generic-python` para el dominio.

Pero la contribución mayor del Dev Kit es el flujo de trabajo fase a fase:

```
US-IEDD de un incremento
       ↓
Phase 0: Validar contexto (¿aggregate afectado? ¿bounded context?)
Phase 1: BDD/Gherkin desde los invariantes del dominio apnea
Phase 2: Plan de implementación en 4 capas (domain/application/infra/presentation)
Phase 3: Código — la capa de dominio primero (hexagonal)
Phase 4: Tests unitarios del aggregate
Phase 5: Tests de integración (event store + read model)
Phase 6: Validación BDD (steps.py conectan con la app real)
Phase 7: Quality Gates (Pylint, complejidad, cobertura)
Phase 8: Documentación (CHANGELOG, ADR si aplica)
Phase 9: Reporte → entrada en la Traceability Matrix
```

Cada incremento de la estrategia v2 tiene una DoD tan clara que se puede traducir directamente en los criterios de aceptación de la US-IEDD. Por ejemplo:

**Incremento 1.2 → US-IEDD:**
```
Como juez
Quiero registrar una performance de punta a punta
Para que quede persistida en el Event Store con integridad

Precondición: Atleta inscripto, Competencia en estado Ejecución
Postcondición: Evento PerformanceRegistrada persiste en event_store;
               Read model actualizado; marca y tarjeta válidas
Invariante: Una vez asignada tarjeta blanca, la performance no puede modificarse
Eventos: PerformanceCreada, MarcaAsignada, TarjetaAsignada
```

### 3.3 Software Limpio → AtaraxiaDive

Los tres agentes tienen un rol específico en el ciclo de vida:

```
Nivel         Agente              Cuándo                Qué verifica en AtaraxiaDive
──────────────────────────────────────────────────────────────────────────────────────
Pre-commit    CodeGuard           Cada commit            PEP8, complejidad de reglas
                                                         de negocio, seguridad básica
PR/Merge      DesignReviewer      Cada incremento        Dependencias hexagonales
                                  terminado              (¿dominio importa infra?),
                                                         acoplamiento entre aggregates
Sprint/BL     ArchitectAnalyst    Al cerrar un SP        Tendencias de deuda técnica,
              --sprint-id BL-NNN  (baseline)             mantenibilidad, cobertura

```

La regla de hexagonal architecture es particularmente relevante: DesignReviewer puede detectar si `domain/` importa algo de `infrastructure/` — una violación de la arquitectura de referencia. Esto es exactamente el tipo de guarda automático que tiene valor en un proyecto solitario donde nadie más hace code review.

Para SP1 (La Performance), el umbral mínimo razonable es:
- Pylint ≥ 8.0 en capa de dominio
- Cobertura ≥ 85% en dominio + application
- Cero imports de infraestructura en dominio

### 3.4 IEDD → AtaraxiaDive

AtaraxiaDive es casi un caso de uso diseñado a medida para demostrar IEDD:

```
Capa IEDD            Artefacto AtaraxiaDive
────────────────────────────────────────────
Dominio              "Torneos de Apnea.docx":
                     Roles, fases, vocabulario (AP, OT, DNS, black-out, brevet)

Modelo (DDD)         Arquitectura de Referencia:
                     6 aggregates explícitos, 9 domain events,
                     Ubiquitous Language implícito

Especificación       Requerimientos Funcionales v1:
                     48 preguntas elicitadas → respuestas que son pre/postcondiciones
                     (ejemplo: RF-PR-03: "¿puede modificarse un anuncio?" → "No"
                      = invariante: AnnounceModified después de Registered → PROHIBIDO)

IA como traductor    Claude Dev Kit Phase 1+2:
                     Convierte la US-IEDD en BDD scenarios + plan de implementación

Arquitectura         Arquitectura de Referencia:
                     Hexagonal, Event Sourcing, offline-first = consecuencias
                     de los invariantes de dominio (no capricho técnico)

Implementación       Código resultante de /implement-us
```

Lo que hace AtaraxiaDive especialmente valioso para IEDD es que el RF v1 tiene la forma de cuestionario con respuestas — exactamente el tipo de diálogo que produce especificaciones verificables. Por ejemplo:

| RF | Pregunta | Respuesta | Invariante IEDD |
|----|----------|-----------|-----------------|
| RF-PR-03 | ¿Puede modificarse un anuncio? | No | `AnnouncementLocked` luego de `AnnouncementRegistered` |
| RF-EJ-02 | ¿Tiempo de espera para DNS? | Sin espera, DQ | `AthleteStatus.DNS` si no se presenta al OT |
| RF-PM-03 | ¿Cómo se resuelven empates? | Mismo puesto y mismos puntos | `RankingPosition` calcula: igual marca → igual posición |

Cada respuesta en el cuestionario RF es una especificación en lenguaje natural que IEDD formaliza como precondición, postcondición, o invariante.

---

## 4. Tensiones e Incertidumbres

### 4.1 El stack backend no está decidido

La Arquitectura de Referencia menciona "Node.js o FastAPI". Esta decisión tiene impacto en qué perfil del Dev Kit usar y cómo configurar Software Limpio (que actualmente solo analiza Python).

**Recomendación:** Decidir el backend antes de SP1. Si es FastAPI → el ecosistema Python queda completamente cubierto. Si es Node.js → Software Limpio no aplica directamente al backend (sí al dominio si se modela en Python separado).

**ADR propuesto:** ADR-002: Decisión de backend — FastAPI vs Node.js

### 4.2 Los RFs pendientes no bloquean SP1 pero sí SP4

Hay ~15 ítems marcados como "Pendiente" en el RF v1 (códigos de penalización RF-EJ-04, integración FAZ RF-IG-01..04, fórmula de puntos RF-PM-01). Ninguno afecta SP1 ni SP2. Afectan SP4 y SP5.

El modelo de incrementos es antifrágil respecto a esto: se avanza con lo conocido y los "Pendiente" se resuelven cuando se llega a ese incremento. La configurabilidad de reglas como datos (AC-CF-XX) es la respuesta arquitectural a esta incertidumbre.

### 4.3 El perfil dev kit no existe para este stack

No hay perfil `fastapi-hexagonal` ni `react-pwa` en el Dev Kit actual. El análisis de integración anterior identificó que `fastapi-rest` es el más cercano, pero la arquitectura hexagonal tiene diferencias con el estilo layered del perfil.

**Solución propuesta:** Crear un customization JSON `ataraxiadive-fastapi.json` que adapte el perfil `fastapi-rest` a la arquitectura hexagonal de AtaraxiaDive. Esto sería la primera contribución real al Dev Kit desde el sandbox.

### 4.4 Software Limpio solo analiza Python

Si el backend es FastAPI/Python, todos los agentes aplican. Si es Node.js, CodeGuard y DesignReviewer no cubren el backend. El dominio podría modelarse primero en Python (para experimentar IEDD), con la capa de presentación y parte de infraestructura en JavaScript.

Esta dualidad puede ser interesante desde el punto de vista académico: modelar el dominio en Python con Software Limpio, y el frontend/offline en JavaScript. El Event Store en PostgreSQL sirve a ambos.

---

## 5. Propuesta de Experimento SP1: La Performance

SP1 es el incremento ideal para arrancar el experimento completo. Es el "walking skeleton": valida arquitectura, Event Sourcing, y la interfaz del juez en una sola corrida. Y es suficientemente pequeño (4 incrementos) para completarse en pocas semanas.

### Secuencia experimental propuesta

```
┌─────────────────────────────────────────────────────────────────┐
│ FASE 0: Inicialización del Repositorio                          │
│                                                                  │
│ [Cowork]                                                         │
│ 1. Crear repo ataraxiadive con estructura entorno-ia-dev        │
│ 2. Crear CLAUDE.md con convenciones del proyecto                │
│ 3. Registrar BL-000 (baseline inicial, pre-código)              │
│ 4. Crear ADR-001 (Event Sourcing), ADR-002 (stack), ADR-003     │
│ 5. Instalar claude-dev-kit (copy/link de skills/)               │
│ 6. Configurar software_limpio (pre-commit hook, pyproject.toml) │
└─────────────────────────────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────────────────────────────┐
│ INCREMENTO 1.1: Fundación técnica                               │
│                                                                  │
│ [Cowork] Redactar US-IEDD-1.1:                                  │
│   - Aggregate: ninguno (es infraestructura)                     │
│   - DoD → criterios de aceptación formales                      │
│   - BDD: docker-compose up → health-check responde 200         │
│                                                                  │
│ [Code] /implement-us US-1.1                                     │
│   Phase 0: validar contexto                                     │
│   Phase 1: feature file (health-check.feature)                  │
│   Phase 2: plan (estructura de capas)                           │
│   Phase 3: código (docker-compose + main.py + health endpoint)  │
│   Phase 4-6: tests                                              │
│   Phase 7: quality gates                                        │
│   Phase 8-9: docs + reporte                                     │
│                                                                  │
│ [Cowork] Registrar cierre: merge, CHANGELOG, tracking →         │
│   traceability matrix entry                                     │
└─────────────────────────────────────────────────────────────────┘
          ↓ (× 3 para 1.2, 1.3, 1.4)
┌─────────────────────────────────────────────────────────────────┐
│ CIERRE SP1 → BASELINE BL-001                                    │
│                                                                  │
│ [Cowork]                                                         │
│ - Correr ArchitectAnalyst --sprint-id BL-001                    │
│ - Registrar métricas en BL-001.md                               │
│ - Mini-retrospectiva: ¿qué funcionó del entorno?                │
│ - Evaluar: ¿ajustar convenciones para SP2?                      │
└─────────────────────────────────────────────────────────────────┘
```

### US-IEDD de ejemplo: Incremento 1.2 "El dominio habla"

```markdown
# US-IEDD-1.2: Registrar Performance con Event Sourcing

**Como** juez de una competencia de apnea
**Quiero** registrar una performance (marca + tarjeta) en el sistema
**Para que** quede persistida con integridad en el Event Store

---
## Contexto de Aggregate
- Aggregate Root: `Performance`
- Bounded Context: Competencia
- Aggregates relacionados: `Atleta` (read), `Competencia` (owner)

## Lenguaje Ubicuo
- **AP (Announced Performance):** marca declarada antes de competir
- **RP (Realized Performance):** marca efectivamente lograda
- **Tarjeta blanca:** performance válida
- **Tarjeta roja:** descalificación
- **Black-out:** pérdida de conciencia → tarjeta roja automática

## Invariantes
1. Una performance sin tarjeta asignada está en estado PENDIENTE
2. Una vez asignada tarjeta blanca, la performance no puede modificarse
3. Un black-out produce automáticamente tarjeta roja
4. La RP puede ser menor al AP (el atleta no completa su anuncio)

## Especificación Formal
**Precondición:** Competencia.estado == EJECUCION ∧ Atleta.inscripto == true
**Postcondición:** event_store contiene [PerformanceCreada, MarcaAsignada, TarjetaAsignada];
                   read_model.performance.estado == COMPLETADA
**Eventos de dominio:** PerformanceCreada, MarcaAsignada, TarjetaBlancaAsignada | TarjetaRojaAsignada
**Excepciones:** AtletaNoInscripto, CompetenciaNoEnEjecucion, MarcaNegativa

## Ejemplo Concreto
Atleta: Carlos Méndez, DNF, AP: 60.5m
Flujo: Juez crea performance → registra RP: 58.3m → asigna tarjeta blanca
Resultado en event_store:
  { event: "PerformanceCreada", atleta_id: "CM-001", competencia_id: "DNF-2026-A" }
  { event: "MarcaAsignada", rp: 58.3, unidad: "metros" }
  { event: "TarjetaBlancaAsignada" }

## BDD Scenarios

Scenario: Juez registra performance válida
  Given una competencia DNF en estado EJECUCION
  And el atleta Carlos Méndez tiene AP de 60.5m
  When el juez registra RP de 58.3m y asigna tarjeta blanca
  Then el event_store contiene 3 eventos para esa performance
  And el read_model muestra la performance como COMPLETADA con marca 58.3m

Scenario: Black-out produce tarjeta roja automática
  Given una competencia STA en estado EJECUCION
  When el juez registra un black-out para el atleta
  Then el sistema asigna tarjeta roja automáticamente
  And la performance queda en estado DESCALIFICADA

Scenario: Intento de modificar performance ya cerrada
  Given una performance con tarjeta blanca asignada
  When el sistema intenta modificar la marca
  Then se lanza PerformanceCerradaException
  And el event_store no contiene eventos adicionales
```

---

## 6. Lo Que AtaraxiaDive Aporta al Ecosistema (Bidireccionalidad)

El sandbox no es solo un proyecto para "probar" las herramientas. Es también un generador de mejoras para el ecosistema:

### 6.1 Para Claude Dev Kit
- Descubrimiento de que `fastapi-rest` necesita variante hexagonal → **nuevo customization `ataraxiadive-fastapi.json`**
- El Event Sourcing como patrón no está en ningún perfil actual → posible fase 3 adicional: "Event Store setup"
- Los 22 incrementos son casos de uso reales para testear la calidad del skill

### 6.2 Para Software Limpio
- AtaraxiaDive tiene una regla arquitectural verificable mecánicamente: _"dominio no importa infraestructura"_. Esto es candidato a un **check custom de DesignReviewer**: `HexagonalBoundaryCheck`
- El hash SHA-256 de cierre de disciplina puede verificarse con un check de `CodeGuard`: _"¿está el hash implementado antes de cerrar la disciplina?"_

### 6.3 Para IEDD
- Los 48 RFs del cuestionario son el corpus perfecto para demostrar que **preguntas de elicitación = especificaciones en embrión**. Se puede publicar la transformación RF → invariante → BDD como ejemplo docente
- AtaraxiaDive tiene un ubiquitous language real (AP, OT, DNS, black-out, brevet) que puede usarse como ejemplo en el libro de DDD

### 6.4 Para el libro de DDD
El capítulo sobre Domain Events tiene en AtaraxiaDive un ejemplo de producción:
- `PerformanceCreada` → `MarcaAsignada` → `TarjetaAsignada` es una secuencia causal con invariantes
- El Event Sourcing como consecuencia de la necesidad de auditoría (no como elección tecnológica)
- La configurabilidad de reglas como datos es un ejemplo de Shared Kernel entre subdominio Configuración y Competencia

---

## 7. Árbol de CIs para AtaraxiaDive

Para la Traceability Matrix, estos son los Configuration Items relevantes:

```
CI-001   /domain/performance/performance.py       Aggregate Performance
CI-002   /domain/performance/events.py            Domain Events de Performance
CI-003   /domain/competencia/competencia.py       Aggregate Competencia
CI-004   /domain/torneo/torneo.py                 Aggregate Torneo + state machine
CI-005   /application/registrar_performance.py    Use Case RegistrarPerformance
CI-006   /infrastructure/event_store.py           Event Store PostgreSQL
CI-007   /infrastructure/read_model.py            Read Model Projections
CI-008   /presentation/judge_interface/           PWA interfaz juez (React)
CI-009   /presentation/organizer_panel/           Panel organizador (React)
CI-010   /infrastructure/config/discipline.py     Configuración de disciplinas
CI-011   docker-compose.yml                       Entorno de desarrollo
CI-012   pyproject.toml                           Configuración de calidad
CI-013   CLAUDE.md                                Convenciones del proyecto
CI-014   docs/adr/                                Architecture Decision Records
```

---

## 8. Evaluación como Sandbox: Veredicto

AtaraxiaDive es el caso de estudio ideal para el entorno IA-Dev por cinco razones convergentes:

**Razón 1: Dominio rico sin artificialidad.** No es un "sistema de gestión de biblioteca" inventado para el aula. Es un dominio real, con usuarios reales (la federación), con Victor como experto de dominio.

**Razón 2: Escala adecuada.** 22 incrementos es suficiente para experimentar el entorno durante meses sin agotarlo. SP1 (4 incrementos) es suficiente para validar el entorno completo en semanas.

**Razón 3: Alineación sin forzar.** Los subproyectos ya son baselines. Las DoDs ya son criterios de aceptación. El cuestionario RF ya son especificaciones. No hay que adaptar el proyecto al entorno — ya están alineados naturalmente.

**Razón 4: Valor real.** Si el experimento funciona, Victor tiene un software que puede usar para torneos de apnea reales. El sandbox no termina en el cajón.

**Razón 5: Potencial académico.** AtaraxiaDive + el entorno completo = un caso de estudio publicable para las clases de Ingeniería de Software y el libro de DDD. Cada incremento es un ejemplo de clase en vivo.

### Próximos pasos inmediatos

1. **Decidir el stack backend** (ADR-002): FastAPI o Node.js
2. **Crear el repositorio AtaraxiaDive** con la estructura del entorno-ia-dev
3. **Escribir los 4 ADRs fundacionales** (Event Sourcing, stack, offline-first, configurabilidad)
4. **Registrar BL-000** con el inventario de CIs inicial
5. **Redactar US-IEDD-1.1** para arrancar el primer incremento con `/implement-us`

---

*Documentos fuente disponibles en `docs/ataraxiadive/`.*
*Análisis relacionados: ANALISIS-INTEGRACION-CLAUDE-DEV-KIT.md, ANALISIS-SOFTWARE-LIMPIO.md, ANALISIS-IEDD.md*
