# PLAN-SP6 — Validación, Ajustes y Despliegue

> Estado documental: vigente  
> Última actualización: 2026-05-03  
> Baseline objetivo: `v1.0.0` (BL-006)

---

## 1. Contexto y Objetivos

SP6 cierra el ciclo de desarrollo de AtaraxiaDive v1.0. Sus tres ejes son:

1. **Ajustes** — corregir defectos y mejoras UX identificados en validación SP5
2. **Validación E2E** — UAT completo con los tres roles sobre datos reales
3. **Despliegue** — configurar y publicar el entorno productivo

El insumo principal son los hallazgos de validación de SP5 organizados por rol,
más la deuda técnica pendiente de quality gates.

---

## 2. Hallazgos por Rol

### 2.1 Organizador

| ID | Página | Hallazgo | Fuente |
|----|--------|----------|--------|
| UI-ORG-01 | Inicio | Lista torneos sin orden por fecha + falta mostrar fecha del torneo | Validación SP5 |
| UI-ORG-02 | Panel torneo → Alertas activas | Eliminar botón "Resolver" — solo el juez resuelve alertas | Validación SP5 |
| UI-ORG-03 | Inscriptos | Columna categoría muestra clave técnica; título "Disciplina" → "ANUNCIO" | Validación SP5 |
| UI-ORG-04 | Grilla | Título de columna AP → "Anuncios" | Validación SP5 |
| UI-ORG-05 | Resultados | Podios y overall → mover a página propia; columna AP → "Anuncios"; marcas en mm:ss; eliminar columna "PTS FAAS"; "línea" → número de andarivel | Validación SP5 |
| UI-ORG-06 | Jueces | Eliminar componentes "Cobertura Operativa" y "Estado de Asignación"; en fila del juez: solo selector, sin texto nombre | Validación SP5 |
| UI-ORG-07 | Nuevo torneo | Agregar selección de categorías JUNIOR / SENIOR / MASTER | Validación SP5 |
| UI-ORG-08 | — (nueva) | Crear página de Podios (contenido separado de Resultados) | Validación SP5 |

---

### 2.2 Juez

| ID | Componente | Hallazgo | Severidad | Fuente |
|----|-----------|----------|-----------|--------|
| UI-JUE-01 | Inicio juez | Renombrar "Mis disciplinas" → "Mis asignaciones"; datos del torneo primero; eliminar botón Password; "En línea" en header de Mis asignaciones | Media | Validación SP5 |
| UI-JUE-02 | Flujo performance | Cambiar secuencia: finalizar performance → asignar tarjeta → confirmar marca | Alta | Validación SP5 |
| MUX-01 | `RpSelector.tsx` | Keypad fuera de región visible en móvil (compactar padding/gaps) | Media | mejoras-ux.md |
| MUX-02 | `StepTarjeta.tsx` | Botones de tarjeta sin color identificatorio cuando no están seleccionados | Alta | mejoras-ux.md |
| MUX-03 | `GrillaPage.tsx` | El atleta SIGUIENTE no aparece primero — ordenar por prioridad de estado | Alta | mejoras-ux.md |
| MUX-04 | `usePerformanceFlow.ts` | **BUG:** botón "Confirmar BKO" nunca se habilita — `canSubmitBko` chequea campo eliminado | Crítica | mejoras-ux.md |
| MUX-05 | `PerformanceFlowPage.tsx` | Pantalla "completada" siempre en verde — debe reflejar color de la tarjeta asignada | Media | mejoras-ux.md |
| MUX-06 | Paso 5 (flujo juez) | AtletaCard completa ocupa espacio del RpSelector | Baja | mejoras-ux.md |
| MUX-07 | Tarjeta amarilla | UI de revisión demasiado compleja | Media | mejoras-ux.md |
| MUX-08 | Disciplinas STA | Marcas no se muestran en formato mm:ss | Media | mejoras-ux.md |

---

### 2.3 Atleta

