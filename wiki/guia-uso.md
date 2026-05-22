---
title: "Guía de Uso — LLM Wiki AtaraxiaDive"
type: meta
last_updated: "2026-05-22"
---

# Guía de Uso — LLM Wiki AtaraxiaDive

> Para el usuario humano que interactúa con el wiki a través del LLM.
> El wiki responde preguntas sobre el proyecto usando sus páginas sintetizadas —
> sin necesidad de leer código fuente ni documentación técnica directamente.

---

## Cómo hacer una consulta

Preguntás en lenguaje natural. El LLM identifica la vista relevante, lee las páginas
necesarias del wiki y responde con citas. No necesitás saber qué vista usar ni qué
páginas leer.

**Ejemplos de consultas válidas:**

```
¿Qué se rompe si cambio el esquema del event store?
¿Qué ADRs tengo que revisar antes de agregar un nuevo tipo de tarjeta?
¿Qué tests cubren el flujo de inscripción de atleta?
¿Cuál es la secuencia de pantallas para llegar a Mis Datos?
¿Qué aprendimos sobre Event Sourcing para el libro DDD?
¿Qué BCs se ven afectados si cambio el contrato JWT de Identidad?
¿Esta feature ya está implementada?
```

No hace falta contexto previo — el wiki tiene el estado del proyecto sintetizado.

---

## Las seis vistas: qué tipo de pregunta responde cada una

| Vista | Preguntá desde acá cuando... | Ejemplos |
|-------|------------------------------|---------|
| **Impacto** | Vas a tocar algo y querés saber qué se rompe | *"¿Qué impacta cambiar X?"*, *"¿Qué BCs dependen de Y?"* |
| **Decisiones** | Querés entender por qué el sistema está construido así, o qué ADRs aplican a una nueva decisión | *"¿Por qué SQLite?"*, *"¿Qué ADRs aplican si agrego notificaciones push?"* |
| **Trazabilidad** | Querés rastrear un requerimiento hasta su implementación y tests | *"¿Qué US implementa RF-EJ-04?"*, *"¿Qué tests cubren el registro de performance?"* |
| **Dominio** | Querés entender qué hace el sistema o qué significa un concepto | *"¿Cuántos BCs hay?"*, *"¿Qué es una Grilla?"*, *"¿Qué hace BC Competencia?"* |
| **Salud** | Querés saber el estado de calidad, deuda técnica o inconsistencias | *"¿Cuál es la distancia arquitectónica de BC Registro?"*, *"¿Qué gaps detectó el último lint?"* |
| **Investigación** | Querés conectar aprendizajes del proyecto con el libro, paper o curso | *"¿Qué evidencia tenemos de IEDD para el paper?"*, *"¿Qué casos sirven para el curso semana 4?"* |

No necesitás mencionar la vista — el LLM la detecta solo por el tipo de pregunta.

---

## Tres operaciones de mantenimiento

### 1. Ingestar una nueva fuente

Cuando hay algo nuevo en el proyecto que el wiki todavía no conoce.

```
/wiki-ingest docs/adr/ADR-023-nuevo-adr.md
/wiki-ingest .cm/baselines/BL-007.md
/wiki-ingest docs/reports/US-8.1.1.md
```

O en lenguaje natural:
```
Ingestá el nuevo ADR-023 sobre autenticación OAuth.
Actualizá el wiki con el baseline BL-007.
Incorporá el reporte de cierre del SP8.
```

El LLM lee la fuente, determina qué páginas del wiki crear o actualizar y hace los commits.
Una fuente típica toca entre 5 y 15 páginas.

### 2. Lint periódico

Auditoría de salud del wiki. Detecta inconsistencias, gaps de trazabilidad y páginas
desactualizadas. Genera una nueva página `wiki/salud/lint-NNN.md`.

```
/wiki-lint
```

**Cuándo ejecutarlo:** al cierre de cada SP, o cada vez que sospechés que el wiki
quedó desactualizado respecto al proyecto real.

### 3. Consulta libre

Cualquier pregunta sobre el proyecto. Ver sección anterior.

---

## Triggers naturales para mantener el wiki actualizado

| Evento en el proyecto | Acción wiki |
|-----------------------|-------------|
| Nuevo ADR creado | `/wiki-ingest docs/adr/ADR-NNN-....md` |
| Nuevo baseline (`BL-*.md`) | `/wiki-ingest .cm/baselines/BL-NNN.md` |
| Cierre de Sprint | `/wiki-ingest` de reportes de US + HITOs del SP |
| Nuevo reporte de US | `/wiki-ingest docs/reports/US-X.Y.Z.md` |
| Vas a tocar un BC o componente | Consultá el wiki primero: *"¿qué impacta cambiar X?"* |
| Cada 1-2 SPs | `/wiki-lint` |

---

## Qué esperar como respuesta

El LLM responde citando las páginas del wiki que usó. Cada respuesta incluye:

- La respuesta directa a la pregunta
- Las páginas del wiki consultadas (típicamente 1-3)
- Los ADRs o US relevantes si aplica
- Gaps detectados si la pregunta reveló algo que el wiki no tiene

Si el wiki no tiene información sobre algo, el LLM lo dice explícitamente —
no inventa respuestas.

---

## Qué NO pedirle al wiki

| Pedido | Por qué no | Alternativa |
|--------|-----------|------------|
| *"Implementá esta feature"* | El wiki es de consulta, no de implementación | Usar `/implement-us` en el flujo IEDD |
| *"Leé el archivo src/X/Y.py"* | El wiki ya tiene la síntesis del código; leer fuente directa es más lento | Preguntar al wiki sobre el componente |
| *"¿Qué cambió en el último commit?"* | El wiki no monitorea git en tiempo real | `git log` o `git diff` |
| *"Generame el reporte de calidad"* | Los reportes de calidad son generados por las herramientas (DesignReviewer, ArchitectAnalyst) | Ejecutar las herramientas y luego ingestar el resultado |

---

## Componentes de alto riesgo — consultá antes de tocar

Estos componentes tienen riesgo **muy alto** documentado en `wiki/impacto/`.
Antes de modificarlos, consultá el wiki para entender el alcance:

| Componente | Riesgo | Página de referencia |
|-----------|--------|---------------------|
| `EventStorePort` | Muy alto — impacta 2 BCs con ES + hash SHA-256 | `[[event-store-port]]` |
| BC Identidad / JWT claims | Muy alto — 3 BCs Conformist dependen del contrato | `[[bc-identidad]]` |
| `Categoria` (shared value object) | Medio — ADR-022 pendiente; imports en Resultados | `[[categoria-shared]]` |
| `AtletaNombrePort` / `registro.db` | Medio — lectura cross-BC directa en Competencia y Resultados | `[[atleta-nombre-port]]` |

---

## Resultado del POC (mayo 2026)

El wiki fue evaluado con 4 consultas de prueba respondidas sin acceso a código fuente:

| Métrica | Resultado |
|---------|-----------|
| Consultas respondidas sin código | 4 / 4 |
| Páginas leídas promedio por consulta | 1.5 |
| Gaps detectados honestamente | 1 (push notifications sin ADR) |

Ver `[[evaluacion-poc]]` para el detalle completo.

---

*Guía generada: 2026-05-22 — Wiki branch `wiki`, 246 páginas operativas*
