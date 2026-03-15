# Matriz de Trazabilidad

**Última actualización**: YYYY-MM-DD
**Baseline de referencia**: BL-NNN

---

## US → Código (Implementación)

| User Story                     | Módulo / Archivo                      | Estado        |
|--------------------------------|---------------------------------------|---------------|
| US-001: [título]               | `src/domain/[modulo].py`              | Implementada  |
| US-002: [título]               | `src/application/[servicio].py`       | En progreso   |
| US-003: [título]               | —                                     | Pendiente     |

---

## US → Tests (Verificación)

| User Story                     | Suite de tests                        | Estado        |
|--------------------------------|---------------------------------------|---------------|
| US-001: [título]               | `tests/unit/test_[modulo].py`         | Passing       |
| US-002: [título]               | `tests/integration/test_[srv].py`     | En progreso   |

---

## US → ADR (Decisiones que la afectan)

| User Story                     | ADR relacionado                       | Relación              |
|--------------------------------|---------------------------------------|-----------------------|
| US-001: [título]               | ADR-001: [decisión]                   | Determina diseño      |
| US-004: [título]               | ADR-003: [decisión]                   | Motiva la decisión    |

---

## RFC → CIs afectados

| RFC                            | CIs modificados                       | Baseline resultante   |
|--------------------------------|---------------------------------------|-----------------------|
| RFC-001: [descripción]         | US-002, src/domain/x.py, ADR-002      | BL-002                |

---

## Cobertura general

| Total US definidas | US implementadas | US verificadas | Cobertura tests |
|--------------------|------------------|----------------|-----------------|
| N                  | N                | N              | XX%             |
