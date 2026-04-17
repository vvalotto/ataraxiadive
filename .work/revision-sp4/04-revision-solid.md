# Revisión de Calidad — Cierre SP4
## Revisión SOLID — Código nuevo en SP4

**Fecha:** 2026-04-16
**Archivos revisados:**
- `src/competencia/application/_p08_finalizacion.py`
- `src/competencia/domain/events/performance_events.py`
- `src/competencia/domain/value_objects/resolucion_tarjeta.py`
- `src/resultados/application/queries/exportar_resultados.py`
- `src/notificaciones/application/policies/politica_p10.py`
- `src/notificaciones/application/policies/politica_p11.py`

---

## Metodología

La revisión sigue los cinco principios SOLID en el código producido en SP4.
Los issues de BC Notificaciones (DES-01, DES-02 de `02-analisis-bc-notificaciones.md`)
se retoman aquí para clasificarlos por principio.

---

## SRP — Single Responsibility Principle

### SRP-01 — `ExportarResultadosHandler` tiene múltiples responsabilidades

`ExportarResultadosHandler` (exportar_resultados.py) coordina cuatro operaciones distintas:

1. **Replay de eventos** — reconstruye el estado de performance desde el event store
2. **Resolución de ranking de disciplina** — delega en `RankingDisciplinaRepository`, pero
   también tiene `_calcular_ranking_parcial` para disciplinas sin ranking calculado aún
3. **Exportación de disciplina** — `_exportar_disciplina` produce las filas por atleta
4. **Exportación del overall** — `_exportar_overall` es una variante independiente

Además, el módulo tiene 8+ funciones a nivel de módulo que replican la lógica de
aplicación de eventos de Performance (alternativa al replay vía aggregate):

```python
# A nivel de módulo — no en el handler
def _obtener_estado_y_hash(...) -> tuple[...]: ...
def _obtener_performances_exportables(...) -> list[...]: ...
def _extraer_performance_exportable(...) -> PerformanceExportable | None: ...
def _aplicar_evento_performance_exportable(...) -> PerformanceExportable | None: ...
```

Estas funciones duplican parcialmente la lógica del aggregate `Performance`.
La separación entre métodos del handler y funciones de módulo no sigue un patrón claro.

**Raíz del problema:** La exportación requiere proyectar estado desde eventos sin cargar
el aggregate completo (performance-by-performance). La solución ad-hoc fue añadir
funciones de módulo en lugar de un `PerformanceExportProjection` o similar.

**Severidad:** Media — funciona correctamente, pero la clase y el módulo crecerán si se
agregan nuevos formatos de exportación o nuevas disciplinas.

**Candidato SP-ADJ-06:** Sí — separar `PerformanceReplayer` (responsabilidad de replay)
del handler de exportación. Las funciones de módulo deberían ser métodos de un objeto
de proyección dedicado.

---

### SRP-02 — `ResolucionTarjeta` mezcla construcción, serialización y compatibilidad

```python
# resolucion_tarjeta.py — tres responsabilidades en un VO
@classmethod
def desde_asignacion(cls, ...) -> ResolucionTarjeta: ...     # construcción desde dominio
@classmethod
def desde_payload(cls, ...) -> ResolucionTarjeta: ...         # deserialización desde ES
@classmethod
def _restaurar_motivo_dq(cls, ...) -> MotivoDQ | None: ...   # compatibilidad hacia atrás
def to_event_payload(self) -> dict: ...                       # serialización hacia ES
@property
def rp_observable(self) -> Decimal | None: ...               # lógica de dominio
```

Los tres classmethods de construcción (`desde_asignacion`, `desde_payload`,
`_restaurar_motivo_dq`) tienen propósitos distintos: uno construye desde el flujo
normal del dominio, el otro deserializa para Event Sourcing, el tercero existe por
compatibilidad con payloads viejos. La serialización (`to_event_payload`) está en el
mismo objeto.

En un VO de Event Sourcing, `desde_payload` y `to_event_payload` son inevitables —
el VO es la representación canónica. Pero `_restaurar_motivo_dq` es un parche de
compatibilidad que mezcla responsabilidades.

