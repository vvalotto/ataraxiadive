# Registrar una performance

El flujo de registro guía al juez paso a paso desde la llamada del atleta hasta la confirmación del resultado. El indicador de pasos en la parte superior muestra el progreso.

## Paso 1 — Llamada

Confirmá la llamada del atleta presionando **Llamar atleta**. Esto habilita la performance en el sistema e indica que la ventana de OT comenzará próximamente.

## Paso 2 — Confirmar presencia

Verificá que el atleta está en cámara y listo para iniciar:

- **Continuar** — el atleta está presente, avanzar al OT
- **DNS — No se presenta** — registrar que el atleta no se presentó al OT

!!! info "DNS"
    El DNS (Did Not Start) se registra definitivamente. La performance queda cerrada como DNS y no puede modificarse.

## Paso 3 — OT (Official Top)

La pantalla muestra el OT programado del atleta. El flujo tiene dos momentos:

1. Presioná **Iniciar ventana OT** cuando corresponda abrir la ventana de 30 segundos
2. Cuando el atleta inicia la inmersión, presioná el botón de inicio de performance:
   - **"Vías respiratorias en agua"** para disciplinas de apnea estática (STA)
   - **"Atleta inicia"** para disciplinas dinámicas y en profundidad

## Paso 4 — Performance en curso

La performance está activa. En este paso tenés dos opciones:

- **Finalizar performance** — el atleta completó su intento, avanzar a la asignación de tarjeta
- **BKO — Black-out** — el atleta perdió el conocimiento

### Registrar un BKO

Si el atleta sufre un black-out, el flujo cambia a modo BKO:

1. Ingresá la marca alcanzada antes del BKO (metros y centímetros para disciplinas de distancia; no aplica para STA)
2. Confirmá el motivo de descalificación (preseleccionado según el tipo: **BKO_SUBACUATICO** o **BKO_SUPERFICIE**)
3. Presioná **Confirmar BKO** para registrar la tarjeta roja automática

## Paso 5 — Asignar tarjeta

Seleccioná el resultado de la performance:

| Tarjeta | Descripción |
|---------|-------------|
| **Blanca** | Performance válida sin infracciones |
| **Blanca con penalizaciones** | Performance válida con infracciones técnicas — el RP se descuenta según cantidad de penalizaciones |
| **Amarilla** | Resultado en revisión — queda pendiente hasta que el comité resuelva |
| **Roja** | Descalificación — requiere seleccionar el motivo (MotivoDQ) |

### Penalizaciones (tarjeta Blanca con penalizaciones)

Disponible en disciplinas que lo permiten. Indicá la cantidad de penalizaciones; el sistema calcula el descuento automáticamente (cada penalización resta 3 metros o equivalente según disciplina).

### Motivo de descalificación (tarjeta Roja)

| Código | Significado |
|--------|-------------|
| BKO_SUPERFICIE | Black-out en superficie |
| BKO_SUBACUÁTICO | Black-out subacuático |
| NO_PROTOCOLO | No cumplió el protocolo de superficie |
| INFRACCIÓN_TÉCNICA | Infracción técnica grave |
| NO_INICIO_VENTANA | No inició dentro de la ventana OT |
| SALIDA_FALSO | Salida falsa |

## Paso 6 — Registrar RP y confirmar marca

Ingresá la Realized Performance (RP) medida:

- **Metros y centímetros** para disciplinas de distancia (DNF, DYN, CWT, etc.)
- **Minutos y segundos** para apnea estática (STA)

Presioná **Confirmar marca** para cerrar la performance.

## Resolver revisión (tarjeta amarilla)

Si la performance quedó en tarjeta amarilla, el comité de jueces la resolverá. Una vez resuelta, el sistema presenta el paso de **Resolver revisión** donde podés confirmar el resultado final: Blanca, Blanca con penalizaciones, o Roja con motivo.

## Performance completada

Al finalizar el flujo, la pantalla muestra el resultado:

- Blanca o Blanca con penalizaciones: fondo verde con la marca registrada
- Amarilla (en revisión): fondo ámbar
- Roja (descalificada): fondo rojo con el motivo
- DNS: fondo gris

Presioná **Siguiente atleta** para volver a la grilla y continuar con el próximo.
