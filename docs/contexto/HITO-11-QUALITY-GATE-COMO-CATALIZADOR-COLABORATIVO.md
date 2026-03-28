# HITO-11 — El quality gate como catalizador de colaboración: cómo una métrica automatizada derivó en una decisión de arquitectura

| Campo | Valor |
|-------|-------|
| **Documento** | HITO-11 — Análisis experimental |
| **Fecha** | 2026-03-26 |
| **Sprint** | SP2 — pre-Inc 2.1 |
| **Relacionado** | `ADR-013` · `INC-2.0` · `docs/specs/sp2/INC-2.0.md` · `src/competencia/domain/exceptions.py` |

---

## Contexto

Al inicio de la sesión, con US-2.1.1 y US-2.1.2 ya implementadas y mergeadas
a `develop`, la primera tarea era sincronizar con GitHub. Un push rutinario.

Lo que siguió no fue rutinario.

---

## El relato

### Acto 1 — La herramienta bloquea

El pre-push hook ejecutó DesignReviewer y bloqueó el push con 2 issues CRITICAL:

```
GodObjectAnalyzer │ Performance    │ 22/20 métodos
NOPAnalyzer       │ EstadoCompetencia │ 2/1 padres
```

El `NOPAnalyzer` era un fix directo: `EstadoCompetencia(str, Enum)` debía ser
`EstadoCompetencia(StrEnum)`, consistente con el patrón ya usado en `EstadoPerformance`.
Cinco minutos y resuelto.

El `GodObjectAnalyzer` era diferente. Indicaba que `Performance` tenía demasiados
métodos. El fix técnico también era directo: ajustar el umbral en `pyproject.toml`.
Pero antes de hacerlo, Victor preguntó algo que cambió el curso de la sesión:

> *"A priori no me termina de cerrar que Performance.py sea una clase tan grande.
> Que sea un aggregate no justifica que sea de gran tamaño."*

La herramienta había hecho su trabajo: forzar una pausa.

### Acto 2 — El análisis humano entra en juego

La pregunta de Victor no era sobre la métrica — era sobre el diseño. Y era legítima.
Un aggregate es una frontera de consistencia transaccional, no una justificación
para acumular responsabilidades. "Es el aggregate principal" es una respuesta
cómoda, no una respuesta arquitectónica.

Claude leyó el código de `performance.py` en detalle. El análisis mostró que los
22 métodos se distribuían en tres grupos con naturalezas muy distintas:

- **7 propiedades** — getters de estado interno. Python idiomático.
- **8 métodos de reconstitución ES** — boilerplate del patrón Event Sourcing.
  Cada aggregate con N tipos de evento tendrá N métodos `_apply_*`. No es
  crecimiento de responsabilidades, es el costo fijo del patrón.
- **6 comandos de dominio** — transiciones de estado con invariantes.
  Un ciclo de vida cohesivo y lineal. No se pueden separar sin romper
  la consistencia transaccional.

Conclusión: el GodObjectAnalyzer estaba midiendo complejidad accidental del
patrón, no complejidad esencial del dominio. El ajuste de umbral era correcto.

Pero en ese momento de lectura atenta del archivo, apareció algo que el
DesignReviewer nunca detectó — porque no es lo que mide:

```python
class EstadoInvalidoParaLlamar(Exception): ...
class EstadoInvalidoParaRegistrarResultado(Exception): ...
class EstadoInvalidoParaRegistrarDNS(Exception): ...
class EstadoInvalidoParaAsignarTarjeta(Exception): ...
class MotivoObligatorio(Exception): ...
class DistanciaBlackoutObligatoria(Exception): ...
class EstadoInvalidoParaCorregirResultado(Exception): ...

class Performance(AggregateRoot):
    ...
```

Siete clases de excepción definidas en el mismo archivo que el aggregate.
No porque alguien tomara esa decisión conscientemente — sino porque nunca
se había tomado ninguna decisión sobre dónde viven las excepciones de dominio.

Victor lo reconoció de inmediato:

> *"Creo que aparece una decisión de diseño que nunca definimos: la cuestión
> del exception management para toda la aplicación. A mí se me pasó."*

### Acto 3 — El gap se convierte en decisión arquitectónica

Lo que empezó como un push bloqueado derivó en una conversación sobre arquitectura.
Y esa conversación produjo:

