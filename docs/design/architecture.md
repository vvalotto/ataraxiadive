# Architecture — AtaraxiaDive

| Campo | Valor |
|-------|-------|
| **Documento** | architecture.md |
| **Modelo** | C4 (Simon Brown) — L1 Context · L2 Container · L3 Component |
| **Capa IEDD** | Capa 4 — Arquitectura |
| **Fecha** | 2026-03-20 |
| **Fuentes** | Context Map v1.1 · Domain Model v1.0 · ADR-001 a ADR-012 |
| **Estado** | Histórico / superseded por `docs/architecture/` |

---

> **Documento histórico:** este archivo conserva el diseño C4 producido en Semana
> 0 / Fase 0. Para arquitectura vigente usar `docs/architecture/`. Los contratos
> HTTP operativos deben verificarse contra los routers FastAPI y OpenAPI generado.

## 1. L1 — System Context

AtaraxiaDive como caja negra: actores que la usan y sistemas externos con los que se integra.

```mermaid
C4Context
    title AtaraxiaDive — System Context (L1)

    Person(organizador, "Organizador", "Crea y gestiona torneos,\ndefine grillas y disciplinas")
    Person(juez, "Juez", "Registra resultados\ny asigna tarjetas en tiempo real")
    Person(atleta, "Atleta", "Se inscribe, declara AP\ny consulta resultados")

    System(ataraxia, "AtaraxiaDive", "Plataforma web para gestión\nde torneos de apnea.\nFastAPI + React PWA + SQLite")

    System_Ext(email, "Servicio Email", "SMTP externo\n(ej: SendGrid)")
    System_Ext(push, "Servicio Push", "FCM — notificaciones\nmóviles y web")

    Rel(organizador, ataraxia, "Crea torneos, configura\ncompetencias, gestiona grilla", "HTTPS")
    Rel(juez, ataraxia, "Registra resultados\ny asigna tarjetas", "HTTPS")
    Rel(atleta, ataraxia, "Se inscribe, declara AP\ny consulta resultados", "HTTPS")
    Rel(ataraxia, email, "Envía notificaciones", "HTTPS API")
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
| Integración | AtaraxiaDive → Servicio Email | El sistema delega el envío de correos a un servicio externo vía API HTTPS. |
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

        ContainerDb(sqlite_crud, "SQLite — CRUD BCs", "SQLite · 4 archivos\nuno por Bounded Context", "Persistencia relacional para\nlos 4 BCs CRUD:\nTorneo · Registro · Resultados · Identidad")

        ContainerDb(sqlite_es, "SQLite — ES BCs", "SQLite · 2 archivos\nuno por Bounded Context", "Event store + read model para\nlos 2 BCs con Event Sourcing:\nCompetencia · Notificaciones")
    }

    System_Ext(email, "Servicio Email", "SMTP externo")
    System_Ext(push, "Servicio Push", "FCM")

    Rel(usuario, spa, "Usa", "HTTPS / Browser")
    Rel(spa, api, "API calls", "REST / HTTPS / JSON")
    Rel(api, sqlite_crud, "Lee y escribe", "SQL / aiosqlite")
    Rel(api, sqlite_es, "Append / lee streams\ny actualiza read model", "SQL / aiosqlite")
    Rel(api, email, "Envía", "HTTPS API")
    Rel(api, push, "Envía", "HTTPS")

    UpdateLayoutConfig($c4ShapeInRow="2", $c4BoundaryInRow="1")
```

> **Event Store sobre SQLite:** la tabla `events` actúa como append-only log (ADR-008).
> Cada fila es un evento inmutable con `stream_id`, `stream_pos`, `event_type` y `payload` JSON.
> Los aggregates con ES (Competencia, Notificaciones) reconstruyen su estado reproduciendo su stream.
> El event store convive en el mismo archivo SQLite del BC — sin motor de Event Sourcing externo (ADR-007).

### Elementos

| Elemento o Componente | Responsabilidad asignada |
|-----------------------|--------------------------|
| React PWA | Interfaz de usuario instalable. Renderiza las vistas de gestión de torneos, competencias y resultados. |
| Backend API | Núcleo del sistema. Expone la API REST y orquesta los 6 Bounded Contexts con arquitectura hexagonal. |
| SQLite — CRUD BCs | 4 archivos SQLite independientes (uno por BC). Almacena el estado de los BCs CRUD: Torneo, Registro, Resultados, Identidad. |
| SQLite — ES BCs | 2 archivos SQLite independientes (uno por BC). Almacena el event store y el read model de los BCs con Event Sourcing: Competencia y Notificaciones. |
| Servicio Email | Sistema externo para envío de emails. |
| Servicio Push | Sistema externo para notificaciones push (FCM). |

