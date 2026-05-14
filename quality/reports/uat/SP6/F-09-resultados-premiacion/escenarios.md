# Escenarios — Fase F-09: Resultados Completos y Premiación

**Fecha de apertura:** 2026-05-14
**Branch:** `uat/INC-6.5/F-09-resultados-premiacion`

---

## Criterio de Entrada

- [x] F-08 cerrada: 8/8 PASS · hallazgos H-08-01/02/03 resueltos · PR #176 mergeado
- [x] Torneo en estado `EJECUCION`
- [x] Seed-C disponible con `--disciplina` y mix de resultados

---

## Estrategia de ejecución

Seed-C se corre **por disciplina** para simular el avance cronológico real de la competencia. Entre cada disciplina se verifican rankings y podios parciales.

```bash
# Orden de ejecución
uv run python tests/uat/sp6/seed_ba2025_resultados.py --torneo-id <id> --disciplina STA
uv run python tests/uat/sp6/seed_ba2025_resultados.py --torneo-id <id> --disciplina DBF
uv run python tests/uat/sp6/seed_ba2025_resultados.py --torneo-id <id> --disciplina DNF
uv run python tests/uat/sp6/seed_ba2025_resultados.py --torneo-id <id> --disciplina DYN
uv run python tests/uat/sp6/seed_ba2025_resultados.py --torneo-id <id> --disciplina SPE_2X50
```

---

## Mix de resultados por disciplina (overrides del Seed-C)

| Disciplina | Atleta override | Tipo | Detalle |
|-----------|----------------|------|---------|
| DBF | Matias Gonzalez Courtois | Roja BKO_SUPERFICIE | distancia_blackout=70m |
| DBF | Diego Calvo | Blanca+penalización | INFRACCION_TECNICA −3m → RP 64,95m |
| DNF | Nicolas Stafforini | Roja BKO_SUBACUATICO | distancia_blackout=35m |
| DNF | Diego Calvo | Blanca+penalización | INFRACCION_TECNICA −3m → RP 40,30m |
| DNF | José Clementi, Juan I. Catalano, Laura Iglesias, Pablo Sale, Thiago Stalldecker, Nicolás Zimmermann | DNS | En schedules, sin resultado real |
| DYN | Ezequiel Cuchiarelli | Roja BKO_SUPERFICIE | distancia_blackout=15m |
| DYN | Sebastián Quintana | Blanca+penalización | INFRACCION_TECNICA −3m → RP 52,50m |
| DYN | Juan I. Catalano | DNS | En schedules, sin resultado real |
| SPE | Matias Gonzalez Courtois | Roja BKO_SUBACUATICO | tiempo disciplines |
| SPE | Nicolás Burgell | Blanca+penalización | INFRACCION_TECNICA −5s → RP 94,36s |
| SPE | Diego Calvo, José Clementi, Shaojun Wang | DNS | En schedules, sin resultado real |
| STA | Matias Gonzalez Courtois | Roja BKO_SUPERFICIE | |
| STA | Nicolás Burgell | Blanca+penalización | INFRACCION_TECNICA −5s → RP 182,22s |

> Atletas NO en overrides → Blanca con RP de results.json
> Atletas ya procesados en F-07/F-08 → skip automático

---

## Escenarios

### Bloque A — STA (primera disciplina)

| ID | Actor | Dispositivo | Acción | Resultado esperado | Resultado real | Estado | Hallazgo |
|----|-------|-------------|--------|--------------------|----------------|--------|----------|
| F09-S01a | — | — | Correr Seed-C `--disciplina STA` | Errores: 0 · reporta BKO y penalización en log | — | ⬜ PENDIENTE | — |
| F09-S01b | Organizador | Desktop | Ver resultados **STA** · verificar formato | Marcas en mm:ss · sin columna "PTS FAAS" · andarivel numérico | — | ⬜ PENDIENTE | — |
| F09-S02 | Organizador | Desktop | Ver **podios STA SENIOR MASC** | 1° José Enjuto 06:33 · 2° Mauro Almada 05:42 · 3° Pablo Sale 05:19 | — | ⬜ PENDIENTE | — |
| F09-S03 | Organizador | Desktop | Ver **podios STA MASTER MASC** | 1° Víctor Valotto 04:32 · 2° Alejandro Alperin 04:04 · 3° Raúl Urquiza 03:39 | — | ⬜ PENDIENTE | — |
| F09-S04 | Organizador | Desktop | Verificar **Matias Gonzalez Courtois STA** — BKO | Tarjeta roja · motivo BKO_SUPERFICIE visible · excluido del ranking | — | ⬜ PENDIENTE | — |
| F09-S05 | Organizador | Desktop | Verificar **Nicolás Burgell STA** — penalización | RP original visible · deducción −5s · RP final 182,22s (3:02.22) | — | ⬜ PENDIENTE | — |
| F09-S06 | Atleta (Víctor Valotto) | Móvil | Ver resultado propio **STA** | RP=04:32.98 en mm:ss · rank 1 MASTER MASC STA | — | ⬜ PENDIENTE | — |

### Bloque B — DBF

