# Wiki Index — AtaraxiaDive

> Catálogo de todas las páginas del wiki.
> El LLM actualiza este archivo en cada operación de ingest.
> Leer este archivo primero al responder cualquier consulta.

**Última actualización:** 2026-05-28
**Total de páginas:** 304

---

## Estado del wiki

| Sección | Páginas | Estado |
|---------|---------|--------|
| Bounded Contexts | 7 / 7 | ✅ Ingest completo + métricas de salud BL-006 (ArchitectAnalyst + DesignReviewer) |
| Componentes C4 L3 | 41 / ~47 | 🔄 Fases B1–B6 completas (Competencia + Registro + Torneo + Resultados + Identidad + Notificaciones); Fase C pendiente |
| Decisiones (ADRs) | 22 / 22 | ✅ Ingest completo |
| Trazabilidad (US) | 185 | ✅ SP1–SP7 + SP-ADJ-01 a SP-ADJ-11 completos; SP7 INC-7.1 + INC-7.2 documentados |
| Trazabilidad (RF área) | 8 | ✅ 8 páginas de área — tablas con wikilinks `[[RF-XX-NN]]` navegables |
| Trazabilidad (RF individual) | 54 | ✅ 54 páginas en `wiki/trazabilidad/rf/` — cadena RF→US→tests navegable |
| Investigación | 5 | ✅ Ingest completo (HITOs + experimento) |
| Conceptos de dominio | 16 | ✅ 9 originales + 7 nuevos (L6 lint-001 resuelto) |
| Impacto | 4 | ✅ 4 páginas de análisis (L5 lint-001 resuelto) |
| Estado del proyecto | 1 | ✅ Fase 3 completa — síntesis BL-000..BL-006 + SP7 en curso |
| Salud / lint | 2 | ✅ calidad-BL-006 + lint-001 ejecutado (Fase 4 completa) |
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

[[US-1.1.1-setup-esqueleto-bc-competencia-setup-esqueleto-bc-competencia-setup-esqueleto-bc-competencia]] · [[US-1.2.1-registrarap-registrarap-registrarap]] [[US-1.2.2-llamaratleta-llamaratleta-llamaratleta]] [[US-1.2.3-registrarresultado-registrarresultado-registrarresultado]] [[US-1.2.4-asignartarjeta-blanca-roja-asignartarjeta-blanca-roja-asignartarjeta-blanca-roja]] [[US-1.2.5-registrardns-registrardns-registrardns]] [[US-1.2.6-corregirresultado-corregirresultado-corregirresultado]] · [[US-1.3.1-read-models-performanceactual-proximosatletas-read-models-performanceactual-proximosatletas-read-models-performanceactual-proximosatletas]] · [[US-1.4.1-asignartarjeta-roja-black-out-con-distancia-asignartarjeta-roja-black-out-con-distancia-asignartarjeta-roja-black-out-con-distancia]] [[US-1.4.2-flujo-e2e-audit-log-get-events-flujo-e2e-audit-log-get-events-flujo-e2e-audit-log-get-events]]

#### SP-ADJ-01

[[US-ADJ-1.1-refactoring-domain-ot-programado-event-handlers-snake-refactoring-domain-ot-programado-event-handlers-snake-refactoring-domain-ot-programado-event-handlers-snake]] [[US-ADJ-1.2-refactoring-domain-helpers-recalcular-ots-aplicar-swap-refactoring-domain-helpers-recalcular-ots-aplicar-swap-refactoring-domain-helpers-recalcular-ots-aplicar-swap]] [[US-ADJ-1.3-refactoring-application-stream-ids-py-fuente-unica-refactoring-application-stream-ids-py-fuente-unica-refactoring-application-stream-ids-py-fuente-unica]] [[US-ADJ-1.4-refactoring-api-dip-en-router-p-08-a-composition-root-refactoring-api-dip-en-router-p-08-a-composition-root-refactoring-api-dip-en-router-p-08-a-composition-root]] [[US-ADJ-1.5-refactoring-api-srp-router-en-schemas-py-dependencies-refactoring-api-srp-router-en-schemas-py-dependencies-refactoring-api-srp-router-en-schemas-py-dependencies]]

#### SP-ADJ-02

[[US-ADJ-2.6-refactoring-cross-bc-vos-y-eventstore-a-shared-refactoring-cross-bc-vos-y-eventstore-a-shared-refactoring-cross-bc-vos-y-eventstore-a-shared]] [[US-ADJ-2.7-refactoring-eliminar-codigo-muerto-get-on-finalizada-refactoring-eliminar-codigo-muerto-get-on-finalizada-refactoring-eliminar-codigo-muerto-get-on-finalizada]] [[US-ADJ-2.8-refactoring-api-dip-fix-eventstoredep-tipado-como-refactoring-api-dip-fix-eventstoredep-tipado-como-refactoring-api-dip-fix-eventstoredep-tipado-como]]

#### SP2 (INC-2.0 a INC-2.4)

