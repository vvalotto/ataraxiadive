# Domain Model — AtaraxiaDive

| Campo | Valor |
|-------|-------|
| **Documento** | domain-model.md |
| **Capa IEDD** | Capa 2 — Modelo DDD |
| **Fecha** | 2026-03-18 |
| **Fuentes** | ES Big Picture · ES Competencia · Context Map v1.1 |
| **Estado** | ✅ v1.0 — Competencia completo; otros BCs en modelo de referencia |

---

## 1. Mapa General

```mermaid
graph TD
    subgraph COMPETENCIA["⭐ BC Competencia (Core Domain)"]
        C[Competencia\naggregate root]
        P[Performance\naggregate]
        PAR[Participante\nentidad]
        C --> P
        C --> PAR
        P --> PAR
    end

    subgraph TORNEO["🏆 BC Torneo (Supporting)"]
        T[Torneo\naggregate root]
        EO[EntidadOrganizadora\naggregate root]
        SE[Sede\naggregate root]
        T --> EO
        T --> SE
    end

    subgraph REGISTRO["📋 BC Registro (Supporting)"]
        AT[Atleta\naggregate root]
        INS[Inscripcion\naggregate]
        AT --> INS
    end

    subgraph RESULTADOS["🥇 BC Resultados (Supporting)"]
        RC[RankingCompetencia\naggregate root]
        OV[OverallTorneo\naggregate]
    end

    subgraph IDENTIDAD["🔐 BC Identidad (Generic)"]
        US[Usuario\naggregate root]
    end

    subgraph NOTIFICACIONES["🔔 BC Notificaciones (Generic · ES)"]
        NO[Notificacion\naggregate root]
    end

    TORNEO -->|InscripcionHabilitada| REGISTRO
    REGISTRO -->|ACL: AtletaInscripto → Participante| COMPETENCIA
    COMPETENCIA -->|CompetenciaFinalizada| RESULTADOS
    TORNEO -->|eventos| NOTIFICACIONES
    REGISTRO -->|eventos| NOTIFICACIONES
    RESULTADOS -->|eventos| NOTIFICACIONES
```

---

## 2. BC Competencia — Core Domain (detalle completo)

### 2.1 Aggregate: Competencia

```mermaid
classDiagram
    class Competencia {
        +CompetenciaId id
        +TorneoId torneoId
        +Disciplina disciplina
        +IntervaloDisciplina intervalo
        +GrillaDeSalida grilla
        +EstadoCompetencia estado
        +List~ParticipanteId~ participantes
        --
        +configurarIntervaloOT(intervalo) IntervaloOTConfigurado
        +generarGrilla() GrillaDeSalidaGenerada
        +ajustarGrilla(cambios) GrillaDeSalidaAjustada
        +confirmarGrilla() GrillaConfirmada
        +iniciar(juezId) CompetenciaIniciada
        +finalizar() CompetenciaFinalizada
    }

    class GrillaDeSalida {
        +List~EntradaGrilla~ entradas
        +estaConfirmada() bool
        +calcularOTs(intervalo) List~OT~
    }

    class EntradaGrilla {
        +ParticipanteId participanteId
        +Int posicion
        +Int andarivel
        +OT otProgramado
    }

    class IntervaloDisciplina {
        +Int minutos
        +validar() bool
    }

    Competencia "1" *-- "1" GrillaDeSalida
    GrillaDeSalida "1" *-- "N" EntradaGrilla
    Competencia "1" *-- "1" IntervaloDisciplina
```

**Eventos de dominio:**

| Evento | Disparado por |
|--------|--------------|
| `IntervaloOTConfigurado` | `configurarIntervaloOT()` |
| `GrillaDeSalidaGenerada` | `generarGrilla()` |
| `GrillaDeSalidaAjustada` | `ajustarGrilla()` |
| `GrillaConfirmada` | `confirmarGrilla()` |
| `CompetenciaIniciada` | `iniciar()` |
| `CompetenciaFinalizada` | `finalizar()` — disparado por política P-08 |

