# Revisión UAT — INC-5.1
## Hallazgos Funcionales Durante Prueba Manual

**Fecha:** 2026-04-21
**Contexto:** UAT funcional del panel organizador `INC-5.1`
**Branch observado:** `develop`
**Servidores usados:** backend `http://127.0.0.1:8000` · frontend `http://127.0.0.1:5173`

---

## Hallazgos abiertos

| ID | Área | Hallazgo | Severidad | Estado |
|----|------|----------|-----------|--------|
| UAT-5.1-01 | Frontend organizador · Competencias | En torneos abiertos, al seleccionar `Ver competencias`, la lista aparece vacía aunque el torneo tiene disciplinas configuradas | Alta | Abierto |
| UAT-5.1-02 | Frontend organizador · Jueces | La UI permite asignar jueces antes de generar la grilla de tiempos oficiales | Alta | Abierto |
| UAT-5.1-03 | Frontend organizador · Torneo cancelado | Un torneo cancelado sigue mostrando información operativa registrada | Alta | Abierto |
| UAT-5.1-04 | Frontend organizador · Acciones de fase | Torneo en ejecución muestra botón `Iniciar Ejecución` en lugar de acción para finalizar competencias/pasar a premiación | Alta | Abierto |
| UAT-5.1-05 | Frontend organizador · Tabs por fase | En inscripción abierta, las pestañas `Grilla`, `Jueces` y `Ejecucion` aparecen habilitadas aunque el flujo todavía no corresponde | Alta | Abierto |
| UAT-5.1-06 | Frontend organizador · Ejecución por disciplina | Al pasar el torneo a ejecución, no se visualizan todas las disciplinas con detalle ni existe acción para habilitarlas individualmente | Alta | Abierto |
| UAT-5.1-07 | Frontend organizador · Cierre manual de disciplina | No existe opción para finalizar manualmente la prueba de una disciplina desde el panel organizador | Alta | Abierto |

---

## UAT-5.1-01 — `Ver competencias` muestra lista vacía en torneos abiertos

### Síntoma

Desde el panel del organizador, en un torneo con estado `INSCRIPCION_ABIERTA`, al usar la
acción `Ver competencias`, la pantalla `Competencias del torneo` muestra:

> Este torneo no tiene competencias configuradas.

El torneo sí tiene disciplinas configuradas.

### Evidencia local

Torneo observado en `data/torneo.db`:

```text
deccbf8f-7dca-4bfc-9351-e1d377c55a98
Smoke Test Open 2026
INSCRIPCION_ABIERTA
[{"disciplina": "DNF", "juez_id": "06ab133d-3698-4850-9d7c-7151e0d535a9"}]
```

Proyección `competencias_por_torneo` en `data/competencia.db` no contiene filas para ese
`torneo_id`.

### Causa probable

`frontend/src/pages/organizador/TorneoCompetenciasPage.tsx` carga la lista usando solo:

```typescript
fetchCompetenciasPorTorneo(torneoId)
```

Ese cliente consume:

```http
GET /competencia?torneo_id={id}
```

Ese endpoint devuelve competencias ya materializadas en el BC `competencia`, no las disciplinas
configuradas en el aggregate `Torneo`.

Para estados tempranos (`CREADO`, `INSCRIPCION_ABIERTA`, `PREPARACION`), el torneo puede tener
disciplinas configuradas en:

```http
GET /torneos/{torneo_id}/disciplinas
```

pero todavía no tener competencias creadas en `competencia.db`.

### Impacto

El organizador pierde visibilidad de las disciplinas configuradas del torneo desde la pantalla
`Ver competencias`. Esto afecta el flujo observable de `INC-5.1`, especialmente antes de generar
grillas.

### Acción propuesta

Modificar `TorneoCompetenciasPage` para componer ambas fuentes:

1. `GET /torneos/{torneo_id}/disciplinas` como fuente de disciplinas del torneo.
2. `GET /competencia?torneo_id={id}` como fuente opcional de competencias ya creadas.
3. Renderizar una fila/card por disciplina configurada.
4. Si existe `competencia_id`, habilitar `Ver auditoria`.
5. Si no existe `competencia_id`, mostrar estado `Competencia pendiente de configurar` y guiar al tab `Grilla`.

