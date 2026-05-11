# Escenarios — Fase F-02: Creación del Torneo

## Criterio de Entrada

- [x] F-01 cerrada: usuarios autenticables · portal público accesible
- [x] Backend y frontend levantados

## Datos usados

Torneo de referencia UAT: **Puerto Madryn 2016** (`cedbbe83-a87a-4a81-9d80-68de6f6f5405`)  
*(el nombre del torneo no afecta la funcionalidad del UAT — los datos del dataset BA2025 se vinculan por torneo_id)*

## Escenarios

| ID | Actor | Dispositivo | Acción | Resultado esperado | Resultado real | Estado | Hallazgo |
|----|-------|-------------|--------|--------------------|----------------|--------|----------|
| F02-S01 | Organizador | Desktop | Crear torneo con datos y categorías | Torneo creado · `torneo_id` disponible | Torneo creado correctamente · categorías JUNIOR/SENIOR/MASTER | ✅ PASS | H-02-01 · H-02-02 · H-02-03 · H-02-04 (todos resueltos) |
| F02-S02 | Organizador | Desktop | Configurar disciplinas: DBF, DNF, DYN, SPE_2X50, STA | 5 disciplinas asociadas al torneo | 5 disciplinas confirmadas vía API | ✅ PASS | H-02-06 🟡 diferido |
| F02-S03 | Organizador | Desktop | Verificar categorías: JUNIOR, SENIOR, MASTER | Categorías guardadas | Confirmadas en API (`grupos_etarios`) | ✅ PASS | — |
| F02-S04 | Visitante | Cualquier | Refrescar `/portalapnea` | Torneo aparece en la lista | Ambos torneos visibles en portal público | ✅ PASS | — |
| F02-S05 | Organizador | Desktop | Verificar lista de torneos ordenada por fecha | Torneos ordenados por fecha de inicio ascendente | Orden correcto tras fix | ✅ PASS | H-02-05 (resuelto) |

## Registro de torneo_id

```
torneo_id: cedbbe83-a87a-4a81-9d80-68de6f6f5405  (Puerto Madryn 2016)
```

## Criterio de Salida

- [x] Torneo creado con 5 disciplinas y 3 categorías
- [x] `torneo_id` registrado
- [x] Torneo visible en portal público
- [x] Lista del organizador ordenada por fecha ascendente
- [x] Estado: `CREADO`
