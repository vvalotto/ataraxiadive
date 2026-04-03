# US-ADJ-3.8: Auditar y corregir import cross-BC en `ResultadosCompetenciaAdapter`

**Estado**: `To Do`
**Sprint**: SP-ADJ-03 — Ajuste Técnico Post-SP3
**Issues**: HITO-14 D-06
**Bounded Context**: `resultados`
**Capas afectadas**: `resultados/infrastructure/repositories/resultados_competencia_adapter.py`

---

## Descripción

Como **desarrollador del sistema**,
quiero **reemplazar el import directo de `Performance` (aggregate de BC Competencia) en `ResultadosCompetenciaAdapter` por lectura de eventos crudos**
para **que el ACL no acople BC Resultados al modelo de dominio interno de BC Competencia**.

---

## Contexto de la deuda

### HITO-14 D-06 — Import cross-BC del aggregate `Performance`

`resultados/infrastructure/repositories/resultados_competencia_adapter.py`:

```python
from competencia.domain.aggregates.performance import Performance
from competencia.domain.value_objects.estado_performance import EstadoPerformance
```

El adapter reconstituye el aggregate `Performance` del BC Competencia para extraer
los datos que necesita:

```python
performance = Performance.reconstitute(stream_events)

if performance.disciplina != disciplina:
    continue
if performance.estado not in (EstadoPerformance.Ejecutada, EstadoPerformance.DNS):
    continue

tarjeta = performance.tarjeta.value if performance.tarjeta is not None else None
```

**El problema:** el adapter importa y reconstituye un aggregate concreto de otro BC.
Esto significa que BC Resultados tiene una dependencia estructural oculta sobre el
modelo de dominio de BC Competencia. Si `Performance` cambia (nuevos estados, nuevo
esquema de eventos), `ResultadosCompetenciaAdapter` puede romperse silenciosamente.

La regla del proyecto (CLAUDE.md §6) dice que los ACLs deben consumir contratos
delgados (puertos/DTOs), no aggregates concretos del upstream.

### ¿Es realmente una violación?

La pregunta válida: el adapter *es* la capa anticorrupción de BC Resultados.
¿No es su trabajo exactamente traducir desde el modelo del upstream?

**Sí, pero:** la traducción debería hacerse sobre el contrato *externo* del upstream
(eventos crudos como dicts, o un DTO de lectura), no sobre su aggregate interno.
Reconstituir `Performance` acopla el ACL a los internals del otro BC, no solo
a su interfaz pública.

---

## Especificación

### Opción preferida — leer eventos crudos directamente

Reemplazar `Performance.reconstitute(stream_events)` por lectura directa del payload
de los eventos relevantes:

```python
async def get_resultados_finales(self, competencia_id, disciplina) -> list[ResultadoFinal]:
    prefix = f"performance-{competencia_id}-"
    all_streams = await self._event_store.load_all_streams_with_prefix(prefix)

    resultados = []
    for stream_events in all_streams:
        resultado = _extraer_resultado_de_stream(stream_events, disciplina)
        if resultado is not None:
            resultados.append(resultado)
    return resultados


def _extraer_resultado_de_stream(
    stream_events: list[dict],
    disciplina_buscada: Disciplina,
) -> ResultadoFinal | None:
    """Extrae ResultadoFinal leyendo eventos crudos sin reconstituir el aggregate."""
    estado_final = None
    disciplina = None
    tarjeta = None
    rp = None
    unidad = None
    atleta_id = None

    for event in stream_events:
        et = event["event_type"]
        p = event["payload"]
        if et == "PerformanceIniciada":
            atleta_id = UUID(p["participante_id"])
            disciplina = Disciplina(p["disciplina"])
        elif et == "TarjetaAsignada":
            tarjeta = p["tipo"]
            estado_final = "Ejecutada"
        elif et == "DNSRegistrado":
            estado_final = "DNS"
        elif et == "ResultadoRegistrado":
            rp = p.get("rp")
            unidad = p.get("unidad")

    if disciplina != disciplina_buscada:
        return None
    if estado_final not in ("Ejecutada", "DNS"):
        return None

    return ResultadoFinal(
        atleta_id=atleta_id,
        rp=Decimal(rp) if rp and estado_final != "DNS" else None,
        unidad=unidad if estado_final != "DNS" else None,
        tarjeta=tarjeta,
        es_dns=(estado_final == "DNS"),
    )
```

### Postcondición

```python
# resultados/infrastructure/repositories/resultados_competencia_adapter.py
# NO contiene:
from competencia.domain.aggregates.performance import Performance
from competencia.domain.value_objects.estado_performance import EstadoPerformance
```

### Invariantes

- `INV-ADJ-3.8-1`: `grep "from competencia.domain"` en `resultados_competencia_adapter.py` devuelve cero matches
- `INV-ADJ-3.8-2`: `get_resultados_finales` retorna resultados idénticos a los actuales para los mismos streams de eventos
- `INV-ADJ-3.8-3`: todos los tests existentes de BC Resultados pasan sin modificación

---

## Criterios de aceptación

```gherkin
Scenario: adapter no importa nada de competencia.domain
  Given el archivo resultados_competencia_adapter.py refactorizado
  Then no contiene imports desde competencia.domain.aggregates
  And no contiene imports desde competencia.domain.value_objects

Scenario: get_resultados_finales retorna los mismos resultados
  Given un stream de performance con TarjetaAsignada=Blanca y RP=90.0
  When se llama get_resultados_finales
  Then retorna ResultadoFinal con tarjeta=Blanca, rp=90.0, es_dns=False

Scenario: performance DNS se mapea correctamente
  Given un stream de performance con DNSRegistrado
  When se llama get_resultados_finales
  Then retorna ResultadoFinal con es_dns=True, rp=None

Scenario: performance de otra disciplina se filtra
  Given un stream de performance con disciplina=DNF y query para disciplina=STA
  When se llama get_resultados_finales(disciplina=STA)
  Then no incluye esa performance en el resultado

Scenario: los tests de ranking siguen pasando
  Given el adapter refactorizado
  When se ejecuta pytest tests/unit/resultados/ tests/integration/resultados/
  Then todos los tests pasan
```

---

## Notas de implementación

- El adapter **ya tiene la lógica correcta de filtrado** — solo hay que reescribirla
  sin instanciar `Performance`. Los event_types a procesar son:
  `PerformanceIniciada`, `ResultadoRegistrado`, `TarjetaAsignada`, `DNSRegistrado`.
- Verificar los nombres exactos de event_type leyendo los eventos de dominio en
  `competencia/domain/events/` antes de implementar — deben coincidir exactamente.
- El import de `EstadoPerformance` desaparece completamente — se compara strings.
- El import de `shared.domain.value_objects.disciplina.Disciplina` **sí se mantiene**
  (es un tipo cross-BC permitido porque vive en `shared/`).
- Si los tests mockean `ResultadosCompetenciaPort` (el puerto), no necesitan cambio.
  Solo si mockean `Performance.reconstitute` directamente requerirían actualización.

---

## Referencias

- HITO-14 D-06: `docs/contexto/HITO-14-ANALISIS-METODOLOGIA-Y-ESTRUCTURA.md`
- Issues consolidados: `.work/revision-sp3/07-issues-consolidados.md`
- US-ADJ-2.6: antecedente — movió `Disciplina` a `shared/` por la misma razón
- CLAUDE.md §6 — Regla de Oro: comunicación entre BCs solo vía puertos/ACLs
- Plan SP-ADJ-03: `docs/plans/sp-adj-03/PLAN-SP-ADJ-03.md`

---

*Redactado: 2026-04-03 — SP-ADJ-03*