| ID | Página | Hallazgo | Severidad | Fuente |
|----|--------|----------|-----------|--------|
| UI-ATL-01 | Inicio | "En línea" en cabecera; eliminar cartel "Hola"; si hay torneos en curso: mostrar disciplinas ordenadas (próxima → posteriores → realizadas) antes del componente principal | Media | Validación SP5 |
| UI-ATL-02 | Inscripción | Incluir declaración de AP de la disciplina seleccionada en el formulario | Alta | Validación SP5 |
| RF-IN-05 | Inscripción (backend) | Persistencia de apto médico — UI hecha, backend pendiente | Alta | matrix.md — deuda técnica |
| RF-IN-06 | Inscripción (backend) | Persistencia de constancia de pago — UI hecha, backend pendiente | Alta | matrix.md — deuda técnica |

> Nota: quedan ajustes adicionales de atleta identificados para trabajar con dinámica vibe coding (por definir durante INC-6.3).

---

### 2.4 Compartido

| ID | Área | Hallazgo | Prioridad | Fuente |
|----|------|----------|-----------|--------|
| RF-NT-02 | Notificaciones | Recordatorio al atleta cuando se acerca el plazo de AP — definido, sin implementar | Media | matrix.md |
| RF-NT-03 | Notificaciones | Notificaciones a juez u organizador durante ejecución — marcado como futuro | Baja | matrix.md |

---

### 2.5 Sistema

#### ArchitectAnalyst — Tendencia BL-004 → BL-005

| Módulo | BL-004 | BL-005 | Tendencia | Estado |
|--------|--------|--------|-----------|--------|
| `competencia/domain/aggregates` | DependencyCycle=2 CRITICAL | DependencyCycle=2 CRITICAL | = estable | ⚠️ No resuelto en SP5 |
| `competencia` (BC) | D=0.62 CRITICAL | D=0.46 WARNING | ↓ mejora | ✅ Salió de critical |
| `torneo` (BC) | D=0.64 CRITICAL | D=0.48 WARNING | ↓ mejora | ✅ Salió de critical |
| `identidad` (BC) | D=0.87 CRITICAL | D=0.67 CRITICAL | ↓ mejorando | 🔄 En progreso |
| `registro` (BC) | D=0.56 CRITICAL | D=0.59 CRITICAL | ↑ degradando | ⚠️ Empeora |
| `shared` (BC) | D=0.63 CRITICAL | D=0.63 CRITICAL | = estable | ⚠️ Sin cambio |
| Warnings totales | 55 | 61 | ↑ +6 | Instability en routers/apis |

#### Hallazgos pendientes

| ID | Módulo | Hallazgo | Prioridad | Fuente |
|----|--------|----------|-----------|--------|
| AA-01 | `competencia/domain/aggregates` | **CRITICAL** — Ciclo ADP persiste desde BL-004 sin mejora — violación Principio Dependencias Acíclicas | Alta | BL-004/BL-005 |
| AA-02 | `identidad` | **CRITICAL** — D=0.67 Zone of Pain (mejorando ↓ desde 0.87) | Media | BL-005 |
| AA-03 | `registro` | **CRITICAL** — D=0.59 degradando ↑ (riesgo de empeorar en SP6 con RF-IN-05/06) | Alta | BL-005 |
| AA-04 | `shared` | **CRITICAL** — D=0.63 Zone of Pain, estable — estructura concreto-rígida | Media | BL-005 |
| ARCH-01 | `competencia/application/queries` | Proyección `competencias_por_torneo` no materializada → O(n) scan en producción | Alta | HITO-15 |
| ARCH-02 | `identidad/`, `registro/`, `torneo/` | Routers importan `JWTService` (infra) directamente — violación hexagonal D-05 | Alta | notas .work |
| ARCH-03 | `resultados_competencia_adapter.py` | Import cross-BC directo — decisión pendiente: ¿ACL aceptable o violación? | Media | notas .work |
| DR-01 | `RankingCompetencia` | LCOM 2/1 — mezcla lógica ranking + acumulación overall → candidato SRP | Media | DR INC-5.6 |
| DR-02 | `AlgoritmoPuntajeFAAS` | LCOM 2/1 + C=11 — dos paths cálculo → dispatch por TipoDisciplina | Media | DR INC-5.6 + CG |
| DR-06 | `DeclararAPInscripcionHandler` | FeatureEnvy 4/2 — lógica AP debería estar en aggregate `Inscripcion` | Media | DR SP-ADJ-09 |
| DR-07 | `SQLiteInscripcionRepository` | FeatureEnvy 7/2 + FanOut 9/7 — query ensambla múltiples entidades | Media | DR SP-ADJ-09 |
| CG-01/03/04/05 | varios | E501 (4 líneas) + `import os` huérfano — resolubles con `black` | Baja | CodeGuard |
| QG-01 | DesignReviewer | Evaluar reducción `max_cbo`/`max_wmc` post-SP6 | Baja | memory |

