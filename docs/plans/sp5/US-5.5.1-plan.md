# Plan de Implementación — US-5.5.1: Registro de APs

**Fecha:** 2026-04-25
**Branch:** `feature/US-5.5.1-registro-aps`
**Puntos:** 3 | **Estimación total:** 50 min

---

## Contexto de diseño

El `RegistrarAPHandler` + `RegistrarAPCommand` ya existen en
`src/competencia/application/commands/registrar_ap.py`. Esta US
únicamente los expone via HTTP y construye la UI del atleta.

**Nota de UI:** La grilla solo existe DESPUÉS de que el organizador ejecuta
`GenerarGrilla`. Antes de eso, `fetchGrillaCompetencia` devuelve `[]`.
Por tanto, la detección de "AP ya registrado" en la UI es mediante estado
local React (optimistic update post-201), no desde la grilla.

---

## Tareas

### T1 — Backend: schema (5 min)
Archivo: `src/competencia/api/schemas.py`

Agregar:
```python
class RegistrarAPRequest(BaseModel):
    disciplina: str
    valor_ap: Decimal
    unidad: str
```

### T2 — Backend: dependency + endpoint (15 min)
Archivo: `src/competencia/api/router.py`

**Imports a agregar:**
- `from competencia.application.commands.registrar_ap import RegistrarAPHandler, RegistrarAPCommand, APYaRegistrado, GrillaYaConfirmadaError, PlazoAPVencidoError`
- `from shared.api.dependencies import JuezDep, OrganizadorDep, AtletaDep` (extender import existente)
- `from competencia.application.commands.registrar_resultado import UnidadIncompatible`

**Dependency factory:**
```python
def get_registrar_ap_handler(
    event_store: EventStoreDep,
    disciplina_descriptor: DisciplinaDescriptorDep,
) -> RegistrarAPHandler:
    return RegistrarAPHandler(
        event_store,
        CompetenciaEstadoAdapter(event_store),
        disciplina_descriptor,
    )

RegistrarAPHandlerDep = Annotated[RegistrarAPHandler, Depends(get_registrar_ap_handler)]
```

**Endpoint:**
```
POST /{competencia_id}/registrar-ap
Auth: AtletaDep
Body: { disciplina, valor_ap, unidad }
participante_id: user["sub"] del JWT

201 → { performance_id: UUID }
409 → { detail: "..." }  (AP duplicado, grilla confirmada, plazo vencido)
422 → { detail: "..." }  (valor inválido, unidad incompatible)
```

### T3 — Frontend: API function (10 min)
Archivo: `frontend/src/api/competencia.ts`

```typescript
export interface RegistrarAPParams {
  competenciaId: string
  disciplina: string
  valorAp: number
  unidad: string
}

export interface RegistrarAPResponse {
  performance_id: string
}

export async function registrarAP(params: RegistrarAPParams): Promise<RegistrarAPResponse>
```

### T4 — Frontend: UI panel (20 min)
Archivo: `frontend/src/pages/atleta/AtletaDashboardPage.tsx`

Agregar componente `MisAPsPanel` que:
- Recibe `torneo` + `atletaId`
- Llama `fetchCompetenciasPorTorneo(torneo.torneo_id)` 
- Por cada competencia: muestra disciplina + formulario de AP o badge "AP registrado"
- Estado local `apRegistrado` por competencia para optimistic update post-201
- Formulario: campo numérico `valor_ap` + select `unidad` + botón "Registrar AP"
- Errores inline: 409 ("Ya registrado") / 422 (mensaje backend)

La sección se integra en cada `article` del torneo (debajo de `InscripcionPanel`).

---

## Orden de implementación

T1 → T2 → T3 → T4

## Quality gates post-implementación

- `pytest tests/unit/competencia/api/ -x` — tests endpoint
- `pytest tests/integration/competencia/ -x` — integración
- `pytest tests/features/ -k "5.5.1" -x` — BDD
- `cd frontend && npm run build` — TypeScript sin errores
- `codeguard src/competencia/` — pylint ≥ 8.0
