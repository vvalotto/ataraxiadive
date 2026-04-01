# HITO-15 — Las proyecciones CQRS emergen naturalmente del Event Sourcing

| Campo | Valor |
|-------|-------|
| **Documento** | HITO-15 — Hallazgo arquitectónico durante SP3 |
| **Fecha** | 2026-03-31 |
| **Sprint** | SP3 — US-3.3.1 (torneo_id en Competencia) |
| **Relacionado** | `docs/specs/sp3/US-3.3.1.md` · `docs/reports/US-3.3.1-report.md` · `docs/plans/sp-adj-03/PLAN-SP-ADJ-03.md` |

---

## Contexto

Al implementar US-3.3.1, el requisito era: dado un `torneo_id`, listar todas las
competencias que pertenecen a ese torneo.

En un modelo relacional esto es trivial: `SELECT * FROM competencias WHERE torneo_id = ?`.
En Event Sourcing, no existe esa tabla. La información está distribuida en streams
independientes (`competencia-{uuid}`), uno por instancia de aggregate.

La solución implementada en `ObtenerCompetenciasPorTorneoHandler`:

```python
streams = await self._event_store.load_all_streams_with_prefix("competencia-")
# filtrar en memoria aquellos cuyo primer IntervaloOTConfigurado tiene el torneo_id buscado
```

Es decir: cargar todos los streams, deserializar el primer evento de cada uno, filtrar.
O(n) donde n = número de competencias.

---

## El hallazgo

**Cada vez que un query handler hace `load_all_streams_with_prefix` + filter en memoria,
está implementando una proyección ad-hoc no materializada.**

Esto no es un error de diseño — es una señal del sistema. Event Sourcing separa
estructuralmente las escrituras (comandos → eventos) de las lecturas (queries → read models).
Cuando el read model no está materializado, el query handler lo reconstruye en tiempo real.

Para volumen bajo (SP3) es aceptable. En producción o con crecimiento, la solución
canónica es una **tabla de proyección** que se actualiza al procesar cada evento relevante:

```sql
CREATE TABLE competencias_por_torneo (
    competencia_id TEXT PRIMARY KEY,
    torneo_id      TEXT NOT NULL,
    disciplina     TEXT NOT NULL
);
-- Se actualiza al procesar cada IntervaloOTConfigurado con torneo_id presente
```

El projector puede correr en el mismo proceso (síncrono, dentro del handler) o como
proceso separado (asíncrono, consuming del event store). En SP3 el patrón síncrono
es suficiente.

---

## Por qué es un hallazgo experimental

IEDD especifica las US en términos de precondición, postcondición e invariantes de
negocio. En US-3.3.1 la postcondición incluía `GET /competencias?torneo_id=` —
un query cross-aggregate. La especificación no anticipa explícitamente si ese query
requiere un read model materializado o no.

El experimento muestra que **la necesidad de proyecciones no emerge de la especificación,
emerge del contacto con la implementación**. Es un gap metodológico de IEDD: no hay
una capa en la cadena de 5 capas que fuerce a preguntarse "¿este query cruza streams?
¿necesita un read model?".

Hipótesis a validar en SP3/SP4: si la especificación US-IEDD incluyera una sección
explícita de **read models** (¿qué proyecciones requiere este caso de uso?), el diseño
de la arquitectura de lectura emergería antes de la implementación, no durante.

---

## Regla práctica identificada

> Si un query handler carga múltiples streams y filtra en memoria,
> ese filtro es un read model implícito que debería materializarse
> cuando el volumen lo justifique.

Señales de que el volumen lo justifica:
- El query se llama en cada request de usuario (no solo en admin)
- El número de streams a escanear crece con el uso normal del sistema
- El tiempo de respuesta es observable por el usuario final

En AtaraxiaDive, `GET /competencia?torneo_id=` cumplirá estas condiciones en SP4
(cuando haya torneos reales con múltiples disciplinas). El read model se agrega
en SP-ADJ-03 o SP4.

---

## Acción pendiente

- [ ] Agregar proyección `competencias_por_torneo` como ítem en SP-ADJ-03
      o en INC-3.4 si la query es crítica para el flujo E2E de US-3.3.2.
- [ ] Evaluar si la plantilla US-IEDD debería incluir una sección "Read Models"
      para capturar este gap en la especificación antes de la implementación.

---

*Registrado durante la implementación de US-3.3.1 — SP3 El Torneo*
