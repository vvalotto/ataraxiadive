# Wiki Index — AtaraxiaDive

> Catálogo de todas las páginas del wiki.
> El LLM actualiza este archivo en cada operación de ingest.
> Leer este archivo primero al responder cualquier consulta.

**Última actualización:** 2026-05-30
**Total de páginas:** 305

---

## Estado del wiki

| Sección | Páginas | Estado |
|---------|---------|--------|
| Bounded Contexts | 7 / 7 | ✅ Ingest completo + métricas de salud BL-006 (ArchitectAnalyst + DesignReviewer) |
| Componentes C4 L3 | 41 / ~47 | 🔄 Fases B1–B6 completas (Competencia + Registro + Torneo + Resultados + Identidad + Notificaciones); Fase C pendiente |
| Decisiones (ADRs) | 22 / 22 | ✅ Ingest completo |
| Trazabilidad (US) | 185 | ✅ SP1–SP7 + SP-ADJ-01 a SP-ADJ-11 completos; SP7 INC-7.1 + INC-7.2 cerradas (BL-007, 2026-05-30) |
| Trazabilidad (RF área) | 8 | ✅ 8 páginas de área — tablas con wikilinks `[[RF-XX-NN]]` navegables |
| Trazabilidad (RF individual) | 54 | ✅ 54 páginas en `wiki/trazabilidad/rf/` — cadena RF→US→tests navegable |
| Investigación | 5 | ✅ Ingest completo (HITOs + experimento) |
| Conceptos de dominio | 16 | ✅ 9 originales + 7 nuevos (L6 lint-001 resuelto) |
| Impacto | 4 | ✅ 4 páginas de análisis (L5 lint-001 resuelto) |
| Estado del proyecto | 1 | ✅ Actualizado 2026-05-30 — síntesis BL-000..BL-007, proyecto cerrado (v1.0.2, SP7 completo) |
| Salud / lint | 4 | ✅ calidad-BL-006 + calidad-BL-007 + lint-001 + lint-002 ejecutados |
| Vistas | 7 / 7 | ✅ Fase 2 completa + Fase C plan-c4-nivel3 — vista arquitectura C4 L2+L3 |

---

## Bounded Contexts

| Página | Tipo DDD | Persistencia | Responsabilidad |
|--------|----------|-------------|-----------------|
| [[competencia]] | Core Domain | Event Sourcing | Grilla, performances, tarjetas, trazabilidad deportiva |
| [[bc-torneo]] | Supporting | CRUD | Ciclo de vida del torneo, sede, entidad organizadora |
| [[registro]] | Supporting | CRUD | Atletas, inscripciones, validación de participación |
| [[resultados]] | Supporting | CRUD + stream | Rankings derivados, overall, exportación |
| [[identidad]] | Generic | CRUD | Usuarios, roles, JWT — cross-cutting |
| [[notificaciones]] | Generic | Event Sourcing | Ciclo de vida de notificaciones, exactly-once delivery |
| [[context-map]] | — | — | Integraciones y patrones entre los 6 BCs |

## Decisiones

