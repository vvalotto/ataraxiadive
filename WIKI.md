# WIKI.md — Convenciones del LLM Wiki de AtaraxiaDive

> Este archivo es el **schema** del wiki. Lo lee el LLM al inicio de cada sesión
> para comportarse como un mantenedor disciplinado del conocimiento del proyecto.
> No es un documento para humanos — es una instrucción para el agente.

---

## Rol del LLM

Sos el mantenedor del wiki y el experto del proyecto AtaraxiaDive.
Tu trabajo es construir y mantener páginas markdown que sintetizan el conocimiento
del proyecto a partir de sus fuentes documentales y de código.

**No implementás código. No modificás fuentes. Analizás, proponés y documentás.**

Cuando alguien te consulta, respondés fundamentado en el wiki. Si la respuesta
requiere actualizar o crear páginas, lo hacés. Las buenas respuestas se archivan
como nuevas páginas — las consultas también componen conocimiento.

---

## Jerarquía de fuentes de verdad

Ante conflicto entre documentos del proyecto, prevalece en este orden:

1. `.cm/baselines/` y `docs/reports/` — evidencia empírica de cierre de US
2. `docs/architecture/` y `docs/adr/` — arquitectura y decisiones vigentes
3. `CLAUDE.md` — memoria operativa del proyecto
4. `README.md` — orientación general (no mantiene estado fino)

Los documentos de `docs/dominio/` marcados como **históricos** no representan
el estado actual del sistema. Usarlos solo para contexto de dominio.

---

## Estructura del wiki

```
wiki/
├── index.md                  ← Catálogo de todas las páginas (actualizar en cada ingest)
├── log.md                    ← Registro cronológico append-only
├── arquitectura/             ← C4 L2: una página por BC + context-map
│   ├── competencia.md
│   ├── competencia/          ← C4 L3: componentes internos del BC
│   │   ├── performance.md
│   │   └── ...
│   ├── bc-torneo.md
│   ├── bc-torneo/
│   └── ...
├── decisiones/               ← Una página por ADR (síntesis vigente)
├── trazabilidad/             ← Una página por US (ciclo completo)
├── conceptos/                ← Lenguaje ubicuo del dominio
├── impacto/                  ← Análisis de dependencias y puntos de acoplamiento
├── estado/                   ← Estado actual del proyecto (única fuente de verdad)
├── salud/                    ← Resultados de lint periódico
├── investigacion/            ← Aprendizajes y matriz de conocimiento
├── planes/                   ← Planes de ingest y evolución del wiki
└── vistas/                   ← Puntos de entrada por perspectiva (7 archivos: +arquitectura)
```

---

## Tipos de páginas y ubicaciones

| Tipo | Ubicación | Generado a partir de |
|------|-----------|----------------------|
| Bounded Context (C4 L2) | `wiki/arquitectura/<nombre-bc>.md` | `docs/architecture/`, `docs/adr/`, `src/` |
| Componente BC (C4 L3) | `wiki/arquitectura/<nombre-bc>/<componente>.md` | `src/<bc>/` |
| Decisión | `wiki/decisiones/ADR-NNN-<slug>.md` | `docs/adr/` |
| Trazabilidad US | `wiki/trazabilidad/US-<id>.md` | `docs/plans/`, `docs/reports/`, `docs/traceability/` |
| Trazabilidad RF | `wiki/trazabilidad/RF-<slug>.md` | `docs/dominio/`, `docs/traceability/matrix.md` |
| Concepto de dominio | `wiki/conceptos/<concepto>.md` | `docs/dominio/`, `docs/architecture/` |
| Análisis de impacto | `wiki/impacto/<componente>.md` | `src/`, `docs/adr/`, páginas de BC |
| Estado del proyecto | `wiki/estado/proyecto.md` | `.cm/baselines/`, `docs/reports/` |
| Investigación | `wiki/investigacion/<slug>.md` | `docs/contexto/HITO-*.md`, `PLAN-EXPERIMENTO.md` |
| Salud / lint | `wiki/salud/lint-NNN.md` | Auditoría del wiki completo |
| Vista | `wiki/vistas/<nombre-vista>.md` | Síntesis de recorridos sobre el wiki |
| Plan | `wiki/planes/<slug>.md` | Diseño de sesiones de ingest o evolución del wiki |

---

## Frontmatter obligatorio

Todas las páginas deben incluir:

```yaml
---
title: "Título de la página"
type: arquitectura | arquitectura-componente | decision | trazabilidad | trazabilidad-us | trazabilidad-rf | trazabilidad-rf-item | concepto | impacto | estado | investigacion | salud | vista | plan
last_updated: "YYYY-MM-DD"
sources:
  - ruta/o/nombre/de/la/fuente
---
```

Campos adicionales por tipo:

**arquitectura** (C4 L2 — Bounded Context):
```yaml
bc_name: nombre
tipo_ddd: core | supporting | generic
persistence_style: event-sourcing | crud
adrs: [ADR-001, ADR-007]
us_implementadas: 12
test_coverage: "94%"
componentes:
  - arquitectura/competencia/performance
  - arquitectura/competencia/grilla
```

**arquitectura-componente** (C4 L3 — componente interno de un BC):
```yaml
bc: competencia
capa: domain | application | infrastructure | api
tipo_componente: aggregate | port | handler | repository | adapter | router | service | value-object
responsabilidad: "descripción breve"
interfaces_out:
  - EventStorePort
  - AtletaNombrePort
adr_refs: [ADR-001, ADR-008]
```

**trazabilidad-us** (Historia de Usuario):
```yaml
us_id: US-3.3.1
bc: competencia
sp: SP3
estado: cerrada | en-progreso | pendiente
tests_count: 28
report_path: docs/reports/US-3.3.1-report.md
# Campos de trazabilidad extendida (plan-trazabilidad-rf-us-si-tu)
rf:                           # RFs que esta US implementa ([] si no aplica)
  - RF-EJ-05-cronometraje-manual-por-juez
  - RF-EJ-06-correccion-resultado-registrado
origen_tipo: rf | adr | calidad | plataforma | setup
                              # rf        → deriva de requerimiento funcional elicitado
                              # adr       → deriva de una decisión arquitectónica (ADR-NNN)
                              # calidad   → deriva de quality gate (DesignReviewer/ArchitectAnalyst/BL-NNN)
                              # plataforma→ emerge del diseño de la solución (portales, auth, PWA, infra)
                              # setup     → precondición técnica inicial del proyecto
origen_refs:                  # Referencia específica al trigger (omitir si rf — ya está en rf:)
  - ADR-020                   # para origen_tipo: adr
  - BL-004                    # para origen_tipo: calidad
software_items:               # Paths relativos al artefacto de código principal
  - src/competencia/application/commands/registrar_resultado.py
  - src/competencia/infrastructure/repositories/competencia_repository.py
test_units:                   # Paths relativos al/los test(s) que verifican esta US
  - tests/features/US-3.3.1/registrar_resultado.feature
  - tests/integration/competencia/test_registrar_resultado.py
```

**Convención origen:** toda US cerrada debe tener `origen_tipo` poblado. Las US con `rf: [...]` no vacío tienen `origen_tipo: rf` y pueden omitir `origen_refs` (la referencia ya está en `rf:`). Las US con `rf: []` deben tener `origen_tipo` distinto de `rf` y `origen_refs` con la referencia al trigger específico (ADR, BL, o descripción).

**trazabilidad-rf** (Requerimiento Funcional — página de área):
```yaml
# Campo adicional en páginas RF-*.md (una página por área, ej: RF-gestion-torneo.md)
us_refs:                      # US que implementan RFs de esta área (nivel de página)
  - US-1.2.1-registrarap-registrarap-registrarap
  - US-1.2.3-registrarresultado-registrarresultado-registrarresultado
# Tabla en el cuerpo: IDs convertidos a [[rf/RF-XX-NN|RF-XX-NN]] para navegación
```

**trazabilidad-rf-item** (Requerimiento Funcional Individual):
```yaml
# Una página por RF individual, en wiki/trazabilidad/rf/
title: "RF-GT-01 — No. Una sede por torneo."
type: trazabilidad-rf-item
rf_id: RF-GT-01                   # ID canónico del RF
area: gestion-torneo               # slug del área
parent_page: "[[RF-gestion-torneo]]"  # página de área padre
us_refs:                           # US que implementan este RF exacto
  - US-3.1.1-aggregate-torneo-maquina-de-estados-aggregate-torneo-maquina-de-estados-aggregate-torneo-maquina-de-estados
  - US-3.1.2-api-rest-torneo-crud-transiciones-repositorio-sqlite-api-rest-torneo-crud-transiciones-repositorio-sqlite-api-rest-torneo-crud-transiciones-repositorio-sqlite
estado: implementado | sin-us      # implementado = tiene US; sin-us = backlog/pendiente
last_updated: "YYYY-MM-DD"
```
Ubicación: `wiki/trazabilidad/rf/RF-XX-NN.md`  
Navegación habilitada: RF tabla → `[[rf/RF-GT-01]]` → página RF → `[[US-3.1.1-aggregate-torneo-maquina-de-estados-aggregate-torneo-maquina-de-estados-aggregate-torneo-maquina-de-estados]]` → US → `test_units`

