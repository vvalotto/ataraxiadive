# Métricas Frontend — LOC y Composición

> Fuente: `cloc frontend/src/`  
> Herramienta: cloc 2.08  
> Fecha de ejecución: 2026-05-18  
> Referencia: PLAN-METRICAS.md §A.2.1

---

## 1. Resumen global

| Lenguaje | Archivos | Blancos | Comentarios | SLOC |
|----------|:--------:|:-------:|:-----------:|-----:|
| TypeScript / TSX | 115 | 1 444 | 33 | **15 623** |
| CSS | 1 | 3 | 0 | 14 |
| **Total** | **116** | **1 447** | **33** | **15 637** |

**Relación comentarios/código:** 33 / 15 637 = 0.2% — prácticamente sin comentarios, código auto-documentado por nombres descriptivos.

---

## 2. LOC por subdirectorio funcional

| Directorio | Archivos | SLOC | % del total |
|------------|:--------:|-----:|:-----------:|
| `pages/` | 37 (Pages) + archivos de estructura | ~8 999 | 57% |
| `components/` | ~50 | ~4 356 | 28% |
| `hooks/` | 9 | ~1 254 | 8% |
| `api/` | 8 | 1 469 | 9% |
| `stores/` | 3 | 174 | 1% |

> Nota: los subdirectorios se solapan parcialmente en el conteo de cloc (incluye App.tsx, routing, config). Los valores son estimaciones por tipo de artefacto; el total autoritativo es 15 623 SLOC.

---

## 3. LOC por tipo de artefacto

### Pages (37 archivos)

| Rango LOC | Cantidad | Páginas representativas |
|-----------|:--------:|------------------------|
| < 100 | 3 | OrganizadorJuecesPage (53), OrganizadorGrillaPage (58), OrganizadorInscriptosPage (59) |
| 100–200 | 14 | LoginPage (242), PublicTorneosPage (239), GrillaPage (282) |
| 200–400 | 14 | AuditoriaCompetenciaPage (219), DashboardPage (265), ResultadosPage (298), PerformanceFlowPage (304) |
| > 400 | 6 | RegistroPage (390), CrearTorneoPage (501), AtletaInscripcionPage (526), DetalleTorneoPage (552), DashboardOperativoPage (615) |

**Promedio:** 243 LOC/página · **Máximo:** 615 LOC (DashboardOperativoPage)

Páginas > 400 LOC son candidatas a extracción de componentes si el proyecto continúa:
- `DashboardOperativoPage` (615): vista de juez durante ejecución — múltiples estados de grilla, performance flow, sync offline
- `DetalleTorneoPage` (552): detalle completo del torneo con disciplinas, jueces, competencias anidadas
- `AtletaInscripcionPage` (526): formulario de inscripción multi-paso con declaración de AP

### Componentes (≈ 50 archivos)

**Promedio:** 87 LOC/componente · **Máximo:** 402 LOC · **Total:** ~4 356 LOC

Los componentes siguen el principio de componentes pequeños y enfocados — la mediana es << 87 (distribución asimétrica con pocos componentes grandes).

### Hooks custom (9 archivos)

| Hook | LOC | Función |
|------|----:|---------|
| `usePerformanceFlow` | 486 | Flujo completo OT → resultado → tarjeta (juez) |
| `useSyncQueue` | 289 | Cola de sync offline-first para PWA |
| `usePrecarga` | 147 | Precarga de datos antes de acceder a grilla |
| `useComandoQueue` | 108 | Queue de comandos al backend con retry |
| `useDisciplinasJuez` | 89 | Disciplinas asignadas al juez activo |
| `useAuditoriaCompetencia` | 58 | Datos de auditoría de competencia |
| `useGrillaQueue` | 51 | Estado de la grilla con queue de actualizaciones |
| `useNavigateWithRedirect` | 16 | Navegación con preservación de redirect |
| `useAuditLog` | 10 | Acceso al log de eventos de auditoría |

**Total hooks:** 1 254 LOC · **Promedio:** 139 LOC/hook

`usePerformanceFlow` (486 LOC) y `useSyncQueue` (289 LOC) son los artefactos más complejos del frontend. Concentran la lógica de dominio del panel del juez (ejecución offline-first durante la competencia).

### Stores Zustand (3 archivos)

| Store | LOC | Responsabilidad |
|-------|----:|-----------------|
| `useAuthStore` | 66 | Sesión de usuario, JWT, rol activo |
| `useConnectionStore` | 64 | Estado de conectividad (online/offline) |
| `useCompetenciaStore` | 44 | Estado global de la competencia en curso |

**Total stores:** 174 LOC — stores deliberadamente pequeños; la lógica vive en los hooks.

### API clients (8 archivos)

| Cliente | LOC | BCs cubiertos |
|---------|----:|---------------|
| `competencia.ts` | 485 | BC Competencia — todos los endpoints de performance |
| `registro.ts` | 382 | BC Registro — atleta, juez, organizador |
| `torneo.ts` | 302 | BC Torneo — ciclo de vida, disciplinas, jueces |
| `identidad.ts` | 152 | BC Identidad — auth, usuarios |
| `resultados.ts` | 66 | BC Resultados — rankings, podios |
| `auth.ts` | 54 | Helpers de autenticación |
| `tokenProvider.ts` | 17 | Gestión de JWT |
| `health.ts` | 11 | Health check |

**Total API clients:** 1 469 LOC

---

## 4. Bundle de producción

| Artefacto | Tamaño |
|-----------|-------:|
| `index-*.js` (único chunk JS) | 672 KB |
| Total `dist/` | 792 KB |

El bundle no está dividido (single chunk). Para el contexto de uso (aplicación de competencia, usuarios técnicos con buena conectividad) el tamaño es aceptable. Considerar code splitting si el proyecto escala a uso público masivo.

---

*Ejecutado: 2026-05-18 — rama doc/metricas — PLAN-METRICAS.md §A.2.1 completado*
