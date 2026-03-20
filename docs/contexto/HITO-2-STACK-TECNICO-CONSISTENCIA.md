# HITO-2 — Stack Técnico SP1 y Consistencia Documental

| Campo | Valor |
|-------|-------|
| **Documento** | HITO-2 — Análisis experimental |
| **Fecha** | 2026-03-20 |
| **Sesiones involucradas** | Pre-SP1 (ADR-007..012) + Revisión de consistencia |
| **Hipótesis activas** | RQ1 (fricción de ecosistema), RQ2 (calidad de especificaciones) |
| **Relacionado** | `HITO-1-ADHERENCIA-IEDD-FASE0.md` · ADR-007 a ADR-012 |

---

## 1. Contexto

Entre el cierre de Fase 0 (tag `v0.1.0`) y el arranque de SP1, se tomaron dos grupos
de decisiones con consecuencias experimentales relevantes:

1. **Decisiones técnicas transversales (ADR-007 a ADR-012):** definición del stack
   tecnológico completo para SP1 — persistencia, event store, migraciones, entorno,
   logging y manejo de errores HTTP.

2. **Revisión de consistencia documental:** revisión sistemática de todos los documentos
   del proyecto para alinearlos con las decisiones de los ADRs. Una sesión completa
   dedicada exclusivamente a este trabajo.

Ambas actividades son evidencia empírica relevante para el experimento IEDD.

---

## 2. Bloque ADR-007 a ADR-012 — El Stack Técnico como Unidad Coherente

### 2.1 Decisiones tomadas

| ADR | Decisión | Motivación principal |
|-----|----------|---------------------|
| ADR-007 | SQLite — un archivo por BC | Escala real no justifica PostgreSQL; aislación física de BCs |
| ADR-008 | Event Store como tabla `events` append-only en SQLite | Sin licencias restrictivas; puerto hexagonal abstrae el motor |
| ADR-009 | Alembic independiente por BC | Coherencia con BC-first (ADR-006) y un `.db` por BC (ADR-007) |
| ADR-010 | Docker solo en prod — Cloud Run + Litestream | Sin Docker Desktop disponible en dev; SQLite no requiere servidor |
| ADR-011 | structlog | JSON en prod (Cloud Logging), texto legible en dev |
| ADR-012 | RFC 7807 | Estándar IETF; manejo genérico de errores en el cliente |

### 2.2 Aprendizaje — El stack como cascada de decisiones

Los 6 ADRs no son independientes: forman una cascada donde cada decisión habilita
o condiciona a la siguiente.

```
ADR-007 (SQLite por BC)
  └─► ADR-008 (Event Store en SQLite — sin servidor externo)
        └─► ADR-009 (Alembic por BC — un .db, un historial de migraciones)
ADR-007
  └─► ADR-010 (sin servidor de DB → sin Docker en dev → Cloud Run viable)
        └─► ADR-011 (Cloud Run → Cloud Logging → JSON obligatorio en prod)
ADR-002 (FastAPI) + ADR-006 (BC-first)
  └─► ADR-012 (RFC 7807 consistente entre todos los BCs)
```

**Implicación para IEDD:** las decisiones de infraestructura tienen dependencias
entre sí tan reales como las dependencias del dominio. IEDD modela bien las
dependencias de dominio (capas 1-3) pero no tiene un mecanismo explícito para
capturar la cadena de decisiones técnicas. Los ADRs lo resuelven, pero la
relación entre ADRs no está formalizada en la metodología.

**Hipótesis derivada:**
> Una US-IEDD implementada bajo un ADR que depende de otro ADR no formalizado
> produce deuda técnica oculta. La cadena ADR-007→ADR-009 debería ser visible
> al especificar US-1.1.1 (fundación técnica).

### 2.3 Aprendizaje — SQLite como decisión de escala, no de conveniencia

La elección de SQLite en lugar de PostgreSQL podría interpretarse como una
decisión de comodidad ("es más fácil"). El análisis muestra que no es así:

- La escala real del sistema (500 performances/torneo, 4 torneos/año, 50 usuarios
  concurrentes máximo) no justifica un servidor de base de datos.
- La aislación física por BC (`competencia.db`, `torneo.db`, etc.) refuerza la
  frontera de BC a nivel de infraestructura — no solo de código.
