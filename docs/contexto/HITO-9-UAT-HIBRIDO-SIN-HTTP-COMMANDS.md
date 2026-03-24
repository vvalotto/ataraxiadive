# HITO-9 — UAT Híbrido: cuando el dominio no tiene endpoints de escritura

| Campo | Valor |
|-------|-------|
| **Documento** | HITO-9 — Análisis experimental |
| **Fecha** | 2026-03-24 |
| **Sprint** | SP1 — cierre formal |
| **Relacionado** | `BL-001` · `quality/reports/uat/SP1/` · `tests/uat/sp1/` |

---

## Contexto

Al cerrar SP1, se propuso ejecutar un UAT con Postman para evidenciar el DoD.
Al revisar el router del BC Competencia, se descubrió que **no existen endpoints POST**:
los comandos (`RegistrarAP`, `LlamarAtleta`, `RegistrarResultado`, etc.) se invocan
directamente por código en la capa Application — no están expuestos via HTTP.

Esto generó la pregunta: ¿cómo hacer un UAT observable y con evidencia cuando
el sistema no acepta input externo todavía?

---

## Hipótesis experimental activada

**H-9.1** — En proyectos IEDD con sprints tempranos focalizados en dominio (no en
interfaz), el UAT no puede ser "manual con herramienta HTTP". Necesita una estrategia
alternativa que mantenga la observabilidad sin comprometer la secuencia de capas.

---

## Observación

El BC Competencia en SP1 es un **dominio puro con proyecciones de lectura**.
Los endpoints GET (audit log, Read Models) son la ventana observable hacia el
Event Store — pero solo existen porque los tests de integración ya los ejercitan.

La solución que emergió fue un **UAT híbrido en dos capas**:

```
Capa 1 — Automatizada (pytest)
  Ejecuta el flujo completo via Application handlers.
  Verifica invariantes, Event Store y Read Models desde el código.
  No depende del servidor — es la fuente primaria de verdad.

Capa 2 — HTTP Manual (curl)
  Siembra una DB real con el mismo flujo (seed script).
  Verifica los endpoints GET del servidor levantado.
  Confirma que el stack completo funciona end-to-end.
```

---

## Hallazgos

**H-9.1 confirmada parcialmente.** La Capa 1 (pytest) es suficiente para verificar
el DoD técnico. La Capa 2 (HTTP) agrega valor de integración real: confirma que
el servidor arranca, la DB persiste en disco y los endpoints responden — cosas que
los tests con `tmp_path` no verifican.

**Hallazgo secundario:** el Event Store generó 20 eventos, no 18 como estimaba
el diseño. La diferencia: los 5 `APRegistrado` son eventos independientes antes
del flujo de ejecución. El diseño estimaba desde el primer `LlamarAtleta` — error
de cálculo en el design.md. La traza de 20 eventos es más fiel a la realidad:
todo lo que ocurre en el dominio queda registrado, incluyendo los APs previos.

---

## Patrón identificado: estructura UAT del proyecto

```
tests/uat/<spN>/
├── seed_competencia.py   ← siembra DB real con el flujo DoD
└── run_uat.sh            ← orquesta Capa 1 + seed + Capa 2

quality/reports/uat/<SPn>/
├── design.md             ← diseño de pruebas (qué, cómo, criterios)
├── uat_ids.json          ← IDs generados por el seed
├── capa1-pytest.txt      ← salida pytest -v
├── capa2-http.json       ← respuestas HTTP capturadas
└── report.md             ← reporte con resultado final
```

Esta estructura se replica en cada SP. El diseño es estático (no cambia entre
ejecuciones); el report documenta la ejecución concreta.

---

## Implicaciones para el experimento IEDD

1. **Capa 3 → Capa 5 sin Capa 4 HTTP completa:** IEDD no requiere que todos los
   endpoints estén disponibles para cerrar un SP. El DoD puede verificarse con
   tests de integración mientras la interfaz HTTP se completa en sprints posteriores.
   Esto valida que la secuencia de capas IEDD es coherente: el dominio puede estar
   "completo y verificado" antes de que la interfaz exista.

2. **El seed script como artefacto de trazabilidad:** el `seed_competencia.py` es
   una especificación ejecutable del escenario DoD. Documenta exactamente qué datos
   se usaron para la verificación — más preciso que una colección Postman, porque
   es código versionado con el proyecto.

3. **Evidencia formal sin GUI:** para un torneo de apnea real, el juez usaría
   una app móvil. En SP1, la evidencia es el Event Store + los tests. La app
   llega en SP4. El experimento demuestra que se puede tener confianza en el dominio
   antes de que exista la interfaz de usuario.

---

## Recomendación para SP2

- El UAT de SP2 ya tendrá endpoints POST (la grilla y los comandos se exponen via HTTP).
  La Capa 2 del UAT podrá ser un flujo HTTP completo, reemplazando el seed script.
- Mantener la misma estructura `tests/uat/sp2/` + `quality/reports/uat/SP2/`.
- El `design.md` de SP2 debería anticipar si los comandos estarán disponibles via HTTP
  o si el patrón híbrido se repite.

---

*2026-03-24 — HITO-9 — generado al cerrar SP1 con UAT ejecutado y evidencia capturada*