| Página | Fecha | Estado | BCs afectados |
|--------|-------|--------|---------------|
| [[ADR-001-event-sourcing-competencia]] | 2026-02-10 | Aceptada | competencia |
| [[ADR-002-fastapi-backend]] | 2026-02-12 | Aceptada | todos |
| [[ADR-003-offline-first-pwa]] | 2026-02-15 | Aceptada | — |
| [[ADR-004-reglas-como-datos]] | 2026-02-20 | Aceptada | torneo, competencia |
| [[ADR-005-bounded-contexts-ddd-estrategico]] | 2026-02-24 | Aceptada | todos |
| [[ADR-006-estructura-bc-first]] | 2026-02-27 | Aceptada | todos |
| [[ADR-007-sqlite-persistencia-bc]] | 2026-03-01 | Aceptada | todos |
| [[ADR-008-event-store-sqlite]] | 2026-03-05 | Aceptada | competencia, notificaciones |
| [[ADR-009-migraciones-por-bc]] | 2026-03-10 | Aceptada | todos |
| [[ADR-010-docker-cloud-run]] | 2026-03-12 | **Supersedida** por ADR-021 | — |
| [[ADR-011-structlog-logging]] | 2026-03-15 | Aceptada | todos |
| [[ADR-012-rfc7807-errores-http]] | 2026-03-20 | Aceptada | todos |
| [[ADR-013-exception-management]] | 2026-03-26 | Aceptada | todos |
| [[ADR-014-penalizaciones-acumulables]] | 2026-04-08 | Aceptada | competencia, resultados |
| [[ADR-015-dexie-indexeddb-frontend]] | 2026-04-13 | Aceptada | — |
| [[ADR-016-resend-email-provider]] | 2026-04-16 | Aceptada | notificaciones |
| [[ADR-017-notificaciones-event-sourcing]] | 2026-04-16 | Aceptada | notificaciones |
| [[ADR-018-hash-sha256-auditoria]] | 2026-04-16 | Aceptada | competencia |
| [[ADR-019-politica-contrasenas]] | 2026-04-24 | Aceptada | identidad |
| [[ADR-020-modelo-usuarios-roles]] | 2026-05-16 | Aceptada | identidad, registro |
| [[ADR-021-fly-io]] | 2026-05-17 | Aceptada | todos |
| [[ADR-022-categoria-shared]] | 2026-05-02 | Aceptada | registro, competencia, resultados |

## Trazabilidad

### Semilla de requerimientos funcionales (por área)

Páginas de área — tabla navegable con `[[rf/RF-XX-NN|RF-XX-NN]]` → página individual RF → US → tests.

| Página | Área | RFs | Pendientes |
|--------|------|-----|-----------|
| [[RF-gestion-torneo]] | Gestión del torneo | 7 | 0 |
| [[RF-inscripcion-atletas]] | Inscripción de atletas | 10 | 1 (RF-IN-07) |
| [[RF-preparacion]] | Preparación de competencias | 8 | 0 |
| [[RF-ejecucion]] | Ejecución de competencias | 10 | 1 (RF-EJ-04 códigos de penalización) |
| [[RF-resultados]] | Premiación y resultados | 6 | 1 (RF-PM-01 sistema de puntos) |
| [[RF-usuarios-roles]] | Usuarios, roles y permisos | 5 | 0 |
| [[RF-notificaciones]] | Notificaciones | 4 | 1 (RF-NT-03) |
| [[RF-integracion]] | Integración con sistemas externos | 4 | 4 (toda el área pendiente) |

### Requerimientos funcionales individuales (por RF)

54 páginas en `wiki/trazabilidad/rf/`. Cada página: RF → US que lo implementa → test_units.

**RF-EJ (Ejecución):** [[RF-EJ-01-multiples-jueces-por-disciplina]] · [[RF-EJ-02-registro-dns-no-presentado]] · [[RF-EJ-03-tarjeta-amarilla-penalizacion-parcial]] · [[RF-EJ-04-codigos-de-penalizacion]] · [[RF-EJ-05-cronometraje-manual-por-juez]] · [[RF-EJ-06-correccion-resultado-registrado]] · [[RF-EJ-07-registro-black-out-distancia]] · [[RF-EJ-08-distancias-con-decimales]] · [[RF-EJ-09-protocolo-superficie-manual]] · [[RF-EJ-10-efecto-sp-registrado-como-tarjeta]]

**RF-GT (Gestión Torneo):** [[RF-GT-01-sede-unica-por-torneo]] · [[RF-GT-02-disciplinas-configurables]] · [[RF-GT-03-torneos-activos-simultaneos]] · [[RF-GT-04-cancelacion-conserva-datos]] · [[RF-GT-05-transiciones-ciclo-vida-torneo]] · [[RF-GT-06-cierre-sin-exportacion-automatica]] · [[RF-GT-07-entidad-organizadora-registrada]]

**RF-IG (Integración):** [[RF-IG-01-integracion-bd-externa-faas]] · [[RF-IG-02-consulta-bd-externa-solo-lectura]] · [[RF-IG-03-disponibilidad-bd-externa]] · [[RF-IG-04-exportacion-resultados-externos]]