### Relaciones

| Tipo de relación | Nombre | Descripción |
|-----------------|--------|-------------|
| Uso | Usuario → React PWA | El usuario interactúa con la interfaz web/PWA desde el navegador. |
| Llamada API | React PWA → Backend API | El frontend realiza llamadas REST/JSON sobre HTTPS para todas las operaciones. |
| Persistencia | Backend API → SQLite CRUD BCs | El backend lee y escribe el estado de los BCs CRUD mediante SQL/aiosqlite. |
| Event Sourcing | Backend API → SQLite ES BCs | El backend hace append de eventos, lee streams para reconstruir aggregates con ES, y actualiza el read model síncronamente en el mismo comando. |
| Notificación | Backend API → Servicio Email | El backend delega el envío de emails al servicio externo mediante API HTTPS. |
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

        Component(infra, "Infrastructure Layer", "Python · aiosqlite", "Implementa los puertos del dominio.\nRepositorios concretos (SQLite / event store).\nAdaptadores para servicios externos.")
    }

    ContainerDb(db, "Base de Datos", "SQLite", "CRUD relacional\no Event Store\nsegún el BC")

    Rel(routes, usecases, "Invoca comandos / queries")
    Rel(usecases, domain, "Usa aggregates y puertos")
    Rel(infra, domain, "Implementa puertos (inversión de dependencia)")
    Rel(infra, db, "Lee y escribe", "SQL / aiosqlite")

    UpdateLayoutConfig($c4ShapeInRow="2", $c4BoundaryInRow="1")
```

### Elementos

| Elemento o Componente | Responsabilidad asignada |
|-----------------------|--------------------------|
| API Layer | Adaptador de entrada. Expone rutas HTTP, valida entrada/salida con Pydantic y verifica el token JWT. Traduce requests HTTP en comandos/queries para la capa de aplicación. |
| Application Layer | Orquestador del flujo de negocio. Recibe comandos, carga aggregates via puertos, ejecuta la operación de dominio, persiste cambios y publica eventos. No contiene lógica de negocio. |
| Domain Layer | Núcleo del sistema. Contiene aggregates con invariantes, value objects inmutables, interfaces de repositorios (puertos) y definición de eventos de dominio. No depende de nada externo. |
| Infrastructure Layer | Adaptador de salida. Implementa los puertos definidos en el dominio: repositorios concretos para SQLite / event store y adaptadores para servicios externos. |
| Base de Datos | Almacenamiento persistente. CRUD relacional o Event Store según el BC que corresponda. |

### Relaciones

| Tipo de relación | Nombre | Descripción |
|-----------------|--------|-------------|
| Invocación | API Layer → Application Layer | La capa API deserializa el request y delega la ejecución al caso de uso correspondiente. |
| Uso de puertos | Application Layer → Domain Layer | La capa de aplicación usa los aggregates del dominio e invoca los puertos para cargar y persistir el estado. |
| Implementación de puerto | Infrastructure Layer → Domain Layer | La capa de infraestructura implementa las interfaces (puertos) definidas en el dominio (inversión de dependencia). El dominio no depende de la infraestructura. |
| Persistencia | Infrastructure Layer → Base de Datos | La capa de infraestructura lee y escribe en la base de datos mediante SQL/aiosqlite. |

### Regla de dependencias (Regla de Oro — §6 CLAUDE.md)

```
api/  →  application/  →  domain/
         infrastructure/  ↗  (implementa interfaces definidas en domain/)
