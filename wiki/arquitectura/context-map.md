---
title: "Context Map — Integraciones entre Bounded Contexts"
type: arquitectura
last_updated: "2026-05-20"
sources:
  - docs/architecture/03-bounded-contexts.md
  - docs/architecture/20-context-map-integrations.md
---

# Context Map — Integraciones entre Bounded Contexts

## Los seis Bounded Contexts

| BC | Tipo DDD | Persistencia | Responsabilidad |
|----|----------|--------------|-----------------|
| [[competencia]] | Core Domain | Event Sourcing | Ejecución deportiva: grilla, performances, tarjetas |
| [[bc-torneo]] | Supporting | CRUD | Ciclo de vida del torneo y contexto organizativo |
| [[registro]] | Supporting | CRUD | Atletas, inscripciones y participación |
| [[resultados]] | Supporting | CRUD + stream propio | Rankings derivados y publicación |
| [[identidad]] | Generic | CRUD | Usuarios, roles, JWT |
| [[notificaciones]] | Generic | Event Sourcing | Ciclo de vida de notificaciones, idempotencia |

## Diagrama de relaciones

```
Identidad ──Conformist (JWT)──► Torneo
Identidad ──Conformist (JWT)──► Registro
Identidad ──Conformist (JWT)──► Competencia

Torneo ──Customer-Supplier (InscripcionHabilitada)──► Registro
Registro ──Referencia por ID + adaptadores──► Competencia
Competencia ──Customer-Supplier (CompetenciaFinalizada)──► Resultados
Torneo ──Consulta read-only──► Resultados

Torneo ──Eventos de dominio──► Notificaciones
Registro ──Eventos de dominio──► Notificaciones
Competencia ──Eventos de dominio──► Notificaciones
Resultados ──Eventos de dominio──► Notificaciones
```

## Integraciones detalladas

### Identidad → Torneo, Registro, Competencia

**Patrón:** Conformist. Los BCs downstream aceptan el contrato JWT de Identidad sin negociar el modelo.

**Mecanismo:** Validación síncrona del token en cada request. Los BCs downstream no consultan a Identidad en runtime — consumen claims locales (`userId`, `rol`).

### Torneo → Registro

**Patrón:** Customer-Supplier. Torneo upstream, Registro downstream.

**Mecanismo:** Evento de dominio `InscripcionHabilitada`.

**Datos que cruzan la frontera:** `torneoId`, `fechaFinInscripcion`, `disciplinasDisponibles`.

### Registro → Competencia

**Patrón:** Referencia por ID + adaptadores de infraestructura. Evolución objetivo: evento `AtletaInscripto` + ACL formal.

**Mecanismo actual:** Referencias `participante_id` / `atleta_id` en streams y eventos. `AtletaNombrePort` + `AtletaNombreAdapter` consultando `registro.db`.

**Restricción:** El dominio de Competencia no depende del modelo de Registro — solo de IDs estables.

### Competencia → Resultados

**Patrón:** Customer-Supplier.

**Mecanismo principal:** Evento `CompetenciaFinalizada`.

**Mecanismo adicional (SP5):** `ObtenerRankingProvisionalHandler` lee `competencia.db` directamente cuando no existe ranking calculado — deuda técnica conocida respecto al patrón formal.

### Torneo → Resultados

**Patrón:** Customer-Supplier (enriquecimiento contextual).

**Mecanismo:** Consulta read-only por `torneoId` — nombre, sede, fechas. `Resultados` no depende de `Torneo` para validar lógica de ranking.

### Todos los BCs → Notificaciones

**Patrón:** Customer-Supplier. Notificaciones es downstream de todos los BCs funcionales.

**Mecanismo:** Consumo de eventos de dominio (callbacks in-process en SP4). Ningún BC funcional depende de Notificaciones para completar su caso de uso.

## Tabla resumen

| Upstream | Downstream | Patrón | Mecanismo |
|----------|------------|--------|-----------|
| Identidad | Torneo | Conformist | JWT / claims |
| Identidad | Registro | Conformist | JWT / claims |
| Identidad | Competencia | Conformist | JWT / claims |
| Torneo | Registro | Customer-Supplier | `InscripcionHabilitada` |
| Registro | Competencia | Referencia por ID + adaptadores | `participante_id` / `atleta_id` |
| Competencia | Resultados | Customer-Supplier | `CompetenciaFinalizada` |
| Torneo | Resultados | Customer-Supplier | Consulta read-only por `torneoId` |
| Torneo | Notificaciones | Customer-Supplier | Eventos de dominio |
| Registro | Notificaciones | Customer-Supplier | Eventos de dominio |
| Competencia | Notificaciones | Customer-Supplier | Eventos de dominio |
| Resultados | Notificaciones | Customer-Supplier | Eventos de dominio |

## Principios de integración

- Un BC no accede directamente a la base de datos de otro BC.
- No se permiten joins ni lecturas cruzadas entre archivos SQLite de distintos BCs.
- Las integraciones cross-BC quedan contenidas en adaptadores o composition root.
- Cada BC conserva su propio lenguaje ubicuo y protege su modelo interno.

## ADRs relacionados

- [[ADR-005-bounded-contexts-ddd-estrategico]] — mapa estratégico; BC Configuración eliminado
- [[ADR-006-estructura-bc-first]] — organización de código BC-first; reglas de import
- [[ADR-007-sqlite-persistencia-bc]] — un SQLite por BC como frontera física
