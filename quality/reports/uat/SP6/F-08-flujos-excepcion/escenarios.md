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
| Ezequiel Cuchiarelli | DNF | 1 | Juez 1 | 25m | BKO (F08-S01/S02/S03) |
| Sebastián Quintana | DYN | — | Juez 2 | — | Tarjeta amarilla → blanca con penalización (F08-S04/S05/S06) |

> **Nota:** Cuchiarelli ya tiene DNS en DBF (F-07) pero no en DNF — válido para BKO.
> Saslavsky no estaba en la lista de DYN del juez — se usa Quintana. Una penalización de 1 infracción descuenta 3m → RP final = RP − 3m.

---

## Escenarios

| ID | Actor | Dispositivo | Acción | Resultado esperado | Resultado real | Estado | Hallazgo |
|----|-------|-------------|--------|--------------------|----------------|--------|----------|
| F08-S01 | Juez 1 (móvil) | iPhone | Abrir grilla DNF · seleccionar Ezequiel Cuchiarelli (andarivel 1) · avanzar al paso de ingreso · marcar BKO con botón "Confirmar BKO" | Botón "Confirmar BKO" **habilitado** (MUX-04 resuelto) · al confirmar: performance queda con tarjeta **roja** automática · MotivoDQ = `BKO_SUPERFICIE` | Botón habilitado · tarjeta roja · pide confirmación de distancia recorrida antes del BKO | ✅ PASS | — |
| F08-S02 | Juez 1 (móvil) | iPhone | Verificar pantalla de resultado post-BKO | Pantalla de completado muestra color **rojo** (no verde) · mensaje indica DQ/BKO | Pantalla roja correcta | ✅ PASS | — |
| F08-S03 | Organizador | Desktop | Ver grilla DNF · verificar fila de Ezequiel Cuchiarelli | Tarjeta roja visible · DQ con motivo `BKO_SUPERFICIE` en la columna correspondiente | Tarjeta roja · RP en rojo · motivo "Blackout" visible | ✅ PASS | H-08-01 resuelto |
| F08-S04 | Juez 2 (móvil) | iPhone | Abrir grilla DYN · seleccionar Sebastián Quintana · ingresar RP · asignar **tarjeta amarilla** | Performance queda en estado "revisión" · la fila del atleta muestra estado pendiente de revisión en la grilla del juez | Estado "revisión" visible en grilla organizador y portal público | ✅ PASS | — |
| F08-S05 | Juez 2 (móvil) | iPhone | Cerrar revisión de tarjeta amarilla de Quintana como **blanca** | Performance válida · tarjeta blanca registrada · RP original mantenido | Tarjeta blanca registrada correctamente | ✅ PASS | — |
| F08-S06 | Organizador | Desktop | Ver resultados DYN · verificar Sebastián Quintana | RP visible · aparece en ranking DYN SENIOR MASC · tarjeta blanca indicada | RP y tarjeta Blanca correctos | ✅ PASS | — |
| F08-S07 | Juez 2 (móvil) | iPhone | Mauro Almada DYN · ingresar RP=75m · aplicar **1 penalización** al momento de ingreso de marca | Performance válida · RP final = 72m · tarjeta blanca con penalización registrada | RP final = 72m · BlancaConPenalizaciones registrada | ✅ PASS | H-08-02 resuelto |
| F08-S08 | Organizador | Desktop | Ver resultados DYN · verificar atleta con penalización | RP ajustado (−3m) visible · tarjeta "BlancaConPenalizaciones" o equivalente indicada | | ⬜ PENDIENTE | — |

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
- [ ] Tarjeta amarilla cierra correctamente como Blanca (revisión solo admite Blanca o Roja)
- [ ] BlancaConPenalizaciones registrada correctamente en flujo normal de ingreso de RP con penalización
- [ ] Sistema listo para F-09 (resultados completos y premiación)
