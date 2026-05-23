# Plan de Integración Obsidian — AtaraxiaDive Wiki

> **Vault:** `/Users/victor/PycharmProjects/ataraxiadive-wiki/`
> **Branch:** `wiki` (worktree independiente de `develop`)
> **Tiempo estimado total:** ~45 min

---

## Fase 1 — Vault Setup (5 min)

**Objetivo:** Que Obsidian apunte al worktree y muestre el wiki.

1. Abrir Obsidian
2. En la pantalla de inicio → **Open folder as vault**
3. Seleccionar `/Users/victor/PycharmProjects/ataraxiadive-wiki/`
4. Obsidian va a indexar el contenido — esperar que termine

**Verificación:** Deberías ver en el panel izquierdo:
```
ataraxiadive-wiki/
├── WIKI.md
├── OBSIDIAN-SETUP.md  ← este archivo
└── wiki/
    ├── index.md
    ├── arquitectura/
    ├── conceptos/
    ├── decisiones/
    ├── impacto/
    ├── investigacion/
    ├── salud/
    ├── trazabilidad/
    └── vistas/
```

---

## Fase 2 — Configuración básica (5 min)

**Objetivo:** Que los wikilinks funcionen y Obsidian no indexe basura.

Ir a **Settings** (ícono engranaje) y configurar:

### Files & Links
- **Default location for new notes:** `wiki/` (carpeta específica)
- **New link format:** `Shortest path when possible`
- **Use [[Wikilinks]]:** ON ← crítico, es el formato que usa el wiki

### Files & Links → Excluded files
Agregar estas rutas para que Obsidian no las indexe:
```
.git
.claude
.idea
.work
data
```

### Editor
- **Readable line length:** ON (mejora lectura de páginas largas)
- **Show frontmatter:** OFF (el frontmatter es para Dataview, no para leer)

**Verificación:** Abrir `wiki/index.md` — los `[[competencia]]`, `[[ADR-001-event-sourcing-competencia]]` deben aparecer como links azules clickeables, no como texto plano.

---

## Fase 3 — Plugin Dataview (10 min)

**Objetivo:** Habilitar vistas dinámicas que consultan el frontmatter del wiki.

### Instalación
1. Settings → **Community plugins** → **Turn on community plugins**
2. **Browse** → buscar `Dataview`
3. Instalar y **Enable**

### Configuración de Dataview
En Settings → Dataview:
- **Enable JavaScript Queries:** ON
- **Automatic view refreshing:** ON

### Verificación
Crear una nota de prueba temporal con este contenido:

````markdown
```dataview
TABLE title, type, last_updated
FROM "wiki/arquitectura"
SORT last_updated DESC
```
````

Debe mostrar una tabla con los 6 BCs y sus fechas de actualización.
Borrar la nota de prueba una vez verificado.

---

## Fase 4 — Plugin Obsidian Git (10 min)

**Objetivo:** Que los cambios que hagas en Obsidian se commiteen al branch `wiki` automáticamente.

### Instalación
1. Settings → Community plugins → Browse → buscar `Obsidian Git`
2. Instalar y Enable

### Configuración
Settings → Obsidian Git:
- **Vault backup interval (minutes):** `0` (desactivar auto-commit, preferible hacerlo manual)
- **Auto pull interval (minutes):** `0`
- **Default commit message:** `wiki: obsidian edit — {{date}}`
- **Pull updates on startup:** OFF

### Uso manual
- `Cmd+P` → `Obsidian Git: Commit all changes` → commitea al branch `wiki`
- `Cmd+P` → `Obsidian Git: Push` → pushea a `origin/wiki`

> **Nota:** Claude Code también commitea al branch `wiki` desde el worktree.
> No hay conflicto: usá Obsidian Git para ediciones manuales, Claude Code para
> ingests y páginas generadas.

### .gitignore para .obsidian/
Agregar al `.gitignore` del worktree (o commitear `.obsidian/` si querés la config compartida):

```bash
# Desde ataraxiadive-wiki/ en terminal
echo ".obsidian/" >> .gitignore
git add .gitignore
git commit -m "chore: gitignore .obsidian config"
```

---

