# Workflow de Desarrollo — AtaraxiaDive

**Versión:** 1.5
**Fecha:** 2026-03-29
**Alcance:** Convenciones de branching, PRs, quality gates y gestión administrativa para SP1 en adelante

---

## 1. Jerarquía de Trabajo

```
SP (Subproyecto)          → Baseline (BL-NNN) + tag git (v0.N.0) + Milestone GitHub
  └── Incremento (X.Y)    → PR a develop + DoD de integración verificable
        └── US-IEDD (X.Y.Z) → GitHub Issue + docs/specs/spX/US-X.Y.Z.md + branch feature/
```

No existe un nivel "iteración" — el Incremento cubre esa función.

---

## 2. Gestión Administrativa (GitHub)

### División de responsabilidades

| Artefacto | Dónde vive | Propósito |
|-----------|-----------|-----------|
| **GitHub Issue** | GitHub Issues | Fuente de verdad del estado — qué hay que hacer, criterios de aceptación, seguimiento |
| **`docs/specs/spX/US-X.Y.Z.md`** | Repositorio | Especificación US-IEDD — precondición, postcondición, invariantes, input de `/implement-us` |

### Estructura en GitHub

- **Milestones** = uno por Subproyecto (`SP1 — La Performance`, `SP2 — La Competencia`, etc.)
- **Labels** = `us-iedd`, `incremento-1.1`, `incremento-1.2`, `blocked`, `in-progress`, `done`
- **Sin Project board** — los Milestones + Labels proveen seguimiento suficiente para desarrollo en solitario

### Template de Issue (US-IEDD)

```markdown
## Descripción
Como <rol>, quiero <acción> para <valor>.

## Criterios de Aceptación
- [ ] ...

## Precondición
...

## Postcondición
...

## Invariantes
- INV-1: ...

## Referencias
- Incremento: X.Y
- Bounded Context: ...
- docs/specs/spX/US-X.Y.Z.md
```

---

## 3. Ciclo de Elaboración de US por SP

```
1. Claude elabora el archivo de US candidatas: docs/plans/spN/SP-N-candidatas.md
   → Lista todas las US del SP con descripción, criterios y estimación
2. Victor revisa y aprueba (con ajustes si corresponde)
3. Por cada US aprobada:
   a. Crear GitHub Issue con template US-IEDD → asignar Milestone + Labels
   b. Crear docs/specs/spN/US-X.Y.Z.md con la especificación US-IEDD completa
4. Las US quedan en estado "backlog" hasta iniciar su Incremento
```

---

## 4. Branching

```
main          ← baselines etiquetadas (v0.1.0, v0.2.0...)
  └── develop ← integración continua — recibe PRs individuales de cada US
        ├── feature/US-X.Y.Z-descripcion-corta  ← una branch por US-IEDD
        ├── feature/inc-X.Y-descripcion-corta   ← incrementos técnicos sin US
        └── fix/descripcion-corta               ← correcciones
```

### Nomenclatura de branches

| Tipo | Patrón | Ejemplo |
|------|--------|---------|
| US-IEDD | `feature/US-X.Y.Z-descripcion-corta` | `feature/US-1.2.1-registrar-ap` |
| Incremento técnico (sin US) | `feature/inc-X.Y-descripcion-corta` | `feature/inc-1.1-fundacion-tecnica` |
| Corrección | `fix/descripcion-corta` | `fix/invariante-ap-nulo` |

**Reglas:**
- Cada US-IEDD tiene su propia branch — PR individual directo a `develop`.
- Los incrementos técnicos (sin US-IEDD, como Inc 1.1) usan `feature/inc-X.Y-*` con commits por tarea.
- `develop` se mergea a `main` solo al cerrar un Subproyecto (Baseline).
- Descripción en kebab-case, máximo 4 palabras, en español.

---

## 5. Ciclo por US-IEDD

### Orden de arranque (no negociable)

```
1. git checkout -b feature/US-X.Y.Z-descripcion desde develop
2. Verificar con git branch que el branch activo es el correcto
3. Inicializar TimeTracker: tracker init US-X.Y.Z → start_phase(0)
   → El archivo .claude/tracking/US-X.Y.Z-tracking.json debe existir
     ANTES de crear cualquier artefacto
4. Recién entonces arrancar Fase 0
```

> **Antes de iniciar:** verificar que no haya trackers activos de USs anteriores sin cerrar.
> `_find_active_us_id()` retorna el primero con `completed_at == null` — si hay trackers
> viejos abiertos, las fases se aplican al tracker equivocado.