**Invariantes:** INV-C-01 a INV-C-04 (ver `event-storming-competencia.md`)

---

### 2.2 Aggregate: Performance

> **Estructura interna (US-4.1.5):** el aggregate fue descompuesto en tres módulos:
> `performance.py` (aggregate root + comandos), `performance_state.py` (aplicación de eventos),
> `performance_events.py` (builders de eventos). Los VOs `ResolucionTarjeta` y `RPFinal`
> encapsulan la lógica de tarjeta y cálculo de RP penalizado.

```mermaid
classDiagram
    class Performance {
        +PerformanceId id
        +CompetenciaId competenciaId
        +ParticipanteId participanteId
        +Disciplina disciplina
        +AP apDeclarado
        +RP rpMedido
        +EstadoPerformance estado
        --
        +rp() RP
        +registrarAP(valor, unidad) APRegistrado
        +llamar(otProgramado) AtletaLlamado
        +registrarResultado(valor, juezId) ResultadoRegistrado
        +asignarTarjeta(asignacion, juezId) TarjetaAsignada
        +registrarDNS(juezId) DNSRegistrado
        +corregirResultado(valor, motivo, juezId) ResultadoCorregido
    }

    class TarjetaAsignacion {
        +TipoTarjeta tipo
        +MotivoDQ motivoDQ
        +String motivoTexto
        +tuple~PenalizacionTecnica~ penalizaciones
        +validar() void
    }

    class ResolucionTarjeta {
        +TipoTarjeta tipo
        +MotivoDQ motivoDQ
        +tuple~PenalizacionTecnica~ penalizaciones
        +RPFinal rpFinal
        +desde_asignacion(asignacion, rpMedido) ResolucionTarjeta
    }

    class RPFinal {
        +Decimal valor
        +UnidadMedida unidad
        +desde_medicion(rpMedido, penalizaciones) RPFinal
    }

    class PenalizacionTecnica {
        +TipoPenalizacion tipo
        +Decimal deduccion
    }

    class MotivoDQ {
        <<enumeration>>
        BKO_SUPERFICIE
        BKO_SUBACUATICO
        NO_PROTOCOLO
        INFRACCION_TECNICA
        NO_INICIO_VENTANA
        SALIDA_FALSO
    }

    class AP {
        +Decimal valor
        +UnidadMedida unidad
        +validar() bool
    }

    Performance "1" *-- "1" AP
    Performance "1" *-- "0..1" ResolucionTarjeta
    ResolucionTarjeta "1" *-- "0..1" RPFinal
    ResolucionTarjeta "1" *-- "N" PenalizacionTecnica
    ResolucionTarjeta "1" *-- "0..1" MotivoDQ
    TarjetaAsignacion "1" *-- "0..1" MotivoDQ
    TarjetaAsignacion "1" *-- "N" PenalizacionTecnica
```

**Tipos de tarjeta (`TipoTarjeta`):**

| Valor | Significado | Requiere |
|-------|-------------|---------|
| `Blanca` | Performance válida sin infracciones | — |
| `BlancaConPenalizaciones` | Performance válida con infracciones técnicas; RP = medido − Σ deducciones | ≥1 `PenalizacionTecnica` |
| `Amarilla` | En revisión — debe cerrarse como Blanca, BlancaConPenalizaciones o Roja | — |
| `Roja` | Descalificación | `MotivoDQ` obligatorio |

**Eventos de dominio:**

| Evento | Disparado por |
|--------|--------------|
| `APRegistrado` | `registrarAP()` |
| `AtletaLlamado` | `llamar()` |
| `ResultadoRegistrado` | `registrarResultado()` |
| `TarjetaAsignada` | `asignarTarjeta()` — payload incluye `resolucion` con tipo, motivo, penalizaciones y rp_final |
| `DNSRegistrado` | `registrarDNS()` |
| `ResultadoCorregido` | `corregirResultado()` |

**Invariantes:** INV-P-01 a INV-P-14 (ver `event-storming-competencia.md`)