[[US-2.0-exception-management-cross-bc-exception-management-cross-bc-exception-management-cross-bc]] · [[US-2.1.1-configurarintervaloot-scaffold-aggregate-competencia-configurarintervaloot-scaffold-aggregate-competencia-configurarintervaloot-scaffold-aggregate-competencia]] [[US-2.1.2-generargrilla-regenerargrilla-generargrilla-regenerargrilla-generargrilla-regenerargrilla]] [[US-2.1.3-ajustargrilla-ajustargrilla-ajustargrilla]] [[US-2.1.4-confirmargrilla-iniciarcompetencia-confirmargrilla-iniciarcompetencia-confirmargrilla-iniciarcompetencia]] · [[US-2.2.1-disciplinadescriptor-value-object-port-disciplinadescriptor-value-object-port-disciplinadescriptor-value-object-port]] [[US-2.2.2-api-disciplina-aware-validacion-de-unidades-api-disciplina-aware-validacion-de-unidades-api-disciplina-aware-validacion-de-unidades]] · [[US-2.3.1-ejecucion-multi-andarivel-ejecucion-multi-andarivel-ejecucion-multi-andarivel]] · [[US-2.4.1-competenciafinalizada-automatico-politica-p-08-competenciafinalizada-automatico-politica-p-08-competenciafinalizada-automatico-politica-p-08]] [[US-2.4.2-calcularranking-—-bc-resultados-nucleo-calcularranking-—-bc-resultados-nucleo-calcularranking-—-bc-resultados-nucleo]]

#### SP-ADJ-03

[[US-ADJ-3.1-extraer-grilladesalida-vo-eliminar-disciplinas-sp3-extraer-grilladesalida-vo-eliminar-disciplinas-sp3-extraer-grilladesalida-vo-eliminar-disciplinas-sp3]] [[US-ADJ-3.2-extraer-tarjetaasignacion-vo-extraer-tarjetaasignacion-vo-extraer-tarjetaasignacion-vo]] [[US-ADJ-3.3-refactorizar-build-app-constante-event-type-refactorizar-build-app-constante-event-type-refactorizar-build-app-constante-event-type]] [[US-ADJ-3.4-mover-deps-auth-a-shared-api-dependencies-py-dip-cross-mover-deps-auth-a-shared-api-dependencies-py-dip-cross-mover-deps-auth-a-shared-api-dependencies-py-dip-cross]] [[US-ADJ-3.5-limpiar-imports-cross-module-en-ports-de-competencia-limpiar-imports-cross-module-en-ports-de-competencia-limpiar-imports-cross-module-en-ports-de-competencia]] [[US-ADJ-3.6-tokenserviceport-passwordhashingport-dip-en-identidad-tokenserviceport-passwordhashingport-dip-en-identidad-tokenserviceport-passwordhashingport-dip-en-identidad]] [[US-ADJ-3.7-proyeccion-competencias-por-torneo-o-n-o-1-proyeccion-competencias-por-torneo-o-n-o-1-proyeccion-competencias-por-torneo-o-n-o-1]] [[US-ADJ-3.8-desacoplar-acl-resultados-de-bc-competencia-desacoplar-acl-resultados-de-bc-competencia-desacoplar-acl-resultados-de-bc-competencia]]

#### SP-ADJ-04

[[US-ADJ-4.1-renombrar-dynb-dbf-y-spe2x50-spe-acronimos-dominio-real-renombrar-dynb-dbf-y-spe2x50-spe-acronimos-dominio-real-renombrar-dynb-dbf-y-spe2x50-spe-acronimos-dominio-real]] [[US-ADJ-4.2-corregir-orden-grilla-sta-ascendente-corregir-orden-grilla-sta-ascendente-corregir-orden-grilla-sta-ascendente]] [[US-ADJ-4.3-renombrar-juvenil-junior-en-enum-categoria-renombrar-juvenil-junior-en-enum-categoria-renombrar-juvenil-junior-en-enum-categoria]] [[US-ADJ-4.4-agregar-campo-club-a-aggregate-atleta-agregar-campo-club-a-aggregate-atleta-agregar-campo-club-a-aggregate-atleta]] [[US-ADJ-4.5-ranking-por-disciplina-categoria-en-bc-resultados-ranking-por-disciplina-categoria-en-bc-resultados-ranking-por-disciplina-categoria-en-bc-resultados]] [[US-ADJ-4.6-value-object-tiempoap-parsear-mm-ss-segundos-value-object-tiempoap-parsear-mm-ss-segundos-value-object-tiempoap-parsear-mm-ss-segundos]]

#### SP3 (INC-3.1 a INC-3.5)

