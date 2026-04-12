# HITO-19 — El cierre de incremento como checkpoint formal de captura de hallazgos de diseño

| Campo | Valor |
|-------|-------|
| **Documento** | HITO-19 — Hallazgo metodológico al cierre de INC-4.1 |
| **Fecha** | 2026-04-08 |
| **Sprint** | SP4 — cierre de INC-4.1 |
| **Relacionado** | `HITO-11` · `HITO-13` · `docs/plans/sp4/PLAN-SP4.md` · `docs/reports/US-4.1.2-report.md` · `docs/reports/US-4.1.3-report.md` · `docs/reports/US-4.1.4-report.md` |

---

## Contexto

El cierre de `INC-4.1` dejó cuatro US implementadas:

- `US-4.1.1` — motivos de tarjeta roja
- `US-4.1.2` — tarjeta blanca con penalizaciones
- `US-4.1.3` — subdisciplinas SPE
- `US-4.1.4` — orden reglamentario de grilla

Las funcionalidades quedaron completas, testeadas y con artefactos de pipeline.
Sin embargo, al ejecutar `DesignReviewer` sobre el scope consolidado del incremento
emergió nuevamente una pregunta estructural:

> ¿cómo capturamos y planificamos la deuda de diseño que no bloquea la entrega
> funcional de una US, pero sí afecta la mantenibilidad del siguiente tramo?

Este HITO documenta el hallazgo y transforma la salida del quality gate en backlog
planificable.

---

## Resultado consolidado del DesignReviewer

Corrida ejecutada:

```bash
.venv/bin/designreviewer src/competencia src/shared src/torneo src/resultados --config pyproject.toml
```

Resultado:

- `1 blocking`
- `111 warning`

### Blocking único

- `Performance` en `src/competencia/domain/aggregates/performance.py`
  - `GodObjectAnalyzer`
  - métrica: `31/28`
  - esfuerzo estimado: `4.5h`

### Grupos de warnings dominantes

1. **Aggregate / entidad sobrecargados**
   - `Performance`
   - `Competencia`
   - `GrillaDeSalida`
   - `RankingCompetencia`
   - `Torneo`

2. **Handlers de aplicación con demasiada orquestación**
   - `RegistrarAPHandler`
   - `RegistrarResultadoHandler`
   - `RegistrarDNSHandler`
   - `CorregirResultadoHandler`
   - `GenerarGrillaHandler`
   - `AsignarTarjetaHandler`
   - `LlamarAtletaHandler`
   - `CalcularRankingHandler`

3. **Adaptadores / repositorios con responsabilidad expandida**
   - `ResultadosCompetenciaAdapter`
   - `SQLiteTorneoRepository`
   - `PerformancesAPAdapter`
   - `PerformancesEstadoAdapter`
   - `AndarivelesActivosAdapter`

4. **Objetos de soporte con demasiada lógica incidental**
   - `TarjetaAsignada`
   - `TarjetaAsignacion`
   - `DisciplinaDescriptor`

---

## Qué se observó

### 1. El pipeline de US funciona para entregar features, pero no absorbe por sí solo la deuda emergente

`/implement-us` fue suficiente para llevar `INC-4.1` a un estado funcional correcto.
Lo que no hace automáticamente es reabsorber el crecimiento estructural acumulado
cuando varias US consecutivas expanden el mismo núcleo del dominio.

El caso evidente fue `Performance`: cada US fue correcta en aislamiento, pero el
efecto acumulado dejó al aggregate por encima del umbral del analyzer.

### 2. El cierre de incremento es el punto correcto para mirar diseño

Si el refactoring se hubiera intentado dentro de `US-4.1.2`, se mezclaban decisiones
de diseño con una feature sensible del dominio. Si se hubiese postergado sin registro,
quedaba como deuda difusa.

La revisión al final del incremento produjo un mejor punto de corte:

- las reglas del dominio ya están estables
- el changeset funcional ya está cubierto por tests
- los hallazgos pueden agruparse por afinidad estructural y no por urgencia táctica

### 3. El quality gate no solo valida: también estructura backlog