```

| Capa | Puede importar | No puede importar |
|------|---------------|-------------------|
| `domain/` | Solo stdlib Python y tipos propios del dominio | Nada externo |
| `application/` | `domain/` | `infrastructure/`, `api/` |
| `infrastructure/` | `domain/`, libs externas (aiosqlite, etc.) | `application/`, `api/` |
| `api/` | `application/`, Pydantic | `domain/` directamente, `infrastructure/` |

> DesignReviewer detecta automáticamente las violaciones de estas reglas en cada merge.

---

## 4. L3b — Component: BC Competencia (Core Domain)

Instancia el patrón hexagonal con los componentes reales del Core Domain.
BC Competencia usa Event Sourcing — los aggregates reconstruyen su estado reproduciendo el stream.
Las proyecciones se actualizan síncronamente en el mismo comando (ADR-008 — sin subscriptions reactivas).

```mermaid
C4Component
    title BC Competencia — Component (L3b · Core Domain ★ ES)

    Container_Boundary(competencia_bc, "BC Competencia dentro del Backend API") {

        Container_Boundary(api_layer, "API Layer") {
            Component(routes_comp, "CompetenciaRoutes", "FastAPI · Pydantic", "POST /competencia\nGET  /competencia\nPOST /competencia/{id}/generar-grilla\nPOST /competencia/{id}/confirmar-grilla\nPOST /competencia/{id}/iniciar\nPOST /competencia/{id}/finalizar\nGET  /competencia/{id}/grilla\nGET  /competencia/{id}/estado")
            Component(routes_perf, "PerformanceRoutes", "FastAPI · Pydantic", "POST /competencia/{id}/llamar\nPOST /competencia/{id}/registrar-resultado\nPOST /competencia/{id}/registrar-dns\nPOST /competencia/{id}/asignar-tarjeta\nPOST /competencia/{id}/resolver-revision\nPOST /competencia/{id}/performances/{performance_id}/corregir-resultado-tras-dns")
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
            Component(repo_comp, "CompetenciaEventStore", "aiosqlite · events", "Implementa CompetenciaRepository.\nAppend de eventos al stream.\nReconstrucción de estado desde stream_id.")
            Component(repo_perf, "PerformanceEventStore", "aiosqlite · events", "Implementa PerformanceRepository.\nStream propio por instancia de Performance.")
            Component(proj, "CompetenciaReadProjection", "aiosqlite · SQLite", "Proyecta eventos a tablas\ndenormalizadas para consultas GET.\nActualización síncrona en el mismo comando.")
        }
    }

    ContainerDb(sqlite_comp, "competencia.db", "SQLite", "Tabla events (event store)\n+ tablas proyectadas (read model)")

    Rel(routes_comp, cmd_comp, "Invoca")
    Rel(routes_perf, cmd_perf, "Invoca")
    Rel(cmd_comp, agg_comp, "Carga y persiste aggregate")
    Rel(cmd_perf, agg_perf, "Carga y persiste aggregate")
    Rel(acl, ent_part, "Crea / actualiza")
    Rel(repo_comp, agg_comp, "Implementa puerto")
    Rel(repo_perf, agg_perf, "Implementa puerto")
    Rel(repo_comp, sqlite_comp, "Append / read stream", "SQL / aiosqlite")
    Rel(repo_perf, sqlite_comp, "Append / read stream", "SQL / aiosqlite")
    Rel(cmd_comp, proj, "Actualiza read model\ntras append de eventos")
    Rel(cmd_perf, proj, "Actualiza read model\ntras append de eventos")
    Rel(proj, sqlite_comp, "Escribe proyecciones", "SQL / aiosqlite")
    Rel(routes_comp, sqlite_comp, "Consultas GET", "SQL via handler")

    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

### Elementos

| Elemento o Componente | Responsabilidad asignada |
|-----------------------|--------------------------|
| CompetenciaRoutes | Expone endpoints REST bajo `/competencia` para configuración, grilla, inicio, finalización, estado y consultas de competencia. |
| PerformanceRoutes | Expone endpoints REST bajo `/competencia/{competencia_id}/...` para operaciones sobre performances: llamado, resultado, DNS, tarjeta, revisión y corrección post-DNS. |
| CompetenciaHandlers | Maneja los comandos del ciclo de vida de Competencia: GenerarGrilla, AjustarGrilla, ConfirmarGrilla, IniciarCompetencia, FinalizarCompetencia. Actualiza el read model tras cada append. |
| PerformanceHandlers | Maneja los comandos del ciclo de vida de Performance: RegistrarAP, LlamarAtleta, RegistrarResultado, AsignarTarjeta, RegistrarDNS, CorregirResultado. Actualiza el read model tras cada append. |
| ParticipanteACL | Anti-Corruption Layer. Suscribe al evento AtletaInscripto de BC Registro y traduce el modelo de Atleta al modelo local de Participante. Aísla el Core Domain de cambios en BC Registro. |
| Competencia | Aggregate Root del ciclo de vida de la competencia. Contiene GrillaDeSalida e IntervaloDisciplina. Custodia los invariantes INV-C-01 a INV-C-04. |
| Performance | Aggregate Root del ciclo de vida de una performance individual. Contiene AP, RP y Tarjeta. Custodia los invariantes INV-P-01 a INV-P-14. |
| Participante | Entidad local sin aggregate propio. Representa al atleta dentro del contexto de Competencia. Creada y mantenida por el ParticipanteACL a partir de eventos de BC Registro. |
| CompetenciaEventStore | Implementa CompetenciaRepository. Persiste eventos de Competencia en la tabla `events` y reconstruye el aggregate desde el stream_id. |
| PerformanceEventStore | Implementa PerformanceRepository. Cada instancia de Performance tiene su propio stream en la tabla `events`. |
| CompetenciaReadProjection | Proyecta los eventos de dominio a tablas desnormalizadas en SQLite para servir consultas GET eficientes. La actualización es síncrona: el handler llama a la proyección tras cada append al event store. |
| competencia.db | Archivo SQLite del BC Competencia. Contiene la tabla `events` (event store) y las tablas proyectadas (read model). Es la única fuente de persistencia del BC. |

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
| Event Sourcing | CompetenciaEventStore → competencia.db | Escribe eventos de Competencia en la tabla `events` y los lee para reconstruir el aggregate. |
| Event Sourcing | PerformanceEventStore → competencia.db | Escribe y lee el stream propio de cada Performance en la tabla `events`. |
| Proyección síncrona | CompetenciaHandlers → CompetenciaReadProjection | El handler invoca la proyección síncronamente tras cada append al event store. No hay subscripción reactiva ni polling. |
| Proyección síncrona | PerformanceHandlers → CompetenciaReadProjection | Ídem para eventos de Performance que afecten el read model de grilla/estado. |
| Persistencia | CompetenciaReadProjection → competencia.db | Escribe las proyecciones desnormalizadas en las tablas del read model. |
| Consulta | CompetenciaRoutes → competencia.db | Las consultas GET de grilla y estado de competencia se resuelven contra el read model, no contra el event store. |

