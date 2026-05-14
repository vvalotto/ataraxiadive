# Hallazgos — Fase F-09: Resultados Completos y Premiación

**Fecha de apertura:** 2026-05-14

---

## Defectos

| ID | Escenario | Descripción | Severidad | Pasos para reproducir | Estado | Fix |
|----|-----------|-------------|-----------|----------------------|--------|-----|
| H-09-01 | F09-S02/S03 | Pestaña "Podios" vacía durante estado `EJECUCION` | ✅ Diseño correcto | — | ✅ Cerrado | Comportamiento esperado: podios y overall se calculan y muestran solo al pasar a `PREMIACION` |
| H-09-02 | F09-S04 | Motivo de descalificación (`BKO_SUPERFICIE`) no visible en ninguna grilla — tarjeta roja aparece pero sin MotivoDQ | 🟠 Moderado | Grilla STA organizador → fila Matias Gonzalez Courtois → tarjeta roja presente · motivo ausente | ✅ Resuelto | `TablaDisciplinaResultados`: fallback `motivo_dq` y `penalizaciones` desde `GrillaAtletaDto` cuando ranking no los trae |
| H-09-03 | F09-S08 | Etiqueta `BKO_SUPERFICIE` muestra "Blackout" genérico — no distingue de `BKO_SUBACUATICO` en ninguna grilla | 🟡 Menor | Grilla DBF/STA → tarjeta roja BKO_SUPERFICIE → label "Blackout" sin especificar tipo | ✅ Resuelto | `tarjeta.ts`: `BKO_SUPERFICIE` → `'Blackout superficie'` |
| H-09-04 | F09-S12/S13 | Callback `on_finalizada` nunca cableado en el router HTTP — P-08 (`CalcularRanking`) y P-09 (`CalcularOverall`) no se disparaban al finalizar una competencia vía API | 🔴 Crítico | Finalizar todas las performances de una disciplina → `GET /ranking/{id}` devuelve `calculado: false` y rankings vacíos | ✅ Resuelto | `router.py`: `configure_on_finalizada_callback()` + los tres handlers (`asignar_tarjeta`, `registrar_dns`, `resolver_revision`) reciben el callback. `app.py`: llamada a `configure_on_finalizada_callback` con `AlgoritmoPuntajeFAAS()`. Script `recalcular_rankings.py` para datos ya existentes. |
| H-09-05 | F09-S14/S15 | Algoritmo FAAS calcula `d_max`/`t_min`/`t_max` globalmente — debería ser por categoría+género | 🔴 Crítico | Rankings DNF/DYN: atleta con mejor RP de su categoría recibe < 100 pts si otra categoría tiene una marca mayor | ✅ Resuelto | `algoritmo_faas.py`: `_agrupar_por_categoria()` + iteración por grupo en `_calcular_distancia` y `_calcular_tiempo` |

---

## Mejoras (fuera de scope UAT)

| ID | Origen | Descripción | Prioridad sugerida |
|----|--------|-------------|-------------------|
| — | — | Sin mejoras registradas | — |
