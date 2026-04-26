# Reporte Final - US-5.5.2

**Historia:** US-5.5.2  
**Titulo:** Vista del organizador de inscriptos con estado AP  
**Fecha:** 2026-04-26  
**Estado:** IMPLEMENTADA

---

## Resultado

Se implemento la vista operativa del organizador para inscriptos del torneo con estado AP por disciplina, integrada en la seccion `Inscriptos` de la gestion del torneo.

La solucion corrige los gaps principales de la spec:

- usa nombre y apellido visibles;
- excluye inscripciones canceladas de la lista operativa;
- deja de depender de la grilla para detectar AP;
- muestra `AP pendiente`, `AP declarado` y `AP cerrado`;
- deja la vista en solo lectura visible cuando el torneo ya no esta en inscripcion abierta.

---

## Archivos principales

- `src/registro/api/router.py`
- `src/registro/application/queries/listar_inscriptos.py`
- `src/registro/domain/ports/inscripcion_repository_port.py`
- `src/registro/infrastructure/repositories/sqlite_inscripcion_repository.py`
- `frontend/src/api/registro.ts`
- `frontend/src/components/organizador/InscriptosPanel.tsx`
- `frontend/src/components/organizador/TablaInscriptos.tsx`
- `frontend/src/components/organizador/EstadoAPBadge.tsx`
- `frontend/src/pages/organizador/DetalleTorneoPage.tsx`
- `tests/integration/registro/test_inscriptos_detalle_endpoint.py`

---

## Quality Gates

- `./.venv/bin/pytest tests/integration/registro/test_inscriptos_detalle_endpoint.py -q` -> OK (`2 passed`)
- `npm run lint` en `frontend/` -> OK
- `npm run build` en `frontend/` -> OK

Observaciones:

- El build de Vite reporta warning de chunk grande preexistente, pero no bloquea.
- No se ejecuto browser automation de UX.
- No se corrio `codeguard` especifico de esta US.

---

## Desvios declarados

- La UX global del organizador sigue sin migrar completa al shell dark del prototipo.
- Esta US corrige la vista funcional de inscriptos y su semantica de producto, no el rediseño total del rol.
