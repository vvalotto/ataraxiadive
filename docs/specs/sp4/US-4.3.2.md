# US-4.3.2: Flujo de performance — los 6 pasos conectados al backend

**Estado**: `To Do`
**Sprint**: SP4 — La Plataforma
**Incremento**: INC-4.3
**Bounded Context**: `frontend` + `competencia` (nuevos endpoints HTTP)
**Capas afectadas**: `competencia/api/router.py`, `frontend/src/pages/juez/`

---

## Descripción

Como **juez**,
quiero **ejecutar el flujo completo de una performance desde mi celular** (llamar → confirmar → iniciar → finalizar → registrar marca → asignar tarjeta)
para **registrar cada actuación en el backend sin necesidad de papel ni PC**.

---

## Contexto del dominio

### Modelo involucrado

| Elemento DDD | Nombre | Responsabilidad |
|---|---|---|
| Aggregate | `Performance` | Ciclo de vida de la actuación de un atleta |
| Command | `LlamarAtletaCommand` | Mueve Performance de AnunciadaAP → Llamada |
| Command | `RegistrarResultadoCommand` | Mueve Performance de Llamada → ResultadoRegistrado |
| Command | `AsignarTarjetaCommand` | Mueve Performance de ResultadoRegistrado → TarjetaAsignada |
| Evento | `AtletaLlamado` | Performance en Llamada, OT programado |
| Evento | `ResultadoRegistrado` | RP registrado en metros/cm |
| Evento | `TarjetaAsignada` | Resultado final (Blanca/Roja) |
| Página | `GrillaJuez` | Pantalla S-02 — grilla de salida con estados |
| Página | `PasosPerformance` | Pantallas S-03 a S-09 — wizard 6 pasos |
| Componente | `StepIndicator` | Indicador visual de paso actual (6 puntos) |
| Componente | `AtletaCard` | Card con nombre, AP, andarivel, OT |
| Componente | `RpSelector` | Selector de metros (presets + ajuste) + numpad cm |

### Lenguaje ubicuo relevante

- **OT (Official Top):** momento exacto en que el atleta puede iniciar su actuación.
- **AP (Announced Performance):** marca declarada antes de la competencia.
- **RP (Realized Performance):** marca efectivamente lograda — se ingresa en metros + cm.
- **Llamada:** estado de la Performance después de que el juez llamó al atleta.
- **Grilla de salida:** lista ordenada por OT de todos los atletas de la disciplina.

---

## Especificación del comportamiento

### Invariantes

- **INV-4.3.2-01:** Un atleta solo puede ser llamado si su Performance está en estado `AnunciadaAP` (no permite doble-llamada).
- **INV-4.3.2-02:** El RP solo puede registrarse si la Performance está en `Llamada`.
- **INV-4.3.2-03:** La tarjeta solo puede asignarse si la Performance está en `ResultadoRegistrado`.
- **INV-4.3.2-04:** El botón `CONFIRMAR MARCA` está deshabilitado si metros = 0 y cm no ingresado.
- **INV-4.3.2-05:** En Paso 6, solo se puede asignar Blanca o Roja (no Amarilla — Amarilla es US-4.3.4). El path feliz de esta US termina en S-09 Resultado Blanca.

### Operación principal — LlamarAtleta

**Nombre**: `POST /competencia/{competencia_id}/llamar`

| | Descripción |
|---|---|
| **Precondición** | Competencia en `EnEjecucion`. Performance en `AnunciadaAP`. Andarivel libre (INV-C-05). |
| **Postcondición** | Performance en `Llamada`. Evento `AtletaLlamado` persistido. |
| **Excepciones** | 409 si Performance no está en AnunciadaAP. 409 si andarivel ocupado. |

**Body:**
```json
{ "participante_id": "uuid", "disciplina": "DNF", "ot_programado": "ISO8601", "posicion_grilla": 3, "andarivel": 1 }
```

### Operación secundaria — RegistrarResultado

**Nombre**: `POST /competencia/{competencia_id}/registrar-resultado`

| | Descripción |
|---|---|
| **Precondición** | Performance en `Llamada`. |
| **Postcondición** | Performance en `ResultadoRegistrado`. Evento `ResultadoRegistrado` persistido. |

**Body:**
```json
{ "participante_id": "uuid", "disciplina": "DNF", "valor_rp": 75.43, "unidad": "Metros", "registrado_por": "juez@ataraxia.com" }
```

### Operación secundaria — AsignarTarjeta (camino feliz)

**Nombre**: `POST /competencia/{competencia_id}/asignar-tarjeta`

| | Descripción |
|---|---|
| **Precondición** | Performance en `ResultadoRegistrado`. `tarjeta` ∈ {Blanca, Roja} (Amarilla → US-4.3.4). |
| **Postcondición** | Performance en `TarjetaAsignada`. Evento `TarjetaAsignada` persistido. |

**Body:**
```json
{ "participante_id": "uuid", "disciplina": "DNF", "tarjeta": "Blanca", "penalizaciones": 0, "registrado_por": "juez@ataraxia.com" }
```

**Ejemplo concreto:**

