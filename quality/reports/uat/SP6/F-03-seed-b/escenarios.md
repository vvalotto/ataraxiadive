# Escenarios — Fase F-03: Volcado de Datos (Seed-B)

## Criterio de Entrada

- [ ] F-02 completada: torneo creado · `torneo_id` anotado
- [ ] `uat_ba2025_usuarios_ids.json` existe en `quality/reports/uat/SP6/`

## Comando

```bash
# Seed-B abre inscripciones, carga 31 atletas y deja el torneo en INSCRIPCION_ABIERTA
uv run python tests/uat/sp6/seed_ba2025_inscripciones.py --torneo-id <torneo_id_de_F02>
```

## Escenarios de verificación

| ID | Actor | Dispositivo | Acción | Resultado esperado | Resultado real | Estado | Hallazgo |
|----|-------|-------------|--------|--------------------|----------------|--------|----------|
| F03-S01 | Organizador | Desktop | Ver lista de inscriptos en DBF | Atletas con disciplina DBF · columna "ANUNCIO" con AP en metros · categoría legible | — | ⬜ PENDIENTE | — |
| F03-S02 | Organizador | Desktop | Verificar atleta Víctor Valotto en STA | AP visible en formato mm:ss en columna ANUNCIO | — | ⬜ PENDIENTE | — |
| F03-S03 | Atleta (Víctor Valotto) | Móvil | Login → ver inscripciones propias | Sus disciplinas con AP declarada | — | ⬜ PENDIENTE | — |

## Criterio de Salida

- [ ] Seed-B completado sin errores
- [ ] 31 atletas visibles en la lista de inscriptos
- [ ] APs correctas en cada disciplina
- [ ] Estado del torneo: `INSCRIPCION_ABIERTA` (Seed-B lo abre internamente)
