# Documentación — AtaraxiaDive

> Estado documental: derivado
> Resume información de: [`inventario/DOCUMENTATION-MAP.md`](inventario/DOCUMENTATION-MAP.md) e [`inventario/FUENTES-DE-VERDAD-DOCUMENTAL.md`](inventario/FUENTES-DE-VERDAD-DOCUMENTAL.md)
> Ante contradicción, consultar la fuente principal.

Punto de entrada a la documentación del proyecto. Para **saber qué leer y qué documento manda** en cada tema, empezar por:

- 🧭 [**Mapa documental**](inventario/DOCUMENTATION-MAP.md) — qué leer según lo que necesites.
- ⚖️ [**Fuentes de verdad**](inventario/FUENTES-DE-VERDAD-DOCUMENTAL.md) — autoridad por tema y jerarquía documental (única fuente de la jerarquía).

> La memoria operativa del proyecto vive en [`CLAUDE.md`](../CLAUDE.md) (raíz). El **manual de usuario** se construye con MkDocs en [`manual/`](../manual/) y se publica en GitHub Pages: <https://vvalotto.github.io/ataraxiadive/>.

## Qué hay en cada carpeta

| Carpeta | Contenido | Vigencia |
|---|---|---|
| [`architecture/`](architecture/) | Arquitectura vigente (vistas C4: contexto, contenedores, por BC, transversales, despliegue). | **Fuente vigente de arquitectura.** |
| [`adr/`](adr/) | Decisiones arquitectónicas (el *por qué* y sus trade-offs). | Vigente / evidencia. |
| [`design/`](design/) | Modelado DDD: `domain-model.md`, `context-map.md`. `architecture.md` es C4 inicial (histórico). | Modelado de referencia. |
| [`dominio/`](dominio/) | Elicitación del dominio de torneos de apnea, atributos de calidad, RF. | Narrativa de dominio. |
| [`requirements/`](requirements/) | `vision.md` — propósito del producto. | Vigente. |
| [`iedd/`](iedd/) | Marco metodológico IEDD. | Vigente / metodológico. |
| [`plans/`](plans/) | `WORKFLOW-DESARROLLO.md` (vigente) + planes por SP/INC/ADJ. | Mixto (ver cada plan). |
| [`specs/`](specs/) | US-IEDD (precondición, postcondición, invariantes). | Especificación detallada. |
| [`traceability/`](traceability/) | `matrix.md` — trazabilidad RF → BC → INC → US → estado. | Vigente. |
| [`contexto/`](contexto/) | Experimento (`PLAN-EXPERIMENTO.md`), HITOs, análisis metodológicos. | Evidencia del experimento. |
| [`metricas/`](metricas/) | Métricas estructurales del código. | Evidencia técnica. |
| [`reports/`](reports/) | Reportes de calidad y UAT. | Evidencia técnica. |
| [`inventario/`](inventario/) | Autoridad documental y navegación (FUENTES, MAP, INVENTARIO). | Vigente. |

## Documentos sueltos en `docs/`

- [`POLITICA-MEJORA-DOCUMENTAL.md`](POLITICA-MEJORA-DOCUMENTAL.md) — política de mantenimiento documental.
- [`PLAN-ADECUACION-DOCUMENTAL.md`](PLAN-ADECUACION-DOCUMENTAL.md) — plan de adecuación documental.
- [`WBS-ATARAXIADIVE.md`](WBS-ATARAXIADIVE.md) — estructura de desglose del trabajo.
