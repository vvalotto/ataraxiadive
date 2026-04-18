# PLAN-SP-ADJ-06 — Sprint de Ajuste Técnico, Documental y UAT post-SP4

| Campo | Valor |
|-------|-------|
| **Sprint** | SP-ADJ-06 |
| **Contexto** | Ajuste técnico + documental + UAT integral post-SP4, pre-BL-004 |
| **Fuentes** | Revisión de calidad pre-BL-004 (`.work/revision-sp4/01–06`) · ArchitectAnalyst BL-004 · SP-ADJ-05 diferido |
| **Branch base** | `develop` |
| **Estado** | ⏳ Planificado |

---

## Contexto

SP4 cierra con la plataforma completa: frontend PWA (INC-4.2/4.3), offline-first (INC-4.4),
BC Notificaciones (INC-4.5) y auditoría/exportación (INC-4.6). La revisión de calidad
pre-BL-004 identificó issues en cuatro áreas:

1. **Arquitectura:** un ciclo ADP entre `performance` y `performance_state` (nuevo en BL-004)
   y un posible import cross-BC en `exportar_resultados.py`.
2. **SOLID:** `inspect.signature` en `_p08_finalizacion.py`, duplicación en políticas.
3. **Frontend:** dos violaciones de capa en `GrillaPage` y una función de utilidad mal ubicada.
4. **Documental:** corrección FAZ→FAAS heredada de SP-ADJ-05 diferido.

La US de UAT (US-4.6.5) se incorpora aquí — es el gate de validación integral antes
de ejecutar el merge `develop → main` y el tag `v0.5.0`.

---

## Hallazgos ArchitectAnalyst BL-004 — Registro e Interpretación

| Módulo | Analyzer | BL-003 | BL-004 | Tendencia | Interpretación |
|--------|----------|:------:|:------:|:---------:|----------------|
| `competencia` | Distance | D=0.616 | D=0.62 | → estable | Core Domain: no superó D=0.70 — sin acción |
| `identidad` | Distance | D=0.87 | D=0.87 | = estable | BC CRUD puro — aceptado |
| `registro` | Distance | D=0.563 | D=0.56 | ↓ mejora | BC CRUD estable — sin acción |
| `shared` | Distance | D=0.611 | D=0.63 | ↑ leve | Módulo cross-BC — monitorear |
| `torneo` | Distance | — | D=0.64 | NEW | BC CRUD en expansión — mismo patrón aceptado |
| `performance` | Cycles | — | ciclo | **NEW** | Ciclo ADP real — acción en US-ADJ-6.2 |

**Acción para SP5:** si `competencia` supera D=0.70 en BL-005 o `torneo` supera D=0.70,
evaluar extracción de abstracciones (nuevos puertos o VOs).

---

## US planificadas

### US-ADJ-6.1 — Investigación y resolución LAZY-01: import cross-BC en `exportar_resultados.py`

**Prioridad: Alta (pre-merge blocker)**
**Tipo:** investigación + refactor si aplica
**Área:** `resultados/application/queries/exportar_resultados.py`

`_performance_a_resultado_final()` contiene un lazy import de `Performance` de
`competencia/domain/`. Si el import es necesario en runtime, hay un acoplamiento cross-BC
que viola la arquitectura hexagonal.

**Acciones:**
1. Leer la función y determinar qué se usa de `Performance`
2. Si el import es solo para tipos → mover bajo `TYPE_CHECKING` (sin ciclo real)
3. Si instancia `Performance` → rediseñar: proyectar los datos necesarios desde el
   repositorio de Competencia como puerto, sin importar el aggregate directamente
4. Confirmar con madge que el grafo de dependencias cross-BC queda limpio

---

### US-ADJ-6.2 — Eliminar ciclo ADP: `reconstituir_performance()` como classmethod

**Prioridad: Alta**
**Tipo:** refactor
**Área:** `competencia/domain/aggregates/performance.py` + `performance_state.py`

