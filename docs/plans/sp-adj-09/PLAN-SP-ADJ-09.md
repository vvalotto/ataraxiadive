# PLAN-SP-ADJ-09 — Sprint de Ajuste: Alineación UX del Organizador post-SP5

| Campo | Valor |
|-------|-------|
| **Sprint** | SP-ADJ-09 |
| **Contexto** | Corrección de divergencia estructural entre la UX aprobada del organizador y la implementación React actual |
| **Fuentes** | `docs/design/ux/wireframes-organizador.md` · `docs/design/ux/prototipos/prototipo-organizador.html` · `docs/design/ux/decisiones-frontend.md` · hallazgo UAT manual INC-5.6 |
| **Branch base** | `develop` |
| **Estado** | ⏳ Pendiente |

---

## Contexto

Durante la validación manual posterior a `US-5.6.6` se confirmó un gap estructural:
la UI del organizador implementada en `frontend/` no respeta la fuente de verdad UX
definida en `docs/design/ux/`.

La divergencia no está limitada a la pantalla `Resultados`; afecta al shell completo
del rol organizador:

- navegación primaria;
- layout compartido;
- lenguaje visual;
- jerarquía de pantallas;
- composición de las vistas principales `Panel`, `Grilla`, `Resultados`, `Jueces`,
  `Torneo` y `Audit Log`.

Seguir implementando funcionalidades nuevas sobre el shell actual incrementaría deuda
técnica y de producto. Por eso corresponde abrir un sprint de ajuste explícito,
análogo a los `SP-ADJ` previos, antes de seguir expandiendo el frontend del organizador.

---

## Diagnóstico consolidado

### 1. Divergencia de shell y navegación

La UX aprobada define una aplicación del organizador de pantalla única con navbar
superior sticky y tabs persistentes:

`[📊 Panel] [📋 Grilla] [🏆 Resultados] [👥 Jueces] [📝 Torneo] [🔍 Audit Log]`

La implementación real está organizada como páginas y rutas separadas, sin navbar
compartida ni estado activo persistente:

- `/organizador/dashboard`
- `/organizador/torneo/:torneoId`
- `/organizador/resultados`
- `/organizador/torneos/:torneoId/competencias`
- `/organizador/competencias/:id/auditoria`

Esto viola el invariante UX principal documentado en `wireframes-organizador.md`.

### 2. Divergencia visual

La UX aprobada del organizador es:

- dark theme;
- desktop-first;
- navbar sticky de 56 px;
- tokens `--bg`, `--surface`, `--surface2`, `--accent`, etc.

La implementación actual usa un shell claro/beige con cards blancas y encabezados
por página. No es una variación aceptable del diseño: es otro lenguaje visual.

### 3. Divergencia funcional de pantallas primarias

El `Dashboard` aprobado es un panel operativo en vivo (KPI strip + disciplina activa +
alertas + próximos). El `DashboardPage` real funciona como listado de torneos.

Además, parte de la navegación aprobada de primer nivel quedó reemplazada por tabs
locales dentro de `DetalleTorneoPage`, mezclando navegación primaria con detalle
contextual del torneo.

### 4. Impacto transversal

El problema ya afecta o condiciona varias US de SP5:

- `US-5.1.x` — panel del organizador;
- `US-5.2.x` — ejecución por disciplina;
- `US-5.5.2` — inscriptos;
- `US-5.6.5` y `US-5.6.6` — resultados y podios.

No conviene corregir estas divergencias historia por historia. El shell del organizador
debe normalizarse primero.

---

## Objetivo del SP-ADJ-09

Reestablecer la UX aprobada del organizador como contrato implementado en código,
mediante una refactorización controlada del shell y la navegación principal del rol.

Esto implica:

1. introducir un shell persistente del organizador;
2. alinear el lenguaje visual con los artefactos UX aprobados;
3. reubicar las vistas primarias dentro de la navegación correcta;
4. dejar una base consistente para rehacer o ajustar las pantallas que hoy dependen
   del layout divergido.

---

## Estrategia

El ajuste debe hacerse **de afuera hacia adentro**:

1. **Shell y navegación**
   - navbar sticky;
   - active state;
   - layout dark compartido;
   - ubicación consistente de conexión y usuario.

2. **Pantallas primarias**
   - `Panel`
   - `Grilla`
   - `Resultados`
   - `Jueces`
   - `Torneo`
   - `Audit Log`

3. **Recomposición de flujos secundarios**
   - detalle de torneo;
   - accesos desde cards;
   - vínculos entre secciones.

No se recomienda empezar por `Resultados` ni por componentes aislados. Sin shell
común, cualquier ajuste sería parcialmente descartable.

---

## US candidatas

### US-ADJ-9.1 — Shell del organizador: navbar sticky + tema dark + estado activo

**Prioridad: Alta**
**Tipo:** refactor frontend estructural
**Área:** `frontend/src/components/organizador/` + routing organizador

Implementar un `OrganizadorShell` persistente alineado a la UX aprobada:

- navbar sticky;
- tabs `Panel / Grilla / Resultados / Jueces / Torneo / Audit Log`;
- tema dark y tokens compartidos;
- badge de conexión;
- nombre del usuario visible;
- estado `active` consistente por ruta.

Esta US crea la base arquitectónica visual sobre la que deben colgar todas las demás.

---

### US-ADJ-9.2 — Reestructurar routing del organizador según navegación primaria aprobada

**Prioridad: Alta**
**Tipo:** refactor frontend estructural
**Área:** `frontend/src/App.tsx` + páginas organizador

Reordenar las rutas del organizador para que reflejen la navegación aprobada y no una
colección de páginas inconexas. La shell debe ser el punto de montaje común del rol.

