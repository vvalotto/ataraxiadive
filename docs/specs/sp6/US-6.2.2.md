# US-6.2.2: Inscriptos + Grilla — Categoría Legible + Columna AP → Anuncios

**Estado**: `Done`
**Incremento**: INC-6.2 — Ajustes Organizador  
**Hallazgos**: UI-ORG-03 · UI-ORG-04  
**Bounded Context**: `frontend`  
**Capas afectadas**: `frontend/components/organizador/TablaInscriptos.tsx`, `frontend/components/organizador/TablaGrilla.tsx`

---

## Descripción

Como **organizador revisando inscriptos y grilla**,
quiero **ver la categoría del atleta en formato legible y la columna de marca anunciada con su nombre correcto**
para **interpretar la información sin conocer los códigos internos del sistema**.

---

## Contexto de los Hallazgos

### UI-ORG-03 — Inscriptos: categoría técnica + columna de disciplina sin label claro

**Ubicación**: `frontend/src/components/organizador/TablaInscriptos.tsx`

La columna `Categoria` muestra el valor raw del enum (ej: `SENIOR_MASCULINO`). Además, los headers de las columnas de disciplina muestran solo el código (`DNF`, `STA`) sin indicar que el valor que se muestra es el AP/Anuncio declarado.

### UI-ORG-04 — Grilla: columna "AP" sin nombre correcto

**Ubicación**: `frontend/src/components/organizador/TablaGrilla.tsx` — línea `<th>AP</th>`

El término interno "AP" (Announced Performance) no es claro para el organizador; debe decir "Anuncio".

## Fuente de verdad UX

- `docs/design/ux/wireframes-organizador.md` — estructura de tablas y lenguaje visual del portal organizador.
- `docs/design/ux/prototipos/prototipo-organizador.html` — prototipo navegable aprobado para el rol organizador.
- `docs/plans/sp6/PLAN-SP6.md` — hallazgos UI-ORG-03 y UI-ORG-04 detectados en validación SP5.
- `frontend/src/components/organizador/TablaInscriptos.tsx` y `TablaGrilla.tsx` — implementación React actual comparada contra los hallazgos.

---

## Especificación

### Tarea 1: Formatear categoría en TablaInscriptos

| | |
|---|---|
| **Precondición** | Columna `Categoria` muestra `SENIOR_MASCULINO`, `JUNIOR_FEMENINO`, etc. |
| **Postcondición** | Muestra `Senior M`, `Senior F`, `Master M`, `Master F`, `Junior M`, `Junior F` |
| **Invariante** | Categorías no mapeadas muestran el valor raw como fallback |

```typescript
const CATEGORIA_LABELS: Record<string, string> = {
  SENIOR_MASCULINO: 'Senior M',
  SENIOR_FEMENINO:  'Senior F',
  MASTER_MASCULINO: 'Master M',
  MASTER_FEMENINO:  'Master F',
  JUNIOR_MASCULINO: 'Junior M',
  JUNIOR_FEMENINO:  'Junior F',
}

function formatCategoria(categoria: string): string {
  return CATEGORIA_LABELS[categoria] ?? categoria
}

// En la celda:
<td className="px-4 py-3 text-slate-300">{formatCategoria(row.categoria)}</td>
```

### Tarea 2: Renombrar headers de columna de anuncio en TablaInscriptos

| | |
|---|---|
| **Precondición** | Los headers de las columnas de disciplina muestran solo el código: `DNF`, `STA`, etc. |
| **Postcondición** | Cada header muestra `Anuncio · DNF`, `Anuncio · STA`, etc. |
| **Invariante** | El nombre de la disciplina se mantiene visible para identificar a qué competencia corresponde el AP |

```typescript
// En el thead:
{disciplinasVisibles.map((disciplina) => (
  <th key={disciplina} className="px-4 py-3">
    Anuncio · {disciplina}
  </th>
))}
```

### Tarea 3: Renombrar columna AP → Anuncios en TablaGrilla

| | |
|---|---|
| **Precondición** | `TablaGrilla.tsx` muestra `<th>AP</th>` |
| **Postcondición** | El header muestra `Anuncio` |
| **Invariante** | El dato mostrado en la columna no cambia — solo el label |

```typescript
// En TablaGrilla.tsx:
<th className="px-4 py-3">Anuncio</th>
```

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-6.2.2 — Categoría legible + columna AP renombrada

  Scenario: Categoría se muestra en formato legible
    Given un inscripto con categoria="SENIOR_MASCULINO"
    When el organizador ve la tabla de inscriptos
    Then la columna Categoria muestra "Senior M"

  Scenario: Categoría femenina en formato legible
    Given una inscripta con categoria="JUNIOR_FEMENINO"
    When el organizador ve la tabla de inscriptos
    Then la columna Categoria muestra "Junior F"

  Scenario: Columna de anuncio en inscriptos tiene header claro
    Given un torneo con disciplina DNF
    When el organizador ve la tabla de inscriptos
    Then el header de la columna de AP dice "Anuncio · DNF"

  Scenario: Columna AP de la grilla renombrada
    Given una grilla generada para una disciplina
    When el organizador ve la tabla de grilla
    Then la columna que mostraba "AP" ahora dice "Anuncio"
```

---

## Notas de implementación

- Cambios puramente de presentación — sin impacto en lógica ni backend
- El mapeo `CATEGORIA_LABELS` puede extraerse a un archivo compartido `frontend/src/utils/formatters.ts` si ya existe o si lo necesita alguna otra US del incremento

---

## Referencias

- Hallazgos: `docs/plans/sp6/PLAN-SP6.md` — UI-ORG-03 · UI-ORG-04
- Componentes: `frontend/src/components/organizador/TablaInscriptos.tsx`, `TablaGrilla.tsx`
- Enum backend: `src/registro/domain/value_objects/categoria.py`

---

*Redactado: 2026-05-05 — SP6 INC-6.2*