### Notas de diseño — BC Competencia

**Performance como aggregate separado**
`Performance` tiene su propio stream de eventos (no está anidado en `Competencia`).
Esto permite auditar el ciclo de vida de cada performance de forma independiente,
y reconstruir el estado de una performance sin cargar toda la competencia.

**Read Model y Event Store en el mismo archivo SQLite**
`competencia.db` contiene tanto la tabla `events` (append-only) como las tablas proyectadas.
No hay base de datos separada para el read model — es el mismo archivo SQLite del BC (ADR-007).
Las proyecciones se actualizan síncronamente en el mismo comando que produce los eventos (ADR-008).

**ACL en Application Layer**
El Anti-Corruption Layer vive en `application/` — no en `domain/`.
El dominio no sabe que existe Registro; solo conoce `Participante`.

---

## 5. BCs CRUD — Referencia de estructura

Los BCs Torneo, Registro, Resultados e Identidad siguen el patrón hexagonal canónico (§3)
con persistencia relacional estándar en SQLite. No requieren L3 detallado en Fase 0
— se elabora al diseñar cada BC en su SP correspondiente.

| BC | Tipo | SP | Persistencia | Notas |
|----|------|:--:|-------------|-------|
| Torneo | Supporting | SP3 | SQLite CRUD | Incluye catálogos EntidadOrganizadora y Sede |
| Registro | Supporting | SP3 | SQLite CRUD | ACL de salida hacia Competencia |
| Resultados | Supporting | SP2 | SQLite CRUD | Alimentado por CompetenciaFinalizada |
| Identidad | Generic | SP3 | SQLite CRUD | JWT cross-cutting; candidato a solución externa en H2-H3 |
| Notificaciones | Generic | SP4 | SQLite + ES | Idempotencia exactly-once; suscribe a todos los BCs |

---

## 6. Decisiones de Arquitectura — Referencia

| ADR | Decisión |
|-----|----------|
| ADR-001 | Event Sourcing para BC Competencia (aggregates Performance y Competencia) |
| ADR-002 | FastAPI como framework backend |
| ADR-003 | PWA offline-first con Service Worker + IndexedDB para el juez |
| ADR-004 | Reglas de competencia (disciplinas, categorías, tarjetas) como datos configurables en SQLite |
| ADR-005 | 6 Bounded Contexts definitivos + Event Sourcing en Competencia y Notificaciones |
| ADR-006 | Estructura de código BC-first — cada BC como paquete Python independiente |
| ADR-007 | SQLite como motor de persistencia — un archivo `.db` por Bounded Context |
| ADR-008 | Event Store como tabla `events` append-only en el SQLite del BC |
| ADR-009 | Migraciones Alembic independientes por BC |
| ADR-010 | Docker solo para producción — Cloud Run (GCP) + Litestream para backup de SQLite |
| ADR-011 | structlog para logging estructurado (JSON en prod, texto en dev) |
| ADR-012 | RFC 7807 (Problem Details) como convención de errores HTTP |

Ver `docs/adr/` para justificación completa de cada decisión.

---

## 7. L4 — Deployment (candidato)