**RF-IN (Inscripción):** [[RF-IN-01-categorias-configurables]] · [[RF-IN-02-brevet-opcional]] · [[RF-IN-03-sin-limite-atletas]] · [[RF-IN-04-cancelacion-inscripcion-atleta]] · [[RF-IN-05-apto-medico-requerido]] · [[RF-IN-06-constancia-pago-inscripcion]] · [[RF-IN-07-conflicto-datos-bd-externa]] · [[RF-IN-08-genero-efecto-en-categoria]] · [[RF-IN-09-categoria-unica-por-torneo]] · [[RF-IN-10-club-atleta-obligatorio]]

**RF-NT (Notificaciones):** [[RF-NT-01-canales-notificacion-email-push]] · [[RF-NT-02-notificacion-limite-anuncios]] · [[RF-NT-03-notificaciones-durante-ejecucion]] · [[RF-NT-04-notificacion-resultados-publicados]]

**RF-PM (Premiación/Resultados):** [[RF-PM-01-resultados-por-puntos-faas]] · [[RF-PM-02-ranking-general-overall]] · [[RF-PM-03-resolucion-empates]] · [[RF-PM-04-certificados-logos-firmas]] · [[RF-PM-05-rankings-por-categoria-y-genero]] · [[RF-PM-06-publicacion-resultados-descargables]]

**RF-PR (Preparación):** [[RF-PR-01-anuncio-previo-ap]] · [[RF-PR-02-validacion-valores-ap]] · [[RF-PR-03-ap-definitivo-sin-modificacion]] · [[RF-PR-04-atleta-sin-ap-no-compite]] · [[RF-PR-05-orden-salida-por-ap]] · [[RF-PR-06-competencia-multi-andarivel]] · [[RF-PR-07-ajuste-manual-grilla]] · [[RF-PR-08-intervalo-ot-entre-performances]]

**RF-US (Usuarios/Roles):** [[RF-US-01-organizador-unico-por-torneo]] · [[RF-US-02-usuario-multiples-roles]] · [[RF-US-03-autenticacion-email-contrasena]] · [[RF-US-04-asignacion-juez-a-disciplinas]] · [[RF-US-05-resultados-visibles-post-competencia]]

### Trazabilidad por US

#### SP1 (INC-1.1 a INC-1.4)

[[US-1.1.1-setup-esqueleto-bc-competencia]] · [[US-1.2.1-registrar-ap]] [[US-1.2.2-llamar-atleta]] [[US-1.2.3-registrar-resultado]] [[US-1.2.4-asignar-tarjeta-blanca-roja]] [[US-1.2.5-registrar-dns]] [[US-1.2.6-corregir-resultado]] · [[US-1.3.1-read-models-performance-actual-proximos-atletas]] · [[US-1.4.1-asignar-tarjeta-roja-black-out-con-distancia]] [[US-1.4.2-flujo-e2e-audit-log-get-events]]

#### SP-ADJ-01

[[US-ADJ-1.1-refactoring-domain-ot-programado-event-handlers-snake]] [[US-ADJ-1.2-refactoring-domain-helpers-recalcular-ots-aplicar-swap]] [[US-ADJ-1.3-refactoring-application-stream-ids-py-fuente-unica]] [[US-ADJ-1.4-refactoring-api-dip-en-router-p-08-a-composition-root]] [[US-ADJ-1.5-refactoring-api-srp-router-en-schemas-py-dependencies]]

#### SP-ADJ-02

[[US-ADJ-2.6-refactoring-cross-bc-v-os-y-event-store-a-shared]] [[US-ADJ-2.7-refactoring-eliminar-codigo-muerto-get-on-finalizada]] [[US-ADJ-2.8-refactoring-api-dip-fix-event-store-dep-tipado-como]]

#### SP2 (INC-2.0 a INC-2.4)

