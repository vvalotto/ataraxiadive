# Plan de Implementación — INC-2.0
# Exception Management — domain/exceptions.py + exception_handlers.py

**Fecha:** 2026-03-26
**Branch:** `feature/INC-2.0-exception-management`
**Estimación:** 45 min
**Tiempo real:** ~45 min

---

## Contexto

Las excepciones de dominio estaban definidas en los archivos de los aggregates
(`performance.py` y `competencia.py`). ADR-013 formaliza que deben vivir en
`domain/exceptions.py` por BC, con `DomainError` como base común para que el
API layer pueda mapearlas a RFC 7807 (ADR-012).

---

## Artefactos a crear

| # | Tipo | Archivo | Descripción |
|---|------|---------|-------------|
| T1 | NEW | `src/competencia/domain/exceptions.py` | `DomainError` base + 11 subclases (7 de Performance, 4 de Competencia) |
| T2 | NEW | `src/competencia/api/exception_handlers.py` | `register_exception_handlers(app)` — DomainError → HTTP 422 RFC 7807 |
| T3 | NEW | `tests/unit/competencia/api/test_exception_handlers.py` | 6 tests del handler genérico |

## Artefactos a modificar

| # | Tipo | Archivo | Cambio |
|---|------|---------|--------|
| T4 | REFACTOR | `src/competencia/domain/aggregates/performance.py` | Eliminar 7 definiciones de excepción, importar desde `domain/exceptions` |
| T5 | REFACTOR | `src/competencia/domain/aggregates/competencia.py` | Eliminar 3 definiciones de excepción, importar desde `domain/exceptions` |
| T6 | MOD | `src/app.py` | Registrar `register_exception_handlers(app)` al iniciar |
| T7 | MOD | 23 archivos de test | Actualizar imports: excepciones ahora desde `competencia.domain.exceptions` |

---

## Dependencias entre tareas

```
T1 (exceptions.py)
  ├── T2 (exception_handlers.py)  →  T6 (app.py)
  ├── T4 (performance.py)
  ├── T5 (competencia.py)
  └── T7 (tests — imports)
```

T1 debe completarse antes que cualquier otra tarea.
T7 puede ejecutarse en paralelo con T2 una vez T1 esté listo.

---

## Jerarquía de excepciones (T1)

```python
DomainError(Exception)
├── Performance
│   ├── EstadoInvalidoParaLlamar
│   ├── EstadoInvalidoParaRegistrarResultado
│   ├── EstadoInvalidoParaRegistrarDNS
│   ├── EstadoInvalidoParaAsignarTarjeta
│   ├── EstadoInvalidoParaCorregirResultado
│   ├── MotivoObligatorio
│   └── DistanciaBlackoutObligatoria
└── Competencia
    ├── IntervaloNoConfigurado
    ├── GrillaYaConfirmada
    ├── EstadoInvalidoParaGenerarGrilla
    └── SinPerformancesParaGrilla     ← descubierta en T5, no estaba en spec inicial
```

---

## Criterio de completitud

- [ ] `pytest tests/` → 284 passed, 0 failed (sin cambios de lógica en tests)
- [ ] `designreviewer src/ --config pyproject.toml` → 0 CRITICAL
- [ ] `codeguard src/` → 0 warnings nuevos
- [ ] `docs/reports/INC-2.0-report.md` generado

---

*Plan redactado: 2026-03-26 — INC-2.0 Exception Management*
