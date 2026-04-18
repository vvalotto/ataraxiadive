# Wireframes — Setup del Torneo

> Artefacto INC-4.0 · Especificación formal derivada de `prototipo-setup-torneo.html` validado
> Fuente funcional: configuración del torneo antes de operación en vivo
> Última actualización: 2026-04-08

---

## Principios de diseño

| Principio | Valor |
|-----------|-------|
| Tema | Dark (fondo #0f172a) |
| Ancho máximo de contenido | 1100 px |
| Altura de topbar | 56 px sticky |
| Fuente | System UI (-apple-system, BlinkMacSystemFont) |
| Contexto | Organizador en desktop/tablet durante preparación del torneo |

**Tokens de color**:

| Token | Valor | Uso |
|-------|-------|-----|
| `--bg` | `#0f172a` | Fondo general |
| `--surface` | `#1e293b` | Panels, cards, tablas |
| `--surface2` | `#334155` | Inputs, estados neutros |
| `--border` | `#475569` | Bordes generales |
| `--accent` | `#38bdf8` | Acción principal, estado abierto |
| `--blanca` | `#22c55e` | Estado listo/completo |
| `--amarilla` | `#eab308` | Pendientes y advertencias |
| `--roja` | `#ef4444` | Fallo crítico o acción destructiva |
| `--muted` | `#94a3b8` | Texto secundario |

---

## Flujo general

Este artefacto modela el setup previo a la publicación/ejecución:

```text
Datos del torneo
  → Disciplinas
    → Configuración por disciplina
      → Revisión de inscriptos
        → Generación de grilla
          → Asignación de jueces
            → Torneo listo/publicado
```

**Regla central:** no se puede publicar un torneo hasta que cada disciplina tenga parámetros, grilla y jueces asignados.

---

## Pantallas

### S-00 — Login

**Propósito:** autenticación del organizador antes del setup.

**Componentes:**
- logo "AtaraxiaDive"
- subtítulo "Panel de Organización"
- campo `Email`
- campo `Contraseña`
- botón `INGRESAR`
- label `Rol activo: Organizador`

**Acción:** `INGRESAR` → S-01 Mis torneos

---

### S-01 — Mis torneos

**Propósito:** entry point para torneos en ejecución, preparación o finalizados.

**Topbar:** marca + usuario + botón `+ Nuevo torneo`.

**Secciones:**
- `En ejecución`
- `En preparación`
- `Finalizados`

#### Torneo card

Cada `torneo-card` muestra:
- icono contextual
- nombre del torneo
- fecha + sede + cantidad de disciplinas/atletas
- badge de estado
- CTA textual

**Estados mockeados:**

| Estado | Badge | CTA |
|--------|-------|-----|
| En ejecución | `EN EJECUCIÓN` | `Ir al panel →` |
| En preparación | `INSCRIPCIONES ABIERTAS` | `Configurar →` |
| Finalizado | `FINALIZADO` | `Ver resultados →` |

**Acciones:**
- `+ Nuevo torneo` → S-02 Crear torneo
- tap torneo en preparación → S-03 Preparación

---

### S-02 — Crear torneo

**Propósito:** registrar los datos marco del torneo.

**Topbar:** `← Mis torneos` + "Nuevo torneo".

**Stepper:** 3 pasos:
- `1 Datos del torneo`
- `2 Disciplinas`
- `3 Por disciplina`

**Panels:**
- `Identificación del torneo`
- `Estado de inscripciones`

#### Identificación del torneo

Campos:
- nombre del torneo
- fecha de inicio
- fecha de fin
- sede
- ciudad
- reglamento

#### Estado de inscripciones

Campo:
- select `Estado inicial`

Opciones mockeadas:
- `Borrador (no visible para atletas)`
- `Inscripciones abiertas`

**Acciones:**
- `Cancelar` → S-01 Mis torneos
- `Continuar — Disciplinas →` → S-04 Lista de disciplinas

---

### S-03 — Preparación del torneo

**Propósito:** vista de checklist global y control de readiness del torneo.

**Topbar:** `← Mis torneos` + nombre torneo + badge `INSCRIPCIONES ABIERTAS`.

**Layout:** dos columnas.

#### Columna izquierda

Elementos:
- bloque `Torneo` con check de datos básicos
- checklist por disciplina (`disc-steps`)

Cada disciplina expone 4 hitos:
- parámetros
- inscriptos
- grilla
- jueces

**Estados soportados:**

| Estado | Ícono | Significado |
|--------|-------|-------------|
| completo | `✅` | hito resuelto |
| pendiente advertencia | `⚠️` | requiere atención |
| vacío | `⚪` | no generado |
| bloqueado | `🔒` | depende de otro paso |

#### Columna derecha

Elementos:
- panel `Estado general`
- `info-box` amarilla con cuello de botella
- botón `Publicar torneo`
- helper explicando por qué está deshabilitado
- CTA `+ Agregar disciplina`

#### Métricas mockeadas

| Métrica | Valor |
|---------|-------|
| Disciplinas | 2 |
| Atletas inscriptos | 8 |
| Grillas generadas | 1 de 2 |
| Disciplinas con jueces | 1 de 2 |

**Acciones:**
- `Editar` datos básicos → S-02
- `Editar` parámetros → S-05
- `Ver` inscriptos → S-06
- `Generar/Ver` grilla → S-07
- `Ver` jueces → S-08
- `+ Agregar disciplina` → S-04

**Regla UX:** `Publicar torneo` permanece disabled hasta que todas las disciplinas completen grilla y asignación de jueces.

---

### S-04 — Lista de disciplinas

**Propósito:** administrar el conjunto de disciplinas del torneo.

**Topbar:** `← Preparación` + título "Disciplinas".

**Componentes:**
- título de página + botón `+ Agregar disciplina`
- cards de disciplina
- card dashed de alta rápida

#### Card de disciplina

Muestra:
- ícono
- nombre largo
- fecha + hora + andariveles + intervalo + inscriptos
- chip de estado
- botón `Editar`

**Estados mockeados:**
- `Grilla pendiente`
- `Completa ✓`

**Acciones:**
- tap card o `Editar` → S-05 Configurar disciplina
- `+ Agregar disciplina` → S-05

---

### S-05 — Configurar disciplina

**Propósito:** definir los parámetros operativos de una disciplina.

**Topbar:** `← Disciplinas` + título "Configurar disciplina".

**Panels:**
- `Tipo, fecha y horario`
- `Andariveles habilitados`
- `Categorías habilitadas`
- `Criterio de ordenamiento de grilla`

#### Tipo, fecha y horario

Campos:
- tipo de disciplina
- fecha de competencia
- hora de inicio
- intervalo entre atletas

#### Andariveles habilitados

Checklist de calles A/B/C/D.

#### Categorías habilitadas

Checklist de categorías:
- Senior M/F
- Junior M/F
- Master M/F

#### Criterio de ordenamiento

Opciones mockeadas:
- `AP ascendente — menor distancia sale primero (CMAS default)`
- `AP descendente`
- `Orden de inscripción`

**Acciones:**
- `Cancelar` → S-04
- `Guardar disciplina` → S-04

**Invariante:** la disciplina debe tener al menos un andarivel y una categoría habilitada.

---

### S-06 — Inscriptos (solo lectura + corrección)

**Propósito:** revisar atletas de una disciplina y corregir datos previos a la grilla.

**Topbar:** `← Preparación` + "Inscriptos — [DISCIPLINA]".

**Componentes:**
- título + subtítulo
- info-box de alcance
- tabla de inscriptos
- advertencia por AP faltante
- botones `Volver` y `Guardar correcciones`

#### Tabla

Columnas:
- `#`
- atleta
- categoría
- club
- AP declarado
- estado

**Comportamiento permitido:**
- editar AP inline
- revisar categoría
- no alta ni baja de atletas desde esta vista

**Estados de fila:**
- `✓ Con AP`
- `⚠ Sin AP`

**Acciones:**
- `Guardar correcciones` → S-03 Preparación

**Regla de negocio visible:** el organizador corrige datos incorrectos, pero no reemplaza el flujo de inscripción del atleta.

---

### S-07 — Preview y confirmar grilla

**Propósito:** validar el orden de salida antes de fijarlo.

**Topbar:** `← Preparación` + "Generar grilla — [DISCIPLINA]".

**Header visual:** `grilla-ok` con resumen de cálculo.

**Layout:** dos columnas.

#### Columna izquierda — Grilla calculada

Tabla con columnas:
- posición
- atleta
- OT
- andarivel
- AP

Pie informativo:
- criterio `AP asc`
- alternancia de andariveles

#### Columna derecha — Validaciones

Checklist de validaciones:
- atletas con OT y andarivel
- ausencia de solapamiento
- alternancia balanceada
- advertencia por atleta sin AP

**Acciones:**
- `← Volver` → S-03
- `↓ PDF` → exportación
- `Confirmar grilla — Asignar jueces →` → S-08

**Regla importante:** el mock permite confirmar una grilla aun con atletas sin AP declarado.

---

### S-08 — Asignar jueces por competidor

**Propósito:** vincular un juez a cada fila de la grilla ya confirmada.

**Topbar:** `← Grilla` + "Asignar jueces — [DISCIPLINA]".

**Layout:** dos columnas.

#### Columna izquierda — Grilla con selector de juez

Tabla con columnas:
- `#`
- atleta
- OT
- andarivel
- juez

El campo `juez-select` soporta:
- `— Sin asignar —`
- lista de jueces disponibles

**Estados visuales:**

| Estado | Clase |
|--------|-------|
| asignado | `asignado` |
| pendiente | `pendiente` |

CTA secundaria:
- `Completar filas pendientes con…`

#### Columna derecha — Jueces disponibles

Lista de tarjetas-resumen con:
- avatar/iniciales
- nombre
- licencia
- chip con filas cubiertas

Más:
- alerta por fila sin juez
- caja explicativa de rotación

**Acciones:**
- cambio en select actualiza estado visual
- `Confirmar asignación →` → S-09 Torneo publicado
- `← Grilla` → S-07

**Regla UX:** el mismo juez puede aparecer en varias filas según rotación acordada.

---

### S-09 — Torneo publicado

**Propósito:** estado final de setup exitoso.

**Topbar:** marca + usuario.

**Componentes:**
- icono celebración
- título "¡Torneo publicado!"
- subtítulo con impacto
- tres KPI cards
- botón `Ir al panel de organización →`
- botón `← Volver a mis torneos`

#### KPI mockeados

| KPI | Valor |
|-----|-------|
| Atletas | 8 |
| Disciplinas | 2 |
| Jueces | 3 |

**Acciones:**
- `Ir al panel de organización →` → panel operativo
- `← Volver a mis torneos` → S-01

---

## Diagrama de navegación

```text
S-00 Login
  └─► S-01 Mis torneos
        ├─► S-02 Crear torneo
        │     └─► S-04 Lista de disciplinas
        ├─► S-03 Preparación del torneo
        │     ├─► S-02 Crear torneo
        │     ├─► S-05 Configurar disciplina
        │     ├─► S-06 Inscriptos
        │     ├─► S-07 Preview grilla
        │     │     └─► S-08 Asignar jueces
        │     │           └─► S-09 Torneo publicado
        │     └─► S-04 Lista de disciplinas
        └─► Panel en vivo / resultados
```

---

## Componentes React identificados

| Componente | Props clave | Pantallas |
|-----------|-------------|-----------|
| `OrganizerTopbar` | `title`, `user`, `backAction` | S-01 a S-09 |
| `TournamentCard` | `torneo`, `estado`, `actionLabel`, `onOpen` | S-01 |
| `SetupStepper` | `currentStep`, `steps[]` | S-02 |
| `SetupPanel` | `title`, `children` | S-02, S-05, S-07, S-08 |
| `PreparationChecklist` | `disciplina`, `steps[]` | S-03 |
| `StatusMetricPanel` | `metrics[]`, `blockingMessage` | S-03 |
| `DisciplinaCard` | `disciplina`, `status`, `onEdit` | S-04 |
| `CheckboxChipGroup` | `options`, `selected`, `onToggle` | S-05 |
| `EditableAthletesTable` | `rows`, `onApChange` | S-06 |
| `GridPreviewTable` | `rows`, `sortRule`, `lanes` | S-07 |
| `ValidationList` | `items[]` | S-07 |
| `JudgeAssignmentTable` | `rows`, `judges`, `onAssign` | S-08 |
| `JudgeAvailabilityCard` | `judge`, `assignedRows` | S-08 |
| `PublishSuccessPanel` | `torneo`, `metrics`, `onOpenDashboard` | S-09 |

---

## Invariantes de negocio formalizados

| ID | Regla | Fuente |
|----|-------|--------|
| INV-ST-01 | Un torneo no se publica hasta que todas las disciplinas tengan grilla y jueces asignados | Prototipo S-03 |
| INV-ST-02 | La asignación de jueces se habilita recién después de confirmar la grilla | Prototipo S-03/S-08 |
| INV-ST-03 | El organizador puede corregir AP/categoría antes de generar grilla, pero no dar de alta/baja atletas en esa vista | Prototipo S-06 |
| INV-ST-04 | La grilla debe validar OT sin solapamiento y distribución por andariveles | Prototipo S-07 |
| INV-ST-05 | El criterio por defecto de ordenamiento es AP ascendente según CMAS | Prototipo S-05/S-07 |
| INV-ST-06 | Puede confirmarse una grilla con atletas sin AP declarado, manteniendo la advertencia visible | Prototipo S-07 |
| INV-ST-07 | Un mismo juez puede cubrir múltiples filas según la rotación acordada | Prototipo S-08 |
| INV-ST-08 | El estado inicial del torneo puede ser borrador o inscripciones abiertas | Prototipo S-02 |

---

*Artefacto generado: 2026-04-08 — INC-4.0 UX Design*
*Capa IEDD: 3b — Especificación interactiva*
