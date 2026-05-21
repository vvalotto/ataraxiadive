# Wiki Log — AtaraxiaDive

> Registro cronológico append-only de todas las operaciones del wiki.
> Formato de entrada: `## [YYYY-MM-DD] <tipo> | <descripción>`
> Tipos: ingest | query | lint | init

---

## [2026-05-21] vistas | Fase 2 — 6 vistas operativas construidas

Páginas actualizadas: 6

**Vistas completadas (wiki/vistas/):**
- `dominio.md` — 6 preguntas + recorridos + tabla de BCs + glosario del lenguaje ubicuo
- `decisiones.md` — 7 preguntas + tabla de ADRs por área + ADR-010 supersedido documentado
- `trazabilidad.md` — 7 preguntas + tabla de pendientes RF + mapa RF→BC + remisión a matrix.md
- `salud.md` — 7 preguntas + tabla D-02/D-03/D-05/D-06/D-09 + instrucción para primer lint
- `impacto.md` — 7 preguntas + mapa de dependencias reales + tabla de interfaces críticas
- `investigacion.md` — 7 preguntas + HITOs para el paper + capitalización por producto intelectual

**Estado del wiki:** H-2 completado. Próximo paso: Fase 3 (ingest de estado).

---

## [2026-05-20] ingest | docs/contexto/ (ANALISIS-*.md, INDICE-HITOS.md, PLAN-EXPERIMENTO.md)

Páginas creadas: 2 | Páginas actualizadas: 1

**Páginas creadas (wiki/investigacion/):**
- `hitos-catalog.md` — catálogo de los 32 HITOs; tabla por SP; agrupación por tema (ecosistema, DDD/ES, calidad, validación, arquitectura emergente)
- `experimento-plan.md` — el objetivo real del experimento (no construir software sino demostrar factibilidad empírica); 3 horizontes; jerarquía de trabajo; tabla de capitalización de conocimiento

**Página enriquecida:**
- `iedd-hipotesis-experimento.md` — tabla completa de 22 hipótesis con estado (✅/🔄) y HITOs de evidencia; links a nuevas páginas

**Hallazgo:** 20 hipótesis confirmadas de 22 a mayo 2026 (SP6 en curso). Las dos en evaluación son las más amplias: RQ1 (fricción de coordinación) y RQ2 (IEDD mejora calidad de specs).

---

## [2026-05-20] ingest | docs/architecture/ (14 archivos)

Páginas creadas: 7 | Páginas actualizadas: 0

**Páginas creadas (wiki/arquitectura/):**
- `context-map.md` — 6 BCs, 11 integraciones, principios de cruce de fronteras, tabla resumen
- `competencia.md` — Core Domain; ES; aggregates Competencia y Performance; integración Registro/Resultados/Notificaciones
- `torneo.md` — Supporting; CRUD; máquina de estados EstadoTorneo (7 estados); integración Registro/Resultados/Notificaciones
- `registro.md` — Supporting; CRUD; aggregates Atleta e Inscripcion; ACL read-only a Torneo; upstream de Competencia
- `resultados.md` — Supporting; stream propio; RankingCompetencia; deuda técnica cross-BC (ranking provisional)
- `identidad.md` — Generic; CRUD; JWT cross-cutting; multi-rol desde ADR-020; política contraseñas ADR-019
- `notificaciones.md` — Generic; ES por idempotencia; P-10 y P-11 implementadas; ResendEmailAdapter + LoggingEmailAdapter

**Hallazgo:** Resultados usa Event Sourcing (stream propio) aunque clasificado como CRUD en diseño general.
**Deuda técnica documentada:** `ObtenerRankingProvisionalHandler` lee `competencia.db` directamente — lectura cross-BC fuera de ACL formal.

---

## [2026-05-20] ingest | docs/adr/ (22 archivos — ADR-001 a ADR-022)

Páginas creadas: 22 | Páginas actualizadas: 0

**Páginas creadas (wiki/decisiones/):**
- ADR-001 a ADR-016: creadas en sesión anterior
- ADR-017: Event Sourcing en BC Notificaciones (exactly-once delivery)
- ADR-018: Hash SHA-256 para integridad de resultados — `CalculadorHashCompetencia`
- ADR-019: Política de contraseñas (10+, mayúscula, número) + `PasswordStrengthBar.tsx`
- ADR-020: `Usuario.roles: list[Rol]` + perfiles Juez y Organizador en BC Registro
- ADR-021: Fly.io + volumen persistente (supersede ADR-010 Cloud Run + Litestream)
- ADR-022: `Categoria` StrEnum movida a `shared/domain/value_objects/`

**ADR-010 marcada como SUPERSEDIDA por ADR-021.**
**Cobertura de decisiones:** 22/22 ADRs del proyecto. Vista Decisiones completa.

---

## [2026-05-20] ingest | docs/iedd/ (6 archivos)

Páginas creadas: 3 | Páginas actualizadas: 0

