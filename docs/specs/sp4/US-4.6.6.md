# US-4.6.6: Documentación de arquitectura — Offline-first

**Estado**: `To Do`
**Sprint**: SP4 — La Plataforma
**Incremento**: INC-4.6
**Tipo**: Documentación de arquitectura y diseño
**Artefactos producidos**: `docs/design/offline-first.md` · actualización de `docs/adr/ADR-003-offline-first-pwa.md`

---

## Descripción

Como **equipo de desarrollo y futuros colaboradores**,
quiero **documentación completa del diseño offline-first implementado en INC-4.4**
para **entender las decisiones de arquitectura tomadas, el flujo de datos entre Service Worker / IndexedDB / Backend, y las restricciones que todo cambio futuro debe respetar**.

---

## Contexto

INC-4.4 implementó la operación offline de la interfaz del juez. Las decisiones de diseño se tomaron durante la implementación (INC-4.4) y están dispersas en ADR-003, ADR-015 y el código. Esta US las consolida en documentación estructurada.

**ADRs existentes relacionados:**
- **ADR-003** (2026-03-14): decisión estratégica PWA + Service Worker + IndexedDB. Describe el "qué" pero fue escrito antes de la implementación — no refleja el "cómo" real.
- **ADR-015** (2026-04-13): adopción de Dexie.js. Completo para su alcance.

**Gaps que esta US cubre:**
- Cómo funciona realmente el ciclo offline/online/sync en el código implementado
- La arquitectura de la cola de comandos (`comando_queue`) y su protocolo de sincronización
- La estrategia de resolución ante conflictos (qué pasa si dos jueces editan el mismo atleta)
- Los límites del diseño: qué NO soporta offline (pantallas del organizador, auditoría)

---

## Especificación — qué debe contener la documentación

### ADR-003 — Secciones a actualizar

El ADR-003 original (2026-03-14) fue escrito en Fase 0 como decisión prospectiva. Actualizar las siguientes secciones para reflejar la implementación real de INC-4.4:

**Sección "Consecuencias — Notas de implementación" (nueva sección a agregar):**
- Módulos implementados: `usePrecarga`, `useComandoQueue`, `useSyncQueue`, `GrillaPage`
- Dexie.js como capa de acceso (referencia a ADR-015)
- Background Sync automático al detectar reconexión (listener `online` en `useSyncQueue`)
- Comportamiento en iOS: las restricciones del Service Worker en Safari requieren sync manual como fallback

**Sección "Límites del diseño offline" (nueva sección a agregar):**
- Solo la interfaz del juez opera offline
- El organizador requiere conexión permanente
- La pantalla de auditoría (INC-4.6) no está disponible offline
- Las notificaciones (INC-4.5) son exclusivamente del lado servidor

---

### docs/design/offline-first.md — Documento nuevo

El documento debe cubrir los siguientes bloques:

**1. Problema y decisión estratégica**
- Por qué offline es no negociable (AC-DS-03, entornos de competencia)
- La decisión PWA vs app nativa (referencia a ADR-003)

**2. Arquitectura del frontend offline**

Diagrama de componentes y flujo de datos:

```
┌─────────────────────────────────────────────────────────────┐
│  GrillaPage                                                 │
│    usePrecarga()         → IndexedDB (grilla_cache)         │
│    useComandoQueue()     → IndexedDB (comando_queue)        │
│    useSyncQueue()        → background sync al reconectar    │
└─────────────────────────────────────────────────────────────┘
         │                              │
         ▼ online                       ▼ sync
   Backend API                    Backend API
   (GET grilla,                   (POST comandos
    GET estado)                    pendientes)
```

Diagrama de secuencia del ciclo completo (online → offline → reconexión → sync).

**3. Cola de comandos — protocolo**
- Estructura de un item en `comando_queue`: `{ id, endpoint, method, body, timestamp, retries, status }`
- Estados de un comando en cola: `pending` → `syncing` → `done` | `failed`
- Política de reintentos: máximo 3 intentos con backoff exponencial
- Qué ocurre si un comando falla definitivamente (alerta al usuario)

**4. Estrategia de conflictos**
- Diseño actual: cada atleta es operado por un único juez → no hay conflictos concurrentes por diseño del dominio
- Qué pasa si dos jueces intentan operar el mismo atleta: el backend rechaza el segundo comando (invariante del aggregate `Performance`)
- Cómo se manifiesta en la UI: el comando fallido queda en estado `failed` en la cola; el juez ve una alerta

**5. Restricciones de plataforma**
- Safari/iOS: Service Worker con restricciones. Mitigación: sync manual como fallback (botón visible cuando hay comandos pendientes)
- Chrome/Android: comportamiento nominal

**6. Límites del diseño — qué NO opera offline**
- Pantallas del organizador (incluyendo auditoría INC-4.6)
- Notificaciones email (servidor-lado)
- Login/autenticación (requiere conexión)

**7. Evolución futura**
- En SP5: si se requiere multi-juez concurrente, evaluar CRDT o timestamps lógicos
- En SP5: Service Worker más sofisticado para cache de assets (actualmente solo datos)

---

## Criterios de aceptación

```gherkin
Feature: US-4.6.6 — Documentación offline-first

  Scenario: ADR-003 refleja la implementación real
    Given el ADR-003 actualizado
    Then contiene una sección "Notas de implementación" con los módulos de INC-4.4
    And contiene una sección "Límites del diseño offline"
    And la fecha de última modificación está actualizada

  Scenario: docs/design/offline-first.md existe y es completo
    Given el documento creado
    Then contiene los 7 bloques especificados
    And incluye al menos un diagrama de arquitectura (Mermaid o ASCII)
    And incluye un diagrama de secuencia del ciclo offline/sync
    And describe el protocolo de la cola de comandos con sus estados
    And es consistente con el código en frontend/src/hooks/

  Scenario: consistencia con ADR-015
    Then offline-first.md referencia ADR-015 para la decisión de Dexie.js
    And no contradice ninguna afirmación de ADR-015
```

---

## Impacto arquitectónico

- [x] Sí → ADR-016 no aplica aquí; se actualiza ADR-003 existente

**Artefactos a producir:**
1. `docs/adr/ADR-003-offline-first-pwa.md` — agregar secciones de implementación y límites (no reescribir, solo extender)
2. `docs/design/offline-first.md` — documento nuevo

---

## Referencias

- ADR-003: decisión estratégica PWA (a actualizar)
- ADR-015: Dexie.js (referencia, no modificar)
- US-4.4.1, US-4.4.2, US-4.4.3: implementación fuente
- `frontend/src/hooks/usePrecarga.ts`, `useComandoQueue.ts`, `useSyncQueue.ts`
- AC-DS-03: atributo de calidad — operación sin conexión

---

*Redactado: 2026-04-15 — INC-4.6 documentación transversal*
