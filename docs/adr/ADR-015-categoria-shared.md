# ADR-015: Ubicación del Value Object `Categoria`

Fecha: 2026-05-02
Estado: Accepted

Contexto

El value object `Categoria` (StrEnum) está definido actualmente en `src/registro/domain/value_objects/categoria.py` pero es importado y usado por múltiples bounded contexts (por ejemplo `resultados` y `competencia`). Esto introduce acoplamiento innecesario entre BCs y dificulta la reusabilidad.

Decisión

Mover `Categoria` a `shared/domain/value_objects/categoria.py` y exponerlo como nguồn común para los BCs que lo necesiten.

Racional

- `Categoria` es un value object de dominio (tipo simple) que representa una noción transversal del dominio y no pertenece exclusivamente al BC `registro`.
- Colocarlo en `shared` reduce acoplamiento y mejora claridad arquitectónica acorde a la regla hexagonal del proyecto.

Consecuencias

- Código que importe `registro.domain.value_objects.categoria` deberá cambiar a `shared.domain.value_objects.categoria`.
- Requiere un refactor controlado (mover fichero y actualizar imports). Se recomienda aplicar en SP6 como tarea/PR única para minimizar ruido.
- Si por motivos prácticos se decide mantenerlo en `registro`, documentar la decisión en un ADR y aceptar el acoplamiento.

Acción recomendada

1. Crear este ADR (hecho).
2. Planear y ejecutar un refactor en SP6: mover archivo a `shared/domain/value_objects/` y actualizar imports (tests incluidos).
3. Si se opta por no mover, crear ADR justificando la decisión y documentar el impacto.

Referencias

- docs/design/architecture.md
- docs/architecture/10-bc-competencia.md

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
