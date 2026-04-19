# Changelog

Todos los cambios notables de AtaraxiaDive se documentan en este archivo.

Formato: [Keep a Changelog](https://keepachangelog.com/es/1.0.0/)
Versionado: [Semantic Versioning](https://semver.org/lang/es/)

---

## [Unreleased]

### Added
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
