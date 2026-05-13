# Escenarios — Fase F-07: Ejecución Normal de Performances

## Criterio de Entrada

- [ ] F-06 cerrada: torneo en estado `EJECUCION`
- [ ] Portal público activo · grilla visible públicamente
- [ ] Jueces asignados por andarivel en todas las disciplinas
- [ ] Dataset BA 2025 disponible: schedules.json con APs y results.json con RPs reales

## Atletas del Escenario Manual

| Atleta | Disciplina | Andarivel | Juez | AP | RP real | Tarjeta |
|--------|-----------|:---------:|------|-----|---------|---------|
| Ezequiel Cuchiarelli | DBF | 1 | Juez 1 | (schedules) | DNS | — |
| Víctor Valotto | DBF | 2 | Juez 2 | (schedules) | 52.40m | Blanca |
| Guadalupe Fardi | DNF | 1 | Juez 1 | (schedules) | 41.05m | Blanca |
| Alejandro Alperin | SPE | 2 | Juez 2 | (schedules) | 00:59.00 | Blanca |
| Víctor Valotto | STA | 2 | Juez 2 | 03:15 | 04:32.98 | Blanca |
| José Enjuto | STA | 3 | Juez 3 | (schedules) | 06:33.05 | Blanca |

## Escenarios

| ID | Actor | Dispositivo | Acción | Resultado esperado | Resultado real | Estado | Hallazgo |
|----|-------|-------------|--------|--------------------|----------------|--------|----------|
| F07-S01 | Juez 1 | Móvil | Abrir grilla DBF · ver atletas asignados a andarivel 1 | Primer atleta = mayor prioridad de estado · sin scroll horizontal | — | ⬜ PENDIENTE | — |
| F07-S02 | Juez 1 | Móvil | Seleccionar Ezequiel Cuchiarelli DBF · marcar DNS | Performance queda como DNS · atleta no aparece en ranking DBF | — | ⬜ PENDIENTE | — |
| F07-S03 | Juez 2 | Móvil | Seleccionar Víctor Valotto DBF (andarivel 2) · ingresar RP=52.40 · asignar tarjeta blanca | Secuencia correcta: performance → tarjeta → confirmar · pantalla completada en verde | — | ⬜ PENDIENTE | — |
| F07-S04 | Juez 2 | Móvil | Verificar botones de tarjeta antes de seleccionar | Tarjetas sin color cuando no están seleccionadas · diferenciadas al seleccionar | — | ⬜ PENDIENTE | — |
| F07-S05 | Juez 1 | Móvil | Seleccionar Guadalupe Fardi DNF (andarivel 1) · ingresar RP=41.05 | Tarjeta blanca · JUNIOR FEM rank 1 DNF | — | ⬜ PENDIENTE | — |
| F07-S06 | Juez 2 | Móvil | Seleccionar Alejandro Alperin SPE (andarivel 2) · ingresar RP=00:59.00 | Marca en mm:ss · tarjeta blanca | — | ⬜ PENDIENTE | — |
| F07-S07 | Juez 2 | Móvil | Seleccionar Víctor Valotto STA (andarivel 2) · ingresar RP=04:32.98 | Marca en formato mm:ss · tarjeta blanca | — | ⬜ PENDIENTE | — |
| F07-S08 | Juez 3 | Móvil | Seleccionar José Enjuto STA (andarivel 3) · ingresar RP=06:33.05 | Tarjeta blanca · pantalla completada en verde | — | ⬜ PENDIENTE | — |
| F07-S09 | Juez 3 | Móvil | Ver "Mis asignaciones" · verificar que solo aparece STA | Solo STA en su lista · no ve DBF/DNF/DYN/SPE | — | ⬜ PENDIENTE | — |
| F07-S10 | Juez 1 | Móvil | Verificar keypad RpSelector en pantalla de ingreso de RP | Keypad completamente visible sin scroll horizontal en móvil | — | ⬜ PENDIENTE | — |

## Verificación Cruzada

| Momento | Actor | Qué verificar |
|---------|-------|---------------|
| Post F07-S03 | Organizador (desktop) | Resultado de Víctor Valotto visible en grilla DBF con RP y tarjeta |
| Post F07-S06 | Portal (visitante) | Página pública muestra resultado de José Enjuto en STA (polling 30s) |
| Post F07-S07 | Atleta Guadalupe Fardi (móvil) | Login → ver resultado propio · RP=41.05 · rank 1 JUNIOR FEM DNF |

## Criterio de Salida

- [ ] Todos los escenarios 🔴 en PASS (F07-S01, F07-S02, F07-S03, F07-S07, F07-S08)
- [ ] 6 performances manuales registradas
- [ ] Secuencia ingreso RP → tarjeta → confirmar correcta en móvil
- [ ] Formatos de marca correctos: metros (DBF/DNF/DYN) y mm:ss (STA/SPE)
- [ ] Verificación cruzada positiva: organizador · portal · atleta ven los resultados
- [ ] Sistema en estado `EJECUCION` listo para F-08 (flujos de excepción)