Esto extiende el patrón ya observado en `HITO-11`:

- `HITO-11`: el quality gate actuó como catalizador de una decisión arquitectónica
- `HITO-19`: el quality gate actúa como **mecanismo de agrupación y priorización**
  de refactor post-incremento

La salida relevante no es solo “hay warnings”, sino “qué conjunto coherente de ajustes
conviene planificar ahora que el incremento cerró”.

---

## Decisión derivada

Se establece una práctica explícita para incrementos con alto impacto de dominio:

> **Todo cierre de incremento que acumule cambios sobre aggregates/core handlers debe
> terminar con una corrida consolidada de DesignReviewer y, si aparecen hallazgos
> estructurales significativos, generar un HITO de planificación de ajustes.**

Este HITO no reemplaza al `SP-ADJ` formal descrito en `HITO-13`. Lo complementa.

- `HITO-13` define **cuándo** existe una etapa formal de ajuste técnico
- `HITO-19` define **cómo se captura y empaqueta** el backlog de diseño al cierre
  de un incremento concreto

---

## Backlog de ajustes derivado

### AJ-INC-4.1.1 — Descomponer `Performance`

**Prioridad:** Crítica

Objetivo:
- reducir la concentración de responsabilidades del aggregate
- extraer la resolución de tarjeta final / penalizaciones / compatibilidad legacy

Focos:
- separar cálculo y resolución de tarjeta de `Performance`
- mover compatibilidad de payload legacy fuera del aggregate cuando sea posible
- revisar firma larga de `asignar_tarjeta()`

### AJ-INC-4.1.2 — Aliviar handlers de `competencia`

**Prioridad:** Alta

Objetivo:
- reducir `FeatureEnvy` y `LongMethod` en handlers core

Focos:
- factorizar construcción de commands/policies/helpers
- aislar validaciones de unidad, estado y stream en helpers reutilizables
- simplificar `AsignarTarjetaHandler` y `GenerarGrillaHandler`

### AJ-INC-4.1.3 — Simplificar `GrillaDeSalida` y agregado de ranking

**Prioridad:** Media-Alta

Objetivo:
- bajar complejidad de métodos largos y lógica incidental de orden/ajuste

Focos:
- partir `GrillaDeSalida.ajustar()`
- revisar `RankingCompetencia` y `ResultadosCompetenciaAdapter`

### AJ-INC-4.1.4 — Limpiar `torneo` y objetos de soporte

**Prioridad:** Media

Objetivo:
- reducir complejidad accidental en `Torneo`, `SQLiteTorneoRepository`,
  `TarjetaAsignacion`, `TarjetaAsignada`, `DisciplinaDescriptor`

---

## Orden recomendado de ejecución

1. `Performance`
2. handlers de `competencia`
3. `GrillaDeSalida` + `RankingCompetencia` + adapters de resultados
4. `Torneo` + repositorio + objetos de soporte

La razón del orden es simple: primero se ataca el único blocking y el núcleo con
más riesgo de seguir creciendo; después se avanza hacia capas de soporte.

---

## Qué valida para el experimento

Este HITO fortalece una hipótesis metodológica nueva:

> **El incremento, no la US aislada, es la unidad correcta para capturar deuda
> estructural emergente cuando varias features impactan el mismo núcleo de dominio.**

Esto no contradice IEDD; lo complementa:

- la US sigue siendo la unidad correcta de implementación funcional
- el incremento aparece como la unidad correcta de lectura estructural

En otras palabras:

- **US:** entrega comportamiento
- **Incremento:** revela acumulación de complejidad
- **HITO de cierre:** traduce esa complejidad en backlog accionable

---

## Próximo paso recomendado

Convertir este backlog en un artefacto operativo concreto:

- o bien un `PLAN-SP-ADJ-*`
- o bien un `INC` técnico corto de refactoring

La decisión depende de si los ajustes se ejecutan:

- inmediatamente al cierre de `INC-4.1`
- o como etapa formal separada antes del siguiente bloque funcional de SP4

---

*Redactado: 2026-04-08 — cierre de INC-4.1*
