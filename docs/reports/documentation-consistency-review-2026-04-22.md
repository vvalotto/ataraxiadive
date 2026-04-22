# Revisión de Consistencia Documental — 2026-04-22

## Alcance

Esta revisión contrasta la documentación funcional y técnica del proyecto contra
la implementación disponible en el repositorio al inicio de `INC-5.2`.

Incluye:

- estado de proyecto, baselines y plan SP5;
- documentación de arquitectura y diseño;
- matriz de trazabilidad funcional;
- contratos API observables en código;
- estado real del frontend PWA/offline-first;
- alcance implementado hasta `INC-5.1` y trabajo local de `US-5.2.1`.

No incluye correcciones sobre los documentos fuente. Este reporte es un
diagnóstico y una propuesta de saneamiento.

## Método

1. Inventario de documentación en `README.md`, `CLAUDE.md`, `.cm/`, `docs/`.
2. Lectura comparativa de planes, baselines, arquitectura y trazabilidad.
3. Verificación contra implementación en `src/`, `frontend/src/` y `tests/`.
4. Clasificación de hallazgos por severidad e impacto operativo.

## Resumen ejecutivo

La documentación del proyecto es abundante y preserva bien el razonamiento
histórico IEDD, pero hoy hay varias fuentes que se presentan como vigentes y
dicen cosas incompatibles entre sí.

El mayor riesgo no es técnico sino de gobernanza documental: un nuevo
desarrollador, un agente o una revisión externa puede tomar como actual un
documento desactualizado y ejecutar contra un mapa incorrecto del producto.

La prioridad recomendada es establecer una jerarquía explícita de fuentes:

1. `docs/plans/sp5/PLAN-SP5.md` como fuente de alcance vigente del SP5.
2. `.cm/baselines/` como fuente de estado de cierre por subproyecto.
3. `docs/architecture/` como arquitectura vigente.
4. `docs/design/` y `docs/dominio/` como modelado/historia, salvo documentos
   marcados explícitamente como actuales.

## Hallazgos

### H1 — Estado del proyecto inconsistente entre README, CLAUDE y baselines

**Severidad:** Alta

`README.md` informa que `SP4` y `SP5` están pendientes, y además dice que el
estado del producto quedó en `SP3`/`v0.4.0`.

Evidencia:

- `README.md:14` marca `SP4 — La Plataforma` como pendiente.
- `README.md:15` marca `SP5 — La Puesta en Marcha` como pendiente.
- `README.md:17` describe cierre en `SP3` con tag `v0.4.0`.
- `CLAUDE.md` documenta `SP4` cerrado el 2026-04-18 con tag `v0.5.0`.
- `.cm/baselines/BL-004.md` registra el cierre de `SP4`.
- `.cm/baselines/BL-005-draft.md` registra `SP5` en construcción con `INC-5.1`
  cerrado.

Impacto:

- El `README.md` es el primer punto de entrada del repositorio y hoy induce a
  operar como si el frontend y SP4 no existieran.
- Afecta onboarding, revisión documental y cualquier automatización que use el
  README como estado resumido.

Recomendación:

- Actualizar `README.md` para reflejar `SP4` cerrado y `SP5` en curso.
- Convertir el README en índice hacia `.cm/baselines/` y `docs/plans/sp5/`.

### H2 — Arquitectura offline-first declarada como no implementada, pero ya existe

**Severidad:** Alta

`docs/architecture/50-offline-sync.md` dice que el modo offline-first todavía no
aparece materializado con Service Worker, IndexedDB ni cola de sincronización.

Evidencia documental:

- `docs/architecture/50-offline-sync.md:35-37` declara ausencia de Service
  Worker, IndexedDB y cola de sincronización.

Evidencia de implementación:

- `frontend/src/sw.ts`
- `frontend/src/db/index.ts`
- `frontend/src/db/schema.ts`
- `frontend/src/db/queries.ts`
- `frontend/src/hooks/useComandoQueue.ts`
- `frontend/src/hooks/useGrillaQueue.ts`
- `frontend/src/hooks/usePrecarga.ts`
- `frontend/src/hooks/useSyncQueue.ts`

Impacto:

- La carpeta `docs/architecture/` se define a sí misma como arquitectura
  vigente, por lo que este desvío es especialmente costoso.
- Puede ocultar deuda real porque mezcla una afirmación obsoleta con una
  arquitectura objetivo todavía útil.

Recomendación:

- Reescribir la sección "Estado actual" como estado implementado en SP4.
- Separar claramente capacidades ya implementadas, límites conocidos y
  arquitectura objetivo futura.

### H3 — `docs/design/architecture.md` conserva contratos API obsoletos

**Severidad:** Alta

`docs/design/architecture.md` se presenta como arquitectura del sistema y
mantiene endpoints que ya no coinciden con la API real.

Evidencia documental:

