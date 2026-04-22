# US-5.2.1 — Documentacion Funcional

## Vista maestro-detalle de ejecucion

El tab `Ejecucion` del panel organizador deja de mostrar solamente competencias ya iniciadas.
Ahora funciona como una vista maestro-detalle:

- **Maestro:** lista todas las disciplinas configuradas del torneo.
- **Detalle:** muestra el estado operativo y datos de la disciplina seleccionada.

La fuente primaria del maestro es `GET /torneos/{torneo_id}/disciplinas`. La proyeccion
`GET /competencia?torneo_id={id}` se usa para enriquecer cada disciplina cuando ya existe una
competencia materializada.

## Estados operativos

La UI deriva un estado operativo por disciplina:

| Estado | Significado |
|---|---|
| `Configurar competencia` | La disciplina existe en el torneo pero aun no tiene competencia. |
| `Confirmar grilla antes de habilitar` | La competencia existe pero la grilla no esta confirmada. |
| `Asignar juez antes de habilitar` | La grilla esta confirmada pero falta juez asignado. |
| `Lista para iniciar` | La competencia esta confirmada, con grilla confirmada y juez asignado. |
| `En ejecucion` | La competencia ya fue iniciada. |
| `Finalizada` | La competencia cerro y queda en modo lectura. |

## Habilitacion de disciplina

La accion `Habilitar disciplina` se muestra solo cuando el estado operativo es
`Lista para iniciar`.

La accion llama:

```http
POST /competencia/{competencia_id}/iniciar
```

con body:

```json
{
  "disciplina": "DNF",
  "juez_id": "..."
}
```

El `juez_id` proviene de la asignacion del torneo. No se solicita manualmente en esta pantalla.

## Limite de alcance

Esta US no implementa `Finalizar prueba`. Ese cierre manual corresponde a `US-5.2.2`.
