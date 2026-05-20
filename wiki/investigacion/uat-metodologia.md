---
title: "UAT Controlado — Metodología"
type: investigacion
last_updated: "2026-05-20"
sources:
  - docs/iedd/UAT-POLITICA-CONTROLADA.md
---

# UAT Controlado — Metodología

Política y estrategia del proceso de User Acceptance Testing en AtaraxiaDive. Desarrollada a partir de la experiencia acumulada en SP1..SP5.

> **Documento fuente:** `docs/iedd/UAT-POLITICA-CONTROLADA.md` (actualizado 2026-05-11)
> **Referencias:** HITO-20, HITO-28, HITO-9

---

## Principio fundacional

> El UAT no valida roles — valida **procesos**.

La unidad de organización del UAT es la **fase del ciclo de vida del sistema**, no el actor que la ejecuta. Testear por rol en forma aislada oculta bugs de integración entre estados y actores.

En AtaraxiaDive el ciclo es:
```
CREADO → INSCRIPCION_ABIERTA → PREPARACION → EJECUCION → PREMIACION → CERRADO
```

Las **transiciones de estado** son puntos de verificación obligatorios.

---

## Principios de la estrategia

| Principio | Descripción |
|-----------|-------------|
| Portal público desde el inicio | Cualquier superficie pública activa desde la primera fase — un bug tardío cuesta más |
| Registro de usuarios como parte del flujo | Onboarding y permisos se validan, no se asumen |
| Datos en dos etapas | Seed-A (usuarios) antes del UAT; Seed-B+ (datos de negocio) generados por los escenarios |
| Verificación cruzada de roles | Toda acción significativa se verifica desde al menos otro rol |
| Flujos de excepción dentro de la ejecución | DNS, BKO, tarjeta amarilla son escenarios de la fase de ejecución, no una fase separada |
| Dispositivo por rol real | Juez en móvil, Organizador en desktop, Atleta en móvil/tablet |
| Criterio de bloqueo explícito | Definido antes de iniciar el UAT |

### Dispositivos por rol

| Rol | Dispositivo | Razón |
|-----|-------------|-------|
| Organizador | Desktop / laptop | Gestión de torneo, tablas, múltiples tabs |
| Juez | Móvil (iPhone / Android) | Contexto real en pileta, una mano libre |
| Atleta | Móvil o tablet | Consulta en sitio |
| Portal público | Cualquier dispositivo | Sin restricción |

### Criterio de bloqueo

| Severidad | Definición | Acción |
|-----------|-----------|--------|
| 🔴 Bloqueante | Impide continuar la fase · pérdida de datos · flujo roto · resultado incorrecto | Detener · registrar · no avanzar |
| 🟡 Observación | Incorrecto pero el flujo puede continuar | Registrar · continuar UAT |
| ⚪ Estético | Texto, color, alineación | Registrar para corrección posterior |

---

## Proceso por fase (5 pasos)

```
1. PREPARACIÓN      — verificar criterio de entrada, crear seed, documentar escenarios
2. EJECUCIÓN MANUAL — correr seed, ejecutar escenarios, registrar PASS/FAIL
3. REGISTRO         — completar hallazgos.md con cada FAIL
4. VIBE CODING      — resolver hallazgos 🔴 antes de continuar; re-ejecutar afectados
5. CIERRE           — verificar criterio de salida, commit de cierre, avanzar
```

### Criterio de entrada (precondición de fase)
- Fases anteriores cerradas con criterio de salida cumplido
- Seed de fase anterior ejecutado exitosamente
- Entorno en el estado esperado (verificar, no asumir)

### Criterio de salida (postcondición de fase)
- Todos los escenarios 🔴 en PASS
- Hallazgos 🔴 resueltos y re-verificados
- Sistema en el estado esperado para la siguiente fase

---

## Estructura de artefactos

```
quality/reports/uat/<SP>/
├── F-NN-<nombre>/
│   ├── seed_fNN_<nombre>.py    ← script de seed si aplica
│   ├── escenarios.md           ← tabla de escenarios con PASS/FAIL
│   ├── hallazgos.md            ← defectos y mejoras encontradas
│   └── reporte_fNN.md          ← criterio entrada/salida, métricas
└── REPORTE-FINAL-<INC>.md      ← consolidado de todas las fases
```

**Branch por fase:** `uat/INC-X.Y/F-NN-nombre` — creado desde `develop`, mergeado al cerrar.

---

## Vibe Coding en UAT

Resolución ágil de defectos **durante** la sesión sin abrir US formal.

| Alcance del fix | Proceso |
|-----------------|---------|
| Solo frontend (componente, estilo, texto, formato) | Vibe coding en UAT |
| Backend sin cambio de dominio (query, serialización, endpoint) | Vibe coding con test de smoke |
| Cambio en `domain/` o `application/` | US-IEDD dentro del mismo INC |
| Nuevo comportamiento no planificado | US-IEDD en INC siguiente |

> Ver HITO-28 para el análisis de la tensión UAT vibe coding vs. pipeline formal.

---

## Datos reales como oráculo

Cuando el UAT usa datos de una competencia real (ej. Buenos Aires 2025), los resultados conocidos actúan como **oráculo de verdad**: el sistema debe producir exactamente esos rankings, marcas y podios.

Esta propiedad elimina la ambigüedad del criterio de aceptación.

> Ver HITO-17 sobre datos reales como oráculo del dominio.

---

## Límites del proceso

Este proceso **no reemplaza**:
- Tests unitarios y de integración (validan invariantes de dominio)
- DesignReviewer al cierre de cada INC (valida la arquitectura)
- ArchitectAnalyst al cierre de SP (valida tendencias estructurales)

Es una capa de validación funcional E2E que **complementa** los quality gates automáticos.

---

## Relaciones

- Ver [[iedd-marco-conceptual]] para el marco metodológico que da contexto al UAT.
- Ver [[iedd-hipotesis-experimento]] para el rol del UAT como pieza del experimento.
- Template de US que alimenta las correcciones detectadas en UAT: `docs/iedd/US-IEDD-template.md`.
