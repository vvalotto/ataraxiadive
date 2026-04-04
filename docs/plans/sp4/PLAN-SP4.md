# Plan SP4 — La Plataforma (BL-004)

| Campo | Valor |
|-------|-------|
| **Sprint** | SP4 |
| **Baseline** | BL-004 |
| **Tag git** | `v0.5.0` |
| **Fecha** | 2026-04-04 |
| **Estado** | ⏳ Pendiente |

---

## Objetivo

Transformar el sistema de API-only a plataforma completa: crear el frontend React PWA,
implementar BC Notificaciones (primera implementación real), y exponer la auditoría
de resultados. El juez puede operar desde el celular, desconectado de la red, con
confirmación de que sus acciones llegaron al servidor.

**DoD de cierre de SP4:** el juez puede ejecutar un flujo completo de performance
desde la PWA en el celular — incluyendo modo offline — y los atletas reciben
notificaciones email en los momentos clave.

---

## BCs activos

| BC | Tipo | Novedad en SP4 |
|----|------|----------------|
| **Competencia** | Core / ES | Extensión — auditoría visible via API + hash SHA-256 al cierre de disciplina |
| **Notificaciones** | Generic / ES | **Nuevo** — primera implementación real: aggregate + event store + email |
| **Resultados** | Supporting / CRUD | Extensión — endpoint exportación CSV/JSON |
| **Frontend** | React PWA | **Nuevo** — creación desde cero con Vite |

---

## Prerequisito de tooling (antes de INC-4.2)

Antes de la primera US de implementación backend, adaptar `/implement-us` al perfil
`hexagonal-ddd-bc` del proyecto. Ver issue **vvalotto/claude-dev-kit#46**.

Acción concreta: crear `docs/plans/ATARAXIADIVE-CONTEXT.md` con el mapa de BCs actual
y actualizar `.claude/skills/implement-us/customizations/` si el perfil fue publicado.
Si el perfil no está disponible aún en el Dev Kit, verificar que la customización
existente (`fastapi-rest.json` v2.0.0) sigue alineada con el estado actual de SP4.

---

## Incrementos y US

### INC-4.0 — UX Design

**Responsable:** Cowork (claude.ai) con input de Victor
**DoD:** artefactos de diseño comprometidos en `docs/design/ux/` y aprobados por Victor
antes de escribir una línea de frontend.

| Artefacto | Descripción |
|-----------|-------------|
| `docs/design/ux/flujos-por-rol.md` | Flujos de usuario por rol (juez, organizador, atleta) |
| `docs/design/ux/wireframes-juez.md` | Wireframes de las pantallas críticas del juez (6 pasos + offline) |
| `docs/design/ux/wireframes-organizador.md` | Panel del organizador: torneo, grilla, jueces |
| `docs/design/ux/wireframes-atleta.md` | Portal del atleta: inscripción, anuncios, resultados |
| `docs/design/ux/decisiones-frontend.md` | Stack: librería UI, routing, state management, estrategia offline |

> **Nota:** INC-4.0 no genera código. Produce especificaciones de diseño que son el
> input directo de INC-4.1 y INC-4.2. No se puede iniciar INC-4.1 sin INC-4.0 aprobado.

---

### INC-4.1 — Fundación Frontend

**DoD:** la aplicación React PWA levanta, conecta con el backend existente, y muestra
un health-check visual. La estructura de carpetas está establecida (BC-first o por feature
— según decisión de INC-4.0). El CI verifica que el build frontend no rompe.

| US | Descripción |
|----|-------------|
| US-4.1.1 | Scaffold Vite + React + PWA — estructura, routing base, health-check visual conectado a `GET /health` |
| US-4.1.2 | Autenticación en frontend — login JWT, contexto de usuario, rutas protegidas por rol |

---

### INC-4.2 — Interfaz del Juez

**DoD:** el juez puede ejecutar el flujo completo (6 pasos: Llamar → Confirmar → Iniciar →
Finalizar → Registrar marca → Asignar tarjeta) desde la PWA en el celular, con los datos
reales del backend. La pantalla respeta los principios de diseño: botones ≥ 48px, alto
contraste, máximo 6 toques por performance (AC-US-02, AC-US-03).

| US | Descripción |
|----|-------------|
| US-4.2.1 | Pantalla de selección de competencia — juez ve sus disciplinas asignadas |
| US-4.2.2 | Flujo de performance — los 6 pasos conectados al backend (AP, llamar, confirmar, resultado, tarjeta) |
| US-4.2.3 | Casos alternativos — DNS y black-out desde la UI |

---

### INC-4.3 — Offline-first

**DoD:** el juez puede poner el celular en modo avión, registrar 5 performances, reconectar,
y verificar que se sincronizaron al servidor. Un indicador visible muestra el estado de
conexión. Los datos persistidos en IndexedDB sobreviven un cierre del navegador.

| US | Descripción |
|----|-------------|
| US-4.3.1 | Service Worker + pre-carga — al abrir una disciplina se pre-cargan grilla, atletas y reglas en IndexedDB |
| US-4.3.2 | Operación offline — el flujo de los 6 pasos funciona sin conexión (eventos locales en IndexedDB) |
| US-4.3.3 | Sincronización — Background Sync API envía eventos locales al reconectar; indicador de conexión |

---

