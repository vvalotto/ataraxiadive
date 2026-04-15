# US-4.6.1: API de audit log — secuencia de eventos de una performance

**Estado**: `To Do`
**Sprint**: SP4 — La Plataforma
**Incremento**: INC-4.6
**Bounded Context**: `competencia/api/`
**Capas afectadas**: `competencia/api/`, `competencia/application/queries/`

---

## Descripción

Como **organizador**,
quiero **consultar la secuencia completa de eventos de una performance**
para **auditar el historial de registro: qué se registró, cuándo, y si hubo correcciones**.

---

## Contexto del dominio

### Modelo involucrado

| Elemento DDD | Nombre | Responsabilidad |
|---|---|---|
| Agregado | `Performance` | Raíz del aggregate; sus eventos forman el audit log |
| Evento de dominio | `PerformanceRegistrada`, `TarjetaAsignada`, `ResultadoCorregido`, `DNSRegistrado`, … | Cada evento es una entrada inmutable del log |
| Query | `ObtenerAuditLog` | Recupera la secuencia ordenada de eventos de una performance desde el event store |

### Lenguaje ubicuo relevante

- **Audit log:** secuencia ordenada e inmutable de los eventos de dominio que componen el historial de una performance. No es un log técnico — es el registro oficial de lo que ocurrió.
- **Corrección:** un organizador puede corregir un resultado ya registrado (comando `CorregirPerformance`). La corrección agrega un evento nuevo; el evento original permanece intacto en el log.

---

## Especificación del comportamiento

### Invariantes

- **INV-4.6.1-01:** El audit log es de solo lectura. No se puede modificar ni eliminar ningún evento del log a través de esta API.
- **INV-4.6.1-02:** Los eventos se devuelven en orden cronológico estricto (por `sequence_number` del event store).
- **INV-4.6.1-03:** Si la performance no existe, el endpoint devuelve 404.
- **INV-4.6.1-04:** Solo el organizador del torneo puede consultar el audit log (rol `organizador` o `admin`).

### Operación principal

**Nombre**: `GET /competencias/{competencia_id}/performances/{atleta_id}/audit-log`

| | Descripción |
|---|---|
| **Precondición** | La competencia y la performance existen; el solicitante es organizador |
| **Postcondición** | Se devuelve la lista ordenada de eventos del aggregate `Performance` para ese atleta |
| **Excepciones** | 404 si competencia o atleta no existen · 403 si el rol no es organizador |

**Respuesta esperada:**

```json
{
  "competencia_id": "comp-abc",
  "atleta_id": "ath-123",
  "atleta_nombre": "Martín García",
  "disciplina": "DNF",
  "eventos": [
    {
      "sequence": 1,
      "tipo": "PerformanceRegistrada",
      "timestamp": "2026-05-15T10:05:00Z",
      "datos": { "ap": 60.0 }
    },
    {
      "sequence": 2,
      "tipo": "ResultadoRegistrado",
      "timestamp": "2026-05-15T10:12:34Z",
      "datos": { "rp": 58.0 }
    },
    {
      "sequence": 3,
      "tipo": "TarjetaAsignada",
      "timestamp": "2026-05-15T10:12:40Z",
      "datos": { "tarjeta": "Blanca", "penalizaciones": 0 }
    }
  ]
}
```

**Ejemplo concreto:**

```
GET /competencias/comp-abc/performances/ath-123/audit-log
  → 200 OK
  → 3 eventos en orden: PerformanceRegistrada → ResultadoRegistrado → TarjetaAsignada

GET /competencias/comp-abc/performances/ath-999/audit-log
  → 404 Not Found
```

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-4.6.1 — API audit log de performance

  Background:
    Given existe una competencia "comp-abc" con disciplina DNF
    And el atleta "ath-123" tiene 3 eventos registrados en el event store

  Scenario: organizador consulta audit log exitosamente
    Given el usuario autenticado tiene rol organizador
    When hace GET /competencias/comp-abc/performances/ath-123/audit-log
    Then la respuesta es 200 OK
    And contiene 3 eventos en orden cronológico
    And el primer evento es de tipo "PerformanceRegistrada"

  Scenario: los eventos incluyen correcciones si las hubo
    Given la performance del atleta fue corregida (4 eventos: reg + resultado + tarjeta + corrección)
    When el organizador consulta el audit log
    Then la respuesta incluye 4 eventos
    And el último evento es de tipo "ResultadoCorregido"
    And el evento original de resultado NO fue eliminado del log

  Scenario: performance inexistente
    When el organizador hace GET con atleta_id="ath-999" que no existe
    Then la respuesta es 404 Not Found

  Scenario: juez no puede consultar audit log
    Given el usuario autenticado tiene rol juez
    When hace GET /competencias/comp-abc/performances/ath-123/audit-log
    Then la respuesta es 403 Forbidden

  Scenario: los eventos están en orden cronológico estricto
    Given la performance tiene eventos con sequence_number 1, 2, 3
    When el organizador consulta el audit log
    Then los eventos aparecen en el orden sequence 1 → 2 → 3
    And el campo "sequence" de cada evento refleja ese orden
```

---

## Impacto arquitectónico

- [ ] No — se implementa con la arquitectura existente

**Capa(s) afectadas:**
- [x] Application — nueva query `ObtenerAuditLog` en `competencia/application/queries/`
- [x] Infrastructure — el event store SQLite ya persiste los eventos; la query los lee directamente
- [x] API — nuevo endpoint en `competencia/api/router.py`

---

## Referencias

- Plan SP4 §INC-4.6 — US-4.6.1
- ADR-001: Event Sourcing — el event store es la fuente del audit log
- ADR-008: event store SQLite — estructura de la tabla de eventos
- Prerrequisito de US-4.6.2 (hash SHA-256) y US-4.6.3 (UI auditoría)

---

*Redactado: 2026-04-15 — INC-4.6 Auditoría y Exportación*
