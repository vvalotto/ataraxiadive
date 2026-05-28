# Administrar inscriptos

La sección **Inscriptos** muestra todos los atletas inscriptos al torneo con sus disciplinas y el estado de su AP (Announced Performance).

## La tabla de inscriptos

Las solapas superiores permiten filtrar por disciplina (**TODAS**, **DBF**, **DNF**, **DYN**, **STA**). Cada fila muestra:

| Columna | Descripción |
|---------|-------------|
| **Atleta** | Apellido y nombre |
| **Club** | Club al que pertenece |
| **Categoría** | Grupo etario y género (ej: Master M, Junior F) |
| **Estado** | Estado de la inscripción — ACEPTADO en verde, RECHAZADO en rojo |
| **Anuncio** | AP declarada para la disciplina activa (ej: "90 m") |

![Tabla de inscriptos con disciplina DBF seleccionada](../assets/screenshots/portal-organizador/inscriptos.png)

!!! info "Estado del AP"
    Mientras el torneo esté en **Inscripciones abiertas**, el AP puede editarse. Una vez cerradas las inscripciones, el valor queda fijo para la generación de la grilla.

## Ver el detalle de un inscripto

Hacé clic en cualquier fila para abrir el panel lateral con el detalle completo del atleta:

- **Categoría y club**
- **Brevet** (número de licencia de apnea)
- **DNI** y **Teléfono**
- **Estado de la inscripción** (ACEPTADO / RECHAZADO)
- Botones **Aceptar** y **Rechazar**

![Panel lateral con el detalle de inscripción de un atleta](../assets/screenshots/portal-organizador/inscripto-detalle.png)

## Aceptar o rechazar inscripciones

Desde el panel lateral podés cambiar el estado de aceptación de cada inscripción:

- **Aceptar** — la inscripción queda confirmada
- **Rechazar** — el atleta no aparecerá en la grilla

El badge de estado (ACEPTADO / RECHAZADO) se actualiza inmediatamente en la tabla.

## Ingresar o modificar el AP

Si necesitás corregir el AP de un atleta mientras las inscripciones están abiertas, podés editarlo directamente en la celda de la columna **Anuncio**:

1. Hacé clic en la celda del AP de la disciplina correspondiente
2. Ingresá el valor (formato `mm:ss` para tiempos como STA/SPE, metros con coma decimal para DYN/DNF/DBF, ej: `2:30`, `80,5`)
3. El valor se guarda automáticamente

!!! warning "El AP solo se puede modificar con inscripciones abiertas"
    Una vez que el torneo pasa a **Preparación**, los AP quedan fijos para la generación de la grilla.