**Páginas creadas:**
- `wiki/investigacion/iedd-marco-conceptual.md` — modelo de 5 capas, tesis central, rol de DDD e IA
- `wiki/investigacion/iedd-hipotesis-experimento.md` — hipótesis del ensayo, 5 puntos confirmados, tesis provisional, qué sigue abierto
- `wiki/investigacion/uat-metodologia.md` — política UAT: principios, proceso 5 pasos, vibe coding, datos reales como oráculo

**Fuentes ingresadas:** 01, 02, 03 (marco conceptual 5 capas), 04 (hipótesis), UAT-POLITICA-CONTROLADA.md, US-IEDD-template.md (referenciado, no creado como página propia)

**Hallazgo metodológico:** el framework IEDD se auto-documenta al usarse en AtaraxiaDive — el proyecto es simultáneamente laboratorio del experimento y producto del mismo.

---

## [2026-05-20] ingest | docs/dominio/03-atributos_calidad.md

Páginas creadas: 1 | Páginas actualizadas: 0

**Página creada:**
- `wiki/conceptos/atributos-calidad.md` — 8 atributos de calidad con valores concretos, drivers y mapa hacia ADRs

**Valores clave capturados:**
- Latencia máxima juez: 500 ms | Atletas simultáneos: 3 | Usuarios concurrentes: 50
- Modo offline requerido (conectividad precaria confirmada)
- Flujo juez: máximo 6 acciones; dispositivo principal: celular
- Log de auditoría inalterable requerido (→ ADR-018)
- Confiabilidad: performance es evento único e irrepetible (→ ADR-001 Event Sourcing)
- Reglas de negocio configurables sin desarrollador (→ ADR-004)
- Exportación de resultados requerida (CSV/JSON/AIDA-CMAS)

---

## [2026-05-20] ingest | docs/dominio/05-requerimientos_funcionales.md

Páginas creadas: 8 | Páginas actualizadas: 3 (performance, grilla, anuncio)

**Semilla de trazabilidad por área funcional:**
- `wiki/trazabilidad/RF-gestion-torneo.md` — 7 RFs; disciplinas: STA, DNF, DBF, DYN, SPE (configurable)
- `wiki/trazabilidad/RF-inscripcion-atletas.md` — 10 RFs; brevet no obligatorio; club obligatorio
- `wiki/trazabilidad/RF-preparacion.md` — 8 RFs; orden grilla: distancia=menor→mayor, tiempo=mayor→menor; OT definido por juez
- `wiki/trazabilidad/RF-ejecucion.md` — 10 RFs; black-out (no back-out); cronómetro manual; DNS = DQ inmediata
- `wiki/trazabilidad/RF-resultados.md` — 6 RFs; existe ranking "Overall"; empates → mismo puesto
- `wiki/trazabilidad/RF-usuarios-roles.md` — 5 RFs; 1 organizador por torneo; juez asignado por disciplina
- `wiki/trazabilidad/RF-notificaciones.md` — 4 RFs; mail + push; pendiente: notif. durante ejecución
- `wiki/trazabilidad/RF-integracion.md` — área completa pendiente de definición

**Enriquecimientos en conceptos existentes:**
- `performance`: black-out con distancia, cronómetro manual, DNS
- `grilla`: orden por tipo de disciplina, OT, atleta sin anuncio=no compite
- `anuncio`: definitivo (no modificable), valor > 0

**Pendientes globales detectados:** RF-IN-07, RF-EJ-04, RF-PM-01, RF-NT-03, RF-IG-01..04

---

## [2026-05-20] ingest | docs/dominio/01-dominio_torneos_apnea.md

Páginas creadas: 8 | Páginas actualizadas: 0

**Conceptos creados:**
- `wiki/conceptos/torneo.md` — ciclo de vida del torneo, etapas, datos
- `wiki/conceptos/disciplina.md` — modalidades de prueba (tiempo/distancia)
- `wiki/conceptos/grilla.md` — planilla de salida por disciplina
- `wiki/conceptos/performance.md` — actuación del atleta; tipos de finalización
- `wiki/conceptos/tarjeta.md` — validez de performance (blanca/roja); código de penalización
- `wiki/conceptos/anuncio.md` — marca declarada en Preparación; input para grilla
- `wiki/conceptos/atleta.md` — participante; datos deportivos; categoría; brevet
- `wiki/conceptos/roles.md` — Organizador, Juez, Atleta, Administrador

**Nota:** Fuente marcada como referencia histórica (elicitación feb 2026). Conceptos base
del dominio capturados. Arquitectura vigente (BCs) pendiente de fuentes 4-5 (ADRs + architecture/).

---

## [2026-05-20] init | Inicialización del wiki

Branch huérfano `wiki` creado.
Estructura de directorios y archivos base inicializados.
WIKI.md (schema) creado con convenciones, tipos de páginas y vistas.
Páginas de vistas (6) creadas con propósito, stakeholders y recorridos.

**Próximo paso:** Fase 0 — Preparación (resolver gaps G-01, G-02, G-03 en branch develop)
**Luego:** Fase 1 — Ingest fundacional (docs/dominio/, docs/adr/, docs/architecture/)