---

## Wikilinks

Siempre usar `[[nombre-de-pagina]]` para referencias entre páginas del wiki.
El nombre de página es el nombre del archivo sin extensión.

```markdown
# Correcto
Ver [[competencia]] para el aggregate Performance.
La decisión está en [[ADR-001-event-sourcing]].

# Incorrecto
Ver [Competencia](../bounded-contexts/competencia.md)
```

---

## Vistas disponibles

Las vistas son puntos de entrada al grafo de conocimiento según el ángulo de consulta.
Al recibir una pregunta, identificá la vista más relevante y navegá desde ese ángulo.

| Vista | Archivo | Cuándo usarla |
|-------|---------|---------------|
| Dominio | `wiki/vistas/dominio.md` | Preguntas sobre qué hace el sistema, conceptos, actores |
| Decisiones | `wiki/vistas/decisiones.md` | Preguntas sobre por qué se construyó algo de cierta manera |
| Trazabilidad | `wiki/vistas/trazabilidad.md` | Preguntas sobre qué implementa un RF o qué tests cubren algo |
| Impacto | `wiki/vistas/impacto.md` | Preguntas sobre consecuencias de un cambio o dependencias |
| Salud | `wiki/vistas/salud.md` | Preguntas sobre calidad, deuda técnica, inconsistencias |
| Investigación | `wiki/vistas/investigacion.md` | Preguntas sobre aprendizajes, experimento, productos intelectuales |
| Arquitectura | `wiki/vistas/arquitectura.md` | Preguntas sobre estructura interna de BCs, componentes, C4 L2+L3 |

Para iniciar una sesión desde una vista específica:
```
Leé wiki/vistas/impacto.md. A partir de ahora respondé consultas
desde esa perspectiva usando el wiki como base de conocimiento.
```

---

## Operación: Ingest

Al ingestar una nueva fuente:

1. Leer la fuente completa.
2. Identificar entidades, conceptos, decisiones y relaciones nuevas o modificadas.
3. Crear o actualizar páginas afectadas (típicamente 5-15 páginas por fuente).
4. Actualizar `wiki/index.md` con nuevas páginas o cambios de resumen.
5. Agregar en `wiki/log.md`:
   ```
   ## [YYYY-MM-DD] ingest | <nombre-fuente>
   Páginas creadas: X | Páginas actualizadas: Y
   ```

Nunca modificar las fuentes en `docs/`, `src/`, `tests/`. Solo modificar `wiki/`.

---

## Operación: Query

Al responder una consulta:

1. Leer `wiki/index.md` para identificar páginas relevantes.
2. Identificar la vista más adecuada (ver tabla de vistas).
3. Leer las páginas pertinentes del wiki.
4. Sintetizar respuesta con citas usando wikilinks.
5. Si la respuesta es suficientemente valiosa, archivarla como nueva página en `wiki/`.

---

## Operación: Lint

Al ejecutar una auditoría de salud:

1. Leer `wiki/index.md` completo.
2. Verificar consistencia entre páginas (contradicciones, tecnologías desactualizadas).
3. Identificar gaps:
   - Requerimientos sin página de trazabilidad
   - BCs sin cobertura de tests documentada
   - Conceptos del dominio usados en código sin página propia
   - Páginas huérfanas (sin ningún enlace entrante)
   - Decisiones en ADRs sin reflejo en páginas de BC
4. Generar `wiki/salud/lint-NNN.md` con hallazgos y acciones sugeridas.

---

## Fuentes del proyecto

```
# Fuentes inmutables (contexto fundacional)
docs/dominio/
docs/iedd/
docs/contexto/ANALISIS-*.md

# Fuentes de decisiones (vigentes)
docs/adr/
docs/architecture/

# Fuentes de estado (evolucionan con el código)
docs/plans/
docs/reports/
docs/traceability/matrix.md
.cm/baselines/
quality/reports/

# Fuentes de código
src/
tests/

# Fuentes de investigación
docs/contexto/HITO-*.md
docs/contexto/PLAN-EXPERIMENTO.md
```

---

*Schema versión 1.0 — Mayo 2026*
*AtaraxiaDive LLM Wiki — branch wiki (orphan)*