[[US-3.1.1-aggregate-torneo-maquina-de-estados-aggregate-torneo-maquina-de-estados-aggregate-torneo-maquina-de-estados]] [[US-3.1.2-api-rest-torneo-crud-transiciones-repositorio-sqlite-api-rest-torneo-crud-transiciones-repositorio-sqlite-api-rest-torneo-crud-transiciones-repositorio-sqlite]] · [[US-3.2.1-bc-identidad-usuario-jwt-minimo-auth-bc-identidad-usuario-jwt-minimo-auth-bc-identidad-usuario-jwt-minimo-auth]] [[US-3.2.2-aggregate-atleta-registro-consulta-y-repositorio-sqlite-aggregate-atleta-registro-consulta-y-repositorio-sqlite-aggregate-atleta-registro-consulta-y-repositorio-sqlite]] [[US-3.2.3-aggregate-inscripcion-inscribir-cancelar-y-listar-aggregate-inscripcion-inscribir-cancelar-y-listar-aggregate-inscripcion-inscribir-cancelar-y-listar]] · [[US-3.3.1-torneo-id-opcional-en-competencia-para-overall-torneo-id-opcional-en-competencia-para-overall-torneo-id-opcional-en-competencia-para-overall]] [[US-3.3.2-acl-torneo-registro-competencia-crear-competencias-por-acl-torneo-registro-competencia-crear-competencias-por-acl-torneo-registro-competencia-crear-competencias-por]] · [[US-3.4.1-asignardisciplinas-asignarjuez-en-torneo-asignardisciplinas-asignarjuez-en-torneo-asignardisciplinas-asignarjuez-en-torneo]] [[US-3.4.2-auth-por-rol-en-apis-escribibles-con-jwt-middleware-auth-por-rol-en-apis-escribibles-con-jwt-middleware-auth-por-rol-en-apis-escribibles-con-jwt-middleware]] · [[US-3.5.1-aggregate-rankingoverall-calcularoverallhandler-aggregate-rankingoverall-calcularoverallhandler-aggregate-rankingoverall-calcularoverallhandler]] [[US-3.5.2-politica-p-09-overall-automatico-al-cerrar-torneo-politica-p-09-overall-automatico-al-cerrar-torneo-politica-p-09-overall-automatico-al-cerrar-torneo]] [[US-3.5.3-api-get-resultados-{torneo-id}-overall-api-get-resultados-{torneo-id}-overall-api-get-resultados-{torneo-id}-overall]]

#### SP4 (INC-4.1 a INC-4.6)

