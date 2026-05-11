# UAT Controlado — Política y Estrategia

> Tipo: Documento metodológico — IEDD  
> Ámbito: AtaraxiaDive · aplicable a cualquier SP con validación E2E  
> Última actualización: 2026-05-11  
> Referencias: HITO-20 · HITO-28 · HITO-9 · UAT-INC-6.5-plan.md (instancia SP6)

---

## 1. Principio Fundacional

El UAT no valida roles — valida **procesos**. Un sistema como AtaraxiaDive no funciona por rol: funciona por ciclo de vida. Los roles participan en cada etapa donde corresponde naturalmente. Testear por rol en forma aislada oculta bugs de integración entre estados y actores.

> **Regla:** la unidad de organización del UAT es la **fase del ciclo de vida del sistema**, no el actor que la ejecuta.

---

## 2. Estrategia General

### 2.1 Ciclo de vida como eje organizador

Cada sistema tiene un ciclo de vida con estados formales. En AtaraxiaDive: `CREADO → INSCRIPCION_ABIERTA → PREPARACION → EJECUCION → PREMIACION → CERRADO`. El UAT recorre ese ciclo de principio a fin, en orden, una fase por vez.

Las transiciones de estado son **puntos de verificación obligatorios**: cuando el sistema cambia de estado, todos los roles y superficies (portal, organizador, juez, atleta) deben reflejar el nuevo estado correctamente. Estos cambios fueron fuente de bugs recurrentes en SP4 y SP5.

### 2.2 Portal público desde el inicio

Cualquier superficie pública del sistema debe estar activa y verificada desde la primera fase, no al final. Un bug en el portal puede tener impacto cruzado con el resto del ciclo — descubrirlo tarde aumenta el costo de corrección.

### 2.3 Registro de usuarios como parte del flujo

El registro y autenticación de cada rol es parte del escenario de prueba, no un prerrequisito silencioso. Esto valida el flujo de onboarding y asegura que los permisos y redirecciones post-login son correctos para cada rol.

### 2.4 Datos en dos etapas

Los datos de prueba se cargan en dos momentos distintos:

| Etapa | Cuándo | Qué carga |
|-------|--------|-----------|
| **Seed-A (usuarios)** | Antes de iniciar el UAT | Usuarios de cada rol con credenciales predefinidas |
| **Seed-B+ (datos de negocio)** | Después de cada fase que genera entidades | Datos que dependen de IDs generados por la UI (torneo_id, etc.) |

El objetivo es que el UAT **genere** los datos de negocio a través de los escenarios, no que los precargue todos desde el inicio. Solo se usa seed cuando la escala de datos hace inviable el ingreso manual (ej. 31 atletas con APs para 5 disciplinas).

### 2.5 Verificación cruzada de roles

Toda acción significativa se verifica desde al menos otro rol. El juez registra una performance → el organizador debe verla → el atleta debe verla → el portal público debe reflejarla. Si solo se verifica desde el rol que ejecutó, los bugs de propagación quedan ocultos.

### 2.6 Flujos de excepción dentro de la ejecución

Los flujos de excepción (DNS, BKO, tarjeta amarilla con revisión) no son una fase separada — son escenarios dentro de la fase de ejecución. Se ejecutan sobre los mismos datos que el happy path, después de al menos un escenario exitoso que confirme que el flujo normal funciona.

### 2.7 Dispositivos por rol

Cada rol se prueba en el dispositivo que usa en contexto real:

| Rol | Dispositivo | Razón |
|-----|-------------|-------|
| Organizador | Desktop / laptop | Gestión de torneo, tablas, múltiples tabs |
| Juez | Móvil (iPhone / Android) | Contexto real en pileta, una mano libre |
| Atleta | Móvil o tablet | Consulta en sitio |
| Portal público | Cualquier dispositivo | Sin restricción de uso |

Testear el flujo del juez desde desktop no valida el sistema real — el keypad, la visibilidad de la grilla y la pantalla de resultado son críticos en pantalla pequeña.

### 2.8 Criterio de bloqueo explícito

Antes de iniciar el UAT, se define qué es bloqueante y qué es observación. Sin este criterio, un detalle visual puede detener una sesión de validación que de otro modo sería válida.

| Severidad | Definición | Acción durante UAT |
|-----------|-----------|-------------------|
| 🔴 Bloqueante | Impide continuar la fase · pérdida de datos · flujo roto · resultado incorrecto | Detener la fase · registrar hallazgo · no avanzar hasta resolver |
| 🟡 Observación | Comportamiento incorrecto pero el flujo puede continuar | Registrar hallazgo · continuar UAT |
| ⚪ Estético | Texto, color, alineación — no afecta la función | Registrar para corrección posterior |

