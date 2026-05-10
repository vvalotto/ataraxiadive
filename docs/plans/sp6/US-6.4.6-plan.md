# Plan de Implementación — US-6.4.6

**US:** US-6.4.6 — Decisión ARCH-03 + SRP RankingCompetencia + monitoreo identidad/shared  
**Fase:** 2 — Plan  
**Generado:** 2026-05-10

---

## Diagnósticos previos a la implementación

| Hallazgo | Diagnóstico | Acción |
|----------|-------------|--------|
| ARCH-03 | `ResultadosCompetenciaAdapter` no tiene imports de `competencia.*` — ACL legítimo | Documentar decisión en BL-006 |
| DR-01 | `RankingCompetencia` LCOM=2 es inherente al patrón ES (comando + reconstitución) — falso positivo | Documentar en BL-006, NO cambiar código |
| AA-02 | `identidad` D=0.67, tendencia ↓ desde 0.87 — mejorando, sin intervención en SP6 | Documentar en BL-006 |
| AA-04 | `shared` D=0.63, estable — impacto sistémico alto para refactorizar en v1.0 | Documentar en BL-006 |

## Tareas

### T1: Crear BL-006 (draft SP6)
- Crear `.cm/baselines/BL-006.md` con estructura igual a BL-005
- Registrar INC-6.1..6.4 cerrados con PRs y quality gates
- Registrar decisiones ARCH-03, DR-01, AA-02, AA-04
- **Archivo:** `.cm/baselines/BL-006.md`

### T2: Actualizar matrix.md §32 INC-6.4
- Marcar US-6.4.1, US-6.4.2 como ✅ Done (estaban como Pending pero fueron mergeadas)
- Marcar US-6.4.6 como ✅ Done al cerrar
- Actualizar estado INC-6.4 → ✅ Cerrado
- **Archivo:** `docs/traceability/matrix.md`

### T3: Ejecutar DesignReviewer y registrar resultado en BL-006
- `designreviewer src/ --config pyproject.toml`
- Confirmar 0 CRITICAL, `should_block=false`
- Guardar reporte en `quality/reports/designreviewer/INC-6.4-report.txt`

## Estimaciones

| Tarea | Est. |
|-------|------|
| T1: Crear BL-006 | 20 min |
| T2: Actualizar matrix.md | 10 min |
| T3: DesignReviewer + registro | 10 min |
| **Total** | **40 min** |

## Artefactos de salida

- `.cm/baselines/BL-006.md` (nuevo)
- `docs/traceability/matrix.md` (actualizado §32)
- `quality/reports/designreviewer/INC-6.4-report.txt` (nuevo)
- `docs/reports/US-6.4.6-report.md` (Fase 9)
