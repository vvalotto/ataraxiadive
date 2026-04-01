# PLAN-SP-ADJ-03 — Sprint de Ajuste Post-SP3

| Campo | Valor |
|-------|-------|
| **Sprint** | SP-ADJ-03 |
| **Contexto** | Ajuste documental y arquitectónico post-SP3 (BL-003) |
| **Fuente** | HITO-14 — Análisis crítico metodología y estructura |
| **Branch base** | `develop` (después de cerrar BL-003) |
| **Estado** | ⏳ Pendiente — ejecutar después de cerrar SP3 |

---

## Objetivo

Cerrar las debilidades de mayor impacto identificadas en HITO-14, más cualquier deuda
adicional que emerja durante INC-3.3/3.4/3.5.

El criterio para iniciar SP-ADJ-03 es que todos los incrementos de SP3 estén
mergeados en `develop` y BL-003 esté lista para taggear.

---

## Acciones base (HITO-14)

| ID | Debilidad | Acción | Tipo | Prioridad |
|----|-----------|--------|------|-----------|
| D-02 | Múltiples fuentes de verdad | Simplificar README; declarar jerarquía `baseline > CLAUDE.md > README` | Documental | Alta |
| D-03 | Documentación desalineada | Corregir README, `docker-compose.yml`, `docs/dominio/02-arquitectura_referencia.md`, `docs/dominio/04-estrategia_desarrollo.md` — eliminar refs a PostgreSQL | Documental | Alta |
| D-05 | Regla hexagonal no cumplida en `api/` | Composition root explícito en `app.py` — sacar inyección de repositorios concretos de los routers | Arquitectónico | Alta |
| D-06 | Imports cross-BC en `resultados/` | Auditar `resultados_competencia_adapter.py` y clasificar: aceptable / temporal / corregir | Arquitectónico | Media-Alta |

---

## Acciones adicionales (emergidas post-INC-3.3)

| ID | Descripción | Tipo | Prioridad | Spec |
|----|-------------|------|-----------|------|
| **US-ADJ-3.1** | Extraer `GrillaDeSalida` como entidad de dominio — Competencia WMC=64 → ~34 | Refactoring dominio | **Alta** — WMC en límite | `docs/specs/sp-adj-03/US-ADJ-3.1.md` |
| **US-ADJ-3.2** | Extraer `TarjetaAsignacion` como Value Object — DataClumps en Performance | Refactoring dominio | Media | `docs/specs/sp-adj-03/US-ADJ-3.2.md` |

### Ajuste de umbrales post-refactor (post US-ADJ-3.1)

```toml
# pyproject.toml — bajar después de implementar US-ADJ-3.1
max_wmc = 45              # bajado de 65 (GrillaDeSalida reduce Competencia a ~34)
max_god_object_lines = 420 # bajado de 540
```

### Secuencia recomendada

```
1. US-ADJ-3.1 + US-ADJ-3.2  ← mismo PR (ambas en competencia/domain/)
2. D-05 (composition root)   ← independiente
3. D-06 (audit cross-BC)     ← independiente
4. D-02 + D-03 (docs)        ← último
```

---

## Descartado por ahora

- **D-04** (`/implement-us` no ajustado al proyecto): el skill produce estructura correcta con adaptación manual mínima. Reescribir el perfil no es prioritario hasta tener más evidencia de fricción sistemática.
- **D-01/D-07/D-08/D-09/D-10**: observaciones válidas, impacto inmediato bajo. Revisar en retrospectiva SP3.

---

*Iniciado: 2026-03-31 — basado en HITO-14*
*Actualizado: 2026-04-01 — US-ADJ-3.1/3.2 agregadas post-análisis WMC Competencia (INC-3.3)*
