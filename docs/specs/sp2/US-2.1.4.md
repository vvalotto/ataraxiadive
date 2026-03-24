# US-2.1.4: Confirmar Grilla + Iniciar Competencia

**Estado**: `Backlog`
**Incremento**: Inc 2.1 — La Grilla de Salida
**Subproyecto**: SP2 — La Competencia
**Agregado principal**: `Competencia`
**Bounded Context**: `competencia`

---

## Descripción (lenguaje de negocio)

Como **organizador o juez**,
quiero **confirmar la grilla de salida e iniciar la competencia**
para **congelar el orden de los atletas y habilitar el registro de performances según la grilla**.

Esta US también **reemplaza el stub `CompetenciaEstadoPort`** de SP1 por la
implementación real que consulta el stream de Competencia.

---

## Contexto del dominio

### Modelo involucrado

| Elemento DDD | Nombre | Responsabilidad |
|---|---|---|
| Aggregate | `Competencia` | Transiciona de Preparacion → Confirmada → EnEjecucion |
| Port | `CompetenciaEstadoPort` | Consultado por `Performance` para verificar estado de la competencia |
| Domain Event | `GrillaConfirmada` | Hito de bloqueo: grilla congelada |
| Domain Event | `CompetenciaIniciada` | Habilita la ejecución de performances según grilla |

### Lenguaje ubicuo relevante

- **GrillaConfirmada**: hito irreversible (v1) — después de este evento, la grilla no puede modificarse.
- **CompetenciaIniciada**: la disciplina comienza. El juez puede llamar al primer atleta.
- **Estado Confirmada**: estado intermedio entre grilla lista y competencia en marcha.

---

## Especificación del comportamiento

### Operación 1: ConfirmarGrilla

**Nombre**: `confirmar_grilla()`

| | Descripción |
|---|---|
| **Precondición** | Grilla generada (`GrillaDeSalidaGenerada` emitido). Competencia en estado `Preparacion`. |
| **Postcondición** | `GrillaConfirmada` persiste. Competencia en estado `Confirmada`. Grilla congelada: `GenerarGrilla`, `RegenerarGrilla`, `AjustarGrilla` y `ConfigurarIntervaloOT` quedan bloqueados. |
| **Eventos generados** | `GrillaConfirmada` |
| **Excepciones** | `GrillaNoGenerada` · `GrillaYaConfirmada` |

**INV-C-02** (completo): `GrillaConfirmada` es unidireccional — no puede revertirse en v1.

---

### Operación 2: IniciarCompetencia

**Nombre**: `iniciar_competencia(juez_id: str)`

| | Descripción |
|---|---|
| **Precondición** | Competencia en estado `Confirmada` (`GrillaConfirmada` emitido). INV-C-03. |
| **Postcondición** | `CompetenciaIniciada` persiste. Competencia en estado `EnEjecucion`. Las Performances habilitadas para `LlamarAtleta` (política P-06). |
| **Eventos generados** | `CompetenciaIniciada` |
| **Excepciones** | `CompetenciaNoConfirmada` (INV-C-03) |

---

### Implementación real de CompetenciaEstadoPort

El stub `CompetenciaEstadoStub` de SP1 retornaba siempre:
- `is_grilla_confirmada() → False`
- `is_en_ejecucion() → True`

La implementación real `CompetenciaEstadoAdapter` consulta el stream `competencia-{id}`
del Event Store y retorna el estado proyectado:

| Método | Lógica real |
|--------|------------|
| `is_grilla_confirmada(competencia_id)` | True si `GrillaConfirmada` existe en el stream |
| `is_en_ejecucion(competencia_id)` | True si `CompetenciaIniciada` existe y `CompetenciaFinalizada` no existe |
| `is_plazo_vencido(competencia_id)` | True si `PlazoAPVencido` existe en el stream |

