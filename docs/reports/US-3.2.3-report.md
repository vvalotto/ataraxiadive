# Reporte de Implementación — US-3.2.3
## BC Registro — Inscripcion (inscribir + cancelar)

| Campo | Valor |
|-------|-------|
| **US** | US-3.2.3 |
| **Sprint** | SP3 — El Torneo |
| **Incremento** | INC-3.2 |
| **Branch** | `feature/US-3.2.3-inscripcion-atleta` |
| **Fecha** | 2026-03-31 |
| **Tiempo total** | 22 min |

---

## Artefactos Producidos

### Dominio
- `registro/domain/value_objects/estado_inscripcion.py` — `EstadoInscripcion(StrEnum)`
- `registro/domain/aggregates/inscripcion.py` — `Inscripcion` con `cancelar()` (INV-I-03)
- `registro/domain/ports/inscripcion_repository_port.py` — puerto abstracto
- `registro/domain/ports/torneo_consulta_port.py` — ACL read-only sobre Torneo
- `registro/domain/exceptions.py` — 5 nuevas excepciones (INV-I-01..05)

### Aplicación
- `registro/application/commands/inscribir_atleta.py` — valida INV-I-01..05
- `registro/application/commands/cancelar_inscripcion.py`
- `registro/application/queries/listar_inscriptos.py`

### Infraestructura
- `registro/infrastructure/acl/sqlite_torneo_consulta.py` — lee `torneo.db` directamente
- `registro/infrastructure/repositories/sqlite_inscripcion_repository.py` — tabla `inscripciones` en `registro.db`

### API
- `POST /registro/inscripciones` → 201
- `DELETE /registro/inscripciones/{id}` → 200
- `GET /registro/torneos/{id}/inscriptos` → 200

---

## Tests

| Tipo | Cantidad |
|------|----------|
| Unitarios | 17 |
| Integración | 7 |
| BDD | 7 |
| **Total nuevos** | **31** |
| **Suite total** | **643** |

---

## Quality Gates

| Gate | Resultado |
|------|-----------|
| CodeGuard | ✅ 0 errores, 0 advertencias |
| Tests | ✅ 643/643 pass |

---

## Decisiones de Diseño

1. **`TorneoConsultaPort` en `registro/domain/ports/`**: ACL read-only — el dominio de Registro no importa nada de Torneo, solo define la interfaz. La implementación en `infrastructure/acl/` lee `torneo.db` directamente.

2. **`obtener_disciplinas` retorna todas las disciplinas hasta US-3.4.1**: Torneo no tiene campo `disciplinas` en SP3 (se agrega en INC-3.4). INV-I-01 se activará completamente en US-3.4.1.

3. **`inscripcion.cancelar()` recibe `fecha_actual: date` inyectada**: no `datetime.today()` interno, lo que hace los tests deterministas.

4. **Misma `registro.db`** para `atletas` e `inscripciones`: coherente con ADR-007 (un SQLite por BC).

---

*Generado: 2026-03-31*
