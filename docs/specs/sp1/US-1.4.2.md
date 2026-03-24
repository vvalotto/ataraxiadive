# US-1.4.2 — Flujo Completo E2E: AP → Tarjeta

| Campo | Valor |
|-------|-------|
| **ID** | US-1.4.2 |
| **Incremento** | 1.4 |
| **BC** | Competencia |
| **Actor** | Juez (desde el celular) |
| **RFs** | RF-EJ-05, RF-EJ-10 |
| **Invariantes** | INV-P-05, INV-P-06, INV-P-07, INV-P-08, INV-P-09, INV-P-10 |

---

## Historia de Usuario

Como juez, quiero ejecutar el flujo completo de una competencia desde el celular
(AP → llamar → resultado → tarjeta) y poder ver la traza completa de eventos,
para verificar que el Event Store refleja fielmente todo lo ocurrido.

---

## Precondición

- BC Competencia con todos los comandos del flujo disponibles (US-1.2.1 a US-1.4.1 implementadas)
- Read Models disponibles (US-1.3.1 implementada)
- Al menos una competencia activa con `competenciaId` conocido

## Postcondición

- 5 performances ejecutadas (flujo completo AP → llamar → resultado/DNS → tarjeta)
- Al menos 1 DNS registrado en el lote
- Al menos 1 corrección de resultado (`CorregirResultado`) aplicada
- `GET /competencia/{id}/events` retorna la secuencia ordenada de eventos de las 5 performances
- Los Read Models (`/performance/actual`, `/performance/proximas`, `/progreso`) son consistentes con el Event Store

## Invariantes verificados E2E

- INV-P-05: `LlamarAtleta` solo si Performance = `AnunciadaAP`
- INV-P-06: `RegistrarResultado` solo si Performance = `Llamada`
- INV-P-07: `AsignarTarjeta` solo si `ResultadoRegistrado` previo
- INV-P-08: `RegistrarDNS` solo si Performance = `Llamada`
- INV-P-09: `RegistrarResultado` y `RegistrarDNS` son mutuamente excluyentes
- INV-P-10: `CorregirResultado` solo si Performance = `Ejecutada` (no DNS)

---

## Nuevo endpoint requerido

### `GET /competencia/{competencia_id}/events`

Retorna todos los eventos del Event Store para una competencia, en orden de secuencia.

**Response 200:**
```json
{
  "competencia_id": "uuid",
  "total_events": 18,
  "events": [
    {
      "sequence": 1,
      "event_type": "APRegistrado",
      "performance_id": "uuid",
      "occurred_at": "2026-03-23T10:00:00Z",
      "data": { "atleta_id": "...", "valor_ap": 60.0, "disciplina": "STA" }
    }
  ]
}
```

**Response 404:** si la competencia no existe o no tiene eventos.

**Nota:** Este endpoint es de solo lectura — proyecta eventos sin transformar. Es el equivalente a un audit log del Event Store.

---

## Escenario DoD

```
5 atletas con AP registrado (hardcodeados en SP1):
  - Atleta A: AP 60m, disciplina STA → flujo completo → tarjeta blanca
  - Atleta B: AP 40m, disciplina STA → DNS
  - Atleta C: AP 80m, disciplina STA → resultado 72m → tarjeta amarilla (sin superficie)
  - Atleta D: AP 50m, disciplina STA → resultado 55m → tarjeta blanca → corregir a 53m
  - Atleta E: AP 90m, disciplina STA → resultado 90m → tarjeta roja (black-out, distancia 45m)

Verificación final:
  GET /competencia/{id}/events → 18+ eventos en orden
  GET /competencia/{id}/progreso → { ejecutadas: 5, total: 5, dns: 1 }
  Read Models consistentes con el Event Store
```

---

## Criterios de aceptación (BDD)

```gherkin
Feature: Flujo completo E2E de una competencia de apnea

  Background:
    Given una competencia activa con id "comp-sp1-test"
    And 5 atletas con AP registrado en la grilla

  Scenario: Flujo completo para atleta con tarjeta blanca
    Given el atleta "Atleta A" tiene AP de 60m en estado AnunciadaAP
    When el juez llama al atleta "Atleta A"
    And registra un resultado de 60m
    And asigna tarjeta blanca sin motivo
    Then la performance de "Atleta A" está en estado Ejecutada con tarjeta blanca
    And el evento TarjetaAsignada existe en el Event Store

  Scenario: Flujo con DNS registrado
    Given el atleta "Atleta B" tiene AP de 40m en estado Llamada
    When el juez registra DNS para "Atleta B"
    Then la performance de "Atleta B" está en estado DNS
    And el evento DNSRegistrado existe en el Event Store

  Scenario: Corrección de resultado después de asignar tarjeta
    Given el atleta "Atleta D" tiene tarjeta blanca asignada con resultado 55m
    When el juez corrige el resultado a 53m con motivo "error de lectura"
    Then el evento ResultadoCorregido existe en el Event Store
    And el Read Model de progreso refleja el resultado corregido

  Scenario: Verificación de la traza completa en el Event Store
    Given el flujo completo de los 5 atletas fue ejecutado
    When el juez consulta GET /competencia/comp-sp1-test/events
    Then la respuesta contiene 18 o más eventos en orden de secuencia
    And el progreso reporta 5 ejecutadas, 0 pendientes, 1 DNS

  Scenario: Consistencia entre Event Store y Read Models
    Given el flujo completo de los 5 atletas fue ejecutado
    When el juez consulta GET /competencia/comp-sp1-test/progreso
    Then ejecutadas = 5 y total = 5 y dns = 1
    And el Event Store tiene exactamente los mismos datos proyectados
```

---

## Impacto arquitectónico

- [ ] No — se implementa con la arquitectura existente
- [x] Sí → nuevo endpoint `GET /competencia/{id}/events` en `competencia/api/`

**Capa(s) afectadas:**
- [ ] Domain — sin cambios (todos los invariantes ya existen)
- [x] Application — nueva query `ObtenerEventos` con handler
- [x] Infrastructure — `SQLiteEventStore` ya tiene `load()`; el handler proyecta desde ahí
- [x] API — nuevo router endpoint + response schema

---

## Notas de implementación

- **No hay nueva lógica de dominio** — esta US verifica integración de lo ya implementado
- El endpoint `/events` proyecta el Event Store crudo (serialización de eventos como JSON)
- Los tests E2E se implementan como tests de integración en `tests/integration/competencia/`
- El escenario DoD se implementa como un test de integración E2E que ejecuta el flujo completo via comandos (no via HTTP) y verifica el Event Store + Read Models
- Los tests BDD de esta US viven en `tests/features/US-1.4.2.feature`
- En SP1 los `atleta_id` y `competencia_id` son UUIDs hardcodeados

---

## Referencias

- Incremento: 1.4 — Todo Conectado
- Bounded Context: Competencia
- Candidatas: `docs/plans/sp1/SP1-candidatas.md` (US-1.4.2)
- US relacionadas: US-1.2.1 a US-1.4.1 (prerequisitos del flujo)
- DoD SP1: 5 performances desde el celular + Event Store con traza completa
