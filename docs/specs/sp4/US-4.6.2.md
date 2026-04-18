# US-4.6.2: Hash SHA-256 al cierre de disciplina

**Estado**: `To Do`
**Sprint**: SP4 — La Plataforma
**Incremento**: INC-4.6
**Bounded Context**: `competencia/domain/`, `competencia/infrastructure/`
**Capas afectadas**: `competencia/domain/aggregates/`, `competencia/infrastructure/event_store/`

---

## Descripción

Como **organizador**,
quiero **que al cerrar una disciplina se calcule y persista un hash SHA-256 de todos sus eventos**
para **poder verificar en cualquier momento que los resultados no fueron alterados después del cierre**.

---

## Contexto del dominio

### Modelo involucrado

| Elemento DDD | Nombre | Responsabilidad |
|---|---|---|
| Agregado | `Competencia` | Gestiona el ciclo de vida; el comando `CerrarCompetencia` dispara el hash |
| Evento de dominio | `CompetenciaCerrada` | Incluye el `hash_sha256` calculado como parte del payload del evento |
| Servicio de dominio | `CalculadorHashCompetencia` | Calcula el SHA-256 sobre la secuencia canónica de eventos de la disciplina |

### Lenguaje ubicuo relevante

- **Hash de disciplina:** digest SHA-256 de la concatenación ordenada (por `sequence_number`) de todos los eventos de todas las performances de una disciplina. Permite verificar integridad post-cierre.
- **Secuencia canónica:** los eventos ordenados por `sequence_number` ASC, serializados a JSON con campos ordenados alfabéticamente. Es la representación determinista que garantiza que el mismo conjunto de eventos siempre produce el mismo hash.
- **Cierre de disciplina:** el organizador ejecuta `CerrarCompetencia` cuando todos los atletas de una disciplina completaron su performance o fueron marcados DNS. Después del cierre no se aceptan nuevos eventos para esa disciplina.

---

## Especificación del comportamiento

### Invariantes

- **INV-4.6.2-01:** El hash se calcula **solo en el momento del cierre**. No se recalcula después.
- **INV-4.6.2-02:** El hash incluye **todos** los eventos de todas las performances de la disciplina cerrada, en orden estricto por `sequence_number`.
- **INV-4.6.2-03:** Si la competencia ya está cerrada, el comando `CerrarCompetencia` se rechaza (INV previo del aggregate `Competencia`).
- **INV-4.6.2-04:** El hash se persiste como parte del evento `CompetenciaCerrada` en el event store — no como campo separado de la tabla.
- **INV-4.6.2-05:** Una disciplina sin performances registradas produce un hash del conjunto vacío (SHA-256 de cadena vacía = valor fijo conocido).

### Operación principal

**Nombre**: `CerrarCompetencia(competencia_id, disciplina)`

| | Descripción |
|---|---|
| **Precondición** | La competencia existe y está en estado `EnEjecucion`; todas las performances tienen tarjeta asignada o DNS |
| **Postcondición** | La competencia pasa a estado `Cerrada`; se emite `CompetenciaCerrada` con `hash_sha256` en el payload |
| **Eventos generados** | `CompetenciaCerrada { competencia_id, disciplina, hash_sha256, timestamp_cierre }` |
| **Excepciones** | Error si quedan performances sin cerrar (atletas en estado `AnunciadaAP`, `Llamada`, `ResultadoRegistrado` sin tarjeta) |

**Algoritmo del hash:**

```
1. Recuperar del event store todos los eventos de la competencia,
   ordenados por sequence_number ASC.

2. Para cada evento, serializar a JSON canónico:
   - campos ordenados alfabéticamente
   - sin campos de metadata (id interno de la fila)
   - incluir: tipo, sequence_number, timestamp, datos del payload

3. Concatenar los JSON separados por "\n".

4. Calcular SHA-256 de la cadena resultante (UTF-8).

5. El digest hex (64 caracteres) es el hash_sha256.
```

