# HITO-23 — La auditoría navegable no emerge de un backend aislado: aparece cuando la evidencia del Event Sourcing se vuelve composable en read models y accesible desde la UI

| Campo | Valor |
|-------|-------|
| **Documento** | HITO-23 — Hallazgo metodológico durante US-4.6.3 |
| **Fecha** | 2026-04-16 |
| **Sprint** | SP4 — INC-4.6 — US-4.6.3 |
| **Relacionado** | `frontend/src/pages/organizador/` · `frontend/src/hooks/useAuditoriaCompetencia.ts` · `src/competencia/application/queries/obtener_estado_competencia.py` · `HITO-22` · `docs/reports/US-4.6.3-report.md` |

---

## Contexto

Durante `US-4.6.3` se implementó la UI de auditoría para organizador. A primera
vista parecía una historia puramente frontend: pantallas nuevas, rutas nuevas y
consumo de `US-4.6.1` y `US-4.6.2`.

La implementación mostró algo distinto. La evidencia ya existía en backend, pero
no estaba todavía en una forma directamente consumible por la interfaz. El caso
concreto fue `hash_sha256`: estaba persistido en `CompetenciaFinalizada`, pero
no estaba expuesto por ninguna query pensada para encabezados de pantalla.

---

## Qué reveló la implementación

La UI de auditoría terminó dependiendo de una composición de fuentes:

- `GET /competencia/{id}/estado`
- `GET /competencia/{id}/grilla`
- `GET /resultados/{id}/ranking`
- `GET /competencia/{id}/performances/{atleta_id}/audit-log`

Eso dejó dos hallazgos claros:

- la US no era frontend puro
- la solución no necesitaba una mega-query nueva si las queries existentes podían
  enriquecerse y componerse bien

---

## El aprendizaje central

`US-4.6.1` validó la trazabilidad puntual. `US-4.6.2` validó la integridad del
cierre. `US-4.6.3` agrega la tercera capa:

> La auditoría no se vuelve realmente útil cuando existe en la base o en el API.
> Se vuelve útil cuando la evidencia del dominio puede recorrerse sin conocer el
> event store, componiendo read models estables y navegables en la UI.

Esto desplaza la lectura de “frontend como presentación” hacia algo más preciso:

- el frontend no inventa la auditoría
- la hace operable

---

## La falsa frontera entre frontend y backend

La spec parecía ubicar la US enteramente en `frontend/`, pero el hash de cierre
no podía mostrarse sin una extensión backend mínima. Eso expuso una regla útil:

> Cuando una pantalla necesita un dato semántico de estado, la separación
> frontend/backend deja de ser una frontera de alcance válida. El alcance real
> está en la cadena completa que vuelve observable ese dato.

En este caso, la decisión correcta no fue crear un endpoint nuevo, sino ampliar
`GET /estado` con `hash_sha256`.

Eso deja una heurística estable:

- si el dato pertenece al encabezado semántico de la pantalla, enriquecer la
  query de estado suele ser mejor que abrir una API paralela

---

## La auditoría como composición, no como proyección monolítica

Otra lección importante es que la pantalla no necesitó una query agregada
monolítica. La solución se armó con composición:

- `estado` para contexto y hash
- `grilla` para lista base de atletas
- `ranking` para enriquecimiento del resultado final
- `audit-log` para la traza puntual

Esto confirma una idea útil para CQRS liviano:

> Varias queries pequeñas, estables y bien nombradas pueden sostener una
> experiencia compleja sin necesidad inmediata de una proyección única.

La condición es que cada query tenga una frontera semántica clara y que el
frontend tolere que algunas sean enriquecimiento opcional, no dependencia dura.

---

## El ranking como dato opcional

La implementación mostró también que `ranking` no debía ser obligatorio para
abrir la auditoría. Si la pantalla colapsaba por ausencia de ranking, una capa
de enriquecimiento terminaba bloqueando el acceso a la evidencia principal.

Eso produjo otra regla práctica:

> En una UI operativa de auditoría, distinguir entre datos nucleares y datos de
> enriquecimiento no es detalle de UX; es una decisión de resiliencia funcional.

En esta US:

- núcleo: estado, hash, grilla, audit log
- enriquecimiento: ranking

---

## El límite metodológico actual: falta infraestructura de tests frontend

La validación de `US-4.6.3` quedó apoyada en:

- pytest backend
- `npm run build`
- `npm run lint`

Eso fue suficiente para cerrar la US, pero dejó visible un límite del ecosistema:

> SP4 ya tiene suficiente superficie React como para que la ausencia de harness
> formal de testing frontend deje de ser una omisión menor y pase a ser deuda
> metodológica visible.

Mientras el frontend era mínimo, `build` y `lint` bastaban. Con rutas por rol,
hooks, navegación y estados de carga/error, ya no cubren toda la semántica.

---

## Implicancia para INC-4.6 y para el experimento

Las tres primeras US de `INC-4.6` forman una secuencia coherente:

- `US-4.6.1`: la traza es legible
- `US-4.6.2`: la traza es verificable
- `US-4.6.3`: la traza es accesible operativamente

La tesis que emerge es fuerte:

> El valor de auditoría no aparece al implementar solo el backend. Aparece
> cuando la evidencia técnica del Event Sourcing se traduce en una interfaz que
> un organizador puede recorrer sin acceso a base de datos ni conocimiento del
> modelo interno de eventos.

Eso valida una idea importante para sistemas DDD con Event Sourcing:

- el event store resuelve persistencia y trazabilidad
- los read models resuelven operabilidad
- la UI resuelve apropiación real del valor por parte del usuario

---

## Acciones incorporadas

- [x] `GET /estado` extendido con `hash_sha256`
- [x] Navegación de organizador desde dashboard hasta traza puntual
- [x] Composición de queries en frontend en lugar de endpoint monolítico nuevo
- [x] Ranking tratado como enriquecimiento opcional
- [ ] Evaluar incorporación formal de `vitest` o `playwright` para SP4/SP5
- [ ] Evaluar si `US-4.6.4` debe reutilizar esta navegación como punto de entrada a exportación

---

## Conexión con HITO-22

`HITO-22` mostró que el event store puede sostener integridad criptográfica.
`HITO-23` agrega la siguiente capa:

> no alcanza con que la evidencia exista y sea correcta; también debe estar
> dispuesta en read models y navegación para que un usuario no técnico pueda
> usarla

Así, la secuencia queda:

- `HITO-22`: la evidencia del dominio es verificable
- `HITO-23`: la evidencia verificable debe ser composable y navegable para tener valor operativo

---

*Registrado durante US-4.6.3 — cuando la auditoría dejó de ser solo una capacidad del backend y pasó a ser una experiencia operable para organizador*
