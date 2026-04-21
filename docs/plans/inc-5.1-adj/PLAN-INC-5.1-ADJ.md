# PLAN-INC-5.1-ADJ — Ajuste post-UAT INC-5.1

| Campo | Valor |
|-------|-------|
| **Incremento** | INC-5.1-ADJ |
| **Contexto** | Hallazgos UAT funcional del panel organizador — 2026-04-21 |
| **Fuentes** | UAT-5.1-01..05 — registrados en `.work/revision-sp5/01-hallazgos-uat-inc-5.1.md` |
| **Branch base** | `develop` |
| **Estado** | Planificado |

---

## Contexto

Al completar INC-5.1 e iniciar la UAT funcional del panel organizador, se identificaron
cinco hallazgos de severidad Alta que impiden el flujo operativo real del torneo:

| ID | Descripción breve |
|----|-------------------|
| UAT-5.1-01 | `Ver competencias` vacío aunque el torneo tiene disciplinas configuradas |
| UAT-5.1-02 | Jueces asignables antes de generar grilla de tiempos oficiales |
| UAT-5.1-03 | Torneo cancelado muestra información operativa activa |
| UAT-5.1-04 | Torneo en ejecución muestra botón `Iniciar Ejecución` en lugar de acción de finalización |
| UAT-5.1-05 | Tabs `Grilla`, `Jueces`, `Ejecucion` habilitadas durante `INSCRIPCION_ABIERTA` |

Todos son bugs de código ya implementado en INC-5.1 — no scope nuevo. El INC-5.1 no
puede considerarse cerrado con estos hallazgos abiertos.

---

## US planificadas

### US-5.1.7 — Política de tabs por fase y estado CANCELADO

**Prioridad:** Alta
**Tipo:** fix funcional de navegación
**Área:** `frontend/src/pages/organizador/DetalleTorneoPage.tsx`
**Hallazgos:** UAT-5.1-03, UAT-5.1-05

`DetalleTorneoPage` renderiza todas las tabs sin considerar el estado del torneo.

**Fix:**
1. Definir política de tabs por estado:
   - `CREADO`, `INSCRIPCION_ABIERTA` → habilitar solo `Detalle` e `Inscriptos`
   - `PREPARACION`, `EJECUCION` → todas las tabs habilitadas
   - `CANCELADO` → mostrar solo resumen básico y mensaje de cancelación; ocultar tabs operativas
   - `FINALIZADO` → tabs en modo lectura (sin acciones)
2. Evitar que `activeTab` conserve una tab operativa si el torneo recarga en estado incompatible.

---

### US-5.1.8 — Componer disciplinas + competencias en `Ver competencias`

**Prioridad:** Alta
**Tipo:** fix funcional de composición
**Área:** `frontend/src/pages/organizador/TorneoCompetenciasPage.tsx`
**Hallazgo:** UAT-5.1-01

`TorneoCompetenciasPage` solo consulta `GET /competencia?torneo_id={id}`, que devuelve
competencias ya materializadas. Para estados tempranos (`INSCRIPCION_ABIERTA`, `PREPARACION`),
el torneo tiene disciplinas configuradas en `torneo.db` pero todavía no tiene competencias
en `competencia.db`.

**Fix:**
1. Consultar `GET /torneos/{torneo_id}/disciplinas` como fuente primaria de disciplinas.
2. Cruzar con `GET /competencia?torneo_id={id}` para enriquecer con `competencia_id` si existe.
3. Renderizar una card por disciplina configurada; si no tiene competencia, mostrar estado
   `Competencia pendiente de configurar` y guiar al tab `Grilla`.
4. Habilitar `Ver auditoría` solo si existe `competencia_id`.

---

### US-5.1.9 — Precondición grilla en asignación de jueces

**Prioridad:** Alta
**Tipo:** fix de regla funcional
**Área:** `frontend/src/components/organizador/JuecesPanel.tsx`
**Hallazgo:** UAT-5.1-02

El selector de juez se muestra habilitado para todas las disciplinas del torneo,
independientemente de si tienen grilla OT generada.

**Fix:**
1. Consultar competencias del torneo y su estado por disciplina.
2. Habilitar el selector de juez solo si la disciplina tiene competencia con grilla generada.
3. Mostrar estado bloqueado por fila: `Generar grilla antes de asignar juez`.
4. Mantener visible la asignación existente pero bloquear cambios sin grilla.

---

### US-5.1.10 — Corregir acciones de fase en `AccionesPanel`

**Prioridad:** Alta
**Tipo:** fix de acciones por estado
**Área:** `frontend/src/components/organizador/AccionesPanel.tsx`
**Hallazgo:** UAT-5.1-04

`AccionesPanel` muestra `Iniciar Ejecución` aunque el torneo ya está en `EJECUCION`.
Falta la acción de transición hacia `PREMIACION`/finalización.

**Fix:**
1. Confirmar nombres exactos de estados retornados por backend (`EJECUCION`, etc.).
2. Mostrar `Iniciar Ejecución` solo cuando `estado === "PREPARACION"` y precondiciones cumplidas.
3. Mostrar acción de finalización/premiación cuando `estado === "EJECUCION"`.
4. Validar llamada a `iniciarPremiacion(torneoId)` o endpoint equivalente.

---

## Secuencia de ejecución

```
US-5.1.7  ← política de tabs (bloquea exploración de bugs secundarios)
  ↓
US-5.1.8  ← composición disciplinas/competencias (independiente de tabs)
  ↓
US-5.1.9  ← precondición grilla en jueces (depende de composición correcta de disciplinas)
  ↓
US-5.1.10 ← acciones de fase (independiente, pero conveniente validar con tabs ya fijas)
```

---

## Criterio de cierre de INC-5.1-ADJ

- [x] US-5.1.7 — tabs habilitadas correctamente por fase; `CANCELADO` muestra solo resumen
- [x] US-5.1.8 — `Ver competencias` muestra disciplinas configuradas aunque no existan competencias
- [x] US-5.1.9 — selector de juez bloqueado si disciplina no tiene grilla generada
- [ ] US-5.1.10 — `Iniciar Ejecución` oculto en `EJECUCION`; acción de premiación visible
- [ ] UAT de regresión: flujo completo del organizador sin errores visibles
- [ ] DesignReviewer 0 CRITICAL post-INC-5.1-ADJ

---

*Creado: 2026-04-21 — hallazgos UAT funcional INC-5.1*