---

## 3. Proceso por Fase

Cada fase del UAT sigue el mismo ciclo de cinco pasos:

```
┌─────────────────────────────────────────────────────────────┐
│  FASE N                                                      │
│                                                              │
│  1. PREPARACIÓN                                              │
│     ├── Verificar criterio de entrada (precondiciones)       │
│     ├── Crear / actualizar script de seed de la fase         │
│     └── Documentar escenarios en escenarios.md               │
│                                                              │
│  2. EJECUCIÓN MANUAL                                         │
│     ├── Correr seed si corresponde                           │
│     ├── Ejecutar escenarios en orden                         │
│     └── Registrar resultado (PASS / FAIL) en escenarios.md   │
│                                                              │
│  3. REGISTRO DE HALLAZGOS                                    │
│     └── Completar hallazgos.md con cada FAIL                 │
│                                                              │
│  4. VIBE CODING — RESOLUCIÓN DE DEFECTOS                     │
│     ├── Resolver hallazgos 🔴 antes de continuar             │
│     ├── Resolver hallazgos 🟡 si el tiempo lo permite        │
│     └── Re-ejecutar escenarios afectados → confirmar PASS    │
│                                                              │
│  5. CIERRE DE FASE                                           │
│     ├── Verificar criterio de salida (postcondiciones)       │
│     ├── Completar reporte_fNN.md                             │
│     ├── Commit de cierre de fase en git                      │
│     └── Avanzar a la siguiente fase                          │
└─────────────────────────────────────────────────────────────┘
```

### 3.1 Criterio de entrada (precondición de fase)

Antes de iniciar cada fase, verificar explícitamente:
- Las fases anteriores tienen criterio de salida cumplido
- El seed de la fase anterior fue ejecutado exitosamente
- El entorno está en el estado esperado (verificar estado del sistema, no asumir)

Si el criterio de entrada no se cumple, **no iniciar la fase**. Resolver primero.

### 3.2 Criterio de salida (postcondición de fase)

Al cerrar cada fase, verificar:
- Todos los escenarios 🔴 están en PASS
- Los hallazgos 🔴 están resueltos y re-verificados
- El sistema está en el estado esperado para la siguiente fase
- El reporte de la fase está completo

### 3.3 Separación de defectos y mejoras

Durante el vibe coding aparecerán cosas que "podrían estar mejor" pero no son defectos funcionales. Se registran en una sección separada de `hallazgos.md` y **no bloquean** el cierre de la fase. El criterio de cierre aplica solo a defectos — no a mejoras.

### 3.4 Branch y commit por fase

Cada fase del UAT se ejecuta en su propio branch, creado desde `develop` al iniciar la fase y mergeado a `develop` al cerrarla.

**Nomenclatura de branch:**
```
uat/INC-X.Y/F-NN-nombre
```

**Ciclo de vida del branch:**
```
develop
  └── uat/INC-6.5/F-01-setup      ← crear al iniciar F-01
        ├── artefactos de la fase (escenarios.md, hallazgos.md, reporte)
        ├── fixes de vibe coding si los hay
        └── commit de cierre → PR → merge a develop → crear F-02
```

**Commit de cierre:**
```
test(uat): fase F-NN completa — N hallazgos resueltos [INC-X.Y]
```

Este ciclo garantiza que:
- Cada fase es un punto de retorno limpio en git
- Los fixes de vibe coding quedan asociados a la fase que los generó
- `develop` avanza fase a fase con evidencia verificable del progreso

---

## 4. Estructura de Artefactos por Fase

```
quality/reports/uat/<SP>/
├── F-01-<nombre>/
│   ├── seed_f01_<nombre>.py      ← script de seed si aplica
│   ├── escenarios.md             ← tabla de escenarios con resultado
│   ├── hallazgos.md              ← defectos y mejoras encontradas
│   └── reporte_f01.md            ← resumen: criterio entrada/salida, métricas
├── F-02-<nombre>/
│   └── ...
└── REPORTE-FINAL-<INC>.md        ← consolidado de todas las fases
```

### 4.1 Plantilla: escenarios.md

```markdown
# Escenarios — Fase F-NN: <nombre>

## Criterio de Entrada
- [ ] <precondición 1>
- [ ] <precondición 2>

## Escenarios

| ID | Actor | Dispositivo | Acción | Resultado esperado | Resultado real | Estado | Hallazgo |
|----|-------|-------------|--------|--------------------|----------------|--------|----------|
| F-NN-S01 | Organizador | Desktop | ... | ... | ... | ⬜ PENDIENTE | — |

## Criterio de Salida
- [ ] Todos los escenarios 🔴 en PASS
- [ ] <postcondición específica>
```