**Nota US-4.1.3:** la familia SPE queda desagregada en `SPE_2X50`, `SPE_4X50`,
`SPE_8X50` y `SPE_16X50` para torneos nuevos. Estas variantes usan segundos y
generan competencias/rankings independientes. `SPE` genérica se mantiene solo
como valor legacy para compatibilidad histórica.

---

### 2.3 Entidad: Participante

`Participante` es una entidad dentro del BC Competencia, creada mediante el ACL
que traduce `AtletaInscripto` (BC Registro) al modelo local.

```mermaid
classDiagram
    class Participante {
        +ParticipanteId id
        +AtletaId atletaId
        +String nombreCompleto
        +Categoria categoria
        +Genero genero
        +List~Disciplina~ disciplinasHabilitadas
    }

    class Categoria {
        +String nombre
        +derivarDeEdad(fechaNacimiento) Categoria
    }

    Participante "1" *-- "1" Categoria
```

> `Participante` no tiene aggregate propio. Es una entidad de consulta dentro de
> Competencia — los aggregates `Competencia` y `Performance` la referencian por id.
> Se actualiza cuando llega `DatosAtletaActualizados` desde Registro.

---

### 2.4 Enumeraciones y Value Objects compartidos

| Tipo | Valores / Descripción |
|------|-----------------------|
| `Disciplina` | STA, DNF, DYN, DBF, SPE, SPE_2X50, SPE_4X50, SPE_8X50, SPE_16X50, CNF, CWT, FIM, VWT |
| `EstadoCompetencia` | Preparacion, Confirmada, EnEjecucion, Finalizada |
| `EstadoPerformance` | AnunciadaAP, Llamada, Ejecutada, DNS |
| `TipoTarjeta` | Blanca, BlancaConPenalizaciones, Amarilla, Roja |
| `UnidadMedida` | Metros, Segundos |
| `OT` | DateTime con precisión de segundos |

---

## 3. BC Torneo — Supporting

> Modelo de referencia — detalle completo en ES Nivel 2 de Torneo (pendiente para SP3)

### Aggregates

| Aggregate | Tipo | Responsabilidad |
|-----------|------|-----------------|
| `Torneo` | Aggregate root | Ciclo de vida: Abierto → EnInscripcion → EnPreparacion → EnEjecucion → Cerrado / Cancelado |
| `EntidadOrganizadora` | Aggregate root | Catálogo de federaciones/clubs organizadores (CRUD) |
| `Sede` | Aggregate root | Catálogo de sedes físicas con datos de pileta (CRUD) |

### Value Objects de configuración del Torneo

| Value Object | Descripción |
|-------------|-------------|
| `FormulaPuntos` | Fórmula deportiva para calcular puntos por disciplina. Configurable por torneo (AIDA / CMAS / genérica). Consumida por BC Resultados para calcular el Overall. |
| `VentanaImpugnacion` | Lapso en minutos desde `CompetenciaFinalizada` durante el cual se permite `CorregirResultado`. Configurable por torneo. Consumida por BC Competencia como INV-P-15. |
| `TiempoAP` | Parser y normalizador de APs de tiempo en formato `MM:SS` o `HH:MM:SS` a segundos (`Decimal`). Reutilizable en seeds, ingesta y futuros flujos de registro/anuncio. |

### Eventos principales

| Evento | Descripción |
|--------|-------------|
| `TorneoCreado` | Torneo inicializado con EntidadOrganizadora y Sede seleccionadas |
| `DisciplinasSeleccionadas` | Lista de disciplinas del torneo definida |
| `FormulaPuntosConfigurada` | Fórmula de cálculo de Overall seleccionada para el torneo |
| `VentanaImpugnacionConfigurada` | Lapso de corrección de resultados establecido |
| `InscripcionHabilitada` | Publicado al bus → BC Registro puede aceptar inscripciones |
| `InscripcionCerrada` | Automática (fecha) o manual (organizador) |
| `TorneoCerrado` | Torneo finalizado — dispara notificaciones con resumen individual a todos los participantes |
| `TorneoCancelado` | Cancelación en cualquier fase — datos preservados |

---

