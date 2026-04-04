# PLAN-SP-ADJ-05 — Sprint de Ajuste Documental y Metodológico post-SP3

| Campo | Valor |
|-------|-------|
| **Sprint** | SP-ADJ-05 |
| **Contexto** | Ajuste documental + metodológico post-BL-003 |
| **Fuentes** | HITO-14 (D-01, D-02, D-03, D-07, D-08, D-09) · ArchitectAnalyst BL-003 |
| **Branch base** | `develop` (después de cerrar BL-003 / tag v0.4.0) |
| **Estado** | ⏳ Pendiente — iniciar después de merge develop→main |

---

## Contexto

SP-ADJ-03 y SP-ADJ-04 resolvieron la deuda de código de SP3 (SOLID, refactors,
correcciones de dominio real). SP-ADJ-05 cierra los ítems **documentales y metodológicos**
de HITO-14 que fueron descartados intencionalmente de SP-ADJ-03 para no mezclar scope.

El momento es el correcto: HITO-14 D-01 dice explícitamente *"ejecutar poda metodológica
al cierre de SP3"*. BL-003 acaba de cerrarse.

---

## Hallazgos ArchitectAnalyst BL-003 — Registro e Interpretación

ArchitectAnalyst identificó 4 CRITICAL en `DistanceAnalyzer` (should_block=false).
Son todos **Zone of Pain**: módulos estables y concretos, alejados de la Main Sequence.

| Módulo | D | Tendencia | Interpretación |
|--------|---|-----------|----------------|
| `identidad` | 0.87 | ↓ mejorando | BC CRUD puro: alta estabilidad por diseño. Sin abstracciones pendientes en SP4. |
| `shared` | 0.61 | ↓ mejorando | Módulo cross-BC: concentra VOs y tipos comunes. Estabilidad es deseable. |
| `competencia` | 0.62 | ↑ degradando | **A monitorear.** Core Domain: la tendencia ascendente puede indicar que está absorbiendo demasiada concreción. Revisar en BL-004. |
| `registro` | 0.56 | — estable | BC CRUD estable: sin cambios previstos en SP4. |

**Acción para SP4:** si `competencia` supera D=0.70 en BL-004, evaluar extracción de
abstracciones (nuevos puertos o value objects que reduzcan la concreción del aggregate).

---

## Items de HITO-14 planificados

### SP-ADJ-5.1 — Poda metodológica: clasificar artefactos (D-01)
**Prioridad: Alta** — el momento es ahora (HITO-14 lo prescribe al cierre de SP3)

**Acción:** Crear `docs/contexto/ARTEFACTOS-WORKFLOW.md` con una tabla de tres columnas:
- `obligatorio`: sin él el workflow no funciona
- `opcional`: aporta valor pero se puede omitir sin consecuencias sistémicas
- `derivado`: se genera automáticamente, no requiere mantenimiento manual

Fuente: inventariar artefactos actuales por US, por Incremento y por SP.
Resultado esperado: identificar qué se puede eliminar o automatizar para bajar el overhead.

---

### SP-ADJ-5.2 — Consistencia documental operativa residual (D-02 + D-03)
**Prioridad: Media-Alta**

SP-ADJ-02-doc atacó la mayor parte. Verificar qué sobrevive:
- `README.md`: ¿todavía menciona PostgreSQL o instrucciones pre-ADR?
- `docker-compose.yml`: ¿sigue configurado para PostgreSQL?
- `docs/dominio/02-arquitectura_referencia.md`: ¿alineado con ADR-007 (SQLite por BC)?
- `docs/dominio/04-estrategia_desarrollo.md`: ¿estrategia de BD alineada?

Si quedan referencias pre-ADR: corregir o archivar con nota explícita de vigencia.

---

### SP-ADJ-5.3 — Marcar madurez de BCs en documentación (D-07)
**Prioridad: Media**

`Notificaciones` aparece en `CLAUDE.md §7` y `context-map.md` con la misma madurez
implícita que `Competencia` o `Torneo`, pero en código es casi solo scaffolding.

**Acciones:**
- En `CLAUDE.md §7`: agregar columna `Madurez` a la tabla de BCs con valores
  `operativo` / `parcial` / `modelado`.
- En `docs/design/context-map.md`: agregar nota de estado de implementación por BC.

---

### SP-ADJ-5.4 — Marcar vigencia de documentos históricos (D-09)
**Prioridad: Media**

Documentos tempranos siguen redactados como si el stack no estuviera fijado.
No se reescribe la historia, se agrega una nota editorial al inicio del doc.

**Documentos a marcar:**
- `docs/contexto/PLAN-EXPERIMENTO.md` — decisiones de BD/stack ya cerradas
- `docs/dominio/02-arquitectura_referencia.md` — si no se actualiza en SP-ADJ-5.2

Convención a definir: `<!-- ESTADO: histórico | activo | reemplazado por [doc] -->`.

---

### SP-ADJ-5.5 — Corregir deuda en tooling `.claude/` (D-08)
**Prioridad: Baja**

Evidencia: `.claude/tracking/README.md` apunta a docs inexistentes.

**Acciones:**
- Auditar `.claude/tracking/` y corregir o eliminar referencias rotas.
- Decidir si `tracking/` sigue siendo parte del workflow o puede archivarse.

---

## Fuera de scope → candidato SP4 temprano

### D-04 — Adaptar `/implement-us` a la arquitectura real de AtaraxiaDive

El skill actual trabaja con un perfil `fastapi-rest` orientado a layered architecture.
AtaraxiaDive usa BC-first + hexagonal + DDD. La fricción es observable y sistemática.

**Por qué no en SP-ADJ-05:**
- Es una iniciativa de tooling, no documental
- Requiere análisis de `.claude/skills/implement-us/` + creación de perfil nuevo
- El impacto se siente en SP4 (primeros BCs nuevos), que es el momento natural para ajustarlo

**Acción para SP4:** iniciar con una US de adaptación del skill antes de la primera US de implementación.

---

## Priorización

| US | Descripción | Prioridad | Fuente |
|----|-------------|-----------|--------|
| SP-ADJ-5.1 | Poda metodológica (artefactos obligatorios/opcionales/derivados) | Alta | HITO-14 D-01 |
| SP-ADJ-5.2 | Consistencia documental residual (README, docker-compose, docs dominio) | Media-Alta | HITO-14 D-02/D-03 |
| SP-ADJ-5.3 | Marcar madurez de BCs en CLAUDE.md y context-map | Media | HITO-14 D-07 |
| SP-ADJ-5.4 | Marcar vigencia histórica en docs fundacionales | Media | HITO-14 D-09 |
| SP-ADJ-5.5 | Deuda tooling `.claude/tracking/` | Baja | HITO-14 D-08 |

---

## Criterio de inicio

Todos los incrementos de SP3 mergeados en `main` (BL-003 cerrada, tag `v0.4.0`).

---

*Creado: 2026-04-04 — al cerrar UAT SP3 + DesignReviewer + ArchitectAnalyst BL-003*
