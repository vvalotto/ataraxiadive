# Escenarios — Fase F-08: Flujos de Excepción

**Fecha de apertura:** 2026-05-13  
**Branch:** `uat/INC-6.5/F-08-flujos-excepcion`

---

## Criterio de Entrada

- [x] F-07 cerrada con 10/10 PASS (PR #175 mergeado a develop)
- [x] 6 performances manuales registradas correctamente en el sistema
- [x] Torneo en estado `EJECUCION`
- [x] Jueces logueados y con asignaciones activas

---

## Atletas del Escenario

| Atleta | Disciplina | Andarivel | Juez | AP | Escenario |
|--------|-----------|:---------:|------|-----|-----------|
| Sebastián Quintana | DNF | 1 | Juez 1 | 25m | BKO (F08-S01/S02/S03) |
| Ignacio Saslavsky | DYN | 2 | Juez 2 | 60m | Tarjeta amarilla → blanca con penalización (F08-S04/S05/S06) |

> **Nota:** Quintana y Fardi ya tienen resultados en DNF (Fardi: 41.05m blanca). Quintana está en andarivel 1 → Juez 1.
> Saslavsky (DYN, andarivel 2) → Juez 2. Una penalización de 1 infracción descuenta 3m → RP final = RP − 3m.

---

## Escenarios

| ID | Actor | Dispositivo | Acción | Resultado esperado | Resultado real | Estado | Hallazgo |
|----|-------|-------------|--------|--------------------|----------------|--------|----------|
| F08-S01 | Juez 1 (móvil) | iPhone | Abrir grilla DNF · seleccionar Sebastián Quintana (andarivel 1) · avanzar al paso de ingreso · marcar BKO con botón "Confirmar BKO" | Botón "Confirmar BKO" **habilitado** (MUX-04 resuelto) · al confirmar: performance queda con tarjeta **roja** automática · MotivoDQ = `BKO_SUPERFICIE` | | ⬜ PENDIENTE | — |
| F08-S02 | Juez 1 (móvil) | iPhone | Verificar pantalla de resultado post-BKO | Pantalla de completado muestra color **rojo** (no verde) · mensaje indica DQ/BKO | | ⬜ PENDIENTE | — |
| F08-S03 | Organizador | Desktop | Ver grilla DNF · verificar fila de Sebastián Quintana | Tarjeta roja visible · DQ con motivo `BKO_SUPERFICIE` en la columna correspondiente | | ⬜ PENDIENTE | — |
| F08-S04 | Juez 2 (móvil) | iPhone | Abrir grilla DYN · seleccionar Ignacio Saslavsky (andarivel 2) · ingresar RP = 54m · asignar **tarjeta amarilla** | Performance queda en estado "revisión" · la fila del atleta muestra estado pendiente de revisión en la grilla del juez | | ⬜ PENDIENTE | — |
| F08-S05 | Juez 2 (móvil) | iPhone | Cerrar revisión de tarjeta amarilla de Saslavsky como **blanca con penalización** · ingresar 1 penalización (3m de deducción) | Performance válida · RP final = 54 − 3 = **51m** · tarjeta blanca con penalización registrada | | ⬜ PENDIENTE | — |
| F08-S06 | Organizador | Desktop | Ver resultados DYN · verificar Ignacio Saslavsky | RP = 51m visible · aparece en ranking DYN SENIOR MASC · tarjeta blanca con penalización indicada | | ⬜ PENDIENTE | — |

---

## Verificación Cruzada

| Punto | Actor | Qué verificar |
|-------|-------|---------------|
| Post F08-S01 | Portal (visitante) | Si la UI pública expone estado de ejecución, verificar que no hay errores al consultar DNF |
| Post F08-S05 | Organizador | RP ajustado de Saslavsky visible (51m) · ranking actualizado |

---

## Criterio de Salida

- [ ] Todos los escenarios 🔴 en PASS
- [ ] BKO genera tarjeta roja automática con MotivoDQ = BKO_SUPERFICIE (MUX-04 verificado)
- [ ] Pantalla post-BKO muestra color rojo (MUX-05 verificado)
- [ ] Tarjeta amarilla cierra correctamente como blanca con penalización con RP ajustado
- [ ] Sistema listo para F-09 (resultados completos y premiación)