[[US-4.1.1-motivodq-strenum-tarjetaasignacion-extendida-brecha-motivodq-strenum-tarjetaasignacion-extendida-brecha-motivodq-strenum-tarjetaasignacion-extendida-brecha]] [[US-4.1.2-tipotarjeta-blancaconpenalizaciones-tipotarjeta-blancaconpenalizaciones-tipotarjeta-blancaconpenalizaciones]] [[US-4.1.3-subdisciplinas-spe-spe-2x50-spe-4x50-spe-8x50-spe-16x50-subdisciplinas-spe-spe-2x50-spe-4x50-spe-8x50-spe-16x50-subdisciplinas-spe-spe-2x50-spe-4x50-spe-8x50-spe-16x50]] [[US-4.1.4-orden-spe-descendente-en-grilladesalida-orden-spe-descendente-en-grilladesalida-orden-spe-descendente-en-grilladesalida]] [[US-4.1.5-descomponer-aggregate-performance-en-modulos-descomponer-aggregate-performance-en-modulos-descomponer-aggregate-performance-en-modulos]] [[US-4.1.6-handler-utils-py-helpers-comunes-para-handlers-handler-utils-py-helpers-comunes-para-handlers-handler-utils-py-helpers-comunes-para-handlers]] [[US-4.1.7-descomponer-grilladesalida-ajustar-y-rankingcompetencia-descomponer-grilladesalida-ajustar-y-rankingcompetencia-descomponer-grilladesalida-ajustar-y-rankingcompetencia]] [[US-4.1.8-limpieza-torneo-sqlitetorneorepository-limpieza-torneo-sqlitetorneorepository-limpieza-torneo-sqlitetorneorepository]] · [[US-4.2.1-scaffold-frontend-vite-react-typescript-pwa-scaffold-frontend-vite-react-typescript-pwa-scaffold-frontend-vite-react-typescript-pwa]] [[US-4.2.2-auth-store-login-routing-guards-de-rol-auth-store-login-routing-guards-de-rol-auth-store-login-routing-guards-de-rol]] · [[US-4.3.1-misdisciplinas-juez-vista-real-en-react-misdisciplinas-juez-vista-real-en-react-misdisciplinas-juez-vista-real-en-react]] [[US-4.3.2-grillapage-operativa-wizard-movil-de-performance-grillapage-operativa-wizard-movil-de-performance-grillapage-operativa-wizard-movil-de-performance]] [[US-4.3.3-wizard-extendido-dns-bko-tarjeta-roja-con-motivodq-y-wizard-extendido-dns-bko-tarjeta-roja-con-motivodq-y-wizard-extendido-dns-bko-tarjeta-roja-con-motivodq-y]] [[US-4.3.4-estado-enrevision-resolverrevision-ui-tarjeta-amarilla-estado-enrevision-resolverrevision-ui-tarjeta-amarilla-estado-enrevision-resolverrevision-ui-tarjeta-amarilla]] [[US-4.3.5-adaptacion-wizard-para-sta-vias-respiratorias-adaptacion-wizard-para-sta-vias-respiratorias-adaptacion-wizard-para-sta-vias-respiratorias]] · [[US-4.4.1-dexie-js-cache-local-de-grilla-expiracion-24h-dexie-js-cache-local-de-grilla-expiracion-24h-dexie-js-cache-local-de-grilla-expiracion-24h]] [[US-4.4.2-usecomandoqueue-cola-offline-estado-optimista-en-grilla-usecomandoqueue-cola-offline-estado-optimista-en-grilla-usecomandoqueue-cola-offline-estado-optimista-en-grilla]] [[US-4.4.3-service-worker-con-background-sync-syncstatusbadge-service-worker-con-background-sync-syncstatusbadge-service-worker-con-background-sync-syncstatusbadge]] · [[US-4.5.1-aggregate-notificacion-ciclo-de-vida-idempotencia-aggregate-notificacion-ciclo-de-vida-idempotencia-aggregate-notificacion-ciclo-de-vida-idempotencia]] [[US-4.5.2-emailport-resendemailadapter-emailport-resendemailadapter-emailport-resendemailadapter]] [[US-4.5.3-politica-p-10-email-al-atleta-al-confirmar-inscripcion-politica-p-10-email-al-atleta-al-confirmar-inscripcion-politica-p-10-email-al-atleta-al-confirmar-inscripcion]] [[US-4.5.4-politica-p-11-email-a-atletas-al-publicar-resultados-politica-p-11-email-a-atletas-al-publicar-resultados-politica-p-11-email-a-atletas-al-publicar-resultados]] [[US-4.5.5-cableado-p-10-al-endpoint-post-registro-inscripciones-cableado-p-10-al-endpoint-post-registro-inscripciones-cableado-p-10-al-endpoint-post-registro-inscripciones]] · [[US-4.6.1-obtenerauditlog-por-performance-obtenerauditlog-por-performance-obtenerauditlog-por-performance]] [[US-4.6.2-calculadorhashcompetencia-hash-sha-256-de-integridad-calculadorhashcompetencia-hash-sha-256-de-integridad-calculadorhashcompetencia-hash-sha-256-de-integridad]] [[US-4.6.3-ui-auditoria-para-organizador-timeline-hash-ui-auditoria-para-organizador-timeline-hash-ui-auditoria-para-organizador-timeline-hash]] [[US-4.6.4-exportarresultados-descarga-csv-json-del-torneo-exportarresultados-descarga-csv-json-del-torneo-exportarresultados-descarga-csv-json-del-torneo]]

#### SP-ADJ-05

[[US-ADJ-5.1-poda-metodologica-clasificar-artefactos-artefactos-poda-metodologica-clasificar-artefactos-artefactos-poda-metodologica-clasificar-artefactos-artefactos]] [[US-ADJ-5.2-consistencia-documental-residual-readme-docker-compose-consistencia-documental-residual-readme-docker-compose-consistencia-documental-residual-readme-docker-compose]] [[US-ADJ-5.3-marcar-madurez-de-bcs-en-context-map-marcar-madurez-de-bcs-en-context-map-marcar-madurez-de-bcs-en-context-map]] [[US-ADJ-5.4-marcar-vigencia-de-documentos-historicos-fundacionales-marcar-vigencia-de-documentos-historicos-fundacionales-marcar-vigencia-de-documentos-historicos-fundacionales]] [[US-ADJ-5.5-corregir-deuda-tooling-claude-tracking-corregir-deuda-tooling-claude-tracking-corregir-deuda-tooling-claude-tracking]]

#### SP-ADJ-06

[[US-ADJ-6.1-renombrar-faz-faas-en-codigo-renombrar-faz-faas-en-codigo-renombrar-faz-faas-en-codigo]] [[US-ADJ-6.2-renombrar-faz-faas-en-tests-renombrar-faz-faas-en-tests-renombrar-faz-faas-en-tests]] [[US-ADJ-6.3-eliminar-inspect-signature-callback-on-finalizada-eliminar-inspect-signature-callback-on-finalizada-eliminar-inspect-signature-callback-on-finalizada]] [[US-ADJ-6.4-eliminar-duplicacion-p-10-p-11-y-staticmethod-eliminar-duplicacion-p-10-p-11-y-staticmethod-eliminar-duplicacion-p-10-p-11-y-staticmethod]] [[US-ADJ-6.5-corregir-violaciones-de-capa-en-grillapage-frontend-corregir-violaciones-de-capa-en-grillapage-frontend-corregir-violaciones-de-capa-en-grillapage-frontend]] [[US-ADJ-6.6-correccion-acronimo-faz-faas-en-documentacion-correccion-acronimo-faz-faas-en-documentacion-correccion-acronimo-faz-faas-en-documentacion]] [[US-ADJ-6.7-uat-sp4-inc-4-4-4-5-4-6-bug-sp4-001-002-ux-fixes-uat-sp4-inc-4-4-4-5-4-6-bug-sp4-001-002-ux-fixes-uat-sp4-inc-4-4-4-5-4-6-bug-sp4-001-002-ux-fixes]]

