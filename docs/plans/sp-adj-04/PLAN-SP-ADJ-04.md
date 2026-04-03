# PLAN-SP-ADJ-04 — Sprint de Ajuste: Discrepancias de Dominio Real

| Campo | Valor |
|-------|-------|
| **Sprint** | SP-ADJ-04 |
| **Contexto** | Ajuste de dominio pre-cierre BL-003 |
| **Fuentes** | HITO-17 · `.work/analisis-discrepancias-dataset-reales.md` |
| **Branch base** | `develop` (antes de taggear BL-003) |
| **Estado** | 🔄 En progreso |

---

## Objetivo

Corregir las discrepancias detectadas al contrastar el modelo de la app con el dataset
real "Apnea Indoor Buenos Aires 2025" (HITO-17). Estas discrepancias son errores de
lenguaje ubicuo, semántica y modelo conceptual que no fueron detectados por la
especificación, el Event Storming ni los tests — porque todos fueron construidos
sobre el mismo conocimiento declarado que contenía los errores.

El criterio de inicio: todos los incrementos de SP3 y SP-ADJ-03 están mergeados en
`develop`. El criterio de cierre: el dataset real puede usarse como datos de prueba
en el UAT de SP3 y producir output verificable contra la documentación oficial del torneo.

---

## Progreso

| US | Descripción | Estado |
|----|-------------|--------|
| `US-ADJ-4.1` | Renombrar `DYNB → DBF` y `SPE2X50 → SPE` en enum `Disciplina` | ✅ Implementada |
| `US-ADJ-4.2` | Corregir orden de grilla STA: `orden_ascendente=True` | ✅ Implementada |
| `US-ADJ-4.3` | Renombrar `JUVENIL → JUNIOR` en enum `Categoria` | ✅ Implementada |
| `US-ADJ-4.4` | Agregar campo `club` a aggregate `Atleta` y exponerlo en grillas/reportes | ✅ Implementada |
| `US-ADJ-4.5` | Ranking y overall por categoría/género | ✅ Implementada |
| `US-ADJ-4.6` | Value Object `TiempoAP` para parsear `MM:SS → segundos` | ✅ Implementada |

---

## US planificadas

---

### US-ADJ-4.1 — Renombrar `DYNB → DBF` y `SPE2X50 → SPE` en enum `Disciplina`
**Prioridad: Alta**
**Capa:** `shared/domain/value_objects/disciplina.py` + todos los archivos que referencian los valores
**Issue:** DISC-02 + DISC-03

Los acrónimos actuales (`DYNB`, `SPE2X50`) no coinciden con el lenguaje ubicuo del
dominio (AIDA/CMAS). Las competencias reales usan `DBF` y `SPE`. Cualquier integración
con datos reales falla al intentar mapear disciplinas.

**Cambios:**
```python
# Antes
DYNB    = "DYNB"
SPE2X50 = "SPE2X50"

# Después
DBF = "DBF"   # Dynamic Bi-Fins (acrónimo estándar AIDA)
SPE = "SPE"   # Speed Endurance
```

**Impacto:** afecta todos los archivos que referencian `Disciplina.DYNB` o `Disciplina.SPE2X50`
(domain, application, infrastructure, tests). Cambio de string value — requiere migración
de cualquier DB existente con esos valores almacenados.

**Spec:** `docs/specs/sp-adj-04/US-ADJ-4.1.md`

---

### US-ADJ-4.2 — Corregir orden de grilla STA: `orden_ascendente=True`
**Prioridad: Alta**
**Capa:** `shared/domain/value_objects/disciplina_descriptor.py`
**Issue:** DISC-04

La grilla STA real ordena de menor AP a mayor AP (ascendente), igual que las disciplinas
de distancia. El dataset Buenos Aires 2025 lo confirma: AP=30s va primero, AP=330s va último.
La app tiene `orden_ascendente=False` para STA, lo que invierte la grilla.

**Cambio:**
```python
# Antes
if disciplina.es_tiempo():
    return cls(..., orden_ascendente=False)  # mayor AP primero — INCORRECTO

# Después
if disciplina.es_tiempo():
    return cls(..., orden_ascendente=True)   # menor AP primero — igual que distancia
```

