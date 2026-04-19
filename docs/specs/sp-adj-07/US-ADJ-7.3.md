# US-ADJ-7.3: Cablear P-11 a `CompetenciaFinalizada` — SCOPE-SP4-001

**Estado**: `Implementada`
**Iteración / Sprint**: SP-ADJ-07
**Tipo**: feat de integración (composition root)
**Área principal**: `src/app.py` (función `_on_finalizada`)
**Bounded Contexts involucrados**: `competencia`, `resultados`, `registro`, `torneo`, `notificaciones`

---

## Descripción (lenguaje de negocio)

Como **atleta inscripto**,
quiero recibir un email con mis resultados cuando una disciplina finaliza
para conocer mi posición en el ranking sin necesidad de estar en el lugar de la competencia.

---

## Contexto del dominio

### Problema

`PoliticaP11Handler` y su factory `build_p11_handler()` están definidos en `app.py`
pero **nunca se invocan**. La política P-11 dice:

> *Cuando una disciplina finaliza (`CompetenciaFinalizada`), enviar los resultados
> a cada atleta que compitió en esa disciplina.*

El callback `_on_finalizada` en `app.py` solo ejecuta P-08 (calcular ranking) y P-09
(calcular overall). P-11 nunca se dispara, haciendo al BC Notificaciones letra muerta
excepto para P-10.

### Solución

Extender `_on_finalizada` con una nueva fase `_notificar_resultados_p11` que:

1. Recupera el ranking ya calculado (P-08 ya corrió) del event store de Resultados
2. Para cada entrada del ranking, busca nombre y email del atleta en el BC Registro
3. Construye un `ResultadosPublicados` con los datos completos
4. Llama a `build_p11_handler().handle(ResultadosPublicados(...))`

### Flujo de eventos en `_on_finalizada` (post-fix)

```
CompetenciaFinalizada (emitido por AsignarTarjetaHandler o RegistrarDNSHandler)
  │
  ├── P-08: _calcular_ranking_por_finalizacion(...)   ← sin cambios
  │                           ↓
  │              ResultadosCalculados en ranking store
  │
  ├── P-09: _calcular_overall_si_corresponde(...)     ← sin cambios
  │
  └── P-11: _notificar_resultados_p11(...)            ← NUEVO
                              ↓
              ObtenerRankingHandler → ranking entries
              SQLiteAtletaRepository → nombre + email por atleta_id
              SQLiteTorneoRepository → torneo_nombre
                              ↓
              ResultadosPublicados(...)
                              ↓
              PoliticaP11Handler.handle(...)
                              ↓
              SolicitarEnvioHandler → NotificacionSolicitada
              EnviarNotificacionHandler → NotificacionEnviada (Resend)
```

### Idempotencia

La idempotencia está garantizada por el aggregate `Notificacion` existente (US-4.5.1):
`SolicitarEnvioHandler` verifica que no exista ya un `NotificacionEnviada` para el
`evento_fuente_id = "{competencia_id}:{atleta_id}"` antes de solicitar el envío.
Si `_notificar_resultados_p11` se llama dos veces (por retry), no se duplican los emails.

---

## Especificación del comportamiento

### Precondición

- `CompetenciaFinalizada` fue emitido para `(competencia_id, disciplina)`.
- P-08 ya calculó el ranking (stream `ranking-{competencia_id}-{disciplina}` no vacío).
- `RESEND_API_KEY` puede estar o no configurada (si no está, `ResendEmailAdapter`
  falla silenciosamente o usa `LoggingEmailAdapter` — comportamiento existente).

### Postcondición

Para cada atleta en el ranking:
- Si tiene email registrado: `NotificacionSolicitada` + `NotificacionEnviada` en el
  event store de notificaciones, y email enviado vía Resend.
- Si no tiene email: `NotificacionFallida` con `motivo="sin_email"` (comportamiento
  existente de `registrar_fallo_sin_email`).
- Si el atleta está en estado DNS: se incluye en `ResultadosPublicados.resultados`
  con `estado="DNS"` — la política P-11 lo filtra usando `estado == "Retirado"` para
  skip, pero DNS se notifica (el atleta sabe que no se presentó).

### Invariante de integración