## 4. BC Registro — Supporting

> Modelo de referencia — detalle completo en ES Nivel 2 de Registro (pendiente para SP3)

### Aggregates

| Aggregate | Tipo | Responsabilidad |
|-----------|------|-----------------|
| `Atleta` | Aggregate root | Datos personales, club, brevet, cuenta de usuario |
| `Inscripcion` | Aggregate | Participación de un atleta en un torneo específico |

### Eventos principales

| Evento | Descripción |
|--------|-------------|
| `AtletaRegistrado` | Primera vez que el atleta crea su perfil en el sistema |
| `AtletaInscripto` | Atleta se inscribe en un torneo — publicado al bus → ACL en Competencia |
| `InscripcionCancelada` | Atleta cancela su participación |
| `DatosAtletaActualizados` | Cambio en datos relevantes → ACL actualiza `Participante` en Competencia |

---

## 5. BC Resultados — Supporting

> Modelo de referencia — detalle completo en ES Nivel 2 de Resultados (pendiente para SP3)

### Aggregates

| Aggregate | Tipo | Responsabilidad |
|-----------|------|-----------------|
| `RankingCompetencia` | Aggregate root | Ranking por disciplina y categoría/género, derivado de `CompetenciaFinalizada` |
| `OverallTorneo` | Aggregate | Ranking general multi-disciplina del torneo por categoría/género |

### Eventos principales

| Evento | Descripción |
|--------|-------------|
| `ResultadosCalculados` | Ranking por disciplina calculado |
| `OverallCalculado` | Ranking general calculado (después de todas las disciplinas) |
| `ResultadosPublicados` | Publicación incremental por disciplina |
| `PremiosEntregados` | Registro administrativo del hecho de entrega — sin efectos secundarios ni notificaciones (HS-22: ✅) |

---

## 6. BC Identidad — Generic

> Modelo mínimo — candidato a solución externa en horizontes 2-3

### Aggregate

| Aggregate | Responsabilidad |
|-----------|-----------------|
| `Usuario` | Credenciales, roles (organizador, juez, atleta, admin), perfil básico |

**Contrato de salida:** JWT con `{ userId, role, exp }` — consumido por todos los BCs.

---

## 7. BC Notificaciones — Generic (Event Sourcing)

> `US-4.5.1` implementa el núcleo del aggregate y su event store propio.
> `US-4.5.2` implementa el adaptador email con Resend.
> `US-4.5.3` implementa P-10: `InscripcionConfirmada` -> email de confirmación.
> `US-4.5.4` implementa P-11: `ResultadosPublicados` -> email individual a atletas.
> `US-4.5.5` cablea P-10 al endpoint HTTP de inscripción desde `src/app.py`.

### Aggregate

| Aggregate | Tipo | Responsabilidad |
|-----------|------|-----------------|
| `Notificacion` | Aggregate root | Ciclo de vida de un intento de comunicación: `Solicitada -> Enviada | Fallida`; aplica idempotencia estructural por `evento_fuente_id` |

### Value Objects

| Tipo | Descripción |
|------|-------------|
| `NotificacionId` | UUID inmutable del aggregate |
| `EventoFuenteId` | Identificador del evento fuente que originó la notificación — clave de idempotencia |
| `Destinatario` | Email válido + nombre opcional del receptor |
| `ContenidoEmail` | Asunto no vacío + cuerpo de texto + HTML opcional |
| `CanalEnvio` | Enum `Email | Push` (`SP4` implementa solo `Email`) |

### Eventos propios

| Evento | Descripción |
|--------|-------------|
| `NotificacionSolicitada` | Primer evento del stream; captura destinatario, contenido, canal y `evento_fuente_id` |
| `NotificacionEnviada` | Marca el stream como exitoso y terminal; puede persistir `proveedor_id` |
| `NotificacionFallida` | Marca el stream como fallido y terminal; persiste `motivo` |

### Event Store propio