**Impacto en SP1:** los tests de SP1 que usaban el stub deben seguir pasando.
Se reemplaza el registro del stub en el contenedor DI por el adaptador real.
Para tests unitarios de `Performance`, el stub se mantiene como test double.

---

## Criterios de aceptación (BDD)

```gherkin
Feature: Confirmar Grilla e Iniciar Competencia

  Background:
    Given una competencia "C001" en estado "Preparacion"
    And la grilla fue generada con 3 atletas

  Scenario: Confirmar grilla exitosamente
    When el organizador confirma la grilla
    Then el evento GrillaConfirmada persiste
    And la competencia pasa al estado "Confirmada"
    And GenerarGrilla queda bloqueado

  Scenario: Rechazo — confirmar sin grilla generada
    Given la grilla no fue generada aún
    When el organizador intenta confirmar la grilla
    Then el sistema rechaza con error "GrillaNoGenerada"

  Scenario: Iniciar competencia exitosamente
    Given la grilla ya fue confirmada (estado "Confirmada")
    When el juez inicia la competencia
    Then el evento CompetenciaIniciada persiste
    And la competencia pasa al estado "EnEjecucion"
    And el comando LlamarAtleta queda habilitado para las performances

  Scenario: Rechazo — iniciar sin grilla confirmada
    Given la competencia está en estado "Preparacion" (no Confirmada)
    When el juez intenta iniciar la competencia
    Then el sistema rechaza con error "CompetenciaNoConfirmada"

  Scenario: CompetenciaEstadoPort real — is_grilla_confirmada
    Given el stream de Competencia "C001" contiene GrillaConfirmada
    When Performance consulta CompetenciaEstadoPort.is_grilla_confirmada("C001")
    Then retorna True
    And el intento de registrar un nuevo AP falla con "GrillaYaConfirmada"

  Scenario: CompetenciaEstadoPort real — is_en_ejecucion
    Given el stream de Competencia "C001" contiene CompetenciaIniciada
    When Performance consulta CompetenciaEstadoPort.is_en_ejecucion("C001")
    Then retorna True
    And LlamarAtleta queda habilitado para esa competencia
```

---

## Impacto arquitectónico

**¿Esta US requiere una decisión arquitectónica?**
- [x] Sí — reemplaza el stub con la implementación real, cerrando el "agujero" de SP1

**Capas afectadas:**
- [x] Domain — `GrillaConfirmada` y `CompetenciaIniciada` events; transiciones de `EstadoCompetencia`
- [x] Application — `ConfirmarGrillaHandler`, `IniciarCompetenciaHandler`
- [x] Infrastructure — `CompetenciaEstadoAdapter` (reemplaza `CompetenciaEstadoStub`)
- [x] API — endpoints `POST /competencia/{id}/confirmar-grilla` y `POST /competencia/{id}/iniciar`

**Nota de migración del stub:**
- El stub `CompetenciaEstadoStub` se mantiene como test double en `tests/` — no se elimina.
- El adaptador real se registra en el contenedor DI del `router.py` / `app.py`.

---

## Read Models nuevos (o actualizados)

| Read Model | Endpoint | Información |
|-----------|----------|-------------|
| `GrillaDeSalida` | `GET /competencia/{id}/grilla` | Lista ordenada: atleta, posición, andarivel, OT |
| `EstadoCompetencia` | `GET /competencia/{id}/estado` | Estado actual + intervalo + grilla confirmada/no |

---

## Referencias

- Event Storming Competencia: `docs/design/event-storming-competencia.md` — Flujo 1, US-C-04 + US-C-05
- Invariantes: INV-C-02 (completo), INV-C-03; Hot Spot HS-P1 (resuelto)
- Políticas: P-04, P-06
- SP1 nota: `CompetenciaEstadoPort` stub definido en `docs/specs/sp1/US-1.2.1.md`
- `docs/plans/sp2/SP2-candidatas.md` — Inc 2.1

---

*Redactado: 2026-03-24 — IEDD Capa 3*