- El puerto `RepositorioPuerto` en `domain/ports/` hace que la migración futura
  a PostgreSQL sea un cambio de adaptador, no un cambio de dominio.

**El experimento dentro del experimento:** si en SP3 o SP4 la escala o los
requisitos justifican migrar a PostgreSQL, la retrospectiva de esa baseline
documentará cuánto cambió fuera de `infrastructure/repositories/`. Ese dato
es evidencia directa de que la arquitectura hexagonal absorbe el cambio de motor
de persistencia — o no.

### 2.4 Aprendizaje — La ausencia de Docker en dev como decisión productiva

ADR-010 decide no usar Docker en desarrollo por una restricción concreta (sin
Docker Desktop disponible). La consecuencia no documentada en el ADR: elimina
una fuente de fricción real en el ciclo de trabajo diario.

Con SQLite, el entorno de desarrollo es `git clone` + `uv sync` + `uv run fastapi dev`.
Sin imagen, sin volumen, sin puerto mapeado, sin `docker-compose up`.

La diferencia entre dev y prod (SQLite local vs Cloud Run + Litestream) es real
y está documentada como trade-off. Pero la simplificación del ciclo de desarrollo
tiene un valor que va más allá de la restricción técnica que la motivó.

**Observación para IEDD:** las restricciones del desarrollador (hardware, licencias,
herramientas disponibles) son datos de contexto que deberían ser explícitos en la
Capa 1 del marco — no supuestos implícitos que aparecen recién al tomar decisiones
técnicas.

---

## 3. Revisión de Consistencia Documental — Evidencia sobre RQ1

### 3.1 El trabajo realizado

Al tomar las decisiones ADR-007 a ADR-012, varios documentos escritos antes de esos
ADRs quedaron inconsistentes — principalmente porque asumían PostgreSQL como motor
de persistencia.

La revisión sistemática cubrió:

| Carpeta | Archivos revisados | Archivos modificados |
|---------|:-----------------:|:-------------------:|
| `docs/adr/` | 12 | 4 (ADR-001, 002, 004, 006) |
| `docs/design/` | 6 | 3 (architecture, domain-model, estrategia-bc) |
| `docs/traceability/` | 1 | 1 (matrix.md) |
| `CLAUDE.md` | 1 | 1 |
| `docs/plans/` | 1 | 0 (ya era consistente) |
| `docs/requirements/` | 1 | 0 (documento de entrada) |
| `docs/contexto/`, `docs/dominio/` | varios | 0 (documentos de entrada — no se modifican) |

**Total: 9 archivos modificados en 4 carpetas.** Una sesión completa de trabajo.

### 3.2 Causa raíz de la inconsistencia

La inconsistencia no fue un error de proceso — fue una consecuencia natural de la
secuencia IEDD:

1. Los documentos de Fase 0 (architecture.md, domain-model.md, CLAUDE.md) se
   escribieron cuando el stack técnico era PostgreSQL (supuesto inicial de los
   documentos de dominio).
2. Las decisiones ADR-007..010 cambiaron ese supuesto de forma justificada.
3. Los documentos derivados no se actualizaron de inmediato — se actualizaron
   en la siguiente sesión.

El punto clave: **la inconsistencia apareció porque una decisión tardía (ADR-007)
contradijo un supuesto de documentos tempranos.** Esto es esperable en cualquier
proceso iterativo.

### 3.3 Aprendizaje — Documentos de entrada vs documentos derivados

Durante la revisión emergió una distinción metodológica que no estaba formalizada:

**Documentos de entrada (no se modifican con los ADRs):**
- `docs/contexto/` — fundamentos del experimento
- `docs/dominio/` — descripción del dominio tal como existía antes del proyecto
- `docs/requirements/vision.md` — Capa 1 del IEDD

Estos documentos capturan el conocimiento previo al análisis técnico. Modificarlos
retroactivamente destruiría la evidencia de "qué sabíamos al empezar".

**Documentos derivados (se actualizan cuando cambia un ADR):**
- `docs/design/` — decisiones de diseño y arquitectura
- `docs/adr/` — las propias decisiones (referencias cruzadas entre ADRs)
- `CLAUDE.md` — memoria operativa del proyecto
- `docs/traceability/matrix.md` — trazabilidad RF→implementación
- `docs/plans/` — especificaciones de US

