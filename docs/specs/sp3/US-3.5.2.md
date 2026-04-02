# US-3.5.2: Política P-09 — todas las disciplinas finalizadas → CalcularOverall

**Estado**: `Done`
**Sprint**: SP3 — El Torneo
**Incremento**: INC-3.5
**Bounded Context**: `competencia` · `resultados`
**Capas afectadas**: `src/app.py`

---

## Descripción

Como **sistema**,
quiero **calcular el Overall automáticamente cuando todas las disciplinas de un torneo finalicen**
para **que los resultados generales estén disponibles sin acción manual del organizador**.

---

## Contexto

**P-09** es la política que conecta la finalización de competencias con el cálculo del Overall:

```
Evento: CompetenciaFinalizada (con torneo_id)
Condición: todas las disciplinas del torneo tienen CompetenciaFinalizada
Acción: CalcularOverall(torneo_id, disciplinas)
```

Es análoga a P-08 (`CompetenciaFinalizada → CalcularRanking`) pero opera a nivel de torneo.

---

## Especificación

### Precondición

```python
# src/app.py — P-08 ya implementado
# US-3.3.1: Competencia tiene torneo_id
# US-3.5.1: CalcularOverallHandler implementado
# El callback P-08 (AsignarTarjetaHandler) ya dispara CalcularRanking al finalizar
```

### Postcondición

```python
# src/app.py — extensión del composition root

def build_on_finalizada_callback(
    competencia_event_store: SQLiteEventStore,
) -> Callable[[UUID, Disciplina, UUID | None], Awaitable[None]]:
    """Construye callback P-08 + P-09.

    P-08: CompetenciaFinalizada → CalcularRanking (ya implementado)
    P-09: Si torneo_id presente Y todas las disciplinas del torneo finalizaron
          → CalcularOverall(torneo_id)

    Args:
        competencia_event_store: Event Store de Competencia.
    """
    ranking_db_path = os.getenv("RESULTADOS_DB_PATH", "data/resultados.db")
    torneo_db_path = os.getenv("TORNEO_DB_PATH", "data/torneo.db")

    async def _on_finalizada(
        competencia_id: UUID,
        disciplina: Disciplina,
        torneo_id: UUID | None = None,   # ← nuevo parámetro
    ) -> None:
        # P-08: CalcularRanking (sin cambios)
        ...

        # P-09: CalcularOverall si aplica
        if torneo_id is not None:
            todas_finalizadas = await _verificar_todas_disciplinas_finalizadas(
                torneo_id, competencia_event_store, torneo_db_path
            )
            if todas_finalizadas:
                disciplinas_torneo = await _obtener_disciplinas_torneo(torneo_id, torneo_db_path)
                overall_store = SQLiteEventStore(ranking_db_path)
                handler = CalcularOverallHandler(overall_store, competencia_event_store)
                await handler.handle(CalcularOverallCommand(
                    torneo_id=torneo_id,
                    disciplinas=disciplinas_torneo,
                ))

    return _on_finalizada

async def _verificar_todas_disciplinas_finalizadas(
    torneo_id: UUID,
    competencia_event_store: EventStorePort,
    torneo_db_path: str,
) -> bool:
    """Verifica si todas las disciplinas del torneo tienen CompetenciaFinalizada."""
    ...
```

### Invariantes

- `INV-P09-01`: P-09 solo se activa si `torneo_id is not None` en el evento `CompetenciaFinalizada`
- `INV-P09-02`: P-09 verifica que TODAS las disciplinas del torneo tengan `CompetenciaFinalizada` antes de calcular el Overall
- `INV-P09-03`: P-08 sigue funcionando igual — P-09 es aditivo, no modifica P-08
- `INV-P09-04`: Si solo hay 1 disciplina en el torneo, el Overall se calcula al finalizar esa sola disciplina
- `INV-P09-05`: P-09 es idempotente: si el Overall ya fue calculado, no genera un segundo cálculo

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-3.5.2 — Política P-09

  Scenario: una sola disciplina en el torneo finaliza
    Given torneo con 1 disciplina (STA), competencia STA configurada con torneo_id
    When CompetenciaFinalizada para STA
    Then P-08 calcula RankingCompetencia STA
    And P-09 detecta todas finalizadas → CalcularOverall ejecutado

  Scenario: torneo con 2 disciplinas, primera finaliza
    Given torneo con [STA, DNF], solo STA finalizada
    When CompetenciaFinalizada para STA
    Then P-08 calcula RankingCompetencia STA
    And P-09 NO dispara (DNF aún no finalizada)

  Scenario: torneo con 2 disciplinas, segunda finaliza
    Given torneo con [STA, DNF], STA ya finalizada, DNF finaliza ahora
    When CompetenciaFinalizada para DNF
    Then P-09 detecta todas finalizadas → CalcularOverall ejecutado

  Scenario: competencia sin torneo_id no activa P-09
    Given competencia standalone sin torneo_id (SP1/SP2 backward compat)
    When CompetenciaFinalizada
    Then P-08 ejecuta normalmente
    And P-09 no se activa (torneo_id is None)
```

---

## Notas de implementación

- `_verificar_todas_disciplinas_finalizadas` busca en el event store de Competencia los streams con `torneo_id` dado y verifica que cada uno tenga un evento `CompetenciaFinalizada`.
- La firma del callback cambia: agrega `torneo_id: UUID | None = None`. Backward compat: parámetro opcional.
- El handler `AsignarTarjetaHandler` (que dispara el callback) debe pasar `torneo_id` si la competencia lo tiene. Requiere que `Competencia._torneo_id` sea accesible desde el handler (via `EventStorePort`).
- Alternativa más simple: `app.py` lee la competencia del event store para obtener el `torneo_id` antes de llamar el callback.

---

## Referencias

- US-3.3.1: `torneo_id` en Competencia
- US-3.5.1: `CalcularOverallHandler`
- P-08: `build_on_finalizada_callback` en `src/app.py`
- Plan: `docs/plans/sp3/PLAN-SP3.md`

---

*Redactado: 2026-03-28 — SP3*
