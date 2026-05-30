# Changelog

Todos los cambios notables de AtaraxiaDive se documentan en este archivo.

Formato: [Keep a Changelog](https://keepachangelog.com/es/1.0.0/)
Versionado: [Semantic Versioning](https://semver.org/lang/es/)

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

## [Unreleased]

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

### Added (SP1 — v0.1.0)
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
