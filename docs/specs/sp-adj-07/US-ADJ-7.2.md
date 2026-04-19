# US-ADJ-7.2: Exponer `tarjeta_asignada` en `/grilla` — BUG-SP4-004

**Estado**: `Implementada`
**Iteración / Sprint**: SP-ADJ-07
**Tipo**: fix de API + frontend
**Agregado principal afectado**: `ObtenerGrillaHandler`
**Bounded Context**: `competencia` + frontend `AuditoriaPage`

---

## Descripción (lenguaje de negocio)

Como **organizador**,
quiero ver el color de la tarjeta de cada atleta en la grilla de auditoría
para identificar de un vistazo qué atletas obtuvieron tarjeta blanca, con penalizaciones,
o roja, sin necesidad de abrir el detalle de cada uno.

---

## Contexto del dominio

### Problema

`ObtenerGrillaHandler` proyecta `EntradaGrillaDTO` que incluye `estado` pero no
`tarjeta_asignada`. La pantalla de auditoría del organizador (`AuditoriaPage.tsx`)
necesita este dato para aplicar colores condicionales:

| Tarjeta | Color esperado |
|---------|----------------|
| `Blanca` | verde |
| `BlancaConPenalizaciones` | amarillo-ámbar |
| `Roja` | rojo |
| `EnRevision` / sin tarjeta | gris neutro |

El aggregate `Performance` ya expone `performance.tarjeta → TipoTarjeta | None` (propiedad
existente en `performance.py` línea 136). El dato está disponible — solo falta exponerlo.

### Modelo involucrado

| Elemento DDD | Nombre | Responsabilidad |
|---|---|---|
| Query Handler | `ObtenerGrillaHandler` | Proyecta el read model de la grilla |
| DTO | `EntradaGrillaDTO` | Añadir campo `tarjeta_asignada: str \| None` |
| Proyección interna | `_PerformanceProjection` | Añadir campo `tarjeta_asignada: str \| None` |

---

## Especificación del comportamiento

### Precondición

`GET /competencias/{id}/grilla?disciplina=DNF` retorna la lista de entradas de grilla
sin el campo `tarjeta_asignada`.

### Postcondición

La respuesta incluye `tarjeta_asignada: string | null` para cada entrada:
- `null` si la performance no tiene tarjeta asignada aún (estados: `AnunciadaAP`,
  `Llamada`, `ResultadoRegistrado`, `EnRevision`)
- `"Blanca"`, `"BlancaConPenalizaciones"`, `"Roja"` si la tarjeta fue asignada
  (estados: `Ejecutada`)

### Invariante de lectura

El valor de `tarjeta_asignada` es siempre el valor actual del campo `tarjeta` del
aggregate `Performance` en el momento de la proyección. Es un campo de solo lectura;
no expone ningún comando nuevo.

---

## Criterios de aceptación

```gherkin
Feature: Grilla de competencia expone tarjeta_asignada

  Background:
    Given una competencia con 3 atletas: uno con tarjeta blanca, uno con tarjeta roja, uno en Llamada

  Scenario: La grilla incluye tarjeta_asignada para atletas con tarjeta
    When se hace GET /competencias/{id}/grilla?disciplina=DNF
    Then la respuesta incluye tarjeta_asignada="Blanca" para el primer atleta
    And la respuesta incluye tarjeta_asignada="Roja" para el segundo atleta
    And la respuesta incluye tarjeta_asignada=null para el tercero (estado Llamada)

  Scenario: La grilla incluye tarjeta_asignada para atleta con penalizaciones
    Given un atleta con tarjeta blanca con penalizaciones aplicadas
    When se hace GET /competencias/{id}/grilla?disciplina=DNF
    Then tarjeta_asignada="BlancaConPenalizaciones" para ese atleta

  Scenario: La grilla incluye tarjeta_asignada=null para atleta DNS
    Given un atleta en estado DNS
    When se hace GET /competencias/{id}/grilla?disciplina=DNF
    Then tarjeta_asignada=null para ese atleta

  Scenario: El frontend de auditoría aplica color según tarjeta_asignada
    Given una grilla con atletas en distintos estados de tarjeta
    When el organizador abre AuditoriaPage
    Then los atletas con tarjeta blanca tienen fondo verde
    And los atletas con tarjeta con penalizaciones tienen fondo ámbar
    And los atletas con tarjeta roja tienen fondo rojo
    And los atletas sin tarjeta asignada tienen fondo neutro
```

---

## Artefactos a modificar

| Artefacto | Cambio |
|-----------|--------|
| `src/competencia/application/queries/obtener_grilla.py` | Agregar `tarjeta_asignada: str \| None` a `EntradaGrillaDTO` y `_PerformanceProjection`; extraer en `_load_performance` |
| `frontend/src/pages/organizador/AuditoriaPage.tsx` (o el componente de grilla equivalente) | Consumir `tarjeta_asignada` del endpoint; aplicar clases de Tailwind condicionales |

---

## Cambio en `obtener_grilla.py`

### `EntradaGrillaDTO`

```python
@dataclass
class EntradaGrillaDTO:
    performance_id: str
    atleta_id: str
    nombre_atleta: str
    posicion: int
    andarivel: int
    ot_programado: str
    ap_declarado: str
    unidad: str
    estado: str
    tarjeta_asignada: str | None  # ← nuevo campo
```

### `_PerformanceProjection`

```python
@dataclass(frozen=True)
class _PerformanceProjection:
    nombre_atleta: str
    ap_declarado: str
    unidad: str
    estado: str
    tarjeta_asignada: str | None  # ← nuevo campo
```

### `_load_performance` — extracción del valor

```python
return _PerformanceProjection(
    nombre_atleta=nombre,
    ap_declarado=str(ap.valor) if ap else "",
    unidad=ap.unidad.value if ap else "",
    estado=performance.estado.value if performance.estado else "",
    tarjeta_asignada=performance.tarjeta.value if performance.tarjeta else None,
)
```

`performance.tarjeta` es la propiedad ya existente en el aggregate (`TipoTarjeta | None`).

---

## Cambio en el frontend

En el componente de auditoría, aplicar clases condicionales por `tarjeta_asignada`:

```typescript
function clasePorTarjeta(tarjeta: string | null): string {
  switch (tarjeta) {
    case "Blanca": return "bg-green-100 text-green-800";
    case "BlancaConPenalizaciones": return "bg-amber-100 text-amber-800";
    case "Roja": return "bg-red-100 text-red-800";
    default: return "bg-slate-100 text-slate-600";
  }
}
```

---

## Notas de implementación

1. El campo `tarjeta_asignada` en el JSON de respuesta se incluye automáticamente al
   añadirlo al DTO — el router serializa con `dict()` (FastAPI lo convierte a JSON).
2. Los tests de integración existentes de `ObtenerGrillaHandler` deben actualizarse para
   verificar el nuevo campo (no solo que no rompen — verificar el valor correcto).
3. Validar que el frontend TypeScript del tipo de respuesta esté actualizado para incluir
   `tarjeta_asignada?: string | null`.

---

*Spec creada: 2026-04-19 — BUG-SP4-004 de BL-004*
