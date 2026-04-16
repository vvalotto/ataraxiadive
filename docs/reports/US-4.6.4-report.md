# Reporte de Implementación — US-4.6.4
## Exportación de resultados CSV y JSON

**Sprint:** SP4 — La Plataforma  
**Incremento:** INC-4.6  
**Branch:** `feature/US-4.6.4-export-resultados`  
**Fecha:** 2026-04-16

---

## Resumen

Se implementó la cuarta US de `INC-4.6` en el BC `resultados`: una exportación
descargable por torneo en formatos `json` y `csv`, consolidando disciplinas,
rankings, estado de competencia, `hash_sha256` cuando la disciplina está
finalizada y overall del torneo.

La solución agrega una query de exportación que compone información de tres BCs:

- `Resultados` para ranking y overall
- `Competencia` para estado, hash y performances finalizadas
- `Registro`/`Torneo` para datos de atleta y metadata del torneo

---

## Cambios implementados

### Código

| Archivo | Cambio |
|---------|--------|
| `src/resultados/application/queries/exportar_resultados.py` | Nueva query `ExportarResultados` con consolidación por torneo, cálculo parcial en memoria cuando no hay ranking persistido y DTOs exportables |
| `src/resultados/api/router.py` | Nuevo endpoint `GET /resultados/{torneo_id}/export?format=csv|json` con descarga y validación de formato |
| `src/resultados/infrastructure/repositories/atleta_info_adapter.py` | Nuevo ACL a Registro para nombre completo, categoría y club |
| `src/resultados/domain/exceptions.py` | Nueva excepción `TorneoNoEncontrado` |

### Tests

| Archivo | Cobertura |
|---------|-----------|
| `tests/unit/resultados/application/test_exportar_resultados_handler.py` | 404 lógico por torneo inexistente y exportación con hash solo en disciplina finalizada |
| `tests/unit/resultados/api/test_router_export.py` | `200` JSON, `200` CSV, `400` format inválido, `404` torneo inexistente y `403` por rol juez |

### Artefactos de proceso

| Archivo | Propósito |
|---------|-----------|
| `tests/features/US-4.6.4-exportacion-resultados.feature` | Escenarios BDD de la US |
| `docs/plans/sp4/US-4.6.4-plan.md` | Plan aprobado de implementación |
| `docs/reports/US-4.6.4-bdd-waiver.md` | Sustitución explícita de automatización BDD por tests unitarios + HTTP |
| `docs/traceability/matrix.md` | Registro de `US-4.6.4` dentro de `INC-4.6` |
| `quality/reports/codeguard/US-4.6.4-codeguard.json` | Evidencia del quality gate focalizado |

---

## Decisiones de diseño

### 1. Exportación como query agregada, no como composición en el router

La lógica de consolidación quedó en `ExportarResultadosHandler`, no repartida en
el endpoint. El router solo valida formato, control de acceso y serialización.

Esto evita que la API termine concentrando lógica cross-BC.

### 2. Ranking persistido si existe; cálculo parcial en memoria si no

Si la disciplina ya tiene ranking persistido en `Resultados`, se exporta esa
fuente. Si todavía no existe pero sí hay performances finalizadas, la query
calcula un ranking parcial en memoria sin persistir eventos nuevos.

Esto permite exportar disciplinas en ejecución con los resultados disponibles.

### 3. Hash solo cuando la disciplina está finalizada

El `hash_sha256` se resuelve desde el stream de competencia y solo se expone en
JSON cuando el estado de la disciplina es `Finalizada`. Para disciplinas en
ejecución queda omitido.

---

## Validación ejecutada

### Pytest focalizado

Comando ejecutado:

```bash
./.venv/bin/pytest \
  tests/unit/resultados/application/test_exportar_resultados_handler.py \
  tests/unit/resultados/api/test_router_export.py \
  tests/unit/resultados/api/test_router_ranking.py \
  tests/unit/resultados/api/test_router_overall.py
```

Resultado:

```text
10 passed in 3.74s
```

### CodeGuard focalizado

Comando ejecutado:

```bash
./.venv/bin/codeguard \
  src/resultados/application/queries/exportar_resultados.py \
  src/resultados/api/router.py \
  src/resultados/infrastructure/repositories/atleta_info_adapter.py \
  src/resultados/domain/exceptions.py \
  tests/unit/resultados/application/test_exportar_resultados_handler.py \
  tests/unit/resultados/api/test_router_export.py \
  -c pyproject.toml -a pre-commit -t 15 --format json \
  > quality/reports/codeguard/US-4.6.4-codeguard.json
```

Resultado:

```text
0 errors
3 warnings
37 infos
```

Los warnings remanentes corresponden a `assert` en tests, no a código productivo.

---

## Estado respecto de la spec

### Cumplido

- Exportación en `json` y `csv`
- `Content-Disposition` para descarga
- `400` para formatos inválidos
- `404` para torneo inexistente
- `403` para rol juez
- Inclusión condicional de `hash_sha256`
- Exportación de disciplinas del torneo con lo que haya disponible

### Diferencia menor respecto de la redacción original

- El campo `puntos` de la exportación por disciplina se resuelve con la semántica
  posicional actualmente disponible en el dominio (`posicion` para resultados
  válidos, `0` para DNS/Roja), porque el BC no tiene hoy un puntaje federativo
  separado persistido por disciplina.

---

## Riesgos y próximos pasos

- Si FAAS necesita un esquema de puntaje disciplinar distinto del puntaje
  posicional actual, habrá que formalizarlo como regla de dominio explícita.
- La exportación hoy consolida ACLs cross-BC dentro de la query; si crece el
  número de formatos o consumidores, puede convenir separar serialización y
  consolidación en servicios más finos.
- `US-4.6.5+` ya no necesita backend nuevo para exportación base; puede apoyarse
  en este endpoint como salida estable del incremento.
