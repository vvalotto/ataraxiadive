# US-2.4.1: Competencia Finalizada (automático)

**Estado**: `Backlog`
**Incremento**: Inc 2.4 — El Ranking
**Subproyecto**: SP2 — La Competencia
**Agregado principal**: `Competencia`
**Bounded Context**: `competencia`

---

## Descripción (lenguaje de negocio)

Como **sistema**,
quiero **detectar automáticamente cuando todas las performances de una disciplina han finalizado y emitir `CompetenciaFinalizada`**
para **que BC Resultados pueda calcular el ranking sin intervención manual del juez**.

---

## Contexto del dominio

### Modelo involucrado

| Elemento DDD | Nombre | Responsabilidad |
|---|---|---|
| Aggregate (existente) | `Competencia` | Nuevo método `finalizar()` que emite `CompetenciaFinalizada` |
| Domain Event (nuevo) | `CompetenciaFinalizada` | Señal de cierre de la disciplina — dispara cálculo de ranking |
| Port (nuevo) | `PerformancesEstadoPort` | Consulta cuántas performances están en estado `Ejecutada` o `DNS` |

### Lenguaje ubicuo relevante

- **Competencia finalizada**: todas las performances de la disciplina están en estado `Ejecutada` o `DNS`. No puede haber performances en `AnunciadaAP` ni `Llamada`.
- **Política P-08**: disparador automático — se verifica en `AsignarTarjetaHandler` y `RegistrarDNSHandler` tras cada operación.

---

## Especificación del comportamiento

### INV-C-04 (existente, ahora implementado)

```
INV-C-04: CompetenciaFinalizada solo cuando TODAS las Performances están en
          estado Ejecutada o DNS — sin excepciones.
```

### Operación: finalizar()

**Nombre**: `Competencia.finalizar()`

| | Descripción |
|---|---|
| **Precondición** | Competencia en estado `EnEjecucion`. Todas las Performances de la disciplina están en `Ejecutada` o `DNS`. (INV-C-04) |
| **Postcondición** | `CompetenciaFinalizada` persiste. Competencia en estado `Finalizada`. |
| **Eventos generados** | `CompetenciaFinalizada` |
| **Excepciones** | `CompetenciaNoFinalizable` si quedan performances en estado `AnunciadaAP` o `Llamada` |

**Ejemplo concreto:**

```
Performances (3 atletas):
  A: Ejecutada (tarjeta blanca)
  B: DNS
  C: Llamada  ← aún activa

AsignarTarjeta(C, blanca) → Performance C pasa a Ejecutada
Post-acción: verificar si todas = Ejecutada | DNS → SÍ
→ Competencia.finalizar() → CompetenciaFinalizada
```

### Flujo de disparo automático (Política P-08)

El disparo se implementa en dos handlers:

**AsignarTarjetaHandler** — tras persistir `TarjetaAsignada`:
1. Consultar `PerformancesEstadoPort.todas_finalizadas(competencia_id, disciplina)`
2. Si True → cargar Competencia del stream → llamar `competencia.finalizar()` → persistir `CompetenciaFinalizada`

**RegistrarDNSHandler** — tras persistir `DNSRegistrado`:
1. Misma verificación
2. Si True → mismo flujo de finalización

---

## Criterios de aceptación (BDD)

```gherkin
Feature: Competencia Finalizada — disparo automático por política P-08

  Background:
    Given una competencia STA en estado EnEjecucion con 3 performances
    And performances A y B están en estado Ejecutada
    And performance C está en estado Llamada

  Scenario: Competencia finaliza automáticamente cuando el último atleta recibe tarjeta
    When el juez asigna tarjeta blanca a la performance C
    Then el evento TarjetaAsignada persiste
    And el sistema dispara CompetenciaFinalizada automáticamente
    And la competencia pasa al estado "Finalizada"

  Scenario: Competencia finaliza automáticamente cuando el último atleta registra DNS
    When el juez registra DNS para la performance C
    Then el evento DNSRegistrado persiste
    And el sistema dispara CompetenciaFinalizada automáticamente

  Scenario: No se finaliza si quedan performances pendientes
    Given performance C está en estado Llamada
    When el juez asigna tarjeta blanca a performance A (no es la última)
    Then TarjetaAsignada persiste
    And CompetenciaFinalizada NO es emitido

  Scenario: Rechazo — finalizar manualmente sin que todas estén terminadas
    Given performance C está en estado AnunciadaAP
    When el sistema intenta finalizar la competencia
    Then la operación es rechazada con "CompetenciaNoFinalizable"

  Scenario: CompetenciaFinalizada persiste en el stream de Competencia
    When todas las performances finalizan
    Then el stream "competencia-{id}" contiene el evento CompetenciaFinalizada
    And el evento incluye competencia_id, disciplina, y total_performances
```

---

## Impacto arquitectónico

**¿Esta US requiere una decisión arquitectónica?**
- [ ] No — extiende handlers existentes con verificación post-acción

**Capas afectadas:**
- [x] Domain — `Competencia.finalizar()` + `CompetenciaFinalizada` event + `EstadoCompetencia.Finalizada`
- [x] Application — `AsignarTarjetaHandler` y `RegistrarDNSHandler` verifican P-08 y disparan `finalizar()` si corresponde; nuevo `PerformancesEstadoPort`
- [x] Infrastructure — `PerformancesEstadoAdapter` consulta streams de performances

**Payload del evento `CompetenciaFinalizada`:**
```
{
  "competencia_id": UUID,
  "disciplina": str,
  "total_performances": int,
  "ejecutadas": int,
  "dns_count": int,
  "finalizada_en": ISO8601
}
```

---

## Notas de implementación

- `PerformancesEstadoPort.todas_finalizadas()` es equivalente al check en `ObtenerProgreso` que ya existe: `completadas == total`. Se puede reutilizar o refactorizar para compartir lógica.
- `EstadoCompetencia` necesita un nuevo valor: `Finalizada` (actualmente solo tiene `Preparacion`, `Confirmada`, `EnEjecucion`).
- La transición `EnEjecucion → Finalizada` es unidireccional — no puede revertirse.
- En SP2, BC Resultados recibe `CompetenciaFinalizada` via llamada directa del handler (no hay event bus). En SP4+, esta integración se reemplaza por publicación al bus.

---

## Referencias

- Event Storming Competencia: `docs/design/event-storming-competencia.md` — P-08, INV-C-04
- Domain Model: `docs/design/domain-model.md` — BC Competencia (Competencia.finalizar())
- SP2 candidatas: `docs/plans/sp2/SP2-candidatas.md` — Inc 2.4, US-2.4.1
- US-2.4.2: CalcularRanking (consumer de CompetenciaFinalizada)

---

*Redactado: 2026-03-26 — IEDD Capa 3*
