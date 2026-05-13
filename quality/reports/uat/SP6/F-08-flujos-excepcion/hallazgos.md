# Hallazgos — Fase F-08: Flujos de Excepción

## Defectos

| ID | Escenario | Descripción | Severidad | Pasos para reproducir | Estado | Fix |
|----|-----------|-------------|-----------|----------------------|--------|-----|
| H-08-01 | F08-S03 | Grilla organizador y portal público: (a) falta motivo DQ en texto legible · (b) RP no visible para tarjeta roja · (c) motivo_dq no serializado en router | 🟡 | 1. Registrar BKO · 2. Ver resultados como organizador/portal — motivo y RP ausentes | Resuelto | `eba8e42` + `77b01be` + `ace40df` — motivo_dq en ranking provisional, DTO, router competencia/resultados; RP preservado; FilaResultado y AtletaRow muestran texto legible |

| H-08-02 | F08-S07 | Columna tarjeta en resultados (organizador y portal público) no muestra penalizaciones en lenguaje natural — solo muestra "BlancaConPenalizaciones" como texto crudo o "BLANCA" sin detalle | 🟡 | 1. Registrar performance con BlancaConPenalizaciones · 2. Ver resultados como organizador o portal — sin detalle de infracciones | Resuelto | `b85bf8b` — penalizaciones fluyen desde TarjetaAsignada/grilla, FilaResultado y AtletaRow muestran cada infracción en ámbar |
| H-08-03 | F08-S08 | Panel organizador muestra RP final (69m) sin indicar que hubo deducción — no queda claro que la marca original era 72m | 🟡 | 1. Registrar BlancaConPenalizaciones con RP=75m y 1 penalización · 2. Ver resultados — solo se ve 72m sin contexto | Resuelto | `795fd38` — rp_medido propagado por todo el pipeline; FilaResultado muestra desglose "(72m − 3m)" debajo del RP final |

## Mejoras (fuera de scope UAT)

| ID | Origen | Descripción | Estado |
|----|--------|-------------|--------|
| M-08-01 | Sesión F-08 portal atleta | Badge "Backend online" flotante se pisaba con botón Salir · menú de navegación en pie de página dificultaba acceso | Resuelto — `0f4f811` + `0f257e1`: badge excluido del portal atleta; nav movida a la cabecera sticky |
| M-08-02 | Sesión F-08 portal atleta | Disciplinas de "En ejecución" y "Mis resultados" se mostraban apiladas — sin posibilidad de navegar entre ellas | Resuelto — `4117cc6` + `8ffa799`: pestañas de disciplina en ambas secciones |
| M-08-03 | Sesión F-08 portal atleta | Formato de hora en 12h (AM/PM) en portal atleta y tabla organizador | Resuelto — `3583d82`: `hour12: false` en `formatHora` y `toLocaleTimeString` |
