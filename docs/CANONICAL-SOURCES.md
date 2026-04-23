# Fuentes Canonicas

Este indice define que documento consultar primero cuando dos artefactos dicen
cosas distintas.

| Tema | Fuente primaria | Fuentes de apoyo |
|------|-----------------|------------------|
| Estado del proyecto | `.cm/baselines/` | `README.md`, `CLAUDE.md` |
| Alcance SP5 | `docs/plans/sp5/PLAN-SP5.md` | `.cm/baselines/BL-005-draft.md` |
| Arquitectura vigente | `docs/architecture/` | `docs/adr/`, routers FastAPI |
| Contrato HTTP observable | `src/*/api/router.py` / OpenAPI generado | docs de arquitectura si existen |
| Trazabilidad funcional | `docs/traceability/matrix.md` | `docs/specs/`, docs de dominio |
| Dominio y elicitacion original | `docs/dominio/` | `docs/design/`, ADRs |
| Diseño DDD historico | `docs/design/` | `docs/architecture/` para estado actual |
| US implementadas | `docs/specs/` + `.cm/baselines/` | reportes en `docs/reports/` y `quality/reports/` |

## Estados documentales

- **Vigente:** fuente operativa actual para planificar o implementar.
- **Referencia:** conserva conocimiento util, pero debe contrastarse con la
  fuente primaria del tema.
- **Historico:** documenta una decision, plan o contrato de un momento anterior.
- **Superseded:** reemplazado por otra fuente explicita; no usar como guia
  operativa sin verificar.

