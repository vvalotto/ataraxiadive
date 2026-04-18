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
| **Competencia** | Core / ES | Extensión — motivos tarjeta roja, tarjeta blanca con penalizaciones, orden de grilla, auditoría + hash SHA-256 |
| **Torneo** | Supporting / CRUD | Extensión — subdisciplinas SPE (variante) |
| **Resultados** | Supporting / CRUD | Extensión — RP penalizado, ranking por variante SPE, exportación CSV/JSON |
| **Notificaciones** | Generic / ES | **Nuevo** — primera implementación real: aggregate + event store + email |
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

### INC-4.1 — Correcciones de dominio por reglamento CMAS/FAAS

**Prerequisito:** INC-4.0 aprobado.
**DoD:** el dominio refleja el reglamento oficial en los puntos identificados. Cero regresiones
en los 785 tests existentes. Las nuevas reglas tienen cobertura de tests unitarios ≥ 90%.

> Este incremento es backend puro — no toca el frontend. Debe completarse antes de INC-4.3
> (Interfaz del Juez) para que el frontend se construya sobre el modelo correcto.
> Fuente: `docs/dominio/06-brechas-reglamento.md`

| US | Descripción | BC afectado |
|----|-------------|-------------|
| US-4.1.1 | Motivos de tarjeta roja — CRUD de causas de descalificación (BKO superficie, BKO subacuático, no siguió protocolo, infracción técnica, no inició en ventana, salida en falso) | `competencia/domain/` |
| US-4.1.2 | Tarjeta Blanca con penalizaciones — nuevo resultado: performance válida con infracciones técnicas; RP final = medido − N×3m; las penalizaciones se acumulan | `competencia/domain/`, `resultados/domain/` |
| US-4.1.3 | Subdisciplinas SPE — cuatro variantes (2×50m, 4×50m, 8×50m, 16×50m); la disciplina SPE pasa a tener atributo `variante`; cada variante tiene su propia grilla y ranking | `torneo/domain/`, `resultados/domain/` |
| US-4.1.4 | Orden de grilla reglamentario — generación de grilla con ordenamiento por AP ascendente (DNF/DYN/DBF/STA) o descendente (SPE); el organizador puede ajustar manualmente después | `competencia/domain/` |
| US-4.1.5 | Descomponer aggregate `Performance` — eliminar GodObject (métrica 31/28 DesignReviewer) extrayendo VOs de resolución de tarjeta y cálculo de RP penalizado | `competencia/domain/` |
| US-4.1.6 | Aliviar handlers de `competencia` — reducir FeatureEnvy y LongMethod en AsignarTarjetaHandler, GenerarGrillaHandler y otros handlers core | `competencia/application/` |
| US-4.1.7 | Simplificar `GrillaDeSalida` y `RankingCompetencia` — partir métodos largos de ajuste de grilla y cálculo de ranking en submétodos cohesivos | `competencia/domain/`, `resultados/domain/`, `resultados/infrastructure/` |
| US-4.1.8 | Limpiar `Torneo`, `SQLiteTorneoRepository` y VOs de soporte — reducir complejidad accidental en objetos con responsabilidad expandida | `torneo/domain/`, `torneo/infrastructure/`, `competencia/domain/value_objects/` |

> **US-4.1.5 a US-4.1.8:** ajustes técnicos derivados del DesignReviewer al cierre del incremento funcional (HITO-19).
> Son parte del mismo INC-4.1 — se implementan antes del PR de cierre.

**Documentos a actualizar al cerrar INC-4.1:**
- `docs/design/domain-model.md` — nuevos conceptos: motivos de tarjeta roja, tarjeta blanca con penalizaciones, variante SPE
- `docs/design/event-storming-competencia.md` — nuevos eventos y comandos derivados de las correcciones
- `CLAUDE.md §8` — lenguaje ubicuo: agregar términos Tarjeta Blanca con Penalizaciones, Motivo de DQ, Variante SPE
- `docs/traceability/matrix.md` — registrar US-4.1.1 a US-4.1.8
- ADR nuevo si alguna decisión de diseño lo amerita (ej: modelo de penalizaciones acumulables)