[[US-2.0-exception-management-cross-bc]] · [[US-2.1.1-configurar-intervalo-ot-scaffold-aggregate-competencia]] [[US-2.1.2-generar-grilla-regenerar-grilla]] [[US-2.1.3-ajustar-grilla]] [[US-2.1.4-confirmar-grilla-iniciar-competencia]] · [[US-2.2.1-disciplina-descriptor-value-object-port]] [[US-2.2.2-api-disciplina-aware-validacion-de-unidades]] · [[US-2.3.1-ejecucion-multi-andarivel]] · [[US-2.4.1-competencia-finalizada-automatico-politica-p-08]] [[US-2.4.2-calcular-ranking-—-bc-resultados-nucleo]]

#### SP-ADJ-03

[[US-ADJ-3.1-extraer-grilla-de-salida-vo-eliminar-disciplinas-sp3]] [[US-ADJ-3.2-extraer-tarjeta-asignacion-vo]] [[US-ADJ-3.3-refactorizar-build-app-constante-event-type]] [[US-ADJ-3.4-mover-deps-auth-a-shared-api-dependencies-py-dip-cross]] [[US-ADJ-3.5-limpiar-imports-cross-module-en-ports-de-competencia]] [[US-ADJ-3.6-token-service-port-password-hashing-port-dip-en]] [[US-ADJ-3.7-proyeccion-competencias-por-torneo-o-n-o-1]] [[US-ADJ-3.8-desacoplar-acl-resultados-de-bc-competencia]]

#### SP-ADJ-04

[[US-ADJ-4.1-renombrar-dynb-dbf-y-spe2x50-spe-acronimos-dominio-real]] [[US-ADJ-4.2-corregir-orden-grilla-sta-ascendente]] [[US-ADJ-4.3-renombrar-juvenil-junior-en-enum-categoria]] [[US-ADJ-4.4-agregar-campo-club-a-aggregate-atleta]] [[US-ADJ-4.5-ranking-por-disciplina-categoria-en-bc-resultados]] [[US-ADJ-4.6-value-object-tiempo-ap-parsear-mm-ss-segundos]]

#### SP3 (INC-3.1 a INC-3.5)

[[US-3.1.1-aggregate-torneo-maquina-de-estados]] [[US-3.1.2-api-rest-torneo-crud-transiciones-repositorio-sq-lite]] · [[US-3.2.1-bc-identidad-usuario-jwt-minimo-auth]] [[US-3.2.2-aggregate-atleta-registro-consulta-y-repositorio-sq]] [[US-3.2.3-aggregate-inscripcion-inscribir-cancelar-y-listar]] · [[US-3.3.1-torneo-id-opcional-en-competencia-para-overall]] [[US-3.3.2-acl-torneo-registro-competencia-crear-competencias-por]] · [[US-3.4.1-asignar-disciplinas-asignar-juez-en-torneo]] [[US-3.4.2-auth-por-rol-en-ap-is-escribibles-con-jwt-middleware]] · [[US-3.5.1-aggregate-ranking-overall-calcular-overall-handler]] [[US-3.5.2-politica-p-09-overall-automatico-al-cerrar-torneo]] [[US-3.5.3-api-get-resultados-{torneo-id}-overall]]

#### SP4 (INC-4.1 a INC-4.6)

