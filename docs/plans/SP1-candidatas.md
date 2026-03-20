# SP1 — La Performance: Incrementos y US Candidatas

| Campo | Valor |
|-------|-------|
| **Subproyecto** | SP1 — La Performance |
| **Baseline objetivo** | BL-001 |
| **BC activo** | Competencia (núcleo — solo aggregate Performance) |
| **DoD del SP1** | 5 performances registradas desde el celular. Event Store muestra la traza completa. |
| **Fecha** | 2026-03-20 |

---

## Resumen de Incrementos

| Inc. | Nombre | Tipo | US candidatas | DoD observable |
|------|--------|------|---------------|----------------|
| **1.1** | Fundación técnica | Setup | — (tarea técnica) | `GET /health` → 200 · `competencia.db` con tabla `events` · todas las capas scaffold |
| **1.2** | El dominio habla | Domain | US-1.2.1 a US-1.2.6 | Tests unitarios del aggregate Performance pasan · EventStore persiste y recarga eventos |
| **1.3** | El juez ve y toca | API + Read Models | US-1.3.1 | Endpoints del flujo del juez responden · Read Models retornan datos correctos |
| **1.4** | Todo conectado | E2E | US-1.4.1 | Flujo AP → llamar → resultado → tarjeta ejecutable desde el celular |

---

## Incremento 1.1 — Fundación Técnica

**Objetivo:** walking skeleton. Sin lógica de negocio — solo la estructura que permite que
todo lo demás crezca encima.

**Tareas técnicas (no son US-IEDD):**

| Tarea | Entregable |
|-------|-----------|
| Scaffold BC Competencia con capas hexagonales | `src/competencia/{domain,application,infrastructure,api}/` |
| Puerto `EventStorePort` en `domain/ports/` | Interfaz con `append()` + `load()` + `load_from()` |
| Adaptador `SQLiteEventStore` en `infrastructure/event_store/` | Tabla `events` en `data/competencia.db` (ADR-008) |
| Migraciones Alembic para `competencia.db` | `infrastructure/migrations/` (ADR-009) |
| Health-check endpoint | `GET /health` → `{"status": "ok"}` |
| Test de integración del EventStore | Append + load en SQLite in-memory |

**DoD:** `pytest tests/unit/competencia/` y `pytest tests/integration/competencia/` pasan.
`GET /health` retorna 200.

---

## Incremento 1.2 — El Dominio Habla

**Objetivo:** aggregate `Performance` completo con todos sus invariantes y el Event Store.

### US-1.2.1 — Registrar AP

| Campo | Valor |
|-------|-------|
| **Comando** | `RegistrarAP` |
| **Evento** | `APRegistrado` |
| **Actor** | Atleta / Sistema |
| **Invariantes** | INV-P-01, INV-P-02, INV-P-03, INV-P-04 |

**Precondiciones:**
- No existe un AP activo del mismo atleta para esta disciplina y competencia
- El plazo de AP no ha vencido (`PlazoAPVencido` no emitido)
- La grilla no está confirmada (`GrillaConfirmada` no emitido)

**Postcondición:** `APRegistrado` persiste en el event stream. Performance en estado `AnunciadaAP`.

**Invariantes a proteger:**
- `valorAP > 0`
- Un único AP activo por (atleta, disciplina, competencia)
- No permitido después de `PlazoAPVencido`
- No permitido después de `GrillaConfirmada`

---

### US-1.2.2 — Llamar Atleta

| Campo | Valor |
|-------|-------|
| **Comando** | `LlamarAtleta` |
| **Evento** | `AtletaLlamado` |
| **Actor** | Sistema (según grilla) |
| **Invariantes** | INV-P-05 |

**Precondición:** Performance en estado `AnunciadaAP`.

> **Nota SP1:** en SP1 la Competencia está hardcodeada en estado `EnEjecucion`
> (el aggregate Competencia se implementa en SP2). INV-P-05 se verifica con stub.

**Postcondición:** `AtletaLlamado` persiste. Performance en estado `Llamada`.

**Invariantes:** `AtletaLlamado` solo si Competencia = `EnEjecucion`.

---

### US-1.2.3 — Registrar Resultado

| Campo | Valor |
|-------|-------|
| **Comando** | `RegistrarResultado` |
| **Evento** | `ResultadoRegistrado` |
| **Actor** | Juez |
| **Invariantes** | INV-P-06, INV-P-09 |

**Precondición:** Performance en estado `Llamada`.

**Postcondición:** `ResultadoRegistrado` persiste. Performance en estado `ResultadoRegistrado`.

**Invariantes:**
- Solo si Performance = `Llamada`
- Mutuamente excluyente con `DNSRegistrado`

---

### US-1.2.4 — Asignar Tarjeta

| Campo | Valor |
|-------|-------|
| **Comando** | `AsignarTarjeta` |
| **Evento** | `TarjetaAsignada` |
| **Actor** | Juez |
| **Invariantes** | INV-P-07, INV-P-11 |

**Precondición:** `ResultadoRegistrado` emitido. Performance en estado `ResultadoRegistrado`.

**Postcondición:** `TarjetaAsignada` persiste. Performance en estado `Ejecutada` (estado final).

**Invariantes:**
- Solo si `ResultadoRegistrado` previo
- `motivo` obligatorio si tarjeta = amarilla o roja

---

### US-1.2.5 — Registrar DNS

