# US-5.2.2: Finalizacion manual de prueba por disciplina

**Estado**: `To Do`
**Sprint**: SP5 — La Puesta en Marcha
**Incremento**: INC-5.2
**Bounded Context**: `competencia` + `frontend`
**Capas afectadas**: `src/competencia/domain/`, `src/competencia/application/`, `src/competencia/api/`, `frontend/src/components/organizador/`, `frontend/src/api/competencia.ts`

---

## Descripcion

Como **organizador**,
quiero **finalizar manualmente una prueba de una disciplina cuando ya no quedan performances pendientes**
para **registrar de forma explicita el cierre operativo de la disciplina y dejar trazabilidad de si el cierre fue manual o automatico**.

---

## Contexto del dominio

### Modelo involucrado

| Elemento | Nombre | Responsabilidad |
|---|---|---|
| Aggregate | `Competencia` | Valida si la competencia es finalizable y emite `CompetenciaFinalizada` |
| Policy | `P-08` | Finalizacion automatica cuando todas las performances estan cerradas |
| Command | `FinalizarCompetenciaManualCommand` | Solicita cierre explicito por organizador |
| Event | `CompetenciaFinalizada` | Evento de cierre de competencia; debe distinguir origen manual/automatico |
| Query | `ObtenerProgresoHandler` | Permite detectar pendientes antes de habilitar la accion |
| Service | `CalculadorHashCompetencia` | Calcula hash SHA-256 del cierre de la disciplina |
| Componente | `EjecucionPanel` / `MonitorDisciplina` | Muestra accion `Finalizar prueba` y bloqueo si hay pendientes |

### Lenguaje ubicuo relevante

- **Cierre automatico:** cierre emitido por P-08 luego de registrar DNS o tarjeta final y detectar que todas las performances terminaron.
- **Cierre manual:** cierre solicitado por el organizador desde el panel, usando las mismas invariantes de finalizacion.
- **Performance pendiente:** performance que todavia no esta en estado terminal (`Ejecutada`, `DNS` o tarjeta final segun la proyeccion vigente).
- **Origen de cierre:** dato auditable que indica si `CompetenciaFinalizada` fue emitida por politica automatica o por solicitud manual.

---

## Especificacion del comportamiento

### Invariantes

- **INV-5.2.2-01:** Solo una competencia en estado `EnEjecucion` puede finalizarse manualmente.
- **INV-5.2.2-02:** La finalizacion manual esta permitida solo si no quedan performances pendientes.
- **INV-5.2.2-03:** La finalizacion manual reutiliza la misma validacion de `Competencia.finalizar()` que P-08.
- **INV-5.2.2-04:** Una competencia ya `Finalizada` no puede finalizarse nuevamente; la operacion debe ser idempotente visualmente en frontend y rechazada o no-op controlado en backend.
- **INV-5.2.2-05:** El evento de cierre debe dejar trazabilidad del origen: `manual` o `automatico`.
- **INV-5.2.2-06:** Si quedan pendientes, la UI no dispara el endpoint y muestra el detalle de bloqueo.

### Operacion principal — finalizar prueba manualmente

**Nombre propuesto**: `POST /competencia/{competencia_id}/finalizar`

| | Descripcion |
|---|---|
| **Precondicion** | Usuario autenticado con rol ORGANIZADOR. Competencia en estado `EnEjecucion`. Todas las performances de la disciplina estan cerradas. |
| **Postcondicion** | Competencia en estado `Finalizada`; se persiste `CompetenciaFinalizada` con hash SHA-256 y origen `manual`. |
| **Body** | `{ disciplina, solicitado_por }` o `{ disciplina }` usando el usuario autenticado como solicitante. |
| **Excepciones** | 409 si hay performances pendientes o la competencia no esta en estado finalizable; 404 si no existe la competencia. |

**Flujo backend esperado:**

```
1. Handler recibe FinalizarCompetenciaManualCommand(competencia_id, disciplina, solicitado_por).
2. Consulta PerformancesEstadoPort para total, ejecutadas y dns_count.
3. Si quedan pendientes, rechaza con CompetenciaNoFinalizable.
4. Calcula hash SHA-256 con CalculadorHashCompetencia.
5. Reconstituye Competencia desde Event Store.
6. Ejecuta Competencia.finalizar(..., origen="manual", finalizada_por=solicitado_por).
7. Persiste CompetenciaFinalizada.
```

### Ajuste requerido — coexistencia con P-08

La politica P-08 debe seguir funcionando sin accion del organizador:

```
asignar tarjeta / registrar DNS
  -> trigger_finalizacion_si_corresponde()
  -> si todas estan cerradas, CompetenciaFinalizada(origen="automatico")
```

La nueva accion manual no reemplaza P-08. Ambas rutas deben emitir el mismo evento de dominio
con una diferencia auditable de origen.

### Operacion frontend — habilitar accion `Finalizar prueba`

| | Descripcion |
|---|---|
| **Precondicion** | Disciplina seleccionada en el detalle de `EjecucionPanel`. Competencia en `EnEjecucion`. |
| **Postcondicion** | Si no hay pendientes, se llama al endpoint y el detalle recarga en estado `Finalizada`. |

**Regla de habilitacion UI:**

