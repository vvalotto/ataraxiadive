# Plan del Experimento: AtaraxiaDive como Laboratorio Vivo

**Fecha:** 2026-03-14
**Versión:** 1.1 — Corrección: jerarquía Incremento → US → /implement-us
**Propósito:** Desarrollar AtaraxiaDive con el entorno completo (CM + Dev Kit + Software Limpio + IEDD), aprender sistemáticamente, y volcar ese aprendizaje en producción intelectual.

---

## El objetivo real

No es "construir un gestor de torneos de apnea".

El objetivo es **demostrar, con evidencia empírica propia, que es posible desarrollar software con IA manteniendo la memoria del producto viva, la deuda técnica visible, y el conocimiento formalizable**. AtaraxiaDive es el vehículo. El conocimiento producido en el proceso es el producto de fondo.

Hay tres preguntas que este experimento busca responder:

1. ¿El entorno CM + Dev Kit + Software Limpio funciona como sistema integrado o cada herramienta exige fricción de coordinación?
2. ¿IEDD es una metodología que mejora la calidad de las especificaciones o es teoría que no sobrevive el contacto con un proyecto real?
3. ¿Cuánto del conocimiento producido durante el desarrollo se puede capitalizar directamente en material académico sin reescritura?

---

## Los tres horizontes

### Horizonte 1 — Validar (2 a 3 meses)
*SP1 La Performance + SP2 La Competencia*

El objetivo no es tener software funcional. Es validar que el entorno completo funciona para un ciclo real. Al cerrar SP1, tenés BL-001 con métricas reales, 4 US-IEDD procesadas con `/implement-us`, y la primera lectura de ArchitectAnalyst. Eso es suficiente para saber si el experimento tiene futuro.

SP2 confirma que el modelo escala: más aggregates, más interacciones de dominio, más complejidad en las invariantes. Si SP1 fue el "¿funciona?", SP2 es el "¿funciona cuando el dominio se complica?".

**Criterio de éxito del Horizonte 1:** Podés mostrar BL-002 con métricas de calidad, la traceability matrix con al menos 12-15 US trazadas (SP1 tiene ~10 USs, SP2 tiene ~10 USs), y la primera retrospectiva documentada del entorno.

### Horizonte 2 — Construir (4 a 6 meses)
*SP3 El Torneo + SP4 La Plataforma*

El sistema empieza a ser usable. SP3 cierra el ciclo completo del torneo — si en algún momento querés detener el proyecto, SP3 es el punto donde tiene sentido hacerlo. SP4 ataca los atributos de calidad más exigentes: offline, configurabilidad, auditoría. Es donde el entorno se prueba bajo presión real.

**Criterio de éxito del Horizonte 2:** Podés simular un torneo completo de principio a fin. El log de ArchitectAnalyst muestra la evolución de la deuda técnica a través de 4 baselines. Tenés material suficiente para un paper sobre IEDD con evidencia empírica.

### Horizonte 3 — Producir (6 a 12 meses)
*SP5 La Puesta en Marcha + capitalización del conocimiento*

SP5 es la transición a la realidad: un torneo real, usuarios reales, el sistema como herramienta oficial. Y en paralelo: el conocimiento acumulado durante los Horizontes 1 y 2 se transforma en capítulos del libro, módulos del curso, y ponencias.

**Criterio de éxito del Horizonte 3:** AtaraxiaDive se usa en un torneo real. Y el proceso de construirlo produjo al menos: 3 capítulos del libro DDD con ejemplos de producción, 1 caso de estudio completo para la materia IS, y 1 artículo o ponencia sobre IEDD + IA.

---

## La jerarquía de trabajo

Antes del ritmo, conviene tener clara la jerarquía de unidades de trabajo. Son tres niveles con responsables distintos:

```
Subproyecto (SP1–SP5)
  └── Incremento (ej: 1.2 "El dominio habla")
        └── Historia de Usuario (ej: US-1.2.1, US-1.2.2, US-1.2.3)
              └── /implement-us → 10 fases por US
```

- El **subproyecto** cierra cuando todos sus incrementos están terminados → genera una Baseline.
- El **incremento** cierra cuando todas sus USs están implementadas **y** la DoD se cumple como conjunto. La DoD del incremento no es la suma de las DoDs individuales — es una condición de integración observable (ej: "el juez puede registrar 5 performances desde el celular en PostgreSQL"). El incremento puede tener de 2 a 5 USs según su complejidad.
- La **Historia de Usuario** es la unidad del Dev Kit. Cada US se procesa con `/implement-us` y sus 10 fases. Corresponde a una función cohesiva del sistema (un aggregate, un caso de uso, una capacidad observable).

Por ejemplo, el Incremento 1.2 "El dominio habla" se descompone en:

| US | Descripción | Aggregate |
|----|-------------|-----------|
| US-1.2.1 | Definir entidad Performance con invariantes | Performance |
| US-1.2.2 | Registrar performance en el Event Store | Performance |
| US-1.2.3 | Asignar tarjeta y cerrar performance | Performance |

Las tres USs se implementan con `/implement-us`. El incremento 1.2 cierra cuando las tres están hechas **y** el test de integración del flujo completo pasa.