#### SP-ADJ-07

[[US-ADJ-7.1-bug-sp4-003-corregirresultadotrasdns-bug-sp4-003-corregirresultadotrasdns-bug-sp4-003-corregirresultadotrasdns]] [[US-ADJ-7.2-bug-sp4-004-exponer-tarjeta-asignada-en-grilla-bug-sp4-004-exponer-tarjeta-asignada-en-grilla-bug-sp4-004-exponer-tarjeta-asignada-en-grilla]] [[US-ADJ-7.3-scope-sp4-001-cablear-p-11-a-competenciafinalizada-scope-sp4-001-cablear-p-11-a-competenciafinalizada-scope-sp4-001-cablear-p-11-a-competenciafinalizada]]

#### SP5 — Panel Organizador (INC-5.1)

[[US-5.1.1-creartorneopage-formulario-de-creacion-para-el-creartorneopage-formulario-de-creacion-para-el-creartorneopage-formulario-de-creacion-para-el]] [[US-5.1.2-detalletorneopage-tabs-y-panel-de-acciones-de-fase-detalletorneopage-tabs-y-panel-de-acciones-de-fase-detalletorneopage-tabs-y-panel-de-acciones-de-fase]] [[US-5.1.3-inscriptospanel-lista-de-atletas-con-estado-ap-inscriptospanel-lista-de-atletas-con-estado-ap-inscriptospanel-lista-de-atletas-con-estado-ap]] [[US-5.1.4-grillapanel-generar-y-confirmar-grilla-por-disciplina-grillapanel-generar-y-confirmar-grilla-por-disciplina-grillapanel-generar-y-confirmar-grilla-por-disciplina]] [[US-5.1.5-juecespanel-asignacion-de-juez-por-disciplina-juecespanel-asignacion-de-juez-por-disciplina-juecespanel-asignacion-de-juez-por-disciplina]] [[US-5.1.6-ejecucionpanel-monitor-de-competencias-activas-ejecucionpanel-monitor-de-competencias-activas-ejecucionpanel-monitor-de-competencias-activas]]

#### SP5 — INC-5.1-ADJ (ajuste post-UAT)

[[US-5.1.7-politica-de-tabs-por-fase-en-detalletorneopage-politica-de-tabs-por-fase-en-detalletorneopage-politica-de-tabs-por-fase-en-detalletorneopage]] [[US-5.1.8-torneocompetenciaspage-composicion-disciplinas-torneocompetenciaspage-composicion-disciplinas-torneocompetenciaspage-composicion-disciplinas]] [[US-5.1.9-precondicion-de-grilla-para-asignacion-de-juez-precondicion-de-grilla-para-asignacion-de-juez-precondicion-de-grilla-para-asignacion-de-juez]] [[US-5.1.10-normalizacion-del-campo-estado-en-fetchtorneo-normalizacion-del-campo-estado-en-fetchtorneo-normalizacion-del-campo-estado-en-fetchtorneo]]

#### SP5 — Ejecución por Disciplina (INC-5.2)

[[US-5.2.1-torneocompetenciaspage-maestro-detalle-por-disciplina-torneocompetenciaspage-maestro-detalle-por-disciplina-torneocompetenciaspage-maestro-detalle-por-disciplina]] [[US-5.2.2-accion-finalizar-prueba-por-disciplina-accion-finalizar-prueba-por-disciplina-accion-finalizar-prueba-por-disciplina]]

#### SP-ADJ-08

[[US-ADJ-8.1-sp-adj-08-ux-paneles-organizador-post-uat-inc-5-2-sp-adj-08-ux-paneles-organizador-post-uat-inc-5-2-sp-adj-08-ux-paneles-organizador-post-uat-inc-5-2]] [[US-ADJ-8.2-sp-adj-08-selector-de-grilla-filtrado-y-transicion-a-sp-adj-08-selector-de-grilla-filtrado-y-transicion-a-sp-adj-08-selector-de-grilla-filtrado-y-transicion-a]] [[US-ADJ-8.3-sp-adj-08-cancelar-torneo-con-confirmacion-fuerte-sp-adj-08-cancelar-torneo-con-confirmacion-fuerte-sp-adj-08-cancelar-torneo-con-confirmacion-fuerte]]

#### SP5 — Gestión de Usuarios (INC-5.3)

[[US-5.3.1-usuariospage-gestion-de-usuarios-para-el-organizador-usuariospage-gestion-de-usuarios-para-el-organizador-usuariospage-gestion-de-usuarios-para-el-organizador]] [[US-5.3.2-atletadashboardpage-perfil-inscripcion-a-torneos-atletadashboardpage-perfil-inscripcion-a-torneos-atletadashboardpage-perfil-inscripcion-a-torneos]]

