# ADR-015: Dexie.js como capa de acceso a IndexedDB en frontend

| Campo | Valor |
|-------|-------|
| **Estado** | Aceptada |
| **Fecha** | 2026-04-13 |
| **Autores** | Victor Valotto |
| **Relacionado** | ADR-003, US-4.4.1, US-4.4.2, US-4.4.3 |

---

## Contexto

INC-4.4 requiere operación offline para la interfaz del juez. En `US-4.4.1` la pantalla
de grilla debe precargar y persistir localmente:

- `grilla` de atletas por `(competencia, disciplina)`;
- `estado` de competencia asociado;
- timestamp de actualización.

La API nativa de IndexedDB es verbosa y aumenta complejidad accidental para operaciones
frecuentes (búsqueda compuesta, upsert, versionado de schema, tipado TypeScript).

## Opciones consideradas

**Opción A — IndexedDB nativa**
- Sin dependencia externa.
- Mayor costo de implementación y mantenimiento.

**Opción B — Dexie.js**
- API promise-based y tipada.
- Índices compuestos declarativos.
- Manejo simple de versión/schema.

## Decisión

Se adopta **Dexie.js** como capa de acceso a IndexedDB del frontend.

## Consecuencias

**Positivas**

- Menor fricción para implementar cache offline y cola de comandos.
- Código más legible (`where(...).equals(...)`, `put`, `Table` tipada).
- Base lista para la cola `comando_queue` de `US-4.4.2`.

**Negativas**

- Se agrega una dependencia nueva al frontend.
- Hay que mantener lockfile y actualizarla en revisiones de seguridad.

## Notas de implementación

- DB singleton: `AtaraxiaDiveDB`.
- Tablas creadas en v1:
  - `grilla_cache`
  - `comando_queue` (preparada para US-4.4.2).
- La lógica de precarga vive en `usePrecarga`; `GrillaPage` solo consume estado.

