# 30 Runtime Interactions

## Propósito

Describir las interacciones dinámicas más relevantes entre bounded contexts y
componentes principales de AtaraxiaDive.

Esta vista complementa los documentos estructurales mostrando cómo fluye la
información en runtime, qué dependencias síncronas existen y dónde aparecen
integraciones asíncronas entre contextos.

## Alcance

Incluye:

- flujos síncronos dentro de un BC;
- interacciones entre BCs por ACL, lookup o claims;
- flujos asíncronos previstos por eventos de dominio;
- diferencias entre interacciones implementadas y objetivo arquitectónico.

No cubre el detalle offline-first del juez, que se documenta por separado en
`50-offline-sync.md`.

## Fuentes

- `docs/architecture/20-context-map-integrations.md`
- `docs/architecture/10-bc-competencia.md`
- `docs/architecture/11-bc-torneo.md`
- `docs/architecture/12-bc-registro.md`
- `docs/architecture/13-bc-resultados.md`
- `docs/architecture/14-bc-identidad.md`
- `docs/architecture/15-bc-notificaciones.md`
- `docs/design/context-map.md`
- `docs/adr/ADR-003-offline-first-pwa.md`
- `src/`

## Principios de interacción

Las interacciones de runtime deben respetar estas reglas:

- cada BC persiste únicamente en su propia base;
- la autenticación se resuelve por verificación local de JWT;
- los BCs funcionales no dependen de `Notificaciones` para completar su caso de
  uso;
- las dependencias cross-BC deben quedar contenidas en ACLs, lookups read-only o
  consumo de eventos;
- cuando exista una brecha entre diseño e implementación, esa brecha debe ser
  explícita.

## Escenario 1: autenticación y uso de claims

Este flujo muestra cómo `Identidad` autentica y cómo los demás BCs consumen el
token sin consultar de nuevo al BC emisor.

```mermaid
sequenceDiagram
    actor U as Usuario
    participant ID_API as Identidad API
    participant ID_APP as AutenticarUsuarioHandler
    participant ID_REPO as UsuarioRepository
    participant JWT as JWTService
    participant BC_API as API de BC consumidor

    U->>ID_API: POST /auth/login(email, password)
    ID_API->>ID_APP: AutenticarUsuarioCommand
    ID_APP->>ID_REPO: find_by_email(email)
    ID_REPO-->>ID_APP: Usuario
    ID_APP->>JWT: generate(usuario)
    JWT-->>ID_APP: access_token
    ID_APP-->>ID_API: TokenResponse
    ID_API-->>U: JWT bearer

    U->>BC_API: Request con Authorization: Bearer <token>
    BC_API->>JWT: verify(token)
    JWT-->>BC_API: claims {sub, email, rol, exp}
    BC_API-->>U: operación autorizada o 401
```

### Observaciones

- `Identidad` es upstream y el BC consumidor adopta una relación `Conformist`.
- La verificación del token es local; no hay llamada síncrona a `Identidad` en
  cada request.
- Este flujo está implementado en `src/identidad/`.

## Escenario 2: inscripción de atleta a torneo

Este flujo muestra el caso de uso principal de `Registro`, incluyendo el ACL
read-only hacia `Torneo`.

```mermaid
sequenceDiagram
    actor A as Atleta
    participant REG_API as Registro API
    participant REG_APP as InscribirAtletaHandler
    participant TOR_ACL as TorneoConsultaPort / SQLiteTorneoConsulta
    participant TOR_DB as torneo.db
    participant INS_REPO as InscripcionRepository
    participant REG_DB as registro.db

    A->>REG_API: POST /registro/inscripciones
    REG_API->>REG_APP: InscribirAtletaCommand
    REG_APP->>TOR_ACL: esta_abierto_para_inscripcion(torneoId)
    TOR_ACL->>TOR_DB: SELECT estado
    TOR_DB-->>TOR_ACL: INSCRIPCION_ABIERTA / otro
    TOR_ACL-->>REG_APP: bool

    REG_APP->>TOR_ACL: obtener_disciplinas(torneoId)
    TOR_ACL->>TOR_DB: SELECT torneo / datos disponibles
    TOR_DB-->>TOR_ACL: datos mínimos del torneo
    TOR_ACL-->>REG_APP: disciplinas habilitadas

    REG_APP->>INS_REPO: find_by_atleta_y_torneo(atletaId, torneoId)
    INS_REPO->>REG_DB: SELECT inscripciones
    REG_DB-->>INS_REPO: inscripción existente / none
    INS_REPO-->>REG_APP: resultado

    REG_APP->>INS_REPO: save(Inscripcion)
    INS_REPO->>REG_DB: INSERT OR REPLACE
    REG_DB-->>INS_REPO: ok
    INS_REPO-->>REG_APP: ok
    REG_APP-->>REG_API: inscripcion_id
    REG_API-->>A: 201 Created
```

### Observaciones

- La regla de negocio depende del estado del torneo y de la fecha de inicio.
- Hoy la integración `Registro -> Torneo` está implementada como lectura
  read-only directa sobre `torneo.db` contenida en infraestructura.
- Arquitectónicamente, el diseño de referencia preferiría eventos o contratos
  más explícitos; la implementación actual resuelve la validación con un ACL
  técnico.

## Escenario 3: atleta inscripto propagado hacia Competencia

