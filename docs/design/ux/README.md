# INC-4.0 — UX Design — Proceso y Artefactos

| Campo | Valor |
|-------|-------|
| **Incremento** | INC-4.0 — UX Design |
| **Sprint** | SP4 — La Plataforma |
| **Responsable** | Cowork (claude.ai) con input de Victor |
| **Fecha** | 2026-04-08 |
| **DoD** | Todos los artefactos comprometidos en esta carpeta y aprobados por Victor antes de escribir una línea de frontend |

---

## Propósito de esta carpeta

`docs/design/ux/` contiene los artefactos de diseño de interfaz que son el **input directo
de INC-4.1 y siguientes**. Sin estos artefactos aprobados, Code no puede iniciar la
implementación del frontend.

Esta carpeta tiene dos tipos de artefactos con roles distintos:

| Tipo | Formato | Propósito | Consumidor |
|------|---------|-----------|-----------|
| **Prototipo navegable** | HTML autocontenido | Validación visual e interactiva — se revisa en el chat y en el celular | Victor (revisión) |
| **Spec de diseño** | Markdown | Especificación técnica que Code usa para implementar | Claude Code + `/implement-us` |

Los prototipos se guardan en `prototipos/`. Las specs en la raíz de esta carpeta.
Ambos se commitean al repo — los prototipos son documentación viva del diseño.

---

## Artefactos de INC-4.0

### Specs (Markdown — input para Code)

| Artefacto | Estado | Descripción |
|-----------|--------|-------------|
| `flujos-por-rol.md` | ✅ Completo | Flujos de usuario por rol: juez, organizador y atleta |
| `wireframes-juez.md` | ✅ Completo | Pantallas del juez: 6 pasos + amarilla en revisión + BKO + offline |
| `wireframes-organizador.md` | ✅ Completo | Panel del organizador: torneo, grilla, jueces asignados, auditoría |
| `wireframes-atleta.md` | ✅ Completo | Portal del atleta: inscripción, anuncios, grilla y resultados |
| `wireframes-registro-roles.md` | ✅ Completo | Onboarding, perfil multirol, notificaciones e invitaciones de juez |
| `wireframes-setup-torneo.md` | ✅ Completo | Flujo de preparación del torneo: disciplinas, grilla y asignación de jueces |
| `decisiones-frontend.md` | ✅ Completo | Stack final: librería UI, routing, state management y estrategia offline |
| `decisiones-registro-usuario.md` | ✅ Completo | Decisiones específicas del flujo de registro, roles y certificaciones |

### Prototipos (HTML — input para validación visual)

| Artefacto | Estado | Descripción |
|-----------|--------|-------------|
| `prototipos/prototipo-juez.html` | ✅ Completo | Flujo completo del juez — navegable, mobile-first |
| `prototipos/prototipo-organizador.html` | ✅ Completo | Panel del organizador operativo — navegable |
| `prototipos/prototipo-atleta.html` | ✅ Completo | Portal del atleta — navegable |
| `prototipos/prototipo-registro-roles.html` | ✅ Completo | Registro, perfil multirol, notificaciones e invitaciones |
| `prototipos/prototipo-setup-torneo.html` | ✅ Completo | Setup del torneo antes de la operación en vivo |

### Estado del paquete UX

El paquete base de INC-4.0 quedó cubierto con estos bloques:

- autenticación, onboarding y gestión multirol
- operación del juez en competencia
- operación del organizador en vivo
- preparación y publicación del torneo
- experiencia del atleta pre-competencia y post-competencia
- decisiones de frontend para iniciar INC-4.1

En otras palabras, esta carpeta ya contiene el set mínimo de contratos UX necesarios para comenzar la implementación del frontend.

---

## Proceso de validación por artefacto

El orden no es opcional. Cada pantalla sigue este ciclo antes de pasar a la siguiente:

```
1. Cowork crea prototipo HTML navegable
       ↓
2. Se renderiza en el chat (Claude in Chrome → GIF del flujo)
       ↓
3. Victor lo abre en el celular y toca los botones con el dedo
       ↓
4. Iteración hasta aprobación visual
       ↓
5. Cowork escribe la spec Markdown formal (wireframes-*.md)
       ↓
6. Commit de ambos (prototipo + spec)
       ↓
7. Victor revisa el Markdown y aprueba
       ↓
8. Siguiente artefacto
```

La validación en celular es **obligatoria para la interfaz del juez** por las restricciones
físicas del dominio (ver más abajo). Para organizador y atleta es recomendable pero no bloqueante.

---

## Restricciones de diseño del dominio (no negociables)

Estas restricciones son invariantes de UX — equivalentes a los invariantes de dominio.
Aplican a **toda** la interfaz del juez y guían el diseño de las demás.

### Interfaz del juez

| Restricción | Valor | Fundamento |
|-------------|-------|-----------|
| Toques por performance | ≤ 6 | El juez no puede distraerse de la performance del atleta |
| Tamaño mínimo de botón | ≥ 48px | Operación con manos mojadas en borde de pileta |
| Contraste | Alto — fondo oscuro / texto blanco | Uso bajo sol directo en competencias al aire libre |
| Tipografía | ≥ 18px para datos críticos | Legibilidad a distancia y bajo tensión |
| El juez solo ve sus disciplinas asignadas | — | Invariante de seguridad del BC Competencia |

### Flujo del juez — los 6 pasos

```
[1] Llamar atleta
    ↓
[2] Confirmar presencia
    ↓
[3] Iniciar performance (OT)
    ↓
[4] Finalizar performance
    ↓
[5] Registrar marca (RP)
    ↓
[6] Asignar tarjeta  →  Blanca | Amarilla* | Roja
```

### Casos especiales obligatorios

**Tarjeta amarilla — estado de revisión transitorio:**
```
AsignarTarjeta(Amarilla) → Performance en revisión
    ├── ResolverRevision(Blanca) → Performance válida
    └── ResolverRevision(Roja)  → Performance descalificada

INV: CerrarCompetencia falla si existe alguna Performance con tarjeta Amarilla sin resolver.
```

**BKO (black-out):**
```
El juez activa BKO → tarjeta Roja automática + campo distancia alcanzada obligatorio
```

**DNS (Did Not Start):**
```
El atleta no se presenta al OT → el juez registra DNS → siguiente atleta en la grilla
```

---

## Stack técnico (a confirmar en decisiones-frontend.md)

```
Vite + React + TypeScript
├── Routing:       React Router v6
├── Estado global: Zustand (preferido) o React Query
├── UI:            shadcn/ui + Tailwind — mobile-first, alto contraste
├── PWA:           vite-plugin-pwa (Workbox)
└── Offline:       IndexedDB via Dexie.js
```

La decisión final entre Zustand y React Query se documenta en `decisiones-frontend.md`
con fundamento en los patrones de estado de cada rol.

---

## Herramientas usadas en INC-4.0

| Herramienta | Uso |
|------------|-----|
| **Cowork** | Autor de todos los artefactos |
| **Claude in Chrome** | Abre el HTML, navega el prototipo, graba GIF del flujo para revisión en el chat |
| **design:design-handoff** | Genera la spec técnica de componentes (estados, tamaños, props) a partir del prototipo aprobado |
| **design:ux-copy** | Copy de botones y mensajes de la interfaz del juez — alta precisión requerida |

---

*Creado: 2026-04-04 — inicio de INC-4.0*
*Proceso acordado en sesión Cowork — ver HITO-18*