**Implicación metodológica:** cuando se aprueba un ADR que contradice supuestos
de documentos derivados, la revisión de consistencia debería ser un paso explícito
en el workflow — no una sesión posterior. Ver `docs/plans/WORKFLOW-DESARROLLO.md`
para posible integración.

### 3.4 Aprendizaje — El costo de la revisión es proporcional a la "distancia" del cambio

No todos los cambios de ADR tienen el mismo costo de consistencia. ADR-007
(PostgreSQL → SQLite) tuvo alto impacto porque:

1. **Afecta la capa de infraestructura** — la más referenciada en diagramas técnicos.
2. **Contradice un supuesto de documentos tempranos** — PostgreSQL aparecía en el
   documento de arquitectura de referencia (dominio).
3. **La tecnología es visible en múltiples capas** — L1 (stack), L2 (containers),
   L3 (infrastructure layer), herramientas (asyncpg).

ADR-012 (RFC 7807), en contraste, no generó ningún impacto en documentos existentes
porque no contradecía ningún supuesto previo — simplemente formalizó algo no definido.

**Regla emergente:**
> El costo de consistencia de un ADR es proporcional a cuántos supuestos previos
> contradice, no a la magnitud del cambio técnico en sí.

### 3.5 Evidencia sobre RQ1

RQ1 pregunta: *¿El ecosistema CM + Dev Kit + Software Limpio funciona integrado,
o cada herramienta genera fricción de coordinación?*

Esta sesión aporta evidencia parcial:

- **El CM Framework** (ADRs + documentos) genera fricción de consistencia cuando
  las decisiones técnicas llegan después de los documentos de diseño. La fricción
  es manejable pero real: una sesión de trabajo.
- **La fricción no es de integración de herramientas** — es de mantenimiento de
  coherencia entre artefactos a medida que el proyecto evoluciona. Es fricción
  inherente a cualquier proceso con documentación rigurosa.
- **La herramienta que más redujo la fricción** fue la revisión sistemática por
  carpeta, guiada por los ADRs como fuente de verdad. Sin esa estructura, la
  revisión sería más costosa y menos completa.

**Observación:**
> La fricción de consistencia documental en IEDD no es una falla del método —
> es el precio de tener documentación rigurosa en un proceso iterativo. El valor
> diferencial está en que la inconsistencia es detectable y corregible, a diferencia
> de proyectos sin documentación donde el supuesto incorrecto simplemente se
> implementa.

---

## 4. Hipótesis Activas para BL-001

| # | Hipótesis | Métrica propuesta |
|---|-----------|-------------------|
| H-2.1 | El puerto hexagonal absorbe el cambio SQLite→PostgreSQL sin modificar `domain/` ni `application/` | Si se migra: contar archivos cambiados fuera de `infrastructure/` |
| H-2.2 | El costo de consistencia se reduce si la revisión es inmediata al aprobar el ADR | Comparar tiempo de revisión en este caso vs. próximo bloque de ADRs |
| H-2.3 | Los ADRs que contradicen supuestos previos generan más inconsistencias que los que formalizan decisiones nuevas | Clasificar ADRs futuros y medir archivos impactados por tipo |
| H-2.4 | La distinción documentos-de-entrada / documentos-derivados reduce el scope de revisión y elimina trabajo innecesario | Validar en próximos bloques de ADRs |

---

## 5. Próximos Pasos

- **BL-001 (cierre SP1):** evaluar H-2.1 si se decide experimentar con el adaptador
  de event store (SQLite → NATS JetStream candidato per ADR-008).
- **WORKFLOW-DESARROLLO.md:** agregar paso explícito de revisión de consistencia
  al workflow de aprobación de ADRs.
- **SP1:** la US-1.1.1 (fundación técnica) implementa directamente ADR-007, ADR-008
  y ADR-009 — primer caso de prueba de la cadena de decisiones.

---

*Documento creado: 2026-03-20 — Pre-SP1*
*Tipo: análisis experimental — alimenta paper IEDD y retrospectiva BL-001*
*Mantenido por: Claude Cowork + Victor Valotto*
