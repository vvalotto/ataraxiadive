# HITO-22 — El Event Sourcing no solo sirve para auditoría legible: también permite integridad criptográfica si el cierre se calcula sobre una secuencia canónica previa al evento final

| Campo | Valor |
|-------|-------|
| **Documento** | HITO-22 — Hallazgo metodológico durante US-4.6.2 |
| **Fecha** | 2026-04-16 |
| **Sprint** | SP4 — INC-4.6 — US-4.6.2 |
| **Relacionado** | `src/competencia/application/_p08_finalizacion.py` · `src/competencia/domain/services/calculador_hash_competencia.py` · `src/competencia/domain/events/competencia_finalizada.py` · `HITO-21` · `docs/reports/US-4.6.2-report.md` |

---

## Contexto

Durante `US-4.6.2` se implementó el cálculo y persistencia de un `hash_sha256`
al cerrar una disciplina. El objetivo funcional era dejar una huella verificable
de integridad sobre todos los eventos de las performances de esa disciplina.

La hipótesis inicial parecía simple: “al cerrar, se calcula un hash de los
eventos y se guarda junto con el cierre”. La implementación mostró algo más
interesante: el problema no era solo calcular SHA-256, sino definir con precisión
qué conjunto de eventos se hashea, en qué orden y en qué momento del flujo.

---

## Qué reveló la implementación

La solución correcta terminó teniendo tres propiedades no obvias:

- el hash debía calcularse sobre los eventos de `performance`, no sobre snapshots
  ni sobre proyecciones
- la serialización debía ser canónica y determinista
- el cálculo debía ocurrir antes de persistir `CompetenciaFinalizada`

Si cualquiera de esas tres condiciones fallaba, el hash dejaba de ser una prueba
fuerte de integridad.

---

## El aprendizaje central

`US-4.6.1` ya había validado que el event store sirve como fuente de auditoría
legible para humanos. `US-4.6.2` extiende esa validación:

> El mismo event store puede servir también como base de integridad
> criptográfica, pero solo si el cierre se define como una derivación canónica
> del historial previo y no como una operación posterior o ad hoc.

Esto fortalece la lectura de ADR-001: la ventaja del Event Sourcing no es solo
“guardar historia”, sino poder reutilizar esa historia para distintos fines sin
duplicar persistencia:

- auditoría operativa
- verificabilidad post-cierre
- exportación con evidencia de integridad

---

## La decisión de diseño más importante: el hash vive en P-08, no en el aggregate

El aggregate `Competencia` no debía leer el event store para construir el hash.
Ese dato depende de recorrer todos los eventos persistidos de las performances de
la disciplina, lo cual es una responsabilidad de orquestación de aplicación.

Por eso el cálculo quedó en `P-08`:

- `P-08` consulta el event store
- filtra los streams de la disciplina
- calcula el hash canónico
- recién entonces llama a `competencia.finalizar(...)`

Esto deja una regla útil para futuros casos:

> Cuando una decisión de dominio necesita inspeccionar el historial persistido
> completo, la lectura pertenece a application y el aggregate recibe el dato ya
> resuelto.

---

## El riesgo autorreferencial

La implementación también mostró un riesgo conceptual importante: si el hash se
calculaba después de persistir `CompetenciaFinalizada`, el propio evento de cierre
quedaba potencialmente incluido en el conjunto hasheado.

Eso producía una autorreferencia:

- el cierre contiene un hash
- el hash depende del cierre

En términos prácticos, el valor dejaba de ser una huella estable del historial
previo. Por eso el orden correcto no es accesorio:

1. leer historial persistido de la disciplina
2. serializar canónicamente
3. calcular SHA-256
4. emitir `CompetenciaFinalizada` con ese valor

Este orden forma parte de la corrección funcional, no de una optimización técnica.

---

## La serialización canónica como contrato

Otro hallazgo fue que el hash no depende solo de “los datos”, sino también de su
representación exacta. Para que el digest sea determinista, la serialización debe
ser estable:

- mismo conjunto de campos
- mismas claves
- mismo orden
- mismo orden de eventos

En esta US eso se resolvió con JSON canónico y `sort_keys=True`, usando solo:

- `tipo`
- `sequence_number`
- `timestamp`
- `datos`

Esto convierte la representación canónica en un contrato técnico. Si en el futuro
se cambia esa forma de serialización, no cambia solo una implementación interna:
cambia el significado del hash.

---

## Backward compatibility: extender eventos exige proteger la lectura histórica

Agregar `hash_sha256` a `CompetenciaFinalizada` parecía un cambio menor, pero
expuso otra lección estable:

> En un sistema con event streams durables, extender un evento no es solo escribir
> más payload hacia adelante; también es garantizar que los streams viejos sigan
> pudiendo reconstituirse.

La decisión de usar `payload.get("hash_sha256")` en `from_payload()` evitó romper
tests legacy, fixtures previos y streams ya persistidos.

Eso confirma una regla práctica:

- escribir eventos nuevos es fácil
- evolucionar eventos existentes exige siempre una estrategia explícita de
  compatibilidad hacia atrás

---

## Implicancia para SP4 y para el experimento

`INC-4.6` empieza a mostrar una convergencia fuerte:

- `US-4.6.1`: el historial es legible y auditable
- `US-4.6.2`: el historial es verificable criptográficamente

La tesis emergente es que el event store no está cumpliendo un único rol
arquitectónico. Está funcionando como infraestructura común para:

- observabilidad del proceso deportivo
- evidencia de auditoría
- garantía de integridad

Eso es metodológicamente relevante porque valida la apuesta de persistir eventos
como fuente primaria incluso en una plataforma relativamente pequeña.

---

## Acciones incorporadas

- [x] `CalculadorHashCompetencia` creado como servicio de dominio puro
- [x] `P-08` calcula el hash antes de persistir `CompetenciaFinalizada`
- [x] `CompetenciaFinalizada` persiste `hash_sha256`
- [x] `from_payload()` mantiene compatibilidad con streams históricos
- [ ] Evaluar si la secuencia canónica debe documentarse formalmente en un ADR o anexo técnico
- [ ] Evaluar si futuras exportaciones (`US-4.6.4`) deben incluir el hash como evidencia de integridad

---

## Conexión con HITO-21

`HITO-21` mostró que la evidencia del proceso exige secuencialidad metodológica.
`HITO-22` agrega otra capa:

> la evidencia del dominio también exige secuencialidad, porque el valor de
> integridad depende del orden exacto en que se lee, deriva y persiste el cierre

Así, la secuencialidad aparece en dos planos:

- `HITO-21`: secuencialidad del proceso de desarrollo y su tracker
- `HITO-22`: secuencialidad del proceso de cierre y su evidencia criptográfica

---

*Registrado durante US-4.6.2 — cuando el event store dejó de ser solo una fuente de auditoría y pasó a comportarse también como base de integridad verificable*