#### SP5 — Identidad Extendida (INC-5.4)

[[US-5.4.1-auto-registro-publico-de-usuarios-auto-registro-publico-de-usuarios-auto-registro-publico-de-usuarios]] [[US-5.4.2-cambiar-contrasena-para-usuario-autenticado-cambiar-contrasena-para-usuario-autenticado-cambiar-contrasena-para-usuario-autenticado]] [[US-5.4.3-recuperar-contrasena-via-token-jwt-recuperar-contrasena-via-token-jwt-recuperar-contrasena-via-token-jwt]]

#### SP5 — Portal Atleta e Inscripción con AP (INC-5.5)

[[US-5.5.1-portal-atleta-completo-shell-inscripcion-ap-portal-atleta-completo-shell-inscripcion-ap-portal-atleta-completo-shell-inscripcion-ap]] [[US-5.5.2-vista-organizador-inscriptos-con-datos-completos-y-vista-organizador-inscriptos-con-datos-completos-y-vista-organizador-inscriptos-con-datos-completos-y]]

#### SP5 — Algoritmo de Puntaje y Rankings (INC-5.6)

[[US-5.6.1-puerto-algoritmopuntaje-implementacion-faas-puerto-algoritmopuntaje-implementacion-faas-puerto-algoritmopuntaje-implementacion-faas]] [[US-5.6.2-tiporeglamento-en-torneo-di-en-calcularrankinghandler-tiporeglamento-en-torneo-di-en-calcularrankinghandler-tiporeglamento-en-torneo-di-en-calcularrankinghandler]] [[US-5.6.3-rankingcompetencia-con-puntos-por-categoria-rankingcompetencia-con-puntos-por-categoria-rankingcompetencia-con-puntos-por-categoria]] [[US-5.6.4-rankingoverall-puntos-acumulados-por-categoria-y-genero-rankingoverall-puntos-acumulados-por-categoria-y-genero-rankingoverall-puntos-acumulados-por-categoria-y-genero]] [[US-5.6.5-ui-resultadospage-tabla-de-resultados-por-disciplina-ui-resultadospage-tabla-de-resultados-por-disciplina-ui-resultadospage-tabla-de-resultados-por-disciplina]] [[US-5.6.6-ui-podios-por-division-6-divisiones-fijas-ui-podios-por-division-6-divisiones-fijas-ui-podios-por-division-6-divisiones-fijas]]

#### SP-ADJ-09

[[US-ADJ-9.1-sp-adj-09-shell-dark-del-portal-organizador-sp-adj-09-shell-dark-del-portal-organizador-sp-adj-09-shell-dark-del-portal-organizador]] [[US-ADJ-9.2-sp-adj-09-routing-organizador-reestructurado-sp-adj-09-routing-organizador-reestructurado-sp-adj-09-routing-organizador-reestructurado]] [[US-ADJ-9.3-sp-adj-09-home-del-organizador-formalizado-sp-adj-09-home-del-organizador-formalizado-sp-adj-09-home-del-organizador-formalizado]] [[US-ADJ-9.4-sp-adj-09-dashboard-operativo-del-torneo-en-ejecucion-sp-adj-09-dashboard-operativo-del-torneo-en-ejecucion-sp-adj-09-dashboard-operativo-del-torneo-en-ejecucion]] [[US-ADJ-9.5-sp-adj-09-resultadospage-integrada-en-el-panel-sp-adj-09-resultadospage-integrada-en-el-panel-sp-adj-09-resultadospage-integrada-en-el-panel]] [[US-ADJ-9.6-sp-adj-09-arquitectura-ux-organizador-formalizada-sp-adj-09-arquitectura-ux-organizador-formalizada-sp-adj-09-arquitectura-ux-organizador-formalizada]] [[US-ADJ-9.7-sp-adj-09-declarar-ap-en-el-wizard-de-inscripcion-sp-adj-09-declarar-ap-en-el-wizard-de-inscripcion-sp-adj-09-declarar-ap-en-el-wizard-de-inscripcion]]

#### SP5 — Portal del Atleta (INC-5.7)

[[US-5.7.1-mis-torneos-lista-de-torneos-inscriptos-del-atleta-mis-torneos-lista-de-torneos-inscriptos-del-atleta-mis-torneos-lista-de-torneos-inscriptos-del-atleta]] [[US-5.7.2-mi-grilla-posicion-del-atleta-por-disciplina-mi-grilla-posicion-del-atleta-por-disciplina-mi-grilla-posicion-del-atleta-por-disciplina]] [[US-5.7.3-mis-resultados-resulthero-disciplinapendientecard-mis-resultados-resulthero-disciplinapendientecard-mis-resultados-resulthero-disciplinapendientecard]] [[US-5.7.4-rankings-y-podios-para-el-atleta-rankings-y-podios-para-el-atleta-rankings-y-podios-para-el-atleta]]