### Clasificación

- **Tipo:** bug funcional de composición frontend.
- **Capa:** `frontend/src/pages/organizador/`.
- **US relacionadas:** `US-5.1.2`, `US-5.1.4`, `US-5.1.6`.
- **Candidato:** fix previo a cierre de `INC-5.1`.

---

## UAT-5.1-02 — Jueces asignables antes de generar grilla de tiempos oficiales

### Síntoma

Durante la UAT se observa que el organizador puede asignar jueces desde el tab `Jueces` antes de
generar la grilla de tiempos oficiales.

### Regla funcional esperada

Los jueces solo deben poder asignarse luego de la generación de la grilla de tiempos oficiales.

La secuencia esperada para el organizador es:

1. Configurar disciplinas del torneo.
2. Generar grilla de tiempos oficiales.
3. Asignar jueces a las disciplinas ya configuradas con grilla.

### Causa probable

`US-5.1.5` implemento asignacion de jueces con la regla documentada hasta ese momento:

- backend permite asignar en estado `Preparacion`;
- frontend muestra el tab `Jueces` y el selector con base en disciplinas del torneo;
- no se verifica si existe competencia/grilla generada para cada disciplina.

La nueva regla operacional agrega una precondicion que no esta modelada en la UI actual:

```text
disciplina asignable a juez ⇔ disciplina tiene grilla de tiempos oficiales generada
```

### Impacto

El organizador puede dejar asignaciones de jueces sobre disciplinas que todavia no tienen grilla.
Eso habilita un flujo operativo desordenado y puede confundir al juez, porque su responsabilidad
queda definida antes de existir una programacion oficial de performances.

### Acción propuesta

Modificar el flujo de `JuecesPanel`/`TablaJueces` para:

1. Consultar competencias del torneo y estado/grilla por disciplina.
2. Habilitar selector de juez solo si la disciplina tiene competencia/grilla generada.
3. Mostrar estado bloqueado por fila: `Generar grilla antes de asignar juez`.
4. Mantener visible la asignacion existente, pero bloquear cambios si no hay grilla.
5. Evaluar si la precondicion tambien debe reforzarse en backend para evitar llamadas directas a
   `PUT /torneos/{torneo_id}/disciplinas/{disciplina}/juez` fuera de secuencia.

### Clasificación

- **Tipo:** bug/regla funcional faltante.
- **Capa:** `frontend/src/components/organizador/JuecesPanel.tsx` y posiblemente `torneo/api`.
- **US relacionadas:** `US-5.1.4`, `US-5.1.5`.
- **Candidato:** fix previo a cierre de `INC-5.1`.

---

## UAT-5.1-03 — Torneo cancelado muestra información operativa registrada

### Síntoma

Durante la UAT se observa que un torneo con estado `CANCELADO` sigue permitiendo ver informacion
operativa ya registrada en el panel organizador.

### Regla funcional esperada

Un torneo cancelado no debe mostrar la informacion registrada como si siguiera formando parte del
flujo operativo activo.

La cancelacion debe dejar el torneo en un estado terminal visible, sin exponer tabs/acciones que
sugieran continuidad del flujo de inscripcion, preparacion, grilla, jueces o ejecucion.

### Causa probable

`DetalleTorneoPage` renderiza los tabs del panel (`Detalle`, `Inscriptos`, `Grilla`, `Jueces`,
`Ejecucion`) sin aplicar una politica especial para estado `CANCELADO`.

Los paneles hijos cargan informacion por `torneoId` independientemente del estado del torneo:

- inscriptos;
- grilla/competencias;
- jueces asignados;
- monitor de ejecucion.

### Impacto

El organizador puede interpretar que un torneo cancelado sigue siendo operable o auditable desde
el flujo normal de gestion. Esto rompe la expectativa de estado terminal y puede exponer datos
operativos que deberian quedar ocultos o reemplazados por un mensaje de cancelacion.

### Acción propuesta

