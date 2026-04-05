# Wireframes — Interfaz del Juez

> Artefacto INC-4.0 · Especificación formal derivada de `prototipo-juez.html` validado
> Fuente reglamentaria: CMAS Apnea Indoor v2022/01 (FAAS)
> Última actualización: 2026-04-05

---

## Principios de diseño

| Principio | Valor |
|-----------|-------|
| Tema | Dark (fondo #0f172a) |
| Ancho máximo | 390 px (mobile-first) |
| Altura mínima de botón | 58 px |
| Fuente | System UI (-apple-system, BlinkMacSystemFont) |
| Contraste | Alto — operable bajo luz solar directa y manos mojadas |
| Toque máximo por performance | 6 acciones principales |

**Tokens de color:**

| Token | Valor | Uso |
|-------|-------|-----|
| `--bg` | `#0f172a` | Fondo general |
| `--surface` | `#1e293b` | Cards, headers |
| `--surface2` | `#334155` | Botones secundarios, inputs |
| `--accent` | `#38bdf8` | Acción principal, OT |
| `--blanca` | `#22c55e` | Tarjeta blanca, ATLETA INICIA |
| `--amarilla` | `#eab308` | Tarjeta amarilla, alerta |
| `--roja` | `#ef4444` | Tarjeta roja, DQ, BKO |
| `--dns` | `#64748b` | DNS |
| `--muted` | `#94a3b8` | Texto secundario |

---

## Pantallas

### S-00 — Login

**Propósito:** autenticación del juez.

**Componentes:**
- Logo "AtaraxiaDive" (accent, 32 px, bold)
- Campo Email (pre-llenado en prototipo)
- Campo Contraseña
- Botón `INGRESAR` (btn-primary, ancho completo)
- Label "Rol activo: Juez"

**Acción:**
- `INGRESAR` → S-01 Mis Disciplinas

---

### S-01 — Mis Disciplinas

**Propósito:** selección de la disciplina a juzgar.

**Componentes:**
- Header: nombre del juez + nombre del torneo
- Badge conexión (online/offline)
- Lista de disciplinas asignadas (`disc-card`)
- Card torneo (nombre, fecha, sede)
- Botón `Cerrar sesión`

**Estados de disc-card:**

| Estado | Badge | Acción al tap |
|--------|-------|---------------|
| ACTIVA | verde | → S-02 Grilla |
| PENDIENTE | gris | deshabilitado |

---

### S-02 — Grilla de Salida

**Propósito:** vista general de todos los atletas de la disciplina, ordenada por OT ascendente.

**Componentes:**
- Header: nombre disciplina + estado (EN EJECUCIÓN)
- Botón `← Disciplinas`
- Label: cantidad de atletas + intervalo
- Badge conexión
- Lista `grilla-row` ordenada por OT

**Estados de grilla-row:**

| Estado | Estilo | Tappable | Destino |
|--------|--------|----------|---------|
| ✓ BLANCA | opacidad 45% | No | — |
| ✓ ROJA | opacidad 45% | No | — |
| DNS | opacidad 55% | No | — |
| ⚠ REVISIÓN | borde amarillo | Sí | S-15 Revisión |
| ▶ SIGUIENTE | borde accent, fondo accent/6% | Sí | S-03 Paso 1 |
| PENDIENTE | normal | Sí | S-03 Paso 1 |

**Invariante:** ningún atleta PENDIENTE puede tener OT anterior al último atleta ejecutado.

**Datos por fila:**
- Posición (#)
- Apellido, Nombre
- OT + Andarivel
- AP (metros, color accent)
- Badge de estado

---

### S-03 — Paso 1: Llamar Atleta

**Propósito:** el juez anuncia al atleta que debe dirigirse a la zona de inicio.

**Componentes:**
- Indicador de pasos (6 puntos, punto 1 activo)
- Card atleta: nombre, AP, posición, andarivel, OT
- Label "Paso 1 de 6"
- Botón `📢 LLAMAR ATLETA` (btn-primary)
- Botón `DNS — No se presenta` (btn-dns)

**Acciones:**
- `LLAMAR ATLETA` → S-04 Paso 2
- `DNS` → S-13 DNS

---

### S-04 — Paso 2: Confirmar Presencia

**Propósito:** verificar que el atleta llegó al andarivel.

**Componentes:**
- Indicador pasos (paso 2 activo, paso 1 completado)
- Card atleta
- Texto "¿El atleta se presenta en el andarivel?"
- Label "Paso 2 de 6"
- Botón `✓ PRESENTE` (btn-primary)
- Botón `DNS — No se presenta` (btn-dns)

**Acciones:**
- `PRESENTE` → S-05 Paso 3
- `DNS` → S-13 DNS

---

### S-05 — Paso 3: Tiempo Oficial

**Propósito:** gestionar la ventana de inicio OT±30s conforme CMAS 1.2.1.8.

**Componentes:**
- Indicador pasos (paso 3 activo)
- Card atleta
- Panel OT: horario programado (ej: 14:00:00), label estado
- Botón `⏱ TIEMPO OFICIAL` (btn-primary, 66 px altura) — **Estado A**
- Panel ventana activa (oculto en Estado A, visible en Estado B):
  - Label "⏱ Ventana activa — el atleta puede sumergirse"
  - Countdown numérico grande (30→0)
  - Colores: verde 30s–11s · amarillo 10s–6s · rojo 5s–1s
- Botón `▶ ATLETA INICIA` (btn-blanca/verde, oculto en Estado A) — **Estado B**
- Panel DQ (oculto hasta que countdown = 0):
  - Alerta roja "Ventana de +30s vencida"
  - Botón `REGISTRAR DQ — No inició en ventana` (btn-roja)

**Estados:**

| Estado | Trigger | Visible |
|--------|---------|---------|
| A — Esperando OT | entrada a la pantalla | Botón TIEMPO OFICIAL |
| B — Ventana activa | tap TIEMPO OFICIAL | Panel ventana + countdown + ATLETA INICIA |
| C — Vencida | countdown = 0 | Botón ATLETA INICIA deshabilitado + panel DQ |

**Acciones:**
- `TIEMPO OFICIAL` → arranca countdown 30s (Estado A → B)
- `ATLETA INICIA` → para countdown → S-06 Paso 4 + inicia cronómetro de performance
- `REGISTRAR DQ` → S-11 Resultado Roja

**Regla CMAS:** el atleta puede iniciar desde OT hasta OT+30s. Antes del OT → DQ (salida en falso). Después de OT+30s → DQ (no inició en ventana).

---

### S-06 — Paso 4: Performance en Curso

**Propósito:** monitorear la performance activa.

**Componentes:**
- Header: "DNF — EN CURSO" + nombre atleta
- Badge conexión
- Indicador pasos (paso 4 activo)
- Cronómetro activo (MM:SS, color verde, fuente 52 px)
- Card atleta: nombre, AP, andarivel
- Label "Paso 4 de 6"
- Botón `⏹ FINALIZAR PERFORMANCE` (btn-primary)
- Botón `⚡ BKO — Black-out` (btn-roja, 52 px altura)

**Acciones:**
- `FINALIZAR PERFORMANCE` → para cronómetro → S-07 Paso 5
- `BKO` → para cronómetro → S-12 BKO

---

### S-07 — Paso 5: Registrar RP

**Propósito:** ingresar la distancia realizada por el atleta con precisión de 1 cm (CMAS 2.1.4.1).

**Componentes:**
- Indicador pasos (paso 5 activo)
- Card atleta: nombre, AP
- Display RP: `[metros] m · [cm] cm`
  - Metros: fuente 58 px, color accent
  - Separador `·`
  - Centímetros: fuente 44 px, color muted si vacío / texto si ingresado
- Sección Metros:
  - Label "Metros — selección rápida"
  - Presets: `25 | 50 | 75 | 100 | 125` (54 px altura)
  - Ajuste: `−1 | +1 | +5 | +10` (52 px altura)
- Sección Centímetros:
  - Label "Centímetros"
  - Numpad 3×3 + fila 0+⌫:
    ```
    7  8  9
    4  5  6
    1  2  3
    0  0  ⌫
    ```
  - Botones numpad: 58 px altura, fondo surface2
  - `0` ocupa 2 columnas; `⌫` ocupa 1 (rojo suave)
- Label "Paso 5 de 6"
- Botón `CONFIRMAR MARCA` (btn-primary)

**Comportamiento numpad cm:**
- Máximo 2 dígitos (rango 00–99)
- Ingreso: cada dígito nuevo desplaza hacia la izquierda (`"4"` → `"04"`, luego `"3"` → `"43"`)
- Display muestra `"--"` hasta que se ingresa el primer dígito
- `⌫` elimina el último dígito

**Acciones:**
- Preset → setea metros, resetea selección previa
- `±m` → ajusta metros (no afecta cm)
- Numpad → ingresa cm dígito a dígito
- `CONFIRMAR MARCA` → S-08 Paso 6

---

### S-08 — Paso 6: Asignar Tarjeta

**Propósito:** el juez asigna el resultado de la performance.

**Componentes:**
- Indicador pasos (paso 6 activo, todos anteriores completados)
- Card atleta: nombre, AP, RP confirmado
- Label "Paso 6 de 6 — Asignar tarjeta"
- Botón `⬜ TARJETA BLANCA` (btn-blanca, 19 px)
- Botón `🟨 TARJETA AMARILLA` (btn-amarilla, 19 px)
- Botón `🟥 TARJETA ROJA` (btn-roja, 19 px)

**Acciones:**
- `BLANCA` → S-09 Resultado Blanca
- `AMARILLA` → S-10 Resultado Amarilla (en revisión)
- `ROJA` → S-11 Resultado Roja

---

### S-09 — Resultado: Tarjeta Blanca

**Componentes:**
- Header "Performance completada"
- Hero card: ⬜ icono, "TARJETA BLANCA" (color blanca/verde), nombre + RP, nota AP
- Botón `SIGUIENTE ATLETA →` (btn-primary)

**Acción:** → S-02 Grilla

---

### S-10 — Resultado: Tarjeta Amarilla (En Revisión)

**Propósito:** gestionar la deliberación post-performance (CMAS 1.2.3.1 — máx 3 minutos).

**Componentes:**
- Header "Tarjeta en revisión"
- Badge amarillo "🟨 TARJETA AMARILLA — EN REVISIÓN"
- Sub-label "Debe resolverse antes de cerrar la disciplina"
- Card atleta: nombre, AP, RP
- Alerta amarilla: "La competencia no puede cerrarse mientras existan tarjetas amarillas sin resolver"
- Label "Resolver revisión"
- Botón `⬜ RESOLVER → BLANCA` (btn-blanca)
- Botón `🟥 RESOLVER → ROJA` (btn-roja)
- Botón `Volver a la grilla (queda en revisión)` (btn-ghost)

**Acciones:**
- `RESOLVER → BLANCA` → S-09 Resultado Blanca
- `RESOLVER → ROJA` → S-11 Resultado Roja
- `Volver a la grilla` → S-02 Grilla (fila queda con badge ⚠ REVISIÓN)

---

### S-11 — Resultado: Tarjeta Roja

**Componentes:**
- Header "Performance completada"
- Hero card: 🟥 icono, "TARJETA ROJA" (color roja), nombre + "Descalificada"
- Botón `SIGUIENTE ATLETA →` (btn-primary)

**Acción:** → S-02 Grilla

---

### S-12 — BKO: Black-out

**Propósito:** registrar pérdida de conciencia — tarjeta roja automática (CMAS 1.1.10).

**Componentes:**
- Header "BKO — Black-out" + "Tarjeta roja automática"
- Panel rojo: "⚡ BLACK-OUT DETECTADO — Se asigna tarjeta ROJA automáticamente"
- Card atleta
- Alerta roja: "El campo de distancia alcanzada es **obligatorio**"
- Selector distancia (igual que S-07, con prefijo `bko-`):
  - Display `[metros] m · [cm] cm`
  - Presets metros + ajuste ±1/+5/+10
  - Numpad cm
- Botón `CONFIRMAR BKO — TARJETA ROJA` (btn-roja)

**Restricción:** botón deshabilitado si metros = 0 y cm = "--" (distancia obligatoria).

**Acción:** → S-11 Resultado Roja

---

### S-13 — DNS: Did Not Start

**Propósito:** registrar que el atleta no se presentó al OT.

**Componentes:**
- Header "DNS — Did Not Start"
- Card atleta: nombre, AP, posición, andarivel, OT
- Alerta amarilla: "El atleta no se presentó al OT programado. Se registrará DNS."
- Botón `CONFIRMAR DNS` (btn-dns)
- Botón `Cancelar` (btn-outline) — regresa al paso de origen

**Acciones:**
- `CONFIRMAR DNS` → S-14 Resultado DNS
- `Cancelar` → S-03 Paso 1

---

### S-14 — Resultado DNS

**Componentes:**
- Header "DNS registrado"
- Hero card: "—" icono, "DNS" (color muted), nombre + "No se presentó"
- Botón `SIGUIENTE ATLETA →` (btn-primary)

**Acción:** → S-02 Grilla

---

### S-15 — Revisión desde Grilla (Amarilla pendiente)

**Propósito:** resolver una tarjeta amarilla que quedó pendiente de sesiones anteriores.

**Componentes:**
- Header "En revisión" + "DNF #N"
- Badge "🟨 TARJETA AMARILLA — PENDIENTE"
- Sub-label "Requiere resolución antes del cierre"
- Card atleta: nombre, AP, RP, posición
- Alerta: "La disciplina no puede cerrarse hasta resolver esta tarjeta"
- Botón `⬜ RESOLVER → BLANCA`
- Botón `🟥 RESOLVER → ROJA`

**Acciones:** → S-02 Grilla (con estado actualizado)

---

### S-16 — Demo Offline

**Propósito:** demostrar el comportamiento offline-first.

**Componentes:**
- Badge "Sin conexión" (rojo, parpadeante)
- Alerta azul "📵 Modo offline activo — acciones guardadas localmente"
- Panel "Cola de sincronización" (lista de eventos pendientes)
- Botón `SIMULAR RECONEXIÓN`
- Panel confirmación sync (aparece post-reconexión)

**Acceso:** doble-tap en el header de la grilla (modo demo).

---

## Flujo completo — resumen visual

```
S-00 Login
  └── S-01 Mis Disciplinas
        └── S-02 Grilla de Salida ←─────────────────────────┐
              ├── S-15 Revisión (amarilla pendiente) ────────┤
              └── S-03 Paso 1 Llamar                        │
                    ├── S-13 DNS → S-14 Resultado DNS ───────┤
                    └── S-04 Paso 2 Confirmar                │
                          ├── S-13 DNS → S-14 Resultado DNS ─┤
                          └── S-05 Paso 3 Tiempo Oficial     │
                                ├── DQ ventana → S-11 ───────┤
                                └── S-06 Paso 4 En Curso     │
                                      ├── S-12 BKO → S-11 ──┤
                                      └── S-07 Paso 5 RP     │
                                            └── S-08 Paso 6  │
                                                  ├── S-09 ──┤
                                                  ├── S-10 ──┤
                                                  └── S-11 ──┘
```

---

## Componentes reutilizables para implementación React

| Componente | Pantallas | Props clave |
|------------|-----------|-------------|
| `StepIndicator` | S-03 a S-08 | `total=6, current=N` |
| `AtletaCard` | S-03 a S-08, S-12, S-13 | `nombre, ap, rp?, pos, andarivel, ot?` |
| `ConnectionBadge` | S-01, S-02, S-06 | `online: boolean` |
| `GrillaRow` | S-02 | `atleta, estado, onClick?` |
| `RpSelector` | S-07, S-12 | `id, onValue(m, cm)` |
| `NumpadCm` | S-07, S-12 | `id, value, onChange` |
| `OtWindow` | S-05 | `otTime, onInicia, onDq` |
| `ResultHero` | S-09, S-11, S-14 | `tipo, nombre, rp?` |
| `AlertaRevision` | S-10, S-15 | `atleta, onBlanca, onRoja` |

---

*Prototipo de referencia: `docs/design/ux/prototipos/prototipo-juez.html`*
*Próximo artefacto: `prototipo-organizador.html` + `wireframes-organizador.md`*
