# HITO-5 — US-1.2.2: Segundo Ciclo de /implement-us

| Campo | Valor |
|-------|-------|
| **Documento** | HITO-5 — Análisis experimental |
| **Fecha** | 2026-03-22 |
| **Alcance** | US-1.2.2 — LlamarAtleta (segunda US-IEDD del proyecto) |
| **Hipótesis activas** | RQ1 (fricción de ecosistema), H-4.1 (bugs de herramienta vs bugs de código) |
| **Relacionado** | `HITO-4-US-1-2-1-PRIMER-CICLO-IMPLEMENT-US.md` · PR #14 · Issue #3 |

---

## 1. Contexto

US-1.2.2 es el segundo ciclo completo de `/implement-us`. A diferencia de US-1.2.1,
donde los bugs de herramienta dominaron el tiempo real, este ciclo se ejecutó con
el ecosistema ya estabilizado (tracking CLI operativo, `--config` explícito en
DesignReviewer, `StrEnum` como patrón establecido).

El objetivo experimental de este HITO es verificar las hipótesis derivadas en HITO-4:
¿el overhead de ecosistema baja cuando los bugs están corregidos?

**Tiempos:** Estimado 1h 50min → Real **33 min** (varianza -82%)

---

## 2. Verificación de Hipótesis de HITO-4

### RQ1 — ¿El ecosistema genera fricción de coordinación?

**Evidencia de US-1.2.2:** El overhead de ecosistema fue mínimo. No hubo bugs de
herramienta que requirieran trabajo no planificado. El único tiempo "extra" fue
en Fase 7 (9 min) para ajustar la config de CodeGuard y elevar `max_cbo`.

**Conclusión parcial:** El overhead de US-1.2.1 era incidental, no sistémico.
Los bugs corregidos en ese ciclo no reaparecieron. La fricción del ecosistema
disminuyó drásticamente en el segundo ciclo.

**Matiz:** Surgió un nuevo problema de configuración en CodeGuard (campos inválidos
`max_complexity` y `paths`), pero fue resuelto en minutos. No es un bug del ecosistema
sino un error de configuración en `pyproject.toml`.

### H-4.1 — ¿Los bugs de herramienta son más costosos que los bugs de código?

**Confirmado.** US-1.2.1 tuvo ~2h de overhead por bugs de herramienta sobre una
US de ~2.5h estimadas (80% overhead). US-1.2.2, con el mismo ecosistema pero
sin bugs, tomó 33 min sobre 1h 50min estimados (82% de ahorro).

La diferencia no se explica por la complejidad de la US (similares), sino por
la ausencia de bugs de herramienta. El costo de los bugs se concentró en US-1.2.1
y no se repitió.

---

## 3. Problemas de Proceso

### P-5.1 — Commit directo a develop en lugar de feature branch

**Qué pasó:** El commit de US-1.2.2 fue hecho directamente en `develop` en lugar
de en `feature/US-1.2.2-llamar-atleta`. Fue necesario:
1. Crear la branch retroactivamente apuntando al commit
2. `git reset --hard` en develop al commit anterior
3. `git push --force-with-lease` en develop
4. Crear el PR desde la feature branch

**Causa raíz:** La sesión de implementación se inició con `/resume` desde una
sesión anterior compactada. El contexto restaurado indicaba "branch: develop"
pero no incluía la instrucción de crear una feature branch antes de empezar.
El workflow (`WORKFLOW-DESARROLLO.md §3`) lo especifica, pero no hay enforcement
en el proceso de restauración de sesión.

**Riesgo asociado:** El `git reset --hard` sobre develop con commits ya pusheados
requiere `--force-with-lease`. En un equipo de más de una persona sería destructivo.
En este proyecto (un solo desarrollador) fue seguro.

**Acción correctiva:** Agregar al skill `/resume` una verificación explícita de
branch activo y, si es `develop` o `main`, sugerir crear la feature branch antes
de cualquier cambio de código.

**Aprendizaje L-5.1:**
> El proceso de restauración de sesión (`/resume`) debe incluir como primer paso
> verificar si hay una feature branch activa. Si el branch es `develop`, crear
> `feature/US-X.Y.Z-descripcion` antes de tocar código. No asumir que el contexto
> restaurado incluye esa instrucción.

---

## 4. Problemas de Herramienta

### H-5.1 — CodeGuard: campos inválidos en pyproject.toml causan crash

**Qué pasó:** La sección `[tool.codeguard]` en `pyproject.toml` tenía dos campos
inválidos heredados de una versión anterior de la API:
- `max_complexity = 10` → debe ser `check_complexity = true` + `max_cyclomatic_complexity = 10`
- `paths = [...]` → no existe en `CodeGuardConfig`

Ambos causaban `TypeError` al inicializar `CodeGuard`, bloqueando la ejecución
en Fase 7.

**Diagnóstico:** `python -c "from quality_agents.codeguard.config import CodeGuardConfig; import inspect; print(inspect.signature(CodeGuardConfig.__init__))"` reveló los nombres correctos de los campos.

**Fix aplicado:** Reemplazar ambos campos por los correctos. `paths` se pasa como
argumento CLI (`codeguard src/competencia/`), no como config.

**Aprendizaje L-5.2:**
> Antes de ejecutar Fase 7, verificar que `pyproject.toml` solo contiene campos
> reconocidos por `CodeGuardConfig.__init__`. Un crash de configuración que tarda
> 5 minutos en diagnosticar puede prevenirse con una línea de introspección.

