---
title: "Inscripcion"
type: concepto
last_updated: "2026-05-22"
sources:
  - wiki/arquitectura/registro.md
  - docs/architecture/12-bc-registro.md
---

# Inscripcion

Aggregate del [[BC Registro|registro]] que modela la participación de un [[atleta]] en un [[torneo]] específico.

## Responsabilidad

`Inscripcion` certifica que un atleta tiene derecho a competir. Sin inscripción activa, el BC Competencia no puede incluir al atleta en ninguna [[grilla]].

## Estados

```
ACTIVA → CANCELADA
```

| Estado | Descripción |
|--------|-------------|
| `ACTIVA` | El atleta está habilitado para competir en el torneo |
| `CANCELADA` | El atleta abandonó voluntariamente; no puede volver a inscribirse |

## Invariantes

- Un atleta no puede inscribirse dos veces al mismo torneo (unicidad `atleta_id + torneo_id`).
- El torneo debe estar en estado `INSCRIPCION_ABIERTA` al momento de inscribirse.
- La cancelación solo está permitida antes de la fecha de inicio del torneo.
- Sin [[anuncio]] declarado dentro del plazo → el atleta inscripto no compite en esa [[disciplina]].

## Relación con otros conceptos

- **[[atleta]]** — sujeto de la inscripción; una inscripción pertenece a exactamente un atleta
- **[[torneo]]** — contenedor; la inscripción referencia el `torneoId`
- **[[disciplina]]** — el atleta inscripto puede declarar [[anuncio]] por cada disciplina disponible
- **[[categoria]]** — se hereda del atleta y determina el grupo de ranking

## Eventos generados (modelados, no materializados en código)

| Evento | Cuándo |
|--------|--------|
| `AtletaInscripto` | Al confirmar la inscripción |
| `InscripcionCancelada` | Al cancelar |

**Nota:** Estos eventos de salida no están materializados en el código actual (deuda técnica documentada en [[registro]]). La política P-10 de Notificaciones dispara email a partir del evento `InscripcionConfirmada`.

## BC propietario

[[registro]] — tabla `inscripciones` en `registro.db`.

## ADRs relacionados

- [[ADR-007-sqlite-persistencia-bc]] — persistencia CRUD en SQLite
- [[ADR-022-categoria-shared]] — `Categoria` del atleta compartida por Registro, Competencia y Resultados