> P-11 debe dispararse **después** de P-08, nunca antes. Si P-08 falla (excepción),
> P-11 no se ejecuta. Si P-11 falla, no afecta la finalización de la competencia —
> los fallos de notificación son silenciosos (ya cubiertos por `registrar_fallo_sin_email`).

---

## Criterios de aceptación

```gherkin
Feature: P-11 wiring — notificaciones al finalizar disciplina

  Background:
    Given una competencia con 3 atletas inscriptos con emails registrados
    And todos los atletas completaron su performance (AsignarTarjeta)
    And CompetenciaFinalizada fue emitido

  Scenario: Los 3 atletas reciben email de resultados al finalizar la disciplina
    When _on_finalizada se ejecuta con la disciplina finalizada
    Then el event store de notificaciones contiene NotificacionEnviada para cada atleta
    And cada email contiene nombre del atleta, posición, RP y disciplina

  Scenario: El atleta sin email registrado no genera error
    Given uno de los atletas no tiene email registrado (None o vacío)
    When _on_finalizada se ejecuta
    Then el event store de notificaciones contiene NotificacionFallida para ese atleta
    And los otros 2 atletas reciben su email normalmente

  Scenario: Idempotencia — no se duplican emails si P-11 se ejecuta dos veces
    Given P-11 ya corrió una vez y los emails fueron enviados
    When _on_finalizada se ejecuta de nuevo para la misma (competencia_id, disciplina)
    Then el aggregate Notificacion detecta que NotificacionEnviada ya existe
    And no se envían emails duplicados
    And el event store de notificaciones no tiene nuevas entradas

  Scenario: Fallo de Resend no afecta la competencia
    Given RESEND_API_KEY no está configurada (o Resend devuelve error)
    When _on_finalizada se ejecuta
    Then CompetenciaFinalizada y ResultadosCalculados existen correctamente
    And el fallo de envío queda registrado en el event store de notificaciones
    And no se lanza excepción que propague al handler de dominio
```

---

## Artefactos a modificar / crear

| Artefacto | Cambio |
|-----------|--------|
| `src/app.py` | Agregar `_notificar_resultados_p11(...)` · llamarla desde `_on_finalizada` después de P-08 |
| `tests/unit/test_app_p11_wiring.py` | Tests unitarios del mapeo ranking/atleta/torneo a `ResultadosPublicados` |
| `tests/integration/test_p11_callback_integration.py` | Tests de integración del callback completo e idempotencia |
| `tests/features/US-ADJ-7.3-p11-competencia-finalizada.feature` | Escenarios BDD de P-11 al finalizar competencia |
| `tests/features/steps/p11_competencia_finalizada_steps.py` | Steps BDD para ejecutar el flujo real con stores temporales |

No se requieren cambios en el BC Notificaciones ni en el BC Resultados — todo el
trabajo ocurre en el composition root.

---

## Diseño de `_notificar_resultados_p11`

```python
async def _notificar_resultados_p11(
    ranking_store: SQLiteEventStore,
    competencia_id: UUID,
    disciplina: Disciplina,
    torneo_id: UUID | None,
    registro_db_path: str,
    torneo_db_path: str,
) -> None:
    """Ejecuta P-11: notificar resultados a atletas al finalizar disciplina."""
    # 1. Leer ranking calculado por P-08
    ranking_handler = ObtenerRankingHandler(ranking_store)
    categorias = await ranking_handler.handle(
        ObtenerRankingQuery(competencia_id=competencia_id, disciplina=disciplina)
    )
    todas_las_entradas = [e for cat in categorias for e in cat.entradas]
    if not todas_las_entradas:
        return

    # 2. Leer nombre del torneo
    torneo_nombre = await _obtener_nombre_torneo(torneo_id, torneo_db_path)

    # 3. Leer nombre + email por atleta desde Registro
    atleta_repo = SQLiteAtletaRepository(registro_db_path)
    resultados = []
    podio = []
    for entrada in todas_las_entradas:
        atleta_id = UUID(entrada.atleta_id)
        atleta = await atleta_repo.find_by_id(atleta_id)
        nombre = f"{atleta.nombre} {atleta.apellido}" if atleta else entrada.atleta_id
        email = atleta.email if atleta else None
        resultados.append(ResultadoPublicadoAtleta(
            atleta_id=entrada.atleta_id,
            atleta_email=email,
            atleta_nombre=nombre,
            posicion=entrada.posicion,
            rp=entrada.rp or "DNS",
            tarjeta=entrada.tarjeta,
            estado="DNS" if entrada.es_dns else "Clasificado",
        ))
        if entrada.en_podio:
            podio.append(PodioPublicado(
                posicion=entrada.posicion,
                atleta_nombre=nombre,
                rp=entrada.rp or "DNS",
            ))

    # 4. Construir evento y llamar P-11
    evento = ResultadosPublicados(
        id=str(competencia_id),
        torneo_id=str(torneo_id) if torneo_id else None,
        torneo_nombre=torneo_nombre,
        disciplina=disciplina.value,
        resultados=tuple(resultados),
        podio=tuple(podio),
    )
    p11 = build_p11_handler()
    await p11.handle(evento)
```