```
boton Finalizar prueba habilitado si:
  estado_competencia == "EnEjecucion"
  progreso.total > 0
  progreso.completadas == progreso.total
```

**Ejemplo concreto:**

```
DNF / C1 en EnEjecucion.
Progreso: total=10, ejecutadas=8, dns_count=2, completadas=10.
UI habilita "Finalizar prueba".
POST /competencia/C1/finalizar { disciplina: "DNF" } -> 204
GET /competencia/C1/estado -> { estado: "Finalizada", hash_sha256: "..." }
Detalle muestra "Finalizada" y oculta acciones operativas.
Audit log de eventos contiene CompetenciaFinalizada con origen="manual".
```

---

## Criterios de aceptacion (BDD)

```gherkin
Feature: US-5.2.2 — Finalizacion manual de prueba por disciplina

  Background:
    Given el organizador "org@ataraxia.com" esta autenticado con rol ORGANIZADOR
    And el torneo "BA 2026" con id T1 esta en estado EJECUCION
    And la disciplina DNF tiene competencia C1 en estado EnEjecucion

  Scenario: finalizar manualmente una disciplina sin pendientes
    Given C1 tiene 10 performances totales
    And 8 performances estan ejecutadas
    And 2 performances estan DNS
    When el organizador selecciona DNF en el tab "Ejecucion"
    Then ve la accion "Finalizar prueba" habilitada
    When toca "Finalizar prueba"
    Then el frontend envia POST /competencia/C1/finalizar con disciplina DNF
    And la competencia C1 queda en estado Finalizada
    And se registra CompetenciaFinalizada con origen "manual"
    And el detalle muestra el hash SHA-256 de cierre si esta disponible

  Scenario: no se puede finalizar si quedan performances pendientes
    Given C1 tiene 10 performances totales
    And 7 performances estan completadas
    And 3 performances estan pendientes
    When el organizador selecciona DNF en el tab "Ejecucion"
    Then la accion "Finalizar prueba" esta deshabilitada
    And el detalle muestra "Quedan 3 performances pendientes"
    And no se envia POST /competencia/C1/finalizar

  Scenario: backend rechaza cierre manual con pendientes aunque la UI falle
    Given C1 tiene 10 performances totales
    And 1 performance esta pendiente
    When un cliente envia POST /competencia/C1/finalizar con disciplina DNF
    Then el backend responde 409
    And la competencia C1 permanece en estado EnEjecucion
    And no se emite CompetenciaFinalizada

  Scenario: cierre automatico sigue funcionando
    Given C1 tiene 10 performances totales
    And 9 performances ya estan cerradas
    When el juez asigna la tarjeta final de la ultima performance
    Then P-08 emite CompetenciaFinalizada automaticamente
    And el evento queda registrado con origen "automatico"
    And el organizador ve la disciplina Finalizada al refrescar el detalle

  Scenario: competencia ya finalizada no muestra accion de cierre
    Given C1 ya esta en estado Finalizada
    When el organizador selecciona DNF en el tab "Ejecucion"
    Then no ve la accion "Finalizar prueba"
    And ve el estado "Finalizada"
```

---

## Impacto arquitectonico

- [x] Si — agrega comando/API explicitos para cierre manual y extiende la trazabilidad del evento de cierre.

**Capa(s) afectadas:**
- [x] Dominio — `Competencia.finalizar()` y/o `CompetenciaFinalizada` deben soportar origen de cierre.
- [x] Application — nuevo `FinalizarCompetenciaManualCommand` + handler.
- [x] Application — P-08 debe marcar origen `automatico`.
- [x] API — nuevo endpoint `POST /competencia/{competencia_id}/finalizar`.
- [x] Frontend — `EjecucionPanel`/`MonitorDisciplina`: accion `Finalizar prueba`, bloqueo por pendientes y recarga de estado.
- [x] Frontend — `api/competencia.ts`: wrapper `finalizarCompetencia()`.

---

## Referencias

- Plan SP5: `docs/plans/sp5/PLAN-SP5.md §INC-5.2`
- Hallazgo UAT: `.work/revision-sp5/01-hallazgos-uat-inc-5.1.md §UAT-5.1-07`
- Politica automatica: `src/competencia/application/_p08_finalizacion.py`
- Aggregate: `src/competencia/domain/aggregates/competencia.py`
- Evento actual: `src/competencia/domain/events/competencia_finalizada.py`
- Endpoint iniciar relacionado: `src/competencia/api/router.py` — `POST /competencia/{competencia_id}/iniciar`

---

## Notas de implementacion

- Evitar duplicar la logica de cierre: el handler manual debe reutilizar `Competencia.finalizar()` y los mismos puertos que P-08.
- Si `CompetenciaFinalizada` ya esta persistido sin campo `origen`, la reconstitucion debe ser backward compatible.
- El nuevo campo auditable recomendado es `origen`: valores `automatico` y `manual`; opcionalmente `finalizada_por` para el email/id del organizador.
- El frontend no debe confiar exclusivamente en `progreso.completadas == total`; el backend es la fuente de verdad y debe rechazar con 409 si hay pendientes.
- Esta US depende funcionalmente de `US-5.2.1` para ubicar la accion en el detalle de disciplina.

---

*Redactado: 2026-04-22 — INC-5.2 Ejecucion por Disciplina*
