# PLAN-SP-ADJ-07 — Sprint de Ajuste: Deuda BUG/SCOPE post-SP4

| Campo | Valor |
|-------|-------|
| **Sprint** | SP-ADJ-07 |
| **Contexto** | Resolución de deuda funcional identificada en SP4 antes de arrancar SP5 |
| **Fuentes** | BUG-SP4-003 · BUG-SP4-004 · SCOPE-SP4-001 — registrados en CLAUDE.md §14 al cerrar BL-004 |
| **Branch base** | `develop` |
| **Estado** | ⏳ Planificado |

---

## Contexto

Al cerrar SP4 (BL-004 · tag `v0.5.0`) quedaron tres ítems pendientes que no se
resolvieron en SP-ADJ-06 por falta de tiempo, no por falta de urgencia:

| ID | Tipo | Descripción breve |
|----|------|-------------------|
| BUG-SP4-003 | Bug de dominio | No existe forma de corregir un DNS registrado por error |
| BUG-SP4-004 | Bug de API/frontend | `/grilla` no expone `tarjeta_asignada` — auditoría sin colores |
| SCOPE-SP4-001 | Scope omitido | `build_p11_handler()` está definido en `app.py` pero nunca cableado |

Los tres son bloqueantes para la demo de SP5: BUG-SP4-003 afecta la integridad del
flujo del juez, BUG-SP4-004 degrada la UX de auditoría, y SCOPE-SP4-001 es la razón
de ser de INC-4.5 (BC Notificaciones).

---

## US planificadas

### US-ADJ-7.1 — BUG-SP4-003: comando `CorregirResultadoTrasDNS`

**Prioridad: Alta (bug funcional del juez)**
**Tipo:** feat de dominio
**Área:** `competencia/domain/` + `competencia/application/commands/` + `competencia/api/`

El `registrar_dns()` del aggregate `Performance` solo permite transicionar
`Llamada → DNS`. El `corregir_resultado()` existente requiere estado `Ejecutada`,
por lo que un DNS registrado por error es irreversible en el dominio actual.

**Fix:** Nuevo comando `CorregirResultadoTrasDNS` que transiciona `DNS → ResultadoRegistrado`,
emitiendo un nuevo evento `ResultadoCorregidoTrasDNS` con `motivo_correccion` obligatorio.
Una vez en `ResultadoRegistrado`, el flujo normal de `AsignarTarjeta` continúa.

---

### US-ADJ-7.2 — BUG-SP4-004: exponer `tarjeta_asignada` en `/grilla`

**Prioridad: Alta (UX auditoría)**
**Tipo:** fix de API + frontend
**Área:** `competencia/application/queries/obtener_grilla.py` + frontend `AuditoriaPage`

`EntradaGrillaDTO` no incluye `tarjeta_asignada`. El frontend de auditoría no puede
mostrar los colores por tarjeta (blanca / blanca con penalizaciones / amarilla / roja).

**Fix:** Agregar `tarjeta_asignada: str | None` al DTO y a `_PerformanceProjection`.
Extraer el valor desde `performance.tarjeta.value if performance.tarjeta else None`.
El frontend consume el nuevo campo para aplicar estilos condicionales.

---

### US-ADJ-7.3 — SCOPE-SP4-001: cablear P-11 a `CompetenciaFinalizada`

**Prioridad: Media (sin esta US, BC Notificaciones es letra muerta)**
**Tipo:** feat de integración (composition root)
**Área:** `src/app.py` + nuevo ACL de Resultados para Notificaciones

`build_p11_handler()` está definido en `app.py` pero nunca se invoca. `PoliticaP11Handler`
espera un `ResultadosPublicados` que debe construirse cuando `CompetenciaFinalizada` ocurre
(dentro del callback `_on_finalizada`, después de que P-08 calculó el ranking).

**Fix:** En `_calcular_ranking_por_finalizacion` (o en `_on_finalizada` directamente),
después de calcular el ranking, leer el ranking del event store de Resultados y los emails
de atletas desde el Registro BC, construir `ResultadosPublicados`, y llamar al
`PoliticaP11Handler` construido.

---

## Secuencia de ejecución

```
US-ADJ-7.2  ← fix más simple, sin dependencias, alta visibilidad
  ↓
US-ADJ-7.1  ← nuevo comando de dominio, requiere cuidado en state machine
  ↓
US-ADJ-7.3  ← integración cross-BC, la más compleja
  ↓
merge develop→main no aplica aquí — BL-005 se cierra al final de SP5
```

> Nota: SP-ADJ-07 se ejecuta sobre `develop` sin baseline propia. Los ítems se
> incorporan a BL-005 al cerrar SP5.

---

## Criterio de cierre de SP-ADJ-07

- [ ] US-ADJ-7.1 — `CorregirResultadoTrasDNS` implementado · tests pasan · endpoint verificado
- [x] US-ADJ-7.2 — `/grilla` incluye `tarjeta_asignada` · auditoría muestra colores por tarjeta
- [ ] US-ADJ-7.3 — P-11 se dispara al cerrar una disciplina · email real recibido en prueba
- [ ] DesignReviewer 0 CRITICAL post-SP-ADJ-07

---

*Creado: 2026-04-19 — deuda BUG/SCOPE de BL-004*
