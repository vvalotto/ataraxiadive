---
title: "Atributos de Calidad"
type: concepto
last_updated: "2026-05-31"
sources:
  - docs/dominio/03-atributos_calidad.md
rnf_pages:
  - trazabilidad/rnf/RNF-01-confiabilidad-persistencia-event-sourcing
  - trazabilidad/rnf/RNF-02-disponibilidad-offline-first
  - trazabilidad/rnf/RNF-03-usabilidad-interfaz-movil-juez
  - trazabilidad/rnf/RNF-04-configurabilidad-reglas-como-datos
  - trazabilidad/rnf/RNF-05-seguridad-auditoria-inalterable
  - trazabilidad/rnf/RNF-06-escalabilidad-volumen-modesto
  - trazabilidad/rnf/RNF-07-mantenibilidad-sin-desarrollador
  - trazabilidad/rnf/RNF-08-interoperabilidad-exportacion-resultados
---

# Atributos de Calidad

Drivers no funcionales del sistema AtaraxiaDive. Elicitados en febrero 2026 y materializados en las decisiones de arquitectura vigentes.

---

## Rendimiento (Performance)

| Atributo | Valor definido |
|----------|---------------|
| Latencia máxima de acción del juez | **500 ms** |
| Atletas simultáneos en una disciplina | **3** (andariveles) |
| Usuarios concurrentes por torneo | **50** |
| Atletas máximos por torneo | **100** |
| Cálculo de rankings | Al cerrar la disciplina (no en tiempo real) |

**Driver:** la interfaz del juez es el cuello de botella durante ejecución. El juez registra acciones secuenciales críticas sin tolerancia a demoras.

---

## Disponibilidad (Availability)

| Atributo | Valor definido |
|----------|---------------|
| Conectividad en competencias | **Frecuentemente precaria** (piletas, lagos, mar) |
| Modo offline para el juez | **Requerido** |
| Despliegue | **Servidor en la nube** |
| Ventanas de operación | Ventanas específicas (no 24/7) |
| Plan B manual | Registro en papel como contingencia |

**Driver:** la competencia no se detiene por el sistema. El juez debe poder seguir operando sin internet.

**Decisión derivada:** [[ADR-003-offline-first-pwa]] — arquitectura offline-first con sincronización posterior.

---

## Usabilidad (Usability)

| Atributo | Valor definido |
|----------|---------------|
| Dispositivo principal del juez | **Celular** (puede ser tablet) |
| Máximo de acciones para flujo completo del juez | **6 acciones** |
| Condiciones adversas | Sol directo, manos mojadas, guantes |
| Perfil de atletas | **Rango amplio** (jóvenes a adultos mayores) |
| Idioma | Español (con soporte multi-idioma a futuro) |
| Grilla | Planificada antes de competencia; visible en celular |

**Driver:** cada segundo de fricción con la interfaz es riesgo para la integridad de los datos.

---

## Configurabilidad (Configurability)

| Atributo | Quién configura | Alcance |
|----------|----------------|---------|
| Disciplinas | Administrador del sistema | Global |
| Categorías | Administrador del sistema | Global |
| Tarjetas y penalizaciones | Las federaciones definen, el administrador carga | Global |
| Fórmula de cálculo de puntos | Configurable | **Por torneo** |

**Driver:** las reglas del dominio cambian con los reglamentos federativos. El sistema debe absorberlos sin cambios de código.

**Decisión derivada:** [[ADR-004-reglas-como-datos]] — reglas de negocio configurables como datos, no hardcodeadas.

---

## Seguridad (Security)

| Atributo | Valor definido |
|----------|---------------|
| Datos personales de atletas | No se consideran sensibles en esta etapa |
| Log de auditoría de acciones del juez | **Requerido e inalterable** |
| Juez en disciplina no asignada | **Solo lectura** (no puede modificar) |
| Protección contra manipulación de resultados | **Requerida** |
| Delegación de acciones del organizador | No requerida |

**Driver:** la integridad de los resultados es la credibilidad del torneo.

**Decisión derivada:** [[ADR-018-hash-sha256-auditoria]] — integridad criptográfica del event store para auditabilidad inalterable.

---

## Confiabilidad (Reliability)