> **Bug conocido:** `tracker_cli.py` usa `glob("US-*-tracking.json")` — IDs con prefijo
> distinto a `US-` (ej: `INC-2.0`) no son encontrados por las operaciones de fase.
> Mientras no esté corregido, usar prefijo `US-` para todos los IDs de tracking.

> **Política operativa de tracking:** todas las operaciones sobre `tracker_cli.py`
> (`init`, `start-phase`, `end-phase`, `start-task`, `end-task`, `end`) deben
> ejecutarse **estrictamente en secuencia, una por vez**. No correr llamadas en
> paralelo ni agrupar escrituras concurrentes sobre el mismo
> `.claude/tracking/US-*.json`: el tracker no garantiza concurrencia y puede
> corromper el JSON persistido.

### Ejecución de fases

```
5. Ejecutar /implement-us US-X.Y.Z  (10 fases, input: docs/specs/spX/US-X.Y.Z.md)
   → Cada fase tiene un artefacto físico de output — crearlo con Write, no solo mostrarlo en el chat
   → Fase 2 (plan): auto_approved=False — esperar aprobación explícita antes de continuar
   → Fase 8 (documentación): auto_approved=False — ídem
   → Fases 8 y 9 deben ejecutarse ANTES del commit final, no después
   → El skill no está completo hasta que docs/reports/{US_ID}-report.md exista en disco
   → El tracking se opera automáticamente, pero siempre con llamadas secuenciales
6. [AUTO] CodeGuard corre en cada commit (pre-commit hook, ~5s, solo advierte)
7. Commits atómicos con referencia: feat(domain): ... [US-X.Y.Z]
8. Abrir PR hacia develop con /pr → DesignReviewer corre en pre-push (bloquea si CRITICAL)
   → Usar siempre gh pr create --base develop (default de gh es main)
9. Merge del PR — Issue se cierra automáticamente
```

---

## 6. Ciclo por Incremento

Un Incremento cierra cuando todas sus US-IEDD están mergeadas a `develop`
y el DoD de integración es verificable de punta a punta.

### Preparación al inicio del incremento

Antes de la primera US, estimar el crecimiento total del aggregate principal y ajustar
umbrales en `pyproject.toml` para el total del incremento completo (no US por US):

```toml
# Ajustar según US del incremento — ejemplo Inc 1.2 con 6 US sobre Performance:
max_cbo = 17          # +1 por cada evento importado en el aggregate
max_wmc = 36          # +4-6 por cada método con 2 invariantes
max_god_object_methods = N
max_god_object_lines = N
```

> **Regla práctica:** cada método de dominio con 2 invariantes ≈ 4-6 WMC.
> Cada nuevo evento importado en el aggregate = exactamente 1 CBO.
> Ajustar con margen — las estimaciones optimistas generan bloqueos de push a mitad del incremento.

### Cierre del incremento

```
1. Todas las US del Incremento mergeadas a develop (PR individual por US)
2. Verificar DoD de integración (test end-to-end observable)
3. [MANUAL] Correr DesignReviewer sobre el estado consolidado del incremento:
   designreviewer src/ --config pyproject.toml
   → Complementa el DesignReviewer automático (pre-push por US) — aquí se verifica
     que la interacción entre todas las US del incremento no introdujo violations.
   → Si hay CRITICAL: abrir fix/ branch, corregir, PR a develop
4. Registrar en BL-00N activa:
   → Agregar CIs nuevos a la tabla de inventario
   → Actualizar métricas del incremento
   → Registrar decisiones técnicas relevantes
5. Documentar aprendizajes experimentales en HITO-N si hay observaciones relevantes
6. Mini-retrospectiva: ¿qué funcionó? ¿qué ajustar en el próximo?
7. Cerrar Issue del incremento en GitHub con comentario de DoD verificado
```

**Para incrementos técnicos sin US (ej: Inc 1.1):**
```
1. Branch feature/inc-X.Y-descripcion desde develop
2. Commits por tarea (scaffold, migrations, health-check, etc.)
3. [AUTO] CodeGuard en cada commit
4. Abrir PR con /pr → DesignReviewer pre-push
5. Merge → verificar DoD
6. Registrar en BL-00N + HITO-N si hay aprendizajes
```

---

## 7. Ciclo por Subproyecto (Baseline)

