---
title: "ADR-003: Offline-first PWA + IndexedDB para la interfaz del juez"
type: decision
last_updated: "2026-05-20"
sources:
  - docs/adr/ADR-003-offline-first-pwa.md
estado: Aceptada (implementada en INC-4.4)
fecha: 2026-03-14
bcs_afectados: [competencia]
rnf_refs:
  - RNF-02-disponibilidad-offline-first
  - RNF-03-usabilidad-interfaz-movil-juez
---

# ADR-003: Offline-first PWA + IndexedDB para la interfaz del juez

## Decisión

PWA con Service Worker + IndexedDB para la interfaz del juez. Solo la interfaz del juez opera offline.

## Por qué

- La conectividad en torneos de apnea (piletas, lagos, mar) es frecuentemente inestable o inexistente.
- AC-DS-03: la interfaz del juez **debe funcionar sin conexión**. La competencia no se detiene por el sistema.
- App nativa descartada: requiere publicar en stores y mantener dos codebases.

## Consecuencias vigentes — arquitectura implementada (INC-4.4)

| Hook | Responsabilidad |
|------|----------------|
| `usePrecarga` | Fetch de grilla + estado; caché en `grilla_cache` (IndexedDB); fallback al caché cuando offline |
| `useComandoQueue` | Comandos del juez; encola en `comando_queue` offline; optimistic updates |
| `useSyncQueue` | Drena la cola al reconectar; backoff exponencial; Background Sync API |

- **Dexie.js** como capa de acceso a IndexedDB (ver [[ADR-015-dexie-indexeddb-frontend]]).
- Sincronización: reactiva (hook) + Background Sync API (cuando disponible).
- **iOS/Safari:** Background Sync no disponible en Safari ≤ 17 — fallback reactivo cubre el caso.

## Límites del diseño offline

Solo la interfaz del **juez** opera offline. El resto requiere conexión permanente:
- Pantallas del organizador
- Auditoría y exportación CSV/JSON
- Notificaciones email
- Login / autenticación

## ADRs relacionados

- [[ADR-015-dexie-indexeddb-frontend]] — librería wrapper para IndexedDB
- [[ADR-001-event-sourcing-competencia]] — compatibilidad natural: eventos offline se sincronizan en orden
