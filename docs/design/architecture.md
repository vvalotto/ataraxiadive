# Architecture — AtaraxiaDive

| Campo | Valor |
|-------|-------|
| **Documento** | architecture.md |
| **Modelo** | C4 (Simon Brown) — L1 Context · L2 Container · L3 Component |
| **Capa IEDD** | Capa 4 — Arquitectura |
| **Fecha** | 2026-03-19 |
| **Fuentes** | Context Map v1.1 · Domain Model v1.0 · ADR-001 a ADR-005 |
| **Estado** | ✅ v1.0 — Fase 0 |

---

## 1. L1 — System Context

AtaraxiaDive como caja negra: actores que la usan y sistemas externos con los que se integra.

```mermaid
C4Context
    title AtaraxiaDive — System Context (L1)

    Person(organizador, "Organizador", "Crea y gestiona torneos,\ndefine grillas y disciplinas")
    Person(juez, "Juez", "Registra resultados\ny asigna tarjetas en tiempo real")
    Person(atleta, "Atleta", "Se inscribe, declara AP\ny consulta resultados")

    System(ataraxia, "AtaraxiaDive", "Plataforma web para gestión\nde torneos de apnea.\nFastAPI + React PWA + PostgreSQL")

    System_Ext(email, "Servicio Email", "SMTP externo\n(ej: SendGrid)")
    System_Ext(push, "Servicio Push", "FCM — notificaciones\nmóviles y web")

    Rel(organizador, ataraxia, "Crea torneos, configura\ncompetencias, gestiona grilla", "HTTPS")
    Rel(juez, ataraxia, "Registra resultados\ny asigna tarjetas", "HTTPS")
    Rel(atleta, ataraxia, "Se inscribe, declara AP\ny consulta resultados", "HTTPS")
    Rel(ataraxia, email, "Envía notificaciones", "SMTP/TLS")
    Rel(ataraxia, push, "Envía push notifications", "FCM API / HTTPS")

    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

### Elementos

| Elemento o Componente | Responsabilidad asignada |
|-----------------------|--------------------------|
| Organizador | Actor humano que crea torneos, configura competencias y gestiona grillas. |
| Juez | Actor humano que opera durante la competencia: registra resultados y asigna tarjetas en tiempo real. |
| Atleta | Actor humano que interactúa antes y después de la competencia: inscripción, declaración de AP y consulta de resultados. |
| AtaraxiaDive | Sistema central. Gestiona el ciclo de vida completo de torneos de apnea. |
| Servicio Email | Sistema externo de envío de correos electrónicos. Recibe órdenes de envío desde AtaraxiaDive. |
| Servicio Push | Sistema externo de notificaciones push (FCM). Recibe órdenes de envío desde AtaraxiaDive. |

### Relaciones

| Tipo de relación | Nombre | Descripción |
|-----------------|--------|-------------|
| Uso | Organizador → AtaraxiaDive | El organizador opera el sistema para crear y gestionar torneos y competencias. |
| Uso | Juez → AtaraxiaDive | El juez opera el sistema durante la ejecución de competencias. |
| Uso | Atleta → AtaraxiaDive | El atleta accede para inscribirse, declarar su AP y consultar resultados. |
| Integración | AtaraxiaDive → Servicio Email | El sistema delega el envío de correos a un servicio externo vía SMTP/TLS. |
| Integración | AtaraxiaDive → Servicio Push | El sistema delega el envío de notificaciones push a FCM vía HTTPS. |

---

## 2. L2 — Container

Descompone AtaraxiaDive en sus contenedores técnicos y las tecnologías que los soportan.

```mermaid
C4Container
    title AtaraxiaDive — Container (L2)

    Person(usuario, "Usuario", "Organizador · Juez · Atleta")

    System_Boundary(ataraxia, "AtaraxiaDive") {
        Container(spa, "React PWA", "React · TypeScript", "Single Page App instalable.\nGestión de torneos y competencias\nen tiempo real.")

        Container(api, "Backend API", "Python · FastAPI", "Expone la API REST.\nOrquesta los 6 Bounded Contexts.\nArquitectura Hexagonal.")

        ContainerDb(pg_crud, "PostgreSQL — CRUD", "PostgreSQL 16", "Persistencia relacional para\nlos 4 BCs CRUD:\nTorneo · Registro · Resultados · Identidad")

        ContainerDb(pg_es, "Event Store", "PostgreSQL 16\n(tabla domain_events)", "Streams de eventos para\nlos 2 BCs con Event Sourcing:\nCompetencia · Notificaciones")
    }

    System_Ext(email, "Servicio Email", "SMTP externo")
    System_Ext(push, "Servicio Push", "FCM")

    Rel(usuario, spa, "Usa", "HTTPS / Browser")
    Rel(spa, api, "API calls", "REST / HTTPS / JSON")
    Rel(api, pg_crud, "Lee y escribe", "SQL / asyncpg")
    Rel(api, pg_es, "Append y lee streams", "SQL / asyncpg")
    Rel(api, email, "Envía", "SMTP/TLS")
    Rel(api, push, "Envía", "HTTPS")

    UpdateLayoutConfig($c4ShapeInRow="2", $c4BoundaryInRow="1")
