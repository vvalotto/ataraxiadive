# Changelog

Todos los cambios notables de AtaraxiaDive se documentan en este archivo.

Formato: [Keep a Changelog](https://keepachangelog.com/es/1.0.0/)
Versionado: [Semantic Versioning](https://semver.org/lang/es/)

---

## [1.0.5] - 2026-05-30

### Changed
- **Manual de usuario — revisión completa contra producción** (SP-ADJ-13, PR #218): el manual
  se actualizó para coincidir con la UI real de https://ataraxiadive.fly.dev tras la ejecución
  end-to-end del torneo Puerto Madryn 2026.
  - **Portal público:** nombres de botones reales (Resultados / Podios / Inscribirse); tarjeta
    de lista con Categorías y botón de acción; resultados con pestañas por disciplina y columnas
    Anuncio/OT/Performance/Tarjeta; podios con vistas por disciplina y Overall; nueva página
    anexa "Vista de escritorio"
  - **Portal organizador:** 24 capturas reales (reemplazo de las renombradas); resultados con
    badge FINALIZADA/EN SEGUIMIENTO, estado Pendiente y ejemplos por disciplina; podios con
    estructura por categoría (Overall + por disciplina) y descripción del reglamento FAAS;
    grilla STA en tiempo; panel de disciplina cerrada; Mis Datos con formulario real
  - **Portal atleta:** badge EN PODIO, signo de DIF (RP − AP) y sección Ranking Overall
  - **Portal juez y Tu cuenta:** verificados sin cambios (completos desde INC-7.2)

### Fixed
- **Manual — capturas de escritorio a ancho completo** (`ataraxia.css`): las imágenes apaisadas
  (desktop / portal organizador) ya no quedan limitadas al ancho mobile de 380px

---

## [1.0.4] - 2026-05-30

### Fixed
- **Audit Log — cartel placeholder eliminado** (`AuditoriaCompetenciaPage`): removido el texto
  "Vista contextual de auditoria por disciplina..." que quedó del desarrollo inicial (#213)
- **Audit Log — Hash SHA-256 eliminado** (`AuditoriaCompetenciaPage`): removida la sección
  de hash de integridad que no era parte de la UX esperada (#213)
- **Audit Log — nombre de disciplina** (`TorneoCompetenciasPage`): cada fila ahora muestra
  el nombre de la disciplina (DBF, DNF, DYN, STA) en lugar del UUID de competencia (#215)
- **Resultados — espaciado** (`ResultadosPage`): agregado `mt-6` entre las pestañas de
  selección de disciplina y el título "Ranking por disciplina" (#214)

### Added
- **Navegación móvil — menú hamburguesa** en los tres portales (#216):
  - `OrganizadorLayout`: botón `☰` en mobile despliega panel vertical con todos los items
    de navegación; nav horizontal desktop se mantiene (`md:hidden` / `md:flex`)
  - `JuezLayout`: hamburguesa reemplaza tabs horizontales comprimidos en pantallas chicas
  - `AtletaShell`: hamburguesa reemplaza el `grid-cols-5` ilegible en mobile
  - Item activo marcado con punto sky; menú se cierra automáticamente al navegar
- **Script `seed_produccion_resultados.py`**: herramienta para alimentar la app en producción
  con resultados del dataset BA2025 de forma progresiva por disciplina (`--disciplina`,
  `--limite`, `--desde`, `--dry-run`; soporta Blanca / Roja BKO / DNS / BlancaConPenalizaciones)

### Changed
- `seed_ba2025_usuarios.py`: adaptado a API multi-rol post-SP-ADJ-11
  (`rol` → `roles[]`; `POST /registro/atletas` → `PATCH /registro/atletas/me`)

## [1.0.3] - 2026-05-29

### Changed
- **Estandarización UI de los tres portales** (PR #211): `OrganizadorLayout` / `JuezLayout` /
  `AtletaShell` uniformizados con la estructura `AtaraxiaDive → Portal X → título → descripción`.
  Campos Nombre/Apellido/Email integrados como solo lectura en Mis Datos; `RolesSection` en grid.

### Fixed
- **Build de producción** (`tsc -b`): eliminados imports y variables no usadas en 5 archivos que
  rompían la compilación estricta en Fly.io (no detectados por `tsc --noEmit` local).

---

## [1.0.2] - 2026-05-24

Cierre de **SP7** (referencia: `.cm/baselines/BL-007.md`).

### Added
- **Manual de usuario — INC-7.2** (PR #212): manual completo con MkDocs Material — 5 portales
  + sección "Tu cuenta", ~90 screenshots, build `--strict` verde.
- **SP-ADJ-12 — gestión de roles propios y aceptación de inscripciones** (issues #198–#204,
  PRs #205–#210): `Usuario.agregar_rol()`/`quitar_rol()` + endpoints `POST/DELETE /auth/me/roles`;
  `EstadoAceptacion` en BC Registro + `PATCH /registro/inscripciones/{id}/aceptacion` +
  `InscripcionDetalleDrawer` con Aceptar/Rechazar; JWT incluye `roles[]`.

### Fixed
- SP-ADJ-12 (3 fixes post-revisión): descarga de adjuntos vía `fetch()` + blob URL (evita 401),
  título de pestaña por portal y nuevo favicon.

---

## [1.0.1] - 2026-05-17

### Added
- **Despliegue en producción — INC-7.1** (ADR-021): plataforma Fly.io con volumen persistente
  para los SQLite por BC. App publicada en `https://ataraxiadive.fly.dev/`. Supersede ADR-010
  (Cloud Run + Litestream).

---

## [1.0.0] - 2026-05-16

Cierre de **SP6 · Validación, Ajustes y Despliegue** (referencia: `.cm/baselines/BL-006.md`):
INC-6.1..6.6 (ajustes juez/organizador/atleta, deuda técnica de sistema, portal público) +
SP-ADJ-10 (edición de torneo, Mis Datos atleta, email bienvenida) + SP-ADJ-11 (modelo de
usuarios con múltiples roles — Identidad + Registro + Frontend, ADR-020). UAT 10/10 flows.
Los cambios siguientes se liberaron en esta versión:

### Added
- [US-ADJ-10.2] Página "Mis Datos" del atleta — `PATCH /registro/atletas/me`
  - `Atleta.actualizar()` con semántica PATCH (campos opcionales, solo muta los provistos)
  - `ActualizarAtletaCommand` + `ActualizarAtletaHandler` en BC `registro`
  - Tab "Mis Datos" en `AtletaShell` (5 tabs); `AtletaMisDatosPage` con form pre-rellenado
  - 10 tests unitarios, 4 integración, 4 escenarios BDD — 18 passed
- [US-ADJ-10.1] Edición completa del torneo — `PUT /torneos/{id}`
  - `Torneo.actualizar()` con precondición de estado (`CREADO | INSCRIPCION_ABIERTA`)
  - `ActualizarTorneoCommand` + `ActualizarTorneoHandler` en BC `torneo`
  - `CrearTorneoPage` en modo dual (crear / editar-disciplinas / editar-torneo)
  - Botón "Editar torneo" en `DetalleTorneoPage` visible solo en estados editables
  - 7 tests unitarios, 6 integración, 4 escenarios BDD — 17 passed

### Fixed
- [US-6.4.5] `SQLiteInscripcionRepository` delega reconstitucion en `Inscripcion`
  - Agrega `Inscripcion.from_row()` para reconstruir datos planos persistidos
  - Elimina DR-07 del repositorio en DesignReviewer
  - Documenta DR-06 como falso positivo de coordination handler
- [US-6.4.4] `AlgoritmoPuntajeFAAS` queda como dispatcher explícito
  - Extrae cálculo FAAS de distancia y tiempo a funciones de módulo
  - Elimina el hallazgo LCOM DR-02 en DesignReviewer
  - CodeGuard queda sin errores ni advertencias sobre el componente
- [US-6.4.3] Routers sin imports cross-BC de infraestructura
  - `resultados/api/router.py` deja de importar infraestructura de `competencia` y `torneo`
  - `competencia/api/router.py` deja de importar infraestructura de `registro`
  - `app.py` configura las factories concretas en el composition root
  - `ExportarResultadosHandler` tipa dependencias cross-BC por ports
  - `registro` extrae escritura local de adjuntos detrás de `AdjuntoStoragePort`
  - ArchitectAnalyst mejora `D(registro)` de `0.59` a `0.57`
- [US-6.4.2] `CalcularOverallHandler` usa la proyeccion materializada `competencias_por_torneo`
  - Reemplaza el scan O(n) sobre streams de competencia por `listar_por_torneo(torneo_id)`
  - Actualiza P-09 en `app.py`, tests y BDD de overall
  - Agrega cobertura para torneos sin competencias materializadas
- [US-6.4.1] Eliminado ciclo ADP en `competencia/domain/aggregates`
  - `aggregates/__init__.py` deja de reexportar aggregate roots
  - `Performance` importa helpers de reconstitucion por path directo
  - ArchitectAnalyst reporta `DependencyCycle=0`

### Added
- [US-ADJ-7.3] Cableado de P-11 al finalizar disciplina para publicar resultados por email
  - `_on_finalizada` ejecuta P-08/P-09 y luego construye `ResultadosPublicados` para `PoliticaP11Handler`
  - Fallback local de P-11 a `LoggingEmailAdapter` cuando no hay `RESEND_API_KEY`
  - Tests unitarios, integración y BDD para camino feliz, atleta sin email, idempotencia y fallo de proveedor
- [US-ADJ-7.1] Comando `CorregirResultadoTrasDNS` para corregir DNS registrado por error
  - Nuevo evento `ResultadoCorregidoTrasDNS` y transición `DNS -> ResultadoRegistrado`
  - Endpoint `POST /competencia/{competencia_id}/performances/{performance_id}/corregir-resultado-tras-dns`
  - Tests unitarios, integración y BDD para corrección, rechazos y flujo hasta tarjeta blanca
- [US-2.2.1] DisciplinaDescriptor VO + Port + Adapter — encapsula reglas de disciplina (política P-01) y desacopla el ordering de grilla del enum Disciplina
  - `DisciplinaDescriptor` frozen dataclass con `unidad_esperada` y `orden_ascendente`
  - `DisciplinaDescriptorPort` ABC + `DisciplinaDescriptorAdapter` sin I/O
  - `GenerarGrillaHandler` inyecta el port; 46 tests nuevos, cobertura 100%

### Changed
- [US-2.2.1] `Competencia.generar_grilla()` acepta `descriptor: DisciplinaDescriptor` — elimina dependencia directa en `disciplina.es_tiempo()`
- [US-2.2.1] `GenerarGrillaHandler.__init__` recibe `DisciplinaDescriptorPort` como tercer parámetro

---

## [0.6.0] - 2026-05-01

### Added
- **SP5 · La Puesta en Marcha** (BL-005): panel del organizador, ejecución por disciplina,
  identidad extendida (roles), portal del atleta e inscripción con AP, algoritmo de puntaje
  FAAS y rankings por categoría/género.

---

## [0.5.0] - 2026-04-18

### Added
- **SP4 · La Plataforma** (BL-004): interfaz del juez, offline-first (PWA + cola de comandos),
  BC Notificaciones, auditoría y exportación.

---

## [0.4.0] - 2026-04-04

### Added
- **SP3 · El Torneo** (BL-003): ciclo de vida del torneo, disciplinas y sede (BC Torneo).

---

## [0.3.0] - 2026-03-28

### Added
- **SP2 · La Competencia** (BL-002): grilla, ejecución y ordenamiento por disciplina en el
  BC Competencia.

---

## [0.2.0] - 2026-03-24

### Added
- **SP1 · La Performance** (BL-001): aggregate `Performance`, tarjetas (blanca / con
  penalizaciones / amarilla / roja), Event Sourcing en el BC Competencia.

---

## [0.1.0] - 2026-03-19

### Added
- Estructura inicial del repositorio
- CLAUDE.md con convenciones del proyecto
- ADR-001: Event Sourcing para la fase de competencia
- ADR-002: FastAPI como framework backend
- ADR-003: Offline-first con PWA + IndexedDB para la interfaz del juez
- ADR-004: Reglas de competencia como datos configurables
- BL-000: Baseline pre-código (documentación fundacional)

---

## [0.0.0] — 2026-03-14

Inicialización del repositorio. Sin código todavía.