```
Precondición:  competencia C1 EnEjecucion, atleta P1 AnunciadaAP con AP 75m
Paso 1+2:      POST /competencia/C1/llamar → AtletaLlamado{P1, OT=14:00, andarivel=1}
Paso 3-4:      UI solamente (cronómetro, ventana OT)
Paso 5:        POST /competencia/C1/registrar-resultado → ResultadoRegistrado{P1, RP=72.00m}
Paso 6:        POST /competencia/C1/asignar-tarjeta { tarjeta=Blanca } → TarjetaAsignada{P1, Blanca}
Postcondición: Performance P1 en TarjetaAsignada. S-09 muestra "TARJETA BLANCA — 72.00m"
```

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-4.3.2 — Flujo de 6 pasos de performance conectado al backend

  Background:
    Given el juez "juez@ataraxia.com" está autenticado
    And la competencia C1 de disciplina DNF está en estado EnEjecucion
    And el atleta "García, Ana" tiene AP 75m en AnunciadaAP

  Scenario: flujo completo exitoso — tarjeta blanca
    Given el juez está en la grilla de la competencia C1
    When toca la fila de "García, Ana" (estado SIGUIENTE)
    Then ve el Paso 1 con el botón "LLAMAR ATLETA"
    When toca "LLAMAR ATLETA"
    Then el backend recibe POST /competencia/C1/llamar con participante_id de García
    And la grilla actualiza el estado de García a "▶ EN CURSO"
    When avanza hasta el Paso 5 e ingresa 72m 00cm
    And toca "CONFIRMAR MARCA"
    Then el backend recibe POST /competencia/C1/registrar-resultado con valor_rp=72.00
    When en el Paso 6 toca "TARJETA BLANCA"
    Then el backend recibe POST /competencia/C1/asignar-tarjeta con tarjeta=Blanca
    And ve la pantalla S-09 "Performance completada — TARJETA BLANCA — 72.00m"
    When toca "SIGUIENTE ATLETA →"
    Then regresa a la grilla S-02

  Scenario: grilla muestra estado correcto de cada atleta
    Given la grilla tiene atletas en estados AnunciadaAP, Llamada y TarjetaAsignada
    When el juez accede a /juez/grilla
    Then el atleta TarjetaAsignada aparece con opacidad reducida (no tappable)
    And el atleta Llamada aparece con borde accent (SIGUIENTE)
    And el atleta AnunciadaAP aparece con estado PENDIENTE (tappable)

  Scenario: botón CONFIRMAR MARCA deshabilitado sin RP ingresado
    Given el juez está en el Paso 5
    When no ingresa ningún valor de metros ni centímetros
    Then el botón "CONFIRMAR MARCA" está deshabilitado

  Scenario: error del backend muestra mensaje inline
    Given el juez intenta llamar a un atleta ya llamado
    When el backend responde 409
    Then la pantalla muestra "No se puede ejecutar esta acción en el estado actual"
    And el juez permanece en el Paso 1
```

---

## Impacto arquitectónico

- [x] Sí → exposición de 3 nuevos endpoints HTTP en `competencia/api/router.py`

Los commands `LlamarAtletaHandler`, `RegistrarResultadoHandler` y `AsignarTarjetaHandler` ya existen en `competencia/application/commands/`. Solo falta agregar los endpoints al router.

**Capa(s) afectadas:**
- [x] Infrastructure / API — `competencia/api/router.py` (3 nuevos endpoints)
- [x] Frontend — `GrillaJuez`, `PasosPerformance`, `StepIndicator`, `AtletaCard`, `RpSelector`, `NumpadCm`

---

## Referencias

- Wireframes: `docs/design/ux/wireframes-juez.md §S-02 a S-09`
- Commands existentes: `src/competencia/application/commands/llamar_atleta.py`, `registrar_resultado.py`, `asignar_tarjeta.py`
- Plan SP4: `docs/plans/sp4/PLAN-SP4.md §INC-4.3`
- Tokens de color del tema dark: `docs/design/ux/wireframes-juez.md §Principios de diseño`

---

## Notas de implementación

- **Nuevos endpoints (backend):**
  - `POST /competencia/{competencia_id}/llamar` → `LlamarAtletaHandler`
  - `POST /competencia/{competencia_id}/registrar-resultado` → `RegistrarResultadoHandler`
  - `POST /competencia/{competencia_id}/asignar-tarjeta` → `AsignarTarjetaHandler`
  - Autenticación: `JuezDep` (requiere rol JUEZ u ORGANIZADOR).
  - El campo `registrado_por` se extrae del JWT (`payload["email"]`).
- **Paso 2 (Confirmar presencia) y Paso 3 (OT) son estado local de UI** — no generan llamadas al backend. El cronómetro del Paso 4 corre en el cliente.
- **`RpSelector`:** metros via presets `[25, 50, 75, 100, 125]` + botones `±1/+5/+10`. Centímetros via numpad 3×3 (2 dígitos, rango 00–99, ingreso shift-left).
- **Grilla:** `GET /competencia/{id}/grilla` + `GET /competencia/{id}/performance/actual` para determinar quién es el SIGUIENTE.
- **`useCompetenciaStore`:** agregar `atletaActivo: AtletaGrillaDTO | null` para pasar datos entre pantallas.
- **Paso 6 en esta US:** solo Blanca y Roja (sin penalizaciones ni Amarilla). Penalizaciones y Amarilla se agregan en US-4.3.3 y US-4.3.4 respectivamente.

---

*Redactado: 2026-04-11 — INC-4.3 Interfaz del Juez*