**Estados de escenario:** ✅ PASS · ❌ FAIL · ⏭️ SKIP (bloqueado por fase anterior) · ⬜ PENDIENTE

### 4.2 Plantilla: hallazgos.md

```markdown
# Hallazgos — Fase F-NN: <nombre>

## Defectos

| ID | Escenario | Descripción | Severidad | Pasos para reproducir | Estado | Fix |
|----|-----------|-------------|-----------|----------------------|--------|-----|
| H-NN-01 | F-NN-S01 | ... | 🔴 | 1. ... 2. ... | Abierto | — |

## Mejoras (fuera de scope UAT)

| ID | Origen | Descripción | Prioridad sugerida |
|----|--------|-------------|-------------------|
| M-NN-01 | F-NN-S03 | ... | Baja |
```

**Estados de hallazgo:** Abierto · En resolución · Resuelto · Descartado

### 4.3 Plantilla: reporte_fNN.md

```markdown
# Reporte Fase F-NN: <nombre>

**Fecha de ejecución:** YYYY-MM-DD  
**Ejecutor:** <nombre>  
**Dispositivos usados:** <lista>

## Métricas

| Métrica | Valor |
|---------|-------|
| Escenarios ejecutados | N |
| PASS | N |
| FAIL | N |
| SKIP | N |
| Hallazgos 🔴 | N (N resueltos) |
| Hallazgos 🟡 | N (N resueltos) |
| Mejoras registradas | N |

## Resumen

<2-3 líneas sobre qué funcionó, qué falló, qué se corrigió>

## Criterio de Salida

- [x/] <postcondición 1>
- [x/] <postcondición 2>

## Estado: FASE CERRADA / FASE CON OBSERVACIONES / FASE BLOQUEADA
```

---

## 5. Reporte Final de Incremento

Al cerrar todas las fases, generar `REPORTE-FINAL-<INC>.md` con:

- Tabla de fases: estado de cierre, cantidad de hallazgos por severidad
- Hallazgos 🔴 resueltos: descripción del fix y commit
- Hallazgos 🟡 resueltos: idem
- Hallazgos o mejoras diferidos: qué queda pendiente y por qué
- Criterio de cierre del incremento: cumplido / no cumplido
- Decisión de avance al siguiente incremento

---

## 6. Vibe Coding en UAT

El término "vibe coding" en este contexto designa la resolución ágil de defectos **durante** la sesión de UAT, sin abrir una US formal ni seguir las 10 fases de `/implement-us`. Es adecuado cuando:

- El defecto es pequeño y acotado (un componente, una validación, un formato)
- El fix no requiere cambios de dominio ni de arquitectura
- La corrección puede verificarse en el mismo entorno de UAT sin reiniciar

**No es vibe coding:** cambios que afectan agregados de dominio, handlers de aplicación, o que requieren nuevos tests de integración. Esos van como US-IEDD en el mismo incremento.

> Ver HITO-28 para el análisis de la tensión UAT vibe coding vs. pipeline formal.

### Criterio de uso

| Alcance del fix | Proceso |
|-----------------|---------|
| Solo frontend (componente, estilo, texto, formato) | Vibe coding en UAT |
| Backend sin cambio de dominio (query, serialización, endpoint) | Vibe coding en UAT con test de smoke |
| Cambio en domain/ o application/ | US-IEDD dentro del mismo INC |
| Nuevo comportamiento no planificado | US-IEDD en INC siguiente |

---

## 7. Datos Reales como Oráculo

Cuando el UAT usa datos de una competencia real (ej. Buenos Aires 2025), los resultados conocidos actúan como **oráculo de verdad**: el sistema debe producir exactamente esos rankings, marcas y podios. Cualquier diferencia es un defecto — no una discrepancia de interpretación.

Esta propiedad elimina la ambigüedad del criterio de aceptación: no hay que inventar resultados esperados ni asumir comportamientos. Los datos reales ya los determinan.

> Ver HITO-17 sobre datos reales como oráculo del dominio.

---

## 8. Límites del Proceso

Este proceso de UAT controlado **no reemplaza**:
- Los tests unitarios y de integración (que validan invariantes de dominio)
- El DesignReviewer al cierre de cada INC (que valida la arquitectura)
- El ArchitectAnalyst al cierre de SP (que valida tendencias estructurales)

Es una capa de validación funcional E2E que complementa los quality gates automáticos.

---

*Generado: 2026-05-11 — a partir de la experiencia acumulada en SP1..SP5 y el diseño de INC-6.5*  
*Instancia de referencia: `docs/plans/sp6/UAT-INC-6.5-plan.md`*
