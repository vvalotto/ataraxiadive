# Hallazgos DesignReviewer Pendientes — INC-5.6 + SP-ADJ-09
# Para resolver en US de ajuste del próximo incremento (SP-ADJ-10 o similar)
# Registrado: 2026-04-29
# Reporte fuente: quality/reports/designreviewer/INC-5.6-report.txt

## Resultado quality gate
- **0 CRITICAL** — gate PASS
- **252 WARNING** (+25 vs INC-5.5 que tenía 227)

## Delta +25: origen estimado
- INC-5.6 (clases nuevas ranking): ~15 warnings (LCOM, FanOut, LongMethod en RankingCompetencia/RankingOverall/AlgoritmoPuntajeFAAS)
- SP-ADJ-09 US-ADJ-9.7 (inscripcion): ~10 warnings (FeatureEnvy DeclararAPInscripcionHandler, FanOut SQLiteInscripcionRepository, LCOM Inscripcion)

---

## Hallazgos nuevos — INC-5.6

| ID    | Analyzer        | Clase / Módulo              | Val/Umbral | Observación                                                   | Prioridad |
|-------|-----------------|-----------------------------|------------|---------------------------------------------------------------|-----------|
| DR-01 | LCOMAnalyzer    | `RankingCompetencia`        | 2/1        | Baja cohesión: mezcla lógica de ranking por disciplina y acumulación de puntos para overall. Candidato SRP. | Media |
| DR-02 | LCOMAnalyzer    | `AlgoritmoPuntajeFAAS`      | 2/1        | Dos paths de cálculo (distancia/tiempo) en una clase. Refuerza CG-02 (C=11). Candidato a dispatch por TipoDisciplina. | Media |
| DR-03 | FanOutAnalyzer  | `ranking_competencia.py`    | 9/7        | Alto acoplamiento a VOs (Categoria, Genero, Disciplina, Puntos, etc.). Esperado para un aggregate de ranking — monitorear en BL-005. | Baja |
| DR-04 | FanOutAnalyzer  | `ranking_overall.py`        | 8/7        | Mismo patrón que DR-03. Monitorear. | Baja |
| DR-05 | FanOutAnalyzer  | `resultados_competencia_port.py` | 8/7   | Puerto con alta dependencia de tipos. Evaluar si algunos tipos pertenecen a shared. | Baja |

## Hallazgos nuevos — SP-ADJ-09 (US-ADJ-9.7)

| ID    | Analyzer            | Clase / Módulo                    | Val/Umbral | Observación                                                              | Prioridad |
|-------|---------------------|-----------------------------------|------------|--------------------------------------------------------------------------|-----------|
| DR-06 | FeatureEnvyAnalyzer | `DeclararAPInscripcionHandler`    | 4/2        | Handler accede demasiado a propiedades de objetos externos. La lógica de declarar AP podría estar mejor ubicada en el aggregate `Inscripcion`. | Media |
| DR-07 | FeatureEnvyAnalyzer | `SQLiteInscripcionRepository`     | 7/2        | Repositorio con envy significativo (7/2). Posible consulta que ensambla datos de múltiples entidades. | Media |
| DR-08 | FanOutAnalyzer      | `sqlite_inscripcion_repository.py`| 9/7        | Alto fan-out del repositorio. Relacionado con DR-07. | Baja |

---

## Hallazgos pre-existentes (no nuevos, carry-over)

Presentes desde INC-5.4/5.5 — no atribuibles a INC-5.6 ni SP-ADJ-09:
- `SQLiteTorneoRepository` FeatureEnvy (múltiples)
- `SQLiteUsuarioRepository` FeatureEnvy
- `SQLiteAtletaRepository` FeatureEnvy
- `SQLiteNotificacionEventStore` FeatureEnvy
- `router.py` FanOut (múltiples — API routers conocidos)
- `app.py` FanOut 13/7 (composition root — esperado)
- `exception_handlers.py` LongMethod 96/20 (conocido)

---

## Criterio para US de ajuste

**DR-01 + DR-02:** refuerzan el candidato CG-02 de CodeGuard. Una sola US de refactoring
en `AlgoritmoPuntajeFAAS` (dispatch por tipo) y evaluación de SRP en `RankingCompetencia`
podría resolver ambos.

**DR-06:** `DeclararAPInscripcionHandler` con FeatureEnvy 4/2 es el hallazgo más concreto
de SP-ADJ-09. Si el aggregate `Inscripcion` ya tiene el método `declarar_ap`, el handler
debería delegarle directamente en lugar de acceder a propiedades individualmente.

**DR-07/DR-08:** `SQLiteInscripcionRepository` con FanOut 9/7 y FeatureEnvy 7/2 podría
indicar una query que ensambla datos de inscripcion + identidad + competencia en un solo
método. Evaluar si la query de AP pertenece al repositorio o a un read model.

**DR-03/DR-04/DR-05/DR-08:** FanOut en aggregates y repositorios de ranking — acceptable
por ahora, monitorear en BL-005.