**Severidad:** Baja — es un hallazgo de cohesión, no un defecto funcional.
El VO funciona correctamente. `_restaurar_motivo_dq` es privado y no contamina la API.

**Candidato SP-ADJ-06:** No urgente. Documentar la existencia del método legacy y su
razón de ser.

---

## OCP — Open/Closed Principle

### OCP-01 — `_p08_finalizacion.py` usa `inspect.signature` para ramificar por aridad

```python
# _p08_finalizacion.py — líneas 73-77
sig = inspect.signature(on_finalizada)
params = list(sig.parameters.values())
if len(params) == 1:
    await on_finalizada(competencia_id)
else:
    await on_finalizada(competencia_id, hash_sha256)
```

El código usa reflexión para detectar cuántos parámetros acepta el callback y ramifica
el comportamiento. Esto viola OCP: si se agrega un tercer parámetro al callback en
alguna política futura, hay que modificar `_p08_finalizacion.py`.

**El problema real:** el callback `on_finalizada` tiene dos firmas distintas en uso:
`(competencia_id)` en un contexto y `(competencia_id, hash_sha256)` en otro. En lugar
de unificar la firma, se añadió detección dinámica.

**Fix correcto:** unificar la firma del callback para que siempre reciba ambos parámetros.
Los llamadores que no necesitan el hash simplemente lo ignoran:

```python
# Firma unificada — el llamador ignora lo que no necesita
async def on_finalizada(competencia_id: CompetenciaId, hash_sha256: str) -> None:
    ...  # el que no necesita hash simplemente no lo usa

# _p08_finalizacion.py — sin inspect
await on_finalizada(competencia_id, hash_sha256)
```

Esto elimina el `import inspect` y hace el contrato del callback explícito en los tipos.

**Severidad:** Media — el código funciona, pero el uso de `inspect.signature` para
controlar el flujo es una señal de diseño incorrecto. Si se agrega un nuevo parámetro
al callback, el bug no se detecta en tiempo de compilación.

**Candidato SP-ADJ-06:** Sí — fix de una sola línea con impacto en el contrato del callback.

---

## LSP — Liskov Substitution Principle

No se encontraron violaciones de LSP en el código nuevo de SP4. Los adaptadores
(`ResendEmailAdapter`, `LoggingEmailAdapter`) son intercambiables a través del puerto
`EmailPort` sin cambios de comportamiento observable. Los repositorios implementan
correctamente sus puertos.

---

## ISP — Interface Segregation Principle

No se encontraron violaciones de ISP. Los puertos (`EmailPort`, `NotificacionRepository`,
`CompetenciaRepository`) son interfaces específicas y no fuerzan dependencias no usadas.

---

## DRY — Don't Repeat Yourself (cross-SOLID)

### DRY-01 — DataClumps en `performance_events.py`: 7 factories con los mismos 3 parámetros

Las 7 funciones factory de eventos de Performance comparten siempre el mismo grupo:

```python
# performance_events.py — patrón repetido en 7 funciones
def crear_ap_registrado(
    performance_id: PerformanceId,
    participante_id: ParticipanteId,
    disciplina: Disciplina,
    competencia_id: CompetenciaId,  # solo en esta factory
    ...
) -> DomainEvent: ...

def crear_resultado_registrado(
    performance_id: PerformanceId,
    participante_id: ParticipanteId,
    disciplina: Disciplina,
    ...
) -> DomainEvent: ...

# × 5 factories más con el mismo patrón (performance_id, participante_id, disciplina)
```

El DesignReviewer detectó 3 DataClumps en este módulo (señal B-5 en `01-designreviewer.md`).
El grupo `(performance_id, participante_id, disciplina)` es un candidato natural
a `PerformanceContext`:

```python
@dataclass(frozen=True)
class PerformanceContext:
    performance_id: PerformanceId
    participante_id: ParticipanteId
    disciplina: Disciplina

# Las factories quedan:
def crear_resultado_registrado(ctx: PerformanceContext, ...) -> DomainEvent: ...
```

