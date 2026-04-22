# PLAN-SP-ADJ-08 — Sprint de Ajuste post-UAT INC-5.2

| Campo | Valor |
|-------|-------|
| **Sprint** | SP-ADJ-08 |
| **Contexto** | Ajustes funcionales y UX detectados en UAT de cierre de INC-5.2 |
| **Fuentes** | UAT-5.2-01..08 — registrados en `.work/revision-sp5/02-hallazgos-aut-inc-5.2.md` |
| **Incremento asociado** | INC-5.2 — Ejecucion por Disciplina |
| **Branch base** | `develop` |
| **Estado** | Planificado |

---

## Contexto

Luego de completar `US-5.2.1` y `US-5.2.2`, la UAT funcional del panel organizador
identifico ocho hallazgos. La mayoria son de UX funcional y consistencia de lenguaje,
pero dos afectan reglas operativas:

| ID | Severidad | Descripcion breve |
|----|-----------|-------------------|
| UAT-5.2-01 | Media | Estado vacio de inscriptos se comunica como error |
| UAT-5.2-02 | Alta | Selector de grilla muestra disciplinas fuera del torneo |
| UAT-5.2-03 | Baja | Mensaje de jueces ambiguo entre carga, vacio y error |
| UAT-5.2-04 | Baja | Disciplina seleccionada en ejecucion no se destaca suficiente |
| UAT-5.2-05 | Alta | Transicion a premiacion no depende del cierre de competencias |
| UAT-5.2-06 | Media | Estados tecnicos de ejecucion confunden al organizador |
| UAT-5.2-07 | Media | Lenguaje de premiacion y cierre requiere precision |
| UAT-5.2-08 | Media | Cancelar torneo necesita zona de peligro y confirmacion fuerte |

SP-ADJ-08 agrupa los hallazgos en tres US para mantener trazabilidad sin fragmentar
excesivamente el trabajo.

---

## US planificadas

### US-ADJ-8.1 — Clarificar estados y lenguaje operativo del panel organizador

**Prioridad:** Media
**Tipo:** fix UX funcional frontend
**Area:** paneles de organizador
**Hallazgos:** UAT-5.2-01, UAT-5.2-03, UAT-5.2-04, UAT-5.2-06, UAT-5.2-07
**Spec:** `docs/specs/sp-adj-08/US-ADJ-8.1.md`

Corrige estados vacios/error/loading, mensajes tecnicos de ejecucion, destaque visual
de disciplina seleccionada y nombres de acciones de fase.

**Fix:**
1. Separar estados `loading`, vacio valido y error real en inscriptos y jueces.
2. Convertir bloqueos tecnicos de ejecucion en mensajes accionables.
3. Destacar visualmente disciplina seleccionada y detalle.
4. Usar `Pasar a premiacion` en `EJECUCION` y `Cerrar torneo` en `PREMIACION`.

---

### US-ADJ-8.2 — Restringir operaciones por torneo y fase

**Prioridad:** Alta
**Tipo:** fix de regla funcional frontend + validacion de fase
**Area:** selector de grilla, acciones de fase, posible validacion backend
**Hallazgos:** UAT-5.2-02, UAT-5.2-05, UAT-5.2-07
**Spec:** `docs/specs/sp-adj-08/US-ADJ-8.2.md`

Evita operar disciplinas que no pertenecen al torneo y bloquea el paso a premiacion
si existen competencias pendientes, sin crear, en preparacion, confirmadas o en ejecucion.

**Fix:**
1. Poblar selector de grilla desde `GET /torneos/{torneo_id}/disciplinas`.
2. Cruzar disciplinas esperadas con `GET /competencia?torneo_id=...`.
3. Habilitar `Pasar a premiacion` solo si todas las competencias esperadas estan `Finalizada`.
4. Agregar validacion backend si el endpoint de fase permite avanzar sin esta precondicion.

---

### US-ADJ-8.3 — Fortalecer cancelacion de torneo

**Prioridad:** Media
**Tipo:** hardening UX de accion destructiva
**Area:** acciones del organizador
**Hallazgo:** UAT-5.2-08
**Spec:** `docs/specs/sp-adj-08/US-ADJ-8.3.md`

Separa `Cancelar torneo` en una zona de peligro y exige confirmacion fuerte escribiendo
el nombre exacto del torneo antes de ejecutar la cancelacion.

**Fix:**
1. Mover `Cancelar torneo` fuera del grupo de acciones normales.
2. Abrir modal de confirmacion destructiva.
3. Habilitar la accion final solo si el texto ingresado coincide exactamente con el nombre del torneo.
4. Conservar la API/semantica de cancelacion existente.

---

## Secuencia de ejecucion

```
US-ADJ-8.2  <- primero: reglas operativas de mayor severidad
  ↓
US-ADJ-8.1  <- limpieza UX y lenguaje sobre flujo ya restringido
  ↓
US-ADJ-8.3  <- hardening destructivo aislado
  ↓
UAT de regresion INC-5.2
```

---

## Criterio de cierre de SP-ADJ-08

- [ ] US-ADJ-8.2 — selector de grilla filtrado por torneo y premiacion bloqueada hasta competencias finalizadas.
- [ ] US-ADJ-8.1 — estados vacios/loading/error claros, mensajes accionables y lenguaje de fase preciso.
- [ ] US-ADJ-8.3 — cancelacion en zona de peligro con confirmacion por nombre exacto.
- [ ] UAT de regresion INC-5.2 sin hallazgos Alta abiertos.
- [ ] Frontend build/lint OK.
- [ ] Tests backend/frontend focalizados OK segun alcance real de cada US.

---

## Items fuera de alcance

- Redisenar la navegacion completa del panel organizador.
- Cambiar el ciclo de vida de `Torneo` mas alla de validar precondiciones de fase.
- Agregar nuevas fases de torneo.
- Reemplazar el flujo de grilla, jueces o ejecucion por una arquitectura nueva.

---

*Creado: 2026-04-22 — hallazgos UAT de cierre INC-5.2*
