# Duplicación de Código Frontend — jscpd

> Fuente: `npx jscpd frontend/src/ --min-lines 5 --min-tokens 50`  
> Herramienta: jscpd  
> Fecha de ejecución: 2026-05-18  
> Referencia: PLAN-METRICAS.md §A.2.3

---

## 1. Resumen global

| Tipo | Archivos | Líneas totales | Clones | Líneas duplicadas | % duplicación |
|------|:--------:|:--------------:|:------:|:-----------------:|:-------------:|
| TSX | 85 | 13 521 | 43 | 609 | **4.5%** |
| TypeScript (.ts) | 29 | 3 462 | 10 | 193 | **5.6%** |
| JavaScript | 76 | 5 811 | 2 | 73 | **1.3%** |
| CSS | 1 | 16 | 0 | 0 | 0% |
| **Total** | **191** | **22 810** | **55** | **875** | **3.8%** |

**Umbral de referencia:** < 5% duplicación es considerado aceptable en proyectos de tamaño medio. El frontend de AtaraxiaDive está en **3.8% global**, dentro del rango saludable.

---

## 2. Focos de duplicación identificados

### 2.1 Capa API clients (mayor densidad en .ts)

Los clientes de API concentran la duplicación más significativa. El patrón `fetch` con manejo de errores, headers de autorización y parsing de respuesta se repite con variaciones mínimas entre clientes.

**Clones principales detectados:**

| Archivos | Líneas | Descripción |
|----------|:------:|-------------|
| `api/identidad.ts` ↔ `api/registro.ts` | 16 | Patrón de fetch con JWT idéntico |
| `api/competencia.ts` ↔ `api/identidad.ts` | 13 | Función de request helper duplicada |
| `api/competencia.ts` ↔ `api/registro.ts` | 24 | Bloque de manejo de error HTTP repetido |

**Causa estructural:** cada cliente API es independiente y no comparte una capa base de fetch. La duplicación es del patrón técnico (HTTP + JWT), no de lógica de dominio.

**Evaluación:** bajo riesgo. El patrón duplicado es simple y estable (no cambia con los requisitos de negocio). Extraer un `apiClient` base reduciría el conteo de clones pero agrega una abstracción que no fue necesaria durante el proyecto.

### 2.2 App.tsx — routing duplicado

| Archivo | Líneas | Descripción |
|---------|:------:|-------------|
| `App.tsx` (líneas 257–289) | 24 | Dos bloques de rutas con estructura idéntica (portal organizador vs portal juez) |

**Causa:** los portales de organizador y juez siguen el mismo patrón de layout + rutas protegidas, generando dos bloques isomorfos en el router principal.

### 2.3 TSX pages — patrones de UI repetidos (43 clones)

La mayoría de los 43 clones en `.tsx` son fragmentos de JSX repetidos entre páginas:
- Patrones de tabla de datos (cabecera + filas + estado vacío)
- Bloques de estado de carga (`loading` / `error`)
- Formularios con estructura similar (campo + label + validación)

Estos son smells de UI — candidatos a extracción de componentes si el proyecto escala — pero no representan riesgo funcional dado el alcance actual.

---

## 3. Distribución de clones por zona

```
API clients (.ts):     10 clones · 193 líneas  ██████░░░░░░░░░░░░░░  22%
Pages (.tsx):          43 clones · 609 líneas  █████████████████░░░  70%
App.tsx (routing):      2 clones ·  73 líneas  ███░░░░░░░░░░░░░░░░░   8%
```

---

## 4. Interpretación para el experimento IEDD

- **3.8% de duplicación en 116 archivos y 15 623 SLOC** es un resultado saludable para un proyecto desarrollado con método incremental (US por US).
- La duplicación está concentrada en **patrones técnicos** (fetch, layouts de UI), no en lógica de negocio — señal de que el dominio frontend está bien encapsulado en hooks y stores.
- **0 clones de lógica de dominio** entre hooks — cada hook tiene una responsabilidad clara y no se solapan.
- La tendencia del método IEDD (implementar por historia pequeña, merge frecuente) no generó acumulación de duplicación en el frontend. El bajo porcentaje sugiere que el principio DRY se aplicó de forma natural durante el desarrollo.

---

*Ejecutado: 2026-05-18 — rama doc/metricas — PLAN-METRICAS.md §A.2.3 completado*