## Fase 5 — Verificar wikilinks (5 min)

**Objetivo:** Confirmar que la navegación entre páginas funciona sin errores.

### Chequeo de duplicados (posible causa de links rotos)
Ejecutar en terminal desde `ataraxiadive-wiki/`:

```bash
find wiki/ -name "*.md" | xargs -I{} basename {} .md | sort | uniq -d
```

Si aparece algún nombre duplicado, ese link va a necesitar path completo
(ej: `[[arquitectura/competencia]]` en lugar de `[[competencia]]`).

### Navegación de prueba
1. Abrir `wiki/index.md`
2. Clickear `[[competencia]]` → debe abrir `wiki/arquitectura/competencia.md`
3. Desde competencia, clickear cualquier `[[ADR-*]]` → debe abrir la página de decisión
4. Usar `Alt+←` para volver

---

## Fase 6 — Graph View (5 min)

**Objetivo:** Ver el mapa de conocimiento visual del wiki.

1. `Cmd+Shift+G` → abre el Graph View global
2. En el panel de filtros (esquina superior derecha del graph):
   - **Files:** activar filtro `path:wiki/arquitectura` para ver solo BCs
   - **Display:** aumentar **Node size** a 6-8 para mejor visibilidad
3. Los nodos son páginas, las aristas son `[[wikilinks]]`

### Filtros útiles para explorar
| Filtro | Qué muestra |
|--------|-------------|
| `path:wiki/arquitectura` | BCs y sus conexiones |
| `path:wiki/impacto` | Páginas de análisis de riesgo |
| `path:wiki/trazabilidad` | Grafo completo RF → US → BC |
| `path:wiki/decisiones` | ADRs y a qué páginas impactan |

---

## Fase 7 — Enriquecer frontmatter para Dataview (sesión wiki con Claude)

**Objetivo:** Agregar campos al frontmatter de las páginas existentes para
habilitar consultas dinámicas útiles.

Esta fase se hace con Claude Code, no manualmente.

### Campos a agregar por tipo de página

**Páginas de trazabilidad** (`wiki/trazabilidad/US-*.md`):
```yaml
us_id: US-3.3.1
estado: cerrada      # cerrada | en_progreso | pendiente
sp: 3
bc: competencia
tests_count: 12
```

**Páginas de impacto** (`wiki/impacto/*.md`):
```yaml
riesgo: muy_alto     # muy_alto | alto | medio | bajo
bcs_afectados: [competencia, notificaciones]
tipo: interfaz       # interfaz | shared | cross_bc
```

**Páginas de arquitectura** (`wiki/arquitectura/*.md`):
```yaml
tipo_ddd: core       # core | supporting | generic
test_coverage: 78    # porcentaje numérico
```

### Queries Dataview que esto habilita

Una vez enriquecido el frontmatter, reemplazar el contenido estático de
`wiki/vistas/trazabilidad.md` con:

````markdown
## US por estado
```dataview
TABLE us_id, bc, sp, tests_count
FROM "wiki/trazabilidad"
GROUP BY estado
SORT sp ASC
```

## Componentes de riesgo muy alto
```dataview
LIST bcs_afectados
FROM "wiki/impacto"
WHERE riesgo = "muy_alto"
```

## Cobertura por BC
```dataview
TABLE tipo_ddd, test_coverage
FROM "wiki/arquitectura"
WHERE tipo_ddd != null
SORT test_coverage ASC
```
````

---

## Resumen de fases

| Fase | Tiempo | Acción | Herramienta |
|------|--------|--------|-------------|
| 1 | 5 min | Crear vault | Obsidian |
| 2 | 5 min | Configurar settings | Obsidian |
| 3 | 10 min | Instalar Dataview | Obsidian |
| 4 | 10 min | Instalar Obsidian Git | Obsidian |
| 5 | 5 min | Verificar wikilinks | Terminal + Obsidian |
| 6 | 5 min | Explorar Graph View | Obsidian |
| 7 | ~1h | Enriquecer frontmatter | Claude Code |

Las fases 1–6 son independientes y se pueden hacer en orden en una sola sesión.
La Fase 7 es una sesión separada con Claude Code una vez que Obsidian esté operativo.
