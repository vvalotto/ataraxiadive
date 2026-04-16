# HITO-24 — La exportación no es un detalle de formato: es la prueba de que la evidencia del dominio puede recomponerse como read model transversal sin persistencia paralela

| Campo | Valor |
|-------|-------|
| **Documento** | HITO-24 — Hallazgo metodológico durante US-4.6.4 |
| **Fecha** | 2026-04-16 |
| **Sprint** | SP4 — INC-4.6 — US-4.6.4 |
| **Relacionado** | `src/resultados/application/queries/exportar_resultados.py` · `src/resultados/api/router.py` · `src/resultados/infrastructure/repositories/atleta_info_adapter.py` · `HITO-22` · `HITO-23` · `docs/reports/US-4.6.4-report.md` |

---

## Contexto

Durante `US-4.6.4` se implementó la exportación de resultados en `CSV` y `JSON`
para organizador. La lectura inicial de la historia sugería un alcance acotado:
tomar resultados existentes y serializarlos en dos formatos descargables.

La implementación mostró otra cosa. La exportación no estaba limitada a
`Resultados`; necesitaba recomponer una vista completa del torneo a partir de
varios bounded contexts:

- `Competencia` para estado e `hash_sha256`
- `Torneo` para el nombre del torneo
- `Registro` para nombre, categoría y club del atleta
- `Resultados` para ranking y overall persistidos cuando existieran

---

## Qué reveló la implementación

El problema central no fue escribir `csv.writer()` ni armar un `JSONResponse`.
El problema fue construir una salida coherente sin romper fronteras de dominio ni
crear una persistencia paralela “solo para exportar”.

Eso dejó tres hallazgos claros:

- la exportación era un read model transversal, no una simple serialización
- el event store podía completar huecos de proyección sin duplicar almacenamiento
- el valor de auditoría solo era válido si ciertos datos se exponían de manera
  semánticamente correcta, no por mera disponibilidad técnica

---

## El aprendizaje central

`US-4.6.1` validó la traza legible. `US-4.6.2` validó la integridad del cierre.
`US-4.6.3` volvió esa evidencia navegable. `US-4.6.4` agrega la cuarta capa:

> La auditoría madura cuando la evidencia del dominio puede salir del sistema
> como read model portable, recompuesto desde bounded contexts distintos sin
> exigir una base auxiliar ni degradar las fronteras del modelo.

Esto cambia la lectura de “exportar resultados” por una tesis más precisa:

- exportar no es imprimir datos
- exportar es demostrar que el sistema puede producir evidencia transferible
  desde su fuente de verdad real

---

## La exportación como composición entre bounded contexts

La implementación obligó a unir piezas que no viven en el mismo modelo:

- identidad del torneo
- estado y hash de cada disciplina
- ranking u overall
- identidad humana del atleta

Intentar resolver esto con joins informales o consultas directas cruzadas habría
degradado la arquitectura. La decisión correcta fue formalizar adapters y
repositorios en la query de aplicación.

Eso deja una regla útil:

> Cuando una salida pública necesita mezclar contexto operativo y contexto
> humano, el problema no se resuelve en el formato de salida sino en la calidad
> de la composición entre bounded contexts.

---

## El event store como respaldo operativo de la exportación

No todas las disciplinas tenían necesariamente un ranking persistido listo para
ser exportado. Aun así, la US pudo cerrarse porque el event store permitió
reconstruir performances finales y derivar un ranking en memoria sin crear una
proyección nueva ni persistir resultados auxiliares.

Eso fortalece la hipótesis que venía creciendo desde `HITO-22`:

> El event store no solo sirve para auditar o verificar integridad. También
> puede comportarse como respaldo operativo cuando una proyección no alcanza o
> todavía no existe.

Esto no elimina la utilidad de las proyecciones, pero sí muestra una propiedad
importante del modelo:

- las proyecciones optimizan accesos frecuentes
- el event store preserva la capacidad de recomposición completa

---

## El hash no es “otro campo”: es evidencia condicional

La exportación planteó una decisión semántica relevante: `hash_sha256` estaba
disponible en algunas disciplinas, pero no debía mostrarse siempre.

