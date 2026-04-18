# Plan de Implementación — US-4.1.1
## Motivos de tarjeta roja con catálogo formal

**Branch sugerida:** `feature/US-4.1.1-motivos-dq`
**Sprint:** `SP4`
**Incremento:** `INC-4.1`
**Patrón:** Hexagonal DDD BC-first
**Estimación total operativa:** `3h 15min`
**Estado:** `COMPLETADO`

## Componentes a modificar

### Dominio de Competencia

- `src/competencia/domain/value_objects/motivo_dq.py`
  - Nuevo `StrEnum` con catálogo formal de causas de DQ.
- `src/competencia/domain/value_objects/tarjeta_asignacion.py`
  - Reemplazar `motivo: str | None` por:
    - `motivo_dq: MotivoDQ | None`
    - `motivo_texto: str | None`
  - Validar roja con `MotivoDQ`, amarilla con texto libre y reglas de blackout.
- `src/competencia/domain/aggregates/performance.py`
  - Cambiar firma de `asignar_tarjeta()`.
  - Emitir payload nuevo.
  - Soportar reconstitución con payload histórico.
- `src/competencia/domain/events/tarjeta_asignada.py`
  - Reemplazar `motivo` por `motivo_dq_codigo` y `motivo_texto`.
- `src/competencia/domain/exceptions.py`
  - Agregar `MotivoDQObligatorio` y `DistanciaBlackoutNoAplica`.

### Aplicación e integración

- `src/competencia/application/commands/asignar_tarjeta.py`
  - Ajustar comando y handler al nuevo contrato.
- `src/resultados/infrastructure/repositories/resultados_competencia_adapter.py`
  - Verificar compatibilidad del cambio de payload.

### Tests y BDD

- Adecuar tests unitarios e integración afectados por `motivo`, `black-out` y `TarjetaAsignada`.
- Crear steps para `tests/features/US-4.1.1-motivos-tarjeta-roja.feature`.
- Mantener o adaptar regresiones de `US-1.4.1` al nuevo modelo.

## Tareas

1. **[T1]** Modelar `MotivoDQ` y nuevas excepciones. `20 min`
2. **[T2]** Refactorizar `TarjetaAsignacion`, `TarjetaAsignada` y `Performance` con compatibilidad legacy. `55 min`
3. **[T3]** Ajustar `AsignarTarjetaCommand/Handler` y revisar consumidor en `resultados`. `25 min`
4. **[T4]** Actualizar tests unitarios de dominio y aplicación. `35 min`
5. **[T5]** Actualizar tests de integración. `25 min`
6. **[T6]** Implementar steps BDD de `US-4.1.1`. `20 min`
7. **[T7]** Ejecutar pytest focalizado y corregir fallos. `25 min`
8. **[T8]** Ejecutar quality gates aplicables y documentar resultados. `10 min`

## Decisiones de implementación

- Compatibilidad histórica:
  - Si el payload viejo trae `motivo == "black-out"`, mapear a `MotivoDQ.BKO_SUPERFICIE`.
  - Si el payload viejo trae cualquier otro string en roja, preservarlo como `motivo_texto` solo para lectura histórica.
- Regla vigente:
  - Roja nueva usa exclusivamente `motivo_dq`.
  - Amarilla nueva usa exclusivamente `motivo_texto`.
- El aggregate seguirá exponiendo solo el estado necesario para esta US; no se amplía API pública sin necesidad de test.

## Riesgos

1. Fuerte acoplamiento de tests existentes al payload viejo `motivo`.
2. La compatibilidad legacy puede dispersarse si no queda centralizada en `Performance` y `TarjetaAsignada`.
3. Los escenarios de `US-1.4.1` dejan de expresar el lenguaje correcto del dominio si no se actualizan.

## Criterio de cierre

- Código, tests y artefactos del pipeline alineados a la spec `docs/specs/sp4/US-4.1.1.md`.
- Soporte dual para reconstitución de eventos viejos.
- `docs/reports/US-4.1.1-report.md` generado en Fase 9.

## Métricas de ejecución

- Tracking iniciado: `2026-04-08`
- Tracking cerrado: `2026-04-08`
- Tiempo total registrado: `17 min`
- Tiempo efectivo de tareas: `14.48 min`
- Fases ejecutadas: `0` a `9`
- Suite validada:
  - `tests/unit/competencia/domain/test_performance.py`
  - `tests/unit/competencia/application/test_asignar_tarjeta_handler.py`
  - `tests/integration/competencia/test_asignar_tarjeta_integration.py`
  - `tests/features/steps/asignar_tarjeta_steps.py`
  - `tests/features/steps/blackout_con_distancia_steps.py`
  - `tests/features/steps/test_US_4_1_1_steps.py`
- Resultado consolidado: `102 passed`

## Lecciones aprendidas

- El cambio de contrato de `TarjetaAsignada` impacta más en tests y steps BDD que en lógica pura.
- La compatibilidad histórica quedó mejor encapsulada en `Performance` y `TarjetaAsignada.from_payload()`.
- El tracker del suite no tolera escrituras concurrentes; las operaciones deben hacerse en secuencia.