---

## El ritmo de trabajo

El experimento funciona con dos cadencias paralelas:

### Sesión Cowork (estratégica) — 2 a 3 veces por semana, 30-60 min
Es el momento de pensar antes de construir. Las actividades típicas son:
- Descomponer el próximo incremento en USs e identificar sus aggregates
- Redactar la US-IEDD de cada US (invariantes, pre/post, BDD)
- Revisar los reportes de `/implement-us` completados y decidir si el incremento cierra
- Registrar un ADR cuando surge una decisión de diseño
- Actualizar la traceability matrix
- Reflexionar sobre lo que aprendió el entorno en el incremento anterior

### Sesión Code (táctica) — cuando hay energía, sin fecha fija
Es el momento de construir. Las actividades típicas son:
- Ejecutar `/implement-us` en una US (las 10 fases, una US por vez)
- Resolver los quality gates que fallen
- Correr los tests y verificar que la US cumple su criterio de aceptación
- Hacer el commit final con el Conventional Commit correcto
- Una vez terminadas todas las USs de un incremento: correr el test de integración de la DoD

### Retrospectiva de subproyecto — al cerrar cada SP
Es el momento de evaluar el entorno, no solo el software. Se responde:
- ¿Qué funcionó del entorno? ¿Qué generó fricción innecesaria?
- ¿Las métricas de ArchitectAnalyst reflejan lo que se percibe subjetivamente?
- ¿Qué ajustes hay que hacer al entorno para el siguiente SP?
- ¿Qué aprendizaje de dominio se puede formalizar ahora?

Esta retrospectiva se documenta en `.cm/baselines/BL-NNN.md` y también alimenta directamente el diario del libro.

---

## Plan detallado: Horizonte 1

### Semana 0 — Inicialización (una sesión Cowork de ~90 min)

Esto es lo que hay que hacer una sola vez para que todo funcione:

| Tarea | Herramienta | Output |
|-------|-------------|--------|
| Crear repositorio `ataraxiadive` con estructura entorno-ia-dev | Cowork | Repo inicializado con CLAUDE.md, README, CHANGELOG |
| Decidir stack backend (FastAPI recomendado) | Cowork | ADR-002 registrado |
| Escribir ADR-001 (Event Sourcing), ADR-003 (offline-first), ADR-004 (reglas como datos) | Cowork | 4 ADRs en `docs/adr/` |
| Registrar BL-000 (baseline pre-código) | Cowork | BL-000.md en `.cm/baselines/` |
| Instalar claude-dev-kit y configurar customization `ataraxiadive-fastapi.json` | Code | `skills/` disponibles en el repo |
| Configurar software_limpio pre-commit (codeguard) | Code | `.pre-commit-config.yaml` + `pyproject.toml` |

### Incremento 1.1 — Fundación técnica
*DoD: docker-compose up, health-check responde 200, estructura de capas visible en el repo*

Este incremento es principalmente infraestructura. Tiene una sola US:

| US | Descripción |
|----|-------------|
| US-1.1.1 | Crear la estructura del proyecto con las 4 capas y el entorno de desarrollo funcional |

**Cowork:** Redactar US-IEDD-1.1.1. Acá no hay aggregate — el "dominio" es la arquitectura misma. La postcondición es estructural: las 4 carpetas existen, el proyecto levanta, el health-check responde.

**Code:** `/implement-us US-1.1.1` → `docker-compose.yml` + `main.py` + estructura de capas + test del health-check.

**Cowork (cierre):** Verificar DoD. Entry en traceability matrix. Commit `feat(infra): foundation CI-011`.

### Incremento 1.2 — El dominio habla
*DoD: test automatizado que recorre el flujo completo crear → marcar → asignar tarjeta → verificar estado en Event Store*

Este es el primer incremento con lógica de dominio real. Se descompone en 3 USs:

| US | Descripción | Aggregate |
|----|-------------|-----------|
| US-1.2.1 | Modelar entidad Performance con sus invariantes y estado | Performance |
| US-1.2.2 | Implementar caso de uso RegistrarPerformance con Event Store | Performance |
| US-1.2.3 | Asignar tarjeta (blanca/roja/amarilla) y cerrar performance | Performance |

**Cowork:** Redactar las 3 US-IEDD usando la plantilla `docs/iedd/US-IEDD-template.md`. El lenguaje ubicuo (AP, RP, tarjeta blanca, black-out) debe estar en el glosario de cada US.

**Code:** `/implement-us US-1.2.1`, luego `US-1.2.2`, luego `US-1.2.3`. Cada una con sus 10 fases. El orden importa: el aggregate antes que el caso de uso.

**Cowork (cierre):** Correr DesignReviewer. ¿El dominio importa infraestructura? Si sí, es una RFC. Verificar DoD con el test de integración del flujo completo.

### Incremento 1.3 — El juez ve y toca
*DoD: interfaz visible en celular real con los 6 botones del flujo, sin conexión al backend aún*

Primer incremento de presentación. El Dev Kit cubre BDD y documentación; la implementación React+PWA se hace a mano o con perfil `generic-python` adaptado para el BDD de la interfaz.

