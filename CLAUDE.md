# CLAUDE.md — AtaraxiaDive

> Estado documental: vigente  
> Fuente de verdad para: contexto operativo, decisiones y convenciones de trabajo  
> Última actualización: 2026-05-02

**Memoria operativa del proyecto.** Leer antes de trabajar.

> **Navegación:** [Mapa documental](docs/inventario/DOCUMENTATION-MAP.md) · [Jerarquía de autoridad](docs/inventario/FUENTES-DE-VERDAD-DOCUMENTAL.md) · [Experimento IEDD](docs/contexto/PLAN-EXPERIMENTO.md)

---

## 1. El Producto

**AtaraxiaDive** — plataforma web para gestión de torneos de apnea (freediving).

- **Stack:** Python + FastAPI · React 19 + Vite 6 + TypeScript + Tailwind v4 + PWA · SQLite (un archivo por BC — ADR-007)
- **Arquitectura:** Hexagonal + Event Sourcing (BCs Competencia y Notificaciones)
- **Metodología:** IEDD — cada US tiene precondición, postcondición e invariantes formales
- **Workflow:** `docs/plans/WORKFLOW-DESARROLLO.md` — fuente autoritativa del ciclo US → Incremento → SP

---

## 2. Arquitectura Hexagonal (regla absoluta)

```
<bc>/domain/         → no importa nada fuera de su propio domain/
<bc>/application/    → importa <bc>/domain/, nunca infrastructure/
<bc>/infrastructure/ → implementa puertos definidos en <bc>/domain/ports/
<bc>/api/            → importa <bc>/application/, nunca domain/ directamente
```

- Única excepción: cualquier capa puede importar `shared/domain/`
- Comunicación entre BCs: exclusivamente por puertos — nunca imports directos
- DesignReviewer detecta violaciones automáticamente en cada push

---

## 3. Bounded Contexts

| BC | Tipo | Impl. | Contenido principal |
|---|---|:---:|---|
| **Competencia** | Core Domain | ES | AP, grilla, ejecución, tarjetas — lógica no trivial del deporte |
| **Torneo** | Supporting | CRUD | Ciclo de vida del torneo, disciplinas, sede |
| **Registro** | Supporting | CRUD | Atleta, inscripción, cancelaciones |
| **Resultados** | Supporting | CRUD | Rankings por disciplina/género, Overall, publicación incremental |
| **Identidad** | Generic | CRUD | Usuarios, roles (organizador/juez/atleta), JWT |
| **Notificaciones** | Generic | ES | Idempotencia exactly-once, Email/Push |

> ES = Event Sourcing · CRUD = persistencia relacional estándar
> Context Map: `docs/design/context-map.md` · Decisión formal: ADR-005

---

## 4. Lenguaje Ubicuo

| Término | Significado |
|---------|-------------|
| AP | Announced Performance — marca declarada antes de competir |
| RP | Realized Performance — marca efectivamente lograda |
| OT | Official Top — momento de inicio de la performance |
| DNS | Did Not Start — atleta no se presentó al OT |
| Tarjeta blanca | Performance válida sin infracciones |
| Tarjeta Blanca con Penalizaciones | Performance válida con infracciones técnicas; RP final = RP medido − Σ deducciones (N × 3m) |
| Tarjeta amarilla | Estado de revisión pendiente → se cierra como Blanca, Blanca con Penalizaciones o Roja |
| Tarjeta roja | Descalificación — requiere `MotivoDQ` obligatorio |
| MotivoDQ | BKO_SUPERFICIE · BKO_SUBACUATICO · NO_PROTOCOLO · INFRACCION_TECNICA · NO_INICIO_VENTANA · SALIDA_FALSO |
| Black-out | Pérdida de conciencia → tarjeta roja automática |
| Variante SPE | SPE_2X50 · SPE_4X50 · SPE_8X50 · SPE_16X50 — grilla y ranking independientes; orden AP descendente |
| US-IEDD | User Story con precondición, postcondición e invariantes formales |

---

## 5. Jerarquía de Trabajo y Estado

```
Subproyecto (SP)  → genera Baseline (BL-NNN) + tag git
  └── Incremento  → DoD de integración verificable
        └── US-IEDD → /implement-us → 10 fases

SP-ADJ  → ajuste técnico o documental antes de cerrar la baseline
```

| SP | Nombre | Tag | Estado |
|----|--------|-----|--------|
| SP1 | La Performance | `v0.2.0` | ✅ Cerrado 2026-03-24 |
| SP2 | La Competencia | `v0.3.0` | ✅ Cerrado 2026-03-28 |
| SP3 | El Torneo | `v0.4.0` | ✅ Cerrado 2026-04-04 |
| SP4 | La Plataforma | `v0.5.0` | ✅ Cerrado 2026-04-18 |
| SP5 | La Puesta en Marcha | `v0.6.0` | ✅ Cerrado 2026-05-01 |
| SP6 | Validación, Ajustes y Despliegue | `v1.0.0` | ✅ Cerrado 2026-05-16 |
| SP7 | Despliegue y Documentación | `v1.0.2` | ✅ Cerrado 2026-05-30 |

