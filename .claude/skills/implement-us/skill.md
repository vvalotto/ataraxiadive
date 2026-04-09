# Skill: implement-us

**Nombre del comando:** `/implement-us`

**Descripción:** Implementador asistido de Historias de Usuario siguiendo el patrón arquitectónico configurado para el proyecto.

**Arquitectura:** Orquestador modular que delega cada fase a un agente especializado.

---

## Variables Disponibles

Este skill utiliza las siguientes variables definidas en `config.json` y personalizables mediante perfiles en `customizations/`:

| Variable | Descripción | Valor en AtaraxiaDive |
|----------|-------------|----------------------|
| `{ARCHITECTURE_PATTERN}` | Patrón arquitectónico del proyecto | `hexagonal-ddd-bc` |
| `{COMPONENT_TYPE}` | Tipo de componente DDD | `AggregateRoot`, `ValueObject`, `DomainEvent`, `Port`, `CommandHandler`, `QueryHandler`, `Repository`, `ApiRouter` |
| `{COMPONENT_PATH}` | Ruta base por tipo de componente | `src/{bc}/domain/aggregates/`, `src/{bc}/domain/value_objects/`, etc. (ver `hexagonal-ddd-bc.json`) |
| `{TEST_FRAMEWORK}` | Framework de testing | `pytest + httpx + pytest-bdd` |
| `{PROJECT_ROOT}` | Raíz del código fuente | `src/` |
| `{PRODUCT}` | Bounded Context activo | `competencia`, `torneo`, `registro`, `resultados`, `identidad`, `notificaciones` |

**Perfil activo:** `hexagonal-ddd-bc`
**Customización proyecto:** `.claude/skills/implement-us/customizations/hexagonal-ddd-bc.json`
**Contexto obligatorio Fase 0:** `docs/contexto/ATARAXIADIVE-CONTEXT.md`

### Cómo se Resuelven las Variables

Las variables se resuelven en el siguiente orden de prioridad:

1. **Perfil de customización** (`.claude/skills/implement-us/customizations/hexagonal-ddd-bc.json`)
2. **Configuración base** (`.claude/skills/implement-us/config.json`)
3. **Valores por defecto**

---

## Propósito

Este skill guía paso a paso la implementación de una Historia de Usuario (US) en cualquier proyecto Python, asegurando:

- Adherencia a la arquitectura configurada para el proyecto
- Generación de escenarios BDD
- Implementación completa según el patrón arquitectónico
- Tests unitarios y de integración
- Validación de quality gates
- Documentación y reporte final

El skill es **framework-agnostic** y se adapta automáticamente según el perfil instalado:
- **PyQt/MVC:** Implementación de componentes UI con arquitectura MVC
- **FastAPI:** Implementación de endpoints REST con arquitectura en capas
- **Django:** Implementación MVT siguiendo convenciones Django
- **Generic Python:** Implementación de módulos Python genéricos

---

## Uso

```bash
/implement-us US-001
/implement-us US-001 --producto {PRODUCT}
/implement-us US-001 --skip-bdd  # Salta generación BDD
```

**Parámetros:**
- `US-XXX`: Identificador de la Historia de Usuario (requerido)
- `--producto`: Nombre del producto/módulo (opcional, default: valor de `{PRODUCT}`)
- `--skip-bdd`: Saltar generación de escenarios BDD (opcional)

---

## Flujo de Ejecución

Este skill orquesta la implementación de una US a través de **9 fases secuenciales**, cada una delegada a un agente especializado:

### 🔍 Fase 0: Validación de Contexto
**Agente:** [`phases/phase-0-validation.md`](./phases/phase-0-validation.md)

**Objetivo:** Verificar que el proyecto tiene todo lo necesario para implementar la US.

**Acciones:**
- Buscar y extraer datos de la US
- Validar arquitectura de referencia
- Verificar estándares de calidad

**Duración:** 5-10 min | **Aprobación:** Automática

---

### 📝 Fase 1: Generación de Escenarios BDD
**Agente:** [`phases/phase-1-bdd.md`](./phases/phase-1-bdd.md)

**Objetivo:** Generar escenarios BDD en formato Gherkin.

**Acciones:**
- Analizar criterios de aceptación
- Generar escenarios Given-When-Then
- Crear archivo `.feature`

**Duración:** 15-20 min | **Aprobación:** Requerida (usuario revisa escenarios)

---

### 📋 Fase 2: Generación del Plan de Implementación
**Agente:** [`phases/phase-2-planning.md`](./phases/phase-2-planning.md)

**Objetivo:** Crear plan detallado basado en arquitectura configurada.

**Acciones:**
- Analizar US y arquitectura
- Definir estructura de componentes según `{ARCHITECTURE_PATTERN}`
- Estimar tiempos por tarea
- Generar checklist de implementación

**Duración:** 15-20 min | **Aprobación:** Requerida (usuario revisa plan)

---

### 🔨 Fase 3: Implementación Guiada por Tareas
**Agente:** [`phases/phase-3-implementation.md`](./phases/phase-3-implementation.md)

**Objetivo:** Implementar la funcionalidad siguiendo el plan.

**Acciones:**
- Ejecutar tareas del plan secuencialmente
- Tracking de tiempo por tarea
- Checkpoints opcionales de aprobación

**Duración:** Variable según US | **Aprobación:** Por tarea (configurable)

---

### 🧪 Fase 4: Tests Unitarios
**Agente:** [`phases/phase-4-unit-tests.md`](./phases/phase-4-unit-tests.md)

**Objetivo:** Crear tests unitarios para cada componente.