### Nuevo helper `_obtener_nombre_torneo`

```python
async def _obtener_nombre_torneo(
    torneo_id: UUID | None,
    torneo_db_path: str,
) -> str:
    if torneo_id is None:
        return "Torneo sin nombre"
    torneo_repo = SQLiteTorneoRepository(torneo_db_path)
    torneo = await torneo_repo.find_by_id(torneo_id)
    return torneo.nombre if torneo else f"Torneo {torneo_id}"
```

### Modificación en `_on_finalizada`

```python
async def _on_finalizada(
    competencia_id: UUID,
    disciplina: Disciplina,
    torneo_id: UUID | None = None,
) -> None:
    ranking_store = SQLiteEventStore(ranking_db_path)
    await _calcular_ranking_por_finalizacion(...)       # P-08 — sin cambios
    await _calcular_overall_si_corresponde(...)          # P-09 — sin cambios
    try:
        await _notificar_resultados_p11(                 # P-11 — nuevo
            ranking_store=ranking_store,
            competencia_id=competencia_id,
            disciplina=disciplina,
            torneo_id=torneo_id,
            registro_db_path=os.getenv("REGISTRO_DB_PATH", "data/registro.db"),
            torneo_db_path=torneo_db_path,
        )
    except Exception:  # noqa: BLE001
        logger.warning("No se pudieron notificar resultados P-11", exc_info=True)
```

> El `try/except` en P-11 es intencional: los fallos de envío no deben propagar
> y afectar la finalización de la competencia. Los errores de Resend o de base de
> datos de Registro quedan registrados en el event store de Notificaciones mediante
> `NotificacionFallida`.

---

## Imports adicionales requeridos en `app.py`

```python
from registro.infrastructure.repositories.sqlite_atleta_repository import SQLiteAtletaRepository
from resultados.application.queries.obtener_ranking import ObtenerRankingHandler, ObtenerRankingQuery
from notificaciones.application.policies.politica_p11 import (
    ResultadoPublicadoAtleta,
    ResultadosPublicados,
    PodioPublicado,
)
```

> `SQLiteAtletaRepository` y `ObtenerRankingHandler` son imports de infraestructura
> y application respectivamente — válidos en el composition root (`app.py`).

---

## Validación ejecutada

- Unit: `tests/unit/test_app_p11_wiring.py` — 4 passed.
- Integration: `tests/integration/test_p11_callback_integration.py` — 4 passed.
- BDD: `tests/features/steps/p11_competencia_finalizada_steps.py` — 4 passed.
- Regresión composition root P-09/P-10/P-11 con cobertura: 18 passed, cobertura `src/app.py` 96%.
- CodeGuard acotado a `src/app.py`: 0 errores, 0 warnings.

---

## Notas de implementación

1. `ranking_store` se instancia dentro de `_on_finalizada` (ya existe así para P-08/P-09).
   Reutilizar la misma instancia para P-11 en lugar de crear una nueva.
2. Verificar que `Torneo.nombre` exista como campo en el aggregate `Torneo` (vía
   `SQLiteTorneoRepository.find_by_id`).
3. El test de integración debe usar un seed con atleta real (nombre + email), ejecutar
   el callback `_on_finalizada` directamente, y verificar el event store de notificaciones.
4. Para el smoke test manual: configurar `RESEND_API_KEY` y `NOTIFICACIONES_EMAIL_FROM`,
   completar una disciplina, y verificar email recibido.

---

*Spec creada: 2026-04-19 — SCOPE-SP4-001 de BL-004*
*Implementada: 2026-04-19 — SP-ADJ-07*