#### SP6 — Ajustes Juez (INC-6.1)

[[US-6.1.1-fix-cansubmitbko-reorden-flujo-juez-tarjeta-marca-fix-cansubmitbko-reorden-flujo-juez-tarjeta-marca-fix-cansubmitbko-reorden-flujo-juez-tarjeta-marca]] [[US-6.1.2-colores-tarjeta-outline-filled-heading-paso-5-corregido-colores-tarjeta-outline-filled-heading-paso-5-corregido-colores-tarjeta-outline-filled-heading-paso-5-corregido]] [[US-6.1.3-grilla-ordenada-por-estado-keypad-visible-en-movil-grilla-ordenada-por-estado-keypad-visible-en-movil-grilla-ordenada-por-estado-keypad-visible-en-movil]] [[US-6.1.4-rediseno-inicio-juez-sta-mm-ss-tarjeta-amarilla-rediseno-inicio-juez-sta-mm-ss-tarjeta-amarilla-rediseno-inicio-juez-sta-mm-ss-tarjeta-amarilla]] [[US-6.1.5-atletacard-compacta-en-paso-de-rpselector-atletacard-compacta-en-paso-de-rpselector-atletacard-compacta-en-paso-de-rpselector]]

#### SP6 — Ajustes Organizador (INC-6.2)

[[US-6.2.1-torneos-ordenados-por-fecha-desc-en-lista-organizador-torneos-ordenados-por-fecha-desc-en-lista-organizador-torneos-ordenados-por-fecha-desc-en-lista-organizador]] [[US-6.2.2-inscriptos-y-grilla-columna-categoria-legible-titulo-inscriptos-y-grilla-columna-categoria-legible-titulo-inscriptos-y-grilla-columna-categoria-legible-titulo]] [[US-6.2.3-resultadospage-quitar-pts-faas-andarivel-como-numero-resultadospage-quitar-pts-faas-andarivel-como-numero-resultadospage-quitar-pts-faas-andarivel-como-numero]] [[US-6.2.4-panel-torneo-alertas-sin-boton-resolver-jueces-sin-panel-torneo-alertas-sin-boton-resolver-jueces-sin-panel-torneo-alertas-sin-boton-resolver-jueces-sin]] [[US-6.2.5-nuevo-torneo-con-grupos-etarios-junior-senior-master-nuevo-torneo-con-grupos-etarios-junior-senior-master-nuevo-torneo-con-grupos-etarios-junior-senior-master]] [[US-6.2.6-podiospage-para-el-organizador-podiospage-para-el-organizador-podiospage-para-el-organizador]]

#### SP6 — Ajustes Atleta (INC-6.3)

[[US-6.3.1-inicio-atleta-indicador-en-linea-disciplinas-por-ot-inicio-atleta-indicador-en-linea-disciplinas-por-ot-inicio-atleta-indicador-en-linea-disciplinas-por-ot]] [[US-6.3.2-inscripcion-atleta-ap-inline-apto-medico-constancia-inscripcion-atleta-ap-inline-apto-medico-constancia-inscripcion-atleta-ap-inline-apto-medico-constancia]]

#### SP6 — Deuda Técnica Sistema (INC-6.4)

[[US-6.4.1-romper-ciclo-adp-en-competencia-domain-aggregates-romper-ciclo-adp-en-competencia-domain-aggregates-romper-ciclo-adp-en-competencia-domain-aggregates]] [[US-6.4.2-materializar-proyeccion-competencias-por-torneo-en-materializar-proyeccion-competencias-por-torneo-en-materializar-proyeccion-competencias-por-torneo-en]] [[US-6.4.3-corregir-d-05-imports-cross-bc-en-resultados-api-y-corregir-d-05-imports-cross-bc-en-resultados-api-y-corregir-d-05-imports-cross-bc-en-resultados-api-y]] [[US-6.4.4-refactoring-algoritmopuntajefaas-correcciones-codeguard-refactoring-algoritmopuntajefaas-correcciones-codeguard-refactoring-algoritmopuntajefaas-correcciones-codeguard]] [[US-6.4.5-refactoring-declararapinscripcionhandler-refactoring-declararapinscripcionhandler-refactoring-declararapinscripcionhandler]] [[US-6.4.6-cierre-arch-03-srp-rankingcompetencia-monitoreo-cierre-arch-03-srp-rankingcompetencia-monitoreo-cierre-arch-03-srp-rankingcompetencia-monitoreo]]

#### SP6 — API Pública (INC-6.6)

