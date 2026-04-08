# Contexto de Implementación — US-4.1.3
## Subdisciplinas SPE

**Fecha:** `2026-04-08`
**Estado:** `Relevado`

## Alcance confirmado

- `shared/domain`
  - `Disciplina` debe incorporar `SPE_2X50`, `SPE_4X50`, `SPE_8X50`, `SPE_16X50`
  - `DisciplinaDescriptor` debe describir estas variantes como:
    - `unidad_esperada = Segundos`
    - `orden_ascendente = False`
- `torneo/domain`
  - `Torneo.asignar_disciplinas()` debe rechazar `Disciplina.SPE` genérica en torneos nuevos
  - se requiere nueva excepción de dominio `DisciplinaObsoleta`
- `torneo/api`
  - el endpoint `PUT /torneos/{id}/disciplinas` debe devolver error consistente al intentar usar `SPE`
- `resultados/domain`
  - el ranking ya opera por disciplina, por lo que cada variante SPE queda separada por clave de disciplina
- `competencia`
  - `RegistrarAP` y `RegistrarResultado` usan `DisciplinaDescriptor`, por lo que la validación de unidad para SPE nuevo cae por propagación

## Estado actual del código

- `Disciplina` vive en `src/shared/domain/value_objects/disciplina.py`
- `DisciplinaDescriptor` vive en `src/shared/domain/value_objects/disciplina_descriptor.py`
- `Torneo.asignar_disciplinas()` hoy acepta cualquier valor del enum `Disciplina`
- La API de torneo captura `AsignacionNoPermitida`, pero no existe aún manejo específico para disciplina obsoleta
- Los tests existentes asumen:
  - `STA` es la única disciplina de tiempo
  - el resto de las disciplinas usan metros
  - el orden de grilla es ascendente para todos los casos actuales

## Impactos de prueba identificados

- Unit:
  - descriptor de disciplina
  - aggregate `Torneo`
  - API/handler de asignación de disciplinas
- Integración:
  - API de disciplinas de torneo
  - ranking por disciplina
- BDD:
  - descriptor SPE
  - independencia entre variantes SPE
  - rechazo de `Disciplina.SPE` legacy en torneos nuevos

## Riesgos

1. Cambiar `Disciplina.es_tiempo()` impacta en todo flujo que derive unidad automáticamente desde la disciplina.
2. `US-4.1.3` introduce `orden_ascendente = False` para variantes SPE; `US-4.1.4` profundiza esa regla sobre grilla y puede requerir ajustar tests nuevamente.
3. La API de torneo hoy devuelve `409` manual para algunas reglas de dominio y puede quedar inconsistente si no se agrega el nuevo caso explícitamente.