**Ejemplo concreto:**

```
CerrarCompetencia(competencia_id="comp-abc", disciplina="DNF")

Eventos de la disciplina (10 atletas × ~3 eventos = ~30 eventos):
  seq=1  PerformanceRegistrada {atleta_id: "ath-001", ap: 60.0}
  seq=2  PerformanceRegistrada {atleta_id: "ath-002", ap: 55.0}
  ...
  seq=30 TarjetaAsignada {atleta_id: "ath-010", tarjeta: "Blanca"}

hash_sha256 = "a3f7c2..." (64 hex chars)

CompetenciaCerrada emitido:
  { competencia_id: "comp-abc", disciplina: "DNF",
    hash_sha256: "a3f7c2...", timestamp_cierre: "2026-05-15T14:00:00Z" }
```

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-4.6.2 — Hash SHA-256 al cierre de disciplina

  Background:
    Given existe una competencia "comp-abc" con disciplina DNF en estado EnEjecucion
    And todos los atletas tienen performance cerrada (tarjeta o DNS)

  Scenario: hash calculado y persistido al cerrar
    When el organizador ejecuta CerrarCompetencia("comp-abc", "DNF")
    Then la competencia pasa a estado Cerrada
    And el evento CompetenciaCerrada contiene un campo "hash_sha256" de 64 caracteres hex
    And el hash está persistido en el event store como parte del payload del evento

  Scenario: el hash es determinista — mismo input produce mismo hash
    Given el conjunto de eventos de la disciplina es fijo (no cambia)
    When se calcula el hash dos veces sobre el mismo conjunto
    Then ambos resultados son idénticos

  Scenario: el hash cambia si se altera un evento (verificación de integridad)
    Given el hash original fue "a3f7c2..."
    When se modifica directamente en la DB el payload de cualquier evento de la disciplina
    And se recalcula el hash sobre el conjunto modificado
    Then el nuevo hash es diferente de "a3f7c2..."

  Scenario: disciplina con performances pendientes no puede cerrarse
    Given existe un atleta con estado "ResultadoRegistrado" sin tarjeta asignada
    When el organizador intenta CerrarCompetencia
    Then el sistema rechaza la operación con error "performances_pendientes"
    And el estado de la competencia permanece EnEjecucion

  Scenario: disciplina sin ninguna performance (0 atletas)
    Given la disciplina no tiene performances registradas
    When el organizador cierra la competencia
    Then CompetenciaCerrada se emite con hash SHA-256 del conjunto vacío
    And el hash es el valor fijo conocido de SHA-256("")
```

---

## Impacto arquitectónico

- [ ] No — se implementa con la arquitectura existente

**Notas de implementación:**

- El `CalculadorHashCompetencia` vive en `competencia/domain/` como servicio de dominio puro (no depende de infraestructura).
- Recibe como input la lista de eventos ya cargados — la query al event store la hace la infrastructure layer antes de llamar al servicio.
- Usar `hashlib.sha256` de la stdlib — sin dependencias externas.

**Capa(s) afectadas:**
- [x] Domain — nuevo servicio de dominio `CalculadorHashCompetencia`
- [x] Domain — extensión del comando `CerrarCompetencia` y del evento `CompetenciaCerrada`
- [x] Infrastructure — el event store recupera los eventos para pasárselos al servicio de dominio

---

## Referencias

- Plan SP4 §INC-4.6 — US-4.6.2
- ADR-001: Event Sourcing — la inmutabilidad del event store es el fundamento del hash
- ADR-008: event store SQLite — fuente de los eventos
- US-4.6.1 prerrequisito: los mismos eventos que expone el audit log son los que se hashean
- US-4.6.3: la UI muestra el hash al organizador cuando la disciplina está cerrada

---

*Redactado: 2026-04-15 — INC-4.6 Auditoría y Exportación*