Definir e implementar una politica de UI para `CANCELADO`:

1. En `DetalleTorneoPage`, si `estado === "CANCELADO"`, mostrar solo resumen basico del torneo y
   estado cancelado.
2. Ocultar o deshabilitar tabs operativos (`Inscriptos`, `Grilla`, `Jueces`, `Ejecucion`).
3. Mostrar mensaje explicito: `Torneo cancelado`.
4. Mantener solo acciones permitidas por dominio, si existieran.
5. Verificar si endpoints backend tambien deben rechazar lecturas operativas para torneo cancelado
   o si la restriccion es solamente de UI.

### Clasificación

- **Tipo:** bug funcional/regla de estado terminal faltante.
- **Capa:** `frontend/src/pages/organizador/DetalleTorneoPage.tsx` y paneles hijos.
- **US relacionadas:** `US-5.1.2`, `US-5.1.3`, `US-5.1.4`, `US-5.1.5`, `US-5.1.6`.
- **Candidato:** fix previo a cierre de `INC-5.1`.

---

## UAT-5.1-04 — Torneo en ejecución muestra acción incorrecta de fase

### Síntoma

En el torneo `UAT SP4 — Flujo de Performance`, la UI muestra que el torneo esta en fase de
ejecucion y que hay disciplinas en curso. Sin embargo, el panel de acciones mantiene disponible
el boton:

> Iniciar Ejecución

Esa accion no corresponde para un torneo que ya esta en ejecucion.

### Regla funcional esperada

Si el torneo esta en `EJECUCION`, no debe mostrarse `Iniciar Ejecución`.

La accion esperada para avanzar el flujo es:

> Finalizar competencias

o la accion equivalente que permita cerrar la ejecucion y pasar a `PREMIACION`, cuando las reglas
del dominio indiquen que corresponde.

### Evidencia local

Torneos UAT SP4 observados en `data/torneo.db`:

```text
UAT SP4 — Flujo de Performance | EJECUCION
```

Ademas, la UI del tab `Ejecucion` muestra disciplinas en curso, por lo que el estado operacional
visible contradice la accion ofrecida.

### Causa probable

`AccionesPanel` probablemente decide acciones disponibles a partir de un valor de estado que no
coincide con el enum real retornado por backend o no contempla correctamente `EJECUCION`.

Posibles causas a verificar:

- mismatch entre estados backend (`EJECUCION`) y estados frontend esperados (`EnEjecucion`,
  `En ejecución`, etc.);
- condicion incorrecta que muestra `iniciarEjecucion` fuera de `PREPARACION`;
- falta de accion explicita para pasar de `EJECUCION` a `PREMIACION`/finalizar competencias;
- endpoint `iniciar-premiacion` existe en `api/torneo.ts`, pero el panel no lo presenta en el
  estado correcto.

### Impacto

El organizador ve una accion invalida para la fase actual. Esto afecta directamente el DoD de
`INC-5.1`, porque el panel debe gestionar el ciclo de vida completo del torneo respetando las
restricciones del dominio.

### Acción propuesta

Revisar `frontend/src/components/organizador/AccionesPanel.tsx`:

1. Confirmar nombres exactos de estados retornados por `torneo/api`.
2. Mostrar `Iniciar Ejecución` solo cuando `estado === "PREPARACION"` y se cumplan precondiciones.
3. Mostrar accion de finalizacion/premiacion cuando `estado === "EJECUCION"`.
4. Validar la llamada a `iniciarPremiacion(torneoId)` o endpoint equivalente.
5. Agregar manejo visual para caso de disciplinas aun no finalizadas, si backend rechaza la
   transicion.

### Clasificación

- **Tipo:** bug funcional de acciones por estado.
- **Capa:** `frontend/src/components/organizador/AccionesPanel.tsx`.
- **US relacionadas:** `US-5.1.2`, `US-5.1.6`.
- **Candidato:** fix previo a cierre de `INC-5.1`.

---

## UAT-5.1-05 — Tabs operativas habilitadas durante inscripción abierta

### Síntoma

