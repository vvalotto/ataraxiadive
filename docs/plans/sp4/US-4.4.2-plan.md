# Plan de Implementación — US-4.4.2

**US:** US-4.4.2 — Operación offline del flujo de 6 pasos  
**Incremento:** INC-4.4  
**Sprint:** SP4 — La Plataforma  
**Fecha:** 2026-04-13  
**Branch:** `feature/US-4.4.2-flujo-offline`

---

## Objetivo

Habilitar escritura offline en el flujo del juez:

- encolar comandos cuando no hay red;
- mantener avance del wizard sin interrupciones;
- proyectar estados optimistas en grilla con pendientes.

## Decisiones

1. Introducir `useComandoQueue` como punto único de decisión online/offline.
2. No bloquear UX del flujo: al encolar, se avanza igual de paso.
3. Proyectar estados en `GrillaPage` a partir de la cola (FIFO por `id`).
4. Exponer `pendingCount` en `useConnectionStore`.

## Validación prevista

- `npm run lint`
- `npm run build`
- Smoke manual offline:
  - llamar, resultado, tarjeta y DNS encolan;
  - grilla muestra estados optimistas con `⏳`.