La decisión correcta fue exponerlo solo cuando la disciplina estaba
`Finalizada`. Mostrarlo antes habría sugerido una garantía de integridad que el
sistema todavía no había consolidado.

De ahí surge una regla más general:

> En una salida orientada a auditoría, la corrección semántica de la evidencia
> importa más que su mera disponibilidad técnica.

En otras palabras:

- no todo dato accesible debe exportarse
- la exportación debe respetar el momento de validez del dato

---

## La ACL de Registro como defensa del modelo

Nombre, categoría y club del atleta eran obligatorios para una exportación
usable, pero no pertenecen al bounded context de `Resultados`.

La tentación natural habría sido duplicar esos atributos o resolverlos con
consultas informales. La implementación mostró que valía más explicitar la ACL
de `Registro`:

- mantiene la frontera del BC `Resultados`
- vuelve visible la dependencia externa
- evita que una necesidad de presentación termine contaminando el modelo propio

Esto deja un aprendizaje arquitectónico estable:

> Una exportación pública suele hacer visibles dependencias humanas o
> administrativas que el dominio operativo no necesita internamente. Precisamente
> por eso conviene encapsularlas como ACL y no absorberlas en el BC consumidor.

---

## La exportación como detector de gaps de dominio

La US también expuso una ausencia importante: no existe hoy un puntaje
federativo persistido por disciplina. Para resolver la exportación fue necesario
adoptar una convención operativa, usando la `posicion` como `puntos` para esa
salida.

Eso permitió cerrar la historia, pero dejó un hallazgo metodológico claro:

> Las exportaciones son un buen mecanismo para detectar conceptos que el sistema
> ya necesita comunicar hacia afuera, pero todavía no modeló explícitamente
> hacia adentro.

No es un bug de la US. Es una señal de madurez del dominio:

- internamente, el sistema todavía opera sin ese concepto formalizado
- externamente, la necesidad de comunicarlo ya apareció

---

## Implicancia para INC-4.6 y para el experimento

Las cuatro primeras US de `INC-4.6` forman una progresión nítida:

- `US-4.6.1`: la traza es legible
- `US-4.6.2`: la traza es verificable
- `US-4.6.3`: la traza es navegable
- `US-4.6.4`: la traza es exportable y transferible

La tesis que emerge es fuerte:

> El valor del Event Sourcing no se agota en registrar historia. Se confirma
> cuando esa historia puede recomponerse como evidencia portable para usuarios,
> auditorías o intercambio externo, sin pedir una infraestructura paralela de
> persistencia.

Esto da a `SP4` una validación particularmente sólida:

- la evidencia existe
- la evidencia se verifica
- la evidencia se opera
- la evidencia se transfiere

---

## Acciones incorporadas

- [x] Endpoint `GET /resultados/{torneo_id}/export?format=csv|json`
- [x] Query transversal que compone `Competencia`, `Torneo`, `Registro` y `Resultados`
- [x] Inclusión condicional de `hash_sha256` solo para disciplinas finalizadas
- [x] Fallback a recomposición desde event store cuando no alcanza la proyección
- [x] ACL explícita para información exportable del atleta
- [ ] Evaluar formalización del concepto de puntaje federativo por disciplina
- [ ] Evaluar si futuras exportaciones deben versionar explícitamente su esquema

---

## Conexión con HITO-22 y HITO-23

`HITO-22` mostró que la evidencia del event store puede ser verificable.
`HITO-23` mostró que esa evidencia debe ser navegable desde UI.
`HITO-24` agrega la siguiente capa:

> La evidencia verificable y navegable también debe poder salir del sistema como
> artefacto portable sin romper las fronteras del modelo.

La secuencia queda así:

- `HITO-22`: la evidencia del dominio es verificable
- `HITO-23`: la evidencia verificable se vuelve operable en UI
- `HITO-24`: la evidencia operable se vuelve transferible por exportación

---

*Registrado durante US-4.6.4 — cuando la auditoría dejó de ser solo una capacidad interna y pasó a comportarse como evidencia portable recompuesta desde bounded contexts*
