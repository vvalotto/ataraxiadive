# Contexto de Implementación — US-4.1.4
## Orden de grilla reglamentario

**Fecha:** `2026-04-08`
**Estado:** `Relevado`

## Alcance confirmado

- `GrillaDeSalida.generar()` ya ordena usando `descriptor.orden_ascendente`
- `GenerarGrillaHandler` ya obtiene y propaga el `DisciplinaDescriptor` correcto
- El ajuste funcional principal de `orden_ascendente=False` para variantes SPE ya quedó incorporado en `US-4.1.3`
- Esta US requiere:
  - validar explícitamente la regla reglamentaria para DYN, STA y variantes SPE
  - cubrir la generación de grilla con casos SPE
  - dejar trazabilidad formal en plan/reporte/quality/tracking

## Estado actual del código

- `src/shared/domain/value_objects/disciplina_descriptor.py`
  - variantes `SPE_*` retornan `unidad_esperada=Segundos`
  - variantes `SPE_*` retornan `orden_ascendente=False`
- `src/competencia/domain/entities/grilla_de_salida.py`
  - usa `reverse=not descriptor.orden_ascendente`
- `src/competencia/application/commands/generar_grilla.py`
  - inyecta descriptor por disciplina sin lógica especial adicional

## Cobertura existente detectada

- Ya existen tests unitarios del descriptor con variantes SPE
- Ya existen tests de integración de `RegistrarAP` y descriptor para SPE
- Falta cobertura específica de generación de grilla para:
  - `SPE_4X50`
  - `SPE_2X50`
- Falta BDD específica de la US con escenarios reglamentarios explícitos

## Riesgos

1. La US depende de `US-4.1.3`; si se revirtiera el descriptor, esta US volvería a fallar.
2. Parte de la funcionalidad ya quedó implementada antes de abrir la US, así que el valor principal acá está en la validación y documentación, no en un cambio de lógica grande.
