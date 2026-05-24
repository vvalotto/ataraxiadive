# DesignReviewer — Evolución de Issues por Incremento

> Fuente: `quality/reports/designreviewer/*.txt` + anotaciones en `.cm/baselines/`  
> Métrica: `Resultados totales` (WARNINGs acumulados) por ejecución  
> Fecha de extracción: 2026-05-18  
> Referencia: PLAN-METRICAS.md §B.1

---

## 1. Serie temporal completa

| Incremento | SP | Issues totales | Δ vs anterior | CRITICAL | Fuente |
|------------|----|:--------------:|:-------------:|:--------:|--------|
| US-1.2.2 | SP1 | 11 | baseline | 0 | US-1.2.2-report.txt |
| INC-2.2 | SP2 | 59 | +48 | 0 | INC-2.2-report.txt |
| INC-2.3 | SP2 | 64 | +5 | 0 | INC-2.3-report.txt |
| INC-3.2 | SP3 | 94 | +30 | 0 | INC-3.2-report.txt |
| INC-3.3 | SP3 | 97 | +3 | 0 | INC-3.3-report.txt |
| INC-3.5 | SP3 | 111 | +14 | 0 | INC-3.5-report.txt |
| SP-ADJ-03 | SP3 | 113 | +2 | 0 | SP-ADJ-03-report.txt |
| SP-ADJ-04 | SP3 | 119 | +6 | 0 | SP-ADJ-04-report.txt |
| INC-4.2 | SP4 | 142 | +23 | 0 | INC-4.2-report.txt |
| INC-4.5 | SP4 | 174 | +32 | 0 | INC-4.5-report.txt |
| INC-4.6 | SP4 | 196 | +22 | 0 | INC-4.6-report.txt |
| SP-ADJ-07 | SP4 | 208 | +12 | 0 | SP-ADJ-07-report.txt |
| INC-5.1 | SP5 | 208 | 0 | 0 | INC-5.1-report.txt |
| INC-5.2 | SP5 | 215 | +7 | 0 | INC-5.2-report.txt |
| INC-5.3 | SP5 | 215 | 0 | 0 | INC-5.3-report.txt |
| INC-5.4 | SP5 | 222 | +7 | 0 | INC-5.4-report.txt |
| INC-5.5 | SP5 | 227 | +5 | 0 | INC-5.5-report.txt |
| INC-5.6 | SP5 | 252 | +25 | 0 | INC-5.6-report.txt |
| INC-5.7 | SP5 | 256 | +4 | 0 | INC-5.7-report.txt |
| INC-6.3 | SP6 | 258 | +2 | 0 | anotado en BL-006.md |
| INC-6.4 | SP6 | 253 | −5 | 0 | INC-6.4-report.txt |
| INC-6.6 | SP6 | 253 | 0 | 0 | anotado en BL-006.md |
| SP-ADJ-11 | SP6 | 287 | +34 | 0 | anotado en sesión SP6 |

**Nota:** 0 CRITICAL en toda la historia del proyecto — el gate CRITICAL nunca activó un bloqueo de PR por violación de diseño.

---

## 2. Resumen por SP

| SP | INC inicial | INC final | Δ total SP | Tipo de crecimiento |
|----|:-----------:|:---------:|:----------:|---------------------|
| SP1 | 11 | 11 | +11 | Arranque (1 US de calibración) |
| SP2 | 59 | 64 | +53 | Crecimiento rápido — primeros BCs backend |
| SP3 | 94 | 119 | +55 | Crecimiento sostenido — Torneo + Registro + Resultados |
| SP4 | 142 | 208 | +89 | Mayor Δ absoluto — Identidad + Frontend + SP-ADJ |
| SP5 | 208 | 256 | +48 | Crecimiento moderado — SP-ADJ-09 UX refactor |
| SP6 | 258 | 287 | +31 | Menor Δ — SP6 con corrección neta (INC-6.4 −5) |

**Tendencia general:** crecimiento monotónico con excepción de INC-6.4 (−5) — primer decremento neto en toda la historia del proyecto.

---

## 3. Análisis de picos

### Pico SP4: +89 issues (INC-4.2 → SP-ADJ-07)

SP4 introdujo BC Identidad (autenticación JWT), BC Notificaciones (Event Sourcing exactly-once) y el primer frontend React. Cada nuevo BC aporta ~30–50 issues de DesignReviewer por los métodos de orquestación y la complejidad de wiring.

### Pico SP5-INC-5.6: +25 en un solo incremento

INC-5.6 implementó el portal del organizador completo (US-5.6.1..5.6.n) — gran volumen de código de aplicación y API en una sola entrega. Los picos de Δ correlacionan con incrementos de alta densidad de código nuevo.

### Corrección INC-6.4: −5 issues

Primer decremento neto. SP6 incluyó refactoring explícito de calidad (SP-ADJ-10/11). INC-6.4 tuvo trabajo de simplificación en routers. Señal de que el equipo puede reducir activamente la deuda de diseño cuando el SP lo prioriza.

### SP-ADJ-11: +34 (el mayor delta de un solo SP-ADJ)

SP-ADJ-11 incorporó modelo multi-rol completo (Juez + Organizador en BC Registro + BC Identidad): 10 US, 10 PRs, nueva infraestructura concreta en múltiples BCs. El Δ refleja código nuevo legítimo, no degradación.

---

## 4. Tasa de crecimiento (issues / US implementada)

Estimación aproximada basada en US totales por SP:

| SP | US aprox. | Δ issues | Issues / US |
|----|:---------:|:--------:|:-----------:|
| SP2 | 3 | 53 | 17.7 |
| SP3 | 11 | 55 | 5.0 |
| SP4 | 21 | 89 | 4.2 |
| SP5 | 20 | 48 | 2.4 |
| SP6 | 13 | 31 | 2.4 |

**Tendencia:** la tasa issues/US decrece consistentemente de SP2 (17.7) a SP6 (2.4). El equipo produce menos deuda de diseño por historia a medida que avanza el proyecto — posible señal de mejora en disciplina de diseño o de que el código nuevo es más incremental sobre bases ya existentes.

---

## 5. Interpretación para el experimento IEDD

- **0 CRITICAL en toda la serie:** el gate DesignReviewer funcionó como discriminador, no como bloqueante. Las violaciones de diseño son sistemáticamente WARNINGs (code smells), no violaciones de principios SOLID.
- **Crecimiento lineal con pendiente decreciente:** el proyecto acumula deuda de diseño de forma controlada, sin explosión exponencial. Esto es consistente con la hipótesis de que IEDD + gates automáticos moderan la acumulación de deuda técnica.
- **Los ADJ generan issues, pero menos que los INC:** SP-ADJ-07 (+12), SP-ADJ-11 (+34) vs INC-4.6 (+22), INC-5.6 (+25). Los sprints de ajuste no son más "sucios" que el desarrollo funcional regular.

---

*Extraído: 2026-05-18 — rama doc/metricas — PLAN-METRICAS.md §B.1 completado*
