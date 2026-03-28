# HITO-10 — PerformancesAPPort: el dominio puro cuando el aggregate necesita datos de otro aggregate

| Campo | Valor |
|-------|-------|
| **Documento** | HITO-10 — Análisis experimental |
| **Fecha** | 2026-03-25 |
| **Sprint** | SP2 — Inc 2.1 |
| **Relacionado** | `US-2.1.2` · `src/competencia/domain/ports/performances_ap_port.py` · `src/competencia/infrastructure/repositories/performances_ap_adapter.py` |

---

## Contexto

Al implementar US-2.1.2 (GenerarGrilla), el aggregate `Competencia` necesita los APs
registrados de cada atleta para calcular el ordenamiento de la grilla. Esos APs viven
en eventos del aggregate `Performance` — otro aggregate del mismo BC.

La pregunta de diseño: ¿cómo le damos los datos a `Competencia` sin romper la pureza
del dominio?

---

## El patrón aplicado

Se definió un **puerto secundario** `PerformancesAPPort` en `domain/ports/`:

```python
class PerformancesAPPort(ABC):
    @abstractmethod
    async def get_performances_con_ap(
        self, competencia_id: UUID
    ) -> list[PerformancesAPData]: ...
```

El **handler** orquesta:
1. Reconstituyó `Competencia` desde el Event Store
2. Consultó `PerformancesAPPort` para obtener los datos
3. Pasó `list[PerformancesAPData]` como argumento a `competencia.generar_grilla()`

El **aggregate** recibe datos ya listos — no sabe que existe un Event Store ni un puerto.

La **infraestructura** (`PerformancesAPAdapter`) implementa el puerto: carga todos los
streams `performance-{competencia_id}-*`, reconstituye cada `Performance`, filtra
los que están en estado `AnunciadaAP`.

---

## Qué valida

**Hipótesis H-1 (IEDD + Hexagonal):** Las invariantes formales de la US-IEDD
(`P-01`, `P-02`, `INV-C-01`) se tradujeron directamente a lógica de dominio sin
ambigüedad. No hubo ninguna decisión de implementación no cubierta por la spec.

**Principio de inversión de dependencias en ES:** El aggregate no depende de cómo
se obtienen los datos. Si mañana los APs vienen de una caché o de una proyección
relacional, el aggregate no cambia — solo cambia el adaptador.

**Pureza verificable:** Los 14 tests unitarios de dominio no importan ningún módulo
de `infrastructure/`. La prueba de pureza es ejecutable, no solo declarativa.

---

## Consecuencias observadas

- La firma `generar_grilla(ot_inicio, performances, andariveles)` es completamente
  testeable sin mocks del Event Store — los tests de dominio construyen
  `PerformancesAPData` directamente.
- El `PerformancesAPAdapter` quedó en 65 líneas. La complejidad de "leer streams
  con prefijo" está completamente aislada en infraestructura.
- La prueba de integración con SQLite real (6 tests) validó que el contrato del
  puerto se cumple end-to-end sin modificar el dominio.

---

## Aplicabilidad futura

Este patrón aplica siempre que un aggregate necesite datos de otro aggregate
del mismo BC (o de otro BC vía ACL). La regla: **el aggregate recibe datos,
el handler obtiene datos**. El puerto define el contrato en lenguaje de dominio
(`PerformancesAPData`), no en lenguaje de infraestructura.

En SP2 Inc 2.2 (ejecución de la competencia), `Competencia` necesitará consultar
el estado actual de la grilla confirmada. El mismo patrón aplica.
