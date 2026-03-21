# Fase 7: Quality Gates

**Objetivo:** Validar que el código implementado cumple con los estándares de calidad
usando CodeGuard (Software Limpio) + cobertura de tests.

**Duración estimada:** 5-10 minutos

---

## Tracking

**Al inicio de la fase:**
```python
tracker.start_phase(7, "Quality Gates")
```

---

## Contexto del Proyecto

AtaraxiaDive usa **CodeGuard** (software_limpio) como agente de calidad de código.
CodeGuard orquesta 6 checks: PEP8, Security, Complexity, Pylint, Types, Imports.
Los umbrales están definidos en `pyproject.toml` → `[tool.codeguard]`.

**Umbrales para AtaraxiaDive (perfil fastapi-rest):**

| Métrica | Umbral | Fuente |
|---------|--------|--------|
| Pylint | ≥ 8.0 | `pyproject.toml [tool.codeguard]` |
| Complejidad ciclomática | ≤ 10 | `pyproject.toml [tool.codeguard]` |
| Cobertura | ≥ 90% (domain + application) | `pyproject.toml [tool.pytest]` |

---

## Paso 1: Identificar el BC de la US

La US pertenece a un Bounded Context. Determinar el path del BC:

```
US-1.x.x → src/competencia/
US-2.x.x → src/torneo/
US-3.x.x → src/registro/
US-4.x.x → src/resultados/
US-5.x.x → src/identidad/
US-6.x.x → src/notificaciones/
```

---

## Paso 2: Ejecutar CodeGuard sobre el BC

Dos comandos obligatorios — el primero guarda la evidencia cruda, el segundo muestra
el output en consola para revisión inmediata:

```bash
codeguard src/{BC}/ --format json > quality/reports/codeguard/{US_ID}-codeguard-raw.json
codeguard src/{BC}/
```

**El archivo `{US_ID}-codeguard-raw.json` es la evidencia auténtica del quality gate.**
No sustituir por un JSON escrito manualmente.

**CodeGuard nunca bloquea** — advierte y reporta. El criterio de aprobación
se evalúa manualmente revisando el output.

**Criterio de aprobación:**
- Pylint ≥ 8.0
- Sin issues de severidad ERROR o CRITICAL en los 6 checks
- Complejidad ciclomática ≤ 10 en promedio

**Si hay warnings:**
- Revisar los issues reportados por CodeGuard
- Corregir los de severidad ERROR antes de continuar
- Los WARNING son informativos — documentar si se decide no corregir

---

## Paso 3: Ejecutar cobertura de tests

```bash
pytest tests/unit/{BC}/ \
  --cov=src/{BC}/domain \
  --cov=src/{BC}/application \
  --cov-report=term-missing \
  --cov-report=json:quality/reports/codeguard/{US_ID}-coverage.json
```

**Criterio de aprobación:** Cobertura ≥ 90% en `domain/` + `application/`

**Si cobertura < 90%:**
- Revisar líneas no cubiertas en el reporte
- Agregar tests para los casos faltantes en Fase 4 (retroceder si es necesario)
- Priorizar: aggregates, invariantes, casos de error

---

## Paso 4: Generar reporte consolidado

Crear `quality/reports/codeguard/{US_ID}-quality.json` como **resumen** que referencia
los artefactos de evidencia reales:

```json
{
  "us_id": "{US_ID}",
  "fecha": "<ISO timestamp>",
  "bc": "src/{BC}/",
  "codeguard": {
    "estado": "APROBADO | CON_WARNINGS | RECHAZADO",
    "pylint": "<score>",
    "issues_criticos": 0,
    "evidencia_raw": "quality/reports/codeguard/{US_ID}-codeguard-raw.json"
  },
  "coverage": {
    "estado": "APROBADO | RECHAZADO",
    "porcentaje": "<valor>",
    "evidencia_raw": "quality/reports/codeguard/{US_ID}-coverage.json"
  },
  "estado_final": "APROBADO | RECHAZADO",
  "observaciones": []
}
```

**Estado final:**
- `APROBADO` — CodeGuard sin CRITICALs + cobertura ≥ 90%
- `CON_WARNINGS` — CodeGuard con warnings menores + cobertura ≥ 90% (puede continuar)
- `RECHAZADO` — Issues críticos o cobertura < 90% (corregir antes de Fase 8)

---

## Nota sobre DesignReviewer

**DesignReviewer NO se ejecuta manualmente en esta fase.**
Corre automáticamente como hook pre-push cuando se hace push de la branch
`feature/US-X.Y.Z-*` para abrir el PR a develop. Si hay violations CRITICAL, bloquea el push.

Adicionalmente, al cerrar el Incremento (todas las US mergeadas), se corre una vez más
en forma manual sobre `develop` para confirmar el estado consolidado.

Ver `docs/plans/WORKFLOW-DESARROLLO.md` → §5 Ciclo por US-IEDD y §8 Quality Gates.

---

## Tracking al Finalizar

```python
tracker.end_phase(7, auto_approved=True)
```

---

## Resumen de la Fase

Al finalizar:

✅ CodeGuard ejecutado sobre `src/{BC}/`
✅ Evidencia cruda guardada en `quality/reports/codeguard/{US_ID}-codeguard-raw.json`
✅ Cobertura ≥ 90% en `domain/` + `application/`
✅ Reporte consolidado en `quality/reports/codeguard/{US_ID}-quality.json` (referencia los raw)
✅ Estado final documentado (APROBADO / CON_WARNINGS / RECHAZADO)
⏭️  DesignReviewer corre automáticamente al hacer push (pre-push hook) — no requiere acción manual aquí

**Próxima fase:** Fase 8 — Documentación
