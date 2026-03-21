# Fase 0: Validación de Contexto

**Objetivo:** Verificar que el entorno del proyecto tiene todo lo necesario para implementar la Historia de Usuario.

**Duración estimada:** 5-10 minutos

---

## 0. Leer contexto del proyecto (OBLIGATORIO — hacer antes de cualquier otra cosa)

**Leer el documento `docs/plans/ATARAXIADIVE-CONTEXT.md` antes de continuar.**

Este documento define:
- La arquitectura real del proyecto (hexagonal DDD BC-first, no layered)
- Los paths canónicos de todos los artefactos
- Los tipos de componente DDD a generar por capa
- Los BCs y sus características (Event Sourcing vs CRUD)
- Las convenciones de código y quality gates

> **Sin leer este documento, las rutas, patrones y convenciones de las fases siguientes serán incorrectas.**

---

## Tracking

**Al inicio de la fase — ejecutar ANTES de cualquier otro trabajo:**
```bash
uv run python .claude/tracking/tracker_cli.py init {US_ID} "{US_TITLE}" {US_POINTS} {PRODUCT}
uv run python .claude/tracking/tracker_cli.py start-phase 0 "Validación de Contexto"
```

> **Obligatorio:** sin este paso, todo el tracking de la sesión será post-facto.
> El `tracker_cli.py` persiste estado en `.claude/tracking/{US_ID}-tracking.json`
> al finalizar cada llamada — no requiere objeto en memoria entre fases.

---

## 1. Verificar que existe la historia de usuario

**Buscar en la ubicación canónica de AtaraxiaDive:**

> **Ruta canónica:** `docs/plans/US-X.Y.Z.md`
> (donde X.Y.Z = identificador de la US, ej: `docs/plans/US-1.1.1.md`)

**Extraer de la US:**
- Título de la historia
- Criterios de aceptación
- Puntos de estimación
- Prioridad

**Si no se encuentra:**
- Preguntar al usuario por la ubicación
- O permitir ingresar manualmente los datos de la US

---

## 2. Validar arquitectura de referencia

**Verificar documentación arquitectónica de AtaraxiaDive:**

Los siguientes artefactos deben existir (ya fueron creados en Fase 0 del proyecto):
- `docs/adr/ADR-005-bounded-contexts-ddd-estrategico.md` — decisión de BCs
- `docs/adr/ADR-006-estructura-bc-first.md` — decisión de estructura BC-first
- `docs/design/architecture.md` — arquitectura C4
- `docs/design/domain-model.md` — modelo de dominio

**Verificar que el BC de la US existe en `src/`:**

Identificar el BC al que pertenece la US (de `docs/plans/ATARAXIADIVE-CONTEXT.md` §5) y confirmar que su estructura existe:
- `src/{bc}/domain/`
- `src/{bc}/application/`
- `src/{bc}/infrastructure/`
- `src/{bc}/api/`

**Checkpoint:**
- ✅ Arquitectura documentada encontrada
- ✅ Patrones requeridos confirmados en el proyecto
- ⚠️ Si falta documentación, advertir al usuario pero continuar

---

## 3. Verificar estándares de calidad

**Validar que existen:**

1. **CLAUDE.md** con quality gates definidos:
   - Pylint score mínimo
   - Complejidad ciclomática máxima
   - Cobertura de tests mínima

2. **Estructura de tests:**
   - Directorio `tests/` existe
   - `conftest.py` configurado (si usa pytest)
   - Framework de testing instalado (verificar según `{TEST_FRAMEWORK}`)

3. **Herramientas de calidad configuradas** (ver `pyproject.toml`):**
   - `[tool.codeguard]` — CodeGuard configurado con paths de BCs
   - `[tool.designreviewer]` — check_hexagonal = true
   - `[tool.coverage.run]` — fuentes apuntando a `src/`

**Si faltan herramientas:**
- Advertir al usuario
- Ofrecer crear configuración básica
- O continuar sin quality gates (no recomendado)

---

## Output de la Fase

**Template de resumen:**

```markdown
## ✅ Contexto Validado

**Historia de Usuario:** US-XXX - {título}
**Producto:** {PRODUCT}
**Puntos:** X
**Prioridad:** Alta/Media/Baja

**Arquitectura:**
- Patrón: {ARCHITECTURE_PATTERN}
- Documentación: {ARCHITECTURE_DOC} encontrado
- Patrones verificados: {PATTERNS}

**Quality Gates:**
- ✅ CLAUDE.md configurado
- ✅ Tests configurados ({TEST_FRAMEWORK})
- ✅ Herramientas de calidad disponibles

**Listo para proceder con Fase 1: Generación de Escenarios BDD**
```

---

## Tracking

**Al finalizar la fase:**
```bash
uv run python .claude/tracking/tracker_cli.py end-phase 0
```

---

**Siguiente fase:** [Fase 1: Generación de Escenarios BDD](./phase-1-bdd.md)