| Campo | Valor |
|-------|-------|
| **Comando** | `RegistrarDNS` |
| **Evento** | `DNSRegistrado` |
| **Actor** | Juez |
| **Invariantes** | INV-P-08, INV-P-09 |

**Precondición:** Performance en estado `Llamada`.

**Postcondición:** `DNSRegistrado` persiste. Performance en estado `DNS` (estado final).

**Invariantes:**
- Solo si Performance = `Llamada`
- Mutuamente excluyente con `ResultadoRegistrado`

---

### US-1.2.6 — Corregir Resultado

| Campo | Valor |
|-------|-------|
| **Comando** | `CorregirResultado` |
| **Evento** | `ResultadoCorregido` |
| **Actor** | Juez |
| **Invariantes** | INV-P-12, INV-P-13, INV-P-14 _(INV-P-15 diferido a SP3)_ |

**Precondición:** Performance en estado `Ejecutada`.

**Postcondición:** `ResultadoCorregido` persiste como nuevo evento. Read Model proyecta el valor corregido.

**Invariantes SP1:**
- `motivo` obligatorio — sin excepción
- No permitido si Performance = `DNS`
- Se corrige sobre el estado actual proyectado (no sobre eventos anteriores)

> **INV-P-15 diferido:** la ventana de impugnación (`ventanaImpugnacion`) es un atributo
> configurado en BC Torneo (no existe en SP1). Se implementa en SP3 cuando BC Torneo esté disponible.

---

## Incremento 1.3 — El Juez Ve y Toca

**Objetivo:** Read Models y API endpoints. El juez puede ver el estado actual y los próximos atletas.

### US-1.3.1 — Interfaz del Juez: Read Models y Endpoints

| Campo | Valor |
|-------|-------|
| **Actor** | Juez |
| **Endpoints** | `GET /competencia/{id}/performance/actual` · `GET /competencia/{id}/performance/proximas` · `GET /competencia/{id}/progreso` |

**Read Models a proyectar:**

| Read Model | Endpoint | Datos |
|-----------|----------|-------|
| `PerformanceActual` | `GET .../performance/actual` | atleta (nombre hardcodeado SP1), AP declarado, andarivel, estado |
| `ProximosAtletas` | `GET .../performance/proximas` | siguientes 3 según posición en grilla (orden por posicionGrilla) |
| `ProgresoCompetencia` | `GET .../progreso` | ejecutadas / total, DNS acumulados |

**Postcondición:** los tres endpoints retornan 200 con datos correctos proyectados desde el Event Store.

**Nota SP1:** `nombre del atleta` es un string hardcodeado — BC Registro no existe aún.

---

## Incremento 1.4 — Todo Conectado

**Objetivo:** flujo end-to-end verificable desde el celular.

### US-1.4.1 — Flujo Completo AP → Tarjeta

**Escenario de DoD:**
1. 5 atletas con AP registrado (datos hardcodeados)
2. Juez ejecuta el flujo desde el celular: llamar → resultado → tarjeta (para cada uno)
3. Al menos 1 DNS en el lote
4. Al menos 1 corrección de resultado
5. Event Store muestra la traza completa de los 5 atletas

**Verificación:** `GET /competencia/{id}/events` retorna la secuencia de eventos en orden.
Los Read Models son consistentes con el Event Store.

> **Black-out:** se registra como tarjeta roja con `motivo = "black-out"`.
> No requiere comando separado en v1 — es una convención de uso de `AsignarTarjeta`.

---

## Mapping US candidatas → US del ES Competencia

| US SP1 | US ES (event-storming-competencia.md) | Estado INV-P-15 |
|--------|---------------------------------------|-----------------|
| US-1.2.1 | US-P-01 (RegistrarAP) | — |
| US-1.2.2 | US-P-02 (LlamarAtleta) | — |
| US-1.2.3 | US-P-03 (RegistrarResultado) | — |
| US-1.2.4 | US-P-04 (AsignarTarjeta) | — |
| US-1.2.5 | US-P-05 (RegistrarDNS) | — |
| US-1.2.6 | US-P-06 (CorregirResultado) | INV-P-15 → SP3 |

**US del ES Competencia no asignadas a SP1:**
- US-C-01 a US-C-06 (aggregate Competencia: grilla, confirmación, inicio) → **SP2**

---

## Datos Hardcodeados en SP1

SP1 opera sin BC Registro, BC Torneo ni BC Identidad. Los datos que normalmente
vendrían de esos BCs se hardcodean:

| Dato | Fuente real | En SP1 |
|------|------------|--------|
| Datos del atleta (nombre, categoría) | BC Registro | String fijo en el comando |
| `competenciaId` activo | BC Competencia aggregate | UUID fijo en los tests |
| Estado de Competencia = `EnEjecucion` | BC Competencia aggregate | Stub que retorna siempre `EnEjecucion` |
| `ventanaImpugnacion` | BC Torneo | Sin validación (INV-P-15 diferido) |

---

## Próximos Pasos

1. Crear Milestone SP1 en GitHub
2. Crear Issues en GitHub por cada US (1.1 como issue técnico, 1.2.1 a 1.4.1 como US-IEDD)
3. Redactar `docs/plans/US-1.1.md` (tarea técnica) y `docs/plans/US-1.2.1.md` (primera US-IEDD)
4. Ejecutar `/implement-us US-1.2.1` como primer uso real del Dev Kit