---

## 3. Estructura de Incrementos

```
SP6
├── INC-6.1  Ajustes Juez (bugs + UX flujo de competencia)
├── INC-6.2  Ajustes Organizador (UI + nueva página Podios)
├── INC-6.3  Ajustes Atleta (UX + backend inscripción)
├── INC-6.4  Deuda técnica sistema (DR + ARCH)
└── INC-6.5  Validación E2E + Despliegue (UAT completo + deploy)
```

### INC-6.1 — Ajustes Juez

Foco: corregir el flujo de competencia — BUG crítico MUX-04 primero, luego mejoras UX del flujo.

| US | Descripción | Hallazgos |
|----|-------------|-----------|
| US-6.1.1 | Fix BUG canSubmitBko + corrección secuencia tarjeta→marca | MUX-04 + UI-JUE-02 |
| US-6.1.2 | Colores tarjeta + pantalla completada según resultado | MUX-02 + MUX-05 |
| US-6.1.3 | Grilla ordenada por estado + keypad visible en móvil | MUX-03 + MUX-01 |
| US-6.1.4 | Rediseño inicio juez + STA mm:ss + tarjeta amarilla | UI-JUE-01 + MUX-08 + MUX-07 |
| US-6.1.5 | AtletaCard compacta en paso 5 | MUX-06 |

### INC-6.2 — Ajustes Organizador

Foco: corregir UX del portal organizador y crear página de Podios.

| US | Descripción | Hallazgos |
|----|-------------|-----------|
| US-6.2.1 | Inicio: ordenar torneos por fecha + mostrar fecha | UI-ORG-01 |
| US-6.2.2 | Inscriptos + Grilla: renombrar columnas AP → Anuncios + categoría legible | UI-ORG-03 + UI-ORG-04 |
| US-6.2.3 | Resultados: reordenar contenido + quitar PTS FAAS + andarivel | UI-ORG-05 |
| US-6.2.4 | Panel torneo: alertas sin "Resolver" + jueces sin texto nombre | UI-ORG-02 + UI-ORG-06 |
| US-6.2.5 | Nuevo torneo: selección categorías JUNIOR/SENIOR/MASTER | UI-ORG-07 |
| US-6.2.6 | Crear página de Podios | UI-ORG-08 |

### INC-6.3 — Ajustes Atleta

Foco: corregir UX del portal atleta y completar backend de inscripción.

| US | Descripción | Hallazgos |
|----|-------------|-----------|
| US-6.3.1 | Inicio atleta: en línea en header + sin "Hola" + torneos en curso ordenados | UI-ATL-01 |
| US-6.3.2 | Inscripción: declarar AP en formulario | UI-ATL-02 |
| US-6.3.3 | Backend inscripción: persistir apto médico (RF-IN-05) | RF-IN-05 |
| US-6.3.4 | Backend inscripción: persistir constancia de pago (RF-IN-06) | RF-IN-06 |
| US-6.3.x | Ajustes adicionales vibe coding (por identificar) | — |

### INC-6.4 — Deuda Técnica Sistema

Foco: resolver hallazgos DesignReviewer + correcciones arquitectónicas críticas.

