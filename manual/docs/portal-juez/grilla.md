# Ver la grilla

La sección **Grilla** muestra el listado de atletas asignados al juez en la disciplina seleccionada, ordenados por estado de ejecución.

## Acceder a la grilla

Desde **Mis Asignaciones**, tocá el botón de la disciplina que está activa. Las disciplinas inactivas (no en ejecución) aparecen deshabilitadas.

## La tabla de atletas

Cada fila representa un atleta asignado y muestra:

| Dato | Descripción |
|------|-------------|
| **Posición y andarivel** | Orden en la grilla y andarivel asignado |
| **Nombre** | Apellido y nombre del atleta |
| **AP** | Announced Performance declarada (en metros o mm:ss) |
| **Estado** | Estado actual de la performance |

## Estados de las performances

Los atletas se ordenan automáticamente según el estado de su performance:

| Estado | Color | Descripción |
|--------|-------|-------------|
| **Siguiente** | Verde | El próximo atleta en salir |
| **En curso** | Cyan | Performance actualmente en ejecución |
| **Revisión** | Ámbar | Tarjeta amarilla pendiente de resolución |
| **Pendiente** | Gris oscuro | Aún no fue llamado |
| **Finalizada** | Gris atenuado | Performance completada o DNS registrado |

!!! info "Orden automático"
    La grilla se reordena en tiempo real a medida que avanza la competencia. Los atletas finalizados quedan al fondo.

## Registrar una performance

Tocá el nombre del atleta para abrir el flujo de registro de performance. Los atletas en estado **Finalizada** no son seleccionables.

## Modo offline

Si no hay conexión a internet, la grilla se carga desde el cache local. En ese caso aparece un aviso con la antigüedad del cache.

!!! warning "Cache expirado"
    Si el cache tiene más de 24 horas, la aplicación lo indica. Los datos pueden estar desactualizados respecto al estado real del torneo.
