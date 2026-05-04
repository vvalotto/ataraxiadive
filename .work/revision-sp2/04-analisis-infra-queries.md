# Análisis Infraestructura y Queries — Cierre SP2
## Patrón 3: CBO en infrastructure/repositories y application/queries

**Fecha:** 2026-03-28
**Archivos inspeccionados:**
- `src/competencia/infrastructure/repositories/andariveles_activos_adapter.py` (CBO 7/5)
- `src/competencia/application/queries/obtener_proximas_performances.py` (CBO 6/5)
- `src/competencia/application/commands/llamar_atleta.py` (CBO 7/5, ya analizado en Patrón 2)

---

## AndarivelesActivosAdapter (CBO 7/5)

**CBO estructuralmente justificado:**
- `Performance` — reconstitución desde Event Store
- `AndarivelesActivosPort`, `AndarivelesActivosData` — contrato del puerto
- `EventStorePort` — persistencia
- `Disciplina`, `EstadoPerformance` — VOs de filtrado

Todos los colaboradores son necesarios para proyectar el estado de andariveles.

### Smell real: acceso a atributo privado de Performance

```python
# línea 61:
ot: datetime | None = perf_activa._ot_programado  # noqa: SLF001
```

El adapter accede directamente a `_ot_programado`, un atributo privado de `Performance`.
El `# noqa: SLF001` es evidencia de que el autor sabía que era una violación.

**Causa raíz:** `Performance` no expone `ot_programado` como propiedad pública.
**Fix correcto:** agregar `@property ot_programado` en `Performance` — no tocar el adapter.

---

## ObtenerProximasPerformancesHandler (CBO 6/5)

**CBO estructuralmente justificado:**
- `Competencia` — para obtener el mapa de posiciones de la grilla
- `Performance` — para cada atleta
- `EventStorePort`, `Disciplina`, `EstadoPerformance` — collaborators necesarios

Lógica del handler:
1. Reconstitute `Competencia` → extraer `{performance_id: posicion}` de la grilla
2. Cargar todos los streams con prefijo `performance-{id}-`
3. Filtrar performances en `AnunciadaAP`, ordenar por posición en grilla
4. Retornar los primeros `limit` como DTOs

No hay refactor útil. La coordinación de dos aggregates es necesaria para responder la query.

### Observación arquitectural: O(n) reconstitution por query

`AndarivelesActivosAdapter` y `ObtenerProximasPerformancesHandler` comparten el mismo patrón:
cargar todos los streams con prefijo → reconstituir N aggregates → filtrar en memoria.

Funciona bien para torneos pequeños (10–20 performances). A escala (100+ performances por
disciplina), esto se convierte en un cuello de botella: N roundtrips al Event Store + N
reconstituciones de aggregate por cada llamada HTTP.

La solución canónica es una **projection/read model**: una tabla SQL que se actualiza
incrementalmente desde los eventos, consultable con una sola query. Esto está fuera del
scope de SP2 — es una deuda arquitectural a evaluar en SP3 o SP4.

---

## Veredicto Patrón 3

| Clase | CBO | Causa | Issue real |
|---|---|---|---|
| `AndarivelesActivosAdapter` | 7/5 | Estructural + 1 smell | `_ot_programado` privado accedido directamente |
| `ObtenerProximasPerformancesHandler` | 6/5 | Estructural | — (deuda de escala, no urgente) |
| `LlamarAtletaHandler` | 7/5 | Estructural | — (ver Patrón 2) |

---

## Hallazgos para el Experimento

### H-J — El noqa como indicador de deuda de diseño
El comentario `# noqa: SLF001` en `AndarivelesActivosAdapter` es una señal explícita
de que el autor sabía que estaba violando una restricción. Los `# noqa` son marcadores
de deuda silenciosa: el linter los ignoró, el DesignReviewer no los detectó,
solo apareció al leer el código.
**Implicancia:** en revisiones de cierre de SP, buscar `# noqa` activamente como indicador de deuda.

### H-K — El umbral CBO=5 también es inadecuado para adapters de Event Store
Un adapter que reconstituyendo aggregates desde el Event Store necesita mínimamente:
el aggregate, el port, el event store port, el VO de disciplina, el VO de estado.
Eso es CBO 5 de base, antes de cualquier lógica adicional.
El umbral debería calibrarse en al menos 8–10 para capas infrastructure/ y application/.

### H-L — O(n) reconstitution en queries: deuda arquitectural aceptable en SP2
El patrón "cargar todos los streams → reconstituir → filtrar en memoria" es simple y
correcto para la escala actual. La deuda es conocida y aceptada conscientemente — no es
un descuido. En IEDD, documentar esto en BL-002 es suficiente; la solución (read models)
entra como candidata a SP3 o SP4.
