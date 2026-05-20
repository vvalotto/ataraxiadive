---
title: "Atributos de Calidad"
type: concepto
last_updated: "2026-05-20"
sources:
  - docs/dominio/03-atributos_calidad.md
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

| Atributo | ADR derivado | BC principal |
|----------|-------------|-------------|
| Confiabilidad + Reconstrucción | [[ADR-001-event-sourcing-competencia]] | [[competencia]] |
| Offline-first | [[ADR-003-offline-first-pwa]] | Todos |
| Reglas como datos | [[ADR-004-reglas-como-datos]] | [[competencia]], [[torneo]] |
| Persistencia por BC | [[ADR-007-sqlite-persistencia-bc]] | Todos |
| Auditoría inalterable | [[ADR-018-hash-sha256-auditoria]] | [[competencia]] |
| Notificaciones | [[ADR-016-resend-email-provider]], [[ADR-017-notificaciones-event-sourcing]] | [[notificaciones]] |