| Elemento | Decisión |
|----------|----------|
| Tabla | `notificaciones_events` |
| Stream ID | `notificacion-{notificacion_id}` |
| Índices | `stream_id` + `json_extract(payload, '$.evento_fuente_id')` |
| Regla de idempotencia | si existe `NotificacionEnviada` para un `evento_fuente_id`, un nuevo `SolicitarEnvio` no emite eventos |

### Puerto de repositorio

| Puerto | Responsabilidad |
|--------|-----------------|
| `NotificacionRepository` | Persistir y rehidratar streams; consultar si ya existe `NotificacionEnviada` por `evento_fuente_id` |

### Application

| Componente | Responsabilidad |
|------------|-----------------|
| `SolicitarEnvioHandler` | Crea `NotificacionSolicitada` si no existe un envío exitoso previo para el `evento_fuente_id` |
| `EnviarNotificacionHandler` | Rehidrata la notificación, llama `EmailPort` y registra `NotificacionEnviada` o `NotificacionFallida` |
| `PoliticaP10Handler` | Recibe `InscripcionConfirmada`, renderiza contenido y orquesta solicitud + envío de email al atleta |
| `PoliticaP11Handler` | Recibe `ResultadosPublicados`, crea una notificación por atleta y aplica idempotencia con clave compuesta `{evento.id}:{atleta_id}` |

### Templates e integración

| Componente | Responsabilidad |
|------------|-----------------|
| `InscripcionConfirmadaTemplate` | Genera asunto y cuerpo de email con atleta, torneo, fecha, sede y disciplinas |
| `ResultadosPublicadosTemplate` | Genera email individual con posición, RP, tarjeta, podio y link al ranking |
| `build_p10_handler` | Factory en `src/app.py` para componer P-10 con repositorio SQLite y `ResendEmailAdapter` |
| `build_on_inscripcion_confirmada_callback` | Adapter en `src/app.py` que enriquece `Inscripcion` con datos de Registro/Torneo y llama P-10 |
| `build_p11_handler` | Factory en `src/app.py` para componer P-11 con repositorio SQLite y `ResendEmailAdapter` |

### Puerto y adaptador de email

| Elemento | Responsabilidad |
|----------|-----------------|
| `EmailPort` | Contrato de envío para el canal email; recibe `Destinatario` y `ContenidoEmail`, retorna `provider_id` |
| `ResendEmailAdapter` | Adaptador HTTP concreto actual del BC; implementa `POST /emails` contra proveedor gestionado |

---

## 8. Repositorios (Puertos)

Por cada aggregate root se define un puerto de repositorio en el dominio.
La implementación vive en `infrastructure/`.

| BC | Aggregate Root | Repositorio (puerto) |
|----|---------------|----------------------|
| Competencia | `Competencia` | `CompetenciaRepository` |
| Competencia | `Performance` | `PerformanceRepository` |
| Torneo | `Torneo` | `TorneoRepository` |
| Torneo | `EntidadOrganizadora` | `EntidadOrganizadoraRepository` |
| Torneo | `Sede` | `SedeRepository` |
| Registro | `Atleta` | `AtletaRepository` |
| Registro | `Inscripcion` | `InscripcionRepository` |
| Resultados | `RankingCompetencia` | `RankingRepository` |
| Identidad | `Usuario` | `UsuarioRepository` |
| Notificaciones | `Notificacion` | `NotificacionRepository` |

> **Regla de Oro (§6 CLAUDE.md):** Los repositorios son interfaces definidas en
> `domain/`. Las implementaciones concretas (SQLite, event store) viven en
> `infrastructure/`. El dominio no conoce la implementación.

---

## 9. Próximo Paso

Este Domain Model es insumo directo para:

1. **Architecture doc** (`docs/design/architecture.md`) — estructura de capas, event store, bus
2. **US-IEDD de SP1** — los invariantes de Competencia son las precondiciones/postcondiciones

---

*Documento creado: 2026-03-18 — Semana 0, Fase 0*
*v1.0: Competencia completo; otros BCs en modelo de referencia*
*Fuentes: ES Big Picture + ES Competencia + Context Map v1.1*
*Mantenido por: Claude Cowork + Victor Valotto*
