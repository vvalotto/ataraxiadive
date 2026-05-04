# Análisis de Aggregates — Cierre SP2
## Competencia y Performance: complejidad esencial vs accidental

**Fecha:** 2026-03-28
**Archivos analizados:**
- `src/competencia/domain/aggregates/competencia.py` (580 líneas)
- `src/competencia/domain/aggregates/performance.py` (462 líneas)

---

## Performance — Veredicto: falso positivo casi total

**Métricas:** CBO 22/5, GodObject 25/20, WMC 46/20

El código es cohesivo. Cada método hace una sola cosa:
- 6 comandos de dominio (registrarAP, llamar, registrar_resultado, registrar_dns, asignar_tarjeta, corregir_resultado)
- 6 `_apply_*` handlers de reconstitución ES
- 10 propiedades (getters simples)

El **CBO 22 viene exclusivamente de las importaciones estructurales de ES:**
- 6 tipos de eventos
- 7 excepciones de dominio
- 5 Value Objects
- AggregateRoot + stdlib

No hay lógica enredada. El GodObject y WMC altos son consecuencia del conteo de métodos necesarios en ES/CQRS.

**Única deuda real:** `registrarAP` usa camelCase — viola la convención snake_case del resto de la clase.

---

## Competencia — Complejidad accidental identificada

**Métricas:** CBO 23/5, GodObject 21/20, WMC 60/20

Similar a `Performance` en cuanto a CBO (imports estructurales), pero tiene complejidad accidental real en `ajustar_grilla`.

### El método problema: `ajustar_grilla` (127 líneas, líneas 220–346)

Mezcla tres responsabilidades:
1. **Validaciones de precondición** (líneas 239–256) — correcto, es parte del comando
2. **Algoritmo de swap de posiciones** (líneas 258–316) — lógica no trivial, podría ser helper
3. **Recálculo de OTs** (líneas 318–333) — duplicado de lógica presente en otros dos lugares

### Triplicación de lógica de recálculo OT

La misma operación (`ot_inicio + timedelta(minutes=(posicion-1) * intervalo)`) aparece en:
- `generar_grilla` líneas 183–205
- `ajustar_grilla` líneas 318–333
- `_apply_grilla_de_salida_ajustada` líneas 524–538

**Esto es complejidad accidental confirmada.**

---

## Refactor propuesto para Competencia

Extraer dos funciones a nivel de módulo (patrón ya presente: `_ordenar_performances`, `_calcular_andarivel`):

```
_recalcular_ots(grilla, ot_inicio, intervalo) → list[EntradaGrilla]
    Elimina la triplicación del cálculo de OTs.

_aplicar_swap_posicion(grilla_mutable, cambio) → dict
    Encapsula el algoritmo de desplazamiento del ocupante.
```

**Resultado esperado:** `ajustar_grilla` reduciría de 127 a ~50 líneas.
No cambia la frontera del aggregate, no rompe tests.

---

## Diagnóstico comparativo

| Aggregate | Métricas CRITICAL | Causa principal | Refactor real necesario |
|---|---|---|---|
| `Performance` | CBO 22, WMC 46, GodObject 25 | Imports estructurales ES | No — falso positivo |
| `Competencia` | CBO 23, WMC 60, GodObject 21 | Imports estructurales ES + `ajustar_grilla` | Sí — extraer helpers para OT y swap |

---

## Hallazgos para el Experimento

### H-D — Los aggregates ES tienen CBO estructural irreducible
Incluso un aggregate mínimo con 3 eventos, 3 VOs y 3 excepciones supera CBO 5.
El umbral es incorrecto para ES. La señal útil de CBO en este contexto es la *magnitud relativa*
(CBO 23 vs CBO 8 — ambos CRITICAL pero muy diferentes en riesgo real).

### H-E — La duplicación de lógica no la detecta el DesignReviewer
La triplicación del cálculo de OTs en `Competencia` es complejidad accidental real,
pero ningún analyzer la detectó. El LongMethodAnalyzer lo señaló indirectamente (127 líneas),
pero la causa raíz (duplicación) requirió lectura manual del código.
**El análisis estático no reemplaza la revisión de código manual en el cierre de SP.**

### H-F — LCOM bajo en aggregates ES es esperado
LCOM 2/1 en `Competencia` y `RankingCompetencia` indica dos grupos de métodos que no comparten estado.
En ES, esto es estructural: los comandos usan estado de negocio, los `_apply_*` reconstruyen estado.
Son dos "caras" del mismo aggregate por diseño — no es baja cohesión accidental.

---

## Pendiente de decisión
- [ ] ¿Ejecutar refactor `ajustar_grilla` ahora o documentar como deuda en BL-002?
- [ ] Corregir `registrarAP` → `registrar_ap` (snake_case) en Performance
