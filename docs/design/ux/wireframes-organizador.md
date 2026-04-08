# Wireframes — Interfaz del Organizador

> Artefacto INC-4.0 · Especificación formal derivada de `prototipo-organizador.html` validado
> Fuente reglamentaria: CMAS Apnea Indoor v2022/01 (FAAS)
> Última actualización: 2026-04-05

---

## Principios de diseño

| Principio | Valor |
|-----------|-------|
| Tema | Dark (fondo #0f172a) |
| Ancho máximo de contenido | 1100 px (desktop-first) |
| Altura de navbar | 56 px sticky |
| Fuente | System UI (-apple-system, BlinkMacSystemFont) |
| Layout | Two-column (50/50) para secciones de detalle |
| Contraste | Alto — legible en sala de competencia con luz variable |

**Tokens de color** (compartidos con el juez):

| Token | Valor | Uso |
|-------|-------|-----|
| `--bg` | `#0f172a` | Fondo general |
| `--surface` | `#1e293b` | Cards, panels, navbar |
| `--surface2` | `#334155` | Inputs, botones ghost, encabezados de tabla |
| `--border` | `#475569` | Bordes generales |
| `--accent` | `#38bdf8` | Acción principal, link activo nav, AP |
| `--blanca` | `#22c55e` | Tarjeta blanca, progreso |
| `--amarilla` | `#eab308` | Tarjeta amarilla, alertas |
| `--roja` | `#ef4444` | Tarjeta roja, DQ, cierre forzado |
| `--dns` | `#64748b` | DNS |
| `--muted` | `#94a3b8` | Texto secundario, labels |

---

## Navegación principal

La aplicación del organizador es de pantalla única con navegación por tabs en la barra superior. La navbar es sticky (siempre visible al hacer scroll).

**Estructura de la navbar:**

```
[AtaraxiaDive]  [📊 Panel]  [📋 Grilla]  [🏆 Resultados]  [👥 Jueces]  [📝 Torneo]  [🔍 Audit Log]  →  [● En línea]  [Nombre usuario]
```

| Elemento | Comportamiento |
|----------|---------------|
| Marca (izquierda) | Decorativo — no navega |
| Nav items | Tab activo con borde inferior accent + color accent |
| Badge conexión | Verde "En línea" / Rojo "Sin conexión" |
| Nombre usuario | Solo informativo |

**Invariante de navegación:** cada pantalla reusa la misma navbar con el item correspondiente marcado como `active`. La función `go(screenId)` sincroniza el estado activo automáticamente mediante el mapa `navMap`.

---

## Pantallas

### S-00 — Login

**Propósito:** autenticación del organizador.

**Layout:** centrado vertical y horizontal, caja de 380 px máximo.

**Componentes:**
- Logo "AtaraxiaDive" (accent, 28 px, 900 weight)
- Subtítulo "Panel de Organización" (muted)
- Campo Email
- Campo Contraseña
- Botón `INGRESAR` (btn-primary, ancho completo, 44 px alto)
- Label "Rol activo: **Organizador**"

**Acción:**
- `INGRESAR` → S-01 Dashboard

---

### S-01 — Dashboard (Panel Principal)

**Propósito:** vista ejecutiva del estado del torneo en ejecución. Punto de entrada tras login.

**Layout:** KPI strip + two-column (disciplina activa | alertas + próximos).

#### KPI strip (4 columnas)

| KPI | Valor mock | Color valor |
|-----|-----------|-------------|
| Atletas totales | 28 | default |
| Completados | 2 de 12 en DNF | `--blanca` |
| En revisión | 1 tarjeta amarilla | `--amarilla` |
| Tiempo estimado | 83' para fin de DNF | `--accent` |

#### Columna izquierda — Disciplina en ejecución

Componente `disc-status` con:
- Nombre disciplina + horario + andariveles + cantidad atletas
- Badge de estado: `EN EJECUCIÓN` (verde) / `PENDIENTE` (gris) / `CERRADA` (accent)
- Barra de progreso horizontal (fill `--blanca`, proporcional a completados/total)
- Label de progreso: "N de M atletas completados (X%)"
- Botones: `Ver grilla completa` (outline) → S-02 · `Cerrar disciplina` (roja, requiere confirmación)

Sección "Otras disciplinas del torneo": lista de `disc-card-mgmt` con disciplinas no activas, solo informativas (badge PENDIENTE, sin acción habilitada).

#### Columna derecha — Alertas activas

Cada alerta es un `alert-card` con:
- Ícono + título + descripción (atleta, disciplina, OT, RP)
- Botón/texto "Resolver →" (accent)
- Tap en la card navega a S-03 (detalle amarilla)

**Invariante UX:** si no hay alertas activas, mostrar empty state "Sin alertas".

Sección "Próximos en DNF": tabla compacta con columnas `#, Atleta, OT, AP, Estado`. El siguiente en ejecutar muestra fila `row-siguiente` (fondo accent tenue + chip "▶ SIGUIENTE").

---

### S-02 — Grilla de Salida (Completa)

**Propósito:** vista exhaustiva de todos los atletas de la disciplina activa. Permite supervisar el progreso y acceder a resoluciones de amarilla.

**Header de página:**
- Título "Grilla — [DISCIPLINA]" + botones `↓ Exportar PDF` y `← Panel`
- Subtítulo: estado + cantidad atletas + intervalo + andariveles

**Filtros rápidos (pill buttons):**

| Filtro | Estilo cuando activo |
|--------|---------------------|
| Todos (N) | outline accent |
| Pendientes (N) | ghost |
| Completados (N) | ghost |
| ⚠ Revisión (N) | ghost amarilla |

**Tabla principal — columnas:**

| Columna | Ancho | Descripción |
|---------|-------|-------------|
| `#` | 36 px | Posición en grilla (orden OT) |
| Atleta | auto | Apellido, Nombre (font-weight 600) |
| Cat. | auto | Categoría (Senior M/F, Junior, Master) — muted sm |
| OT | auto | Hora del OT — muted 13 px |
| And. | auto | Andarivel A / B — muted |
| AP | auto | Distancia anunciada — accent bold |
| RP | auto | Distancia realizada — bold / "—" si pendiente |
| Juez | auto | Chip `chip-juez` con nombre abreviado |
| Estado | auto | Chip de estado (ver tabla de chips) |
| Acciones | auto | Botón contextual según estado |

**Chips de estado en grilla:**

| Estado | Clase CSS | Texto |
|--------|-----------|-------|
| Completado | `chip-blanca` | ✓ BLANCA |
| En revisión | `chip-amarilla` | ⚠ REVISIÓN |
| Siguiente | `chip-sig` | ▶ SIGUIENTE |
| Pendiente | `chip-pend` | PENDIENTE |
| DNS | `chip-dns` | DNS |
| DQ | `chip-roja` | ROJA |

**Estilos de fila:**

| Condición | Clase | Efecto |
|-----------|-------|--------|
| Atleta completado | `row-done` | opacity 0.5 |
| Siguiente atleta | `row-siguiente` | fondo accent tenue |
| Fila con acción | `row-action` | cursor pointer, hover sutil |

**Botones contextuales (columna acciones):**

| Estado atleta | Botón | Destino |
|--------------|-------|---------|
| BLANCA | `Log` (ghost sm) | S-07 Audit Log |
| REVISIÓN | `Resolver` (outline amarilla sm) | S-03 Detalle Amarilla |
| SIGUIENTE / PENDIENTE | — | sin botón |

**Invariante de orden:** filas ordenadas por OT ascendente. Ningún atleta pendiente puede tener OT anterior a un atleta completado.

---

### S-03 — Detalle Amarilla — Resolución

**Propósito:** interfaz para que el organizador (junto con los jueces) resuelva formalmente una tarjeta amarilla pendiente.

**Acceso:** desde S-01 (alerta) o S-02 (botón "Resolver").

**Header:** `← Grilla` + título "Resolución — Tarjeta Amarilla".

**Layout:** two-column.

#### Columna izquierda — Datos de la performance

Panel `detail-panel` con filas label/valor:

| Campo | Valor mock |
|-------|-----------|
| Atleta | López, Andrés |
| Disciplina | DNF — #2 |
| OT | 14:09 · Andarivel B |
| AP declarado | 72.0 m (accent bold) |
| RP medido | 66.0 m |
| Juez | Carlos Méndez |
| Motivo revisión | Protocolo superficie dudoso (amarilla) |

Panel inferior — Penalización aplicable (CMAS 1.1.13.1):
- Texto informativo: "En caso de resolver como BLANCA con penalización general: se restan **3 metros** a la distancia realizada."
- RP efectivo con penalización: **63.0 m** (accent)

#### Columna derecha — Formulario de resolución

Aviso reglamentario (fondo amarilla tenue):
> ⚠ Los jueces tienen máximo **3 minutos** para dar la decisión final (CMAS 1.2.3.1).

Campo **Decisión** (select):
- `Seleccionar resolución...` (placeholder)
- `BLANCA — Performance válida (sin penalización)`
- `BLANCA con penalización — RP: 63.0 m (−3 m)`
- `ROJA — Descalificada (DQ)`

Campo **Observaciones** (textarea, 3 filas, resize vertical): motivo de la decisión.

Botones de acción (lado a lado, ancho completo):
- `⬜ CONFIRMAR BLANCA` (btn-blanca) → S-02 Grilla
- `🟥 CONFIRMAR ROJA` (btn-roja) → S-02 Grilla

**Invariante de negocio:** la resolución es irreversible desde la UI del organizador. El audit log registra el evento con SHA-256. No se puede dejar en estado REVISIÓN indefinidamente (bloquea el cierre de disciplina).

---

### S-04 — Resultados

**Propósito:** vista de rankings parciales por disciplina y ranking overall (disponible al cerrar todas las disciplinas).

**Header:** título "Resultados" + botón `Publicar resultados` (btn-primary sm).

**Subtítulo:** disciplina activa + estado del ranking (parcial/final) + progreso.

**Layout:** two-column.

#### Columna izquierda — Ranking por disciplina (parcial)

Lista de `rank-row`:

| Elemento | Descripción |
|----------|-------------|
| `rank-pos` | Posición numérica (1, 2, 3…); colores oro/plata/bronce para el podio |
| `rank-name` | Apellido, Nombre + Categoría (muted sm) |
| `rank-dist` | Distancia RP (accent, 16 px bold) |
| Chip estado | BLANCA / EN REVISIÓN / DQ / DNS |

Atletas en revisión aparecen con opacity 0.7 y sin posición asignada (guión "—").

Mensaje de cierre: "N atletas pendientes de ejecución…" en muted.

#### Columna derecha — Overall Ranking

Estado vacío mientras no estén cerradas todas las disciplinas:
- Ícono 🏆 + texto "Disponible al cerrar todas las disciplinas"

Una vez disponible: misma estructura de `rank-row` usando puntos CMAS o distancia acumulada según reglamento del torneo.

**Invariante:** botón "Publicar resultados" sólo debe estar habilitado cuando todas las disciplinas estén cerradas y no haya amarillas pendientes (en el prototipo es siempre visible por simplicidad).

---

### S-05 — Jueces

**Propósito:** monitoreo del estado de conexión de los jueces y gestión de asignaciones por andarivel.

**Header:** título "Jueces asignados" + botón `+ Agregar juez` (outline sm).

**Subtítulo:** disciplina activa + cantidad de jueces en línea + andariveles.

**Sección "En línea":**

Cada `juez-card` contiene:
- Avatar con iniciales (circle, accent sobre surface2)
- Nombre completo
- Disciplina + andarivel + lista de atletas asignados (posiciones impares/pares)
- Badge de conexión `online` (verde)
- Botón `Reasignar` (ghost sm)

**Sección "Pendientes (disciplinas futuras)":**

Misma estructura con opacity 0.6, avatar en surface2/muted, sin badge online → texto "Sin conexión".

**Invariante:** un juez solo puede estar asignado a un andarivel a la vez. La reasignación no está implementada en el prototipo (muestra `alert()`).

---

### S-06 — Gestión del Torneo

**Propósito:** edición de datos generales del torneo y gestión de disciplinas.

**Layout:** two-column.

#### Columna izquierda — Datos generales

Panel `detail-panel` con formulario:

| Campo | Tipo | Valor mock |
|-------|------|-----------|
| Nombre del torneo | text input | Apnea Indoor Buenos Aires 2026 |
| Fecha | date input | 2026-04-05 |
| Sede | text input | Club Náutico BA |
| Estado | select | En ejecución / Inscripciones abiertas / Finalizado |

Botón `Guardar cambios` (btn-primary).

#### Columna derecha — Disciplinas

Lista de `disc-card-mgmt` por cada disciplina:

| Campo mostrado | Ejemplo |
|---------------|---------|
| Nombre corto | DNF |
| Detalle | 14:00 · 12 atletas · And. A/B · 9 min intervalo |
| Badge estado | ACTIVA (blanca) / PENDIENTE (gris) |

Botón `+ Agregar disciplina` (outline sm) al pie de la lista.

**Invariante:** no se puede editar una disciplina en estado ACTIVA (bloqueado en prototipo con badge visual; implementar validación en API).

---

### S-07 — Audit Log

**Propósito:** trazabilidad completa de eventos del torneo con integridad verificable mediante hash SHA-256.

**Header:** título "Audit Log" + subtítulo "Historial de eventos · Integridad SHA-256".

**Filtros (dropdowns en línea):**
- Disciplina: Todas / DNF / STA / DBF
- Atleta: Todos / lista
- Juez: Todos / lista

**Lista de eventos (`log-item`):**

Cada entrada contiene:
- `log-time`: hora del evento (HH:MM), muted, ancho fijo
- Chip de tipo de evento (reutiliza chips de grilla: AMARILLA, BLANCA, ROJA, etc.)
- Descripción del evento con atleta destacado (`log-actor`, accent bold)
- `log-hash`: `sha256: XXXXXXXX…` + "Juez: Nombre" — monospace, color border

**Eventos registrados en el mock (orden cronológico inverso):**

| Hora | Tipo | Descripción |
|------|------|-------------|
| 14:19 | AMARILLA | Tarjeta amarilla asignada · López, Andrés · DNF #2 · RP 66.0 m |
| 14:17 | RP | Resultado registrado · López, Andrés · 66.0 m |
| 14:09 | OT | Tiempo Oficial marcado · López, Andrés · Andarivel B |
| 14:07 | BLANCA | Tarjeta blanca asignada · García, Martina · DNF #1 · RP 65.0 m |
| 14:05 | RP | Resultado registrado · García, Martina · 65.0 m |
| 14:00 | OT | Tiempo Oficial marcado · García, Martina · Andarivel A |

---

## Diagrama de navegación

```
S-00 Login
  └─► S-01 Dashboard
        ├─► S-02 Grilla ──────────► S-03 Detalle Amarilla ──► S-02
        │     └─► S-07 Audit Log                               │
        ├─► S-03 Detalle Amarilla (desde alerta) ──────────────┘
        ├─► S-04 Resultados
        ├─► S-05 Jueces
        ├─► S-06 Torneo
        └─► S-07 Audit Log

Navbar siempre visible → acceso directo a cualquier sección desde cualquier pantalla
```

---

## Componentes React identificados

| Componente | Props clave | Pantallas |
|-----------|------------|-----------|
| `NavBar` | `activeSection`, `user`, `connectionStatus` | todas (S-01 → S-07) |
| `KpiCard` | `label`, `value`, `sub`, `color` | S-01 |
| `DisciplinaStatus` | `disciplina`, `completados`, `total`, `estado` | S-01 |
| `AlertaCard` | `tipo`, `atleta`, `disciplina`, `ot`, `rp`, `onResolve` | S-01 |
| `GrillaTable` | `atletas[]`, `filtro`, `onResolve`, `onViewLog` | S-02 |
| `GrillaRow` | `atleta`, `estado`, `onAction` | S-02 |
| `DetalleAmarilla` | `performance`, `onConfirmarBlanca`, `onConfirmarRoja` | S-03 |
| `RankRow` | `pos`, `nombre`, `categoria`, `distancia`, `estado` | S-04 |
| `JuezCard` | `juez`, `disciplina`, `andarivel`, `online` | S-05 |
| `DiscCard` | `disciplina`, `estado`, `readonly` | S-01, S-06 |
| `LogItem` | `hora`, `tipo`, `descripcion`, `actor`, `hash` | S-07 |
| `ConnectionBadge` | `status` | todas |

---

## Invariantes de negocio formalizados

| ID | Regla | Fuente |
|----|-------|--------|
| INV-ORG-01 | Solo una disciplina puede estar en estado ACTIVA simultáneamente | Diseño dominio |
| INV-ORG-02 | No se puede cerrar una disciplina con amarillas pendientes de resolución | Diseño dominio |
| INV-ORG-03 | La resolución de amarilla tiene máximo 3 min de deliberación | CMAS 1.2.3.1 |
| INV-ORG-04 | Penalización general DNF = −3 m sobre RP medido | CMAS 1.1.13.1 |
| INV-ORG-05 | El Overall Ranking solo se publica al cerrar todas las disciplinas | Diseño dominio |
| INV-ORG-06 | Todo evento queda registrado con SHA-256 en el audit log | ADR-005, Event Sourcing |
| INV-ORG-07 | El orden de la grilla es por OT ascendente; no admite reordenamiento manual | Diseño dominio |
| INV-ORG-08 | Una disciplina ACTIVA no es editable desde S-06 | Diseño dominio |

---

*Artefacto generado: 2026-04-05 — INC-4.0 UX Design*
*Capa IEDD: 3b — Especificación interactiva*
