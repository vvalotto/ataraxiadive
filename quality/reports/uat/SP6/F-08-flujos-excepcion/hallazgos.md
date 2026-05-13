# Hallazgos — Fase F-08: Flujos de Excepción

## Defectos

| ID | Escenario | Descripción | Severidad | Pasos para reproducir | Estado | Fix |
|----|-----------|-------------|-----------|----------------------|--------|-----|
| H-08-01 | F08-S03 | Grilla organizador y portal público: (a) falta motivo DQ en texto legible · (b) RP no visible para tarjeta roja · (c) motivo_dq no serializado en router | 🟡 | 1. Registrar BKO · 2. Ver resultados como organizador/portal — motivo y RP ausentes | Resuelto | `eba8e42` + `77b01be` + `ace40df` — motivo_dq en ranking provisional, DTO, router competencia/resultados; RP preservado; FilaResultado y AtletaRow muestran texto legible |

| H-08-02 | F08-S07 | Columna tarjeta en resultados (organizador y portal público) no muestra penalizaciones en lenguaje natural — solo muestra "BlancaConPenalizaciones" como texto crudo o "BLANCA" sin detalle | 🟡 | 1. Registrar performance con BlancaConPenalizaciones · 2. Ver resultados como organizador o portal — sin detalle de infracciones | Resuelto | `b85bf8b` — penalizaciones fluyen desde TarjetaAsignada/grilla, FilaResultado y AtletaRow muestran cada infracción en ámbar |

## Mejoras (fuera de scope UAT)

| ID | Origen | Descripción | Prioridad sugerida |
|----|--------|-------------|-------------------|
| — | — | Sin mejoras aún | — |