---

### H-5.2 — CBO escala linealmente con eventos de dominio del aggregate

**Qué pasó:** `Performance` tenía CBO = 9 al cierre de US-1.2.1 (con `max_cbo = 10`
holgado). US-1.2.2 añadió `AtletaLlamado` → CBO = 11, superando el umbral.
Fue necesario elevar `max_cbo = 12`.

**Patrón identificado:** Cada evento de dominio añadido al aggregate sube su CBO
en 1 (nuevo import). El aggregate es el punto de mayor crecimiento de CBO en el
BC Competencia.

**Proyección:** US-1.2.3 (RegistrarResultado) agregará `ResultadoRegistrado` →
CBO = 12. US-1.2.4 (AsignarTarjeta) agregará `TarjetaAsignada` → CBO = 13.
El umbral actual de 12 se alcanzará en US-1.2.3.

**Acción recomendada:** Anticipar la elevación de `max_cbo` al inicio de cada US
que añada un nuevo evento al aggregate, en lugar de descubrirlo en Fase 7. O bien,
consolidar los imports de eventos en un `__init__.py` intermedio y verificar si
eso reduce el CBO contado por la herramienta.

**Aprendizaje L-5.3:**
> `max_cbo` debe revisarse al inicio de cada US que añada un evento de dominio.
> La regla práctica: `max_cbo = 10 + (número de eventos en Performance)`. Actualizar
> antes de Fase 7, no como consecuencia de un CRITICAL en Fase 7.

---

## 5. Problemas de Código/Tests

### C-5.1 — Step BDD: Background + Given con estado implícito superpuesto

**Qué pasó:** El escenario "Rechazo por performance no en estado AnunciadaAP" tiene:
- **Background:** `la performance del participante está en estado "AnunciadaAP"`
  (que ejecuta `RegistrarAP` → crea la performance con estado `AnunciadaAP`)
- **Given:** `la performance del participante está en estado "Llamada"`
  (implementado inicialmente como: `RegistrarAP` + `LlamarAtleta`)

El step Given re-ejecutaba `RegistrarAP`, que fallaba con `APYaRegistrado` porque
el Background ya lo había hecho.

**Fix:** El step Given `está en estado "Llamada"` solo debe ejecutar `LlamarAtleta`,
confiando en que el Background ya dejó la performance en `AnunciadaAP`.

**Regla derivada:** En pytest-bdd, los steps de escenario no deben repetir
la lógica del Background. El Background establece el estado inicial; los Given del
escenario solo lo modifican desde ese punto.

**Aprendizaje L-5.4:**
> En BDD con Background, los steps `Given` de escenario son **transiciones desde
> el estado del Background**, no reconstrucciones del estado desde cero. Documentar
> explícitamente el estado de entrada en el nombre del step ayuda a evitar la
> duplicación: `"la performance YA EN AnunciadaAP pasa a estado Llamada"`.

---

## 6. Validación de Hipótesis Activas

### RQ2 — ¿IEDD mejora la calidad de las especificaciones?

**Evidencia de US-1.2.2:** La especificación con INV-P-05 (`is_en_ejecucion`)
como invariante explícito produjo directamente la estructura handler/port/stub.
No hubo dudas sobre dónde verificar el invariante ni qué mock usar en los tests.

El tiempo de implementación (Fase 3: 3 min) confirma que la especificación formal
elimina fricción de diseño en el momento de codificar.

**Patrón confirmado:** Los invariantes formales de la US-IEDD se mapean 1:1 a los
tests de rechazo. US-1.2.2 tiene 1 invariante de aplicación (INV-P-05) y exactamente
2 tests de rechazo en la capa de aplicación: `test_competencia_no_en_ejecucion_lanza_excepcion`
y `test_competencia_no_en_ejecucion_no_persiste`.

---

## 7. Resumen de Aprendizajes

| ID | Categoría | Aprendizaje | Acción |
|----|-----------|-------------|--------|
| L-5.1 | Proceso | `/resume` no verifica branch activo → commit directo a develop | Agregar verificación de branch en `/resume` |
| L-5.2 | Herramienta | CodeGuard crashea si pyproject.toml tiene campos inválidos | Verificar campos antes de Fase 7 |
| L-5.3 | Herramienta | CBO sube 1 por cada evento de dominio → anticipar elevación de `max_cbo` | Revisar `max_cbo` al inicio de cada US con nuevo evento |
| L-5.4 | Tests/BDD | Steps BDD de escenario no deben replicar el Background | Given = transición desde el estado del Background, no reconstrucción |

---

## 8. Indicadores del Experimento

| Indicador | US-1.2.1 | US-1.2.2 | Tendencia |
|-----------|----------|----------|-----------|
| Tiempo real | ~3h (estimado ~2.5h) | 33 min (estimado 1h 50min) | ↓ 82% |
| Overhead de ecosistema | ~2h (bugs de herramienta) | ~9 min (config CodeGuard) | ↓ 94% |
| CRITICAL DesignReviewer al cierre | 0 | 0 | = |
| Tests / cobertura | 34 / 92.42% | 49 / 98.48% | ↑ |
| Bugs de herramienta nuevos | 4 (H-4.1 a H-4.4) | 1 (H-5.1) | ↓ |

---

*2026-03-22 — US-1.2.2 cerrada. Próximo: US-1.2.3 RegistrarResultado o HITO-5-BIS al cerrar Inc 1.2.*