Este flujo refleja la colaboración estratégica `Registro -> Competencia`.

```mermaid
sequenceDiagram
    participant REG as BC Registro
    participant BUS as Bus / mecanismo de publicación
    participant ACL as Participante ACL en Competencia
    participant COMP as BC Competencia

    REG->>BUS: Evento AtletaInscripto
    BUS->>ACL: AtletaInscripto
    ACL->>ACL: Traduce Atleta -> Participante
    ACL->>COMP: crea/actualiza Participante local
    COMP-->>ACL: participante disponible para grilla y performance
```

### Observaciones

- Este flujo está definido arquitectónicamente y ya aparece en el context map.
- La implementación del ACL está documentada del lado de `Competencia`.
- La publicación explícita del evento todavía no está materializada en
  `Registro`.

## Escenario 4: cierre de competencia y cálculo de ranking

Este flujo muestra cómo `Resultados` obtiene el estado final deportivo desde
`Competencia` y persiste el ranking calculado.

```mermaid
sequenceDiagram
    participant COMP as BC Competencia
    participant RES_APP as CalcularRankingHandler
    participant RES_ACL as ResultadosCompetenciaAdapter
    participant COMP_DB as competencia.db
    participant RES_AGG as RankingCompetencia
    participant RES_DB as resultados.db

    COMP->>RES_APP: disparador de cálculo al cierre de disciplina
    RES_APP->>RES_ACL: get_resultados_finales(competenciaId, disciplina)
    RES_ACL->>COMP_DB: load_all_streams_with_prefix(performance-...)
    COMP_DB-->>RES_ACL: streams de Performance
    RES_ACL->>RES_ACL: reconstituye y traduce ResultadoFinal
    RES_ACL-->>RES_APP: lista de resultados finales

    RES_APP->>RES_AGG: reconstitute + calcular(resultados, descriptor)
    RES_AGG-->>RES_APP: ResultadosCalculados
    RES_APP->>RES_DB: append stream ranking-{competenciaId}-{disciplina}
    RES_DB-->>RES_APP: ok
```

### Observaciones

- El diseño estratégico define `CompetenciaFinalizada` como evento upstream de
  `Resultados`.
- La implementación actual encapsula la integración en un ACL que lee streams de
  `Competencia` y reconstruye `Performance`.
- La consulta posterior del ranking es local al BC `Resultados` y no vuelve a
  consultar `Competencia`.

## Escenario 5: publicación de eventos hacia Notificaciones

Este flujo representa la arquitectura objetivo de notificaciones, donde los BCs
funcionales producen eventos pero no esperan respuesta.

```mermaid
sequenceDiagram
    participant UP as BC funcional
    participant BUS as Bus / outbox
    participant NOTIF_APP as Notificaciones Application
    participant NOTIF_AGG as Notificacion
    participant NOTIF_DB as notificaciones.db
    participant CH as Canal externo

    UP->>BUS: Evento de dominio
    BUS->>NOTIF_APP: evento recibido
    NOTIF_APP->>NOTIF_DB: verificar existencia por eventoFuenteId
    alt ya enviada
        NOTIF_DB-->>NOTIF_APP: NotificacionEnviada existente
        NOTIF_APP-->>BUS: ignorar duplicado
    else no enviada
        NOTIF_APP->>NOTIF_AGG: solicitar envío
        NOTIF_AGG-->>NOTIF_APP: NotificacionSolicitada
        NOTIF_APP->>NOTIF_DB: append NotificacionSolicitada
        NOTIF_APP->>CH: enviar email/push
        alt éxito
            CH-->>NOTIF_APP: entrega confirmada
            NOTIF_APP->>NOTIF_DB: append NotificacionEnviada
        else fallo
            CH-->>NOTIF_APP: error / timeout
            NOTIF_APP->>NOTIF_DB: append NotificacionFallida
        end
    end
```

### Observaciones

- Este flujo es objetivo arquitectónico vigente, no implementación ya completa.
- La propiedad importante es que el productor del evento no depende del resultado
  de la notificación para completar su caso de uso.
- La idempotencia se resuelve dentro del BC `Notificaciones`.

## Dependencias síncronas y asíncronas

Resumen de la naturaleza de las principales colaboraciones de runtime:

| Origen | Destino | Tipo | Estado |
|--------|---------|------|--------|
| Usuario autenticado | `Identidad` | Síncrona HTTP | Implementado |
| BC consumidor | `Identidad` claims | Verificación local JWT | Implementado |
| `Registro` | `Torneo` | Lookup read-only vía ACL | Implementado |
| `Registro` | `Competencia` | Evento + ACL | Parcial / objetivo |
| `Competencia` | `Resultados` | Evento / ACL de cierre | Parcialmente implementado |
| BCs funcionales | `Notificaciones` | Evento asíncrono | Objetivo |

## Restricciones de runtime relevantes

- `Competencia` no debe consultar `Registro` en runtime para operar una
  performance; debe trabajar sobre `Participante` local.
- `Resultados` no debe recalcular ranking en cada lectura si ya existe el stream
  local calculado.
- `Notificaciones` no debe introducir dependencia síncrona en los casos de uso
  funcionales.
- La validación de identidad downstream debe resolverse a partir del token, no
  con round-trips al BC `Identidad`.
