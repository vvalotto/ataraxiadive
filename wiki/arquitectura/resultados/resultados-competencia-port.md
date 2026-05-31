---
title: "Resultados — ResultadosCompetenciaPort + Adapters"
type: arquitectura-componente
bc: resultados
capa: domain
tipo_componente: port
responsabilidad: "ACL hacia BC Competencia (streams de performances) y BC Registro (categoría del atleta) — dos puertos con sus adaptadores"
interfaces_out: []
adr_refs: [ADR-005, ADR-007, ADR-008]
last_updated: "2026-05-23"
sources:
  - src/resultados/domain/ports/resultados_competencia_port.py
  - src/resultados/infrastructure/repositories/resultados_competencia_adapter.py
  - src/resultados/infrastructure/repositories/atleta_categoria_adapter.py
---

# ResultadosCompetenciaPort — ACL a BC Competencia

## Interfaz

```python
class ResultadosCompetenciaPort(ABC):
    async def get_resultados_finales(
        self,
        competencia_id: UUID,
        disciplina: Disciplina,
    ) -> list[ResultadoFinal]: ...
```

### DTO ResultadoFinal

```python
@dataclass(frozen=True)
class ResultadoFinal:
    atleta_id: UUID
    rp: Decimal | None       # None para DNS
    unidad: str | None       # None para DNS
    tarjeta: str | None      # None para DNS
    es_dns: bool
    categoria: Categoria | None  # enriquecido en el handler
```

---

## ResultadosCompetenciaAdapter (implementación)

Lee directamente el **Event Store de BC Competencia** (`competencia.db`) sin hacer llamadas HTTP.

```python
class ResultadosCompetenciaAdapter(ResultadosCompetenciaPort):
    def __init__(self, competencia_event_store: EventStorePort) -> None:
        self._event_store = competencia_event_store
```

**Algoritmo:**
1. `load_all_streams_with_prefix(f"performance-{competencia_id}-")`
2. Por cada stream, aplica eventos secuencialmente en un dict de estado plano (sin reconstituir el aggregate completo)
3. Filtra por disciplina y estado finalizado (`finalizada=True` vía TarjetaAsignada / DNSRegistrado)
4. Construye `ResultadoFinal` (sin categoría — se enriquece después en el handler)

**Eventos que consume:**

| Evento | Acción |
|--------|--------|
| `APRegistrado` | Captura `atleta_id`, `disciplina`, `unidad` |
| `ResultadoRegistrado` | Actualiza `rp` y `unidad` |
| `TarjetaAsignada` | Actualiza `tarjeta`, `rp_penalizado` ó `rp_medido`, marca `finalizada=True` |
| `RevisionResuelta` | Igual que TarjetaAsignada |
| `DNSRegistrado` | Marca `es_dns=True`, `finalizada=True` |

La categoría llega `None` — la enriquece `CalcularRankingHandler` via `AtletaCategoriaPort`.

---

## AtletaCategoriaPort + AtletaCategoriaAdapter

```python
class AtletaCategoriaPort(ABC):
    async def get_categoria(self, atleta_id: UUID) -> Categoria: ...
```

`AtletaCategoriaAdapter` lee `registro.db` directamente (misma estrategia cross-BC que `AtletaNombreAdapter` en Competencia).

Fallback interno `_CategoriaFallbackPort` retorna `SENIOR_MASCULINO` cuando no se inyecta el adaptador real (usado en tests unitarios).

---

## Relaciones

**Contenedor:** [[arquitectura/resultados]]

- Implementaciones en `infrastructure/` — no en `domain/`
- Usadas por [[command-handlers-resultados]] (CalcularRankingHandler)
- Acceso cross-BC directo a `competencia.db` y `registro.db` — mismo patrón que [[atleta-nombre-port]] en BC Competencia

## Código fuente

| Archivo | Descripción |
|---|---|
| `src/resultados/domain/ports/resultados_competencia_port.py` | Puerto abstracto ResultadosCompetenciaPort |
| `src/resultados/infrastructure/repositories/resultados_competencia_adapter.py` | Adapter ACL — lee performances desde competencia.db |
| `src/resultados/infrastructure/repositories/atleta_categoria_adapter.py` | Adapter ACL — lee categoría del atleta desde registro.db |