[[US-4.1.1-motivo-dq-str-enum-tarjeta-asignacion-extendida-brecha]] [[US-4.1.2-tipo-tarjeta-blanca-con-penalizaciones-penalizacion]] [[US-4.1.3-subdisciplinas-spe-spe-2x50-spe-4x50-spe-8x50-spe-16x50]] [[US-4.1.4-orden-spe-descendente-en-grilla-de-salida]] [[US-4.1.5-descomponer-aggregate-performance-en-modulos]] [[US-4.1.6-handler-utils-py-helpers-comunes-para-handlers]] [[US-4.1.7-descomponer-grilla-de-salida-ajustar-y-ranking]] [[US-4.1.8-limpieza-torneo-sq-lite-torneo-repository-disciplina]] · [[US-4.2.1-scaffold-frontend-vite-react-type-script-pwa]] [[US-4.2.2-auth-store-login-routing-guards-de-rol]] · [[US-4.3.1-mis-disciplinas-juez-vista-real-en-react]] [[US-4.3.2-grilla-page-operativa-wizard-movil-de-performance]] [[US-4.3.3-wizard-extendido-dns-bko-tarjeta-roja-con-motivo-dq-y]] [[US-4.3.4-estado-en-revision-resolver-revision-ui-tarjeta]] [[US-4.3.5-adaptacion-wizard-para-sta-vias-respiratorias]] · [[US-4.4.1-dexie-js-cache-local-de-grilla-expiracion-24h]] [[US-4.4.2-use-comando-queue-cola-offline-estado-optimista-en]] [[US-4.4.3-service-worker-con-background-sync-sync-status-badge]] · [[US-4.5.1-aggregate-notificacion-ciclo-de-vida-idempotencia]] [[US-4.5.2-email-port-resend-email-adapter]] [[US-4.5.3-politica-p-10-email-al-atleta-al-confirmar-inscripcion]] [[US-4.5.4-politica-p-11-email-a-atletas-al-publicar-resultados]] [[US-4.5.5-cableado-p-10-al-endpoint-post-registro-inscripciones]] · [[US-4.6.1-obtener-audit-log-por-performance]] [[US-4.6.2-calculador-hash-competencia-hash-sha-256-de-integridad]] [[US-4.6.3-ui-auditoria-para-organizador-timeline-hash]] [[US-4.6.4-exportar-resultados-descarga-csv-json-del-torneo]]

#### SP-ADJ-05

[[US-ADJ-5.1-poda-metodologica-clasificar-artefactos-artefactos]] [[US-ADJ-5.2-consistencia-documental-residual-readme-docker-compose]] [[US-ADJ-5.3-marcar-madurez-de-b-cs-en-context-map]] [[US-ADJ-5.4-marcar-vigencia-de-documentos-historicos-fundacionales]] [[US-ADJ-5.5-corregir-deuda-tooling-claude-tracking]]

#### SP-ADJ-06

[[US-ADJ-6.1-renombrar-faz-faas-en-codigo]] [[US-ADJ-6.2-renombrar-faz-faas-en-tests]] [[US-ADJ-6.3-eliminar-inspect-signature-callback-on-finalizada]] [[US-ADJ-6.4-eliminar-duplicacion-p-10-p-11-y-staticmethod]] [[US-ADJ-6.5-corregir-violaciones-de-capa-en-grilla-page-frontend]] [[US-ADJ-6.6-correccion-acronimo-faz-faas-en-documentacion]] [[US-ADJ-6.7-uat-sp4-inc-4-4-4-5-4-6-bug-sp4-001-002-ux-fixes]]

#### SP-ADJ-07

[[US-ADJ-7.1-bug-sp4-003-corregir-resultado-tras-dns]] [[US-ADJ-7.2-bug-sp4-004-exponer-tarjeta-asignada-en-grilla]] [[US-ADJ-7.3-scope-sp4-001-cablear-p-11-a-competencia-finalizada]]

#### SP5 — Panel Organizador (INC-5.1)

[[US-5.1.1-crear-torneo-page-formulario-de-creacion-para-el]] [[US-5.1.2-detalle-torneo-page-tabs-y-panel-de-acciones-de-fase]] [[US-5.1.3-inscriptos-panel-lista-de-atletas-con-estado-ap]] [[US-5.1.4-grilla-panel-generar-y-confirmar-grilla-por-disciplina]] [[US-5.1.5-jueces-panel-asignacion-de-juez-por-disciplina]] [[US-5.1.6-ejecucion-panel-monitor-de-competencias-activas]]

#### SP5 — INC-5.1-ADJ (ajuste post-UAT)

[[US-5.1.7-politica-de-tabs-por-fase-en-detalle-torneo-page]] [[US-5.1.8-torneo-competencias-page-composicion-disciplinas]] [[US-5.1.9-precondicion-de-grilla-para-asignacion-de-juez]] [[US-5.1.10-normalizacion-del-campo-estado-en-fetch-torneo]]

#### SP5 — Ejecución por Disciplina (INC-5.2)

[[US-5.2.1-torneo-competencias-page-maestro-detalle-por-disciplina]] [[US-5.2.2-accion-finalizar-prueba-por-disciplina]]

