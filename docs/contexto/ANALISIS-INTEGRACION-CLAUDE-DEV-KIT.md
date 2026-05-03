# Análisis e Integración: Claude Dev Kit en el Framework de Desarrollo con IA

> Estado documental: histórico
> Análisis técnico de integración realizado en Marzo 2026.
> Conservado como evidencia del fundamento de la cadena de desarrollo automático.
> Fuente vigente relacionada: `.claude/skills/implement-us/`, `docs/plans/WORKFLOW-DESARROLLO.md`

**Fecha:** Marzo 2026
**Contexto:** Integración de `claude-dev-kitc` v1.3.0 en el entorno de trabajo definido

---

## 1. ¿Qué es Claude Dev Kit? (Síntesis del análisis)

Claude Dev Kit es un framework que vos mismo construiste, instalable en proyectos Python,
que **automatiza el ciclo completo de implementación de una Historia de Usuario** a través
de Claude Code. Opera en 10 fases estructuradas:

| Fase | Nombre              | Gate de salida              |
|------|---------------------|-----------------------------|
| 0    | Validación          | Automático                  |
| 1    | BDD (Gherkin)       | **STOP — aprobación humana**|
| 2    | Plan de impl.       | **STOP — aprobación humana**|
| 3    | Implementación      | Por tarea (configurable)    |
| 4    | Tests unitarios     | Automático (tests en verde) |
| 5    | Tests integración   | Automático (tests en verde) |
| 6    | Validación BDD      | Automático (escenarios ok)  |
| 7    | Quality Gates       | Automático (métricas ok)    |
| 8    | Documentación       | **STOP — aprobación humana**|
| 9    | Reporte final       | Automático                  |

Características clave que destacan del análisis:
- **Agnóstico de dominio** con perfiles por stack (PyQt-MVC, FastAPI, Flask-REST, Flask-WebApp, Generic)
- **Sistema de tracking de tiempo** automático por fase y tarea (Python puro, persistente en `.claude/tracking/`)
- **Quality gates** con Pylint, complejidad ciclomática e índice de mantenibilidad
- **Templates parametrizados** con variables y snippets por perfil
- **Instalador** que copia el kit al `.claude/` del proyecto del usuario
- **v1.3.0, 107 tests, 99% cobertura** — está en producción, no es un prototipo

---

## 2. Diagnóstico: ¿Dónde encaja en el entorno de trabajo?

La pregunta central es: ¿Claude Dev Kit reemplaza al framework de CM, lo complementa,
o colisiona con él?

**Respuesta: lo complementa en una capa diferente.** Operan en distintos niveles
de abstracción:

```
┌──────────────────────────────────────────────────────────────────┐
│           NIVEL ESTRATÉGICO — Claude Cowork                       │
│                                                                   │
│  Visión del producto · ADRs · RFCs · Líneas Base · Trazabilidad   │
│  "¿Qué construimos? ¿Por qué? ¿Qué decidimos?"                   │
└────────────────────────────┬─────────────────────────────────────┘
                             │  feed: US aprobadas, ADRs activos
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│           NIVEL TÁCTICO — Claude Dev Kit + Claude Code            │
│                                                                   │
│  /implement-us US-NNN  →  10 fases → código + tests + docs        │
│  "¿Cómo implementamos esta US con la mayor calidad posible?"      │
└────────────────────────────┬─────────────────────────────────────┘
                             │  feed: reportes, métricas, artefactos
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│           NIVEL ESTRUCTURAL — Repositorio Git                     │
│                                                                   │
│  Memoria del producto: docs/ + .cm/ + src/ + tests/               │
└──────────────────────────────────────────────────────────────────┘
```

Los tres niveles se alimentan mutuamente. No se reemplazan.

---

## 3. Puntos de integración concretos

### 3.1 US como enlace central

El punto de conexión más natural es la **Historia de Usuario**:

```
Cowork escribe      Code ejecuta         Cowork registra
──────────────   ──────────────────   ─────────────────────
docs/requirements  /implement-us US-NNN  docs/traceability/
user-stories.md  ─────────────────────►  matrix.md actualizada
                  genera:                con US-NNN como
                  · BDD scenarios        implementada +
                  · plan.md              referencia al reporte
                  · código
                  · tests
                  · quality report
                  · final report
```

### 3.2 ADRs → Perfil del kit

Una decisión arquitectónica capturada en un ADR determina qué perfil usar:

