# ADR-007: SQLite como motor de persistencia — un archivo por Bounded Context

| Campo | Valor |
|-------|-------|
| **Estado** | Aceptada |
| **Fecha** | 2026-03-20 |
| **Autores** | Victor Valotto |
| **Relacionado** | ADR-005 (Bounded Contexts), ADR-006 (estructura BC-first), ADR-008 (Event Store) |

---

## Contexto

El sistema requiere una estrategia de persistencia para 6 Bounded Contexts con
patrones de acceso heterogéneos: 4 BCs CRUD (Torneo, Registro, Resultados,
Identidad) y 2 BCs con Event Sourcing (Competencia, Notificaciones).

La arquitectura de referencia (`02-arquitectura_referencia.md`) propuso
PostgreSQL como motor principal, justificado por JSONB y soporte de schemas
para aislación entre BCs. Sin embargo, la escala real del sistema y el
carácter experimental del proyecto abren la pregunta: ¿PostgreSQL es la
elección correcta para este contexto?

**Escala real de AtaraxiaDive:**
- 4 torneos por año
- ~100 atletas por torneo
- ~500 performances por torneo
- 50 usuarios concurrentes como máximo
- Pico de escritura durante ejecución: jueces por disciplina/andarivel,
  con contención mínima (cada juez opera en su propio andarivel)

---

## Opciones Consideradas

**Opción A — PostgreSQL con schemas por BC:**
Una instancia PostgreSQL, un schema por BC (`competencia`, `torneo`, etc.).
Aislación lógica, operación de servidor requerida.

**Opción B — SQLite con un archivo por BC:**
Un archivo `.db` por BC (`competencia.db`, `torneo.db`, etc.).
Aislación física real, cero infraestructura de servidor.

**Opción C — PostgreSQL compartido sin schemas:**
Una instancia, tablas prefijadas por BC (`competencia_events`, `torneo_torneos`).
Sin aislación real — descartada.

---

## Decisión

Se adopta **SQLite con un archivo por BC (Opción B)**.

```
data/
├── competencia.db     ← event store + read models (Core Domain)
├── torneo.db          ← ciclo de vida del torneo, disciplinas, sede
├── registro.db        ← atletas, inscripciones, anuncios
├── resultados.db      ← rankings, publicaciones
├── identidad.db       ← usuarios, roles, tokens
└── notificaciones.db  ← notification events, outbox
```

Cada BC accede **únicamente a su propio archivo**. No hay JOINs entre archivos.
La comunicación entre BCs se realiza a través de los puertos del dominio
(ACL en `infrastructure/` del BC consumidor), nunca por acceso directo a
la DB de otro BC.

---

## Justificación

### Por qué SQLite es suficiente

La concurrencia de escritura serializada de SQLite es el argumento habitual
en contra para aplicaciones web. En AtaraxiaDive este riesgo es bajo porque:

1. **El pico de escritura está naturalmente particionado:** durante la ejecución,
   cada juez opera en su andarivel específico. La contención real es mínima.
2. **El modo WAL de SQLite** (`PRAGMA journal_mode=WAL`) permite lecturas
   concurrentes mientras una escritura está en progreso, eliminando el bloqueo
   más común.
3. **La escala no lo justifica:** 500 performances por torneo, 4 torneos al año.
   No es un caso de alto throughput.

### Por qué un archivo por BC y no un único archivo

- **Aislación física real:** un BC no puede leer datos de otro BC accidentalmente.
  Refuerza la frontera de BC a nivel de infraestructura, no solo de código.
- **Independencia de migraciones:** el schema de cada BC evoluciona sin afectar
  los demás. Las migraciones de Alembic se organizan por BC.
- **Coherente con BC-first (ADR-006):** la estructura `src/<bc>/` tiene su
  correspondencia directa en `data/<bc>.db`.

### Dimensión experimental

El puerto `RepositorioPuerto` en `<bc>/domain/ports/` abstrae completamente
el motor de persistencia. Si en SP3 o SP4 la escala o los requisitos justifican
migrar a PostgreSQL, el cambio afecta únicamente `<bc>/infrastructure/repositories/`
— el dominio y la aplicación no se tocan.

Esto convierte la migración eventual en un caso de prueba empírico de la
arquitectura hexagonal: ¿el puerto absorbe el cambio sin fricción en el dominio?

---

## Consecuencias

**Positivas:**
- Cero infraestructura de servidor para desarrollo y testing
- `docker-compose.yml` más simple (sin servicio de DB)
- Backup trivial: copiar el archivo `.db`
- Tests unitarios y de integración más rápidos (SQLite en memoria: `:memory:`)
- Onboarding simplificado: `git clone` + `uv sync` es suficiente para levantar

**Negativas / trade-offs:**
- Sin JSONB con índices (reemplazado por columnas explícitas o JSON sin índice)
- Backup en producción requiere estrategia explícita (Litestream o copia periódica)
- Si la concurrencia crece significativamente, la migración a PostgreSQL
  es necesaria (condición de escape documentada abajo)

**Condición de escape:**
Migrar a PostgreSQL si se cumple cualquiera de estas condiciones:
- Más de 200 escrituras simultáneas sostenidas durante la ejecución
- Necesidad de full-text search avanzado sobre datos de atletas
- Requerimiento de replicación multi-servidor

---

## Notas del Experimento

Esta decisión es deliberadamente experimental. La hipótesis es que la
arquitectura hexagonal hace al sistema agnóstico al motor de persistencia,
y que SQLite es suficiente para la escala real de AtaraxiaDive.

Si en una baseline futura se decide migrar a PostgreSQL, la retrospectiva
documentará cuánto cambió por fuera de `infrastructure/repositories/` —
ese dato alimenta directamente el análisis de RQ1 del experimento IEDD.