**Severidad:** Media — no bloquea, pero cada nueva factory replica el mismo grupo.
Si el contexto de una performance cambia (ej: agregar `juez_id`), hay que actualizar
7 firmas en lugar de 1.

**Candidato SP-ADJ-06:** Sí — VO `PerformanceContext` + refactor de las 7 factories.

---

### DRY-02 — `_registrar_fallo_sin_email` duplicado entre P-10 y P-11

Documentado en `02-analisis-bc-notificaciones.md` como DES-01. Clasificado aquí como
violación DRY. La lógica es idéntica salvo la firma:

- P-10: recibe el objeto `evento: InscripcionConfirmada`
- P-11: recibe `evento_fuente_id: str` directamente

**Fix:** extraer función utilitaria en `application/` compartida, o usar la firma
de P-11 en ambas (más limpia porque desacopla la función del objeto evento).

**Severidad:** Media — crece linealmente con cada nueva política (P-12, P-13...).

**Candidato SP-ADJ-06:** Sí.

---

## Hallazgo adicional — Lazy import como síntoma de dependencia circular

```python
# exportar_resultados.py — import dentro de función
def _performance_a_resultado_final(...):
    from src.competencia.domain.aggregates.performance import Performance
    ...
```

Los imports a nivel de módulo en Python se ejecutan al cargar el módulo. Un import
dentro de una función indica que hacerlo a nivel de módulo causaría un `ImportError`
circular, o que el desarrollador lo evitó intencionalmente por ese motivo.

En hexagonal, `resultados/application/` no debería necesitar importar `Performance`
de `competencia/domain/`. Si lo hace, hay un acoplamiento entre BCs que viola la
arquitectura.

**Acción requerida:** verificar qué se usa de `Performance` en esa función y si
existe una alternativa que no cruce la frontera del BC (ej: usar el repositorio de
performances de Competencia como puerto, o proyectar solo los datos necesarios desde
el event store de Competencia).

**Severidad:** Alta (arquitectónica) — si el import es necesario, hay un problema de
diseño cross-BC. Si es evitable, es deuda acumulada.

**Candidato SP-ADJ-06:** Investigar antes de cerrar BL-004.

---

## Resumen de issues SOLID

| ID | Principio | Archivo | Issue | Severidad | Candidato SP-ADJ-06 |
|----|-----------|---------|-------|-----------|:-------------------:|
| SRP-01 | SRP | `exportar_resultados.py` | Handler mezcla replay, ranking, exportación; funciones de módulo duplican lógica del aggregate | Media | Sí |
| SRP-02 | SRP | `resolucion_tarjeta.py` | VO mezcla construcción, serialización y compatibilidad legacy | Baja | No |
| OCP-01 | OCP | `_p08_finalizacion.py` | `inspect.signature` para ramificar por aridad del callback | Media | Sí |
| DRY-01 | DRY | `performance_events.py` | DataClumps ×7 — candidato a `PerformanceContext` VO | Media | Sí |
| DRY-02 | DRY | `politica_p10.py` + `politica_p11.py` | `_registrar_fallo_sin_email` duplicado | Media | Sí |
| LAZY-01 | Arquitectura | `exportar_resultados.py` | Lazy import de `Performance` desde `resultados/` — posible violación cross-BC | Alta | Investigar |

---

## Observación experimental

Los issues SOLID del SP4 siguen el mismo patrón observado en SP2 y SP3:
las violaciones emergen en los módulos con más carga funcional nueva, no en código
estabilizado. `ExportarResultadosHandler` es el módulo más nuevo y más complejo del SP;
`_p08_finalizacion.py` creció 9 líneas este SP (acumula lógica con cada INC).

El hallazgo de `inspect.signature` en una política de finalización es el único caso
donde la violación introduce riesgo técnico real (el contrato del callback no está
en los tipos). El resto son deudas de consistencia que crecen linealmente.

---

*Creado: 2026-04-16 — Revisión pre-BL-004*
