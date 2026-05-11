# Escenarios — Fase F-03: Volcado de Datos (Seed-B)

## Criterio de Entrada

- [x] F-02 completada: torneo creado · `torneo_id` anotado
- [x] Organizador abrió inscripciones desde la UI (F-04-S01) → torneo en `INSCRIPCION_ABIERTA`
- [x] `uat_ba2025_usuarios_ids.json` existe en `quality/reports/uat/SP6/`

## Comando

```bash
# Seed-B carga 31 atletas con APs — requiere torneo en INSCRIPCION_ABIERTA
uv run python tests/uat/sp6/seed_ba2025_inscripciones.py --torneo-id cedbbe83-a87a-4a81-9d80-68de6f6f5405
```

## Escenarios de verificación

| ID | Actor | Dispositivo | Acción | Resultado esperado | Resultado real | Estado | Hallazgo |
|----|-------|-------------|--------|--------------------|----------------|--------|----------|
| F03-S01 | Organizador | Desktop | Ver lista de inscriptos en DBF | Atletas con disciplina DBF · columna "ANUNCIO" con AP en metros · categoría legible | 31 atletas visibles · APs correctas · categorías legibles · 2 hallazgos visuales corregidos | ✅ PASS | H-03-01 · H-03-02 |
| F03-S02 | Organizador | Desktop | Verificar atleta Víctor Valotto en STA | AP visible en formato mm:ss en columna ANUNCIO | Se muestra `3:15` correctamente | ✅ PASS | — |
| F03-S03 | Atleta (Víctor Valotto) | Móvil | Login → ver inscripciones propias | Sus disciplinas con AP declarada | Disciplinas e inscripciones visibles con APs declaradas | ✅ PASS | — |

## Criterio de Salida

- [x] Seed-B completado sin errores
- [x] 31 atletas visibles en la lista de inscriptos
- [x] APs correctas en cada disciplina
- [x] Estado del torneo: `INSCRIPCION_ABIERTA` (abierto por el organizador en F-04-S01)
