---
title: "Vista de Impacto"
type: vista
last_updated: "2026-05-21"
sources:
  - wiki/arquitectura/context-map.md
  - wiki/arquitectura/
  - wiki/decisiones/
---

# Vista de Impacto

> El sistema visto desde las dependencias y el riesgo de cambio.

## Propósito

Responder preguntas sobre qué se ve afectado cuando algo cambia. Mapear los puntos de acoplamiento del sistema, las interfaces críticas y los componentes de mayor riesgo. Es la vista de mayor valor para mantenimiento y la única que el wiki construye por inferencia — no existe como documentación previa en el proyecto.

## Stakeholder principal

Desarrollador planificando una modificación, tech lead evaluando el alcance de una tarea.

---

## Mapa de dependencias del sistema

Fuente: `[[arquitectura/context-map]]`. Las flechas indican dependencia (downstream depende de upstream).

```
Identidad ──Conformist (JWT)──► Torneo
Identidad ──Conformist (JWT)──► Registro
Identidad ──Conformist (JWT)──► Competencia

Torneo ──InscripcionHabilitada──► Registro
Registro ──AtletaNombrePort + participante_id──► Competencia
Competencia ──CompetenciaFinalizada──► Resultados
Torneo ──read-only torneoId──► Resultados

Torneo ──eventos──► Notificaciones
Registro ──eventos──► Notificaciones
Competencia ──eventos──► Notificaciones
Resultados ──eventos──► Notificaciones
```

**Principio de aislamiento:** ningún BC accede directamente a la base de datos de otro. Las integraciones van por puertos y adaptadores contenidos en `infrastructure/` del BC consumidor.

---

## Preguntas características y recorridos

### 1. ¿Qué BCs se ven afectados si cambio el contrato JWT de Identidad?

**Todos los BCs** consumen JWT de Identidad con patrón Conformist. Un cambio en el esquema de claims (`userId`, `rol`) impacta:
- `[[arquitectura/torneo]]` — valida JWT en cada request
- `[[arquitectura/registro]]` — valida JWT en cada request
- `[[arquitectura/competencia]]` — valida JWT en cada request

Notificaciones y Resultados no consumen JWT directamente (son downstream de eventos, no de requests del usuario).

**Recorrido:**
`[[arquitectura/identidad]]` → `[[arquitectura/context-map]]` → `[[ADR-020-modelo-usuarios-roles]]` → BCs afectados

**Riesgo:** cambio de alto impacto transversal. Requiere actualización sincronizada en tres BCs.

---

### 2. ¿Qué se rompe si cambio el evento `CompetenciaFinalizada`?

`CompetenciaFinalizada` es el evento que desencadena el cálculo de rankings en Resultados. Es el acoplamiento más crítico del sistema.

**Consumidores:**
- `[[arquitectura/resultados]]` — fuente de verdad para el ranking final; no puede calcular sin este evento
- `[[arquitectura/notificaciones]]` — puede recibir este evento como trigger (callbacks in-process en SP4)

**Recorrido:**
`[[arquitectura/competencia]]` → `[[ADR-001-event-sourcing-competencia]]` → `[[arquitectura/resultados]]` → `[[arquitectura/context-map]]`

**Riesgo:** alto. Resultados depende estructuralmente de este evento para generar rankings.

---

### 3. ¿Qué impacta un cambio en la interfaz `AtletaNombrePort`?

`AtletaNombrePort` + `AtletaNombreAdapter` son el punto de integración entre Registro y Competencia. Competencia consulta nombres de atletas vía este puerto sin depender del modelo interno de Registro.

**Ubicación esperada:** `src/competencia/infrastructure/adapters/atleta_nombre_adapter.py`

**Impacto de un cambio:**
- Solo `[[arquitectura/competencia]]` — el adaptador está contenido en su `infrastructure/`
- Si cambia el contrato del puerto (no solo la implementación): también los tests de integración del adaptador

**Recorrido:**
`[[arquitectura/registro]]` → `[[arquitectura/context-map]]` sección "Registro → Competencia" → `[[arquitectura/competencia]]` sección "Integraciones"

**Riesgo:** medio. El patrón de puerto/adaptador limita el impacto al BC consumidor. La evolución objetivo es reemplazarlo por evento `AtletaInscripto` + ACL formal.

---

### 4. ¿Qué cambios en el BC Torneo impactan al BC Registro?

Torneo es upstream de Registro. El evento `InscripcionHabilitada` transporta:
- `torneoId`
- `fechaFinInscripcion`
- `disciplinasDisponibles`

