# US-3.5.3: API GET /resultados/{torneo_id}/overall

**Estado**: `To Do`
**Sprint**: SP3 — El Torneo
**Incremento**: INC-3.5
**Bounded Context**: `resultados`
**Capas afectadas**: `resultados/application/`, `resultados/api/`

---

## Descripción

Como **atleta u organizador**,
quiero **consultar el ranking general (Overall) de un torneo**
para **ver las posiciones finales considerando todas las disciplinas**.

---

## Especificación

### Precondición

```python
# US-3.5.1: RankingOverall aggregate + CalcularOverallHandler
# US-3.5.2: P-09 dispara CalcularOverall al cerrar todas las disciplinas
# resultados/api/router.py — no tiene endpoint de Overall
```

### Postcondición

```python
# resultados/application/queries/obtener_overall.py
@dataclass(frozen=True)
class ObtenerOverallQuery:
    torneo_id: UUID

class ObtenerOverallHandler:
    def __init__(self, ranking_store: EventStorePort) -> None: ...

    async def handle(self, query: ObtenerOverallQuery) -> list[EntradaOverall]:
        """Lee el último RankingOverallCalculado del stream ranking-overall-{torneo_id}.

        Returns:
            Lista de EntradaOverall ordenada por posición.
            Lista vacía si el Overall no fue calculado aún.
        """
        ...

# resultados/api/router.py (extensión):
@router.get("/{torneo_id}/overall", response_class=JSONResponse)
async def get_overall(
    torneo_id: UUID,
    handler: ObtenerOverallHandlerDep,
) -> JSONResponse:
    ...

# Respuesta:
{
    "torneo_id": "uuid",
    "total": 10,
    "calculado": true,
    "ranking": [
        {
            "posicion": 1,
            "atleta_id": "uuid",
            "puntaje": 3,
            "detalle": { "STA": 1, "DNF": 2 },
            "en_podio": true
        },
        ...
    ]
}
```

### Invariantes

- `INV-OV-API-01`: Si el Overall no fue calculado aún, retorna `{ "calculado": false, "ranking": [] }` — nunca 404
- `INV-OV-API-02`: El endpoint es público (sin auth requerido) para SP3
- `INV-OV-API-03`: El campo `detalle` muestra la posición por disciplina de cada atleta

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-3.5.3 — API Overall

  Scenario: overall calculado disponible
    Given P-09 calculó el Overall para un torneo
    When GET /resultados/{torneo_id}/overall
    Then 200 con calculado=true y lista de entradas

  Scenario: overall no calculado aún
    Given torneo con disciplinas no finalizadas
    When GET /resultados/{torneo_id}/overall
    Then 200 con calculado=false y ranking=[]

  Scenario: respuesta incluye detalle por disciplina
    Given Overall calculado con STA y DNF
    When GET /resultados/{torneo_id}/overall
    Then cada entrada tiene detalle.STA y detalle.DNF con sus posiciones

  Scenario: podio marcado correctamente
    Given 5 atletas en el Overall
    When GET /resultados/{torneo_id}/overall
    Then los 3 primeros tienen en_podio=true
    And los demás tienen en_podio=false
```

---

## Notas de implementación

- `ObtenerOverallHandler` sigue el mismo patrón que `ObtenerRankingHandler` (SP2): lee el stream del event store y proyecta la última versión.
- `ObtenerOverallHandlerDep` se define en `resultados/api/router.py` usando `Depends(get_ranking_store)`.
- El campo `"calculado": bool` evita que el cliente tenga que distinguir entre "torneo no existe" y "Overall pendiente" — en ambos casos `calculado=false`.

---

## Referencias

- US-3.5.1: RankingOverall aggregate
- US-3.5.2: P-09
- US-2.4.2: `ObtenerRankingHandler` — patrón a seguir
- Plan: `docs/plans/sp3/PLAN-SP3.md`

---

*Redactado: 2026-03-28 — SP3*
