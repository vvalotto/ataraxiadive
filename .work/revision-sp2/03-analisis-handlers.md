# Análisis de Handlers — Cierre SP2
## Patrón 2: FeatureEnvy en Commands y Queries

**Fecha:** 2026-03-28
**Handlers inspeccionados:**
- `registrar_ap.py` (FeatureEnvy 22/5)
- `llamar_atleta.py` (CBO 7/5, FeatureEnvy 15/5)
- `asignar_tarjeta.py` (FeatureEnvy 12/6)

---

## Estructura de los Handlers — Patrón canónico CQRS

Los tres handlers y todos los del BC siguen el mismo flujo:

```
1. Verificar precondiciones cross-BC via ports
2. Construir stream_id y cargar aggregate desde Event Store
3. Ejecutar un único método de dominio en el aggregate
4. Persistir eventos pendientes (pull_events + event_store.append)
5. (opcional) Disparar política P-08 u otras side effects
```

Ejemplo de `LlamarAtletaHandler.handle()`:
```python
# 1. Precondición INV-P-05
if not await self._competencia_estado.is_en_ejecucion(command.competencia_id): ...
# 1b. Precondición INV-C-05
if andarivel_activo: raise AndarivelesConflicto(...)
# 2. Cargar aggregate
events = await self._event_store.load(stream_id)
performance = Performance.reconstitute(events)
# 3. Ejecutar dominio
performance.llamar(command.ot_programado, command.posicion_grilla, command.andarivel)
# 4. Persistir
for event in performance.pull_events():
    await self._event_store.append(...)
```

---

## FeatureEnvy — Falso Positivo Confirmado

El analyzer detecta que `handle()` "usa más datos de otras clases que los propios".
Eso es correcto como observación, e incorrecto como diagnóstico:

- En CQRS, el handler es un **orquestador puro** — no tiene estado propio que procesar
- Su responsabilidad es coordinar ports y el aggregate, no poseer lógica
- Todos los handlers lo hacen: el patrón es 100% consistente = convención de diseño, no deuda

**No amerita refactoring.** El código es correcto y bien estructurado.

---

## Hallazgo real: `_build_stream_id` duplicado 11 veces

Descubierto al leer los handlers para validar el FeatureEnvy.

### Duplicación de Performance Stream ID (6 copias idénticas)
```python
# En: registrar_ap.py, llamar_atleta.py, registrar_resultado.py,
#     registrar_dns.py, corregir_resultado.py, asignar_tarjeta.py
def _build_stream_id(competencia_id, participante_id, disciplina) -> str:
    return f"performance-{competencia_id}-{participante_id}-{disciplina.value}"
```

### Duplicación de Competencia Stream ID (5 copias idénticas)
```python
# En: generar_grilla.py, ajustar_grilla.py, confirmar_grilla.py,
#     iniciar_competencia.py, configurar_intervalo_ot.py
def _build_stream_id(competencia_id) -> str:
    return f"competencia-{competencia_id}"
```

**Riesgo:** Si el formato del stream ID cambia, hay que actualizar 11 archivos.
El stream ID es la llave del Event Store — un error de formato es silencioso y rompe la reconstitución.

**Refactor propuesto:**
```python
# competencia/application/commands/_stream_ids.py
def performance_stream_id(competencia_id, participante_id, disciplina) -> str:
    return f"performance-{competencia_id}-{participante_id}-{disciplina.value}"

def competencia_stream_id(competencia_id) -> str:
    return f"competencia-{competencia_id}"
```

---

## Hallazgos para el Experimento

### H-G — FeatureEnvy es un falso positivo predecible en handlers CQRS
El patrón apareció en 100% de los handlers (commands y queries).
El analyzer no distingue entre "clase que envidia datos ajenos" y "clase que orquesta collaborators por diseño".
Configurar FeatureEnvy para que ignore `application/commands/` y `application/queries/` reduciría el ruido significativamente.

### H-H — El análisis automático puede apuntar al área correcta con diagnóstico incorrecto
El FeatureEnvy marcó los handlers → la lectura para validar el warning descubrió la duplicación de stream IDs.
La herramienta fue útil como señal de "lee esta área", aunque su diagnosis específica fue equivocada.
**Implicancia metodológica:** los warnings no deben descartarse sin lectura, incluso cuando son falsos positivos predecibles.

### H-I — La duplicación de stream IDs no fue detectada por ningún analyzer
11 copias de 2 funciones — ningún analyzer de software_limpio lo señaló.
El DataClumpsAnalyzer señaló clumps de parámetros en router.py, pero no esta duplicación en commands/.
Esto es un límite conocido del análisis estático: la duplicación cross-file requiere análisis semántico.