`performance_state.py` contiene `reconstituir_performance()` que hace un lazy import
de `Performance` para instanciarlo — crea ciclo ADP detectado por ArchitectAnalyst.

**Fix:**
- Mover `reconstituir_performance()` como `Performance.reconstituir()` classmethod
- `performance_state.py` queda solo con las funciones `apply_*` que reciben
  `performance: Performance` sin necesidad de instanciar → sin ciclo
- Eliminar el lazy import de línea 33 de `performance_state.py`
- Actualizar todos los llamadores de `reconstituir_performance()`
- Verificar: `architectanalyst` debe reportar 0 ciclos post-fix

---

### US-ADJ-6.3 — OCP: unificar firma del callback `on_finalizada`

**Prioridad: Media**
**Tipo:** refactor
**Área:** `competencia/application/_p08_finalizacion.py` + llamadores

El código usa `inspect.signature(on_finalizada)` para ramificar entre llamadas con 1 y 2
parámetros. Violación OCP: si el callback agrega un parámetro futuro, hay que modificar
`_p08_finalizacion.py`.

**Fix:**
- Unificar la firma: todos los callbacks reciben `(competencia_id, hash_sha256)`
- Los llamadores que no usan `hash_sha256` simplemente lo ignoran
- Eliminar `import inspect` y el bloque condicional
- Ejecutar tests para verificar que la finalización sigue funcionando

---

### US-ADJ-6.4 — Notificaciones: refactor políticas P-10 y P-11

**Prioridad: Media**
**Tipo:** refactor
**Área:** `notificaciones/application/policies/`

Dos issues combinados en una US porque afectan los mismos archivos:

- **DES-01:** `_registrar_fallo_sin_email` duplicado entre `politica_p10.py` y `politica_p11.py`
  → extraer función utilitaria compartida en `application/` o usar la firma de P-11
  (recibe `str`) en ambas

- **DES-02:** `PoliticaP11Handler._evento_fuente_id` no usa `self` → agregar `@staticmethod`
  → elimina LCOM=2 reportado por DesignReviewer

**Fix:**
- Extraer `registrar_fallo_sin_email(evento_fuente_id: str, repository)` como función
  de módulo compartida en `application/commands/solicitar_envio.py` o en un helper nuevo
- Agregar `@staticmethod` a `_evento_fuente_id` en P-11
- Actualizar llamadores en P-10 para alinear firma con P-11

---

### US-ADJ-6.5 — Frontend: correcciones de capa en `GrillaPage` y `usePerformanceFlow`

**Prioridad: Media**
**Tipo:** refactor frontend
**Área:** `frontend/src/pages/juez/GrillaPage.tsx` + `frontend/src/hooks/usePerformanceFlow.ts`

Dos issues de capa combinados (misma área, bajo riesgo):

- **FE-ARCH-02:** `GrillaPage` importa `getCommandsByCompetencia` y `ComandoQueueRecord`
  de `db/queries` directamente. Mover la lógica de "cuántos comandos pendientes por atleta"
  a `useComandoQueue` como nueva propiedad expuesta `pendingByAtleta`

- **FE-DES-01:** `formatMarca` y `buildResultadoValue` exportadas desde `usePerformanceFlow.ts`
  — son funciones puras sin estado. Mover a `frontend/src/utils/marca.ts` (nuevo archivo).
  Actualizar `GrillaPage` para importar desde `utils/marca.ts`

**Validación:** `npm run build` sin errores de TypeScript · ESLint 0 errores

---

### US-ADJ-6.6 — Corrección documental: FAZ → FAAS en 9 archivos

**Prioridad: Baja (heredada de SP-ADJ-05 diferido)**
**Tipo:** documental
**Área:** docs/ + src/ + tests/

La sigla correcta del organismo de apnea argentino es **FAAS** (Federación Argentina de
Actividades Subacuáticas). El término "FAZ" aparece en 9 archivos del proyecto.

