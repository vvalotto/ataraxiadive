# Plan de Implementacion: US-4.6.3 - UI de auditoria del organizador

**Sprint:** SP4 - La Plataforma  
**Incremento:** INC-4.6  
**Bounded Context:** `frontend`  
**Patron:** `react-vite-tailwind`  
**Estimacion total:** 4h 20min  
**Estado:** Pendiente de aprobacion

## Objetivo

Implementar la navegacion y visualizacion de auditoria para organizador,
mostrando la lista de atletas por competencia, la traza cronologica de una
performance y el `hash_sha256` de la disciplina cuando el cierre ya fue
persistido.

## Hallazgo de contexto

- `US-4.6.1` ya expone `GET /competencia/{competencia_id}/performances/{atleta_id}/audit-log`
- `US-4.6.2` persiste `hash_sha256` en `CompetenciaFinalizada`
- El frontend de organizador hoy solo tiene `DashboardPage`
- No existe harness formal de tests frontend en `frontend/package.json`
- El backend actual expone estado y grilla, pero no un endpoint que devuelva el
  `hash_sha256` de la disciplina cerrada

## Componentes a ajustar

### 1. Frontend - rutas y pagina de organizador

- [ ] `frontend/src/App.tsx` (20 min)
  - Agregar rutas protegidas de auditoria para organizador
  - Mantener redireccion de juez sin tocar flujos existentes

- [ ] `frontend/src/pages/organizador/DashboardPage.tsx` (20 min)
  - Convertir el dashboard minimo en punto de entrada navegable
  - Listar torneos y competencias disponibles para llegar a auditoria

- [ ] Nuevas paginas en `frontend/src/pages/organizador/` (55 min)
  - `AuditoriaCompetenciaPage.tsx`
  - `AuditoriaPerformancePage.tsx`
  - Encabezado con disciplina, estado y hash visible solo si corresponde
  - Timeline de eventos en solo lectura

### 2. Frontend - cliente API y hooks

- [ ] `frontend/src/api/competencia.ts` (35 min)
  - Agregar DTO y cliente para audit log puntual
  - Agregar cliente para resumen de auditoria de competencia o endpoint equivalente

- [ ] `frontend/src/hooks/` (35 min)
  - Crear hooks de carga para auditoria de competencia y performance
  - Manejar loading, empty state, 403 y 404

### 3. Backend minimo de soporte para hash visible

- [ ] Revisar `src/competencia/application/queries/obtener_estado_competencia.py` y router (35 min)
  - Extender el read model para incluir `hash_sha256` cuando la competencia este finalizada
  - Mantener compatibilidad para competencias historicas sin hash
  - Evitar crear endpoint redundante si el `GET /estado` puede absorber el dato

### 4. UX y navegacion

- [ ] Diseno de lista y timeline (30 min)
  - Estado visual claro entre `EnEjecucion` y `Finalizada`
  - Accion copiar con feedback breve
  - Mostrar hash truncado y conservar valor completo para copia

- [ ] Estados de error y vacio (20 min)
  - Sin atletas
  - Audit log inexistente
  - Acceso no autorizado

### 5. Validacion

- [ ] Ejecutar `npm run build` en `frontend/` (10 min)
- [ ] Ejecutar `npm run lint` en `frontend/` si el estado base del repo lo permite (10 min)
- [ ] Ejecutar pytest focalizado del backend si se extiende `GET /estado` (10 min)
- [ ] Evaluar waiver BDD/frontend por ausencia de harness automatizado actual (10 min)

## Dependencias y decisiones

- La lista de atletas puede reutilizar `GET /competencia/{id}/grilla` como fuente
  inicial de nombres, estado y orden.
- La traza puntual consume directamente el endpoint de `US-4.6.1`.
- El hash visible requiere exponer `hash_sha256` en un read model backend ya
  existente o crear un endpoint equivalente si la extension resulta forzada.
- La UI debe seguir restringida a `organizador`; un juez se redirige por
  `RequireRole`.

## Riesgos

- `US-4.6.3` parece frontend, pero hoy depende de una minima ampliacion backend
  para mostrar el hash de cierre.
- No hay framework de tests frontend instalado; la validacion automatizada puede
  apoyarse en `build`/`lint` y, si aplica, en un waiver BDD similar a `US-4.6.1`.
- El dashboard organizador es demasiado basico; puede requerir una pequena
  navegacion intermedia para no hardcodear IDs.

## Checklist de salida

- [ ] Rutas de auditoria disponibles para organizador
- [ ] Lista de atletas visible con estado de disciplina
- [ ] Timeline de eventos puntual en orden cronologico
- [ ] Hash visible solo en competencia finalizada
- [ ] Copia de hash con feedback visual
- [ ] Validacion tecnica ejecutada y documentada

*Plan generado: 2026-04-16 - US-4.6.3 INC-4.6 SP4*