```
ADR-001 + ADR-005 + ADR-006: "FastAPI + hexagonal DDD BC-first"
         → config del kit: perfil "hexagonal-ddd-bc"
         → CLAUDE.md referencia a los ADRs
         → /implement-us respeta esa arquitectura automáticamente
```

El ADR es la **fuente de verdad** que justifica la elección del perfil.
El perfil es la **operacionalización** del ADR.

### 3.3 Quality Gates → Deuda técnica observable

Los reportes de la Fase 7 (`quality/reports/US-NNN-quality.json`) son datos duros
que alimentan el registro de deuda técnica en las líneas base:

```
BL-NNN-nombre.md  ──►  sección "Deuda técnica conocida"
                        "Según quality reports: cobertura promedio 87%,
                         3 módulos con complejidad > 8"
```

### 3.4 Tracking de tiempo → Estimación en planificación

El tiempo registrado por el kit (`.claude/tracking/*.json`) acumula datos empíricos
que retroalimentan la estimación de futuras US. Cowork puede consultarlos al planificar
nuevos incrementos.

### 3.5 Final Report → Traceability Matrix

Cada Fase 9 genera `docs/reports/US-NNN-report.md`. La matriz de trazabilidad
en Cowork referencia ese reporte como evidencia de implementación:

```
| US-003 | src/domain/tarea.py | tests/unit/test_tarea.py | docs/reports/US-003-report.md |
```

---

## 4. Tensiones y cómo resolverlas

### Tensión 1: Dos CLAUDE.md

El instalador del kit genera un `CLAUDE.md`. Nuestro framework también define uno.

**Resolución:** Un único `CLAUDE.md` con dos secciones bien delimitadas:

```markdown
## Convenciones del proyecto [mantenido por Cowork]
...

## Claude Dev Kit [instalado por el kit, no editar manualmente]
...
```

El instalador debe tener un flag `--merge-claude-md` para integrar en vez de reemplazar.

### Tensión 2: Estructura de `docs/` compartida

El kit genera artefactos en `docs/plans/`, `docs/reports/`, `quality/reports/`.
Nuestro framework tiene `docs/requirements/`, `docs/design/`, `docs/adr/`.

**Resolución:** Son namespaces que no colisionan. La estructura unificada sería:

```
docs/
├── adr/              ← Cowork (decisiones)
├── requirements/     ← Cowork (visión del producto)
├── design/           ← Cowork (diseño)
├── specs/            ← Cowork (US-IEDD, Capa 3 IEDD — dividido en sp1/, sp2/, …)
├── traceability/     ← Cowork (matriz)
├── plans/            ← Kit (plan técnico por US, fase 2 — dividido en sp1/, sp2/, …)
└── reports/          ← Kit (reporte final por US, fase 9)
quality/
└── reports/          ← Kit (quality gates, fase 7)
```

### Tensión 3: Python-only vs. framework agnóstico

El kit actualmente solo soporta Python. Nuestro framework de CM es agnóstico.

**Resolución:** Ningún problema real hoy. Para el proyecto sandbox Python, el kit
aplica al 100%. Si en el futuro se agregan otros lenguajes, el CM framework sigue
funcionando y el kit se puede extender (ya está previsto en el roadmap: TypeScript).

### Tensión 4: Tracking del kit vs. líneas base de CM

El kit trackea tiempo por US y fase. Las líneas base de CM registran el estado a
nivel de producto. Son granularidades distintas.

**Resolución:** No integrar forzadamente. El tracking del kit es operativo (micro).
Las líneas base son estratégicas (macro). Se referencian pero no se fusionan.

---

## 5. Propuesta de integración: Flujo completo

El flujo integrado de una iteración completa quedaría así:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PLANIFICACIÓN (Cowork)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Cowork revisa/actualiza docs/requirements/user-stories.md
2. Si la US requiere decisión arquitectónica → Cowork crea ADR
3. Cowork verifica que el perfil del kit es coherente con los ADRs activos
4. [Opcional] Cowork crea un RFC si la US modifica requisitos previos

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
IMPLEMENTACIÓN (Claude Code + Kit)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
5. Code: git checkout -b feature/US-NNN-nombre
6. Code: /implement-us US-NNN
   → Fase 0: validación automática
   → Fase 1: BDD — Victor aprueba escenarios
   → Fase 2: Plan — Victor aprueba plan
   → Fase 3-6: implementación + tests automáticos
   → Fase 7: quality gates automáticos
   → Fase 8: documentación — Victor revisa
   → Fase 9: reporte final generado
