# US-4.3.3: Casos alternativos — DNS, BKO y tarjeta blanca con penalizaciones

**Estado**: `To Do`
**Sprint**: SP4 — La Plataforma
**Incremento**: INC-4.3
**Bounded Context**: `frontend` + `competencia` (nuevo endpoint HTTP registrar-dns)
**Capas afectadas**: `competencia/api/router.py`, `frontend/src/pages/juez/`

---

## Descripción

Como **juez**,
quiero **registrar desde la UI los casos que se desvían del camino feliz** (atleta no se presenta, black-out, descalificación, penalizaciones técnicas)
para **cubrir el 100% de los escenarios reglamentarios del CMAS/FAAS sin salir de la aplicación**.

---

## Contexto del dominio

### Modelo involucrado

| Elemento DDD | Nombre | Responsabilidad |
|---|---|---|
| Command | `RegistrarDNSCommand` | Marca Performance como DNS |
| Command | `AsignarTarjetaCommand` | Tarjeta Roja con MotivoDQ, o Blanca con penalizaciones |
| Value Object | `MotivoDQ` | `BKO_SUPERFICIE` \| `BKO_SUBACUATICO` \| `NO_PROTOCOLO` \| `INFRACCION_TECNICA` \| `NO_INICIO_VENTANA` \| `SALIDA_FALSO` |
| Página | `DnsScreen` | Pantalla S-13 + S-14 |
| Página | `BkoScreen` | Pantalla S-12 — BKO con selector de distancia obligatorio |
| Componente | `MotivoDqSelector` | Selector de motivo de descalificación para tarjeta roja |
| Componente | `PenalizacionesSelector` | Contador de penalizaciones técnicas (0..N) para Blanca |

### Lenguaje ubicuo relevante

- **DNS (Did Not Start):** el atleta no se presentó al OT programado.
- **BKO (Black-out):** pérdida de conciencia durante o después de la actuación → tarjeta roja automática con motivo `BKO_SUPERFICIE` o `BKO_SUBACUATICO`.
- **MotivoDQ:** causa formal de descalificación — requerida cuando `tarjeta = Roja`.
- **Penalización técnica:** infracción técnica menor (ej. grabbers) que reduce el RP final en 3m por penalización acumulada.
- **Tarjeta Blanca con Penalizaciones:** performance válida pero con deducciones; RP final = RP medido − N×3m.

---

## Especificación del comportamiento

### Invariantes

- **INV-4.3.3-01:** DNS solo puede registrarse desde los Pasos 1 o 2 (antes de que el atleta inicie). No aplica después del `ATLETA INICIA`.
- **INV-4.3.3-02:** El botón `CONFIRMAR BKO` está deshabilitado si no se ingresó distancia (metros > 0 o cm > 0 obligatorio).
- **INV-4.3.3-03:** `tarjeta = Roja` requiere `motivo_dq` obligatorio. Sin motivo → backend rechaza con 422.
- **INV-4.3.3-04:** `tarjeta = Blanca` con `penalizaciones > 0` requiere que la disciplina admita penalizaciones (DNF, CWTB, FIM, CNF). STA y SPE no admiten penalizaciones.
- **INV-4.3.3-05:** Las penalizaciones son acumulables; cada una descuenta 3m del RP medido.

### Operación DNS

**Nombre**: `POST /competencia/{competencia_id}/registrar-dns`

| | Descripción |
|---|---|
| **Precondición** | Performance en `AnunciadaAP` o `Llamada`. |
| **Postcondición** | Performance en `DNS`. Evento `DNSRegistrado` persistido. |

**Body:**
```json
{ "participante_id": "uuid", "disciplina": "DNF", "registrado_por": "juez@ataraxia.com" }
```

### Operación BKO

Usa el endpoint existente `POST /competencia/{competencia_id}/asignar-tarjeta` con:
- `tarjeta = "Roja"`
- `motivo_dq = "BKO_SUPERFICIE"` o `"BKO_SUBACUATICO"`
- El RP medido hasta el momento del BKO (obligatorio)

El RP se registra primero con `POST /registrar-resultado`, luego se asigna la tarjeta.

### Operación Tarjeta Roja con MotivoDQ

Usa `POST /competencia/{competencia_id}/asignar-tarjeta` con:
```json
{ "participante_id": "uuid", "disciplina": "DNF", "tarjeta": "Roja", "motivo_dq": "NO_PROTOCOLO", "penalizaciones": 0, "registrado_por": "juez@ataraxia.com" }
```

### Operación Tarjeta Blanca con Penalizaciones

Usa `POST /competencia/{competencia_id}/asignar-tarjeta` con:
```json
{ "participante_id": "uuid", "disciplina": "DNF", "tarjeta": "Blanca", "penalizaciones": 2, "registrado_por": "juez@ataraxia.com" }
```
El backend calcula `rp_final = rp_medido − 2×3m`.

**Ejemplo concreto BKO:**

