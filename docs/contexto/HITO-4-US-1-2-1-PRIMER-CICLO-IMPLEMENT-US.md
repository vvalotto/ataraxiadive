# HITO-4 — US-1.2.1: Primer Ciclo Completo de /implement-us

| Campo | Valor |
|-------|-------|
| **Documento** | HITO-4 — Análisis experimental |
| **Fecha** | 2026-03-21 |
| **Alcance** | US-1.2.1 — Registrar AP (primera US-IEDD del proyecto) |
| **Hipótesis activas** | RQ1 (fricción de ecosistema), RQ2 (calidad de especificaciones IEDD) |
| **Relacionado** | `HITO-3-INC-1-1-WALKING-SKELETON.md` · PR #13 · Issue #2 · claude-dev-kit#42 · software_limpio#44 |

---

## 1. Contexto

US-1.2.1 es la primera Historia de Usuario IEDD implementada con el ciclo
completo de `/implement-us`. Es el primer contacto real entre el marco IEDD
(especificaciones con pre/post/invariantes), el Claude Dev Kit (10 fases) y el
aggregate DDD con Event Sourcing del BC Competencia.

Este HITO documenta los problemas encontrados durante el ciclo, organizados
por categoría: proceso, herramienta y código. La distinción importa porque
implica acciones correctivas distintas.

---

## 2. Problemas de Proceso

### P-4.1 — Tracking post-facto: el framework no es ejecutable desde Bash

**Qué pasó:** El `TimeTracker` no se inicializó al inicio de Fase 0. Las 10 fases
del tracking fueron reconstruidas de memoria al final de la sesión. El JSON resultante
tiene la nota: *"Fases 0-8 reconstruidas post-facto"*.

**Causa raíz:** Los phase files (`phase-0-validation.md`, etc.) definen el tracking
como bloques de pseudocódigo Python que documentan la intención pero no son ejecutables:

```python
# Esto no es un comando Bash — Claude Code no puede ejecutarlo
tracker.start_phase(0, "Validación de Contexto")
```

No existe ningún comando Bash que Claude Code pueda correr para registrar el inicio
o fin de una fase. En consecuencia, el tracking se convierte en trabajo voluntario
sin mecanismo de enforcement — y se omite sistemáticamente.

**Acción tomada:** Implementado `tracker_cli.py` + `TimeTracker.load()` (ver P-4.2).
Phase-0 actualizado con comandos Bash ejecutables. Issue upstream: claude-dev-kit#42.

**Aprendizaje L-4.1:**
> Un proceso que depende de la voluntad del agente (Claude Code) sin mecanismo de
> enforcement no se ejecuta. El tracking solo funcionará si cada phase file tiene
> comandos Bash concretos que puedan correrse como herramienta.

---

### P-4.2 — Evidencia CodeGuard fabricada: el comando correcto no estaba claro

**Qué pasó:** El `US-1.2.1-quality.json` fue escrito a mano con los números que
CodeGuard reportó en consola. No es el output directo de `codeguard --format json`.
La evidencia del quality gate es parcialmente fabricada.

**Causa raíz:** El phase-7 decía:
```bash
codeguard src/{BC}/ --format json > quality/reports/codeguard/{US_ID}-codeguard.json
codeguard src/{BC}/
```
Pero el archivo de destino tenía el mismo nombre que el resumen consolidado
(`{US_ID}-quality.json`), generando confusión sobre qué guardar dónde.
El flag `--format json` y el raw output nunca fueron usados.

**Acción tomada:** Phase-7 actualizado para distinguir entre evidencia cruda
(`{US_ID}-codeguard-raw.json`, output directo del comando) y resumen consolidado
(`{US_ID}-quality.json`, referencia a los raw).

**Aprendizaje L-4.2:**
> La distinción entre "evidencia" (artefacto generado por la herramienta) y "resumen"
> (artefacto generado por el agente) debe ser explícita en el proceso. La evidencia
> debe ser siempre el output directo, no una transcripción.

---

### P-4.3 — Ciclo interrumpido sin cierre formal

**Qué pasó:** La sesión anterior terminó sin completar las fases de cierre
(DesignReviewer, actualización de matrix.md, PR, Issue). El ciclo quedó a medias.