Un cambio en cualquiera de estos campos impacta la lógica de Registro que los consume.

**Recorrido:**
`[[arquitectura/torneo]]` → `[[arquitectura/context-map]]` sección "Torneo → Registro" → `[[arquitectura/registro]]`

**Riesgo:** medio. Cambio de contrato de evento requiere migración coordinada.

---

### 5. ¿Cuál es el componente de mayor acoplamiento en el sistema?

**BC Competencia** es el nodo de mayor acoplamiento por densidad de dependencias entrantes y complejidad interna:

| Dependencia | Tipo |
|-------------|------|
| Identidad → Competencia | Conformist (JWT) |
| Registro → Competencia | AtletaNombrePort + participante_id |
| Competencia → Resultados | CompetenciaFinalizada (evento crítico) |
| Competencia → Notificaciones | Eventos de dominio |

Además, concentra: dos aggregates bajo Event Sourcing, el esquema del event store, el hash SHA-256 de auditoría, las reglas de penalización y la interfaz offline del juez.

**Recorrido:**
`[[arquitectura/competencia]]` → `[[ADR-001-event-sourcing-competencia]]` → `[[ADR-008-event-store-sqlite]]` → `[[arquitectura/context-map]]`

---

### 6. Si cambio el esquema del event store, ¿qué se ve afectado?

El esquema de `events` (tabla SQLite) está definido en [[ADR-008-event-store-sqlite]]. Impacta:
- `[[arquitectura/competencia]]` — usa el event store como fuente de verdad
- `[[arquitectura/notificaciones]]` — tiene su propio event store con el mismo patrón
- Migraciones Alembic de ambos BCs (ver [[ADR-009-migraciones-por-bc]])
- El hash SHA-256 ([[ADR-018-hash-sha256-auditoria]]) que opera sobre la secuencia de eventos

**Recorrido:**
`[[ADR-008-event-store-sqlite]]` → `[[ADR-009-migraciones-por-bc]]` → `[[ADR-018-hash-sha256-auditoria]]` → `[[arquitectura/competencia]]` → `[[arquitectura/notificaciones]]`

**Riesgo:** muy alto. Cambio de esquema del event store requiere migración de datos históricos.

---

### 7. Si agrego una nueva disciplina o tipo de tarjeta, ¿qué partes debo revisar?

Las reglas de tarjetas y disciplinas se modelan como datos configurables ([[ADR-004-reglas-como-datos]]). El código no asume un conjunto fijo.

**Partes a revisar:**
- `[[arquitectura/torneo]]` — gestiona el catálogo de disciplinas
- `[[arquitectura/competencia]]` — valida y registra según las reglas vigentes
- `[[ADR-014-penalizaciones-acumulables]]` — lógica de acumulación; ¿el nuevo tipo la sigue?
- Tests BDD en `tests/features/` que asumen disciplinas o tarjetas específicas

**Recorrido:**
`[[ADR-004-reglas-como-datos]]` → `[[ADR-014-penalizaciones-acumulables]]` → `[[arquitectura/torneo]]` → `[[arquitectura/competencia]]`

---

## Interfaces críticas (puntos de mayor riesgo)

| Interfaz / Componente | BCs involucrados | Riesgo de cambio |
|----------------------|-----------------|-----------------|
| JWT / claims de Identidad | Identidad → Torneo, Registro, Competencia | Muy alto (transversal) |
| `CompetenciaFinalizada` (evento) | Competencia → Resultados | Alto (ranking depende de él) |
| Esquema del event store | Competencia, Notificaciones | Muy alto (datos históricos) |
| `AtletaNombrePort` | Registro → Competencia | Medio (contenido en adaptador) |
| `InscripcionHabilitada` (evento) | Torneo → Registro | Medio (contrato de evento) |
| Hash SHA-256 | Competencia → (auditoría externa) | Alto (integridad regulatoria) |

---

## Páginas hub de esta vista

| Página | Por qué es hub |
|--------|----------------|
| `[[arquitectura/context-map]]` | Mapa completo de dependencias entre BCs |
| `[[arquitectura/competencia]]` | BC de mayor complejidad y más dependencias entrantes |
| `[[arquitectura/identidad]]` | BC transversal del que todos dependen vía JWT |
| `[[ADR-008-event-store-sqlite]]` | Define el esquema del componente más crítico |
| `[[ADR-001-event-sourcing-competencia]]` | Justifica la arquitectura del Core Domain |
