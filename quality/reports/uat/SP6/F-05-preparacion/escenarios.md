# Escenarios — Fase F-05: Preparación (Grilla y Asignación de Jueces)

## Criterio de Entrada

- [x] F-01 cerrada: usuarios autenticables · portal público accesible
- [x] F-02 cerrada: torneo "Apnea Indoor Buenos Aires 2025" en estado `CREADO`
- [x] F-03 cerrada: 31 atletas inscriptos con APs cargadas via Seed-B
- [x] F-04 cerrada: torneo en estado `INSCRIPCION_ABIERTA` · flujo inscripción manual verificado

## Escenarios

| ID | Actor | Dispositivo | Acción | Resultado esperado | Resultado real | Estado | Hallazgo |
|----|-------|-------------|--------|--------------------|----------------|--------|----------|
| F05-S01 | Organizador | Desktop | Cerrar inscripciones desde panel del torneo | Estado pasa a `PREPARACION` · tab Grilla habilitada | Estado PREPARACION · tab Grilla habilitada · tab Jueces se habilita tras generar grilla | ✅ PASS | — |
| F05-S02 | Organizador | Desktop | Generar grilla para DBF | Atletas ordenados por AP desc · andarivel numérico · columna "Anuncios" visible | Correcto · columna ESTADO eliminada (H-05-02) · campo intervalo agregado a regenerar (H-05-01) | ✅ PASS | H-05-01 · H-05-02 |
| F05-S03 | Organizador | Desktop | Generar grilla para DNF | Atletas ordenados por AP desc · andarivel numérico | Correcto | ✅ PASS | — |
| F05-S04 | Organizador | Desktop | Generar grilla para DYN | Atletas ordenados por AP desc · andarivel numérico | Correcto | ✅ PASS | — |
| F05-S05 | Organizador | Desktop | Generar grilla para STA | Marcas de AP en formato mm:ss | Correcto — AP en mm:ss | ✅ PASS | — |
| F05-S06 | Organizador | Desktop | Generar grilla para SPE | Marcas de AP en formato mm:ss | Correcto — AP en mm:ss | ✅ PASS | — |
| F05-S07 | Organizador | Desktop | Asignar Juez 1 → andarivel 1 en DBF/DNF/DYN/SPE | Selector funciona · sin texto redundante | Correcto | ✅ PASS | — |
| F05-S08 | Organizador | Desktop | Asignar Juez 2 → andarivel 2 en DBF/DNF/DYN/SPE | Selector funciona correctamente | Correcto | ✅ PASS | — |
| F05-S09 | Organizador | Desktop | Asignar Juez 1/2/3 → STA (3 andariveles) | 3 jueces asignados en STA | Correcto | ✅ PASS | — |
| F05-S10 | Organizador | Desktop | Panel del torneo → alertas activas | Sin botón "Resolver" · alertas informativas | Correcto · H-05-03/04 detectados y resueltos | ✅ PASS | H-05-03 · H-05-04 |
| F05-S11 | Portal (visitante) | Cualquier dispositivo | Refrescar `/portalapnea` tras PREPARACION | Estado actualizado en portal | Muestra "En preparación" | ✅ PASS | — |
| F05-S12 | Juez 1 | Móvil | Login y ver "Mis asignaciones" | Disciplinas asignadas visibles | DBF y STA (únicos andariveles asignados a Juez 1) — correcto | ✅ PASS | H-05-05 |
| F05-S13 | Juez 3 | Móvil | Login y ver "Mis asignaciones" | Solo STA en sus asignaciones | Solo STA — correcto | ✅ PASS | — |

## Criterio de Salida

- [x] F05-S01 ✅: torneo en estado `PREPARACION`
- [x] F05-S02..S06 ✅: grilla generada para las 5 disciplinas (DBF/DNF/DYN/STA/SPE)
- [x] F05-S07..S09 ✅: jueces asignados por andarivel en todas las disciplinas
- [x] F05-S12/S13 ✅: portal juez muestra asignaciones correctas por rol
- [x] Todos los escenarios 🔴 en PASS
- [x] Sistema listo para F-06 (iniciar ejecución)