[[US-6.6.1-endpoint-publico-get-torneos-sin-autenticacion-endpoint-publico-get-torneos-sin-autenticacion-endpoint-publico-get-torneos-sin-autenticacion]] [[US-6.6.2-publictorneospage-pagina-publica-de-lista-de-torneos-publictorneospage-pagina-publica-de-lista-de-torneos-publictorneospage-pagina-publica-de-lista-de-torneos]] [[US-6.6.3-navegacion-contextual-redirect-post-login-y-navegacion-contextual-redirect-post-login-y-navegacion-contextual-redirect-post-login-y]] [[US-6.6.4-publictorneodetallepage-torneo-en-ejecucion-para-publictorneodetallepage-torneo-en-ejecucion-para-publictorneodetallepage-torneo-en-ejecucion-para]]

#### SP-ADJ-10 — Edición de torneo post-cierre

[[US-ADJ-10.1-edicion-completa-del-torneo-put-torneos-{id}-edicion-completa-del-torneo-put-torneos-{id}-edicion-completa-del-torneo-put-torneos-{id}]] [[US-ADJ-10.2-pagina-mis-datos-del-atleta-patch-registro-atletas-me-pagina-mis-datos-del-atleta-patch-registro-atletas-me-pagina-mis-datos-del-atleta-patch-registro-atletas-me]] [[US-ADJ-10.3-email-de-bienvenida-y-auto-login-post-registro-email-de-bienvenida-y-auto-login-post-registro-email-de-bienvenida-y-auto-login-post-registro]] [[US-ADJ-10.4-vista-post-torneo-en-portal-del-atleta-vista-post-torneo-en-portal-del-atleta-vista-post-torneo-en-portal-del-atleta]]

#### SP-ADJ-11 — Modelo de usuarios con múltiples roles

[[US-ADJ-11.1-usuario-roles-list-rol-jwt-rol-activo-login-condicional-usuario-roles-list-rol-jwt-rol-activo-login-condicional-usuario-roles-list-rol-jwt-rol-activo-login-condicional]] [[US-ADJ-11.2-post-delete-auth-usuarios-me-roles-guard-no-quitar-post-delete-auth-usuarios-me-roles-guard-no-quitar-post-delete-auth-usuarios-me-roles-guard-no-quitar]] [[US-ADJ-11.3-atleta-club-categoria-opcionales-dni-telefono-migracion-atleta-club-categoria-opcionales-dni-telefono-migracion-atleta-club-categoria-opcionales-dni-telefono-migracion]] [[US-ADJ-11.4-entidad-juez-juezrepositoryport-endpoints-registro-entidad-juez-juezrepositoryport-endpoints-registro-entidad-juez-juezrepositoryport-endpoints-registro]] [[US-ADJ-11.5-entidad-organizador-organizadorrepositoryport-endpoints-entidad-organizador-organizadorrepositoryport-endpoints-entidad-organizador-organizadorrepositoryport-endpoints]] [[US-ADJ-11.6-registropage-checkboxes-multi-rol-secciones-juez-registropage-checkboxes-multi-rol-secciones-juez-registropage-checkboxes-multi-rol-secciones-juez]] [[US-ADJ-11.7-loginpage-selector-de-rol-cuando-requires-role-loginpage-selector-de-rol-cuando-requires-role-loginpage-selector-de-rol-cuando-requires-role]] [[US-ADJ-11.8-atletamisdatospage-campos-dni-y-telefono-atletamisdatospage-campos-dni-y-telefono-atletamisdatospage-campos-dni-y-telefono]] [[US-ADJ-11.9-juezmisdatospage-organizadormisdatospage-rutas-juezmisdatospage-organizadormisdatospage-rutas-juezmisdatospage-organizadormisdatospage-rutas]] [[US-ADJ-11.10-creacion-automatica-de-perfiles-al-registrarse-creacion-automatica-de-perfiles-al-registrarse-creacion-automatica-de-perfiles-al-registrarse]]

#### SP7 — Despliegue (INC-7.1 + INC-7.2)

[[US-7.1.1-dockerfile-fastapi-estaticos-fly-toml-entorno-dockerfile-fastapi-estaticos-fly-toml-entorno-dockerfile-fastapi-estaticos-fly-toml-entorno]] [[US-7.1.2-fly-deploy-verificacion-flujos-criticos-tag-v1-0-1-fly-deploy-verificacion-flujos-criticos-tag-v1-0-1-fly-deploy-verificacion-flujos-criticos-tag-v1-0-1]] · [[US-7.2.1-manual-organizador-crear-torneo-inscripciones-grilla-manual-organizador-crear-torneo-inscripciones-grilla-manual-organizador-crear-torneo-inscripciones-grilla]] [[US-7.2.2-manual-juez-panel-flujo-de-performance-6-pasos-tarjetas-manual-juez-panel-flujo-de-performance-6-pasos-tarjetas-manual-juez-panel-flujo-de-performance-6-pasos-tarjetas]] [[US-7.2.3-manual-atleta-registro-inscripcion-ap-consulta-de-manual-atleta-registro-inscripcion-ap-consulta-de-manual-atleta-registro-inscripcion-ap-consulta-de]]

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
| [[proyecto]] | Estado unificado del proyecto — síntesis BL-000..BL-006, SP activo, US cerradas |

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