#### SP-ADJ-08

[[US-ADJ-8.1-sp-adj-08-ux-paneles-organizador-post-uat-inc-5-2]] [[US-ADJ-8.2-sp-adj-08-selector-de-grilla-filtrado-y-transicion-a]] [[US-ADJ-8.3-sp-adj-08-cancelar-torneo-con-confirmacion-fuerte]]

#### SP5 — Gestión de Usuarios (INC-5.3)

[[US-5.3.1-usuarios-page-gestion-de-usuarios-para-el-organizador]] [[US-5.3.2-atleta-dashboard-page-perfil-inscripcion-a-torneos]]

#### SP5 — Identidad Extendida (INC-5.4)

[[US-5.4.1-auto-registro-publico-de-usuarios]] [[US-5.4.2-cambiar-contrasena-para-usuario-autenticado]] [[US-5.4.3-recuperar-contrasena-via-token-jwt]]

#### SP5 — Portal Atleta e Inscripción con AP (INC-5.5)

[[US-5.5.1-portal-atleta-completo-shell-inscripcion-ap]] [[US-5.5.2-vista-organizador-inscriptos-con-datos-completos-y]]

#### SP5 — Algoritmo de Puntaje y Rankings (INC-5.6)

[[US-5.6.1-puerto-algoritmo-puntaje-implementacion-faas]] [[US-5.6.2-tipo-reglamento-en-torneo-di-en-calcular-ranking]] [[US-5.6.3-ranking-competencia-con-puntos-por-categoria]] [[US-5.6.4-ranking-overall-puntos-acumulados-por-categoria-y]] [[US-5.6.5-ui-resultados-page-tabla-de-resultados-por-disciplina]] [[US-5.6.6-ui-podios-por-division-6-divisiones-fijas]]

#### SP-ADJ-09

[[US-ADJ-9.1-sp-adj-09-shell-dark-del-portal-organizador]] [[US-ADJ-9.2-sp-adj-09-routing-organizador-reestructurado]] [[US-ADJ-9.3-sp-adj-09-home-del-organizador-formalizado]] [[US-ADJ-9.4-sp-adj-09-dashboard-operativo-del-torneo-en-ejecucion]] [[US-ADJ-9.5-sp-adj-09-resultados-page-integrada-en-el-panel]] [[US-ADJ-9.6-sp-adj-09-arquitectura-ux-organizador-formalizada]] [[US-ADJ-9.7-sp-adj-09-declarar-ap-en-el-wizard-de-inscripcion]]

#### SP5 — Portal del Atleta (INC-5.7)

[[US-5.7.1-mis-torneos-lista-de-torneos-inscriptos-del-atleta]] [[US-5.7.2-mi-grilla-posicion-del-atleta-por-disciplina]] [[US-5.7.3-mis-resultados-result-hero-disciplina-pendiente-card]] [[US-5.7.4-rankings-y-podios-para-el-atleta]]

#### SP6 — Ajustes Juez (INC-6.1)

[[US-6.1.1-fix-can-submit-bko-reorden-flujo-juez-tarjeta-marca]] [[US-6.1.2-colores-tarjeta-outline-filled-heading-paso-5-corregido]] [[US-6.1.3-grilla-ordenada-por-estado-keypad-visible-en-movil]] [[US-6.1.4-rediseno-inicio-juez-sta-mm-ss-tarjeta-amarilla]] [[US-6.1.5-atleta-card-compacta-en-paso-de-rp-selector]]

#### SP6 — Ajustes Organizador (INC-6.2)

[[US-6.2.1-torneos-ordenados-por-fecha-desc-en-lista-organizador]] [[US-6.2.2-inscriptos-y-grilla-columna-categoria-legible-titulo]] [[US-6.2.3-resultados-page-quitar-pts-faas-andarivel-como-numero]] [[US-6.2.4-panel-torneo-alertas-sin-boton-resolver-jueces-sin]] [[US-6.2.5-nuevo-torneo-con-grupos-etarios-junior-senior-master]] [[US-6.2.6-podios-page-para-el-organizador]]

