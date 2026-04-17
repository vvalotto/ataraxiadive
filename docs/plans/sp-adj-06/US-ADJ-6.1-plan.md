# Plan Técnico — US-ADJ-6.1
## Investigar y resolver import cross-BC en `exportar_resultados.py`

*Generado: 2026-04-17 — Fase 2 /implement-us US-ADJ-6.1*

---

## Diagnóstico final

El LAZY-01 de la revisión pre-BL-004 señalaba un lazy import de `Performance` en
`_performance_a_resultado_final`. **Ese import no existe** en el código actual.

Las violaciones reales están en los imports a nivel de módulo:

| Línea | Import | Severidad | Uso real |
|-------|--------|-----------|----------|
| 12 | `competencia.domain.aggregates.competencia.Competencia` | 🔴 CRÍTICO | `_obtener_estado_y_hash()` reconstituye el aggregate solo para leer `estado.value` y `hash_sha256` |
| 13 | `competencia.domain.value_objects.disciplina.Disciplina as CompetenciaDisciplina` | 🔴 dependiente | Solo se usa para construir `Competencia.reconstitute()` |
| 17 | `registro.domain.value_objects.categoria.Categoria` | 🟡 menor | Campo muerto `_PerformanceExportData.categoria` — nunca se lee en output |
| 14–16 | `competencia.infrastructure.repositories.SQLiteCompetenciasPorTorneo` | 🟡 infra | Type hint de parámetro — diferido (requiere crear protocolo en port) |

---

## Solución por tarea

### T1 — Reemplazar `_obtener_estado_y_hash()` con proyección directa

**Problema:** La función carga eventos y reconstituye `Competencia` (aggregate completo)
solo para leer dos campos: `estado.value` y `hash_sha256`.

**Solución:** Proyectar esos campos iterando los eventos como dicts, sin importar el aggregate.

```python
# ANTES — importa Competencia (cross-BC)
competencia = Competencia.reconstitute(
    competencia_id=competencia_id,
    disciplina=CompetenciaDisciplina(disciplina.value),
    events=events,
)
return competencia.estado.value, competencia.hash_sha256

# DESPUÉS — proyección directa desde payloads
estado = "Preparacion"
hash_sha256 = None
for event in events:
    event_type = event["event_type"]
    if event_type == "CompetenciaIniciada":
        estado = "EnCurso"
    elif event_type == "CompetenciaFinalizada":
        payload = _parse_payload(event["payload"])
        estado = "Finalizada"
        hash_sha256 = payload.get("hash_sha256")
return estado, hash_sha256
```

Los estados proyectados son exactamente los que usa el código consumidor:
- `"Preparacion"` — sin eventos
- `"EnCurso"` — después de `CompetenciaIniciada`
- `"Finalizada"` — después de `CompetenciaFinalizada`

**Elimina:** imports líneas 12 y 13.

---

### T2 — Eliminar campo muerto `_PerformanceExportData.categoria`

**Problema:** `_PerformanceExportData.categoria: Categoria | None = None` importa
`Categoria` de `registro/domain/` pero el campo nunca se asigna ni se lee en output.

- `_extraer_performance_exportable()` nunca setea `categoria`
- `_construir_fila_disciplina()` obtiene `categoria` de `atleta_info.categoria.value` directamente
- El `replace(..., categoria=atleta_info.categoria)` en `_calcular_ranking_parcial` opera
  sobre `ResultadoFinal`, no sobre `_PerformanceExportData`

**Solución:** Eliminar el campo y el import.

**Nota:** `ResultadoFinal` en `resultados/domain/ports/` también importa `Categoria`
de `registro/domain/` — eso es una decisión de diseño del ACL y queda fuera de esta US.

---

### T3 — Diferir `SQLiteCompetenciasPorTorneo` (out of scope)

El tipo del parámetro `competencias_por_torneo: SQLiteCompetenciasPorTorneo` en el
`__init__` del handler es una dependencia infra cross-BC. Corregirla requiere crear
un protocolo/port en `resultados/domain/ports/` y su adaptador. Diferido a SP5.

---

## Archivos afectados

| Archivo | Cambio |
|---------|--------|
| `src/resultados/application/queries/exportar_resultados.py` | Eliminar imports 12/13/17, reemplazar `_obtener_estado_y_hash()`, eliminar campo `categoria` de `_PerformanceExportData` |

## Tests afectados

Los tests existentes de `ExportarResultadosHandler` son la red de seguridad.
No se crean tests nuevos — los existentes deben seguir pasando sin modificación.

Ubicación: `tests/unit/resultados/application/` o equivalente.

## Estimación

| Tarea | Estimado |
|-------|----------|
| T1 — reemplazar `_obtener_estado_y_hash()` | 15 min |
| T2 — eliminar `Categoria` campo muerto | 5 min |
| Tests + CodeGuard | 10 min |
| **Total** | **30 min** |
