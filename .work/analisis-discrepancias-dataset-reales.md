# Análisis de Discrepancias — Dataset Real vs. Modelo de la App

| Campo | Valor |
|-------|-------|
| **Fuente** | `data/datasets/buenos_aires_2025/` |
| **Competencia real** | Apnea Indoor Buenos Aires 2025 |
| **Disciplinas** | DBF, DNF, DYN, SPE, STA |
| **Atletas únicos** | 30 |
| **Entries (atleta × disciplina)** | 145 |
| **Fecha análisis** | 2026-04-03 |

---

## Issues identificados

### CRÍTICOS — funcionalidad incorrecta

---

#### DISC-01 — Ranking flat vs. ranking por categoría y sexo

**Comportamiento real:**
El ranking de un torneo de apnea se publica siempre segmentado por `(disciplina, sexo, categoría)`. En Buenos Aires 2025 hay rankings separados para: STA Femenino Junior, STA Femenino Senior, STA Femenino Master, STA Masculino Senior, STA Masculino Master, etc.

**Comportamiento actual de la app:**
`RankingCompetencia` mezcla todos los atletas de una disciplina en un único ranking flat, ignorando sexo y categoría. `EntradaRanking` y `ResultadoFinal` no tienen campo `categoria`.

**Evidencia:**
```
results.json:
  { "discipline": "STA", "sex": "FEMENINO", "rank": 1, "category": "JUNIOR", "name": "Guadalupe Fardi" }
  { "discipline": "STA", "sex": "FEMENINO", "rank": 1, "category": "SENIOR", "name": "María de los Milagros Montangie" }
  { "discipline": "STA", "sex": "FEMENINO", "rank": 1, "category": "MASTER", "name": "Alina Di Lernia" }
  # Tres atletas distintas con rank=1, cada una en su categoría
```

**Impacto:** BC Resultados no puede producir resultados válidos para un torneo real. El ranking que genera es inútil operacionalmente.

**Archivos afectados:**
- `src/resultados/domain/aggregates/ranking_competencia.py`
- `src/resultados/domain/value_objects/entrada_ranking.py`
- `src/resultados/domain/ports/resultados_competencia_port.py` → `ResultadoFinal`
- `src/resultados/infrastructure/repositories/resultados_competencia_adapter.py`

---

#### DISC-02 — Disciplina `DBF` no existe en el enum `Disciplina`

**Comportamiento real:**
DBF (Dynamic Bi-Fins) es una disciplina estándar AIDA practicada en competencias argentinas. Buenos Aires 2025 tiene 30 entries en DBF.

**Comportamiento actual de la app:**
El enum `Disciplina` tiene `DYNB = "DYNB"`. El acrónimo real de AIDA es `DBF`.

```python
# src/shared/domain/value_objects/disciplina.py — actual
DYNB = "DYNB"  # Dynamic Bi-Fins

# Debería ser
DBF = "DBF"   # Dynamic Bi-Fins — acrónimo estándar AIDA/CMAS
```

**Impacto:** Cualquier torneo real que incluya esta disciplina no puede cargarse en la app. Violación del lenguaje ubicuo (el dominio usa DBF, la app usa DYNB).

---

#### DISC-03 — Disciplina `SPE` no existe en el enum `Disciplina`

**Comportamiento real:**
SPE (Speed Endurance) es la disciplina de velocidad en apnea. Buenos Aires 2025 tiene 22 entries en SPE.

**Comportamiento actual de la app:**
El enum tiene `SPE2X50 = "SPE2X50"`. El nombre real usado en competencias es `SPE`.

```python
# actual
SPE2X50 = "SPE2X50"

# Debería ser
SPE = "SPE"  # Speed Endurance — acrónimo estándar
```

**Impacto:** Igual que DISC-02. Torneo con SPE no puede cargarse.

---

#### DISC-04 — Orden de grilla STA: la app usa descendente, la realidad es ascendente

**Comportamiento real:**
En Buenos Aires 2025, la grilla STA está ordenada de **menor AP a mayor AP** (ascendente):

```
12:00  AP=00:30  Pablo Sale         ← menor AP (30s)
12:00  AP=02:00  José Enjuto
12:00  AP=02:00  Sebastián Quintana
...
13:07  AP=05:00  Mauro Almada
13:15  AP=05:30  Diego Calvo        ← mayor AP (330s)
```

Lo mismo aplica para DBF (distancia): la grilla va de menor AP a mayor AP.

**Comportamiento actual de la app:**
`DisciplinaDescriptor` para STA tiene `orden_ascendente=False` (mayor AP primero). Esto produce una grilla invertida respecto a la realidad.

```python
# src/shared/domain/value_objects/disciplina_descriptor.py — actual
if disciplina.es_tiempo():
    return cls(..., orden_ascendente=False)  # INCORRECTO

# Debería ser (igual que distancia)
if disciplina.es_tiempo():
    return cls(..., orden_ascendente=True)   # menor AP primero
```

**Impacto:** La grilla STA generada por la app coloca primero a los mejores atletas (los que aguantan más), que es contrario al protocolo real del deporte. Afecta directamente la ejecución de cualquier competencia STA real.

**Nota:** Para distancia (DBF, DNF, DYN) la app sí tiene `orden_ascendente=True`, lo cual es correcto y coincide con el dataset.

---

### MEDIOS — datos faltantes en el modelo

---

#### DISC-05 — Club del atleta no está modelado