```
1. Todos los Incrementos del SP cerrados en develop — Milestone al 100%
2. Correr ArchitectAnalyst manualmente:
   architectanalyst src/ --sprint-id BL-NNN --format json \
     > quality/reports/architectanalyst/BL-NNN-arquitectura.json
   → Leer y analizar el reporte antes de continuar
   → Copiar también a .cm/baselines/BL-NNN-arquitectura.json
3. Registrar métricas en .cm/baselines/BL-NNN.md
4. UAT post-SP — flujo DoD de punta a punta:
   a. Diseñar pruebas en quality/reports/uat/SPN/design.md
   b. Implementar seed + script en tests/uat/spN/
      → Patrón HTTP completo si los comandos están expuestos como endpoints POST
      → Patrón híbrido (seed Application layer + HTTP) si algún comando no tiene endpoint
   c. Ejecutar: Capa 1 pytest (flujo de dominio) + Capa 2 HTTP (endpoints observables)
   d. Guardar evidencia en quality/reports/uat/SPN/
      (capa1-pytest.txt · capa2-http.json · report.md)
   e. UAT aprobado → PR mergeado a develop antes de continuar
5. Merge develop → main
6. Tag: git tag vN.0.0  — cerrar Milestone en GitHub
7. Retrospectiva documentada en BL-NNN.md (alimenta el libro y el paper)
```

**ArchitectAnalyst es siempre manual** — su valor está en la lectura consciente
del reporte antes de cerrar el Baseline, no en la automatización.

> **SP-ADJ:** evaluar al cierre de cada SP si hay deuda acumulada (técnica o documental)
> que justifique un sprint de ajuste antes de arrancar el siguiente SP.
> Ver patrón establecido en SP-ADJ-01 y SP-ADJ-02 post-SP2.

---

## 8. Quality Gates por Nivel

| Nivel | Herramienta | Cuándo | Modo | Acción |
|-------|-------------|--------|------|--------|
| Commit | CodeGuard | Pre-commit (automático) | `codeguard src/` | Advierte, no bloquea |
| PR a develop | DesignReviewer | Pre-push (automático) | `designreviewer src/ --config pyproject.toml` | Bloquea si CRITICAL |
| Cierre de Incremento | DesignReviewer | Manual, después del último merge | `designreviewer src/ --config pyproject.toml` | Confirmar cero CRITICAL |
| UAT post-SP | Tests funcionales | Manual, antes de merge a main | `tests/uat/spN/run_uat.sh` | Capa 1 + Capa 2 aprobadas |
| Cierre de Subproyecto | ArchitectAnalyst | Manual, antes de merge a main | `architectanalyst src/ --sprint-id BL-NNN --format json` | Informa tendencias |

> **Importante:** siempre pasar `--config pyproject.toml` al correr DesignReviewer manualmente.
> Sin él se usan defaults del sistema (CBO=5, WMC=20) que no reflejan la config del proyecto
> y muestran resultados inflados.

### Flujo de bloqueo por DesignReviewer

```
push → pre-push hook → designreviewer src/ --config pyproject.toml
  ├── OK: push procede
  └── CRITICAL: push bloqueado
        → fix/descripcion branch
        → corregir violación
        → PR a develop
        → push ok
```

---

## 9. Relación con /implement-us

El skill `/implement-us US-X.Y.Z` lee `docs/specs/spX/US-X.Y.Z.md` como input y
ejecuta las 10 fases dentro de la branch `feature/US-X.Y.Z-descripcion`.
Al terminar, se abre PR con `/pr` y se mergea directo a `develop`.

```
# Ejemplo Inc 1.2 — 6 US individuales

feature/US-1.2.1-registrar-ap     → /implement-us → /pr → merge develop
feature/US-1.2.2-llamar-atleta    → /implement-us → /pr → merge develop
feature/US-1.2.3-registrar-resultado → /implement-us → /pr → merge develop
...
(última US mergeada) → designreviewer src/ manual → verificar DoD 1.2 → mini-retro
```

---

*v1.5 — 2026-03-29. §5: orden de arranque, artefactos por fase, aprobaciones, bug tracker prefijo non-US-.*
*§6: ajuste de umbrales CBO/WMC al inicio del incremento. §7: UAT post-SP como paso obligatorio.*
*§8: --config pyproject.toml obligatorio en ejecución manual. SP-ADJ como patrón establecido.*
*v1.4 — 2026-03-22. Reestructuración docs/: specs/ para US-IEDD (Capa 3 IEDD), plans/ con subdirs por SP.*
*v1.3 — 2026-03-21. Ciclo por incremento: agregar registro en BL activa + HITO experimental.*
*Complementa `docs/dominio/04-estrategia_desarrollo.md`.*