**Impacto:** Al retomar se encontraron 5 CRITICAL de DesignReviewer que no estaban
documentados, el issue de GitHub abierto, y cambios sin commitear. El `/resume`
funcionó correctamente para recuperar el contexto, pero el estado incompleto
generó trabajo adicional de diagnóstico.

**Aprendizaje L-4.3:**
> El cierre del ciclo (DesignReviewer, PR, Issue) debe hacerse en la misma sesión
> que la implementación. Si la sesión se interrumpe antes del cierre, el checkpoint
> debe registrar explícitamente qué fases quedaron pendientes.

---

## 3. Problemas de Herramienta

### H-4.1 — Bug: `_load_tracker_from_file()` no restaura estado (Dev Kit)

**Qué pasó:** `commands.py` tiene una función que "carga" el tracker desde JSON
pero solo crea un `TimeTracker` vacío y sobreescribe `storage_path`. No restaura
`phases`, `pauses`, ni `started_at`.

**Consecuencia:** Toda llamada a `tracker.end_phase(N)` en un proceso Python
separado opera sobre `phases=[]`, `_get_phase(N)` retorna `None`, y la operación
falla silenciosamente sin persistir nada.

```python
# commands.py — estado original (roto)
tracker = TimeTracker(...)  # phases=[], started_at=None
tracker.storage_path = file_path  # solo esto
return tracker  # end_phase() aquí → falla silenciosamente
```

**Acción tomada:** Implementado `classmethod TimeTracker.load()` que reconstruye
estado completo (phases, tasks, pauses, current_*, timestamps). Creado `tracker_cli.py`
como CLI wrapper. Issue upstream: claude-dev-kit#42.

**Aprendizaje L-4.4:**
> Un bug de fallo silencioso en una herramienta de proceso (no de producto) puede
> existir en producción indefinidamente porque nunca genera un error visible — solo
> produce datos incorrectos. La cobertura de tests debe incluir las herramientas
> de proceso, no solo el código de dominio.

---

### H-4.2 — Bug: DesignReviewer ignora pyproject.toml silenciosamente (software_limpio)

**Qué pasó:** La sección `[tool.designreviewer]` en `pyproject.toml` incluía
campos que no son parte de `DesignReviewerConfig` (`paths`, `check_hexagonal`,
`forbidden_imports_in_domain`). `cls(**tool_config)` lanzaba `TypeError`,
la excepción era capturada silenciosamente en `load_config()`, y la herramienta
usaba todos los defaults.

**Consecuencia:** `max_cbo = 10` (configurado para acomodar patrones DDD) nunca
fue leído. Los 2 CRITICAL de CBO que generó en US-1.2.1 son consecuencia directa
de este bug — con la config correcta no habrían sido CRITICAL.

**Workaround aplicado:** Separar los campos válidos de `DesignReviewerConfig` en
`[tool.designreviewer]` y pasar `--config pyproject.toml` explícitamente. Actualizado
el pre-push hook. Issue reportado en software_limpio.

**Aprendizaje L-4.5:**
> Una herramienta que falla silenciosamente al leer su configuración y cae a defaults
> es más peligrosa que una que falla ruidosamente. El equipo confía en la configuración
> que escribió y no tiene forma de saber que no está siendo aplicada.

---

### H-4.3 — Umbral CBO default incompatible con DDD (software_limpio)

**Qué pasó:** El threshold default `max_cbo = 5` generó 2 CRITICAL en `Performance`
y `RegistrarAPHandler`. Ambas clases tienen CBO = 8 porque acoplan a sus VOs,
eventos y puertos — acoplamiento legítimo en patrones DDD hexagonales.

**Análisis:** El umbral de 5 está calibrado para OO genérico (literatura clásica).
Un aggregate DDD que conoce 3-4 value objects, 1-2 eventos y 1-2 puertos supera
ese umbral por diseño. No es deuda técnica — es el patrón.

**Acción tomada:** `max_cbo = 10` en pyproject.toml. Issue reportado en software_limpio
para que la documentación incluya guía de configuración para proyectos DDD.

**Aprendizaje L-4.6:**
> Los thresholds de métricas OO clásicas deben ajustarse por patrón arquitectónico.
> Un proyecto DDD hexagonal necesita valores distintos a un proyecto OO genérico.
> La herramienta debería documentar valores recomendados por patrón.

---

## 4. Problemas de Código

### C-4.1 — Enums con `(str, Enum)` en lugar de `StrEnum`

