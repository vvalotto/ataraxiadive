---
title: "Registro — Query Handlers"
type: arquitectura-componente
bc: registro
capa: application
tipo_componente: handler
responsabilidad: "5 handlers de consulta: perfiles por rol, inscriptos por torneo, completitud de APs"
interfaces_out:
  - AtletaRepositoryPort
  - JuezRepositoryPort
  - OrganizadorRepositoryPort
  - InscripcionRepositoryPort
adr_refs: [ADR-005]
last_updated: "2026-05-23"
sources:
  - src/registro/application/queries/obtener_atleta.py
  - src/registro/application/queries/obtener_juez.py
  - src/registro/application/queries/obtener_organizador.py
  - src/registro/application/queries/listar_inscriptos.py
  - src/registro/application/queries/verificar_completitud_ap.py
us_origen:
  - US-5.1.3-inscriptos-panel-lista-de-atletas-con-estado-ap
  - US-5.5.2-vista-organizador-inscriptos-con-datos-completos-y
  - US-5.7.1-mis-torneos-lista-de-torneos-inscriptos-del-atleta
tests:
  - tests/features/US-5.1.3-vista-inscriptos-ap.feature
  - tests/features/US-5.5.2-organizador-inscriptos-ap.feature
  - tests/integration/registro/test_inscriptos_detalle_endpoint.py
  - tests/features/US-5.7.1-mis-torneos.feature
---

# Query Handlers — BC Registro

Handlers de sólo lectura. Todos son clases simples con un método `handle()`.

---

## ObtenerAtletaHandler

```python
async def handle(self, atleta_id: UUID) -> Atleta
```

`find_by_id()` o lanza `AtletaNoEncontrado`.

---

## ObtenerJuezHandler

```python
async def handle(self, email: str) -> Juez
```

Lookup por email (no por UUID). Lanza `JuezNoEncontrado`. La búsqueda por email es consistente con el modelo donde el JWT lleva el email como identificador primario de usuario.

---

## ObtenerOrganizadorHandler

```python
async def handle(self, email: str) -> Organizador
```

Idéntico al patrón de Juez. Lanza `OrganizadorNoEncontrado`.

---

## ListarInscriptosHandler

```python
async def handle(self, torneo_id: UUID) -> list[Inscripcion]
```

`find_active_by_torneo(torneo_id)` — retorna sólo inscripciones en estado `ACTIVA`.

---

## VerificarCompletitudAPHandler

Handler de validación cruzada — el más complejo de los queries.

```python
async def obtener_faltantes(self, torneo_id: UUID) -> list[APFaltante]
```

Recorre todas las inscripciones activas del torneo y detecta atletas que no tienen AP declarado para todas sus disciplinas. Retorna `list[APFaltante]` donde cada item tiene `atleta_nombre` y `disciplina`.

Usado por `build_cierre_inscripcion_precondition()` en [[router-registro]]: BC Torneo llama esta precondición antes de cerrar el período de inscripción, garantizando que todos los atletas hayan declarado sus APs.

---

## Relaciones

**Contenedor:** [[arquitectura/registro]]

- Instanciados directamente en [[router-registro]]
- Usan [[sqlite-repositories-registro]] como fuente de datos
- `VerificarCompletitudAPHandler` es invocado indirectamente por BC Torneo vía el callback de precondición expuesto en [[router-registro]]

## Código fuente

| Archivo | Descripción |
|---|---|
| `src/registro/application/queries/obtener_atleta.py` | Query: ObtenerAtletaHandler |
| `src/registro/application/queries/obtener_juez.py` | Query: ObtenerJuezHandler |
| `src/registro/application/queries/obtener_organizador.py` | Query: ObtenerOrganizadorHandler |
| `src/registro/application/queries/listar_inscriptos.py` | Query: ListarInscriptosHandler |
| `src/registro/application/queries/verificar_completitud_ap.py` | Query: VerificarCompletitudAPHandler |