**Comportamiento real:**
Cada atleta pertenece a un club/escuela que aparece en todos los documentos oficiales del torneo (grilla, resultados, certificados).

```
athlete_index.json:
  { "name": "Alejandro Alperin", "club": "OHANA FREEDIVERS", ... }
  { "name": "Víctor Valotto",    "club": "REGATAS SANTA FE", ... }
```

**Comportamiento actual de la app:**
El aggregate `Atleta` no tiene campo `club`. Solo tiene: nombre, apellido, email, fecha_nacimiento, categoria, brevet.

**Impacto:** La app no puede generar grillas ni resultados con la información mínima requerida por la federación. El club es dato obligatorio en la documentación oficial.

---

#### DISC-06 — AP en formato MM:SS para STA y SPE — no hay conversión en el dominio

**Comportamiento real:**
Las APs de tiempo se registran en los PDFs oficiales en formato `MM:SS` (minutos:segundos):

```
STA: "00:30" (30s), "02:00" (120s), "03:15" (195s), "05:30" (330s)
SPE: "03:00" (180s)
```

**Comportamiento actual de la app:**
`RegistrarAP` recibe un `Decimal` en segundos. No hay ningún value object ni utilidad que convierta `MM:SS → segundos`.

**Impacto:** El punto de entrada de datos (sea manual o automatizado) debe hacer la conversión. Sin una utilidad de dominio explícita, esto es propenso a errores y queda fuera del modelo.

---

#### DISC-07 — Categoría JUNIOR vs. JUVENIL

**Comportamiento real:**
La categoría juvenil en competencias AIDA se denomina `JUNIOR` en los documentos oficiales.

```
participantes_por_categoria.csv:
  Guadalupe Fardi;JUNIOR;ESCUELA MARES;...
```

**Comportamiento actual de la app:**
El enum `Categoria` usa `JUVENIL_MASCULINO` / `JUVENIL_FEMENINO`.

```python
# src/registro/domain/value_objects/categoria.py
JUVENIL_MASCULINO = "JUVENIL_MASCULINO"
JUVENIL_FEMENINO  = "JUVENIL_FEMENINO"
```

**Impacto:** Violación del lenguaje ubicuo. El dominio usa `JUNIOR`, la app usa `JUVENIL`. Genera fricción al cargar datos reales y confusión en la interfaz.

---

### BAJOS — observaciones del dominio sin impacto funcional inmediato

---

#### DISC-08 — RP > AP es la norma en disciplinas de distancia

**Observación:**
En el dataset, prácticamente todos los atletas con tarjeta blanca en distancia tienen RP > AP. No es la excepción — es el comportamiento estándar del deporte (el AP es una declaración conservadora mínima).

```
DBF Sebastián Quintana: AP=112m → RP=140m  (+25%)
DNF Karina Menchini:    AP=100m → RP=128m  (+28%)
DBF María Laura Ortiz:  AP=90m  → RP=152m  (+69%)
```

**Estado en la app:**
`registrar_resultado` acepta cualquier `Decimal` positivo sin validar `rp <= ap`. El comportamiento es correcto, pero **no está documentado como invariante explícito**.

**Recomendación:** Agregar en el docstring de `registrar_resultado` y en la US-IEDD correspondiente que `rp > ap` es válido y esperable.

---

#### DISC-09 — Formato decimal con coma en resultados de distancia

**Observación:**
Los PDFs de la federación registran los resultados de distancia con coma decimal (notación europea):

```
"104,27" en lugar de "104.27"
```

**Estado en la app:**
No afecta la app directamente (no lee PDFs). Pero cualquier script de ingesta o importación de resultados necesita normalizar este formato.

**Recomendación:** Documentar este detalle en el script de seed/UAT para evitar errores silenciosos.

---

#### DISC-10 — Intervalo OT real difiere de los valores usados en tests

**Observación:**
| Disciplina | Intervalo real | Intervalo en tests SP2 |
|-----------|---------------|----------------------|
| DBF       | 7 min          | —                    |
| STA       | 8 min          | 9 min                |

El intervalo es configurable por competencia — no hay bug. Pero los escenarios de test deberían actualizarse para usar valores del dominio real.

---

## Resumen para priorización

| ID | Descripción | Severidad | BC afectado |
|----|-------------|-----------|-------------|
| DISC-01 | Ranking por categoría+sexo | CRÍTICO | Resultados |
| DISC-02 | Disciplina DBF → DYNB incorrecto | CRÍTICO | Shared / Torneo / Competencia |
| DISC-03 | Disciplina SPE → SPE2X50 incorrecto | CRÍTICO | Shared / Torneo / Competencia |
| DISC-04 | Orden grilla STA: descendente ≠ realidad | CRÍTICO | Competencia (shared) |
| DISC-05 | Club del atleta no modelado | MEDIO | Registro |
| DISC-06 | AP en MM:SS sin conversión en dominio | MEDIO | Competencia / Registro |
| DISC-07 | JUNIOR vs. JUVENIL | MEDIO | Registro |
| DISC-08 | RP > AP sin documentar como invariante | BAJO | Competencia |
| DISC-09 | Coma decimal en PDFs de federación | BAJO | Ingesta (fuera de app) |
| DISC-10 | Intervalo OT real vs. tests | BAJO | Tests |

**4 issues críticos** afectan la capacidad de la app de gestionar un torneo real.
**3 issues medios** afectan completitud del modelo de datos.
**3 issues bajos** son observaciones documentales o de configuración.
