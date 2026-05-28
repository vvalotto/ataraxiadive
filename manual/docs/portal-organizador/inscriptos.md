# Administrar inscriptos

La sección **Inscriptos** muestra todos los atletas inscriptos al torneo con sus disciplinas y el estado de su AP (Announced Performance).

## La tabla de inscriptos

Cada fila de la tabla representa un atleta con:

- **Nombre** — apellido y nombre del atleta
- **Club** — club al que pertenece
- **Categoría** — grupo etario (JUNIOR / SENIOR / MASTER)
- **Estado de la inscripción** — activa, pendiente de aceptación, rechazada
- **Disciplinas** — lista de disciplinas en las que está inscripto
- **AP por disciplina** — valor del AP declarado (o "Pendiente" si todavía no lo declaró)

!!! info "Estado del AP"
    Mientras el torneo esté en **Inscripciones abiertas**, el AP puede estar pendiente o declarado.
    Una vez cerradas las inscripciones, la columna muestra el valor final (estado "cerrado").

## Ver el detalle de un inscripto

Hacé clic en cualquier fila para abrir el panel lateral con el detalle completo del atleta:

- Datos personales: nombre, documento, teléfono, club, categoría
- Documentos adjuntos: podés descargar los archivos que el atleta subió al inscribirse
- **Aceptar** o **Rechazar** la inscripción

## Ingresar o modificar el AP

Si el atleta no declaró su AP o necesitás corregirlo mientras las inscripciones están abiertas, podés editarlo directamente en la tabla:

1. Hacé clic en la celda del AP de la disciplina correspondiente
2. Ingresá el valor (formato `mm:ss` para tiempos como STA/SPE, metros con coma decimal para DYN/DNF, ej: `2:30`, `80,5`)
3. El valor se guarda automáticamente

!!! warning "El AP solo se puede modificar con inscripciones abiertas"
    Una vez que el torneo pasa a **Preparación**, los AP quedan fijos para la generación de la grilla.

## Aceptar o rechazar inscripciones

Podés revisar cada inscripción individualmente desde el panel lateral:

- **Aceptar** — la inscripción queda confirmada
- **Rechazar** — la inscripción queda marcada como rechazada; el atleta no aparecerá en la grilla

El estado de aceptación se muestra como un badge en la tabla (ACEPTADO / RECHAZADO).
