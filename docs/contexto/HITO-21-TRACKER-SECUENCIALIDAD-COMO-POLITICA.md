# HITO-21 — La secuencialidad del pipeline incluye al tracker: el registro de fases no es thread-safe y debe tratarse como parte del método

| Campo | Valor |
|-------|-------|
| **Documento** | HITO-21 — Hallazgo metodológico durante US-4.6.1 |
| **Fecha** | 2026-04-16 |
| **Sprint** | SP4 — INC-4.6 — US-4.6.1 |
| **Relacionado** | `docs/plans/WORKFLOW-DESARROLLO.md` · `HITO-16` · `.claude/tracking/tracker_cli.py` · `.claude/tracking/time_tracker.py` |

---

## Contexto

Durante la ejecución de `US-4.6.1` se siguió el pipeline prescriptivo de
`/implement-us`: branch propia, tracker inicializado antes de crear artefactos,
Fase 0, BDD, plan, implementación, tests, documentación y reporte final.

En ese proceso apareció una falla no funcional, pero metodológicamente relevante:
el archivo `.claude/tracking/US-4.6.1-tracking.json` quedó corrupto después de
lanzar operaciones del tracker en paralelo.

El síntoma fue un `JSONDecodeError` al intentar continuar con las fases:

```text
json.decoder.JSONDecodeError: Extra data
```

La causa no fue el dominio ni el código del producto. Fue el propio mecanismo de
tracking del pipeline.

---

## Qué ocurrió realmente

El tracker fue inicializado correctamente y luego recibió operaciones casi
simultáneas de escritura:

- `start-phase`
- `end-phase`
- `start-phase` siguiente

El resultado fue un JSON persistido con contenido duplicado y truncado al final.
Hubo que reparar manualmente el archivo para poder continuar.

Esto mostró que el tracker:

- persiste sobre un único archivo JSON por US
- no usa locking
- no serializa escrituras concurrentes
- asume implícitamente ejecución secuencial

En otras palabras: **el tracker no es thread-safe ni process-safe**.

---

## El aprendizaje central

`HITO-16` ya había mostrado que la secuencialidad del pipeline no era una
preferencia de estilo sino parte del método. `HITO-21` extiende esa idea:

> La secuencialidad no aplica solo a las fases funcionales de `/implement-us`.
> También aplica a la instrumentación del proceso. El tracker forma parte del
> método y debe tratarse como un recurso secuencial.

Hasta ahora la interpretación práctica era:

- no saltear fases
- no mezclar artefactos fuera de orden
- respetar puntos de aprobación

Ahora hay una restricción adicional, concreta:

- **no ejecutar operaciones del tracker en paralelo**

---

## Por qué esto importa metodológicamente

En un proceso tradicional, el tracking de tiempo o de fases es un accesorio.
Si falla, se rehace o se ignora.

En AtaraxiaDive no cumple ese rol. El tracker forma parte de la evidencia del
experimento:

- registra tiempos por fase
- sustenta reportes históricos
- alimenta la lectura del overhead del ecosistema
- sirve como rastro verificable del cumplimiento del pipeline

Si el tracker se corrompe, no solo se pierde comodidad operativa:
se degrada la calidad de la evidencia del experimento.

Por eso este hallazgo no es “un bug menor de tooling”. Es una condición de
validez del método.

---

## Decisión derivada

Se establece una política explícita en `WORKFLOW-DESARROLLO.md`:

> Todas las operaciones sobre `tracker_cli.py` deben ejecutarse estrictamente en
> secuencia, una por vez. El tracking automático está permitido y deseable, pero
> no puede escribir en paralelo sobre el mismo archivo `.claude/tracking/US-*.json`.

Esta política vuelve normativo algo que antes era solo una suposición implícita.

---

## Qué valida para el experimento

Este HITO aporta una precisión importante a la hipótesis de gobierno del proceso:

> La linealidad del pipeline no es solo una propiedad de las tareas de desarrollo.
> También es una propiedad de la telemetría que hace verificable ese pipeline.

Dicho más simple:

- el método es secuencial
- su evidencia también debe producirse secuencialmente

---

## Acciones incorporadas

- [x] Política de secuencialidad del tracker agregada a `WORKFLOW-DESARROLLO.md`
- [x] Uso operativo: no paralelizar llamadas `tracker_cli.py`
- [x] Reparación manual del tracker de `US-4.6.1` para preservar continuidad del pipeline
- [ ] Evaluar si `tracker_cli.py` debe incorporar locking explícito o escritura atómica
- [ ] Evaluar si el skill `/implement-us` debe declarar esta restricción en su documentación interna

---

## Conexión con HITO-16

`HITO-16` afirmó:

> la secuencialidad prescriptiva del pipeline es parte del método

`HITO-21` agrega:

> esa secuencialidad incluye también al mecanismo que registra el cumplimiento del método

Así, el alcance de la tesis se vuelve más preciso:

- `HITO-16`: secuencialidad del flujo de trabajo
- `HITO-21`: secuencialidad de la evidencia del flujo de trabajo

---

*Registrado durante US-4.6.1 — cuando el tracker dejó de ser tooling auxiliar y quedó expuesto como infraestructura metodológica del proceso*
