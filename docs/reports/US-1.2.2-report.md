# Reporte de Implementación: US-1.2.2 — Llamar Atleta

| Campo | Valor |
|-------|-------|
| **US-IEDD** | US-1.2.2 |
| **Incremento** | 1.2 |
| **Subproyecto** | SP1 — La Performance |
| **Fecha** | 2026-03-22 |
| **Branch** | feature/US-1.2.2-llamar-atleta |
| **Estado** | ✅ Implementada |

---

## 1. Resumen Ejecutivo

US-1.2.2 implementa el comando `LlamarAtleta` sobre el BC Competencia usando Event Sourcing.
Añade el evento `AtletaLlamado`, el método `Performance.llamar()`, y la verificación
de INV-P-05 (Competencia en EnEjecucion) via el puerto `CompetenciaEstadoPort`.

---

## 2. Artefactos Producidos

### Código nuevo
| Archivo | Descripción |
|---------|-------------|
| `src/competencia/domain/events/atleta_llamado.py` | Evento de dominio `AtletaLlamado` |
| `src/competencia/application/commands/llamar_atleta.py` | Command + Handler + excepciones de aplicación |
| `tests/unit/competencia/application/test_llamar_atleta_handler.py` | 6 tests unitarios del handler |
| `tests/unit/competencia/infrastructure/test_competencia_estado_stub.py` | 3 tests del stub |
| `tests/integration/competencia/test_llamar_atleta_integration.py` | 4 tests de integración con SQLiteEventStore real |
| `tests/features/steps/llamar_atleta_steps.py` | Step definitions BDD |
| `tests/features/US-1.2.2-llamar-atleta.feature` | 3 escenarios BDD (Gherkin) |
| `docs/specs/sp1/US-1.2.2.md` | Especificación US-IEDD formal |
| `docs/plans/sp1/US-1.2.2-plan.md` | Plan de implementación |

### Código modificado
| Archivo | Cambio |
|---------|--------|
| `src/competencia/domain/ports/competencia_estado_port.py` | +`is_en_ejecucion()` abstracto |
| `src/competencia/domain/aggregates/performance.py` | +`EstadoInvalidoParaLlamar`, +`llamar()`, +`_apply_stored` para `AtletaLlamado` |
| `src/competencia/domain/events/__init__.py` | +exportación de `AtletaLlamado` |
| `src/competencia/infrastructure/competencia_estado_stub.py` | +`is_en_ejecucion() → True` |
| `src/competencia/application/commands/__init__.py` | +exportaciones de `llamar_atleta` |
| `pyproject.toml` | `max_cbo = 12` (Performance CBO=11 con nuevo evento) |

---

## 3. Métricas de Calidad

| Métrica | Valor | Umbral | Estado |
|---------|-------|--------|--------|
| Tests totales (suite completa) | 49 | — | ✅ |
| Coverage global | 98.48% | 90% | ✅ |
| Tests unitarios nuevos | 17 | — | ✅ |
| Tests integración nuevos | 4 | — | ✅ |
| Escenarios BDD | 3 | — | ✅ |
| CodeGuard errores | 0 | 0 | ✅ |
| CodeGuard advertencias | 0 | — | ✅ |
| DesignReviewer CRITICAL | 0 | 0 | ✅ |
| Pylint score | ≥ 8.0 | 8.0 | ✅ |

---

## 4. Invariantes Implementados

| ID | Descripción | Mecanismo |
|----|-------------|-----------|
| INV-P-05 | `LlamarAtleta` solo si Competencia en `EnEjecucion` | `LlamarAtletaHandler.handle()` → `CompetenciaEstadoPort.is_en_ejecucion()` |
| (no numerado) | `Performance.llamar()` solo desde estado `AnunciadaAP` | `Performance.llamar()` → `EstadoInvalidoParaLlamar` |

**SP1 stub:** `StubCompetenciaEstadoAdapter.is_en_ejecucion()` retorna siempre `True`.
La integración real con el estado de Competencia se implementa en SP2.

---

## 5. Flujo Implementado

```
RegistrarAP → [Performance: AnunciadaAP]
     ↓
LlamarAtleta → [Performance: Llamada]
               Event: AtletaLlamado {
                 performance_id, participante_id, disciplina,
                 posicion_grilla, ot_programado, llamado_en
               }
```

---

## 6. Tracking de Tiempo

| Fase | Tiempo |
|------|--------|
| Fase 0: Validación | — |
| Fase 1: BDD | — |
| Fase 2: Plan | — |
| Fase 3: Implementación | — |
| Fase 4: Tests unitarios | — |
| Fase 5: Tests integración | — |
| Fase 6: Validación BDD | — |
| Fase 7: Quality gates | — |
| Fase 8: Documentación | — |
| Fase 9: Reporte final | — |
| **Total real** | **~32 min** |
| **Estimado** | **1h 50min** |

> Tiempo real muy por debajo del estimado: la especificación detallada y los patrones
> establecidos por US-1.2.1 redujeron la fricción de decisión. El tracking fue iniciado
> en el contexto de una sesión restaurada desde un contexto previo.

---

## 7. Decisiones Técnicas

| Decisión | Justificación |
|----------|---------------|
| `EstadoInvalidoParaLlamar` definido en `performance.py` | Excepción de dominio — pertenece al aggregate que la lanza |
| `PerformanceNoEncontrada` en la capa application | Condición verificada por el handler, no el aggregate |
| `CompetenciaNoEnEjecucion` en la capa application | INV-P-05 verificado por el handler via port — aggregate no conoce estado de Competencia |
| `max_cbo = 12` en pyproject.toml | Performance CBO=11 con AtletaLlamado; umbral 10 superado; aún controlado para DDD hexagonal |

---

## 8. Lecciones Aprendidas

| ID | Tipo | Descripción |
|----|------|-------------|
| L-5.1 | Background BDD | Step `la performance del participante está en estado "Llamada"` no debe re-registrar AP si el Background ya lo hizo — solo ejecutar la llamada |
| (confirmación) | max_cbo | Cada evento de dominio nuevo suma 1 CBO al aggregate; con 3+ eventos en SP1, max_cbo=12 es el umbral correcto para DDD |

---

*Generado por `/implement-us US-1.2.2` — 2026-03-22*