### INC-4.4 — BC Notificaciones

**DoD:** al confirmar la inscripción de un atleta se envía un email real a una dirección
de prueba. El aggregate `Notificacion` tiene event store funcional. La idempotencia
exactly-once está verificada por test: un mismo evento fuente no dispara dos emails.

| US | Descripción | BC afectado |
|----|-------------|-------------|
| US-4.4.1 | Aggregate `Notificacion` — ciclo de vida (Solicitada → Enviada / Fallida), event store, idempotencia | `notificaciones/domain/` |
| US-4.4.2 | Adaptador email — integración con servicio gestionado (SendGrid / SES / Resend), puerto + adaptador | `notificaciones/infrastructure/` |
| US-4.4.3 | Política P-10 — `InscripcionConfirmada` (Registro) → `SolicitarNotificacion` → email al atleta | `src/app.py`, `notificaciones/application/` |
| US-4.4.4 | Política P-11 — `ResultadosPublicados` (Resultados) → email a atletas de esa disciplina | `src/app.py`, `notificaciones/application/` |

---

### INC-4.5 — Auditoría y Exportación

**DoD:** el organizador puede ver la traza completa de eventos de cualquier performance
desde la UI. Al cerrar una disciplina se calcula y persiste el hash SHA-256 de todos
sus eventos. La exportación CSV/JSON de resultados funciona y descarga un archivo real.

| US | Descripción | BC afectado |
|----|-------------|-------------|
| US-4.5.1 | API de auditoría — `GET /competencias/{id}/performances/{pid}/audit-log` devuelve secuencia de eventos | `competencia/api/` |
| US-4.5.2 | Hash SHA-256 al cierre — al ejecutar `CerrarCompetencia`, calcular y persistir hash de todos los eventos | `competencia/domain/`, `competencia/infrastructure/` |
| US-4.5.3 | UI auditoría — pantalla del organizador: traza de eventos por performance, hash de disciplina cerrada | `frontend/` |
| US-4.5.4 | Exportación — `GET /resultados/{torneo_id}/export?format=csv|json` descarga resultados completos | `resultados/api/` |

---

## Dependencias entre incrementos

```
INC-4.0 (UX Design)
  └── INC-4.1 (Fundación Frontend)
        └── INC-4.2 (Interfaz del Juez)   ← prerequisito: tooling /implement-us
              └── INC-4.3 (Offline-first)
  INC-4.4 (Notificaciones)               ← independiente del frontend, paralelo a INC-4.2/4.3
  INC-4.5 (Auditoría)                    ← depende de INC-4.1 (UI) e INC-4.2 (backend)
```

> INC-4.4 puede ejecutarse en paralelo con INC-4.2/4.3 — es backend puro.

---

## Notas de implementación

### Frontend — stack (a confirmar en INC-4.0)

```
Vite + React + TypeScript
├── Routing: React Router v6
├── Estado global: Zustand (ligero) o React Query (si es principalmente server state)
├── UI: shadcn/ui + Tailwind (mobile-first, alto contraste)
├── PWA: vite-plugin-pwa (Workbox)
└── Offline: IndexedDB via Dexie.js
```

La elección final de librería UI y estrategia de estado se decide en INC-4.0.

### BC Notificaciones — event store

Usa el mismo patrón que BC Competencia: tabla `notificaciones_events` en SQLite propio
(`notificaciones.db`). La idempotencia se implementa con una query:
`SELECT 1 FROM notificaciones_events WHERE tipo = 'NotificacionEnviada' AND evento_fuente_id = ?`
antes de enviar.

### Offline — estrategia de sincronización

Background Sync API + Service Worker. Si el browser no soporta Background Sync,
fallback a retry automático al detectar `navigator.onLine = true`.
Los eventos locales se persisten en IndexedDB como cola de comandos pendientes.

### Hash SHA-256 — cierre de disciplina

Al ejecutar `CerrarCompetencia`, el command handler:
1. Lee todos los eventos del aggregate desde el event store (orden cronológico)
2. Serializa a JSON canónico (campos ordenados)
3. Calcula SHA-256 del string concatenado
4. Persiste `HashCierre` como evento inmutable en el store

---

## Fuera de scope SP4 → SP5

| Item | Motivo de diferimiento |
|------|----------------------|
| RF-EJ-04 — códigos de penalización configurables | Pendiente de definición por parte de la federación |
| Panel admin de configuración (disciplinas, categorías) | Requiere UX separada; SP5 |
| Notificaciones push (FCM) | Email primero; push cuando esté probado el canal base |
| Integración FAZ (RF-IG-01) | Protocolo pendiente |
| Fórmula de puntos RF-PM-01 | Pendiente de definición |

---

## DoD de Cierre (BL-004)

- [ ] `pytest tests/` — 100% pass
- [ ] Flujo E2E frontend: login juez → seleccionar disciplina → registrar 3 performances → ver ranking
- [ ] Offline verificado: modo avión → 3 performances → reconectar → sincronización confirmada
- [ ] Email enviado realmente a dirección de prueba al confirmar inscripción
- [ ] `designreviewer src/` — cero CRITICAL
- [ ] Hash SHA-256 persiste al cerrar una disciplina
- [ ] `CLAUDE.md §14` actualizado con SP4 completo

---

*Redactado: 2026-04-04 — SP4 La Plataforma*
