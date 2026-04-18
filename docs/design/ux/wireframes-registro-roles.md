# Wireframes — Registro y Roles

> Artefacto INC-4.0 · Especificación formal derivada de `prototipo-registro-roles.html` validado
> Fuente funcional: onboarding, perfil multirol e invitaciones de juez
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
| Contexto | Onboarding y gestión de identidad multirol desde smartphone |

**Tokens de color**:

| Token | Valor | Uso |
|-------|-------|-----|
| `--bg` | `#0f172a` | Fondo general |
| `--surface` | `#1e293b` | Cards, headers, overlays |
| `--surface2` | `#334155` | Inputs, estados neutros |
| `--border` | `#475569` | Bordes y divisores |
| `--accent` | `#38bdf8` | CTA, rol organizador, navegación activa |
| `--blanca` | `#22c55e` | Éxito, atleta, confirmaciones |
| `--amarilla` | `#eab308` | Juez, advertencias, certificaciones |
| `--roja` | `#ef4444` | Notificación crítica, rechazo |
| `--muted` | `#94a3b8` | Texto secundario |

---

## Navegación base

El flujo combina dos shells:

- shell de autenticación y formularios sin tab bar
- shell autenticada con `tabbar` inferior

**Tabs en shell autenticada:**

```
[🏠 Inicio] [🏆 Torneos] [🔔 Alertas] [👤 Perfil]
```

**Regla principal:** los roles no se seleccionan globalmente al entrar; se materializan por torneo y se resumen en dashboard, notificaciones y perfil.

---

## Pantallas

### S-01 — Login

**Propósito:** acceso para usuarios existentes y entrada al registro.

**Componentes:**
- splash de marca `AtaraxiaDive`
- subtítulo "Gestión de torneos de apnea"
- campo `Email`
- campo `Contraseña`
- link `Olvidé mi contraseña`
- botón `Iniciar sesión`
- link `Crear cuenta`

**Acciones:**
- `Iniciar sesión` → S-05 Dashboard con roles
- `Crear cuenta` → S-02 Registro paso 1

---

### S-02 — Registro Paso 1: Datos personales

**Propósito:** crear identidad básica del usuario.

**Header:** `‹` + título "Crear cuenta".

**Indicador:** progreso de 3 pasos, paso 1 activo.

**Componentes:**
- campos `Nombre`, `Apellido`
- campo `Email`
- helper "Necesitarás confirmar este email"
- campo `Fecha de nacimiento`
- helper sobre categoría de competición
- selector tipo pill `Género`
- botón `Siguiente →`
- link `Iniciar sesión`

**Acción:** `Siguiente →` → S-02b

---

### S-02b — Registro Paso 2: Acceso

**Propósito:** definir credenciales.

**Indicador:** paso 1 completado, paso 2 activo.

**Componentes:**
- campo `Contraseña`
- campo `Confirmar contraseña`
- caja informativa con reglas mínimas de password
- botón `Siguiente →`

**Regla UX:** el requisito de complejidad se presenta inline antes de validación server-side.

**Acción:** `Siguiente →` → S-02c

---

### S-02c — Registro Paso 3: Confirmación

**Propósito:** revisar datos y aceptar términos.

**Indicador:** paso 3 activo, pasos previos completos.

**Componentes:**
- card resumen con nombre, email, fecha de nacimiento y género
- checkbox obligatorio `Términos de uso / Política de privacidad`
- checkbox opcional de notificaciones
- botón `Crear mi cuenta`

**Acción:** `Crear mi cuenta` → S-03 Verificar email

**Invariante:** sin aceptación de términos no debe completarse el alta.

---

### S-03 — Verificar Email

**Propósito:** estado intermedio post-registro.

**Componentes:**
- icono de email
- título "Revisá tu email"
- copy con el correo destino
- botón `Ya confirmé mi email`
- links `Reenviar email` y `Volver`

**Acciones:**
- `Ya confirmé mi email` → S-04 Dashboard vacío
- `Volver` → S-02 Registro paso 1

---

### S-04 — Dashboard vacío

**Propósito:** primer acceso sin torneos ni roles activos.

**Header:** marca + acceso a notificaciones.

