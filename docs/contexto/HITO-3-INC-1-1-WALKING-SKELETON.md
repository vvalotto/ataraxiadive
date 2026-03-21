# HITO-3 — Inc 1.1: Walking Skeleton y el Primer Contacto con el Código

| Campo | Valor |
|-------|-------|
| **Documento** | HITO-3 — Análisis experimental |
| **Fecha** | 2026-03-21 |
| **Incremento cubierto** | Inc 1.1 — Fundación técnica |
| **Hipótesis activas** | RQ1 (fricción de ecosistema), H-1.1, H-2.5 |
| **Relacionado** | `HITO-2-STACK-TECNICO-CONSISTENCIA.md` · PR #12 · Issue #1 |

---

## 1. Contexto

Inc 1.1 es el primer incremento de código real del proyecto. No hay US-IEDD —
es una tarea técnica pura: scaffold del BC Competencia, Event Store SQLite,
migraciones Alembic, health-check. Su objetivo es el walking skeleton: la
arquitectura mínima que valida que todas las piezas del stack funcionan juntas.

Este HITO documenta los aprendizajes experimentales de ese primer contacto con
el código, con foco en tres dimensiones:

1. ¿El flujo de trabajo acordado (branching + quality gates + PR) funciona en la práctica?
2. ¿Qué fricciones técnicas emergieron al implementar el stack planificado en los ADRs?
3. ¿Qué aprendizajes retroalimentan las hipótesis activas del experimento?

---

## 2. El Flujo de Trabajo en Acción — Primera Evidencia

### 2.1 Estrategia de branching liviana: confirmada

El flujo acordado funcionó sin fricciones:

```
develop
  └── feature/inc-1.1-fundacion-tecnica
        ├── commit: chore(infra): asyncpg → aiosqlite
        ├── commit: feat(domain): EventStorePort
        ├── commit: feat(infra): SQLiteEventStore
        ├── commit: feat(infra): migraciones Alembic
        ├── commit: feat(api): GET /health
        └── commit: test(infra): 7 tests integración
  → PR #12 → merge develop → Issue #1 cerrado
```

La granularidad "commit por tarea" dentro de un branch de incremento resultó
natural: cada tarea tiene un entregable concreto y los commits son atómicos.
No hubo necesidad de rebase ni de limpiar historial.

**Aprendizaje L-3.1:**
> La estrategia de branching liviana (PR directo a develop, commits por tarea en
> incrementos técnicos) es apropiada para un proyecto solo. No genera overhead
> innecesario y el historial de git refleja con fidelidad el trabajo realizado.

### 2.2 Quality gates: sin fricciones en Inc 1.1

- **CodeGuard (pre-commit):** corrió en cada commit, sin warnings significativos.
- **DesignReviewer (pre-push):** 0 violations CRITICAL — la arquitectura hexagonal
  se respetó desde el primer commit.
- **DesignReviewer manual (cierre Inc 1.1):** confirmó 0 CRITICAL.

El hecho de que no haya habido violaciones en el primer incremento es esperable
(no hay lógica de dominio todavía), pero confirma que la configuración de los
quality gates en `pyproject.toml` es correcta.

**Aprendizaje L-3.2:**
> Los quality gates no generaron fricción en Inc 1.1. La prueba real será en Inc 1.2
> cuando el aggregate `Performance` imponga dependencias más complejas entre capas.

---

## 3. Fricciones Técnicas — Lo que los ADRs no anticiparon

### 3.1 pyproject.toml tenía `asyncpg` en lugar de `aiosqlite`

El archivo de configuración original (creado antes de los ADRs de stack) tenía
`asyncpg` como dependencia. Fue detectado al iniciar el incremento y corregido
antes de escribir una línea de código de dominio.

**Análisis:** Esta fricción es consecuencia directa de la hipótesis H-2.5 —
la documentación de stack (ADRs) se completó antes que el archivo de configuración
se actualizara. El gap entre la decisión (ADR-007) y su reflejo en el código
de configuración generó una inconsistencia que debió corregirse en el momento de
implementar.

**Aprendizaje L-3.3:**
> Los ADRs de stack deben tener un paso explícito de "impacto en configuración" que
> liste qué archivos del proyecto deben actualizarse al tomar la decisión. Un ADR
> que no se refleja en `pyproject.toml` es una decisión incompleta.

### 3.2 Alembic síncrono vs. aiosqlite asíncrono

La configuración de Alembic requirió entender que las migraciones usan el driver
SQLite síncrono estándar, mientras que el código de aplicación usa `aiosqlite`
(asíncrono). Son dos modos de acceso distintos para el mismo archivo `.db`.