**Impacto:** cambio de una línea en `DisciplinaDescriptor.para()`. Requiere actualizar
todos los tests que validan el orden de grilla STA (verificar que usen AP=menor → mayor).

**Spec:** `docs/specs/sp-adj-04/US-ADJ-4.2.md`

---

### US-ADJ-4.3 — Renombrar `JUVENIL → JUNIOR` en enum `Categoria`
**Prioridad: Media**
**Capa:** `registro/domain/value_objects/categoria.py` + referencias
**Issue:** DISC-07

El estándar AIDA denomina esta categoría `JUNIOR`. El dataset usa `JUNIOR`. La app
usa `JUVENIL`, violando el lenguaje ubicuo del dominio.

**Cambio:**
```python
# Antes
JUVENIL_MASCULINO = "JUVENIL_MASCULINO"
JUVENIL_FEMENINO  = "JUVENIL_FEMENINO"

# Después
JUNIOR_MASCULINO = "JUNIOR_MASCULINO"
JUNIOR_FEMENINO  = "JUNIOR_FEMENINO"
```

**Impacto:** refactor de enum + todas las referencias en registro/ + tests. Cambio
de string value — requiere migración de datos almacenados.

**Spec:** `docs/specs/sp-adj-04/US-ADJ-4.3.md`

---

### US-ADJ-4.4 — Agregar campo `club` a aggregate `Atleta`
**Prioridad: Media**
**Capa:** `registro/domain/aggregates/atleta.py` + command + repo + API
**Issue:** DISC-05

`club` (escuela/club de freediving) es dato obligatorio en todos los documentos
oficiales del torneo: grilla de salida, resultados, reportes y certificados. El aggregate
`Atleta` no lo modela. Sin este campo, la app no puede generar documentación oficial.

**Cambios:**
- Agregar `club: str` a `Atleta` (obligatorio, validar no vacío — INV-A-05)
- Agregar `club: str` a `RegistrarAtletaCommand`
- Agregar columna `club` en `SqliteAtletaRepository`
- Agregar `club` en el schema de la API (`RegistrarAtletaRequest`, `AtletaResponse`)
- Propagar `club` a las salidas de grillas y reportes oficiales

**Spec:** `docs/specs/sp-adj-04/US-ADJ-4.4.md`

---

### US-ADJ-4.5 — Ranking y overall por categoría/género
**Prioridad: Alta**
**Capa:** `resultados/domain/` + `resultados/application/` + `resultados/infrastructure/`
**Issue:** DISC-01

BC Resultados produce un ranking flat que mezcla atletas de distintas categorías y sexos.
En ningún torneo de apnea real existe ese ranking. El ranking real es siempre por
`(disciplina, categoría)` y el overall del torneo también se publica por categoría/género,
donde `Categoria` ya encoda el sexo (`SENIOR_MASCULINO`, `MASTER_FEMENINO`, etc.).

**Cambios necesarios:**
1. `ResultadoFinal` (port): agregar campo `categoria: Categoria`
2. `EntradaRanking` (VO): agregar campo `categoria: Categoria`
3. `RankingCompetencia.calcular()`: agrupar por categoría, calcular ranking dentro de cada grupo
4. `ResultadosCompetenciaAdapter` (ACL): cruzar `atleta_id` con BC Registro para obtener `categoria`
   — requiere un nuevo port hacia BC Registro en `resultados/domain/ports/`
5. `ResultadosCalculados` (evento): incluir `categoria` en el payload de cada entrada
6. API `GET /resultados/{id}/ranking`: respuesta agrupada por categoría
7. `RankingOverall` / `CalcularOverall`: segmentar también el overall por categoría
8. API `GET /resultados/{torneo_id}/overall`: respuesta agrupada por categoría

La categoría viaja como dato del atleta desde BC Registro, atraviesa el ACL en
`resultados/infrastructure/`, y se incorpora al `ResultadoFinal` que procesa el dominio.
BC Resultados no "sabe" qué es un atleta — solo ve el `atleta_id` + su `categoria`.

El contrato HTTP acordado para ambos endpoints usa listas de categorías:

```json
{
  "calculado": true,
  "rankings": [
    {
      "categoria": "SENIOR_FEMENINO",
      "entradas": []
    }
  ]
}
```