**Componentes:**
- bloque de bienvenida
- sección "¿Cómo querés empezar?"
- `path-card` para crear torneo
- `path-card` para inscribirse como atleta
- `path-card` deshabilitada para juez
- caja informativa sobre coexistencia de roles
- tab bar activa en `Inicio`

**Caminos visibles:**

| Camino | Estado | Destino |
|--------|--------|---------|
| Crear un torneo | activo | prototipo organizador |
| Inscribirme a un torneo | activo | prototipo atleta |
| Soy juez | informativo | sin CTA |

**Regla de negocio visible:** el rol juez solo se obtiene por invitación de un organizador.

---

### S-05 — Dashboard con roles activos

**Propósito:** resumir torneos y roles del usuario una vez que ya participa en el ecosistema.

**Header:** marca + campana con punto rojo.

**Componentes:**
- saludo al usuario
- resumen de conteos por rol
- lista `Próximos torneos`
- CTA `+ Inscribirme a otro torneo`

#### Resumen de roles

Contadores mockeados:
- `2 Organizando`
- `1 Juzgando`
- `2 Compitiendo`

#### Lista de torneos

Cada `torneo-row` muestra:
- nombre del torneo
- fecha + sede
- badges de rol por torneo

**Combinaciones soportadas:**

| Caso | Badges |
|------|--------|
| Solo organizador | `🏆 Organizador` |
| Juez + atleta | `⚖️ Juez`, `🤿 Atleta` |
| Solo atleta | `🤿 Atleta` |

**Regla UX:** la vista es agregada por torneo, no por rol aislado.

---

### S-06 — Mi Perfil

**Propósito:** editar identidad de cuenta, datos deportivos y certificaciones.

**Header:** marca + acción `Editar`.

**Secciones:**
- avatar y datos básicos
- `Datos de cuenta`
- `Datos deportivos`
- `Certificaciones de juez`
- `Seguridad`

#### Datos de cuenta

Filas de solo lectura:
- nombre
- email
- fecha de nacimiento
- género

#### Datos deportivos

Campos:
- club
- federación
- número de licencia

Estado mockeado:
- todos `No completado`
- acción `+ Agregar`

**Regla UX:** son opcionales al crear la cuenta, pero necesarios para competir.

#### Certificaciones de juez

Elementos:
- aviso contextual de uso por organizadores
- `cert-card` existente
- botón `+ Agregar otra certificación`

#### Seguridad

Opciones:
- `Cambiar` contraseña
- `Ver` sesiones activas
- botón `Cerrar sesión`

**Acciones:**
- `+ Agregar otra certificación` → S-09 Agregar certificación

---

### S-07 — Notificaciones

**Propósito:** bandeja unificada de eventos relevantes por rol.

**Header:** `‹` + título "Notificaciones".

**Secciones:**
- `Nuevas`
- `Anteriores`

#### Tipos de notificación presentes en el mock

| Tipo | Ejemplo | Acción |
|------|---------|--------|
| Invitación a juez | "Te invitaron como juez" | abrir detalle o aceptar/rechazar |
| Inscripción confirmada | aprobación de atleta | informativa |
| Torneo publicado | apertura organizador | informativa |
| Resultados disponibles | ranking / puesto | informativa |

#### Notificación de invitación

Elementos:
- icono `⚖️`
- título
- subtítulo con organizador y torneo
- timestamp
- acciones inline `Aceptar` / `Rechazar`

**Acciones:**
- tap card → S-08 Invitación detalle
- `Aceptar` → aceptación rápida + dashboard actualizado

---

### S-08 — Invitación de juez

**Propósito:** permitir aceptar formalmente una invitación a un torneo como juez.

**Header:** `‹` + título "Invitación de juez".

**Componentes:**
- `inv-hero` con torneo e invitante
- card `Torneo`
- card `Tu rol`
- bloque `Compatibilidad de roles`
- `cert-card` detectada
- botones `Aceptar invitación` y `Rechazar`

#### Información del torneo

Campos:
- fecha
- sede
- organizador

#### Tu rol

Campos:
- función
- disciplinas
- andarivel asignado

#### Compatibilidad de roles

Caso mockeado:
- usuario puede competir y juzgar en el mismo torneo
- la no colisión se resuelve por andarivel o asignación específica

#### Certificación detectada