**Análisis:** No está documentado en los ADRs. ADR-009 dice "Alembic por BC" pero
no especifica el modo de conexión. Para el desarrollador que retome el proyecto,
esta distinción no es obvia.

**Aprendizaje L-3.4:**
> ADR-009 debe incluir una nota explícita sobre el modo de conexión:
> "Alembic usa el driver SQLite síncrono (`sqlite:///`) para las migraciones.
> El runtime usa aiosqlite (`sqlite+aiosqlite://`). Son configuraciones distintas
> con el mismo archivo `.db`."

### 3.3 pythonpath en pytest — brecha entre BC-first y convención Python

La estructura BC-first (`src/competencia/...`) requiere que `src/` esté en el
`PYTHONPATH` para que los imports funcionen sin el prefijo `src.`. Esto no es
automático en pytest y debió agregarse como `pythonpath = ["src"]` en
`pyproject.toml`.

**Análisis:** Es una consecuencia predecible de ADR-006 (BC-first) que no fue
documentada. Cualquier desarrollador nuevo que clone el proyecto y corra pytest
sin esta configuración verá errores de import que no son obvios.

**Aprendizaje L-3.5:**
> ADR-006 o el CLAUDE.md deben documentar que la estructura BC-first requiere
> `pythonpath = ["src"]` en pytest y que los imports no usan el prefijo `src.`.

---

## 4. Validación de Hipótesis Activas

### H-1.1 — El Event Sourcing justifica la complejidad en BC Competencia

**Estado:** Parcialmente observable. Inc 1.1 implementa solo el Event Store
(infraestructura). La complejidad real del ES aparecerá en Inc 1.2 cuando el
aggregate `Performance` emita y recargue eventos.

**Evidencia preliminar:** El patrón port/adapter funcionó limpiamente:
`EventStorePort` en `domain/ports/` es desconocedor de SQLite. La migración
futura a otro motor sería un cambio de adaptador. Esto sugiere que la complejidad
del ES está bien contenida.

**Próxima verificación:** Inc 1.2 — ¿cuántas líneas requiere reconstitución del
aggregate desde eventos vs. carga directa de base de datos?

### H-2.5 — Capa 4 antes de Capa 3 como patrón recurrente con IA

**Estado:** Confirmado parcialmente. Inc 1.1 es pura Capa 4 (infraestructura)
sin Capa 3 (especificaciones US-IEDD). Esto es correcto para una tarea técnica,
pero el patrón se repite: antes de poder especificar US-1.2.1 con precisión, fue
necesario tener la infraestructura del Event Store operativa.

**Implicación:** La secuencia IEDD pura sería: especificar todas las US → luego
implementar. En la práctica con IA, la fundación técnica debe preceder a la
especificación detallada porque la IA necesita contexto concreto (¿qué métodos
tiene el EventStore? ¿qué retorna?) para generar invariantes precisos.

---

## 5. Nueva Hipótesis Derivada

**H-3.1 — Los ADRs de stack generan deuda de configuración si no incluyen impacto en artefactos**

> Cada ADR que toma una decisión de stack (librería, herramienta, driver) debería
> listar explícitamente los archivos de configuración del proyecto que deben
> actualizarse como consecuencia. Sin este paso, la decisión queda documentada
> pero no implementada hasta que alguien lo detecta durante el desarrollo.
>
> **Verificación:** Revisar ADR-007 a ADR-012 y agregar sección "Impacto en
> configuración" en cada uno. Contar cuántas inconsistencias se encuentran.

---

## 6. Resumen de Aprendizajes

| ID | Aprendizaje | Impacto |
|----|-------------|---------|
| L-3.1 | Branching liviano con commits por tarea es natural y efectivo para un dev solo | Workflow — confirma la estrategia elegida |
| L-3.2 | Quality gates sin fricción en Inc 1.1; prueba real en Inc 1.2 con lógica de dominio | Quality — baseline para comparar |
| L-3.3 | ADRs de stack deben incluir "impacto en configuración" explícito | Proceso — mejora ADR template |
| L-3.4 | Distinción Alembic-síncrono / aiosqlite-async no documentada en ADR-009 | Documentación — deuda técnica menor |
| L-3.5 | BC-first requiere `pythonpath = ["src"]` en pytest — no es automático | Configuración — debe estar en CLAUDE.md |

---

*2026-03-21 — Inc 1.1 completado. Próximo: HITO-4 al cerrar Inc 1.2 (aggregate Performance).*