| US | Descripción |
|----|-------------|
| US-1.3.1 | Pantalla del juez: mostrar atleta con datos hardcodeados |
| US-1.3.2 | Flujo de 6 botones: estados visuales y transiciones en pantalla |

**Cowork:** La especificación formal de estas USs es comportamental: precondición = pantalla cargada, postcondición = cada botón avanza el estado. Los BDD scenarios son los 6 pasos del flujo del juez.

### Incremento 1.4 — Todo conectado
*DoD: juez ejecuta los 6 pasos en el celular, eventos persisten en PostgreSQL, flujo repetible para 3-5 atletas*

Integración full-stack. Puede tener 2 o 3 USs según cómo se divida la conexión frontend-backend-database.

| US | Descripción |
|----|-------------|
| US-1.4.1 | Conectar interfaz del juez al backend (API calls reales) |
| US-1.4.2 | Verificar persistencia end-to-end y flujo con datos de prueba |

**Code:** Las fases 5 y 6 de `/implement-us` (tests de integración y validación BDD) son las más ricas en este incremento.

### Cierre SP1 → BL-001

**Code:**
```bash
architectanalyst src/ --sprint-id BL-001 --format json
```

**Cowork:** Registrar BL-001.md con las métricas reales. Primera retrospectiva del entorno. Preguntas clave:
- ¿Cuánto tiempo tomó cada incremento realmente vs lo estimado?
- ¿El quality gate de Pylint detectó algo útil?
- ¿La US-IEDD mejoró la calidad del código generado respecto a una US clásica?
- ¿Qué fricción generó el entorno que no generó valor?

---

## La matriz de conocimiento

Cada incremento produce conocimiento técnico. Esta tabla muestra cómo ese conocimiento fluye hacia los productos intelectuales de largo plazo:

| Qué se aprende en AtaraxiaDive | → Libro DDD | → Curso IS | → Material Gestión | → Paper IEDD |
|-------------------------------|-------------|------------|---------------------|--------------|
| Performance aggregate + invariantes | Cap. "Aggregates con invariantes reales" | Caso práctico semana 4 | — | Ejemplo RF→invariante→BDD |
| Event Sourcing para auditoría | Cap. "Domain Events como memoria del dominio" | Caso práctico semana 8 | — | — |
| Máquina de estados del Torneo | Cap. "State machines como ubiquitous language" | Caso práctico semana 6 | Ejemplo de WIP y flujos | — |
| Reglas como datos (disciplinas) | Cap. "Bounded Context Configuración" | Caso práctico semana 10 | — | — |
| Offline-first + sync | Cap. "Arquitectura como consecuencia del dominio" | — | Gestión de riesgos técnicos | — |
| Métricas ArchitectAnalyst BL-001 a BL-004 | — | Lab: medir deuda técnica | Tendencias de calidad en proyectos ágiles | Evidencia empírica IEDD |
| Retrospectivas de entorno | — | — | Reflexiones del PMBOK v7 principio X | Friction analysis en entornos IA |

La regla es: **no reescribir**. Lo que se escribe en los ADRs, las retrospectivas, y los reportes de `/implement-us` es materia prima directa para los productos intelectuales. El libro de DDD no se escribe desde cero — se ensambla a partir de los artefactos del proyecto.

---

## Los indicadores del experimento

Al terminar cada subproyecto, estas son las preguntas que merecen respuesta documentada:

**Sobre el entorno:**
- Tiempo promedio por incremento (horas)
- Proporción del tiempo en Cowork vs Code
- Número de RFCs abiertos (indica inestabilidad de requerimientos)
- Número de quality gates fallidos en primer intento

**Sobre la calidad del software:**
- Tendencia de Pylint score a través de las baselines
- Tendencia de complejidad ciclomática promedio
- Cobertura de tests por capa (dominio debe ser > 90%)
- Número de violations hexagonales detectadas por DesignReviewer

**Sobre IEDD:**
- ¿Las US-IEDD con invariantes formales produjeron menos defectos en Phase 7 que las US clásicas?
- ¿Los BDD scenarios derivados de los invariantes cubrieron casos que una especificación informal habría omitido?
- ¿Cuántas veces el proceso IEDD reveló una ambigüedad en los RFs que de otra forma habría llegado al código?

---

## El primer paso concreto

Antes de cualquier código, hay una sola decisión que desbloquea todo lo demás:

**¿FastAPI o Node.js para el backend?**

La respuesta determina qué perfil del Dev Kit usar, si Software Limpio cubre todo el backend o solo el dominio, y qué experiencia de desarrollo vas a tener. La recomendación del análisis es FastAPI — el ecosistema Python queda completo y la experiencia de desarrollo es consistente. Pero es tu decisión.

Una vez tomada esa decisión, la Semana 0 puede arrancar.

---

*Este plan es un documento vivo. Se revisa al cerrar cada subproyecto.*
*Análisis previos: ANALISIS-ATARAXIADIVE.md, ANALISIS-IEDD.md, ANALISIS-INTEGRACION-CLAUDE-DEV-KIT.md, ANALISIS-SOFTWARE-LIMPIO.md*
