---
title: "Registro — Aggregate Inscripcion"
type: arquitectura-componente
bc: registro
capa: domain
tipo_componente: aggregate
responsabilidad: "Participación de un atleta en un torneo: disciplinas, estado ACTIVA/CANCELADA, APs declarados y adjuntos"
interfaces_out:
  - InscripcionRepositoryPort
  - TorneoConsultaPort
adr_refs: [ADR-005, ADR-007]
last_updated: "2026-05-23"
sources:
  - src/registro/domain/aggregates/inscripcion.py
us_origen:
  - US-3.2.3-aggregate-inscripcion-inscribir-cancelar-y-listar
tests:
  - tests/features/US-3.2.3-inscripcion-atleta.feature
  - tests/integration/registro/test_sqlite_inscripcion_repository.py
---

# Aggregate Inscripcion

## Responsabilidad

Modela la **participación de un atleta en un torneo**. Registra las disciplinas elegidas, el estado de la inscripción, los APs declarados por disciplina y los adjuntos (apto médico, constancia de pago).

## Campos

| Campo | Descripción |
|-------|-------------|
| `inscripcion_id` | UUID autogenerado |
| `atleta_id` | Referencia al atleta inscripto |
| `torneo_id` | Referencia al torneo |
| `disciplinas` | `frozenset[Disciplina]` — disciplinas elegidas al inscribirse |
| `estado` | `ACTIVA` o `CANCELADA` |
| `fecha_inscripcion` | Timestamp de creación |
| `ap_por_disciplina` | `dict[Disciplina, APDeclarado]` — APs declarados en etapa de Preparación |
| `apto_medico_path` | Path al adjunto de apto médico (opcional) |
| `constancia_pago_path` | Path al adjunto de constancia de pago (opcional) |

## Invariantes

| Inv | Descripción |
|-----|-------------|
| INV-I-03 | Solo se puede cancelar si `fecha_actual < fecha_inicio_torneo` |

## Operaciones

| Método | Descripción |
|--------|-------------|
| `cancelar(fecha_actual, fecha_inicio_torneo)` | Cancela la inscripción si no vence el plazo |
| `declarar_ap(disciplina, valor)` | Registra el AP del atleta para una disciplina específica |
| `tiene_ap_completo()` | True si todas las disciplinas tienen AP declarado |
| `adjuntar_apto_medico(path)` / `adjuntar_constancia_pago(path)` | Registra paths de adjuntos |
| `from_row(data)` | Factory de reconstitución desde SQLite |

## Notas de diseño

- `disciplinas` como `frozenset` garantiza unicidad sin lógica extra
- `ap_por_disciplina` es un dict mutable — se pobla en etapa de Preparación
- `APDeclarado` valida unidad vs tipo de disciplina (metros para distancia, segundos para tiempo)

## Relaciones

**Contenedor:** [[arquitectura/registro]]

- Referencia a [[atleta]] por `atleta_id`
- La validación de inscripción usa [[torneo-consulta-port]] (ACL a BC Torneo)
- Los adjuntos se almacenan via [[adjunto-storage-port]]
- Los APs declarados aquí son luego consumidos por BC Competencia para generar la grilla

## Código fuente

| Archivo | Descripción |
|---|---|
| `src/registro/domain/aggregates/inscripcion.py` | Aggregate Inscripcion — participación, disciplinas, APs |
