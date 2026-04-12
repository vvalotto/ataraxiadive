# Plan de Implementación — US-4.3.4

**US:** US-4.3.4 — Tarjeta amarilla — flujo de revisión y resolución desde la UI  
**Incremento:** INC-4.3  
**Sprint:** SP4 — La Plataforma  
**Fecha:** 2026-04-12  
**Branch:** `feature/US-4.3.4-tarjeta-amarilla`

---

## Objetivo

Convertir la tarjeta amarilla en un estado transitorio real de la performance para que
el juez pueda:

- marcar una performance como `EnRevision`;
- resolverla inmediatamente como blanca o roja;
- o volver a la grilla y resolverla después desde la misma UI.

---

## Alcance real

### Backend

Agregar soporte end-to-end para revisión pendiente:

- nuevo estado `EnRevision` en `EstadoPerformance`;
- cambio de comportamiento en `Performance.asignar_tarjeta(Amarilla)`;
- nuevo evento `RevisionResuelta`;
- nuevo comando `ResolverRevisionCommand`;
- nuevo handler `ResolverRevisionHandler`;
- nuevo endpoint `POST /competencia/{competencia_id}/resolver-revision`.

### Frontend

Extender el flujo actual del juez para soportar:

- selección de tarjeta amarilla en Paso 6;
- pantalla de revisión pendiente con timer informativo;
- resolución inmediata como blanca o roja;
- regreso a grilla con estado `REVISION`;
- reingreso desde grilla a una pantalla de resolución.

---

## Decisiones de alineación con el dominio real

### 1. Amarilla deja de ser estado final

Hoy `AsignarTarjeta(Amarilla)` termina en `Ejecutada`.

Decisión:

- cambiar el dominio para que `Amarilla` deje la performance en `EnRevision`;
- el cierre final se hace solo vía `ResolverRevision(...)`.

### 2. `motivo_texto` para amarilla se conserva

La implementación actual exige `motivo_texto` cuando la tarjeta es amarilla.

Decisión:

- mantener ese requisito por compatibilidad del dominio;
- el frontend enviará un motivo textual mínimo por defecto si la UI no expone edición libre.

### 3. Resolución permitida en esta US

La spec menciona blanca, blanca con penalizaciones y roja.

Decisión:

- para no reabrir más complejidad de la necesaria en esta US, la primera implementación
  resolverá `Blanca` o `Roja`;
- la variante "Blanca con penalizaciones" puede agregarse después si realmente se necesita
  en la misma pantalla de revisión.

### 4. La grilla debe reconocer `EnRevision`

La fila con revisión pendiente debe:

- verse distinta;
- seguir siendo seleccionable;
- navegar al mismo `PerformanceFlowPage` en modo resolución.

No conviene abrir una página nueva separada si el flujo actual ya concentra el estado.

---

## Cambios propuestos

### A. Dominio

Modificar:

- [src/competencia/domain/value_objects/estado_performance.py](/Users/victor/PycharmProjects/ataraxiadive/src/competencia/domain/value_objects/estado_performance.py:1)
- [src/competencia/domain/aggregates/performance.py](/Users/victor/PycharmProjects/ataraxiadive/src/competencia/domain/aggregates/performance.py:1)
- [src/competencia/domain/aggregates/performance_events.py](/Users/victor/PycharmProjects/ataraxiadive/src/competencia/domain/aggregates/performance_events.py:1)

Cambios:

1. agregar `EstadoPerformance.EnRevision`;
2. hacer que `asignar_tarjeta(Amarilla)` deje el aggregate en revisión;
3. agregar `resolver_revision(...)`;
4. registrar evento `RevisionResuelta`;
5. ajustar reconstitución para proyectar correctamente el nuevo estado.

### B. Application

Crear:

- `src/competencia/application/commands/resolver_revision.py`

Cambios:

1. `ResolverRevisionCommand`
2. `ResolverRevisionHandler`
3. misma estrategia de carga/reconstrucción/persistencia que en `AsignarTarjetaHandler`
4. disparar P-08 tras resolver, igual que al asignar tarjeta final

### C. API

Modificar [src/competencia/api/router.py](/Users/victor/PycharmProjects/ataraxiadive/src/competencia/api/router.py:1):

1. agregar body `ResolverRevisionBody`;
2. agregar provider de `ResolverRevisionHandler`;
3. exponer `POST /{competencia_id}/resolver-revision`;
4. mapear errores de dominio a `409` y faltantes a `404`.

### D. Frontend API/store

Modificar:

- [frontend/src/api/competencia.ts](/Users/victor/PycharmProjects/ataraxiadive/frontend/src/api/competencia.ts:1)
- [frontend/src/stores/useCompetenciaStore.ts](/Users/victor/PycharmProjects/ataraxiadive/frontend/src/stores/useCompetenciaStore.ts:1)

Cambios:

1. agregar `resolverRevision(...)`;
2. extender tipos de estado para incluir `EnRevision`;
3. conservar contexto del atleta activo al volver desde la grilla.

### E. UI del juez

Modificar:

- [frontend/src/pages/juez/GrillaPage.tsx](/Users/victor/PycharmProjects/ataraxiadive/frontend/src/pages/juez/GrillaPage.tsx:1)
- [frontend/src/pages/juez/PerformanceFlowPage.tsx](/Users/victor/PycharmProjects/ataraxiadive/frontend/src/pages/juez/PerformanceFlowPage.tsx:1)

Cambios:

1. en Paso 6, agregar CTA `TARJETA AMARILLA`;
2. mostrar estado/pantalla de revisión pendiente;
3. permitir resolver a blanca o roja;
4. bloquear roja sin `MotivoDQ`;
5. volver a grilla conservando `REVISION`;
6. hacer tappable la fila en revisión desde la grilla.

---

## Riesgos

### 1. Reconstitución incompleta del nuevo evento

Si `RevisionResuelta` no se integra bien en la reconstrucción del aggregate, la performance
puede reaparecer en estado incorrecto al consultar grilla o performance actual.

### 2. P-08 puede dispararse antes de tiempo

Si una amarilla sigue siendo considerada finalizada por los adapters de estado, la competencia
podría cerrar indebidamente.

Mitigación:

- verificar que `EnRevision` no cuente como final;
- revisar `PerformancesEstadoAdapter` y consultas derivadas.

### 3. `PerformanceFlowPage` sigue creciendo

La pantalla ya concentra bastante lógica.

Mitigación:

- extraer helpers o sub-secciones si la nueva lógica complica demasiado la lectura;
- evitar duplicar ramas de UI para resolución inmediata y diferida.

---

## Validación prevista

- `npm run build`
- `npm run lint`
- `./.venv/bin/python -m compileall src`
- smoke test backend para `resolver-revision`
- validación manual:
  - amarilla -> blanca inmediata
  - amarilla -> volver a grilla
  - grilla -> retomar revisión
  - amarilla -> roja con motivo

---

## Secuencia de implementación

1. Agregar nuevo estado y evento en dominio.
2. Implementar `resolver_revision` en aggregate y application.
3. Exponer endpoint HTTP.
4. Adaptar query/grilla si el estado nuevo no emerge correctamente.
5. Extender API client y store frontend.
6. Extender `PerformanceFlowPage` y `GrillaPage`.
7. Ejecutar validaciones técnicas.
8. Dejar documentación y reporte final consistentes.

---

*Plan generado: 2026-04-12 — US-4.3.4 INC-4.3 SP4*
