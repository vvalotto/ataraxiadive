# HITO-25 — La restricción técnica produce mejor arquitectura que la convención: offline-first como driver de abstracción involuntario

| Campo | Valor |
|-------|-------|
| **Documento** | HITO-25 — Hallazgo metodológico durante revisión cierre SP4 |
| **Fecha** | 2026-04-16 |
| **Sprint** | SP4 — Revisión pre-BL-004 |
| **Relacionado** | `frontend/src/hooks/` · `frontend/src/pages/` · INC-4.3 (interfaz juez) · INC-4.4 (offline-first) · INC-4.2 (fundación frontend) · `docs/design/offline-first.md` · `.work/revision-sp4/03-analisis-frontend.md` |

---

## Contexto

Durante la revisión de calidad del frontend pre-BL-004 se analizaron las violaciones
de capas en `frontend/src/`. El análisis reveló una asimetría inesperada entre las
dos interfaces del sistema:

**Interfaz del juez** — bien abstraída:
```
GrillaPage → usePrecarga() → fetchGrillaCompetencia()
GrillaPage → useComandoQueue() → db/queries + api/
GrillaPage → useSyncQueue() → db/queries + api/
```

**Interfaz del organizador** — sin abstracción:
```
TorneoCompetenciasPage → fetchCompetenciasPorTorneo()  ← directo
DashboardPage → fetchTorneos()                          ← directo
LoginPage → loginApi()                                  ← directo
```

Las páginas del organizador acceden a `api/` directamente, sin hooks intermedios.
La arquitectura esperada — páginas que orquestan hooks, hooks que acceden a datos —
se cumple en la interfaz del juez pero no en la del organizador.

---

## Qué reveló la comparación

Las dos interfaces fueron implementadas por el mismo equipo, en el mismo sprint, con
las mismas convenciones documentadas. Sin embargo, la calidad arquitectónica es distinta.

La diferencia no fue intención ni disciplina. Fue **la presencia o ausencia de una
restricción técnica concreta**.

La interfaz del juez tenía una restricción no negociable: **operar sin conexión a
internet** (AC-DS-03). Para cumplirla, cada acceso a datos tuvo que pasar por una capa
intermedia capaz de decidir entre servidor e IndexedDB. Esa capa son los hooks.

La restricción no dijo "usá hooks". Dijo "necesitás caché offline". Los hooks
emergieron como la abstracción natural para encapsular esa lógica.

La interfaz del organizador no tenía esa restricción. El camino de menor resistencia —
llamar directamente a `fetchTorneos()` desde la página — fue suficiente para cumplir
la funcionalidad. Sin restricción que lo impidiera, la abstracción no apareció.

---

## El aprendizaje central

> Las restricciones técnicas no negociables producen abstracciones arquitectónicas
> más robustas que las convenciones documentadas.

La convención "las páginas no deben llamar a api/ directamente" existía implícitamente
en el proyecto — la estructura de directorios y el patrón de hooks del juez la
sugerían. Sin embargo, no fue suficiente para que las páginas del organizador la
adoptaran.

La restricción offline-first sí fue suficiente, pero no porque fuera más explícita.
Fue suficiente porque **hacer la cosa "incorrecta" rompía la funcionalidad**. La
consecuencia era inmediata y visible. El desarrollador no podía ignorarla.

Una convención de estilo que se viola no rompe nada. Una restricción técnica que se
viola rompe el feature.

---

## Implicancia para IEDD y el experimento

Este hallazgo toca la Capa 1 de IEDD (Dominio) y la hipótesis H-4 del experimento
(calidad del código como consecuencia de la especificación).

En IEDD, los atributos de calidad (AC-DS-03 en este caso) se documentan en
`docs/dominio/03-atributos_calidad.md`. La hipótesis implícita es que documentar
el atributo es suficiente para que guíe el diseño. Este hallazgo matiza esa hipótesis:

> Un atributo de calidad produce su impacto arquitectónico completo solo cuando
> su incumplimiento es detectado inmediatamente — ya sea por tests, por el runtime
> o por la imposibilidad de cerrar la US.

AC-DS-03 fue detectado porque la US de offline-first (INC-4.4) tenía criterios de
aceptación verificables: el juez debía poder operar sin red. El organizador no tenía
ese gate equivalente — sus páginas pasan los tests aunque accedan a api/ directamente.

**Consecuencia práctica para futuros proyectos IEDD:**
Los atributos de calidad que no tienen criterios de aceptación verificables en
las US-IEDD quedan como convenciones. Los que sí los tienen, se convierten en
restricciones. Solo las restricciones garantizan la abstracción.

---

## La asimetría como detector de deuda

La diferencia entre las dos interfaces no es grave — las páginas del organizador
funcionan correctamente, y en SP5 hay pocas razones para que necesiten operar offline.
La violación es de consistencia, no de correctitud.

Sin embargo, la asimetría es útil como señal: **donde no hubo restricción, no hubo
abstracción**. Si en SP5 el organizador necesitara algo como caché o estado compartido
entre páginas, el costo de agregar esa capa sería mayor que si los hooks ya existieran.

Esto sugiere una regla heurística para el diseño de US-IEDD:

> Antes de implementar una interfaz de usuario, preguntar: ¿existe algún requisito
> no funcional (offline, caché, reintentos, estado compartido) que justifique una
> capa de abstracción entre la página y el acceso a datos? Si la respuesta es sí,
> definir esa capa en el plan de implementación, no esperar a que la restricción
> aparezca durante el desarrollo.

---

## Conexión con hallazgos anteriores

`HITO-19` documentó que los ajustes del DesignReviewer son más efectivos como
US-IEDD que como SP-ADJ, porque los quality gates integrados en el flujo se cumplen
por construcción.

Este hallazgo es análogo pero en frontend: los quality gates arquitectónicos se
cumplen por construcción cuando la restricción técnica los hace inevitables. No
se cumplen por convención cuando violarlos no tiene consecuencias inmediatas.

La tesis que emerge:

> En un sistema desarrollado con IA asistida, las restricciones con consecuencias
> inmediatas son más efectivas que las convenciones documentadas para garantizar
> calidad arquitectónica. El rol de IEDD es convertir atributos de calidad en
> restricciones verificables — no solo en documentación.

---

## Acciones incorporadas

- [x] Asimetría documentada en `03-analisis-frontend.md` (revisión pre-BL-004)
- [x] Issues FE-ARCH-01 y FE-ARCH-02 registrados como candidatos a SP-ADJ-06
- [ ] Evaluar si las US-IEDD del organizador en SP5 deben incluir criterios de
  aceptación que fuercen la abstracción en hooks (ej: "la página no debe importar
  directamente de api/")
- [ ] Revisar `docs/dominio/03-atributos_calidad.md`: ¿qué atributos tienen criterios
  verificables en US-IEDD y cuáles son solo documentación?

---

*Registrado durante revisión de calidad pre-BL-004 — cuando el análisis de capas del frontend reveló que la restricción técnica había producido la abstracción que la convención no logró*