```
Precondición:  atleta García, Ana — Performance en Llamada, AP 75m
BKO en agua:   juez toca "⚡ BKO — Black-out" en Paso 4
Pantalla S-12: juez ingresa distancia alcanzada = 62m 50cm
Operación:     POST registrar-resultado { valor_rp: 62.50, unidad: Metros }
               POST asignar-tarjeta { tarjeta: Roja, motivo_dq: BKO_SUBACUATICO }
Postcondición: Performance en TarjetaAsignada — Roja (BKO_SUBACUATICO), RP=62.50m
```

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-4.3.3 — Casos alternativos del flujo de performance

  Background:
    Given el juez "juez@ataraxia.com" está autenticado
    And la competencia C1 de DNF está en EnEjecucion

  Scenario: DNS desde Paso 1 — atleta no se presenta
    Given el juez está en el Paso 1 de García, Ana
    When toca "DNS — No se presenta"
    Then ve la pantalla S-13 con los datos de García
    When toca "CONFIRMAR DNS"
    Then el backend recibe POST /competencia/C1/registrar-dns con participante_id de García
    And ve S-14 "DNS registrado — No se presentó"
    When toca "SIGUIENTE ATLETA →"
    Then regresa a la grilla con García marcada como DNS

  Scenario: BKO durante la performance — tarjeta roja automática
    Given el juez está en el Paso 4 (performance en curso) de García, Ana
    When toca "⚡ BKO — Black-out"
    Then ve la pantalla S-12 con selector de distancia obligatorio
    And el botón "CONFIRMAR BKO" está deshabilitado
    When ingresa 62m 50cm
    Then el botón "CONFIRMAR BKO" se habilita
    When toca "CONFIRMAR BKO — TARJETA ROJA"
    Then el backend recibe registrar-resultado con valor_rp=62.50
    And el backend recibe asignar-tarjeta con tarjeta=Roja y motivo_dq=BKO_SUBACUATICO
    And ve S-11 "Performance completada — TARJETA ROJA"

  Scenario: tarjeta roja por no seguir protocolo
    Given el juez está en el Paso 6 de García, Ana
    When toca "TARJETA ROJA"
    Then ve el selector de MotivoDQ
    When selecciona "No siguió protocolo"
    And toca "CONFIRMAR ROJA"
    Then el backend recibe asignar-tarjeta con tarjeta=Roja y motivo_dq=NO_PROTOCOLO

  Scenario: tarjeta blanca con penalizaciones en DNF
    Given el juez está en el Paso 6 de García, Ana (RP=75m registrado)
    When toca "TARJETA BLANCA"
    And agrega 2 penalizaciones técnicas
    And toca "CONFIRMAR BLANCA"
    Then el backend recibe asignar-tarjeta con tarjeta=Blanca y penalizaciones=2
    And la grilla muestra RP final de García como 69.00m (75 − 2×3)

  Scenario: penalizaciones no permitidas en STA
    Given el juez está en el Paso 6 de un atleta de STA
    When intenta agregar penalizaciones técnicas
    Then el selector de penalizaciones está deshabilitado con tooltip "STA no admite penalizaciones"
```

---

## Impacto arquitectónico

- [x] Sí → nuevo endpoint `POST /competencia/{id}/registrar-dns`

**Capa(s) afectadas:**
- [x] Infrastructure / API — `competencia/api/router.py` (1 nuevo endpoint: registrar-dns)
- [x] Frontend — `DnsScreen`, `BkoScreen`, `MotivoDqSelector`, `PenalizacionesSelector`

---

## Referencias

- Wireframes: `docs/design/ux/wireframes-juez.md §S-12, S-13, S-14`
- Command existente: `src/competencia/application/commands/registrar_dns.py`
- Value objects: `src/competencia/domain/value_objects/motivo_dq.py`, `penalizacion_tecnica.py`
- US precedente: `US-4.3.2` (flujo base + endpoints llamar/registrar-resultado/asignar-tarjeta)
- Dominio: tarjeta blanca con penalizaciones → `US-4.1.2`

---

## Notas de implementación

- **BKO:** el juez llega a S-12 desde Paso 4 (`BKO` button). El flujo llama primero a `registrar-resultado` con la distancia ingresada, luego a `asignar-tarjeta` con `motivo_dq`. El `motivo_dq` para BKO lo selecciona el juez: `BKO_SUPERFICIE` (BKO en superficie) o `BKO_SUBACUATICO` (BKO bajo el agua).
- **DQ sin pasar por Paso 5 (ej. no-inicio-ventana):** desde S-05 Paso 3, si el countdown vence, el juez registra DQ directamente. Como no hay RP, se usa `registrar-resultado` con `valor_rp=0` antes de `asignar-tarjeta`. Verificar con el dominio si acepta RP=0 para tarjeta roja.
- **`MotivoDqSelector`:** dropdown/selector con los 6 valores del enum `MotivoDQ`. Labels en español: BKO_SUPERFICIE → "Black-out en superficie", BKO_SUBACUATICO → "Black-out subacuático", etc.
- **`PenalizacionesSelector`:** contador simple con botones `−` y `+`. Deshabilitado si disciplina es STA o variante SPE.
- **Nuevo endpoint `POST /registrar-dns`:** usar `JuezDep` (rol JUEZ u ORGANIZADOR). `registrado_por` del JWT.

---

*Redactado: 2026-04-11 — INC-4.3 Interfaz del Juez*