| US | Descripción | Hallazgos |
|----|-------------|-----------|
| US-6.4.1 | Romper ciclo ADP en `competencia/domain/aggregates` | AA-01 |
| US-6.4.2 | Materializar proyección `competencias_por_torneo` (O(n) → O(1)) | ARCH-01 |
| US-6.4.3 | Corregir violación hexagonal D-05 (routers → composition root) + reducir `registro` D↑ | ARCH-02 + AA-03 |
| US-6.4.4 | Refactoring `AlgoritmoPuntajeFAAS` dispatch por TipoDisciplina + black/lint fixes | DR-02 + CG-01/03/04/05 |
| US-6.4.5 | Refactoring `DeclararAPInscripcionHandler` + `SQLiteInscripcionRepository` | DR-06 + DR-07 |
| US-6.4.6 | Decisión formal ARCH-03 + SRP `RankingCompetencia` + monitoreo `identidad`/`shared` D | ARCH-03 + DR-01 + AA-02 + AA-04 |

> INC-6.4 puede ejecutarse en paralelo con INC-6.2/6.3 si el contexto lo permite.

### INC-6.5 — Validación E2E + Despliegue

Foco: UAT final con los tres roles + configuración y publicación del entorno productivo.

| US | Descripción |
|----|-------------|
| US-6.5.1 | UAT E2E rol Juez — flujo completo de competencia con datos reales |
| US-6.5.2 | UAT E2E rol Organizador — ciclo completo torneo → grilla → resultados |
| US-6.5.3 | UAT E2E rol Atleta — inscripción → AP → consulta resultados |
| US-6.5.4 | Configuración entorno productivo (servidor, SSL, dominio, backup) |
| US-6.5.5 | Despliegue `v1.0.0` + tag BL-006 + ArchitectAnalyst final |

---

## 4. Criterio de Cierre SP6 (BL-006 / v1.0.0)

- [ ] INC-6.1..6.4: DesignReviewer 0 CRITICAL en cada cierre de INC
- [ ] AA-01 resuelto — ciclo ADP en `competencia/domain/aggregates` eliminado (ArchitectAnalyst 0 DependencyCycles)
- [ ] MUX-04 corregido — BUG canSubmitBko resuelto y verificado en móvil
- [ ] RF-IN-05/06 implementados — persistencia de adjuntos verificada E2E
- [ ] ARCH-01 implementado — grilla carga O(1) verificado con dataset real
- [ ] ARCH-02 corregido — 0 imports directos de infraestructura en routers
- [ ] INC-6.5: UAT E2E completado con los 3 roles sin bloqueos críticos
- [ ] `v1.0.0` tageado en `main` + BL-006 registrado
- [ ] ArchitectAnalyst BL-006: `should_block=false`

---

## 5. Fuera de Scope SP6

| Ítem | Motivo |
|------|--------|
| RF-NT-02/03 (notificaciones nuevas) | Baja prioridad para v1.0 — diferir a post-despliegue |
| RF-IN-07 (integración FAAS) | Depende de acuerdo externo |
| QG-01 (reducir umbrales DR) | Post-despliegue, cuando el sistema esté estable |
| UX Layer IEDD formal (HITO-29) | Material de paper/experimento — cerrar en retrospectiva post-SP6 |
| SP-ADJ-05 items documentales/metodológicos | Post-SP6 o paper |

---

## 6. Notas de Planificación

- **Prioridad absoluta:** MUX-04 (BUG activo que bloquea el flujo del juez).
- **INC-6.1 debe completarse antes de cualquier UAT** del rol juez.
- **INC-6.3 US-6.3.3/6.3.4** requieren diseño de storage de archivos — decidir antes de implementar (filesystem local vs. objeto en DB vs. ruta relativa).
- **INC-6.4 US-6.4.2 (D-05)** impacta 3 BCs — usar `implement-us` con plan explícito de refactoring antes de tocar routers.
- Los ajustes de atleta con "vibe coding" (mencionados en hallazgos) se documentan como US al inicio de INC-6.3 tras una sesión exploratoria.

---

*Creado: 2026-05-03 — inicio SP6*  
*Fuentes: `.work/AtaraxiaDive - Hallazgos - Validacion.md` · `docs/design/ux/mejoras-ux.md` · `.work/revision-sp5/designreviewer-hallazgos-pendientes.md` · `docs/traceability/matrix.md` · memory/*
