# Waiver BDD — US-6.2.6

**US:** US-6.2.6 — Crear pagina de Podios  
**Fecha:** 2026-05-06  
**Tipo:** Frontend puro  

---

## Motivo

`US-6.2.6` modifica exclusivamente React/Vite:

- `frontend/src/pages/organizador/PodiosPage.tsx`
- `frontend/src/pages/organizador/ResultadosPage.tsx`
- `frontend/src/components/organizador/OrganizadorLayout.tsx`
- `frontend/src/App.tsx`

No toca `src/`, contratos API, persistencia ni reglas de dominio. El repositorio no tiene harness automatizado de browser para ejecutar escenarios Gherkin de UI React.

---

## Contrato BDD

El contrato fue materializado en:

- `tests/features/US-6.2.6-pagina-podios.feature`

Los escenarios cubren:

- Acceso a `/organizador/podios?torneo_id={id}`.
- Ausencia de podios en `/organizador/resultados?torneo_id={id}`.
- Selector de torneo cuando `/organizador/podios` no recibe `torneo_id`.
- Item de navegacion `Podios` con `torneo_id` activo.

---

## Validacion Sustituta

- `cd frontend && npm run build`
- `cd frontend && npm run lint`
- `git diff --check`

Ademas, el diff confirma que `ResultadosPage.tsx` ya no importa ni renderiza `PodiosSection`, y que `PodiosPage.tsx` concentra la logica de `fetchOverall` y podios por disciplina.
