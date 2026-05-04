# Diseño de Pruebas UAT Manual — INC-5.6 Resultados y Podios

| Campo | Valor |
|-------|-------|
| **Subproyecto** | SP5 — La Puesta en Marcha |
| **Incremento** | INC-5.6 |
| **US cubiertas** | US-5.6.1 a US-5.6.6 |
| **Fecha diseño** | 2026-04-28 |
| **Autor** | Victor Valotto |
| **Tipo de validación** | UAT funcional manual |

---

## Objetivo

Verificar de forma observable que el incremento `INC-5.6` cumple su DoD funcional:

1. al cerrar una disciplina, el organizador puede ver la tabla de ejecución ordenada por OT;
2. el ranking por disciplina muestra puntaje FAAS por categoría/género;
3. los podios por disciplina se presentan en 6 divisiones fijas;
4. el overall del torneo permanece bloqueado hasta cerrar todas las disciplinas y se publica correctamente cuando corresponde.

La validación se centra en comportamiento visible del producto, no en detalles internos
de implementación.

---

## Alcance

### Incluido

- Pantalla organizador `/organizador/resultados`
- Selector de torneo
- Selector de disciplina
- Tabla de ejecución (`US-5.6.5`)
- Podios por disciplina (`US-5.6.6`)
- Estado de disponibilidad de overall (`US-5.6.6`)
- Overall publicado con todas las disciplinas cerradas (`US-5.6.4` + `US-5.6.6`)

### Excluido

- Exactitud matemática exhaustiva del algoritmo FAAS a nivel de dominio
- Browser automation
- Performance/load
- Revalidación completa del ciclo de vida del torneo fuera de lo necesario para llegar a resultados

---

## Estrategia

La UAT se ejecuta en tres capas secuenciales:

### Capa 0 — Smoke de entorno

Confirmar antes de empezar:

- backend levantado y accesible;
- frontend levantado y accesible;
- login de organizador operativo;
- torneo de prueba visible;
- al menos una disciplina con competencia creada;
- datos de atletas disponibles en varias categorías.

Si esta capa falla, no continuar con la UAT funcional.

### Capa 1 — Validación focalizada de pantalla Resultados

Casos cortos y observables sobre `ResultadosPage`:

- cambio de disciplina;
- tabla por OT;
- datos parciales en ejecución;
- podios visibles solo al finalizar;
- 6 paneles fijos;
- estados vacíos;
- badges/posiciones;
- overall bloqueado o disponible.

### Capa 2 — Flujo demo integrado de SP5

Ejecutar un recorrido completo mínimo para comprobar que el incremento no solo funciona
aislado sino dentro del flujo real:

- torneo con atletas y AP;
- grilla generada;
- disciplina iniciada y luego finalizada;
- resultados visibles;
- cierre de todas las disciplinas;
- overall publicado.

---

## Entorno sugerido

| Componente | Sugerencia |
|-----------|------------|
| Backend | `uv run fastapi dev src/app.py` |
| Frontend | `npm run dev` en `frontend/` |
| Navegador | Chrome o Safari desktop |
| Roles | 1 organizador |
| Evidencia | capturas, notas breves por caso, archivo de hallazgos |

---

## Dataset mínimo recomendado

Para que la UAT sea valiosa, el torneo de prueba debe cubrir estos casos:

1. Dos disciplinas como mínimo.
2. Una disciplina en `Finalizada`.
3. Una disciplina en `EnEjecucion` o no finalizada.
4. Atletas repartidos en varias categorías:
   - `SENIOR_MASCULINO`
   - `SENIOR_FEMENINO`
   - `MASTER_MASCULINO`
   - `MASTER_FEMENINO`
   - `JUNIOR_MASCULINO`
   - `JUNIOR_FEMENINO`
5. Al menos una categoría sin participantes.
6. Al menos un empate en puntos dentro de una categoría.

Si no existe un fixture listo, conviene preparar un torneo UAT específico antes de la sesión.

---

## Casos UAT — Capa 0 Smoke

### UAT-5.6-SM-01 — Frontend y backend disponibles

**Precondición:** entorno levantado.

**Pasos:**
1. Abrir frontend.
2. Verificar que responde sin error visible.
3. Comprobar login de organizador.

**Esperado:**
- aplicación accesible;
- login exitoso;
- navegación al panel organizador disponible.

### UAT-5.6-SM-02 — Torneo y disciplinas visibles

**Pasos:**
1. Ir a `Resultados`.
2. Verificar listado de torneos.
3. Seleccionar torneo UAT.

**Esperado:**
- torneo visible;
- selector de disciplinas visible;
- no hay errores de carga al entrar.

---

## Casos UAT — Capa 1 Resultados

### UAT-5.6-01 — Selector de disciplina cambia la tabla

**Precondición:** torneo con al menos 2 disciplinas.

**Pasos:**
1. Abrir `Resultados`.
2. Seleccionar disciplina A.
3. Registrar los atletas visibles.
4. Cambiar a disciplina B.

**Esperado:**
- la tabla cambia;
- el encabezado refleja la disciplina activa;
- no quedan filas de la disciplina anterior.

### UAT-5.6-02 — Tabla de ejecución ordenada por OT

**Precondición:** disciplina con grilla generada.

**Pasos:**
1. Abrir una disciplina con varios atletas.
2. Comparar filas con OT esperados.

**Esperado:**
- filas ordenadas por OT ascendente;
- no se ordena por ranking ni por puntos.

### UAT-5.6-03 — Tabla parcial durante ejecución

**Precondición:** disciplina no finalizada.