**Acciones:**
- Generar tests según `{TEST_FRAMEWORK}`
- Configurar fixtures y mocks
- Ejecutar tests y validar cobertura

**Duración:** 20-30 min | **Aprobación:** Automática (tests deben pasar)

---

### 🔗 Fase 5: Tests de Integración
**Agente:** [`phases/phase-5-integration-tests.md`](./phases/phase-5-integration-tests.md)

**Objetivo:** Crear tests de integración entre componentes.

**Acciones:**
- Generar tests de integración
- Validar interacción entre componentes
- Ejecutar suite completa

**Duración:** 15-25 min | **Aprobación:** Automática (tests deben pasar)

---

### ✅ Fase 6: Validación BDD
**Agente:** [`phases/phase-6-bdd-validation.md`](./phases/phase-6-bdd-validation.md)

**Objetivo:** Implementar y ejecutar steps de los escenarios BDD.

**Acciones:**
- Crear step definitions
- Ejecutar escenarios BDD
- Validar que todos los escenarios pasan

**Duración:** 20-30 min | **Aprobación:** Automática (escenarios deben pasar)

---

### 📊 Fase 7: Quality Gates
**Agente:** [`phases/phase-7-quality-gates.md`](./phases/phase-7-quality-gates.md)

**Objetivo:** Validar que el código cumple con estándares de calidad.

**Acciones:**
- Ejecutar pylint
- Validar complejidad ciclomática
- Verificar cobertura de tests
- Generar reporte de calidad

**Duración:** 5-10 min | **Aprobación:** Automática (gates deben pasar)

---

### 📚 Fase 8: Documentación
**Agente:** [`phases/phase-8-documentation.md`](./phases/phase-8-documentation.md)

**Objetivo:** Generar documentación de la implementación.

**Acciones:**
- Actualizar documentación de arquitectura
- Generar docstrings si faltan
- Actualizar README o docs del proyecto

**Duración:** 10-15 min | **Aprobación:** Requerida (usuario revisa docs)

---

### 📄 Fase 9: Reporte Final
**Agente:** [`phases/phase-9-final-report.md`](./phases/phase-9-final-report.md)

**Objetivo:** Generar reporte completo de la implementación.

**Acciones:**
- Consolidar métricas de todas las fases
- Generar reporte de implementación
- Calcular varianza de estimación vs tiempo real
- Exportar métricas para análisis histórico

**Duración:** 5-10 min | **Aprobación:** Automática

---

## Control de Flujo

### Puntos de Aprobación

El skill tiene puntos de aprobación en:
- **Fase 1:** Escenarios BDD (usuario debe revisar)
- **Fase 2:** Plan de implementación (usuario debe revisar)
- **Fase 3:** Opcionalmente por tarea (configurable)
- **Fase 8:** Documentación (usuario debe revisar)

### Fases Opcionales

- `--skip-bdd`: Salta Fase 1 y Fase 6 (no recomendado)

### Manejo de Errores

Si una fase falla:
- **Tests fallan (4, 5, 6):** El skill se detiene hasta que los tests pasen
- **Quality gates fallan (7):** Se advierte al usuario, puede continuar bajo su responsabilidad
- **Validación falla (0):** Se advierte, puede continuar con datos manuales

---

## Tracking de Tiempo

El skill usa el sistema de tracking integrado (`tracking/time_tracker.py`) para:
- Registrar tiempo por fase
- Registrar tiempo por tarea (en Fase 3)
- Calcular varianza estimado vs real
- Generar reportes históricos

**Comandos disponibles:**
- `/track-pause [razón]` - Pausar tracking
- `/track-resume` - Reanudar tracking
- `/track-status` - Ver estado actual
- `/track-report [us_id]` - Generar reporte de US

---

## Arquitectura Modular

Este skill sigue una **arquitectura de orquestador + agentes especializados**:

- **skill.md** (este archivo): Orquestador que coordina el flujo
- **phases/*.md**: Agentes especializados, uno por fase
- **customizations/*.json**: Configuraciones específicas por stack
- **config.json**: Configuración base compartida

**Beneficios:**
✅ **Modularidad:** Cada fase es independiente y modificable
✅ **Mantenibilidad:** Cambios en una fase no afectan otras
✅ **Testeable:** Cada fase se puede probar individualmente
✅ **Extensible:** Fácil agregar nuevas fases o modificar existentes

---

## Ejemplo de Validación de Concepto

### ❌ ANTES (Monolítico - PyQt/MVC específico):

```markdown
### Implementación
- app/presentacion/paneles/display/modelo.py
- app/presentacion/paneles/display/vista.py
- El modelo debe heredar de ModeloBase
```

### ✅ DESPUÉS (Modular - Framework Agnostic):

**Orquestador (skill.md):**
```markdown
### Fase 3: Implementación
Ver phases/phase-3-implementation.md para instrucciones detalladas
```

**Agente Especializado (phase-3-implementation.md):**
```markdown
# Estructura según {ARCHITECTURE_PATTERN}:

**MVC:** {COMPONENT_PATH}/modelo.py, vista.py, controlador.py
**MVT:** {COMPONENT_PATH}/models.py, views.py, templates/
**Layered:** {COMPONENT_PATH}/schemas.py, service.py, router.py

El componente debe heredar de {BASE_CLASS}
```

---

**Versión:** 2.0.0 (Framework-Agnostic - Arquitectura Modular)
**Última actualización:** 2026-02-10
**Basado en:** `_work/from-simapp/skills/implement-us.md` (versión PyQt/MVC)