7. Code: commits con referencias a US-NNN y al ADR si aplica
8. Code: merge a main / PR

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
REGISTRO (Cowork)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
9. Cowork actualiza docs/traceability/matrix.md con US-NNN
10. Cowork actualiza CHANGELOG.md sección [Unreleased]
11. Si fue la última US del incremento → Cowork establece nueva baseline BL-NNN
    (incluye referencia al quality report de la US)
```

---

## 6. Cambios necesarios en los artefactos del framework

### 6.1 CLAUDE.md (enriquecimiento)

Agregar una sección sobre el kit instalado:

```markdown
## Claude Dev Kit (instalado)

Este proyecto tiene Claude Dev Kit v1.3.0 instalado en `.claude/`.
Perfil activo: hexagonal-ddd-bc
ADRs que justifican el perfil: ADR-001, ADR-005, ADR-006

Para implementar una US:
  /implement-us US-NNN

Artefactos generados por el kit (no editar manualmente):
  docs/plans/spN/    — planes de implementación (Fase 2)
  docs/reports/      — reportes finales (Fase 9)
  quality/reports/   — quality gates (Fase 7)
  .claude/tracking/  — datos de tiempo (no commitear)
```

### 6.2 .cm/cm-plan.md (nuevos CIs)

Agregar los artefactos del kit como CIs:

| ID       | Descripción              | Ubicación                        | Propietario |
|----------|--------------------------|----------------------------------|-------------|
| `PLAN-`  | Planes de implementación | `docs/plans/spN/US-NNN-plan.md`  | Code/Kit    |
| `REP-`   | Reportes finales de US   | `docs/reports/US-NNN-report.md`  | Code/Kit    |
| `QG-`    | Quality gate reports     | `quality/reports/US-NNN-*.json`  | Code/Kit    |

### 6.3 Estructura del repositorio (actualizada)

```
/mi-proyecto/
├── CLAUDE.md                    ← Cowork + Kit (secciones delimitadas)
├── README.md
├── CHANGELOG.md
│
├── .cm/                         ← Cowork: CM estratégico
│   ├── cm-plan.md
│   ├── baselines/
│   └── changes/
│
├── .claude/                     ← Kit: instalado por claude-dev-kit
│   ├── skills/implement-us/
│   ├── templates/
│   ├── tracking/
│   └── settings.json
│
├── docs/
│   ├── adr/                     ← Cowork
│   ├── requirements/            ← Cowork
│   ├── design/                  ← Cowork
│   ├── traceability/            ← Cowork
│   ├── plans/                   ← Kit (Fase 2)
│   └── reports/                 ← Kit (Fase 9)
│
├── quality/
│   └── reports/                 ← Kit (Fase 7)
│
├── src/                         ← Code/Kit
└── tests/                       ← Code/Kit
```

---

## 7. Pasos sugeridos para arrancar

**Paso 1** — Instalar claude-dev-kit en el proyecto sandbox:
```bash
cd ~/ruta/al/sandbox
python ~/.claude-dev-kit/install/installer.py --profile generic-python
```

**Paso 2** — Enriquecer el CLAUDE.md generado con las secciones de CM
(Cowork puede hacer esto con los templates ya definidos).

**Paso 3** — Escribir la primera US real en `docs/requirements/user-stories.md`
y ejecutar `/implement-us US-001` para validar el flujo de punta a punta.

**Paso 4** — Revisar qué generó el kit y cómo se integra con la estructura de CM
(ajustar lo que sea necesario antes de establecer BL-001).

**Paso 5** — Establecer BL-001-inception con el estado post primer `/implement-us`.

---

## 8. Valoración general

Claude Dev Kit resuelve con mucha solidez el problema de **cómo implementar**
una US de manera consistente, con calidad verificada y documentada. Es el motor
de ejecución que el framework de CM necesitaba en la capa táctica.

Lo que el framework de CM aporta que el kit no tiene es:
- La **historia de las decisiones** (ADRs)
- El **control de cambios a nivel de producto** (RFCs)
- La **memoria consolidada de incrementos** (baselines)
- La **trazabilidad cruzada** entre requisitos, código y tests a nivel de proyecto

Son capas complementarias. Juntas cubren desde la decisión estratégica hasta
el reporte de calidad de cada línea de código.

---

*Análisis generado con Claude Cowork — Marzo 2026*
