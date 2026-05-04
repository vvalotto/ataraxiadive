# Hallazgos CodeGuard Pendientes — INC-5.6 + SP-ADJ-09
# Para resolver en US de ajuste del próximo incremento (SP-ADJ-10 o similar)
# Registrado: 2026-04-29

## Hallazgos

| ID    | US origen    | Tipo        | Archivo                                          | Detalle                                | Acción sugerida            | Prioridad |
|-------|--------------|-------------|--------------------------------------------------|----------------------------------------|----------------------------|-----------|
| CG-02 | US-5.6.1     | Complexity  | `resultados/domain/services/algoritmo_faas.py`   | `_calcular_puntos` C=11 (umbral ≤10)   | Refactoring: dispatch dict por TipoDisciplina | Media |
| CG-05 | US-ADJ-9.7   | PEP8 F401   | `registro/api/router.py:3`                       | `'os' imported but unused`             | Eliminar `import os`       | Media     |
| CG-01 | US-5.6.1     | PEP8 E501   | `resultados/domain/ports/resultado_puerto.py`    | línea 106 chars                        | `black`                    | Baja      |
| CG-03 | US-5.6.3/4   | PEP8 E501   | `resultados/domain/aggregates/<ranking>.py`      | línea 101 chars                        | `black`                    | Baja      |
| CG-04 | US-ADJ-9.7   | PEP8 E501   | `registro/domain/aggregates/inscripcion.py`      | 2 líneas (106, 102 chars)              | `black`                    | Baja      |

## Criterio para US de ajuste

Los hallazgos E501 (CG-01, CG-03, CG-04) se resuelven en bloque con `black src/` — una
sola US de formato. No requieren revisión de lógica.

CG-05 es un import residual limpio de eliminar — 1 línea.

CG-02 es el único candidato a refactoring real. `_calcular_puntos` maneja distancia,
tiempo y casos borde en una sola función. Una tabla de dispatch por `TipoDisciplina`
reduciría la complejidad a ≤5 por rama. Evaluar como US independiente si el
DesignReviewer también lo señala como CRITICAL.

## Reportes fuente

- `quality/reports/codeguard/INC-5.6-codeguard.txt`
- `quality/reports/codeguard/SP-ADJ-09-codeguard.txt`