Se destaca la credencial existente del usuario para respaldar la invitación.

**Acciones:**
- `Aceptar invitación` → modal de éxito + S-05 Dashboard con roles
- `Rechazar` → S-07 Notificaciones

**Invariante:** una invitación de juez debe hacer visible el rol solamente dentro del torneo correspondiente, no como rol global permanente.

---

### S-09 — Agregar certificación

**Propósito:** registrar credenciales auto-declaradas de juez.

**Header:** `‹` + título "Agregar certificación".

**Componentes:**
- select `Organización`
- selector visual `Nivel`
- campos `Número de certificación`, `Fecha de emisión`, `Vencimiento`
- caja informativa sobre autodeclaración
- botones `Guardar certificación` y `Cancelar`

#### Niveles mockeados

| Nivel | Etiqueta |
|------|----------|
| 1 estrella | Juez Nacional |
| 2 estrellas | Juez Continental |
| 3 estrellas | Juez Internacional |

**Acciones:**
- `Guardar certificación` → S-06 Perfil
- `Cancelar` → S-06 Perfil

**Regla UX:** la plataforma almacena la certificación declarada, pero la verificación final queda en manos del organizador.

---

## Diagrama de navegación

```text
S-01 Login
  ├─► S-02 Registro
  │     ├─► S-02b
  │     ├─► S-02c
  │     └─► S-03 Verificar email
  │           └─► S-04 Dashboard vacío
  └─► S-05 Dashboard con roles
        ├─► S-06 Perfil
        │     └─► S-09 Agregar certificación
        ├─► S-07 Notificaciones
        │     └─► S-08 Invitación de juez
        └─► Flujos externos
              ├─► Portal atleta
              └─► Panel organizador
```

---

## Componentes React identificados

| Componente | Props clave | Pantallas |
|-----------|-------------|-----------|
| `AuthShell` | `title`, `showBack`, `step` | S-01 a S-03 |
| `ProgressSteps` | `currentStep`, `totalSteps` | S-02, S-02b, S-02c |
| `PillSelector` | `options`, `value`, `onChange` | S-02 |
| `CheckRow` | `checked`, `label`, `required` | S-02c |
| `AppShell` | `activeTab`, `notificationsCount` | S-04 a S-09 |
| `PathCard` | `icon`, `title`, `sub`, `disabled`, `onClick` | S-04 |
| `RolesSummary` | `organizing`, `judging`, `competing` | S-05 |
| `TorneoRoleRow` | `torneo`, `roles[]` | S-05 |
| `ProfileInfoRow` | `label`, `value`, `action` | S-06 |
| `CertificationCard` | `org`, `nivel`, `numero`, `vence` | S-06, S-08 |
| `NotificationCard` | `tipo`, `titulo`, `subtitulo`, `time`, `actions` | S-07 |
| `InvitationHero` | `torneo`, `organizador` | S-08 |
| `LevelOptionCard` | `nivel`, `selected`, `onSelect` | S-09 |

---

## Invariantes de negocio formalizados

| ID | Regla | Fuente |
|----|-------|--------|
| INV-RR-01 | Un usuario puede coexistir como organizador, juez y atleta en distintos torneos | Prototipo S-04/S-05 |
| INV-RR-02 | El rol de juez no se autoasigna; solo se obtiene por invitación | Prototipo S-04 |
| INV-RR-03 | La compatibilidad atleta+juez se resuelve por disciplina/andarivel y debe informarse explícitamente | Prototipo S-08 |
| INV-RR-04 | Las certificaciones de juez son auto-declaradas y requieren validación externa si el torneo lo exige | Prototipo S-06/S-09 |
| INV-RR-05 | Los datos deportivos son opcionales al alta, pero necesarios para competir | Prototipo S-06 |
| INV-RR-06 | La aceptación de términos es obligatoria para crear la cuenta | Prototipo S-02c |
| INV-RR-07 | La cuenta debe verificarse por email antes del primer acceso funcional | Prototipo S-03 |
| INV-RR-08 | Las notificaciones agrupan eventos de distintos roles en una sola bandeja | Prototipo S-07 |

---

*Artefacto generado: 2026-04-08 — INC-4.0 UX Design*
*Capa IEDD: 3b — Especificación interactiva*
