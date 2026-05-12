# Escenarios — Fase F-06: Inicio de Ejecución

## Criterio de Entrada

- [x] F-05 cerrada: torneo en estado `PREPARACION`
- [x] Grilla generada para las 5 disciplinas (DBF/DNF/DYN/STA/SPE)
- [x] Jueces asignados por andarivel en todas las disciplinas
- [x] Portal juez muestra asignaciones correctas

## Escenarios

| ID | Actor | Dispositivo | Acción | Resultado esperado | Resultado real | Estado | Hallazgo |
|----|-------|-------------|--------|--------------------|----------------|--------|----------|
| F06-S01 | Organizador | Desktop | Iniciar ejecución del torneo desde panel | Estado pasa a `EJECUCION` · sin errores | Estado EJECUCION · mensaje "Falta cerrar disciplinas" esperado (bloquea PREMIACION, no EJECUCION) | ✅ PASS | — |
| F06-S02 | Portal (visitante) | Cualquier | Refrescar `/portalapnea` tras EJECUCION | Torneo muestra "En ejecución" · botón/link "Ver en vivo" o equivalente | Correcto | ✅ PASS | H-06-01 |
| F06-S03 | Portal (visitante) | Cualquier | Acceder a página pública del torneo | Grilla con tabs por disciplina · podios (vacíos al inicio) | Grilla con tabs correcta · podios no visible sin resultados (comportamiento aceptado) | ✅ PASS | — |
| F06-S04 | Juez 1 | Móvil | Login y ver grilla de DBF | Primer atleta de la grilla aparece primero (mayor prioridad de estado) | Cuchiarelli aparece primero — correcto | ✅ PASS | — |
| F06-S05 | Atleta | Móvil/Tablet | Login y ver inicio | Disciplinas en curso ordenadas (próxima → posteriores → realizadas) | Correcto | ✅ PASS | — |

## Criterio de Salida

- [x] F06-S01 ✅: torneo en estado `EJECUCION`
- [x] F06-S02 ✅: portal público muestra torneo en ejecución
- [x] F06-S03 ✅: página pública del torneo accesible con grilla por disciplina
- [x] F06-S04 ✅: juez ve grilla de DBF con atletas ordenados
- [x] F06-S05 ✅: atleta ve disciplinas en curso ordenadas
- [x] Todos los escenarios 🔴 en PASS
- [x] Sistema listo para F-07 (ejecución de performances)