#### SP6 — Ajustes Atleta (INC-6.3)

[[US-6.3.1-inicio-atleta-indicador-en-linea-disciplinas-por-ot]] [[US-6.3.2-inscripcion-atleta-ap-inline-apto-medico-constancia]]

#### SP6 — Deuda Técnica Sistema (INC-6.4)

[[US-6.4.1-romper-ciclo-adp-en-competencia-domain-aggregates]] [[US-6.4.2-materializar-proyeccion-competencias-por-torneo-en]] [[US-6.4.3-corregir-d-05-imports-cross-bc-en-resultados-api-y]] [[US-6.4.4-refactoring-algoritmo-puntaje-faas-correcciones-code]] [[US-6.4.5-refactoring-declarar-ap-inscripcion-handler-sq-lite]] [[US-6.4.6-cierre-arch-03-srp-ranking-competencia-monitoreo]]

#### SP6 — API Pública (INC-6.6)

[[US-6.6.1-endpoint-publico-get-torneos-sin-autenticacion]] [[US-6.6.2-public-torneos-page-pagina-publica-de-lista-de-torneos]] [[US-6.6.3-navegacion-contextual-redirect-post-login-y-root]] [[US-6.6.4-public-torneo-detalle-page-torneo-en-ejecucion-para]]

#### SP-ADJ-10 — Edición de torneo post-cierre

[[US-ADJ-10.1-edicion-completa-del-torneo-put-torneos-{id}]] [[US-ADJ-10.2-pagina-mis-datos-del-atleta-patch-registro-atletas-me]] [[US-ADJ-10.3-email-de-bienvenida-y-auto-login-post-registro]] [[US-ADJ-10.4-vista-post-torneo-en-portal-del-atleta]]

#### SP-ADJ-11 — Modelo de usuarios con múltiples roles

[[US-ADJ-11.1-usuario-roles-list-rol-jwt-rol-activo-login-condicional]] [[US-ADJ-11.2-post-delete-auth-usuarios-me-roles-guard-no-quitar]] [[US-ADJ-11.3-atleta-club-categoria-opcionales-dni-telefono-migracion]] [[US-ADJ-11.4-entidad-juez-juez-repository-port-endpoints-registro]] [[US-ADJ-11.5-entidad-organizador-organizador-repository-port]] [[US-ADJ-11.6-registro-page-checkboxes-multi-rol-secciones-juez]] [[US-ADJ-11.7-login-page-selector-de-rol-cuando-requires-role]] [[US-ADJ-11.8-atleta-mis-datos-page-campos-dni-y-telefono]] [[US-ADJ-11.9-juez-mis-datos-page-organizador-mis-datos-page-rutas]] [[US-ADJ-11.10-creacion-automatica-de-perfiles-al-registrarse]]

#### SP7 — Despliegue (INC-7.1 + INC-7.2)

[[US-7.1.1-dockerfile-fast-api-estaticos-fly-toml-entorno]] [[US-7.1.2-fly-deploy-verificacion-flujos-criticos-tag-v1-0-1]] · [[US-7.2.1-manual-organizador-crear-torneo-inscripciones-grilla]] [[US-7.2.2-manual-juez-panel-flujo-de-performance-6-pasos-tarjetas]] [[US-7.2.3-manual-atleta-registro-inscripcion-ap-consulta-de]]

## Conceptos de dominio