- **ADR-013** — formalización de la jerarquía de excepciones de dominio:
  `domain/exceptions.py` por BC, `DomainError` como base, application layer
  transparente, infrastructure con sus propias excepciones separadas.
  Complementa ADR-012 (RFC 7807) que ya definía el lado HTTP pero asumía
  el lado dominio sin formalizarlo.

- **INC-2.0** — incremento técnico que implementó la decisión: movió las
  10 excepciones existentes a `domain/exceptions.py`, creó `exception_handlers.py`
  en el API layer, actualizó 23 archivos de test y agregó 6 nuevos tests
  de integración del handler. Cero regresiones.

El incremento se implementó antes de continuar con US-2.1.3 y US-2.1.4 — porque
cada US futura agregaría más excepciones, y establecer el patrón después hubiera
significado hacerlo dos veces.

---

## Los tres actores y su contribución específica

Lo interesante de esta secuencia es que ninguno de los tres actores hubiera
llegado al mismo resultado solo:

**La herramienta (DesignReviewer):**
No detectó el problema de las excepciones — eso está fuera de su alcance.
Lo que hizo fue más valioso en este contexto: **forzó una pausa obligatoria**.
El push no pudo seguir. Hubo que mirar el código. Sin ese bloqueo, `develop`
se hubiera sincronizado y la sesión habría continuado directo a US-2.1.3.
La herramienta creó la ocasión.

**El desarrollador (Victor):**
No se conformó con el fix técnico. Cuando Claude propuso ajustar el umbral,
Victor cuestionó la justificación de fondo. Esa pregunta — "¿es válido que
Performance sea tan grande?" — no la podía hacer ninguna herramienta automática.
Requería juicio sobre intención de diseño, conocimiento del dominio y experiencia
en DDD. Victor convirtió una métrica en una pregunta de diseño.

**Claude:**
Leyó el código con la atención que la pregunta merecía. Esa lectura atenta,
estimulada por la pregunta de Victor, fue lo que encontró las excepciones inline.
Y cuando Victor reconoció el gap, Claude pudo articular la decisión completa:
la relación con ADR-012, la jerarquía mínima, las reglas de ubicación por capa,
el mecanismo de captura en el API layer.

El resultado — ADR-013 + INC-2.0 — emergió de la interacción de los tres.
Ninguno lo hubiera producido por su cuenta en esa sesión.

---

## Qué valida para el experimento

**Hipótesis H-3 (herramientas como red de seguridad):** Confirmada en una
dimensión no anticipada. El valor del quality gate no fue detectar el bug
directamente, sino crear un punto de revisión obligatorio donde la combinación
humano+IA pudo encontrar algo que el analizador estático no mide.

Esto sugiere que los quality gates tienen dos tipos de valor:
1. **Valor directo:** detectar violaciones que el tool puede medir (CBO, WMC, NOP)
2. **Valor indirecto:** crear checkpoints de reflexión donde emerge conocimiento
   de diseño no automatizable

El valor indirecto puede ser tan o más importante que el directo, pero es
invisible si solo se miden las violaciones detectadas.

**Sobre el proceso colaborativo:** Este episodio es evidencia de un patrón de
trabajo que vale documentar para el paper: la IA no reemplaza el juicio del
desarrollador sobre diseño — lo amplifica. Victor hizo la pregunta correcta;
Claude tuvo la capacidad de leer 460 líneas de código en segundos y articular
la respuesta; la herramienta creó la ocasión para que esa conversación ocurriera.

---

## Nota sobre la cadena causal exacta

Para que este hallazgo sea reproducible y honesto en el paper:

El DesignReviewer **no detectó** el problema de las excepciones inline.
Detectó métricas de tamaño (métodos, líneas) que el análisis posterior
mostró ser en gran parte artefactos del patrón Event Sourcing.

El problema de las excepciones emergió de la **lectura atenta del código**
estimulada por la pregunta de diseño de Victor, que a su vez fue estimulada
por el bloqueo del quality gate.

La cadena es: `herramienta bloquea → desarrollador cuestiona → IA analiza → gap emerge`.
No: `herramienta detecta gap`.

Esa distinción importa. El primero es un hallazgo sobre cómo funciona
la colaboración. El segundo sería sobrevender las capacidades del tool.

---

*Redactado: 2026-03-26 — SP2, sesión post-sincronización con GitHub*
