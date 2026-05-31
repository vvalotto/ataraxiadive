---
title: "Resultados — Router FastAPI"
type: arquitectura-componente
bc: resultados
capa: api
tipo_componente: router
responsabilidad: "API HTTP del BC Resultados: 3 endpoints (ranking, overall, export) + configuración de dependencias cross-BC"
interfaces_out: []
adr_refs: [ADR-005]
last_updated: "2026-05-23"
sources:
  - src/resultados/api/router.py
us_origen:
  - US-3.5.3-api-get-resultados-{torneo-id}-overall
  - US-6.4.3-corregir-d-05-imports-cross-bc-en-resultados-api-y
---

# Router — BC Resultados

`APIRouter(prefix="/resultados", tags=["resultados"])`

---

## Endpoints

| Método | Path | Auth | Descripción |
|--------|------|------|-------------|
| `GET` | `/{competencia_id}/ranking` | público | Ranking de disciplina — definitivo o provisional |
| `GET` | `/{torneo_id}/overall` | público | Overall calculado del torneo |
| `GET` | `/{torneo_id}/export` | `OrganizadorDep` | Exportación completa en CSV o JSON |

### `GET /{competencia_id}/ranking?disciplina=DNF`

Lógica de fallback:
1. Intenta cargar ranking definitivo de `resultados.db`
2. Si no existe (`calculado=false`): calcula ranking provisional en tiempo real desde `competencia.db`

Response: `{calculado: bool, rankings: [{categoria, entradas: [...]}]}`

Cada entrada incluye: `posicion`, `atleta_id`, `rp`, `unidad`, `tarjeta`, `es_dns`, `en_podio`, `puntos`, `motivo_dq`, `penalizaciones`, `rp_medido`.

### `GET /{torneo_id}/overall`

Response: `{calculado: bool, rankings: [{categoria, entradas: [{posicion, atleta_id, puntos_overall, detalle, en_podio}]}]}`

### `GET /{torneo_id}/export?format=csv|json`

Auth: `OrganizadorDep`. Formato inválido → 400. Torneo no encontrado → 404.
Descarga con `Content-Disposition: attachment; filename="resultados-{torneo_id}.{format}"`.

---

## Dependencias cross-BC (composition root)

El router expone una función de configuración para inyectar dependencias que BC Resultados no puede resolver directamente:

```python
configure_resultados_cross_bc_dependencies(
    competencias_por_torneo_factory=...,  # BC Competencia
    torneo_repository_factory=...,        # BC Torneo
)
```

Esta configuración se aplica en `app.py` (composition root), manteniendo el router agnóstico a los otros BCs.

---

## Inyección de dependencias

Usa FastAPI `Depends()` para construir los handlers:

- `get_ranking_store()` → `SQLiteEventStore("data/resultados.db")`
- `get_competencia_store()` → `SQLiteEventStore("data/competencia.db")`
- `get_atleta_info_adapter()` → `AtletaInfoAdapter()` (lee `registro.db`)
- Handlers construidos via `Depends(get_obtener_ranking_handler)`, etc.

---

## Relaciones

**Contenedor:** [[arquitectura/resultados]]

- Usa [[query-handlers-resultados]] y [[command-handlers-resultados]]
- Accede a `competencia.db`, `registro.db`, `torneo.db` via ACLs cross-BC
- Auth: `OrganizadorDep` de `shared/api/dependencies.py`

## Código fuente

| Archivo | Descripción |
|---|---|
| `src/resultados/api/router.py` | Router FastAPI — endpoints HTTP del BC |