```

> **Event Store sobre PostgreSQL:** la tabla `domain_events` actúa como append-only log.
> Cada fila es un evento inmutable con `stream_id`, `stream_version`, `event_type` y `payload` JSON.
> Los aggregates con ES (Competencia, Notificaciones) reconstruyen su estado reproduciendo su stream.
> No se usa un motor de Event Sourcing externo — PostgreSQL es suficiente para el horizonte del proyecto.

### Elementos

| Elemento o Componente | Responsabilidad asignada |
|-----------------------|--------------------------|
| React PWA | Interfaz de usuario instalable. Renderiza las vistas de gestión de torneos, competencias y resultados. |
| Backend API | Núcleo del sistema. Expone la API REST y orquesta los 6 Bounded Contexts con arquitectura hexagonal. |
| PostgreSQL — CRUD | Almacena el estado de los 4 BCs con persistencia relacional estándar: Torneo, Registro, Resultados, Identidad. |
| Event Store | Almacena los streams de eventos de los 2 BCs con Event Sourcing: Competencia y Notificaciones. Tabla append-only `domain_events` en PostgreSQL. |
| Servicio Email | Sistema externo para envío de emails. |
| Servicio Push | Sistema externo para notificaciones push (FCM). |

### Relaciones

| Tipo de relación | Nombre | Descripción |
|-----------------|--------|-------------|
| Uso | Usuario → React PWA | El usuario interactúa con la interfaz web/PWA desde el navegador. |
| Llamada API | React PWA → Backend API | El frontend realiza llamadas REST/JSON sobre HTTPS para todas las operaciones. |
| Persistencia | Backend API → PostgreSQL CRUD | El backend lee y escribe el estado de los BCs CRUD mediante SQL/asyncpg. |
| Event Sourcing | Backend API → Event Store | El backend hace append de eventos y lee streams para reconstruir aggregates con ES. |
| Notificación | Backend API → Servicio Email | El backend delega el envío de emails al servicio externo mediante SMTP/TLS. |
| Notificación | Backend API → Servicio Push | El backend delega el envío de push notifications a FCM mediante HTTPS. |

---

## 3. L3a — Component: Patrón Hexagonal (Canónico)

Estructura interna que aplica a **todos los BCs** dentro del Backend API.
Las flechas de dependencia apuntan siempre hacia el dominio — nunca desde el dominio hacia afuera.

```mermaid
C4Component
    title Backend API — Patrón Hexagonal Canónico (L3a)

    Container_Boundary(api_boundary, "Backend API — BC genérico") {

        Component(routes, "API Layer", "FastAPI · Pydantic", "Rutas HTTP, validación de entrada/salida,\ndeserialización de comandos/queries,\nverificación de token JWT.")

        Component(usecases, "Application Layer", "Python — Use Cases / Handlers", "Orquesta el flujo: recibe comandos,\ncarga aggregates via puerto,\npersiste y publica eventos.\nNo contiene lógica de negocio.")

        Component(domain, "Domain Layer", "Python — Aggregates · VOs · Ports", "Aggregates con invariantes.\nValue Objects inmutables.\nInterfaces de repositorios (puertos).\nEventos de dominio.\nNo importa nada externo al dominio.")

        Component(infra, "Infrastructure Layer", "Python · asyncpg", "Implementa los puertos del dominio.\nRepositorios concretos (PostgreSQL / Event Store).\nAdaptadores para servicios externos.")
    }

    ContainerDb(db, "Base de Datos", "PostgreSQL 16", "CRUD relacional\no Event Store\nsegún el BC")

    Rel(routes, usecases, "Invoca comandos / queries")
    Rel(usecases, domain, "Usa aggregates y puertos")
    Rel(infra, domain, "Implementa puertos (inversión de dependencia)")
    Rel(infra, db, "Lee y escribe", "SQL / asyncpg")

    UpdateLayoutConfig($c4ShapeInRow="2", $c4BoundaryInRow="1")
