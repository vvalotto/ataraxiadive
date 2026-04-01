# US-ADJ-3.1: Extraer `GrillaDeSalida` como entidad de dominio

**Estado**: `To Do`
**Sprint**: SP-ADJ-03 — Ajuste Técnico Post-SP3
**Bounded Context**: `competencia`
**Capas afectadas**: `competencia/domain/entities/` · `competencia/domain/aggregates/` · `competencia/infrastructure/`

---

## Descripción

Como **desarrollador del sistema**,
quiero **extraer `GrillaDeSalida` como entidad de dominio separada de `Competencia`**
para **reducir el WMC del aggregate (64 → ~34) y separar las responsabilidades de grilla del ciclo de vida de la competencia**.

---

## Contexto de la deuda

Al cerrar INC-3.3 (US-3.3.1), DesignReviewer reportó WMC=64 en `Competencia`, superando
el umbral anterior de 60. Se ajustó el umbral a 65 como medida de emergencia para no
bloquear el merge, pero el problema de fondo persiste.

### Diagnóstico

`Competencia` (594 líneas) tiene LCOM=2 — dos clusters de cohesión identificados:

**Cluster A — Lifecycle de la competencia (WMC ≈ 24):**
- `configurar_intervalo_ot`, `abrir`, `iniciar`, `cerrar`
- `_apply_intervalo_ot_configurado`, `_apply_competencia_abierta`, `_apply_competencia_iniciada`, `_apply_competencia_cerrada`
- Estado: `_estado`, `_disciplina`, `_intervalo_ot`, `_torneo_id`

**Cluster B — Gestión de la grilla (WMC ≈ 40):**
- `generar_grilla`, `ajustar_grilla`, `confirmar_grilla`, `obtener_grilla`
- `_build_grilla_de_salida`, `_apply_grilla_generada`, `_apply_grilla_ajustada`, `_apply_grilla_confirmada`
- Estado: `_entradas`, `_estado_grilla`

La grilla tiene su propio estado (`_estado_grilla`), sus propios eventos, y sus propias
invariantes (INV-C-04: orden por AP, INV-C-05: andariveles, INV-C-06: swap válido).
Es una entidad natural dentro del aggregate.

### WMC por grupo (estimado)

| Grupo | Métodos | WMC |
|-------|---------|-----|
| Lifecycle | 8 métodos + 4 `_apply_*` | ~24 |
| Grilla | 4 comandos + 4 `_apply_*` + `_build_*` | ~40 |
| Reconstitución | `reconstitute`, `_apply_stored`, `_parse_payload` | ~7 |
| **Total** | **~26 métodos** | **~64** (WMC actual) |

---

## Especificación

### Postcondición

```
competencia/domain/entities/grilla_de_salida.py   ← NUEVO
competencia/domain/aggregates/competencia.py       ← MODIFICADO (WMC ~34)
competencia/infrastructure/                        ← ajustar reconstitución si aplica
```

### Estructura propuesta de `GrillaDeSalida`

```python
class GrillaDeSalida:
    """Entidad que modela la grilla de salida de una competencia.

    Responsable de:
    - generar la grilla ordenada por AP descendente (INV-C-04)
    - ajustar posiciones por swap de atletas (INV-C-06)
    - confirmar la grilla (pasa a estado Confirmada)
    - asignar andariveles (INV-C-05)

    Invariantes:
        INV-C-04: entradas ordenadas por AP descendente
        INV-C-05: andarivel siempre entre 1 y n_andariveles
        INV-C-06: swap solo entre posiciones existentes
    """
    def __init__(self, n_andariveles: int) -> None: ...
    def generar(self, performances: list[Performance]) -> list[EntradaGrilla]: ...
    def ajustar(self, posicion_a: int, posicion_b: int) -> None: ...
    def confirmar(self) -> None: ...
    def obtener(self) -> list[EntradaGrilla]: ...

    @property
    def estado(self) -> EstadoGrilla: ...
    @property
    def entradas(self) -> list[EntradaGrilla]: ...
```

### `Competencia` post-refactor

- Delega toda la lógica de grilla a `GrillaDeSalida`
- Mantiene referencia `self._grilla: GrillaDeSalida | None`
- Los eventos de grilla siguen emitiéndose desde `Competencia` (el aggregate raíz es el emisor de eventos en Event Sourcing)
- La reconstitución aplica los eventos de grilla a través de `self._grilla`

### Invariantes preservadas

- `INV-C-04`: orden por AP descendente — se mueve a `GrillaDeSalida.generar()`
- `INV-C-05`: andariveles — se mueve a `GrillaDeSalida.generar()` / `ajustar()`
- `INV-C-06`: swap válido — se mueve a `GrillaDeSalida.ajustar()`

### Impacto en tests

Todos los tests existentes de `Competencia` permanecen sin cambio (la interfaz pública
de `Competencia` no cambia — los mismos métodos, los mismos eventos). La extracción
es interna al aggregate.

---

## Criterios de aceptación

```gherkin
Scenario: WMC de Competencia post-refactor dentro del umbral
  Given el aggregate Competencia refactorizado con GrillaDeSalida
  When se ejecuta DesignReviewer
  Then WMC de Competencia <= 40
  And max_wmc en pyproject.toml puede bajar a 45

Scenario: tests existentes de grilla no se rompen
  Given el refactor aplicado
  When se ejecuta la suite completa de tests de competencia
  Then todos los tests pasan sin modificación

Scenario: la interfaz pública de Competencia no cambia
  Given el refactor aplicado
  Then generar_grilla / ajustar_grilla / confirmar_grilla / obtener_grilla
       siguen existiendo en Competencia con la misma firma
```

---

## Notas de implementación

- `GrillaDeSalida` es una **entidad** (tiene identidad implícita por su `competencia_id`),
  no un VO (tiene estado mutable).
- Los **eventos siguen siendo responsabilidad del aggregate** — `GrillaDeSalida` no emite
  eventos, los emite `Competencia` después de delegar en la entidad.
- El directorio `competencia/domain/entities/` debe crearse (actualmente no existe).
- Si `GrillaDeSalida` requiere importar `Performance`, hay que verificar que no
  introduce un ciclo de imports — `Performance` también vive en `competencia/domain/`.

---

## Referencias

- Análisis: sesión 2026-04-01 — análisis WMC Competencia post-INC-3.3
- DesignReviewer INC-3.3: `quality/reports/designreviewer/INC-3.3-report.txt`
- US-3.3.1: `torneo_id` en Competencia (el cambio que hizo subir WMC a 64)
- Plan SP-ADJ-03: `docs/plans/sp-adj-03/PLAN-SP-ADJ-03.md`

---

*Redactado: 2026-04-01 — SP-ADJ-03*