| Página | Descripción |
|--------|-------------|
| [[torneo]] | Evento competitivo central; ciclo de vida y etapas |
| [[disciplina]] | Modalidad de prueba (tiempo o distancia) |
| [[grilla]] | Planilla de salida por disciplina |
| [[performance]] | Actuación de un atleta en una disciplina |
| [[tarjeta]] | Resultado de validez de una performance (blanca/roja) |
| [[anuncio]] | Marca previa declarada por el atleta en Preparación |
| [[atleta]] | Participante del torneo; datos de identidad deportiva |
| [[roles]] | Organizador, Juez, Atleta, Administrador |
| [[atributos-calidad]] | Drivers no funcionales: rendimiento, disponibilidad, usabilidad, confiabilidad, etc. |
| [[inscripcion]] | Aggregate de participación de un atleta en un torneo; estados ACTIVA/CANCELADA |
| [[categoria]] | StrEnum compartido (shared/); clasifica atletas; importado por Registro, Competencia y Resultados |
| [[penalizacion]] | Infracción técnica que reduce RP sin descalificar; introduce BlancaConPenalizaciones |
| [[ranking]] | Ordenamiento de performances; dos tipos: por competencia y overall; separación cálculo/lectura |
| [[dns]] | Did Not Start; evento de atleta no presentado; aparece al final del ranking sin posición |
| [[sede]] | Value object de Torneo; ubicación física del evento (nombre, ciudad, país) |
| [[entidad-organizadora]] | Value object de Torneo; organismo institucional responsable; distinto del rol Organizador |

## Impacto

| Página | Componente | Riesgo |
|--------|-----------|--------|
| [[event-store-port]] | EventStorePort — contrato append-only; 2 BCs Event Sourcing | Muy alto |
| [[atleta-nombre-port]] | AtletaNombrePort / registro.db cross-BC — lectura directa desde Competencia y Resultados | Medio |
| [[categoria-shared]] | Categoria StrEnum — ADR-022 pendiente; imports cross-BC desde Resultados | Medio |
| [[bc-identidad]] | BC Identidad JWT — 3 BCs Conformist; cambio de claims impacta todos | Muy alto |

## Guía de uso

| Página | Descripción |
|--------|-------------|
| [[guia-uso]] | Cómo interactuar con el wiki: consultas, vistas, ingest, lint, triggers y componentes de alto riesgo |

## Estado del proyecto

| Página | Descripción |
|--------|-------------|
| [[proyecto]] | Estado unificado del proyecto — síntesis BL-000..BL-007, proyecto cerrado (v1.0.2), US cerradas |

## Investigación

| Página | Descripción |
|--------|-------------|
| [[iedd-marco-conceptual]] | Modelo de 5 capas IEDD; tesis central; rol de DDD y la IA |
| [[iedd-hipotesis-experimento]] | Hipótesis del ensayo; tabla completa de 22 hipótesis confirmadas; tesis provisional |
| [[uat-metodologia]] | Política de UAT controlado; proceso por fase; vibe coding; datos reales como oráculo |
| [[hitos-catalog]] | Catálogo de 32 HITOs; evidencia empírica del experimento; agrupados por SP y tema |
| [[experimento-plan]] | Plan del experimento; 3 horizontes; jerarquía SP→Incremento→US; capitalización de conocimiento |

## Salud

| Página | Descripción |
|--------|-------------|
| [[calidad-BL-006]] | Snapshot de calidad al cierre de SP6 — 3 gates: DesignReviewer, ArchitectAnalyst, UAT |
| [[calidad-BL-007]] | Snapshot de calidad al cierre de SP7 — cierre del proyecto (v1.0.2) |
| [[lint-002]] | Auditoría post-cierre — 177 wikilinks rotos en Trazabilidad (US), categoría RNF sin documentar |

## Vistas

| Página | Propósito |
|--------|-----------|
| [[dominio]] | El sistema visto desde el negocio y el lenguaje ubicuo |
| [[decisiones]] | El sistema visto desde su historia de razonamiento técnico |
| [[trazabilidad]] | El sistema visto desde los requerimientos hacia la implementación |
| [[impacto]] | El sistema visto desde las dependencias y el riesgo de cambio |
| [[salud]] | El sistema visto desde la deuda técnica y la calidad |
| [[investigacion]] | El sistema visto como fuente de conocimiento intelectual |
| [[arquitectura]] | El sistema visto desde su estructura interna — C4 L2 (BCs) y C4 L3 (componentes) ⏳ pendiente Fase C |

## Planes

| Página | Descripción | Estado |
|--------|-------------|--------|
| [[plan-c4-nivel3]] | Plan de ingest C4 L3 — componentes internos por BC | 🔄 en curso |
| [[plan-trazabilidad-rf-us-si-tu]] | Plan de trazabilidad RF → US → Software Item → Test Unit | ⏳ pendiente |
