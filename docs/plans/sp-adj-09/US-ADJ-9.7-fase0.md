# Fase 0 - Validacion de Contexto - US-ADJ-9.7

## Contexto Validado

**Historia de Usuario:** `US-ADJ-9.7` - Declarar AP durante inscripción como precondición de preparación
**Producto:** `ataraxiadive`
**Puntos estimados:** 3
**Prioridad:** Alta
**Tipo:** ajuste transversal de dominio + backend + frontend

## Fuentes verificadas

- `docs/specs/sp-adj-09/US-ADJ-9.7.md`
- `docs/contexto/ATARAXIADIVE-CONTEXT.md`
- `docs/adr/ADR-005-bounded-contexts-ddd-estrategico.md`
- `docs/adr/ADR-006-estructura-bc-first.md`
- `docs/design/architecture.md`
- `docs/design/domain-model.md`
- `CLAUDE.md`
- `pyproject.toml`

## Arquitectura y convenciones

- El proyecto sigue arquitectura hexagonal DDD BC-first y esta US cruza `registro`, `torneo`, `competencia` y `frontend`.
- La fuente primaria del AP debe vivir en `registro`; `torneo` solo valida la completitud para la transición de fase.
- `competencia` puede consumir o proyectar AP para operación, pero no debe seguir tratándolo como dato originado en performances manuales.
- Se mantiene la regla de puertos entre BCs: no introducir imports directos entre dominios.

## Alcance tecnico confirmado

Artefactos de impacto principal identificados:

- `src/registro/`
- `src/torneo/application/commands/transicionar_torneo.py`
- `src/competencia/application/commands/generar_grilla.py`
- `src/registro/api/router.py`
- `frontend/src/components/organizador/InscriptosPanel.tsx`
- `frontend/src/components/organizador/GrillaPanel.tsx`

Hallazgos iniciales:

- La spec formaliza un desalineamiento ya observado entre inscripción, preparación y generación de grilla.
- Hay antecedentes directos en `US-5.5.1` y `US-5.5.2`, por lo que conviene revisar contratos ya existentes antes de mover la fuente primaria.
- La migración debe preservar torneos ya preparados bajo el esquema anterior sin quebrar lectura o generación de grillas.

## Quality Gates

- `tests/` existe con `features/`, `integration/`, `unit/` y `conftest.py`.
- `pyproject.toml` define pytest, cobertura y configuración de CodeGuard/DesignReviewer.
- Para esta US aplican pruebas backend, integración HTTP y build/lint del frontend si los cambios tocan React.

## Riesgos y focos de implementacion

- Evitar duplicar la verdad del AP entre `registro` y `competencia` sin una regla clara de precedencia.
- Mantener consistente el cierre de inscripción en backend y la señalización de faltantes en UI.
- Resolver el consumo de AP para grilla sin introducir acoplamientos directos entre BCs.

## Listo para Fase 1

- Spec localizada y consistente con el sprint.
- Contexto de arquitectura y calidad validado.
- Alcance técnico principal identificado para backend, dominio y frontend organizador.
