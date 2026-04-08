# Wireframes — Portal del Atleta

> Artefacto INC-4.0 · Especificación formal derivada de `prototipo-atleta.html` validado
> Fuente reglamentaria: CMAS Apnea Indoor v2022/01 (FAAS)
> Última actualización: 2026-04-08

---

## Principios de diseño

| Principio | Valor |
|-----------|-------|
| Tema | Dark (fondo #0f172a) |
| Ancho máximo | 430 px (mobile-first) |
| Altura de header | 52 px sticky |
| Altura de tab bar | 56 px sticky |
| Fuente | System UI (-apple-system, BlinkMacSystemFont) |
| Contexto de uso | Pre-competencia y consulta post-competencia desde smartphone |

**Tokens de color** (compartidos con juez y organizador):

| Token | Valor | Uso |
|-------|-------|-----|
| `--bg` | `#0f172a` | Fondo general |
| `--surface` | `#1e293b` | Cards, headers, tab bar |
| `--surface2` | `#334155` | Inputs, chips neutrales, botones ghost |
| `--border` | `#475569` | Bordes generales |
| `--accent` | `#38bdf8` | Acción principal, OT, links |
| `--blanca` | `#22c55e` | Estado válido, confirmaciones |
| `--amarilla` | `#eab308` | Alertas, AP pendiente, deadlines |
| `--roja` | `#ef4444` | Error, rechazo, cancelación crítica |
| `--muted` | `#94a3b8` | Texto secundario |

---

## Navegación base

La experiencia del atleta usa shell móvil con:

- `header` superior sticky
- `scroll` central
- `tabbar` inferior sticky con 4 tabs

**Tabs persistentes:**

```
[🏠 Inicio] [🏆 Torneos] [📋 Mis inscr.] [📊 Resultados]
```

| Tab | Destino |
|-----|---------|
| Inicio | S-01 Portal |
| Torneos | S-02 Torneos |
| Mis inscr. | S-05 Mis inscripciones |
| Resultados | S-08 Mis resultados |

**Regla de navegación:** las pantallas de detalle usan flecha `←` para volver, pero conservan la tab bar para salto directo.

---

## Pantallas

### S-00 — Login

**Propósito:** autenticación del atleta.

**Layout:** caja centrada de 360 px máximo.

**Componentes:**
- Logo "AtaraxiaDive" (accent, 26 px, 900)
- Subtítulo "Portal del Atleta"
- Campo Email
- Campo Contraseña
- Botón `INGRESAR` (btn-primary, ancho completo, 44 px)
- Label "Rol activo: Atleta"
- Link secundario `Registrate`

**Acción:**
- `INGRESAR` → S-01 Portal

---

### S-01 — Portal / Dashboard

**Propósito:** home resumida del atleta con próximo OT y accesos a sus torneos activos.

**Componentes:**
- Header simple con marca + nombre abreviado del atleta
- `hero-card` con saludo, categoría y club
- Card "Tu próximo OT"
- Sección "Mis inscripciones activas"
- CTA `Explorar torneos disponibles`

#### Card "Tu próximo OT"

Contenido:
- torneo + disciplina
- badge `HOY`
- hora OT en tipografía destacada
- andarivel + posición + AP declarado
- link "Ver grilla completa →"

**Acción:** tap card → S-07 Mi grilla

#### Sección "Mis inscripciones activas"

Cada card muestra:
- nombre del torneo
- fecha + sede
- badge de estado
- chips por disciplina

**Estados mockeados:**

| Torneo | Estado | Chips |
|--------|--------|-------|
| Copa Litoral 2026 | `EN EJECUCIÓN` | `DNF ✓ AP`, `STA ✓ AP` |
| Open Litoral 2026 | `INSCRIPCIONES` | `DNF ⚠ Sin AP` |

**Acciones:**
- Tap card → S-05 Mis inscripciones
- `Explorar torneos disponibles` → S-02 Torneos

---

### S-02 — Torneos Disponibles

**Propósito:** discovery de torneos publicados y visualización de estado de inscripción.

**Header:** `←` + título "Torneos".

**Secciones:**
- `Inscripciones abiertas`
- `Próximos (inscripciones no abiertas)`

#### Torneo abierto (`torneo-card`)

Muestra:
- nombre
- badge `ABIERTO`
- fecha + sede
- resumen de disciplinas
- deadline de cierre
- link "Ver detalle →"

**Acción:** tap → S-03 Detalle del torneo

#### Torneo próximo

Muestra:
- nombre
- badge neutro `PRÓXIMO`
- fecha por confirmar

**Regla UX:** cards futuras aparecen con menor prominencia visual y sin CTA.

---

### S-03 — Detalle del Torneo

**Propósito:** informar condiciones del torneo antes de iniciar la inscripción.

**Header:** `←` + nombre del torneo.

**Componentes:**
- Card resumen del torneo
- Sección "Disciplinas disponibles"
- Botón `Inscribirme en este torneo`

#### Card resumen

Campos visibles:
- nombre
- fecha
- sede + ciudad
- badge `ABIERTO`
- reglamento aplicable
- fecha de cierre de inscripciones

#### Lista de disciplinas

Cada `disc-row` muestra:
- ícono de disciplina
- nombre largo
- fecha + hora + andariveles + intervalo
- categorías habilitadas

**Acción principal:**
- `Inscribirme en este torneo` → S-04 Inscribirme

---

### S-04 — Inscribirme (wizard de 3 pasos)

**Propósito:** registrar participación del atleta en un torneo y adjuntar requisitos obligatorios.

**Header:** `←` + título "Inscribirme".

**Indicador:** `step-bar` de 3 pasos:
- `1 Personales`
- `2 Competencia`
- `3 Requisitos`

#### Paso 1 — Datos Personales

**Objetivo:** verificar y completar información civil del atleta.

**Componentes:**
- Caja informativa: datos pre-cargados desde el perfil
- Campo `Correo` readonly
- Campo `Nombre y Apellido *`
- Campo `Fecha de Nacimiento *`
- Grupo radio `Género *`
- Campo compuesto `Documento (Tipo + Número) *`
- Campo `Teléfono *`
- Botón `Siguiente →`

**Acción:** `Siguiente →` activa paso 2

#### Paso 2 — Datos de la Competencia

**Objetivo:** definir disciplinas y categoría competitiva.

**Componentes:**
- Label contextual con torneo y fechas
- Selector múltiple de disciplinas (`toggleDiscInsc`)
- Caja informativa de categoría calculada por fecha de nacimiento
- Grupo radio `Categoría *`
- Campo `Nº Brevet FAAS` opcional
- Botones `← Anterior` y `Siguiente →`

**Disciplinas mockeadas:**
- DNF
- STA
- DYNB

**Regla UX:** la selección de disciplina se comporta como checklist visual dentro de `radio-item`.

#### Paso 3 — Requisitos

**Objetivo:** adjuntar documentación antes de enviar la inscripción.

**Componentes:**
- Aviso reglamentario: inscripción queda `pendiente de verificación`
- Bloque `Certificado Médico *`
- Bloque `Comprobante de Pago *`
- Botones `← Anterior`, `Enviar inscripción`, `Cancelar`

**Certificado médico:**
- texto explicativo
- `upload-area`
- helper de formatos y peso máximo

**Comprobante de pago:**
- datos de transferencia
- pricing por fecha con dos tramos
- `upload-area`
- helper de formatos y peso máximo

**Acciones:**
- `Enviar inscripción` → S-05 Mis inscripciones
- `Cancelar` → S-03 Detalle del torneo

**Invariante:** ambos archivos son obligatorios para completar la inscripción.

---

### S-05 — Mis Inscripciones

**Propósito:** concentrar el estado de participación del atleta por torneo y disciplina.

**Header:** `←` + título "Mis inscripciones".

**Secciones del mock:**
- `En ejecución`
- `Inscripciones abiertas`

#### Torneo en ejecución

Cada fila `insc-estado` muestra:
- disciplina
- AP
- OT
- andarivel
- chip `AP cerrado`
- botón `Ver grilla`

**Acción:** `Ver grilla` → S-07 Mi grilla

#### Torneo con inscripciones abiertas

La fila muestra:
- disciplina
- estado `⚠ Sin AP declarado`
- chip `AP pendiente`
- botón `Declarar AP`

Debajo del listado:
- `deadline` con fecha y hora de cierre de anuncios

**Acción:** `Declarar AP` → S-06 Declarar AP

**Regla de negocio visible:** una vez cerrado el período de anuncios, el atleta solo visualiza `AP cerrado`.

---

### S-06 — Declarar / Modificar AP

**Propósito:** cargar o editar la `Announced Performance` antes del cierre.

**Header:** `←` + título "Declarar AP".

**Componentes:**
- Caja informativa explicando el concepto de AP
- Card de contexto con torneo, disciplina y horario
- Campo destacado `AP — Distancia anunciada *`
- `deadline` de cierre de anuncios
- Botón `Guardar AP`
- Botón `Cancelar`

**Campo principal:**
- input grande centrado
- unidad `metros`
- color accent

**Acciones:**
- `Guardar AP` → S-05 Mis inscripciones
- `Cancelar` → S-05 Mis inscripciones

**Restricción:** el AP se expresa en metros para disciplinas dinámicas; el comportamiento para estática requiere un input de tiempo en implementación real.

---

### S-07 — Mi Grilla

**Propósito:** mostrar OT, posición y orden completo de salida en la disciplina.

**Header:** `←` + título "Mi grilla — [DISCIPLINA]".

**Componentes:**
- `ot-hero` con horario oficial destacado
- chips de AP y estado
- caja informativa con ventana OT+30s
- lista completa `grilla-row`
- botón `Ver mis resultados →`

#### Hero OT

Campos:
- label "Tu Tiempo Oficial"
- hora OT en 52 px
- andarivel + posición + torneo
- chips `AP: ...` y estado actual

#### Lista de grilla

Cada fila muestra:
- posición
- nombre atleta
- marca `TÚ` cuando corresponde
- OT + andarivel
- opcionalmente chip de resultado si ya compitió

**Estados observados:**

| Estado de fila | Estilo |
|----------------|--------|
| `done` | opacidad reducida |
| `yo` | fondo accent tenue + borde izquierdo accent |
| normal | pendiente futura |

**Acciones:**
- `Ver mis resultados →` → S-08 Mis resultados

**Nota de consistencia:** el mock incluye una fila histórica "ya competiste" y luego la grilla activa; en implementación debería resolverse como un único estado consistente según fase del torneo.

---

### S-08 — Mis Resultados

**Propósito:** exponer resultados publicados por disciplina y ranking parcial.

**Header:** `←` + título "Mis resultados".

**Secciones del mock:**
- torneo activo
- resultado publicado por disciplina
- ranking por disciplina
- disciplinas pendientes
- ranking general

#### Resultado publicado (`result-hero`)

Muestra:
- tipo de tarjeta
- disciplina
- distancia principal
- AP declarado
- diferencia contra AP
- chip de validez

**Estados visuales soportados por componente:**

| Estado | Clase |
|--------|-------|
| Blanca | `result-hero blanca` |
| Amarilla | `result-hero amarilla` |
| Roja | `result-hero roja` |

#### Ranking de disciplina

Card con:
- header de ranking
- filas `rank-row`
- distinción visual para top 3
- resalte del atleta actual (`yo`)
- pie "Ranking parcial"

#### Resultado pendiente

Card de disciplina futura con:
- OT
- AP
- andarivel
- chip `Pendiente`
- caja informativa de disponibilidad posterior

#### Ranking general (Overall)

Estado vacío:
- ícono trofeo
- texto "Disponible al finalizar todas las disciplinas del torneo"

**Regla de negocio visible:** el overall no aparece hasta cerrar el torneo o hasta que existan resultados suficientes para publicarlo.

---

## Diagrama de navegación

```text
S-00 Login
  └─► S-01 Portal
        ├─► S-02 Torneos
        │     └─► S-03 Detalle del torneo
        │           └─► S-04 Inscribirme
        │                 └─► S-05 Mis inscripciones
        ├─► S-05 Mis inscripciones
        │     ├─► S-06 Declarar AP
        │     └─► S-07 Mi grilla
        ├─► S-07 Mi grilla
        │     └─► S-08 Mis resultados
        └─► S-08 Mis resultados

Tab bar persistente en S-01, S-02, S-05, S-07 y S-08
```

---

## Componentes React identificados

| Componente | Props clave | Pantallas |
|-----------|-------------|-----------|
| `AthleteShell` | `title`, `showBack`, `activeTab` | S-01 a S-08 |
| `BottomTabBar` | `activeTab` | S-01, S-02, S-05, S-07, S-08 |
| `HeroCard` | `name`, `categoria`, `club` | S-01 |
| `TorneoCard` | `torneo`, `estado`, `disciplinas`, `onOpen` | S-01, S-02 |
| `DisciplinaRow` | `disciplina`, `horario`, `categorias` | S-03 |
| `InscripcionStepper` | `currentStep` | S-04 |
| `DisciplinaToggleCard` | `selected`, `disciplina`, `onToggle` | S-04 |
| `UploadArea` | `label`, `acceptedFormats`, `uploadedFile` | S-04 |
| `InscripcionEstadoRow` | `disciplina`, `ap`, `ot`, `status`, `action` | S-05 |
| `DeadlineBanner` | `label`, `deadline` | S-05, S-06 |
| `ApInputCard` | `disciplina`, `unidad`, `value`, `onChange` | S-06 |
| `OtHero` | `ot`, `andarivel`, `posicion`, `ap`, `estado` | S-07 |
| `GrillaRow` | `pos`, `nombre`, `ot`, `andarivel`, `isSelf`, `estado` | S-07 |
| `ResultHero` | `tarjeta`, `disciplina`, `valor`, `ap`, `diferencia` | S-08 |
| `RankingRow` | `pos`, `nombre`, `marca`, `estado`, `isSelf` | S-08 |

---

## Invariantes de negocio formalizados

| ID | Regla | Fuente |
|----|-------|--------|
| INV-ATL-01 | El atleta solo puede declarar o modificar AP antes del cierre de anuncios | Flujo de atleta |
| INV-ATL-02 | Una inscripción enviada con requisitos pendientes queda en estado de verificación | Prototipo S-04 |
| INV-ATL-03 | El OT y la posición de grilla son de solo lectura para el atleta | Dominio competencia |
| INV-ATL-04 | La grilla se ordena por OT ascendente y resalta al atleta actual | Dominio competencia |
| INV-ATL-05 | Los resultados se muestran una vez publicados por organización | Flujo de atleta |
| INV-ATL-06 | El ranking overall permanece oculto o vacío hasta finalizar las disciplinas relevantes | Prototipo S-08 |
| INV-ATL-07 | La categoría competitiva se deriva de la fecha de nacimiento y debe poder revisarse antes del envío | Prototipo S-04 |
| INV-ATL-08 | Certificado médico y comprobante de pago son obligatorios para completar la inscripción | Prototipo S-04 |

---

*Artefacto generado: 2026-04-08 — INC-4.0 UX Design*
*Capa IEDD: 3b — Especificación interactiva*
