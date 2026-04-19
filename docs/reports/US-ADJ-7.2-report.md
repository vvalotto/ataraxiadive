# Reporte de Implementación: US-ADJ-7.2

| Campo | Valor |
|-------|-------|
| **Sprint** | SP-ADJ-07 |
| **Tipo** | Fix API + frontend |
| **Branch** | `feature-US-ADJ-7.2-tarjeta-grilla` |
| **Estado** | ✅ Implementada |
| **Fecha** | 2026-04-19 |

---

## Resumen

`GET /competencia/{competencia_id}/grilla` ahora expone `tarjeta_asignada` para cada
entrada de grilla. La pantalla de auditoría de competencia consume ese campo para
distinguir visualmente tarjetas blancas, blancas con penalizaciones y rojas.

No se agregaron comandos, eventos ni cambios de dominio. El dato ya existía en
`Performance.tarjeta`; la US lo proyecta en el read model y lo serializa por API.

---

## Componentes modificados

- `src/competencia/application/queries/obtener_grilla.py`
  - `EntradaGrillaDTO.tarjeta_asignada: str | None`
  - `_PerformanceProjection.tarjeta_asignada: str | None`
  - Proyección desde `performance.tarjeta.value`

- `src/competencia/api/router.py`
  - Serialización de `tarjeta_asignada` en `/grilla`

- `frontend/src/api/competencia.ts`
  - `GrillaAtletaDto.tarjeta_asignada: string | null`

- `frontend/src/pages/organizador/AuditoriaCompetenciaPage.tsx`
  - Estilos condicionales por `tarjeta_asignada`

---

## Tests y validaciones

| Validación | Resultado |
|------------|-----------|
| `pytest tests/unit/competencia/application/test_obtener_grilla_handler.py` | ✅ 1 passed |
| `pytest tests/integration/competencia/test_grilla_tarjeta_asignada_api.py` | ✅ 1 passed |
| `npm run build` en `frontend/` | ✅ passed |
| `codeguard src/competencia --format json` | ✅ errors=0 · warnings=5 |

Reporte de calidad:
`quality/reports/codeguard/US-ADJ-7.2-codeguard.json`

### BDD

Se creó feature mínimo:
`tests/features/US-ADJ-7.2-tarjeta-asignada-grilla.feature`

Waiver: no se agregaron step definitions nuevos porque la US es un fix acotado de
proyección/API/UI. La validación ejecutable quedó cubierta por test unitario de query,
test HTTP de serialización y build TypeScript.

---

## Criterios de aceptación

- [x] La grilla incluye `tarjeta_asignada="Blanca"` para atleta ejecutado con tarjeta blanca.
- [x] La grilla incluye `tarjeta_asignada=null` para atleta sin tarjeta final.
- [x] El endpoint HTTP serializa el nuevo campo.
- [x] El frontend usa `tarjeta_asignada` para aplicar estilos visuales por tarjeta.

---

## Observaciones

- `codeguard` informa 5 warnings en el BC `competencia`; no son introducidos por esta US.
- `npm run build` actualizó artefactos en `frontend/dist/`, consistente con el estado actual
  del repo donde `dist/` ya está presente.