Durante la UAT se observa que, mientras el torneo está en estado `INSCRIPCION_ABIERTA`, el panel
del organizador mantiene habilitadas las pestañas operativas:

- `Grilla`
- `Jueces`
- `Ejecucion`

### Regla funcional esperada

Mientras el estado del torneo sea `INSCRIPCION_ABIERTA`, esas pestañas no deben estar habilitadas.

La fase de inscripción debe permitir al organizador revisar el detalle del torneo y la inscripción
de atletas, pero no operar grilla, asignación de jueces ni ejecución de competencias.

### Causa probable

`DetalleTorneoPage` renderiza las tabs del panel con una lista fija:

```typescript
const TABS = ['Detalle', 'Inscriptos', 'Grilla', 'Jueces', 'Ejecucion'] as const
```

La habilitación de tabs no parece depender del estado real del torneo retornado por backend.

### Impacto

El organizador puede acceder a pantallas que pertenecen a fases posteriores antes de cerrar la
inscripción. Esto rompe la secuencia operacional esperada y puede disparar errores secundarios,
como intentar generar grillas o asignar jueces antes de que el torneo esté en preparación.

### Acción propuesta

Modificar `DetalleTorneoPage` para aplicar una política de tabs por fase:

1. Si `estado === "INSCRIPCION_ABIERTA"`, habilitar solo `Detalle` e `Inscriptos`.
2. Mostrar `Grilla`, `Jueces` y `Ejecucion` como deshabilitadas u ocultas.
3. Evitar que `activeTab` conserve una tab operativa si el torneo cambia o recarga en
   `INSCRIPCION_ABIERTA`.
4. Mantener la regla consistente con la política especial para `CANCELADO` registrada en
   `UAT-5.1-03`.

### Clasificación

- **Tipo:** bug funcional/regla de navegación por fase faltante.
- **Capa:** `frontend/src/pages/organizador/DetalleTorneoPage.tsx`.
- **US relacionadas:** `US-5.1.2`, `US-5.1.4`, `US-5.1.5`, `US-5.1.6`.
- **Candidato:** fix previo a cierre de `INC-5.1`.

---

## UAT-5.1-06 — Falta gestión maestro-detalle de ejecución por disciplina

### Síntoma

Al pasar el torneo a estado `EJECUCION`, el panel del organizador no muestra todas las disciplinas
del torneo con su descripción y detalle operativo. El tab `Ejecucion` solo funciona como monitor
de disciplinas ya iniciadas, pero no ofrece un flujo claro para que el organizador habilite cada
disciplina de manera individual ni gestione el ciclo de vida de ejecución de una disciplina
seleccionada.

### Regla funcional esperada

Cuando el torneo pasa a `EJECUCION`, el tab `Ejecucion` debe funcionar como una vista
maestro-detalle:

1. Primero muestra todas las disciplinas configuradas del torneo, con su descripción, juez asignado,
   estado de grilla, estado de ejecución y progreso resumido.
2. Al seleccionar una disciplina, el organizador accede al detalle operativo de esa prueba.
3. En el detalle se gestiona el ciclo de vida de ejecución de esa disciplina.

La habilitación de ejecución es individual por disciplina/prueba:

```text
torneo en EJECUCION + disciplina con grilla OT generada/confirmada + juez asignado
  -> organizador selecciona disciplina
  -> organizador habilita disciplina
  -> disciplina pasa a EnEjecucion
  -> juez puede ejecutar performances
```

El detalle de disciplina debe permitir, como mínimo:

- revisar la grilla OT;
- ver juez asignado;
- habilitar/iniciar la prueba;
- monitorear atleta actual, próximas performances y progreso;
- ver performances pendientes;
- finalizar manualmente la prueba si corresponde;
- ver estado final, hash/resultados cuando cierre.

### Aclaración de dominio

La disciplina se finaliza automáticamente cuando todas sus performances tienen resultado, DNS o
tarjeta final (`ROJA` o `BLANCA`). Esa regla automática sigue vigente y no reemplaza la necesidad
de que el organizador habilite el inicio de cada disciplina.

### Causa probable

El backend ya expone el endpoint:

```http
POST /competencia/{competencia_id}/iniciar
```

pero la UI del organizador no presenta una acción equivalente. `EjecucionPanel` consulta
competencias y muestra solo las que ya están en estado `EnEjecucion`; no compone una vista completa
de disciplinas pendientes, confirmadas, en ejecución y finalizadas, ni tiene un estado de selección
para entrar al detalle de una disciplina.

### Impacto

El organizador no tiene un punto operativo claro para iniciar cada prueba. Esto rompe el flujo real
de torneo: después de generar grillas y asignar jueces, no queda visible el paso que habilita al
juez a comenzar la disciplina ni el lugar donde se administra su avance hasta el cierre.

### Acción propuesta

Modificar el flujo de ejecución del organizador para:

1. Convertir `EjecucionPanel` en vista maestro-detalle.
2. En el maestro, mostrar todas las disciplinas del torneo, no solo las activas.
3. Para cada disciplina, mostrar descripción, juez asignado, estado de grilla, estado de competencia
   y progreso.
4. Al seleccionar una disciplina, abrir el detalle operativo de esa prueba.
5. En el detalle, agregar acción `Habilitar disciplina` o `Iniciar prueba` cuando la disciplina
   tenga grilla OT confirmada y juez asignado.
6. Agregar wrapper frontend para `POST /competencia/{competencia_id}/iniciar`.
7. Bloquear la acción con mensaje claro si falta grilla confirmada o juez asignado.
8. Integrar en el mismo detalle la acción de finalización manual registrada en `UAT-5.1-07`.

### Clasificación

- **Tipo:** gap funcional de flujo operativo.
- **Capa:** `frontend/src/components/organizador/EjecucionPanel.tsx`,
  `frontend/src/api/competencia.ts`.
- **US relacionadas:** `US-5.1.5`, `US-5.1.6`.
- **Candidato:** fix previo a cierre de `INC-5.1`.

---

## UAT-5.1-07 — Falta opción de finalización manual de prueba por disciplina

### Síntoma

El panel del organizador no ofrece una opción para finalizar manualmente la prueba de una
disciplina.

### Regla funcional esperada

Además de la finalización automática cuando todas las performances tienen resultado, DNS o tarjeta
final (`ROJA` o `BLANCA`), el organizador debe contar con una acción explícita para finalizar la
prueba de una disciplina de forma manual.

### Causa probable

El modelo actual implementa finalización automática mediante la política P-08: al asignar tarjeta
o registrar DNS, si todas las performances están cerradas, se emite `CompetenciaFinalizada`.

No hay endpoint ni acción UI explícita para que el organizador solicite el cierre manual de una
disciplina desde el panel.

### Impacto

El organizador no puede expresar administrativamente que una prueba terminó desde la UI. Esto deja
el cierre de disciplina completamente implícito y dificulta operar o auditar el momento real de
finalización de la prueba.

### Acción propuesta

Definir e implementar flujo de cierre manual por disciplina:

1. Agregar acción `Finalizar prueba` en la tarjeta/fila de cada disciplina en `EjecucionPanel`.
2. Permitir la acción solo cuando no queden performances pendientes de resultado/DNS/tarjeta final.
3. Si quedan pendientes, mostrar detalle de bloqueo.
4. Evaluar si se reutiliza la lógica de `Competencia.finalizar()` detrás de un nuevo endpoint
   explícito o si el endpoint dispara la misma verificación P-08 existente.
5. Registrar claramente en auditoría si el cierre fue automático o solicitado manualmente por el
   organizador.

### Clasificación

- **Tipo:** gap funcional de operación y auditoría.
- **Capa:** `competencia/api`, `competencia/application`, `frontend/src/components/organizador/`.
- **US relacionadas:** `US-5.1.6`, posiblemente nueva US de ajuste post-UAT.
- **Candidato:** fix previo a cierre de `INC-5.1` o US de ajuste inmediatamente posterior.

---

## Pendientes de registrar

Agregar aquí los próximos problemas observados durante la UAT antes de corregirlos, para mantener
trazabilidad entre hallazgo, causa, fix y validación.
