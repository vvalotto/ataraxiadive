# US-2.2.2: API Disciplina-Aware + Avance Automático

**Estado**: `Backlog`
**Incremento**: Inc 2.2 — Dos Mecánicas, un Modelo
**Subproyecto**: SP2 — La Competencia
**Agregado principal**: `Performance`
**Bounded Context**: `competencia`

---

## Descripción (lenguaje de negocio)

Como **juez**,
quiero **que el sistema valide que la unidad del resultado coincida con la disciplina que se está ejecutando y que la lista de próximos atletas respete el orden de la grilla oficial**
para **poder registrar performances de STA (tiempo) y DNF (distancia) sin confundir unidades, y ver siempre quién sigue según el orden establecido**.

---

## Contexto del dominio

### Modelo involucrado

| Elemento DDD | Nombre | Responsabilidad |
|---|---|---|
| Aggregate | `Performance` | `_apply_atleta_llamado` almacena `posicion_grilla` para ser consultada en queries |
| Port (de US-2.2.1) | `DisciplinaDescriptorPort` | Provee `unidad_esperada` para validación en handlers |
| Read Model (actualizar) | `PerformanceActual` | Agrega `unidad_esperada` para que el cliente muestre el campo correcto |
| Read Model (actualizar) | `ProximosAtletas` | Ordena por `posicion_grilla` en lugar de `occurred_at` |

### Lenguaje ubicuo relevante

- **Unidad incompatible**: error que se lanza cuando el juez registra un AP o RP en Metros para una disciplina STA (o en Segundos para DNF). El dominio nunca debe persistir una performance con unidad incorrecta.
- **Avance automático**: el sistema sabe qué atleta sigue en la grilla porque cada performance registra su `posicion_grilla` al ser llamada. `ProximosAtletas` usa ese dato para ordenar.
- **Disciplina-aware**: los endpoints y read models exponen información sobre la disciplina (qué unidad usar) para que el cliente pueda adaptar su interfaz.

---

## Especificación del comportamiento

### Operación 1: Validación de unidad en RegistrarResultado

**Precondición ampliada (nueva):**
La unidad del `RegistrarResultadoCommand` debe coincidir con `DisciplinaDescriptorPort.describe(disciplina).unidad_esperada`.

| | Descripción |
|---|---|
| **Precondición** | Performance en estado `Llamada`. Unidad del RP = `unidad_esperada` del descriptor de la disciplina. |
| **Postcondición** | `ResultadoRegistrado` persiste con la unidad validada. |
| **Excepciones** | `UnidadIncompatible` si la unidad no coincide con la disciplina (nueva excepción de aplicación). |

**Ejemplo concreto:**

```
Disciplina: STA, unidad_esperada: Segundos
RegistrarResultado(valor_rp=120, unidad=Metros)
→ UnidadIncompatible("STA requiere Segundos, recibido Metros")

RegistrarResultado(valor_rp=120, unidad=Segundos)
→ ResultadoRegistrado persiste correctamente
```

---

### Operación 2: Validación de unidad en RegistrarAP

Misma lógica que RegistrarResultado. Si el atleta declara un AP con unidad incorrecta, el handler lo rechaza antes de llamar al dominio.

| | Descripción |
|---|---|
| **Precondición** | `unidad` del `RegistrarAPCommand` = `unidad_esperada` del descriptor. |
| **Postcondición** | `APRegistrado` persiste. |
| **Excepciones** | `UnidadIncompatible` si la unidad no coincide. |

---

### Operación 3: posicion_grilla en Performance aggregate

`Performance._apply_atleta_llamado` almacena `posicion_grilla` como estado interno del aggregate.
Esto permite que queries reconstruyan el aggregate y consulten su posición sin re-parsear el payload del evento.

```python
# Antes
def _apply_atleta_llamado(self, payload):
    self._estado = EstadoPerformance.Llamada
    self._ot_programado = datetime.fromisoformat(payload["ot_programado"])

# Después
def _apply_atleta_llamado(self, payload):
    self._estado = EstadoPerformance.Llamada
    self._ot_programado = datetime.fromisoformat(payload["ot_programado"])
    self._posicion_grilla = payload["posicion_grilla"]   # ← nuevo
```

Nueva property: `performance.posicion_grilla: int | None` (None si no fue llamada aún).

---

### Operación 4: ObtenerProximasPerformances ordena por posicion_grilla

El handler `ObtenerProximasPerformancesHandler` actualmente ordena candidatos por `occurred_at`
(proxy válido en SP1, incorrecto en SP2 con grilla oficial).

**Comportamiento nuevo:** ordenar por `performance.posicion_grilla` ascendente entre las
performances en estado `AnunciadaAP` (que ya tienen `posicion_grilla` asignado por `AtletaLlamado`).

**Aclaración de estado:** `AnunciadaAP` es el estado pre-llamada. Las performances que ya fueron
llamadas (`Llamada`, `ResultadoRegistrado`, `Ejecutada`, `DNS`) no aparecen en "próximas".
La query filtra `AnunciadaAP` y ordena por `posicion_grilla`.

---

### Read Model: PerformanceActualDTO actualizado

