# Gestionar el torneo activo (Panel)

El **Panel** es la vista central desde donde controlás el ciclo de vida del torneo: avanzás entre estados, revisás disciplinas y manejás las transiciones de fase.

## Seleccionar el torneo activo

Al entrar al **Panel**, si todavía no seleccionaste un torneo, la plataforma te muestra un selector. Elegí el torneo con el que querés trabajar — el torneo queda "activo" y todas las secciones (Inscriptos, Grilla, Jueces, etc.) operan sobre él.

## Datos generales del torneo

El panel muestra:

- **Nombre del torneo**
- **Fecha de inicio**
- **Sede**
- **Estado actual** — con un selector para avanzar al siguiente estado
- **Ciudad y país**
- **Categorías** (JUNIOR / SENIOR / MASTER)

## Disciplinas

La columna derecha lista las disciplinas del torneo con su estado:

| Estado de disciplina | Significado |
|----------------------|-------------|
| **Pendiente** | La competencia aún no fue creada (ocurre automáticamente al generar la grilla) |
| **Activa** | La competencia está en ejecución (el juez está registrando performances) |
| **Cerrada** | La competencia finalizó — resultados disponibles |

Cada tarjeta de disciplina también indica si tiene juez asignado o no.

## Avanzar el estado del torneo

Usá el selector de **Estado** en la sección "Datos generales" para seleccionar el próximo estado y luego hacé clic en **Guardar cambios**.

Las transiciones posibles son:

| Desde | Hacia |
|-------|-------|
| Creado | Inscripciones abiertas |
| Inscripciones abiertas | Preparación |
| Preparación | En ejecución |
| En ejecución | Premiación |
| Premiación | Cerrado |

!!! warning "Condición para pasar a Premiación"
    La transición a **Premiación** solo se habilita cuando **todas las disciplinas tienen su competencia cerrada**. Si alguna sigue activa, el panel te lo indica con un aviso en ámbar mostrando cuáles disciplinas faltan.

## Cancelar un torneo

En cualquier estado no terminal, podés cancelar el torneo usando el botón **Cancelar torneo** en la parte inferior del panel. El sistema te pedirá que escribas el nombre exacto del torneo para confirmar la acción.

!!! danger "La cancelación es irreversible"
    Un torneo cancelado no puede volver a activarse.
