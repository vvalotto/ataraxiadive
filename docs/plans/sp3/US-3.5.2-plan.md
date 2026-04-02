# Plan de Implementacion — US-3.5.2

## Resumen

Extender la politica de finalizacion en el composition root para que
`CompetenciaFinalizada` siga disparando `CalcularRanking` (`P-08`) y, ademas,
calcule `RankingOverall` cuando la competencia cerrada complete todas las
disciplinas de un torneo (`P-09`).

## Objetivo observable

Al finalizar la ultima disciplina de un torneo, el sistema persiste el ranking
de esa disciplina y el overall del torneo sin intervencion manual.

## Alcance

- `src/app.py`
- `src/competencia/application/_p08_finalizacion.py`
- `src/competencia/application/commands/asignar_tarjeta.py`
- `src/competencia/application/commands/registrar_dns.py`
- artefactos del pipeline que correspondan a la US

No incluye:

- endpoint HTTP del overall (`US-3.5.3`)
- cambios de arquitectura fuera del composition root actual

## Decisiones de diseño

1. `P-09` se implementa en `src/app.py`, junto a `P-08`, para preservar el
   composition root como punto de orquestacion temporal entre BCs.
2. El callback `on_finalizada` pasa a aceptar `torneo_id: UUID | None`; si es
   `None`, el comportamiento queda exactamente como hoy.
3. La lista de disciplinas del torneo se obtiene desde `SQLiteTorneoRepository`,
   no reconstruyendo ese dato desde eventos de competencia.
4. La condicion "todas finalizadas" se verifica sobre competencias del torneo en
   el event store de `competencia`, buscando `CompetenciaFinalizada` por stream.
5. La idempotencia de `P-09` se apoya en `RankingOverall.calcular(...)`: si el
   overall ya existe, no debe persistirse un segundo evento.

## Implementacion por capa

### Integracion / app

- Ampliar `build_on_finalizada_callback(...)` para:
  - ejecutar `P-08` sin cambios funcionales;
  - si `torneo_id` existe, consultar competencias del torneo;
  - verificar si todas tienen `CompetenciaFinalizada`;
  - cargar disciplinas desde repositorio de `torneo`;
  - ejecutar `CalcularOverallHandler`.

- Agregar helpers privados en `src/app.py`:
  - `_verificar_todas_disciplinas_finalizadas(...)`
  - `_obtener_disciplinas_torneo(...)`

### Aplicacion competencia

- Ajustar `trigger_finalizacion_si_corresponde(...)` para reenviar `torneo_id`
  al callback luego de reconstituir la competencia.
- Actualizar `AsignarTarjetaHandler` y `RegistrarDNSHandler` al nuevo tipo del
  callback sin romper backward compatibility.

## Riesgos a resolver

1. `src/app.py` hoy depende de `shared.infrastructure.event_store.SQLiteEventStore`
   mientras `competencia` usa su propia implementacion. Hay que mantener tipos
   compatibles sin introducir acoplamiento accidental.
2. La verificacion de todas las disciplinas debe ignorar competencias standalone
   y no asumir orden de eventos mas alla de la presencia de
   `IntervaloOTConfigurado` y `CompetenciaFinalizada`.
3. La idempotencia de `P-09` debe quedar cubierta por tests para evitar dobles
   eventos si la finalizacion se procesa mas de una vez.

## Artefactos esperados al cierre

- codigo actualizado en `src/app.py` y comandos de `competencia`
- artefactos del pipeline exigidos por `/implement-us`
- `docs/reports/US-3.5.2-report.md`