> **Candidato:** la configuración definitiva de producción (región, memoria, concurrencia de Cloud Run,
> bucket GCS, pipeline CI/CD) se completa en SP5. Este diagrama refleja las decisiones de ADR-010.

Dos entornos con estrategias distintas. El desarrollo es directo (`uv run`), sin Docker.
La producción es un contenedor stateless en Cloud Run cuya persistencia SQLite
se replica en tiempo real a GCS mediante Litestream.

```mermaid
graph TB
    subgraph DEV["💻 Desarrollo Local"]
        direction TB
        DEV_CMD["uv run fastapi dev src/app.py"]
        DEV_DB[("data/\ncompetencia.db · torneo.db\nregistro.db · resultados.db\nidentidad.db · notificaciones.db")]
        DEV_CMD --> DEV_DB
    end

    subgraph GH["GitHub"]
        direction LR
        REPO["Repositorio\nAtaraxiaDive"]
        GHA["GitHub Actions\nCI/CD Pipeline\n(SP5)"]
        REPO -->|"push a main"| GHA
    end

    subgraph GAR["Google Artifact Registry"]
        IMG["imagen Docker\nataraxiadive:latest"]
    end

    subgraph GCP["☁️ Google Cloud Platform"]
        direction TB
        subgraph CR["Cloud Run — instancia stateless"]
            direction LR
            APP["FastAPI\n(Dockerfile)"]
            LS["Litestream\n(proceso paralelo)"]
            APP -.- LS
        end
        subgraph GCS["Cloud Storage"]
            BUCKET[("Bucket GCS\nreplicas de data/*.db")]
        end
        LS -->|"replica en tiempo real"| BUCKET
        BUCKET -->|"restaura al arrancar\nnueva instancia"| LS
    end

    subgraph EXT["Servicios Externos"]
        SMTP["Proveedor Email HTTP\n(ej: Resend / SendGrid / SES)"]
        FCM["FCM\nPush Notifications"]
    end

    GHA -->|"build + push imagen"| GAR
    GAR -->|"deploy"| CR
    APP -->|"HTTPS API"| SMTP
    APP -->|"HTTPS"| FCM
```

### Flujo de despliegue (producción)

```
1. git push → main (baseline tag)
2. GitHub Actions: pytest + designreviewer + build Dockerfile
3. push imagen → Google Artifact Registry
4. Cloud Run: despliega nueva revisión
5. Al arrancar: Litestream restaura data/*.db desde GCS
6. Instancia sirve tráfico
7. Durante operación: Litestream replica cada write a GCS en tiempo real
```

### Flujo de backup / recuperación (Litestream)

```
Escritura SQLite → WAL → Litestream detecta → replica a GCS (< 1s)
                                                      ↓
Nueva instancia Cloud Run ← restaura desde GCS ← punto de recuperación
```

### Elementos

| Elemento | Rol | Notas |
|----------|-----|-------|
| `uv run fastapi dev` | Servidor de desarrollo | Sin Docker — ADR-010 |
| `data/<bc>.db` (local) | Persistencia en dev | 6 archivos SQLite, excluidos de git |
| GitHub Actions | CI/CD | Pipeline completo en SP5; en SP1-SP4 se ejecuta manualmente |
| Google Artifact Registry | Registro de imágenes | Imagen de producción optimizada |
| Cloud Run | Runtime de producción | Stateless — escala a cero entre torneos |
| Litestream | Replicación SQLite | Proceso paralelo al servidor; replica WAL a GCS |
| Cloud Storage (GCS) | Backup continuo de SQLite | Punto de restauración al arrancar nueva instancia |
| SMTP externo | Envío de emails | Delegado — SendGrid u otro proveedor |
| FCM | Push notifications | Delegado — Firebase Cloud Messaging |

---

## 8. Uso actual

Este documento se conserva como referencia histórica del diseño producido antes
de la implementación incremental. No debe usarse como fuente canónica de estado
ni como contrato API vigente.

Fuentes actuales:

1. `docs/architecture/` — arquitectura vigente.
2. `src/*/api/router.py` — contrato HTTP observable en implementación.
3. `docs/plans/sp5/PLAN-SP5.md` — alcance vigente de SP5.

---

*Documento creado: 2026-03-19 — Semana 0, Fase 0*
*v1.1 (2026-03-20): SQLite por BC (ADR-007/008), proyección síncrona sin NOTIFY, ADR-001..ADR-012*
*Modelo: C4 (Simon Brown) — diagramas Mermaid*
*Fuentes: Context Map v1.1 · Domain Model v1.0 · ADR-001 a ADR-012*
*Mantenido por: Claude Cowork + Victor Valotto*