Objetivos:

- reducir navegación “volver al dashboard” como patrón dominante;
- convertir las secciones primarias en destinos directos del shell;
- separar navegación primaria de vistas detalle/contextuales.

---

### US-ADJ-9.3 — Home del organizador: torneos vigentes e histórico

**Prioridad: Alta**
**Tipo:** ajuste funcional + UX
**Área:** `frontend/src/pages/organizador/DashboardPage.tsx` o ruta home equivalente

Formalizar una pantalla que hoy existe en la implementación pero no en el prototipo
UX original: la vista inicial del organizador con el listado de torneos bajo su
responsabilidad.

Comportamiento esperado:

- mostrar por defecto torneos vigentes;
- considerar vigentes, como mínimo:
  - `INSCRIPCION_ABIERTA`
  - `PREPARACION`
  - `EJECUCION`
  - `PREMIACION` si se confirma que sigue siendo operativo para el rol;
- permitir filtro de histórico:
  - `CERRADO`
  - `CANCELADO`
- dejar explícita la diferencia entre:
  - home de torneos;
  - dashboard operativo del torneo activo.

Esta US no contradice la observación de divergencia UX; la completa. Define un caso
de uso real que la implementación introdujo y que debe ser incorporado a la fuente
de verdad antes de rehacer el shell completo.

---

### US-ADJ-9.4 — Dashboard operativo del organizador alineado a S-01

**Prioridad: Alta**
**Tipo:** ajuste funcional + UX
**Área:** `frontend/src/pages/organizador/DashboardPage.tsx`

Implementar la vista operativa aprobada separada del home de torneos:

- KPI strip;
- disciplina activa;
- alertas;
- próximos atletas;
- otras disciplinas informativas.

El listado de torneos queda cubierto por `US-ADJ-9.3`, por lo que esta pantalla ya no
debe asumir el doble rol de catálogo + panel operativo.

---

### US-ADJ-9.5 — Reencuadrar Resultados dentro del shell aprobado

**Prioridad: Alta**
**Tipo:** ajuste UX + composición frontend
**Área:** `frontend/src/pages/organizador/ResultadosPage.tsx`

Rehacer la pantalla `Resultados` para que respete:

- layout de `S-04`;
- header y subtítulo aprobados;
- relación visual entre ranking de disciplina y overall;
- consistencia con el shell y tokens del organizador.

Esta US absorbe la corrección de `US-5.6.5` y `US-5.6.6` desde la perspectiva visual
y de navegación, no del dominio.

---

### US-ADJ-9.6 — Reubicar Grilla, Jueces, Torneo y Audit Log en la arquitectura UX correcta

**Prioridad: Media-Alta**
**Tipo:** ajuste transversal frontend
**Área:** páginas organizador y componentes relacionados

Normalizar las demás secciones primarias del organizador para que queden coherentes con:

- el shell común;
- el patrón de encabezados aprobado;
- la navegación persistente;
- y el flujo entre pantallas del prototipo.

Incluye revisar el rol de `DetalleTorneoPage` para que deje de concentrar navegación
primaria que debería vivir en la barra superior.

---

## Secuencia recomendada

```text
US-ADJ-9.1  Shell del organizador
  ↓
US-ADJ-9.2  Routing primario del organizador
  ↓
US-ADJ-9.3  Home del organizador
  ↓
US-ADJ-9.4  Dashboard operativo S-01
  ↓
US-ADJ-9.5  Resultados S-04
  ↓
US-ADJ-9.6  Grilla / Jueces / Torneo / Audit Log
```

> Regla práctica: no especificar ni implementar en detalle las pantallas internas hasta
> cerrar `US-ADJ-9.1` y `US-ADJ-9.2`. El shell es la fundación de este ajuste.

---

## Criterio de cierre del SP-ADJ-09

- [ ] El organizador usa un shell único, persistente y dark alineado a `docs/design/ux/`
- [ ] La navegación primaria coincide con `Panel / Grilla / Resultados / Jueces / Torneo / Audit Log`
- [ ] Existe una home del organizador explícita para listar torneos vigentes e histórico
- [ ] El dashboard deja de ser un catálogo de torneos y pasa a ser un panel operativo
- [ ] `Resultados` queda reencuadrado dentro del shell UX correcto
- [ ] Las secciones principales del organizador ya no dependen de “volver al dashboard”
- [ ] UAT manual del rol organizador sin hallazgos críticos de navegación/UX estructural

---

## Fuera de scope

No forma parte de este SP-ADJ:

- recalibrar fórmulas de puntaje FAAS;
- cambios de dominio en `src/`;
- rediseñar UX del juez o del atleta;
- automatización browser end-to-end.

Este sprint corrige estructura UX y composición frontend del rol organizador.

---

## Riesgos

1. El ajuste puede tocar muchas pantallas del organizador en paralelo.
   Mitigación: secuenciar shell → routing → páginas.

2. Algunas US de SP5 podrían haber quedado correctamente implementadas en lógica pero
   mal ubicadas en navegación.
   Mitigación: preservar comportamiento cuando sea posible y rehacer solo composición/UX.

3. Si no se corta bien el scope, el sprint puede derivar en rediseño general del frontend.
   Mitigación: restringir el ajuste al rol organizador y a las pantallas documentadas en
   `wireframes-organizador.md`.

---

## Próximo paso

Generar las specs formales individuales de:

- `US-ADJ-9.1`
- `US-ADJ-9.2`
- `US-ADJ-9.3`
- `US-ADJ-9.4`
- `US-ADJ-9.5`
- `US-ADJ-9.6`

en ese orden.

---

*Creado: 2026-04-28 — a partir de hallazgo UAT funcional manual post-US-5.6.6*