- `docs/design/architecture.md:205` usa `/competencias/{id}/...` y
  `/competencias/{id}/finalizar`.
- `docs/design/architecture.md:206` usa endpoints separados bajo
  `/performances/{id}/...`.

Evidencia de implementación:

- `src/competencia/api/router.py:138` define `APIRouter(prefix="/competencia")`.
- Los endpoints reales son, entre otros:
  - `POST /competencia`
  - `GET /competencia`
  - `POST /competencia/{competencia_id}/generar-grilla`
  - `POST /competencia/{competencia_id}/confirmar-grilla`
  - `POST /competencia/{competencia_id}/iniciar`
  - `POST /competencia/{competencia_id}/registrar-resultado`
  - `POST /competencia/{competencia_id}/registrar-dns`
  - `POST /competencia/{competencia_id}/asignar-tarjeta`
  - `GET /competencia/{competencia_id}/grilla`
  - `GET /competencia/{competencia_id}/estado`

Impacto:

- Un consumidor técnico puede implementar contra rutas inexistentes.
- La documentación de diseño compite con la arquitectura vigente de
  `docs/architecture/`.

Recomendación:

- Marcar `docs/design/architecture.md` como histórico o superseded.
- Mover el contrato API actual a un documento canónico, o enlazar OpenAPI como
  fuente de verdad técnica.

### H4 — Roadmap SP5 desalineado entre `PLAN-SP5` y `BL-005-draft`

**Severidad:** Alta

El plan vigente de SP5 y el baseline draft usan una numeración y un alcance
distintos a partir de `INC-5.4`.

Evidencia:

- `docs/plans/sp5/PLAN-SP5.md:221-236` define `INC-5.5` como algoritmo de
  puntaje y rankings por categoría/género.
- `docs/plans/sp5/PLAN-SP5.md:240-251` define `INC-5.6` como Portal del Atleta.
- `docs/plans/sp5/PLAN-SP5.md:255-266` define `INC-5.7` como polish y
  demo-readiness.
- `.cm/baselines/BL-005-draft.md:42-44` define `INC-5.4` como algoritmo de
  puntaje FAAS, `INC-5.5` como resultados y premiación, e `INC-5.6` como UAT
  demo completo.

Impacto:

- El tracker y los commits pueden quedar asociados a incrementos incorrectos.
- Riesgo alto de generar specs o reportes con IDs válidos pero semántica
  equivocada.

Recomendación:

- Actualizar `BL-005-draft.md` para copiar la estructura de `PLAN-SP5`.
- Registrar explícitamente que Integración FAAS/importación CSV quedó fuera de
  scope SP5.

### H5 — Matriz de trazabilidad no refleja el alcance vigente del SP5

**Severidad:** Alta

`docs/traceability/matrix.md` fue actualizada el 2026-04-22, pero conserva
mapeos incompatibles con el plan vigente.

Evidencia:

- `docs/traceability/matrix.md:41` asigna `SP5` pendiente a Integración externa
  `RF-IG-01..04` y `RF-IN-07`.
- `docs/plans/sp5/PLAN-SP5.md:286-294` declara Integración FAAS/importación CSV
  fuera de scope SP5.
- `docs/traceability/matrix.md:69-71` ubica apto médico, constancia de pago y
  conflicto con BD FAAS fuera del incremento `INC-5.4` del plan actual.
- `docs/traceability/matrix.md:114-119` marca fórmula de puntos y rankings por
  categoría/género como definidos/implementados, mientras `PLAN-SP5` los ubica
  en `INC-5.5`.

Impacto:

- La trazabilidad deja de ser confiable para planificar el trabajo restante.
- Puede producir una falsa sensación de cobertura funcional.

Recomendación:

- Reconciliar la matriz contra `PLAN-SP5`.
- Distinguir "definido conceptualmente", "implementado técnicamente" y
  "expuesto en producto final".
- Marcar `RF-IG-01..04` como futuro/fuera de alcance SP5.

### H6 — `docs/architecture/README.md` lista una estructura objetivo que ya no existe

**Severidad:** Media

El README de arquitectura se declara como descripción vigente, pero su estructura
objetivo lista nombres antiguos.

Evidencia:

- `docs/architecture/README.md:50-64` lista `04-runtime-interactions.md`,
  `05-deployment-view.md`, `06-cross-cutting-concerns.md` y
  `07-offline-sync.md`.
- La carpeta real usa documentos como `30-runtime-interactions.md`,
  `40-cross-cutting-concerns.md` y `50-offline-sync.md`.

Impacto:

- Menor que los hallazgos anteriores, pero deteriora la confianza en la carpeta
  que se supone canónica.

Recomendación:

- Actualizar la estructura documentada con los nombres reales.
- Si existen documentos planificados no creados, listarlos en una sección
  separada de pendientes.

### H7 — BC Competencia documenta un `Participante ACL`/entidad local que no aparece como tal

**Severidad:** Media

