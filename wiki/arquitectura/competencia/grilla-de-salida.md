---
title: "Competencia — Entity GrillaDeSalida"
type: arquitectura-componente
bc: competencia
capa: domain
tipo_componente: aggregate
responsabilidad: "Entidad interna de Competencia: generación, ajuste y reconstitución de la grilla de salida por AP"
interfaces_out: []
adr_refs: [ADR-001, ADR-004]
last_updated: "2026-05-23"
sources:
  - src/competencia/domain/entities/grilla_de_salida.py
---

# Entity GrillaDeSalida

## Responsabilidad

Entidad interna del [[competencia-aggregate]]. Encapsula la lógica de construcción y mutación de la grilla de salida: ordenamiento por AP, cálculo de OTs y aplicación de ajustes manuales. No tiene identidad propia — vive dentro del aggregate Competencia.

## Políticas de ordenamiento

| Tipo disciplina | Ordenamiento |
|----------------|-------------|
| Tiempo (STA) | AP mayor → menor (primero el más largo) |
| Distancia (DNF, DYN, etc.) | AP menor → mayor (primero el más conservador) |

## Cálculo de OT (P-02)

```
OT_atleta = ot_inicio + (posicion − 1) × intervaloDisciplina
```

Los OTs se recalculan para todas las entradas cuando se modifica la posición de algún atleta.

## Operaciones

| Método | Descripción |
|--------|-------------|
| `generar()` | Genera entradas desde una lista de `PerformancesAPData`, aplica ordenamiento y calcula OTs |
| `ajustar()` | Aplica lista de `CambioGrilla` (posición o andarivel); recalcula OTs si cambió posición |
| `cargar_desde_payload()` | Reconstitución desde evento `GrillaDeSalidaGenerada` |
| `aplicar_cambios_persistidos()` | Reconstitución desde evento `GrillaDeSalidaAjustada` |
| `asignar_juez()` | Asigna juez a una entrada por `performance_id` |

## Estado

- `esta_generada: bool` — True una vez que se llamó a `generar()` al menos una vez
- `entradas: list[EntradaGrilla]` — lista de entradas actuales (inmutable externamente)

## Relaciones

- Es propiedad exclusiva de [[competencia-aggregate]]
- Consume `PerformancesAPData` del [[performances-ap-port]] (a través del handler)
- Usa `DisciplinaDescriptor` del [[disciplina-descriptor-port]] para saber el tipo de ordenamiento
- `EntradaGrilla` y `CambioGrilla` son value objects del dominio