| ID | Actor | Dispositivo | Acción | Resultado esperado | Resultado real | Estado | Hallazgo |
|----|-------|-------------|--------|--------------------|----------------|--------|----------|
| F09-S07a | — | — | Correr Seed-C `--disciplina DBF` | Errores: 0 · salta a Víctor Valotto y Ezequiel Cuchiarelli (ya procesados) | — | ⬜ PENDIENTE | — |
| F09-S07b | Organizador | Desktop | Ver resultados **DBF** · verificar formato | Marcas en metros · podios correctos | — | ⬜ PENDIENTE | — |
| F09-S08 | Organizador | Desktop | Verificar **Matias Gonzalez Courtois DBF** — BKO | Tarjeta roja BKO_SUPERFICIE · distancia_blackout=70m visible | — | ⬜ PENDIENTE | — |
| F09-S09 | Organizador | Desktop | Verificar **Diego Calvo DBF** — penalización | RP 67,95m · deducción −3m · RP final 64,95m | — | ⬜ PENDIENTE | — |
| F09-S10 | Atleta (Víctor Valotto) | Móvil | Ver resultado propio **DBF** | RP=52.40m · rank correcto MASTER MASC DBF | — | ⬜ PENDIENTE | — |

### Bloque C — DNF, DYN, SPE

| ID | Actor | Dispositivo | Acción | Resultado esperado | Resultado real | Estado | Hallazgo |
|----|-------|-------------|--------|--------------------|----------------|--------|----------|
| F09-S11 | — | — | Correr Seed-C `--disciplina DNF` | Errores: 0 · DNS para 6 atletas sin resultado | — | ⬜ PENDIENTE | — |
| F09-S12 | — | — | Correr Seed-C `--disciplina DYN` | Errores: 0 · BKO Ezequiel Cuchiarelli | — | ⬜ PENDIENTE | — |
| F09-S13 | — | — | Correr Seed-C `--disciplina SPE_2X50` | Errores: 0 · BKO y penalización en log | — | ⬜ PENDIENTE | — |
| F09-S14 | Atleta (Guadalupe Fardi) | Móvil | Ver resultado propio **DNF** | RP=41.05m · rank 1 JUNIOR FEM DNF | — | ⬜ PENDIENTE | — |
| F09-S15 | Atleta (Guadalupe Fardi) | Móvil | Ver **overall** propio | Rank 1 JUNIOR FEM overall | — | ⬜ PENDIENTE | — |

### Bloque D — Overall y Premiación

| ID | Actor | Dispositivo | Acción | Resultado esperado | Resultado real | Estado | Hallazgo |
|----|-------|-------------|--------|--------------------|----------------|--------|----------|
| F09-S16 | Organizador | Desktop | Ver **Overall SENIOR MASC** | Ranking overall correcto según sistema FAAS | — | ⬜ PENDIENTE | — |
| F09-S17 | Organizador | Desktop | Ver página de **Podios** | Podios en página propia · contenido correcto por categoría/disciplina | — | ⬜ PENDIENTE | — |
| F09-S18 | Organizador | Desktop | **Iniciar premiación** | Estado pasa a `PREMIACION` · UI refleja nuevo estado | — | ⬜ PENDIENTE | — |
| F09-S19 | Portal (visitante) | Cualquiera | Ver página pública del torneo | Podios actualizados · grilla con resultados completos | — | ⬜ PENDIENTE | — |

---

## Valores de referencia — oráculo (results.json)

### STA SENIOR MASCULINO top 3
| Pos | Atleta | Resultado |
|-----|--------|-----------|
| 1° | José Enjuto | 06:33.05 |
| 2° | Mauro Almada | 05:42.09 |
| 3° | Pablo Sale | 05:19.94 |

### STA MASTER MASCULINO top 3
| Pos | Atleta | Resultado |
|-----|--------|-----------|
| 1° | Víctor Valotto | 04:32.98 |
| 2° | Alejandro Alperin | 04:04.38 |
| 3° | Raúl Urquiza | 03:39.62 |

### Atletas override — efectos esperados en ranking
| Atleta | Disciplina | Override | Impacto ranking |
|--------|-----------|---------|----------------|
| Matias Gonzalez Courtois | DBF/DNF/DYN/SPE/STA | BKO → Roja | Excluido de todos los rankings |
| Diego Calvo | DBF | Blanca+penal −3m | RP final 64,95m (era 67,95m, rank 12→12) |
| Diego Calvo | DNF | Blanca+penal −3m | RP final 40,30m (era 43,30m, rank 9→9) |
| Sebastián Quintana | DYN | Blanca+penal −3m | RP final 52,50m (era 55,50m, rank 11→11) |
| Nicolás Burgell | SPE | Blanca+penal −5s | RP final 94,36s (era 99,36s, rank 9→9) |
| Nicolás Burgell | STA | Blanca+penal −5s | RP final 182,22s (era 187,22s, rank 9→9) |

---

## Criterio de Salida

- [ ] Seed-C ejecutado para las 5 disciplinas: Errores=0 en todas
- [ ] F09-S02 PASS: podios STA SENIOR MASC correctos (oráculo verificado)
- [ ] F09-S04 PASS: BKO_SUPERFICIE visible en organizador para Matias G.C.
- [ ] F09-S05 PASS: penalización visible y RP final correcto para Nicolás Burgell
- [ ] F09-S18 PASS: torneo en estado `PREMIACION`
- [ ] Todos los escenarios 🔴 en PASS
- [ ] 0 hallazgos 🔴 sin resolver

---

**Estados:** ✅ PASS · ❌ FAIL · ⏭️ SKIP · ⬜ PENDIENTE
