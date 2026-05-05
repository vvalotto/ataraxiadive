# US-6.2.3: Resultados — Quitar PTS FAAS + Andarivel Numérico + AP → Anuncio

**Estado**: `Pending`  
**Incremento**: INC-6.2 — Ajustes Organizador  
**Hallazgos**: UI-ORG-05  
**Bounded Context**: `frontend`  
**Capas afectadas**: `frontend/components/organizador/TablaDisciplinaResultados.tsx`, `frontend/pages/organizador/ResultadosPage.tsx`

---

## Descripción

Como **organizador viendo los resultados de una disciplina**,
quiero **una tabla limpia sin columnas de puntuación FAAS, con el número de andarivel literal y la columna de marca anunciada con nombre correcto**
para **presentar resultados claros sin datos de un sistema de puntuación no activo**.

---

## Contexto del Hallazgo

### UI-ORG-05 — Resultados: columnas sobrantes + formateos incorrectos

**Ubicación**: `frontend/src/components/organizador/TablaDisciplinaResultados.tsx`

Hallazgos concretos en el código:
- Línea ~110: `<th className="px-3 py-2 text-right">Pts FAAS</th>` — columna de puntos FAAS siempre visible aunque el sistema FAAS no esté activo
- Líneas ~25-26: `formatearLinea` convierte `1 → A`, `2 → B` — el organizador ve letras en lugar del número de andarivel real
- Columna AP sin renombrar (aplica igual que UI-ORG-04 en grilla)

El hallazgo "Podios y Overall → mover a página propia" está cubierto por **US-6.2.6**.

---

## Especificación

### Tarea 1: Eliminar columna Pts FAAS

| | |
|---|---|
| **Precondición** | `TablaDisciplinaResultados.tsx` renderiza `<th>Pts FAAS</th>` y la celda `<td>{atleta.puntos_faas}</td>` correspondiente |
| **Postcondición** | Ni el `<th>` ni la `<td>` de Pts FAAS se renderizan |
| **Invariante** | El tipo `AtletaResultadoRow` puede mantener el campo `puntos_faas` — no se elimina del modelo, solo de la vista |

### Tarea 2: Andarivel numérico — eliminar conversión A/B

| | |
|---|---|
| **Precondición** | `formatearLinea(1)` retorna `'A'`, `formatearLinea(2)` retorna `'B'` |
| **Postcondición** | La celda de andarivel muestra el número directamente: `1`, `2`, `3`... |
| **Invariante** | Si el andarivel es `null` o `0`, mostrar `—` |

```typescript
// Eliminar formatearLinea o simplificarla:
function formatearAndarivel(andarivel: number | null | undefined): string {
  if (!andarivel) return '—'
  return String(andarivel)
}
```

### Tarea 3: Renombrar columna AP → Anuncio en resultados

| | |
|---|---|
| **Precondición** | La columna que muestra el AP declarado del atleta tiene header `AP` o similar |
| **Postcondición** | El header dice `Anuncio` |
| **Invariante** | El dato (valor del AP + unidad) no cambia |

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-6.2.3 — Tabla resultados sin FAAS + andarivel numérico + AP renombrado

  Scenario: La columna Pts FAAS no aparece en la tabla de resultados
    Given una competencia con resultados calculados
    When el organizador ve la tabla de resultados por disciplina
    Then no existe ninguna columna "Pts FAAS" visible

  Scenario: El andarivel se muestra como número
    Given un atleta en andarivel 1
    When el organizador ve su fila en la tabla
    Then la celda de andarivel muestra "1", no "A"

  Scenario: Andarivel nulo muestra guión
    Given un atleta sin andarivel asignado
    When el organizador ve su fila en la tabla
    Then la celda de andarivel muestra "—"

  Scenario: Columna de marca anunciada tiene header correcto
    Given una tabla de resultados visible
    Then el header que mostraba "AP" ahora dice "Anuncio"
```

---

## Notas de implementación

- Solo se elimina la columna de la vista — no modificar el tipo ni las queries que traen `puntos_faas`
- Verificar que no haya otro componente que llame a `formatearLinea` antes de eliminarlo o renombrarlo
- Esta US no mueve ni elimina PodiosSection — eso es US-6.2.6

---

## Referencias

- Hallazgo: `docs/plans/sp6/PLAN-SP6.md` — UI-ORG-05
- Componente: `frontend/src/components/organizador/TablaDisciplinaResultados.tsx`
- Página: `frontend/src/pages/organizador/ResultadosPage.tsx`

---

*Redactado: 2026-05-05 — SP6 INC-6.2*
