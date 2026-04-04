# Plan SP3 — El Torneo (BL-003)

| Campo | Valor |
|-------|-------|
| **Sprint** | SP3 |
| **Baseline** | BL-003 |
| **Tag git** | `v0.4.0` |
| **Fecha** | 2026-03-28 |
| **Estado** | ⏳ Pendiente |

---

## Objetivo

Ciclo de vida completo de un torneo via API: crear torneo → inscribir atletas → preparar grillas → ejecutar disciplinas → publicar ranking y Overall.

**DoD de cierre de SP3:** se puede simular un torneo completo con 5 disciplinas, múltiples atletas inscriptos, grillas generadas, competencias ejecutadas y Overall calculado — todo via API sin frontend.

---

## BCs activos

| BC | Tipo | Novedad en SP3 |
|----|------|----------------|
| **Torneo** | Supporting / CRUD | Nuevo — aggregate + API |
| **Registro** | Supporting / CRUD | Nuevo — Atleta + Inscripcion |
| **Identidad** | Generic / CRUD | Nuevo — Usuario + JWT mínimo |
| **Competencia** | Core / ES | Extensión — `torneo_id` + `ConfigurarIntervaloOT` update |
| **Resultados** | Supporting | Extensión — `RankingOverall` + P-09 |

---

## Disciplinas cubiertas en SP3

`STA · DNF · DYNB · DYN · SPE2X50`

Los valores de `Disciplina` no cubiertos en SP3 (CNF, CWT, FIM, VWT) están en el enum pero no tienen casos de uso activos hasta SP4+.

---

## Incrementos y US

### INC-3.1 — Torneo: máquina de estados

**DoD:** `POST /torneos` crea un torneo; las 7 fases (6 del ciclo + Cancelado) transicionan correctamente con sus restricciones; retroceso Ejecución→Preparación funciona.

| US | Descripción | BC afectado |
|----|-------------|-------------|
| US-3.1.1 | Aggregate `Torneo` — crear, `EntidadOrganizadora`, `Sede`, máquina de estados, invariantes | `torneo/domain/` |
| US-3.1.2 | API REST Torneo — CRUD + endpoints de transición de fase | `torneo/api/`, `torneo/application/`, `torneo/infrastructure/` |

---

### INC-3.2 — Identidad + Atleta + Inscripción

**DoD:** usuario puede hacer login y obtener JWT; atleta puede registrarse e inscribirse en un torneo con disciplinas.

| US | Descripción | BC afectado |
|----|-------------|-------------|
| US-3.2.1 | BC Identidad minimal — aggregate `Usuario`, roles, `POST /auth/registro` + `POST /auth/login → JWT` | `identidad/` |
| US-3.2.2 | BC Registro — aggregate `Atleta` (datos personales, `Categoria`) | `registro/domain/`, `registro/application/`, `registro/infrastructure/` |
| US-3.2.3 | BC Registro — `Inscripcion` (inscribir atleta en torneo + disciplinas, cancelar hasta D-1) | `registro/domain/`, `registro/application/`, `registro/api/` |

---

### INC-3.3 — Asociación Torneo→Competencia + flujo E2E

**DoD:** cada `Competencia` sabe a qué torneo pertenece; el flujo completo inscribir→AP→grilla funciona end-to-end.

| US | Descripción | BC afectado |
|----|-------------|-------------|
| US-3.3.1 | Competencia — agregar `torneo_id` a `ConfigurarIntervaloOT` (backward compat: opcional) | `competencia/domain/`, `competencia/application/`, `competencia/api/` |
| US-3.3.2 | Flujo E2E — inscribir atleta (Registro) → registrar AP (Competencia con `participante_id = atleta_id`) → generar grilla | `tests/integration/` |

---

### INC-3.4 — Multi-disciplina + jueces + auth JWT

**DoD:** torneo con disciplinas configuradas; juez asignado a disciplina; JWT requerido en endpoints críticos.

| US | Descripción | BC afectado |
|----|-------------|-------------|
| US-3.4.1 | Torneo — `AsignarDisciplinas` + `AsignarJuez` a disciplina | `torneo/domain/`, `torneo/application/`, `torneo/api/` |
| US-3.4.2 | Auth por rol — middleware JWT en Torneo, Registro y Competencia (organizador/juez/atleta) | `identidad/`, `torneo/api/`, `competencia/api/`, `registro/api/` |

---

### INC-3.5 — Overall ranking

**DoD:** `GET /resultados/{torneo_id}/overall` retorna ranking posicional multi-disciplina.

| US | Descripción | BC afectado |
|----|-------------|-------------|
| US-3.5.1 | Aggregate `RankingOverall` en BC Resultados — fórmula posicional (suma de posiciones, menor es mejor), empates | `resultados/domain/`, `resultados/application/` |
| US-3.5.2 | Política P-09 en `app.py` — todas las disciplinas de un torneo finalizadas → `CalcularOverall` | `src/app.py` |
| US-3.5.3 | API `GET /resultados/{torneo_id}/overall` | `resultados/api/` |

---

## Dependencias entre incrementos

```
INC-3.1 (Torneo)
  └── INC-3.2 (Identidad + Registro) — necesita torneoId para inscribir
        └── INC-3.3 (flujo E2E) — necesita inscripcion + competencia con torneo_id
              └── INC-3.4 (disciplinas + jueces) — necesita torneo con disciplinas
                    └── INC-3.5 (Overall) — necesita torneo_id en Competencia
```

---

## Notas de implementación

### Persistencia CRUD (Torneo, Registro, Identidad)

Los 3 BCs nuevos son CRUD (no Event Sourcing). Usarán SQLite por BC (ADR-007) con:
- Puerto de repositorio abstracto en `domain/ports/`
- Implementación con `aiosqlite` raw SQL en `infrastructure/repositories/`
- Una tabla por aggregate, sin Alembic en SP3 (migrations manuales o `CREATE TABLE IF NOT EXISTS`)

### Identidad — JWT mínimo

- `PyJWT` + `bcrypt` para hash de contraseñas
- Secret en `IDENTIDAD_JWT_SECRET` env var
- Token: `{ sub: user_id, email, rol, exp: +24h }`
- Middleware `get_current_user()` como dependencia FastAPI reutilizable

### torneo_id en Competencia

`ConfigurarIntervaloOT` agrega `torneo_id: UUID | None = None` (backward compat).
Los 481 tests existentes no pasan `torneo_id` → siguen funcionando sin cambios.
La política P-09 (Overall) solo actúa cuando `torneo_id` está presente.

### Registro → Competencia (participante_id)

El `participante_id` en Competencia es el `atleta_id` de Registro (mismo UUID).
No hay ACL en SP3 — se confía en que el atleta inscripto registra su propio AP.
El ACL formal (`AtletaInscripto → ParticipanteHabilitado`) queda para SP4.

---

## DoD de Cierre (BL-003)

- [ ] `pytest tests/` — 100% pass
- [ ] Flujo E2E completo: crear torneo → inscribir atleta → configurar competencia → registrar AP → generar grilla → ejecutar → ranking por disciplina → Overall
- [ ] `designreviewer src/` — cero CRITICAL
- [ ] `grep "from torneo\|from registro\|from identidad" src/competencia src/resultados` — cero imports directos (solo `shared/`)
- [ ] `CLAUDE.md §14` actualizado con SP3 completo

---

*Redactado: 2026-03-28 — SP3 El Torneo*