No se usarán keys dinámicas por categoría en la respuesta JSON.

**Spec:** `docs/specs/sp-adj-04/US-ADJ-4.5.md`

---

### US-ADJ-4.6 — Value Object `TiempoAP` para parsear `MM:SS → segundos`
**Prioridad: Media**
**Capa:** `shared/domain/value_objects/` o `competencia/domain/value_objects/`
**Issue:** DISC-06

Los APs de STA y SPE se expresan en formato `MM:SS` en los documentos de la federación
(`"02:30"`, `"04:01"`, `"05:30"`). La app espera un `Decimal` en segundos. No hay
ninguna utilidad de dominio que haga esta conversión — queda en el llamador (seed,
script de ingesta, frontend) sin garantías.

Crear un Value Object que encapsule el parsing y la validación:

```python
@dataclass(frozen=True)
class TiempoAP:
    """AP expresado en formato MM:SS — convierte y valida a segundos."""
    segundos: Decimal

    @classmethod
    def desde_mmss(cls, texto: str) -> "TiempoAP":
        """Parsea 'MM:SS' o 'HH:MM:SS' a segundos. Valida formato."""
        ...

    @classmethod
    def desde_segundos(cls, valor: Decimal) -> "TiempoAP":
        """Constructor alternativo cuando el valor ya está en segundos."""
        ...
```

Ubicación: `shared/domain/value_objects/tiempo_ap.py` si se usa en más de un BC;
`competencia/domain/value_objects/` si es exclusivo de Competencia.

**Spec:** `docs/specs/sp-adj-04/US-ADJ-4.6.md`

---

## Cierre DoD

| Gate | Criterio |
|------|----------|
| `pytest` por US | Todos PASSED, cobertura ≥ 90% en domain/ y application/ |
| `CodeGuard` por US | Sin CRITICAL nuevos |
| `DesignReviewer` consolidado | 0 CRITICAL en SP-ADJ-04 |
| Dataset real procesable | El seed del UAT SP3 puede cargar atletas y competencia de Buenos Aires 2025 sin errores |

---

## Priorización

| Prioridad | US | Razón |
|-----------|-----|-------|
| 1 (Alta) | US-ADJ-4.1 | Disciplinas incorrectas — bloquean cualquier torneo real |
| 2 (Alta) | US-ADJ-4.2 | Orden STA invertido — la grilla generada es incorrecta |
| 3 (Alta) | US-ADJ-4.5 | Ranking sin categoría — el output es inútil operacionalmente |
| 4 (Media) | US-ADJ-4.3 | JUNIOR/JUVENIL — lenguaje ubicuo, fácil, alto impacto simbólico |
| 5 (Media) | US-ADJ-4.4 | Club en Atleta — dato obligatorio en grillas, reportes y documentos oficiales |
| 6 (Media) | US-ADJ-4.6 | TiempoAP — facilita seed/UAT, encapsula conocimiento del dominio |

---

## Secuencia recomendada

```
1. US-ADJ-4.1    ← shared/domain/ — renombrar disciplinas (base para todo lo demás)
2. US-ADJ-4.2    ← shared/domain/ — corregir orden STA (misma zona de código)
3. US-ADJ-4.3    ← registro/domain/ — renombrar JUVENIL→JUNIOR
4. US-ADJ-4.4    ← registro/ — agregar club a Atleta
5. US-ADJ-4.5    ← resultados/ — ranking y overall por categoría (la más compleja)
6. US-ADJ-4.6    ← shared/domain/ — TiempoAP parser
```

Las dos primeras (4.1 y 4.2) tocan `shared/domain/` y se pueden agrupar en el mismo
branch si el scope no lo desaconseja. US-ADJ-4.5 es la más compleja, impacta `ranking`
y `overall`, y debe ir sola.

---

## Descartado por ahora

- **DISC-08** (RP > AP sin documentar): la app ya lo permite correctamente — agregar
  nota en docstring, sin US formal
- **DISC-09** (coma decimal en PDFs): afecta solo al script de ingesta, no al dominio
- **DISC-10** (intervalo OT en tests): los tests usan valores configurables — no es un bug

---

*Creado: 2026-04-03 — basado en HITO-17 y análisis de discrepancias dataset Buenos Aires 2025*
