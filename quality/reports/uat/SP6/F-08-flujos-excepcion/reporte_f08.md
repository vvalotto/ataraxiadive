# Reporte de Cierre — Fase F-08: Flujos de Excepción

**Fecha de cierre:** 2026-05-13  
**Branch:** `uat/INC-6.5/F-08-flujos-excepcion`  
**Resultado:** ✅ 8/8 PASS

---

## Resumen Ejecutivo

F-08 validó los flujos de excepción del sistema: BKO con tarjeta roja automática, revisión de tarjeta amarilla y registro de BlancaConPenalizaciones. Todos los escenarios pasaron. Se identificaron y resolvieron 3 defectos (H-08-01/02/03) y 3 mejoras de UX en el portal atleta (M-08-01/02/03).

---

## Resultados por Escenario

| ID | Descripción | Estado |
|----|-------------|--------|
| F08-S01 | BKO de Cuchiarelli en DNF — botón habilitado, tarjeta roja automática | ✅ PASS |
| F08-S02 | Pantalla post-BKO en rojo | ✅ PASS |
| F08-S03 | Grilla organizador: tarjeta roja + motivo "Blackout" visible | ✅ PASS |
| F08-S04 | Quintana DYN — tarjeta amarilla registrada, estado revisión visible | ✅ PASS |
| F08-S05 | Cierre de revisión como Blanca (no admite BlancaConPenalizaciones desde revisión) | ✅ PASS |
| F08-S06 | Resultado DYN Quintana visible con tarjeta Blanca | ✅ PASS |
| F08-S07 | Almada DYN — BlancaConPenalizaciones con 1 penalización (75m → 72m) | ✅ PASS |
| F08-S08 | Desglose de penalización visible en panel organizador: 69.00m + "(72m − 3m)" | ✅ PASS |

---

## Defectos Encontrados y Resueltos

| ID | Descripción | Fix |
|----|-------------|-----|
| H-08-01 | Motivo DQ y RP ausentes en grilla organizador y portal público para tarjeta roja | `eba8e42` + `77b01be` + `ace40df` |
| H-08-02 | Penalizaciones no se mostraban en lenguaje natural (texto crudo) | `b85bf8b` + `4cf2832` |
| H-08-03 | Desglose de marca original vs. deducción no visible en panel organizador | `795fd38` |

---

## Corrección de Dominio Identificada

Durante F08-S05 se verificó que **la revisión de una tarjeta amarilla solo puede cerrarse como Blanca o Roja** — no como BlancaConPenalizaciones. BlancaConPenalizaciones es un estado que se registra al momento del ingreso de la marca, no como resultado de una revisión. El escenario original estaba mal planteado y fue corregido en los artefactos.

---

## Mejoras de UX Resueltas (Portal Atleta)

| ID | Descripción | Fix |
|----|-------------|-----|
| M-08-01 | Badge flotante pisaba botón Salir · nav al pie era inaccesible | `0f4f811` + `0f257e1` |
| M-08-02 | Disciplinas apiladas en "En ejecución" y "Mis resultados" | `4117cc6` + `8ffa799` |
| M-08-03 | Formato de hora en 12h (AM/PM) | `3583d82` |

---

## Commits de la Fase

```
90d53ab test(uat): actualizar artefactos F-08
3583d82 fix(frontend): formato de hora en 24h
8ffa799 fix(frontend): tabs en Mis Resultados con una sola disciplina
4117cc6 feat(frontend): disciplinas por pestañas en Mis Inscripciones y Mis Resultados
0f257e1 fix(frontend): nav del portal atleta a cabecera
0f4f811 fix(frontend): botón Salir al header del AtletaShell
795fd38 fix(frontend): desglose rp_medido en panel organizador [H-08-03]
4cf2832 fix(frontend): tarjeta en portal público en palabras separadas [H-08-02]
b85bf8b fix(resultados): penalizaciones en lenguaje natural [H-08-02]
ace40df fix(competencia): motivo DQ en grilla pública [H-08-01]
77b01be fix(resultados): serializar motivo_dq y RP en tarjeta roja [H-08-01]
eba8e42 fix(resultados): motivo DQ en grilla organizador [H-08-01]
793c263 test(uat): apertura F-08
```

---

## Criterio de Salida — Verificado

- [x] 8/8 escenarios PASS
- [x] BKO genera tarjeta roja automática con MotivoDQ = BKO_SUPERFICIE
- [x] Pantalla post-BKO en rojo
- [x] Tarjeta amarilla cierra como Blanca (dominio verificado)
- [x] BlancaConPenalizaciones registrada correctamente al ingresar RP
- [x] Sistema listo para F-09