**Qué pasó:** Los tres enums del BC Competencia (`Disciplina`, `UnidadMedida`,
`EstadoPerformance`) usaban herencia doble `(str, Enum)`, lo que produce NOP = 2.
El umbral es NOP ≤ 1. Tres CRITICAL de DesignReviewer.

**Fix:** `StrEnum` (Python 3.11+) logra el mismo resultado con NOP = 1.
Cambio de una línea por enum. Sin cambio de comportamiento — los tests pasaron
sin modificaciones.

**Aprendizaje L-4.7:**
> `class MiEnum(str, Enum)` es un patrón legítimo pero obsoleto en Python ≥ 3.11.
> El skill `/implement-us` debe generar `StrEnum` por defecto para enums que
> necesitan serialización a string.

---

## 5. Validación de Hipótesis Activas

### RQ1 — ¿El ecosistema genera fricción de coordinación?

**Evidencia de US-1.2.1:** Sí, más de lo esperado. Los problemas H-4.1 y H-4.2
son bugs en las herramientas del ecosistema que generaron trabajo no planificado:
implementar `load()` + `tracker_cli.py` + fix de `pyproject.toml` + actualización
del pre-push hook. Ese trabajo no forma parte de la US — es overhead del ecosistema.

**Cuantificación aproximada:** ~2 horas de trabajo adicional por bugs de herramientas
en una US estimada en 2.5 horas. Overhead de ecosistema: ~80% del tiempo de la US.

**Matiz importante:** El overhead no es inherente al ecosistema — es consecuencia
de bugs específicos que ahora están corregidos. La pregunta es si estos bugs son
incidentales (y el overhead baja en las próximas USs) o sistémicos.

**Próxima verificación:** US-1.2.2 — ¿el overhead de ecosistema baja ahora que
los bugs están corregidos?

### RQ2 — ¿IEDD mejora la calidad de las especificaciones?

**Evidencia de US-1.2.1:** La especificación con pre/post/invariantes formales
(INV-P-01 a INV-P-04) produjo tests precisos que cubren exactamente los casos
de error del dominio. No hubo ambigüedad sobre qué testear. La cobertura del 97.71%
no es accidental — es consecuencia de tener invariantes formales como guía.

**Aprendizaje positivo:** INV-P-01 (valorAP > 0) está implementado en el value
object `AP`, no en el handler. Esto es consecuencia directa de tener el invariante
formalizado: el lugar natural para validarlo es el tipo, no el orquestador.

---

## 6. Nueva Hipótesis Derivada

**H-4.1 — Los bugs de herramienta son más costosos que los bugs de código**

> En un proyecto con IA como agente de implementación, los bugs en las herramientas
> del proceso (tracking, quality gates, configuración) generan overhead proporcional
> al número de USs implementadas. Un bug que tarda 2 horas en corregirse en US-1
> habría costado 2h × N en N USs si no se hubiera detectado temprano.
>
> **Implicación:** Vale la pena invertir tiempo en verificar que las herramientas
> del proceso funcionan correctamente al inicio del sprint, antes de la primera US.
> **Verificación:** Comparar overhead de ecosistema en US-1.2.2 vs US-1.2.1.

---

## 7. Resumen de Aprendizajes

| ID | Categoría | Aprendizaje | Acción |
|----|-----------|-------------|--------|
| L-4.1 | Proceso | El tracking sin comandos Bash ejecutables no se usa | Phase files actualizados con Bash |
| L-4.2 | Proceso | Evidencia ≠ resumen — el raw output debe guardarse | Phase-7 actualizado |
| L-4.3 | Proceso | El cierre del ciclo debe hacerse en la misma sesión | Checkpoint explícito de fases pendientes |
| L-4.4 | Herramienta | Fallo silencioso en `_load_tracker_from_file()` | `load()` + `tracker_cli.py` implementados |
| L-4.5 | Herramienta | DesignReviewer ignora pyproject.toml silenciosamente | `--config` explícito + issue en software_limpio |
| L-4.6 | Herramienta | CBO default incompatible con DDD | `max_cbo = 10` + issue en software_limpio |
| L-4.7 | Código | `(str, Enum)` → `StrEnum` en Python ≥ 3.11 | Enums corregidos; skill debe generarlos con StrEnum |

---

*2026-03-21 — US-1.2.1 cerrada. Próximo: HITO-5 al cerrar Inc 1.2 (todas las US de la competencia).*
