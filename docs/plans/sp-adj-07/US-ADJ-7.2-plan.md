# Plan de Implementación: US-ADJ-7.2 — tarjeta_asignada en grilla

| Campo | Valor |
|-------|-------|
| **Sprint** | SP-ADJ-07 |
| **Tipo** | Fix API + frontend |
| **Branch** | `feature-US-ADJ-7.2-tarjeta-grilla` |
| **BC / producto** | `competencia` + `frontend` |
| **Estimación** | 45-70 min |

---

## Alcance

Exponer el valor ya existente `Performance.tarjeta` en el read model de `/grilla`
y usarlo en la pantalla de auditoría de competencia para aplicar estilos por tarjeta.

No se agregan comandos, eventos ni invariantes nuevas de dominio.

---

## Tareas

### 1. Backend — query y API

- [x] Modificar `src/competencia/application/queries/obtener_grilla.py`
  - Agregar `tarjeta_asignada: str | None` a `EntradaGrillaDTO`.
  - Agregar `tarjeta_asignada: str | None` a `_PerformanceProjection`.
  - Retornar `None` cuando no hay eventos o no hay tarjeta.
  - Retornar `performance.tarjeta.value` cuando la performance tiene tarjeta.

- [x] Modificar `src/competencia/api/router.py`
  - Serializar `tarjeta_asignada` en `GET /competencia/{competencia_id}/grilla`.

### 2. Frontend — auditoría

- [x] Modificar `frontend/src/api/competencia.ts`
  - Agregar `tarjeta_asignada: string | null` a `GrillaAtletaDto`.

- [x] Modificar `frontend/src/pages/organizador/AuditoriaCompetenciaPage.tsx`
  - Reemplazar el estilo basado solo en `estado`.
  - Aplicar estilos para `Blanca`, `BlancaConPenalizaciones`, `Roja` y fallback neutro.
  - Mantener `DNS` distinguible si no hay tarjeta.

### 3. Tests

- [x] Agregar test unitario focalizado de `ObtenerGrillaHandler`
  - Verificar `tarjeta_asignada="Blanca"` para performance ejecutada.
  - Verificar `tarjeta_asignada=None` para performance sin tarjeta.

- [x] Agregar o extender test de integración/API
  - Verificar que el JSON de `/grilla` incluye el campo `tarjeta_asignada`.

- [x] Validar frontend con `npm run build`.

### 4. Quality gates y reporte

- [x] Ejecutar tests focalizados backend.
- [x] Ejecutar build frontend.
- [x] Ejecutar `codeguard` / quality gate aplicable.
- [x] Generar `docs/reports/US-ADJ-7.2-report.md`.

---

## Riesgos

- El endpoint serializa manualmente el DTO, por lo que agregar el campo al dataclass no
  alcanza: hay que actualizar `router.py`.
- La UI actual usa `rankingMap` para mostrar resultado final, pero el color de auditoría
  debe salir de `/grilla` para no depender de ranking disponible.
- `TipoTarjeta.Amarilla` puede aparecer en estado `EnRevision`; la spec pide fallback
  neutro para revisión/sin tarjeta.

---

## Validación mínima esperada

```bash
pytest tests/unit/competencia/application/test_obtener_grilla_handler.py
pytest tests/integration/competencia/test_grilla_tarjeta_asignada_api.py
cd frontend && npm run build
```

---

*Creado: 2026-04-19 — Fase 2 abreviada para fix BUG-SP4-004*