```

### Elementos

| Elemento o Componente | Responsabilidad asignada |
|-----------------------|--------------------------|
| API Layer | Adaptador de entrada. Expone rutas HTTP, valida entrada/salida con Pydantic y verifica el token JWT. Traduce requests HTTP en comandos/queries para la capa de aplicación. |
| Application Layer | Orquestador del flujo de negocio. Recibe comandos, carga aggregates via puertos, ejecuta la operación de dominio, persiste cambios y publica eventos. No contiene lógica de negocio. |
| Domain Layer | Núcleo del sistema. Contiene aggregates con invariantes, value objects inmutables, interfaces de repositorios (puertos) y definición de eventos de dominio. No depende de nada externo. |
| Infrastructure Layer | Adaptador de salida. Implementa los puertos definidos en el dominio: repositorios concretos para PostgreSQL / Event Store y adaptadores para servicios externos. |
| Base de Datos | Almacenamiento persistente. CRUD relacional o Event Store según el BC que corresponda. |

### Relaciones

| Tipo de relación | Nombre | Descripción |
|-----------------|--------|-------------|
| Invocación | API Layer → Application Layer | La capa API deserializa el request y delega la ejecución al caso de uso correspondiente. |
| Uso de puertos | Application Layer → Domain Layer | La capa de aplicación usa los aggregates del dominio e invoca los puertos para cargar y persistir el estado. |
| Implementación de puerto | Infrastructure Layer → Domain Layer | La capa de infraestructura implementa las interfaces (puertos) definidas en el dominio (inversión de dependencia). El dominio no depende de la infraestructura. |
| Persistencia | Infrastructure Layer → Base de Datos | La capa de infraestructura lee y escribe en la base de datos mediante SQL/asyncpg. |

### Regla de dependencias (Regla de Oro — §6 CLAUDE.md)

```
api/  →  application/  →  domain/
         infrastructure/  ↗  (implementa interfaces definidas en domain/)
```

| Capa | Puede importar | No puede importar |
|------|---------------|-------------------|
| `domain/` | Solo stdlib Python y tipos propios del dominio | Nada externo |
| `application/` | `domain/` | `infrastructure/`, `api/` |
| `infrastructure/` | `domain/`, libs externas (asyncpg, etc.) | `application/`, `api/` |
| `api/` | `application/`, Pydantic | `domain/` directamente, `infrastructure/` |

> DesignReviewer detecta automáticamente las violaciones de estas reglas en cada merge.

---

## 4. L3b — Component: BC Competencia (Core Domain)

Instancia el patrón hexagonal con los componentes reales del Core Domain.
BC Competencia usa Event Sourcing — los aggregates reconstruyen su estado reproduciendo el stream.

```mermaid
C4Component
    title BC Competencia — Component (L3b · Core Domain ★ ES)

    Container_Boundary(competencia_bc, "BC Competencia dentro del Backend API") {

        Container_Boundary(api_layer, "API Layer") {
            Component(routes_comp, "CompetenciaRoutes", "FastAPI · Pydantic", "POST /competencias/{id}/grilla\nPOST /competencias/{id}/iniciar\nPOST /competencias/{id}/finalizar\nGET  /competencias/{id}/grilla")
            Component(routes_perf, "PerformanceRoutes", "FastAPI · Pydantic", "POST /performances/{id}/ap\nPOST /performances/{id}/resultado\nPOST /performances/{id}/tarjeta\nPOST /performances/{id}/dns")
        }

        Container_Boundary(app_layer, "Application Layer") {
            Component(cmd_comp, "CompetenciaHandlers", "Python — Commands", "GenerarGrilla · AjustarGrilla\nConfirmarGrilla · IniciarCompetencia\nFinalizarCompetencia")
            Component(cmd_perf, "PerformanceHandlers", "Python — Commands", "RegistrarAP · LlamarAtleta\nRegistrarResultado · AsignarTarjeta\nRegistrarDNS · CorregirResultado")
            Component(acl, "ParticipanteACL", "Python — Translator", "Suscribe AtletaInscripto (BC Registro).\nTraduce Atleta → Participante local.\nAísla el Core Domain de cambios en Registro.")
        }

        Container_Boundary(domain_layer, "Domain Layer") {
            Component(agg_comp, "Competencia", "Aggregate Root", "GrillaDeSalida · IntervaloDisciplina\nINV-C-01 a INV-C-04\nPuerto: CompetenciaRepository")
            Component(agg_perf, "Performance", "Aggregate Root", "AP · RP · Tarjeta · EstadoPerformance\nINV-P-01 a INV-P-14\nPuerto: PerformanceRepository")
            Component(ent_part, "Participante", "Entidad local (sin aggregate propio)", "Creada por ACL desde AtletaInscripto.\nReferenciada por id\ndesde Competencia y Performance.")
        }

        Container_Boundary(infra_layer, "Infrastructure Layer") {
            Component(repo_comp, "CompetenciaEventStore", "asyncpg · domain_events", "Implementa CompetenciaRepository.\nAppend de eventos al stream.\nReconstrucción de estado desde stream_id.")
            Component(repo_perf, "PerformanceEventStore", "asyncpg · domain_events", "Implementa PerformanceRepository.\nStream propio por instancia de Performance.")
            Component(proj, "CompetenciaReadProjection", "asyncpg · PostgreSQL", "Proyecta eventos a tablas\ndenormalizadas para consultas GET.\nActualización por polling o NOTIFY.")
        }
    }

    ContainerDb(event_store, "Event Store", "PostgreSQL 16\ndomain_events", "Streams de eventos de\nCompetencia y Performance")
    ContainerDb(read_db, "Read Model DB", "PostgreSQL 16", "Tablas proyectadas para\nconsultas rápidas de grilla\ny estado de competencia")

    Rel(routes_comp, cmd_comp, "Invoca")
    Rel(routes_perf, cmd_perf, "Invoca")
    Rel(cmd_comp, agg_comp, "Carga y persiste aggregate")
    Rel(cmd_perf, agg_perf, "Carga y persiste aggregate")
    Rel(acl, ent_part, "Crea / actualiza")
    Rel(repo_comp, agg_comp, "Implementa puerto")
    Rel(repo_perf, agg_perf, "Implementa puerto")
    Rel(repo_comp, event_store, "Append / read stream", "SQL")
    Rel(repo_perf, event_store, "Append / read stream", "SQL")
    Rel(proj, event_store, "Suscribe a eventos", "polling / NOTIFY")
    Rel(proj, read_db, "Escribe proyecciones", "SQL")
    Rel(routes_comp, read_db, "Consultas GET", "SQL via handler")

    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