---

### INC-4.2 — Fundación Frontend

**DoD:** la aplicación React PWA levanta, conecta con el backend existente, y muestra
un health-check visual. La estructura de carpetas está establecida (BC-first o por feature
— según decisión de INC-4.0). El CI verifica que el build frontend no rompe.

| US | Descripción |
|----|-------------|
| US-4.2.1 | Scaffold Vite + React + PWA — estructura, routing base, health-check visual conectado a `GET /health` |
| US-4.2.2 | Autenticación en frontend — login JWT, contexto de usuario, rutas protegidas por rol |

---

### INC-4.3 — Interfaz del Juez

**DoD:** el juez puede ejecutar el flujo completo (6 pasos: Llamar → Confirmar → Iniciar →
Finalizar → Registrar marca → Asignar tarjeta) desde la PWA en el celular, con los datos
reales del backend. La pantalla respeta los principios de diseño: botones ≥ 48px, alto
contraste, máximo 6 toques por performance (AC-US-02, AC-US-03).

| US | Descripción |
|----|-------------|
| US-4.3.1 | Pantalla de selección de competencia — juez ve sus disciplinas asignadas |
| US-4.3.2 | Flujo de performance — los 6 pasos conectados al backend (AP, llamar, confirmar, resultado, tarjeta) |
| US-4.3.3 | Casos alternativos — DNS, motivos de tarjeta roja y tarjeta blanca con penalizaciones desde la UI |
| US-4.3.4 | Tarjeta amarilla como estado de revisión — flujo `Amarilla → Blanca\|Roja` + invariante cierre |
| US-4.3.5 | Adaptación STA — Paso 3 muestra botón "Vías respiratorias en agua" en lugar de "Atleta inicia"; cronómetro arranca en ese momento |

---

### INC-4.4 — Offline-first

**DoD:** el juez puede poner el celular en modo avión, registrar 5 performances, reconectar,
y verificar que se sincronizaron al servidor. Un indicador visible muestra el estado de
conexión. Los datos persistidos en IndexedDB sobreviven un cierre del navegador.

| US | Descripción |
|----|-------------|
| US-4.4.1 | Service Worker + pre-carga — al abrir una disciplina se pre-cargan grilla, atletas y reglas en IndexedDB |
| US-4.4.2 | Operación offline — el flujo de los 6 pasos funciona sin conexión (eventos locales en IndexedDB) |
| US-4.4.3 | Sincronización — Background Sync API envía eventos locales al reconectar; indicador de conexión |

---

### INC-4.5 — BC Notificaciones

**DoD:** al confirmar la inscripción de un atleta se envía un email real a una dirección
de prueba. El aggregate `Notificacion` tiene event store funcional. La idempotencia
exactly-once está verificada por test: un mismo evento fuente no dispara dos emails.

| US | Descripción | BC afectado |
|----|-------------|-------------|
| US-4.5.1 | Aggregate `Notificacion` — ciclo de vida (Solicitada → Enviada / Fallida), event store, idempotencia | `notificaciones/domain/` |
| US-4.5.2 | Adaptador email — integración con servicio gestionado (SendGrid / SES / Resend), puerto + adaptador | `notificaciones/infrastructure/` |
| US-4.5.3 | Política P-10 — `InscripcionConfirmada` (Registro) → `SolicitarNotificacion` → email al atleta | `src/app.py`, `notificaciones/application/` |
| US-4.5.4 | Política P-11 — `ResultadosPublicados` (Resultados) → email a atletas de esa disciplina | `src/app.py`, `notificaciones/application/` |

---

### INC-4.6 — Auditoría y Exportación

