# Referencia UAT — SP6 / INC-6.5

## Levantar servidores

```bash
# Backend (desde raíz del proyecto)
uv run uvicorn src.app:app --reload --env-file .env

# Frontend (desde raíz del proyecto)
cd frontend && npm run dev
```

| Servicio | URL |
|----------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| Portal público | http://localhost:5173/portalapnea |
| Docs API | http://localhost:8000/docs |

---

## Seeds

```bash
# Seed-A — Usuarios (correr antes de F-01, con DB limpia)
uv run python tests/uat/sp6/seed_ba2025_usuarios.py

# Seed-B — Inscripciones y APs (correr al inicio de F-04, requiere torneo_id)
uv run python tests/uat/sp6/seed_ba2025_inscripciones.py --torneo-id <id>

# Seed-C — Resultados restantes (correr al inicio de F-09, requiere torneo_id)
uv run python tests/uat/sp6/seed_ba2025_resultados.py --torneo-id <id>
```

---

## Usuarios predefinidos

Contraseña universal: **`Ba2025uat!`**

### Roles operativos

| Rol | Email | Dispositivo |
|-----|-------|-------------|
| Organizador | `organizador@ba2025.uat` | Desktop |
| Juez 1 | `juez1@ba2025.uat` | Móvil — DBF/DNF/DYN/SPE andarivel 1 · STA andarivel 1 |
| Juez 2 | `juez2@ba2025.uat` | Móvil — DBF/DNF/DYN/SPE andarivel 2 · STA andarivel 2 |
| Juez 3 | `juez3@ba2025.uat` | Móvil — STA andarivel 3 (solo STA) |

### Atletas de referencia

| Atleta | Email | Uso en UAT |
|--------|-------|------------|
| Víctor Valotto | `victor.valotto@ba2025.uat` | F07: DBF RP=52.40m · STA RP=04:32.98 |
| Guadalupe Fardi | `guadalupe.fardi@ba2025.uat` | F04: inscripción DYN · F07: DNF RP=41.05m JUNIOR FEM |

### Patrón general atletas

```
nombre.apellido@ba2025.uat  /  ba2025uat
```

---

## Asignación de jueces por disciplina

| Disciplina | Andariveles | Juez 1 | Juez 2 | Juez 3 |
|-----------|:-----------:|--------|--------|--------|
| DBF | 2 | andarivel 1 | andarivel 2 | — |
| DNF | 2 | andarivel 1 | andarivel 2 | — |
| DYN | 2 | andarivel 1 | andarivel 2 | — |
| SPE | 2 | andarivel 1 | andarivel 2 | — |
| STA | 3 | andarivel 1 | andarivel 2 | andarivel 3 |

---

## Criterio de bloqueo

| Severidad | Definición | Acción |
|-----------|-----------|--------|
| 🔴 Bloqueante | Impide continuar · pérdida de datos · flujo roto | Detener — registrar — no avanzar |
| 🟡 Observación | Incorrecto pero el flujo puede continuar | Registrar — continuar |
| ⚪ Estético | Texto, color, alineación | Registrar para después |