Se agrega `unidad_esperada: str` al DTO `PerformanceActualDTO`:

```
PerformanceActualDTO:
  performance_id: str
  nombre_atleta: str
  ap_declarado: str
  unidad: str                  ← unidad del AP declarado (existente)
  unidad_esperada: str         ← unidad que el juez debe usar para el RP (nueva)
  andarivel: int
  estado: str
```

El endpoint `GET /competencia/{id}/performance/actual` incluye `unidad_esperada` en la respuesta.
El cliente usa este campo para mostrar "ingresar tiempo en segundos" o "ingresar distancia en metros".

---

## Criterios de aceptación (BDD)

```gherkin
Feature: API Disciplina-Aware — validación de unidades y avance por grilla

  Background:
    Given una competencia en estado EnEjecucion con 3 atletas en grilla STA
    And el orden de grilla es: posición 1 (AP 300s), posición 2 (AP 180s), posición 3 (AP 120s)

  Scenario: Registrar resultado STA con unidad correcta (Segundos)
    Given el atleta en posición 1 fue llamado
    When el juez registra resultado de 295 Segundos para STA
    Then ResultadoRegistrado persiste con unidad Segundos

  Scenario: Rechazo — registrar resultado STA con unidad incorrecta (Metros)
    Given el atleta en posición 1 fue llamado
    When el juez intenta registrar resultado de 295 Metros para STA
    Then el sistema rechaza con "UnidadIncompatible"
    And ningún evento es persistido

  Scenario: Registrar resultado DNF con unidad correcta (Metros)
    Given una competencia en estado EnEjecucion con disciplina DNF
    And el atleta fue llamado
    When el juez registra resultado de 85.50 Metros para DNF
    Then ResultadoRegistrado persiste con valor "85.50" y unidad Metros

  Scenario: Rechazo — registrar AP con unidad incorrecta
    Given una competencia STA en preparación
    When el atleta intenta declarar AP de 300 Metros para STA
    Then el sistema rechaza con "UnidadIncompatible"

  Scenario: ProximosAtletas respeta el orden de grilla
    Given el atleta en posición 1 fue llamado y completó su performance
    When el juez consulta GET /performance/proximas
    Then el primer resultado es el atleta en posición 2 (AP 180s)
    And el segundo resultado es el atleta en posición 3 (AP 120s)

  Scenario: PerformanceActual incluye unidad_esperada para STA
    Given el atleta en posición 1 está en estado Llamada
    When el juez consulta GET /performance/actual
    Then la respuesta incluye "unidad_esperada": "Segundos"

  Scenario: PerformanceActual incluye unidad_esperada para DNF
    Given una competencia DNF con atleta en estado Llamada
    When el juez consulta GET /performance/actual
    Then la respuesta incluye "unidad_esperada": "Metros"
```

---

## Impacto arquitectónico

**¿Esta US requiere una decisión arquitectónica?**
- [ ] No — amplía handlers existentes con el port de US-2.2.1, sin nuevos ADRs

**Capas afectadas:**
- [x] Domain — `Performance._apply_atleta_llamado` almacena `posicion_grilla`; property `posicion_grilla`
- [x] Application — `RegistrarResultadoHandler` y `RegistrarAPHandler` validan unidad via port; `ObtenerProximasPerformancesHandler` ordena por `posicion_grilla`; `ObtenerPerformanceActualHandler` agrega `unidad_esperada`
- [x] Infrastructure — `DisciplinaDescriptorAdapter` (de US-2.2.1) inyectado en los handlers afectados
- [x] API — `PerformanceActualDTO` agrega campo `unidad_esperada`; endpoint `GET /performance/actual` lo expone

**Nueva excepción de aplicación:** `UnidadIncompatible` — vive en `application/commands/registrar_resultado.py` y `registrar_ap.py` respectivamente. No es una excepción de dominio (el aggregate no la conoce — la validación la hace el handler antes de llamar al aggregate).

---

## DoD del Incremento 2.2

El DoD observable de Inc 2.2 es:

> **STA (tiempo) y DNF (distancia) funcionando · avance automático al siguiente atleta**

Verificación:
1. Registrar resultado STA en Segundos → persiste
2. Intentar registrar resultado STA en Metros → `UnidadIncompatible`
3. Registrar resultado DNF en Metros con decimales → persiste
4. `GET /performance/proximas` retorna atletas en orden de posicion_grilla, no occurred_at
5. `GET /performance/actual` incluye `unidad_esperada` correcto según disciplina

---

## Referencias

- Event Storming Competencia: `docs/design/event-storming-competencia.md` — P-06, Flujo 3
- SP2 candidatas: `docs/plans/sp2/SP2-candidatas.md` — Inc 2.2, US-2.2.2
- RF-EJ-08: distancia con decimales · RF-PR-05: criterio de ordenamiento
- US-2.2.1: `DisciplinaDescriptorPort` (prerequisito — debe implementarse primero)
- SP1 nota en `ObtenerProximasPerformancesHandler`: "En SP2, el orden será por posicion_grilla"

---

*Redactado: 2026-03-26 — IEDD Capa 3*