| Atributo | Valor definido |
|----------|---------------|
| Pérdida de datos al registrar una performance | **Inaceptable** — debe garantizarse la persistencia |
| Confirmación visual al juez después de cada registro | **Requerida** |
| Reconstrucción del estado de competencia desde log | **Requerida** |
| Conflicto entre jueces de andariveles distintos | No es riesgo (sin conflictos esperados) |
| Backup automático durante ejecución | No requerido |

**Driver:** cada performance es un evento único e irrepetible — un dato perdido no puede reconstruirse.

**Decisión derivada:** [[ADR-001-event-sourcing-competencia]] — Event Sourcing en el BC [[competencia]] como garantía de reconstrucción y confiabilidad.

---

## Escalabilidad (Scalability)

| Atributo | Valor definido |
|----------|---------------|
| Torneos por año (inicial) | **4** |
| Horizonte temporal | **5 años** |
| Expansión geográfica | Argentina únicamente (por ahora) |
| Datos históricos | Mantenidos indefinidamente |
| Streaming en vivo para espectadores | No en esta etapa |

**Driver:** el volumen es modesto y predecible. Las decisiones de hoy no deben sobre-diseñar para escala que no existe.

---

## Mantenibilidad (Maintainability)

| Atributo | Valor definido |
|----------|---------------|
| Configuración de reglas sin desarrollador | **Requerida** |
| Frecuencia de cambio de reglamentos | **Muy esporádica** (~cada 2 años) |
| Actualización sin interrumpir torneo en curso | **No requerida** (se actualiza en pausa) |
| Responsable de mantenimiento | Pendiente de definición |

---

## Interoperabilidad (Interoperability)

| Atributo | Estado |
|----------|--------|
| Integración con cronometraje electrónico (touchpads) | Prevista a futuro |
| Exportación de resultados (CSV, JSON, AIDA/CMAS) | **Requerida** |
| Integración con servicios de pago | No requerida por ahora |
| Servicio de notificaciones push | Pendiente (Firebase / OneSignal / otro) |

---

## Mapa de atributos → decisiones arquitectónicas

| Atributo | Página RNF | ADRs derivados | BC principal |
|---|---|---|---|
| Confiabilidad | [[trazabilidad/rnf/RNF-01-confiabilidad-persistencia-event-sourcing\|RNF-01]] | [[ADR-001-event-sourcing-competencia]], [[ADR-008-event-store-sqlite]] | [[competencia]] |
| Disponibilidad | [[trazabilidad/rnf/RNF-02-disponibilidad-offline-first\|RNF-02]] | [[ADR-003-offline-first-pwa]], [[ADR-015-dexie-indexeddb-frontend]] | Todos |
| Usabilidad | [[trazabilidad/rnf/RNF-03-usabilidad-interfaz-movil-juez\|RNF-03]] | [[ADR-003-offline-first-pwa]], [[ADR-015-dexie-indexeddb-frontend]] | Todos |
| Configurabilidad | [[trazabilidad/rnf/RNF-04-configurabilidad-reglas-como-datos\|RNF-04]] | [[ADR-004-reglas-como-datos]] | [[competencia]], [[bc-torneo]] |
| Seguridad | [[trazabilidad/rnf/RNF-05-seguridad-auditoria-inalterable\|RNF-05]] | [[ADR-018-hash-sha256-auditoria]], [[ADR-019-politica-contrasenas]], [[ADR-020-modelo-usuarios-roles]] | [[competencia]], [[identidad]] |
| Escalabilidad | [[trazabilidad/rnf/RNF-06-escalabilidad-volumen-modesto\|RNF-06]] | [[ADR-002-fastapi-backend]], [[ADR-007-sqlite-persistencia-bc]], [[ADR-021-fly-io]] | Todos |
| Mantenibilidad | [[trazabilidad/rnf/RNF-07-mantenibilidad-sin-desarrollador\|RNF-07]] | [[ADR-004-reglas-como-datos]], [[ADR-006-estructura-bc-first]], [[ADR-009-migraciones-por-bc]] | Todos |
| Interoperabilidad | [[trazabilidad/rnf/RNF-08-interoperabilidad-exportacion-resultados\|RNF-08]] | [[ADR-016-resend-email-provider]], [[ADR-017-notificaciones-event-sourcing]] | [[notificaciones]], [[resultados]] |
