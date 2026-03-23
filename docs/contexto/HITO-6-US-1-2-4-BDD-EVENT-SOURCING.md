# HITO-6 — US-1.2.4: Fricción BDD × Event Sourcing × Invariantes DDD

| Campo | Valor |
|-------|-------|
| **Documento** | HITO-6 — Análisis experimental |
| **Fecha** | 2026-03-22 |
| **Alcance** | US-1.2.4 — AsignarTarjeta |
| **Hipótesis activas** | RQ1 (fricción de ecosistema), RQ2 (calidad de especificaciones IEDD) |
| **Relacionado** | `HITO-4` · `HITO-5` · PR #16 · Issue #5 |

---

## 1. Contexto

US-1.2.4 introduce la tarjeta como cierre del ciclo de vida de `Performance`.
El aprendizaje experimental principal no es sobre el código sino sobre la
interacción entre tres elementos del stack metodológico:
**BDD (pytest-bdd) × Event Sourcing × invariantes DDD**.

---

## 2. El Patrón: Conflicto Background × Estado Intermedio

### Problema observado

Los escenarios BDD del Feature US-1.2.4 tienen un **Background** que ejecuta
el camino nominal completo hasta el estado `ResultadoRegistrado`:

```
AP registrado → Atleta llamado → Resultado registrado
```

Un escenario de rechazo necesita la performance en estado `Llamada` (no en
`ResultadoRegistrado`). Pero al ejecutar el Background ya se creó el stream
con todos los eventos — incluyendo `APRegistrado`. Intentar re-registrar el AP
desde el step específico del escenario activa **INV-P-02** (`APYaRegistrado`),
bloqueando el setup del test.

### Causa raíz

No es un bug de pytest-bdd ni de la implementación. Es una consecuencia
estructural de dos decisiones de diseño que interactúan:

1. **INV-P-02 es un invariante del aggregate** — correcto por diseño DDD.
2. **Background en BDD** es estado compartido entre todos los escenarios del Feature.

Cuando el Background cubre el camino nominal completo (la mayoría de los casos),
los escenarios que prueban estados intermedios quedan en conflicto con los
invariantes del aggregate.

### Solución adoptada

Crear un event store con base de datos temporal fresca en el step específico:

```python
@given('la performance del atleta está en estado "Llamada"')
def step_performance_en_llamada(ctx: dict) -> None:
    fresh_store = _make_event_store(tempfile.mkdtemp())  # DB nueva
    cid = uuid4()  # IDs nuevos
    pid = uuid4()
    ctx["event_store"] = fresh_store
    ctx["competencia_id"] = cid
    ctx["participante_id"] = pid
    # ... setup hasta Llamada solamente
```

El step reemplaza el contexto completo — IDs, event store, estado — por uno
que llega solo hasta el estado deseado.

---

## 3. Análisis Experimental

### Relación con RQ2: ¿IEDD mejora la calidad de las especificaciones?

Este patrón de conflicto se hace **visible gracias a las especificaciones IEDD**:
los invariantes están documentados explícitamente (INV-P-02) y los criterios
de aceptación BDD son precisos sobre el estado previo requerido.

Sin INV-P-02 en la especificación, el conflicto habría aparecido como un error
de setup oscuro. Con la especificación IEDD, el análisis fue inmediato.

**Hipótesis derivada (H-6.1):** En sistemas event-sourced con invariantes DDD
fuertes, la fricción BDD × DDD es proporcional a la completitud de las
especificaciones. Más invariantes = más conflictos de Background = más
necesidad de aislamiento de contexto por escenario.

### Relación con RQ1: ¿El ecosistema genera fricción?

La fricción en este caso es **intrínseca al problema**, no al ecosistema.
pytest-bdd, el Event Store y los invariantes DDD se comportan correctamente.
La fricción emerge de la interacción entre ellos.

Esto modifica la hipótesis H-4.1 originalmente planteada en HITO-4:
no toda fricción es "bug de herramienta". Parte de la fricción es
**fricción estructural** — inherente a la combinación de prácticas elegidas.

**Hipótesis derivada (H-6.2):** La fricción estructural (BDD × Event Sourcing
× invariantes fuertes) es predecible y manejable con patrones de aislamiento
de contexto. No requiere simplificar el modelo.

### Relación con la hipótesis H-2.5 (HITO-2)

HITO-2 identificó el patrón "Capa 4 antes de Capa 3" como posible limitación
de IEDD con IA. Este HITO agrega un patrón complementario:
**"Especificación antes de integración de prácticas"** — la fricción entre
BDD y Event Sourcing se resolvió fácilmente porque los invariantes estaban
especificados antes de escribir los tests.

---

## 4. Patrón Reutilizable: Aislamiento de Contexto BDD

Para futuros Features BDD sobre aggregates event-sourced con invariantes fuertes:

**Regla:** Si el Background llega al estado nominal final, los escenarios de
rechazo que requieren estados intermedios deben crear su propio contexto aislado
(event store + IDs frescos) en el step `Given` específico.

**Cuándo no se necesita:** Si el Background solo establece precondiciones
mínimas (ej: "existe una competencia activa") sin ejecutar la cadena de eventos
completa.

**Señal de alerta:** Si un step `Given` de escenario falla con un invariante
de dominio (`APYaRegistrado`, `EstadoInvalidoParaLlamar`, etc.) durante el
*setup* del test — no durante el *When* — es síntoma de conflicto
Background × estado intermedio.

---

## 5. Métricas US-1.2.4

| Métrica | Valor |
|---------|-------|
| Tiempo real (tracker) | 17 min |
| Tests totales | 92 |
| Coverage | 98.34% |
| CRITICAL DesignReviewer | 0 |
| Escenarios BDD | 6/6 ✅ |
| Ajuste max_cbo | 14 → 17 |
| Ajuste max_wmc | 25 → 36 |

---

## 6. Estado de Hipótesis del Experimento

| Hipótesis | Estado | Evidencia |
|-----------|--------|-----------|
| H-4.1: overhead → bugs herramienta, no complejidad | ✅ Verificada (US-1.2.1-1.2.4) | Tiempos estables 9-18 min una vez estabilizado |
| H-6.1: fricción BDD ∝ completitud de invariantes | 🔵 Nueva — requiere más ciclos | Observada una vez (US-1.2.4) |
| H-6.2: fricción estructural es predecible | 🔵 Nueva — requiere más ciclos | Resuelta con patrón de aislamiento |

---

*2026-03-22 — HITO-6 — generado tras US-1.2.4 / PR #16*
