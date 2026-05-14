# Escenarios — Fase F-09: Resultados Completos y Premiación

**Fecha de apertura:** 2026-05-14  
**Branch:** `uat/INC-6.5/F-09-resultados-premiacion`

---

## Criterio de Entrada

- [x] F-08 cerrada: 8/8 PASS · hallazgos H-08-01/02/03 resueltos · PR #176 mergeado
- [x] Torneo en estado `EJECUCION`
- [x] Seed-C disponible: `tests/uat/sp6/seed_ba2025_resultados.py`
- [ ] Seed-C ejecutado sin errores: `uv run python tests/uat/sp6/seed_ba2025_resultados.py --torneo-id <id>`

---

## Preparación: ejecutar Seed-C

```bash
uv run python tests/uat/sp6/seed_ba2025_resultados.py --torneo-id <torneo_id>
```

Esperar: `Errores: 0` antes de continuar con los escenarios.

---

## Escenarios

| ID | Actor | Dispositivo | Acción | Resultado esperado | Resultado real | Estado | Hallazgo |
|----|-------|-------------|--------|--------------------|----------------|--------|----------|
| F09-S01 | Organizador | Desktop | Ver resultados **STA** post-Seed-C · verificar formato de marcas | Marcas en mm:ss · sin columna "PTS FAAS" · andarivel numérico visible | — | ⬜ PENDIENTE | — |
| F09-S02 | Organizador | Desktop | Ver **podios STA SENIOR MASC** | 1° José Enjuto 06:33 · 2° Mauro Almada 05:42 · 3° Pablo Sale 05:19 | — | ⬜ PENDIENTE | — |
| F09-S03 | Organizador | Desktop | Ver página de **Podios** (separada de Resultados) | Podios en página propia · contenido correcto por categoría/disciplina | — | ⬜ PENDIENTE | — |
| F09-S04 | Organizador | Desktop | Ver **Overall SENIOR MASC** | Ranking overall correcto según sistema FAAS | — | ⬜ PENDIENTE | — |
| F09-S05 | Organizador | Desktop | **Iniciar premiación** | Estado pasa a `PREMIACION` · UI refleja nuevo estado | — | ⬜ PENDIENTE | — |
| F09-S06 | Portal (visitante) | Cualquiera | Ver página pública del torneo post-Seed-C | Podios actualizados · grilla con resultados completos | — | ⬜ PENDIENTE | — |
| F09-S07 | Atleta (Víctor Valotto) | Móvil | Ver resultado propio **STA** | RP=04:32.98 en mm:ss · rank 1 MASTER MASC STA | — | ⬜ PENDIENTE | — |
| F09-S08 | Atleta (Víctor Valotto) | Móvil | Ver resultado propio **DBF** | RP=52.40m · rank correcto MASTER MASC DBF | — | ⬜ PENDIENTE | — |
| F09-S09 | Atleta (Guadalupe Fardi) | Móvil | Ver resultado propio **DNF** | RP=41.05m · rank 1 JUNIOR FEM DNF | — | ⬜ PENDIENTE | — |
| F09-S10 | Atleta (Guadalupe Fardi) | Móvil | Ver **overall** propio | Rank 1 JUNIOR FEM overall | — | ⬜ PENDIENTE | — |

---

## Valores de referencia (oráculo — results.json)

### STA SENIOR MASCULINO (top 3)

| Pos | Atleta | Resultado |
|-----|--------|-----------|
| 1° | José Enjuto | 06:33.05 |
| 2° | Mauro Almada | 05:42.xx |
| 3° | Pablo Sale | 05:19.xx |

> Verificar valores exactos contra `data/datasets/buenos_aires_2025/results.json`.

### Víctor Valotto (MASTER MASC)

| Disciplina | RP | Unidad |
|-----------|----|--------|
| DBF | 52.40 | metros |
| STA | 04:32.98 | mm:ss |

### Guadalupe Fardi (JUNIOR FEM)

| Disciplina | RP | Unidad |
|-----------|----|--------|
| DNF | 41.05 | metros |
| DBF | 78.52 | metros |

---

## Criterio de Salida

- [ ] F09-S01 PASS: marcas STA en mm:ss · sin columna "PTS FAAS"
- [ ] F09-S02 PASS: podios STA SENIOR MASC correctos (oráculo verificado)
- [ ] F09-S03 PASS: página de podios existe y tiene contenido correcto
- [ ] F09-S04 PASS: overall SENIOR MASC calculado correctamente
- [ ] F09-S05 PASS: torneo en estado `PREMIACION`
- [ ] Todos los escenarios 🔴 en PASS
- [ ] 0 hallazgos 🔴 sin resolver

---

**Estados de escenario:** ✅ PASS · ❌ FAIL · ⏭️ SKIP · ⬜ PENDIENTE