**SP5 cerrado:** INC-5.1..5.7 + SP-ADJ-07/08/09 · portal organizador + portal atleta + FAAS + rankings · ArchitectAnalyst BL-005: `competencia` D=0.46↓ · `should_block=false`
**SP-ADJ-11 cerrado:** 10/10 US ✅ · PRs #184–#193 · modelo multi-rol completo (Identidad + Registro + Frontend) · DesignReviewer 0 CRITICAL · ADR-020 implementado.
**SP6 cerrado:** INC-6.1..6.6 + SP-ADJ-10/11 · UAT 10/10 flows · BL-006 ✅ · tag `v1.0.0` · despliegue diferido a SP7.
**SP7 cerrado:** INC-7.1 Despliegue en Fly.io ✅ · INC-7.2 Manual de usuario ✅ · PR #212 · BL-007 · tag `v1.0.2`.
**SP-ADJ-12 cerrado:** 6/6 US ✅ + 3 fixes post-revisión · PRs #205–#210 · issues #198–#204 · DesignReviewer 0 CRITICAL · 1049 tests · BL-007 · tag `v1.0.2`.
**SP-ADJ-13 en curso:** ejecución completa en producción · capturas faltantes del manual (roles, podios) · fixes que emerjan.

---

## 6. Convenciones de Código

### Python
- **Formato:** Black (line-length 100) + isort (perfil Black)
- **Linting:** Ruff + Pylint ≥ 8.0
- **Tipos:** mypy modo estricto — todos los métodos públicos tipados
- **Cobertura mínima:** 90% en `domain/` y `application/`

### Commits (Conventional Commits)
```
feat(domain): agregar aggregate Performance [US-1.2.1]
fix(api): corregir endpoint ranking provisional
test(domain): tests unitarios Performance.asignar_tarjeta
docs(adr): ADR-002 decisión FastAPI
chore(cm): registrar BL-001 cierre SP1

# Types: feat | fix | refactor | test | docs | chore
# Scopes: domain | application | infra | api | frontend | cm | tests | design
```

### Branching
```
main     ← baselines etiquetadas
develop  ← integración continua — recibe PRs por US
  ├── feature/US-X.Y.Z-descripcion
  ├── feature/inc-X.Y-descripcion
  └── fix/descripcion
```

---

## 7. Quality Gates

| Momento | Herramienta | Modo |
|---------|-------------|------|
| Cada commit | CodeGuard | Automático — advierte, no bloquea |
| Cada push (PR) | DesignReviewer | Automático — bloquea si CRITICAL |
| Cierre de Incremento | DesignReviewer | Manual — confirmar 0 CRITICAL |
| UAT post-SP | Tests funcionales | Manual |
| Cierre de SP | ArchitectAnalyst | Manual — informa tendencias |

---

## 8. Comandos

```bash
# Setup (una vez al clonar)
git config core.hooksPath .githooks

# Desarrollo
uv run uvicorn src.app:app --reload --env-file .env
cd frontend && npm run dev

# Tests
pytest tests/unit/
pytest tests/integration/
pytest tests/features/

# Calidad
codeguard src/
designreviewer src/ --config pyproject.toml
architectanalyst src/ --sprint-id BL-NNN --format json

# Formato
black src/ tests/ && isort src/ tests/
```

---

## 9. LLM Wiki

El branch `wiki` contiene un wiki mantenido por LLM — **no código, no documentación operativa**. Es una capa de conocimiento sintetizado sobre el proyecto.

**Schema y reglas del wiki:** `WIKI.md` (en el root del branch `wiki`)  
**Plan de implementación:** `LLM-WIKI-DIAGNOSTICO-Y-PLAN.md` (en el root del branch `wiki`)

### Jerarquía de fuentes (para ingest)

El LLM ingestor debe priorizar fuentes en este orden. Ante contradicción, prevalece la fuente de mayor jerarquía:

| Prioridad | Fuente | Descripción |
|-----------|--------|-------------|
| 1 — Más alta | `.cm/baselines/BL-*.md` · `docs/reports/` | Verdad de cierre: lo que fue verificado y etiquetado |
| 2 | `docs/adr/ADR-*.md` | Decisiones arquitectónicas ratificadas |
| 3 | `CLAUDE.md` (este archivo) | Contexto operativo vigente |
| 4 | `README.md` | Descripción pública del proyecto |
| 5 | `docs/architecture/` · `docs/design/` | Documentación técnica de soporte |
| 6 | `docs/plans/` · `docs/traceability/` | Planificación e historias de usuario |
| 7 — Más baja | `docs/dominio/` | Elicitación histórica — puede estar desactualizada |

### Operaciones del wiki

```
/wiki-ingest <fuente>   → procesar fuente y actualizar páginas del wiki
/wiki-query  <pregunta> → navegar el wiki y responder desde conocimiento sintetizado
/wiki-lint              → auditar coherencia, detectar contradicciones, generar salud/lint-NNN.md
```

> El LLM wiki es un **experto que propone, no implementa**. Las páginas del wiki son síntesis y análisis — no sustituyen a las fuentes origen.

---

## 10. Gestión de Sesión

- **Al iniciar:** si el hook muestra flag pendiente → `/resume` antes de cualquier acción
- **Durante:** `/checkpoint` al completar tareas significativas, tomar decisiones, antes de operaciones riesgosas, y cuando el usuario da señales de cierre
- **Al cerrar:** el hook SessionEnd captura commits automáticamente

```
memory/
├── session-metadata.json   ← timestamp, branch, razón de salida
├── session-current.md      ← estado en curso (checkpoints)
├── session-history.md      ← historial de sesiones
└── session-needs-summary.flag
```

**Dónde guardar conocimiento:**
- *¿Vale para el paper/libro/futuros proyectos?* → HITO o BL en `docs/contexto/`
- *¿Claude lo necesita para operar en este proyecto?* → `memory/`

---

*Última actualización: 2026-05-30 — SP6 ✅ v1.0.0 · SP7 ✅ v1.0.2 · SP-ADJ-12 ✅ cerrado · INC-7.2 ✅ manual completo*

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