**DoD:** el organizador puede ver la traza completa de eventos de cualquier performance
desde la UI. Al cerrar una disciplina se calcula y persiste el hash SHA-256 de todos
sus eventos. La exportación CSV/JSON de resultados funciona y descarga un archivo real.

| US | Descripción | BC afectado |
|----|-------------|-------------|
| US-4.6.1 | API de auditoría — `GET /competencias/{id}/performances/{pid}/audit-log` devuelve secuencia de eventos | `competencia/api/` |
| US-4.6.2 | Hash SHA-256 al cierre — al ejecutar `CerrarCompetencia`, calcular y persistir hash de todos los eventos | `competencia/domain/`, `competencia/infrastructure/` |
| US-4.6.3 | UI auditoría — pantalla del organizador: traza de eventos por performance, hash de disciplina cerrada | `frontend/` |
| US-4.6.4 | Exportación — `GET /resultados/{torneo_id}/export?format=csv|json` descarga resultados completos | `resultados/api/` |

---

## Dependencias entre incrementos

```
INC-4.0 (UX Design)
  ├── INC-4.1 (Correcciones dominio)      ← backend puro, prerequisito de INC-4.3
  └── INC-4.2 (Fundación Frontend)        ← prerequisito: tooling /implement-us
        └── INC-4.3 (Interfaz del Juez)   ← requiere INC-4.1 + INC-4.2
              └── INC-4.4 (Offline-first)
  INC-4.5 (Notificaciones)               ← independiente del frontend, paralelo a INC-4.3/4.4
  INC-4.6 (Auditoría)                    ← depende de INC-4.2 (UI) e INC-4.3 (backend)
```

> INC-4.1 e INC-4.2 pueden ejecutarse en paralelo — son independientes entre sí.
> INC-4.5 puede ejecutarse en paralelo con INC-4.3/4.4 — es backend puro.

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

### Tarjeta amarilla — flujo de revisión (nuevo en SP4)

La tarjeta amarilla es un **estado transitorio**, no un resultado final:

```
AsignarTarjeta(Amarilla)  →  Performance en revisión
  ├── ResolverRevision(Blanca)  →  Performance válida
  └── ResolverRevision(Roja)   →  Performance descalificada
```

**INV-nuevo:** `CerrarCompetencia` falla si existe alguna `Performance` con tarjeta
`Amarilla` sin resolver. El sistema debe forzar la resolución antes de permitir el cierre.

Impacto en el dominio existente:
- `Performance` necesita distinguir `tarjeta_final` (Blanca/Roja) de `tarjeta_revision` (Amarilla)
- Nuevo comando `ResolverRevision(performance_id, resolucion: Blanca|Roja, motivo)`
- Nuevo evento `RevisionResuelta`
- `CerrarCompetencia` agrega precondición: `all(p.tarjeta != Amarilla for p in performances)`

### BC Notificaciones — event store

Usa el mismo patrón que BC Competencia: tabla `notificaciones_events` en SQLite propio
(`notificaciones.db`). La idempotencia se implementa con una query:
`SELECT 1 FROM notificaciones_events WHERE event_type = 'NotificacionEnviada'
AND json_extract(payload, '$.evento_fuente_id') = ?`
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
| Integración FAAS (RF-IG-01) | Protocolo pendiente |
| Fórmula de puntos RF-PM-01 | Pendiente de definición |

---

## DoD de Cierre (BL-004)

- [ ] `pytest tests/` — 100% pass
- [ ] Flujo E2E frontend: login juez → seleccionar disciplina → registrar 3 performances (con y sin penalizaciones) → ver ranking
- [ ] Offline verificado: modo avión → 3 performances → reconectar → sincronización confirmada
- [ ] Email enviado realmente a dirección de prueba al confirmar inscripción
- [ ] `designreviewer src/` — cero CRITICAL
- [ ] Hash SHA-256 persiste al cerrar una disciplina
- [ ] `CLAUDE.md §14` actualizado con SP4 completo

---

*Redactado: 2026-04-04 — SP4 La Plataforma*
