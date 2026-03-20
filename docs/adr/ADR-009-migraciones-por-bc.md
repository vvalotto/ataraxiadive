# ADR-009: Migraciones de schema por Bounded Context

| Campo | Valor |
|-------|-------|
| **Estado** | Aceptada |
| **Fecha** | 2026-03-20 |
| **Autores** | Victor Valotto |
| **Relacionado** | ADR-006 (estructura BC-first), ADR-007 (SQLite por BC) |

---

## Contexto

Cada BC tiene su propio archivo SQLite (`<bc>.db`). Las migraciones de schema
deben reflejar esta aislación: el schema de un BC debe poder evolucionar
sin afectar ni conocer el schema de los demás.

## Opciones Consideradas

**Opción A — Migraciones por BC:**
Una carpeta `migrations/` dentro de `<bc>/infrastructure/`. Cada BC tiene
su propio entorno Alembic con su propio `env.py` y archivo `alembic.ini`.

**Opción B — Migraciones globales:**
Una sola carpeta `migrations/` en la raíz del proyecto. Todas las tablas
de todos los BCs en un único historial de versiones.

## Decisión

Se adopta **migraciones por BC (Opción A)**.

```
src/
├── competencia/
│   └── infrastructure/
│       └── migrations/
│           ├── env.py
│           └── versions/
├── torneo/
│   └── infrastructure/
│       └── migrations/
│           ├── env.py
│           └── versions/
...
```

Cada BC corre sus migraciones de forma independiente apuntando a su
propio archivo SQLite:

```bash
alembic -c src/competencia/infrastructure/migrations/alembic.ini upgrade head
```

## Consecuencias

**Positivas:**
- Aislación completa: el schema de un BC evoluciona sin afectar los demás
- Coherente con BC-first (ADR-006) y un archivo SQLite por BC (ADR-007)
- Las migraciones de un BC son legibles y mantenibles de forma independiente

**Negativas / trade-offs:**
- Más configuración inicial: un `alembic.ini` y `env.py` por BC
- Para correr todas las migraciones hay que iterar sobre cada BC
  (se mitiga con un script `migrate_all.sh` o tarea en `Makefile`)