La documentación arquitectónica de Competencia describe un `Participante ACL`
que traduce `AtletaInscripto` a `Participante` local. La implementación actual
usa puertos, adaptadores y proyecciones, pero no se observa una entidad
`Participante` en `src/competencia/domain/entities`.

Evidencia documental:

- `docs/architecture/10-bc-competencia.md:92-94` muestra `Participante ACL`.
- `docs/design/architecture.md:212` describe `ParticipanteACL`.

Evidencia de implementación:

- `src/competencia/domain/entities/` contiene `grilla_de_salida.py` y
  `__init__.py`.
- No hay archivo de entidad `participante` en esa carpeta.

Impacto:

- El diseño documentado parece más explícito que el código real.
- Puede ser deuda de documentación o deuda de modelado; requiere decisión.

Recomendación:

- Verificar si el concepto vive con otro nombre en DTOs/proyecciones.
- Si el diseño actual es correcto, actualizar el documento para hablar de
  puertos/adaptadores/proyecciones reales.
- Si el documento expresa una intención vigente, abrir deuda técnica para
  materializar el ACL como componente explícito.

### H8 — Documentos históricos no están claramente marcados como históricos

**Severidad:** Media

Hay documentos de dominio, diseño y specs tempranas que contienen decisiones,
preguntas o rutas anteriores. Esto es valioso para IEDD, pero algunos pueden ser
leídos como estado actual.

Ejemplos:

- `docs/dominio/05-requerimientos_funcionales.md` conserva preguntas y
  pendientes de elicitación originales.
- Specs antiguas mencionan rutas del tipo `/competencias`.
- Documentos de diseño de SP3/SP4 mezclan objetivo, estado de ese momento y
  arquitectura que luego evolucionó.

Impacto:

- No es un error preservar historia; el problema es no etiquetar qué documentos
  son históricos y cuáles son operativos.

Recomendación:

- Agregar banner estándar: `Histórico`, `Vigente`, `Superseded` o `Referencia`.
- Crear un índice documental con fuente canónica por tema.

## Alineaciones correctas observadas

- `CLAUDE.md` y `.cm/baselines/BL-004.md` reflejan el cierre de SP4.
- `docs/plans/sp5/PLAN-SP5.md` describe de forma coherente el alcance actual de
  SP5 y sus dependencias.
- `docs/architecture/15-bc-notificaciones.md` distingue correctamente email
  implementado con Resend y push como evolución futura.
- La deuda de testing frontend está documentada en reportes/waivers; no aparece
  como inconsistencia oculta.
- Las specs recientes de `US-5.2.1` y `US-5.2.2` están alineadas con el
  incremento `INC-5.2`.

## Matriz resumida

| Área | Documento principal | Estado frente a implementación | Acción recomendada |
|------|---------------------|-------------------------------|--------------------|
| Estado del proyecto | `README.md` | Desactualizado | Corregir primero |
| Estado operativo | `CLAUDE.md` | Mayormente vigente | Mantener como índice operativo |
| Baseline SP4 | `.cm/baselines/BL-004.md` | Vigente | Usar como cierre canónico |
| Baseline SP5 | `.cm/baselines/BL-005-draft.md` | Parcialmente desalineado | Reconciliar contra `PLAN-SP5` |
| Plan SP5 | `docs/plans/sp5/PLAN-SP5.md` | Vigente | Fuente de alcance |
| Arquitectura vigente | `docs/architecture/` | Parcialmente vigente | Corregir offline/estructura/Competencia |
| Diseño histórico | `docs/design/` | Mixto | Etiquetar o superseder documentos |
| Dominio original | `docs/dominio/` | Histórico | Etiquetar como fuente de elicitación |
| Trazabilidad | `docs/traceability/matrix.md` | Desalineada con SP5 | Recalibrar por RF |

## Orden sugerido de saneamiento

1. Actualizar `README.md` y `BL-005-draft.md`.
2. Corregir `docs/architecture/50-offline-sync.md` y
   `docs/architecture/README.md`.
3. Marcar `docs/design/architecture.md` como histórico/superseded o actualizarlo
   completamente.
4. Reconciliar `docs/traceability/matrix.md` con `PLAN-SP5`.
5. Agregar banners de vigencia a documentos históricos de `docs/dominio/` y
   specs antiguas.
6. Crear un índice "fuentes canónicas" para evitar ambigüedad futura.

## Decisión pendiente

Antes de corregir documentos fuente conviene decidir si la estrategia documental
será:

1. **Corrección mínima:** actualizar solo documentos que hoy bloquean trabajo
   operativo (`README`, `BL-005-draft`, `offline-sync`, trazabilidad).
2. **Saneamiento completo:** además de lo anterior, etiquetar todo documento
   histórico y consolidar un índice canónico.

Para continuar con `INC-5.2`, la opción mínima alcanza. Para preparar una
revisión externa del proyecto, conviene el saneamiento completo.