### Elementos

| Elemento o Componente | Responsabilidad asignada |
|-----------------------|--------------------------|
| CompetenciaRoutes | Expone los endpoints REST para operaciones sobre el aggregate Competencia: gestión de grilla, inicio y finalización. |
| PerformanceRoutes | Expone los endpoints REST para operaciones sobre el aggregate Performance: registro de AP, resultado, tarjeta y DNS. |
| CompetenciaHandlers | Maneja los comandos del ciclo de vida de Competencia: GenerarGrilla, AjustarGrilla, ConfirmarGrilla, IniciarCompetencia, FinalizarCompetencia. |
| PerformanceHandlers | Maneja los comandos del ciclo de vida de Performance: RegistrarAP, LlamarAtleta, RegistrarResultado, AsignarTarjeta, RegistrarDNS, CorregirResultado. |
| ParticipanteACL | Anti-Corruption Layer. Suscribe al evento AtletaInscripto de BC Registro y traduce el modelo de Atleta al modelo local de Participante. Aísla el Core Domain de cambios en BC Registro. |
| Competencia | Aggregate Root del ciclo de vida de la competencia. Contiene GrillaDeSalida e IntervaloDisciplina. Custodia los invariantes INV-C-01 a INV-C-04. |
| Performance | Aggregate Root del ciclo de vida de una performance individual. Contiene AP, RP y Tarjeta. Custodia los invariantes INV-P-01 a INV-P-14. |
| Participante | Entidad local sin aggregate propio. Representa al atleta dentro del contexto de Competencia. Creada y mantenida por el ParticipanteACL a partir de eventos de BC Registro. |
| CompetenciaEventStore | Implementa CompetenciaRepository. Persiste eventos de Competencia en el stream y reconstruye el aggregate desde el stream_id. |
| PerformanceEventStore | Implementa PerformanceRepository. Cada instancia de Performance tiene su propio stream en la tabla domain_events. |
| CompetenciaReadProjection | Proyecta los eventos de dominio a tablas desnormalizadas en PostgreSQL para servir consultas GET eficientes sin reproducir el stream. |
| Event Store | Tabla append-only `domain_events`. Almacena todos los eventos de Competencia y Performance. Fuente de verdad del estado de ambos aggregates. |
| Read Model DB | Tablas proyectadas para consultas rápidas de grilla y estado de competencia. No es fuente de verdad — se puede reconstruir desde el Event Store. |

### Relaciones