**Pasos:**
1. Seleccionar disciplina en ejecución.
2. Observar atletas ya ejecutados y pendientes.

**Esperado:**
- atletas pendientes muestran `RP = —`, `Tarjeta = PENDIENTE`, `Puntos = —`;
- atletas ya ejecutados pueden tener RP/tarjeta pero sin puntos si aún no cerró.

### UAT-5.6-04 — Podios ocultos o bloqueados en disciplina no finalizada

**Precondición:** disciplina no finalizada.

**Pasos:**
1. Seleccionar disciplina en ejecución.
2. Ir a la sección `Podios`.

**Esperado:**
- no se muestran podios reales;
- aparece empty state de disponibilidad al cerrar la disciplina.

### UAT-5.6-05 — Podios por disciplina finalizada muestran 6 paneles

**Precondición:** disciplina finalizada con ranking calculado.

**Pasos:**
1. Seleccionar disciplina finalizada.
2. Observar sección `Podios`.

**Esperado:**
- aparecen exactamente 6 paneles:
  - `SENIOR M`
  - `SENIOR F`
  - `MASTER M`
  - `MASTER F`
  - `JUNIOR M`
  - `JUNIOR F`

### UAT-5.6-06 — Categorías vacías muestran “Sin participantes”

**Precondición:** alguna categoría sin atletas.

**Pasos:**
1. Abrir podios de disciplina finalizada.
2. Revisar paneles sin atletas.

**Esperado:**
- el panel existe igualmente;
- muestra `Sin participantes`.

### UAT-5.6-07 — Posiciones y badges correctos

**Precondición:** una categoría con al menos 3 atletas.

**Pasos:**
1. Abrir el panel de una categoría poblada.
2. Verificar orden visible y badge de cada posición.

**Esperado:**
- `1º` con badge oro;
- `2º` con badge plata;
- `3º` con badge bronce;
- posiciones siguientes con estilo muted.

### UAT-5.6-08 — Empate comparte posición

**Precondición:** dos atletas empatados en puntos dentro de la misma categoría.

**Pasos:**
1. Abrir panel con empate.
2. Revisar posición visible de ambos atletas.

**Esperado:**
- ambos muestran el mismo número de posición.

### UAT-5.6-09 — Overall bloqueado mientras faltan disciplinas

**Precondición:** torneo con disciplinas mixtas, no todas finalizadas.

**Pasos:**
1. Ir a sección `Overall`.

**Esperado:**
- aparece mensaje `Disponible al cerrar todas las disciplinas`;
- aparece contador `(N de M disciplinas cerradas)`.

### UAT-5.6-10 — Overall disponible con todas las disciplinas cerradas

**Precondición:** todas las disciplinas del torneo en `Finalizada`.

**Pasos:**
1. Cerrar o usar torneo con todas las disciplinas cerradas.
2. Abrir `Resultados`.
3. Ir a `Overall`.

**Esperado:**
- desaparece el estado bloqueado;
- aparecen 6 paneles de overall;
- cada panel muestra puntaje acumulado;
- categorías vacías conservan `Sin participantes`.

---

## Casos UAT — Capa 2 Flujo Integrado

### UAT-5.6-FL-01 — Cierre de disciplina publica resultados

**Pasos:**
1. Partir de torneo operativo con grilla y ejecución disponible.
2. Finalizar una disciplina.
3. Ir a `Resultados`.

**Esperado:**
- tabla con datos finales;
- podios disponibles sin acción manual adicional.

### UAT-5.6-FL-02 — Cierre completo del torneo publica overall

**Pasos:**
1. Finalizar disciplinas restantes.
2. Volver a `Resultados`.

**Esperado:**
- overall publicado automáticamente;
- contador bloqueado ya no aparece.

---

## Evidencia a recolectar

Por cada caso:

- `PASS / FAIL / N/A`
- fecha y hora
- observación breve
- captura si el hallazgo es visual o de flujo

Archivos sugeridos para la sesión:

- `quality/reports/uat/SP5/inc-5.6-ejecucion-manual.md`
- `.work/revision-sp5/06-hallazgos-uat-inc-5.6.md`

---

## Criterio de salida

La UAT de `INC-5.6` puede darse por satisfecha cuando:

1. El smoke de entorno pasa.
2. Los casos `UAT-5.6-01` a `UAT-5.6-10` están ejecutados.
3. Los hallazgos quedan clasificados.
4. No queda ningún hallazgo severo sin decisión explícita.

---

## Clasificación de hallazgos

Seguir la política del workflow:

- **Solo `frontend/`** → ajuste informal post-UAT.
- **Cualquier archivo en `src/`** → track formal con nueva US/spec y `/implement-us`.

Severidad sugerida:

- **Alta:** bloquea demo o invalida el resultado mostrado.
- **Media:** flujo recuperable pero confuso o incorrecto para el usuario.
- **Baja:** detalle visual, copy, consistencia menor.

---

## Riesgos conocidos al iniciar la sesión

1. El fixture puede no cubrir empates ni las 6 categorías.
2. `Overall` depende del estado real de cierre de disciplinas, no solo del ranking.
3. Existe un error de lint preexistente en `frontend/src/pages/atleta/portalData.ts`; no afecta directamente esta UAT, pero conviene no mezclarlo con hallazgos de resultados.

---

## Recomendación operativa

No arrancar por el flujo completo del torneo. Empezar por la pantalla `Resultados` con
un torneo/fixure preparado y luego pasar al flujo integrado. Eso reduce ruido y permite
detectar rápido si el problema está en:

- composición de datos;
- cierre de disciplina;
- publicación de overall;
- o setup del entorno.
