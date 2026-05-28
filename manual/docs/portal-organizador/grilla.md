# Manejar la grilla

La sección **Grilla** permite generar, revisar, ajustar y confirmar el orden de salida de los atletas por disciplina. La grilla solo se puede operar mientras el torneo esté en estado **Preparación**.

## Seleccionar la disciplina

Usá el selector de disciplina en la parte superior para elegir la disciplina que querés gestionar. La grilla y el estado mostrados corresponden a la disciplina seleccionada.

## Generar la grilla

Si la disciplina todavía no tiene competencia ni grilla, el panel muestra el formulario de configuración:

| Campo | Descripción |
|-------|-------------|
| **Fecha del primer OT** | Fecha en que comienza la competencia (debe estar dentro del rango del torneo) |
| **Primer OT** | Hora del primer Official Top (formato `hh:mm`) |
| **Intervalo OT** | Minutos entre cada atleta (ej: 8 minutos) |
| **Andariveles** | Cantidad de andariveles disponibles simultáneamente |

Hacé clic en **Generar grilla** para crear la competencia y distribuir los atletas automáticamente según sus AP (descendente de mayor a menor).

!!! info "Orden de la grilla"
    Los atletas se ordenan por AP declarada de mayor a menor. Si un atleta no declaró AP, queda al final del orden.

## Revisar la grilla generada

Una vez generada, la tabla muestra:

- **OT** — hora del Official Top de cada atleta
- **Andarivel** — andarivel asignado
- **Atleta** — apellido y nombre
- **AP** — Announced Performance declarada
- **Categoría** — grupo etario

## Ajustar el orden

Podés reordenar los atletas antes de confirmar la grilla:

- Usá los **botones de flecha** (↑ ↓) para mover un atleta hacia arriba o abajo
- Los OT se recalculan automáticamente al mover posiciones

## Regenerar la grilla

Si necesitás volver a generar la grilla desde cero (por ejemplo, si llegaron nuevos AP después de la primera generación), hacé clic en **Regenerar grilla** e ingresá nuevamente los parámetros de configuración.

!!! warning "Regenerar borra los ajustes manuales"
    Si reorganizaste el orden manualmente, regenerar la grilla reemplaza esos cambios con el orden automático por AP.

## Confirmar la grilla

Una vez que el orden es correcto, hacé clic en **Confirmar grilla**. Esto marca la competencia como lista para la ejecución.

!!! info "Grilla confirmada"
    Una vez confirmada, la grilla queda en modo solo lectura. No se puede modificar después de iniciada la ejecución.