| Tipo de relación | Nombre | Descripción |
|-----------------|--------|-------------|
| Invocación | CompetenciaRoutes → CompetenciaHandlers | La ruta deserializa el request y delega la operación al handler de comando correspondiente. |
| Invocación | PerformanceRoutes → PerformanceHandlers | Ídem para operaciones sobre el aggregate Performance. |
| Uso de aggregate | CompetenciaHandlers → Competencia | El handler carga el aggregate desde el repositorio, invoca el método de negocio y persiste los eventos generados. |
| Uso de aggregate | PerformanceHandlers → Performance | Ídem para el aggregate Performance. |
| Traducción ACL | ParticipanteACL → Participante | El ACL crea o actualiza la entidad Participante a partir del evento AtletaInscripto recibido desde BC Registro. |
| Implementación de puerto | CompetenciaEventStore → Competencia | Implementa CompetenciaRepository: append al stream y reconstrucción del aggregate desde la secuencia de eventos. |
| Implementación de puerto | PerformanceEventStore → Performance | Implementa PerformanceRepository con stream propio por instancia de Performance. |
| Event Sourcing | CompetenciaEventStore → Event Store | Escribe eventos de Competencia en `domain_events` y los lee para reconstruir el aggregate. |
| Event Sourcing | PerformanceEventStore → Event Store | Escribe y lee el stream propio de cada Performance en `domain_events`. |
| Proyección | CompetenciaReadProjection → Event Store | Lee los eventos de dominio (por polling o NOTIFY de PostgreSQL) para mantener el read model actualizado. |
| Proyección | CompetenciaReadProjection → Read Model DB | Escribe las proyecciones desnormalizadas para consultas rápidas. |
| Consulta | CompetenciaRoutes → Read Model DB | Las consultas GET de grilla y estado de competencia se resuelven contra el read model, no contra el event store. |

### Notas de diseño — BC Competencia

**Performance como aggregate separado**
`Performance` tiene su propio stream de eventos (no está anidado en `Competencia`).
Esto permite auditar el ciclo de vida de cada performance de forma independiente,
y reconstruir el estado de una performance sin cargar toda la competencia.

**Read Model separado del Event Store**
Las consultas GET (ej: obtener la grilla actual) no reproducen el stream.
El `CompetenciaReadProjection` mantiene una proyección en tablas PostgreSQL
actualizadas cada vez que se produce un evento relevante.

**ACL en Application Layer**
El Anti-Corruption Layer vive en `application/` — no en `domain/`.
El dominio no sabe que existe Registro; solo conoce `Participante`.

---

## 5. BCs CRUD — Referencia de estructura

Los BCs Torneo, Registro, Resultados e Identidad siguen el patrón hexagonal canónico (§3)
con persistencia relacional estándar. No requieren L3 detallado en Fase 0
— se elabora al diseñar cada BC en su SP correspondiente.

| BC | Tipo | SP | Persistencia | Notas |
|----|------|:--:|-------------|-------|
| Torneo | Supporting | SP3 | PostgreSQL CRUD | Incluye catálogos EntidadOrganizadora y Sede |
| Registro | Supporting | SP2 | PostgreSQL CRUD | ACL de salida hacia Competencia |
| Resultados | Supporting | SP2 | PostgreSQL CRUD | Alimentado por CompetenciaFinalizada |
| Identidad | Generic | SP4 | PostgreSQL CRUD | JWT cross-cutting; candidato a solución externa en H2-H3 |
| Notificaciones | Generic | SP4 | Event Store (ES) | Idempotencia exactly-once; suscribe a todos los BCs |

---

## 6. Decisiones de Arquitectura — Referencia

| ADR | Decisión |
|-----|----------|
| ADR-001 a ADR-004 | Stack tecnológico: FastAPI · PostgreSQL · React PWA · Arquitectura Hexagonal |
| ADR-005 | 6 Bounded Contexts definitivos + Event Sourcing en Competencia y Notificaciones |

Ver `docs/adr/` para justificación completa de cada decisión.

---

## 7. Próximo Paso

Este documento es insumo directo para:

1. **`docs/design/estrategia-desarrollo-bc.md`** — mapear los BCs a los incrementos de SP1–SP5
2. **`docs/traceability/matrix.md`** — trazabilidad RFs → BCs → US-IEDD
3. **US-IEDD de SP1** — las rutas y handlers del L3b definen el contrato de las primeras historias

---

*Documento creado: 2026-03-19 — Semana 0, Fase 0*
*v1.0: L1 System Context + L2 Container + L3a Hexagonal canónico + L3b BC Competencia*
*Modelo: C4 (Simon Brown) — diagramas Mermaid*
*Fuentes: Context Map v1.1 · Domain Model v1.0 · ADR-001 a ADR-005*
*Mantenido por: Claude Cowork + Victor Valotto*