**Acciones:**
1. `grep -r "FAZ" docs/ src/ tests/ --include="*.md" --include="*.py"` para identificar todos los casos
2. Reemplazar `FAZ` → `FAAS` en cada ocurrencia
3. Verificar que no haya referencias en comentarios de código o strings de error

---

### US-ADJ-6.7 — UAT SP4: validación integral de la plataforma

**Prioridad: Alta (gate de cierre)**
**Tipo:** UAT — no genera código
**Spec:** `docs/specs/sp4/US-4.6.5.md` (movida desde INC-4.6)

Validación end-to-end de INC-4.4 (offline-first), INC-4.5 (notificaciones email),
INC-4.6 (auditoría/exportación) con datos reales del torneo Buenos Aires 2025.

**Prerrequisitos:** US-ADJ-6.1 a 6.6 completadas · backend y frontend corriendo ·
RESEND_API_KEY configurada · dispositivo móvil real en la misma red

**Criterio de cierre:** todos los checks de `US-4.6.5.md` ✅ ·
0 errores no manejados en consola del browser

---

## Items diferidos a SP5 o SP-ADJ-07

Los siguientes candidatos identificados en la revisión se descartan de SP-ADJ-06 por
razones de scope:

| ID | Razón de diferimiento |
|----|-----------------------|
| DR-04 (PerformanceContext VO) | Refactor de 7 factories — esfuerzo L, sin impacto funcional en SP5 |
| SRP-01 (ExportarResultadosHandler) | Refactor arquitectónico — mejor en SP5 cuando se conozca la evolución del módulo |
| DR-02 (Performance LongMethod 65/20) | Identificar primero cuál método en análisis de SP5 |
| DR-07 (AndarivelesActivosAdapter 52/20) | Tercer SP consecutivo — documentar explícitamente como deuda aceptada |
| FE-ARCH-01 (organizador sin hooks) | Solo justifica acción si SP5 introduce caché en organizador (ver HITO-25) |
| DR-01 (Torneo LCOM=6) | Monitorear — umbral de acción si supera LCOM=8 en BL-005 |
| SP-ADJ-05 items D-01/D-07/D-09 | Scope documental mayor — evaluar post-BL-004 |

---

## Secuencia de ejecución

```
LAZY-01 investigación (US-ADJ-6.1)   ← pre-merge blocker, ejecutar primero
  ↓
Ciclo ADP (US-ADJ-6.2)
  ↓
OCP callback (US-ADJ-6.3)
  ↓
Notificaciones (US-ADJ-6.4)
  ↓
Frontend capas (US-ADJ-6.5)
  ↓
FAZ→FAAS documental (US-ADJ-6.6)     ← puede ejecutarse en cualquier momento
  ↓
UAT SP4 (US-ADJ-6.7)                 ← gate final
  ↓
merge develop→main · tag v0.5.0 · BL-004
```

---

## Criterio de cierre de SP-ADJ-06

- [ ] US-ADJ-6.1 — LAZY-01 resuelto o descartado con justificación
- [ ] US-ADJ-6.2 — ArchitectAnalyst 0 ciclos en `competencia/domain/aggregates/`
- [ ] US-ADJ-6.3 — `inspect` eliminado de `_p08_finalizacion.py` · tests pasan
- [ ] US-ADJ-6.4 — `_registrar_fallo_sin_email` unificado · P-11 con `@staticmethod`
- [ ] US-ADJ-6.5 — `GrillaPage` sin imports de `db/` · `formatMarca` en `utils/marca.ts`
- [ ] US-ADJ-6.6 — 0 ocurrencias de "FAZ" en docs/ src/ tests/
- [ ] US-ADJ-6.7 — UAT completo con todos los checks ✅ · reporte en `quality/reports/uat/SP4/`
- [ ] DesignReviewer final: 0 CRITICAL · merge `develop → main` · tag `v0.5.0`

---

*Creado: 2026-04-16 — post revisión de calidad pre-BL-004*
