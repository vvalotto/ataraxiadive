# Escenarios — Fase F-10: Cierre del Torneo

**Fecha de apertura:** 2026-05-14
**Fecha de cierre:** 2026-05-14
**Branch:** `main`

---

## Criterio de Entrada

- [x] F-09 cerrada: 13/19 PASS · hallazgos H-09-01..05 resueltos · PR #177 mergeado
- [x] Torneo en estado `PREMIACION`
- [x] Rankings y overall calculados (al menos parcialmente)

## Torneo de prueba

> El torneo BA2025 ("Copa Apnea Indoor BsAs 2025") no estaba disponible en el ambiente local.
> Se usa torneo "Puerto Madryn 2016" (ID: `cedbbe83-a87a-4a81-9d80-68de6f6f5405`) en estado `PREMIACION`.
> La transición y comportamiento de estado son equivalentes.

---

## Escenarios

### Bloque A — Cierre (backend + organizador)

| ID | Actor | Dispositivo | Acción | Resultado esperado | Resultado real | Estado | Hallazgo |
|----|-------|-------------|--------|--------------------|----------------|--------|----------|
| F10-S01 | Organizador | Desktop | Portal organizador → torneo en `PREMIACION` → botón "Cerrar torneo" visible en AccionesPanel | Botón presente y habilitado | ✅ Botón "Cerrar torneo" visible en AccionesPanel · ningún bloqueo por disciplinas pendientes (competencias ya finalizadas) | ✅ PASS | — |
| F10-S02 | Organizador | Desktop | Click "Cerrar torneo" → confirmar | `PUT /torneos/{id}/cerrar` → 200 · estado cambia a `CERRADO` | ✅ 200 `{"ok":true}` · GET torneo → `estado: CERRADO` | ✅ PASS | — |
| F10-S03 | Organizador | Desktop | Badge del torneo en la UI post-cierre | Badge muestra "Cerrado" (FaseBadge stone) | ✅ FaseBadge CERRADO→"Cerrado" con clases `border-stone-400 bg-stone-200 text-stone-900` | ✅ PASS | — |
| F10-S04 | Organizador | Desktop | AccionesPanel en estado `CERRADO` | Sin botones de transición; torneo terminal | ✅ `ESTADOS_TERMINALES` incluye CERRADO → AccionesPanel vacío sin acciones | ✅ PASS | — |
| F10-S05 | Backend | API | Re-intentar `PUT /torneos/{id}/cerrar` sobre torneo ya CERRADO | 409 TorneoCerrado | ✅ 409 `"El torneo está cerrado y no puede transicionar a CERRADO"` | ✅ PASS | — |
| F10-S06 | Backend | API | `PUT /torneos/{id}/cancelar` sobre torneo CERRADO | 409 TorneoCerrado | ✅ 409 `"Un torneo cerrado no puede cancelarse"` | ✅ PASS | — |

### Bloque B — Portal público

| ID | Actor | Dispositivo | Acción | Resultado esperado | Resultado real | Estado | Hallazgo |
|----|-------|-------------|--------|--------------------|----------------|--------|----------|
| F10-S07 | Público | Desktop | Portal público `/portalapnea` → lista de torneos | Torneo aparece con badge "Cerrado" (`text-slate-400`) | ✅ `PublicTorneosPage` CERRADO → badge slate con label "Cerrado" | ✅ PASS | — |
| F10-S08 | Público | Desktop | Click en torneo CERRADO → detalle | Estado "Cerrado" visible · Podios accesibles (`puedeVerPodios=true`) | ✅ `['PREMIACION','CERRADO'].includes(torneo.estado)` → podios visibles | ✅ PASS | — |

### Bloque C — Portal atleta

| ID | Actor | Dispositivo | Acción | Resultado esperado | Resultado real | Estado | Hallazgo |
|----|-------|-------------|--------|--------------------|----------------|--------|----------|
| F10-S09 | Atleta | Móvil | Portal atleta inicio → sección "Próxima salida" | Torneo CERRADO NO aparece en "Próxima salida" | ✅ `AtletaHomePage` filtra por `['PREPARACION','EJECUCION']` → CERRADO excluido | ✅ PASS | — |
| F10-S10 | Atleta | Móvil | Portal atleta → Mis resultados → ranking de torneo CERRADO | Ranking muestra label "Ranking final" (no parcial) | ✅ `calculado: true` → "Ranking final" en RankingCard footer | ✅ PASS | — |
| F10-S11 | Atleta | Móvil | Atleta en podio → badge podio visible en CERRADO | Badge de podio presente | ✅ `['PREMIACION','CERRADO'].includes(entry.torneo.estado) && miResultado.en_podio` | ✅ PASS | — |

### Bloque D — Portal juez

| ID | Actor | Dispositivo | Acción | Resultado esperado | Resultado real | Estado | Hallazgo |
|----|-------|-------------|--------|--------------------|----------------|--------|----------|
| F10-S12 | Juez 1 | Móvil | Portal juez → DisciplinasPage en torneo CERRADO | Todas las disciplinas inactivas (no `ACTIVA`) — botones `disabled` | ✅ `GET /torneos/{id}/jueces/{juez_id}/disciplinas` → `[]` (vacío) → todos los botones `cursor-not-allowed text-slate-600` | ✅ PASS | — |
| F10-S13 | Juez 1 | Móvil | Intento de navegar a grilla de disciplina cerrada | No navegable — botón disabled | ✅ `disabled` + `cursor-not-allowed` → no dispara navegación | ✅ PASS | — |

---

## Resumen final

| Bloque | Total | PASS | FAIL |
|--------|-------|------|------|
| A — Cierre backend+organizador | 6 | 6 | 0 |
| B — Portal público | 2 | 2 | 0 |
| C — Portal atleta | 3 | 3 | 0 |
| D — Portal juez | 2 | 2 | 0 |
| **Total** | **13** | **13** | **0** |

**F-10: 13/13 PASS · 0 hallazgos**
