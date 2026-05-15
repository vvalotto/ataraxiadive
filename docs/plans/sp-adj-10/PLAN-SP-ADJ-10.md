# PLAN-SP-ADJ-10 — Sprint de Ajuste post-UAT INC-6.5

| Campo | Valor |
|-------|-------|
| **Sprint** | SP-ADJ-10 |
| **Contexto** | Hallazgos funcionales abiertos detectados en UAT E2E de SP6 (F-01..F-10) |
| **Fuentes** | `quality/reports/uat/SP6/F-01-setup/hallazgos.md` · `quality/reports/uat/SP6/F-02-creacion-torneo/hallazgos.md` |
| **Incremento asociado** | INC-6.5 — Validación E2E |
| **Branch base** | `main` |
| **Estado** | Planificado |

---

## Contexto

Completada la UAT E2E de SP6 (F-01..F-10, 13/13 PASS en F-10), cuatro hallazgos quedaron
abiertos por requerir nuevas US-IEDD con cambios en backend y frontend. Se agrega además
un hallazgo observacional sobre la experiencia del atleta en estado CERRADO que no fue
capturado formalmente durante la UAT pero fue identificado inmediatamente después.

| ID | Fase | Severidad | Descripción breve |
|----|------|-----------|-------------------|
| H-01-06 | F-01 | 🟡 Moderado | No existe página "Mis Datos" del atleta — sin `PATCH /registro/atletas/me` |
| H-02-06 | F-02 | 🟡 Moderado | Edición del torneo solo permite cambiar disciplinas — falta `PUT /torneos/{id}` |
| H-01-03 | F-01 | 🟡 Moderado | Email de bienvenida no se envía al registrar usuario |
| H-01-04 | F-01 | ⚪ Menor | Post-registro no hay auto-login — redirección manual obligatoria |
| observación | post-UAT | — | Portal del atleta no tiene vista definida para torneos en estado CERRADO |

SP-ADJ-10 agrupa los hallazgos en cuatro US ordenadas por dependencia e impacto.

---

## US planificadas

### US-ADJ-10.1 — Edición completa del torneo

**Prioridad:** Alta
**Tipo:** fix funcional backend + frontend
**Área:** BC `torneo` (domain · application · api) + `frontend` organizador
**Hallazgo:** H-02-06
**Spec:** `docs/specs/sp-adj-10/US-ADJ-10.1.md`

El organizador no puede corregir nombre, sede, fechas ni categorías de un torneo ya creado.
La pantalla actual de "Editar disciplinas" no habilita esos campos ni existe endpoint `PUT`.

**Fix:**
1. Agregar `ActualizarTorneoCommand` en `torneo/application/` con handler y validaciones.
2. Implementar `PUT /torneos/{id}` en el router con precondición de estado (`CREADO` o `INSCRIPCION_ABIERTA`).
3. Convertir `CrearTorneoPage` en modo dual: creación y edición. En edición pre-rellena todos los campos y llama `PUT`.
4. Renombrar título de "Editar disciplinas" a "Editar torneo".

---

### US-ADJ-10.2 — Página "Mis Datos" del atleta

**Prioridad:** Alta
**Tipo:** fix funcional backend + frontend
**Área:** BC `registro` (application · api) + `frontend` atleta
**Hallazgo:** H-01-06
**Spec:** `docs/specs/sp-adj-10/US-ADJ-10.2.md`

El atleta no tiene página para ver ni modificar sus datos de perfil (nombre, apellido,
categoría, club). Al auto-registrarse, el perfil queda vacío hasta la primera inscripción.

**Fix:**
1. Agregar `ActualizarAtletaCommand` en `registro/application/` con handler.
2. Implementar `PATCH /registro/atletas/me` en el router (campos: `nombre`, `apellido`, `categoria`, `club`).
3. Crear `AtletaMisDatosPage` accesible desde el portal del atleta con formulario de edición.
4. Agregar enlace a "Mis Datos" en la navegación del `AtletaShell`.

---

### US-ADJ-10.3 — Email de bienvenida y auto-login post-registro

**Prioridad:** Media
**Tipo:** fix funcional backend + UX frontend
**Área:** BC `identidad` (application) + `frontend` registro
**Hallazgos:** H-01-03 · H-01-04
**Spec:** `docs/specs/sp-adj-10/US-ADJ-10.3.md`

Al registrarse, el usuario no recibe email de bienvenida ni es redirigido automáticamente
al portal correspondiente a su rol. Debe loguear manualmente después del registro.

**Fix:**
1. En `RegistrarUsuarioHandler`: invocar `EmailPort` con plantilla de bienvenida siguiendo el patrón de `solicitar_reset_password.py`.
2. En `RegisterPage` (frontend): tras registro exitoso, ejecutar login automático con las credenciales ingresadas y redirigir al portal por rol (`portalPorRol(rol)`).
3. Eliminar la redirección a `/login?registered=1`.

---

### US-ADJ-10.4 — Vista post-torneo en portal del atleta

**Prioridad:** Media
**Tipo:** ajuste UX frontend
**Área:** `frontend` atleta (`AtletaHomePage` · `AtletaTorneoDetallePage`)
**Hallazgo:** observación post-UAT
**Spec:** `docs/specs/sp-adj-10/US-ADJ-10.4.md`

Cuando un torneo pasa a CERRADO, desaparece del home del atleta sin dejar rastro.
`AtletaTorneoDetallePage` tampoco muestra resultados para ese estado.

**Fix:**
1. `AtletaHomePage`: agregar sección "Torneos finalizados" que muestra torneos CERRADO con tarjeta de resultado rápido por disciplina (tarjeta, RP, posición, badge podio si aplica). Máximo 3 torneos más recientes.
2. `AtletaTorneoDetallePage` en estado CERRADO: renderizar resultados finales del atleta (`ResultHero` + `RankingCard` + `OverallCard`) en lugar del bloque estático actual. Reutiliza APIs y componentes existentes de `AtletaResultadosPage`.
3. Definir estado vacío correcto para atleta que compitió pero no tiene resultados registrados (DNS en todas las disciplinas).

---

## Secuencia de ejecución

```
US-ADJ-10.1  Edición del torneo (backend primero — desbloquea dependencias de datos)
  ↓
US-ADJ-10.2  Mis Datos del atleta (backend + frontend independiente de 10.1)
  ↓
US-ADJ-10.3  Email bienvenida + auto-login (backend + frontend, sin dependencias)
  ↓
US-ADJ-10.4  Vista post-torneo atleta (frontend puro, reutiliza componentes existentes)
```

> US-ADJ-10.2 y US-ADJ-10.3 pueden ejecutarse en paralelo si se trabaja en ramas
> separadas, ya que no comparten código.

---

## Criterio de cierre de SP-ADJ-10

- [x] US-ADJ-10.1 — `PUT /torneos/{id}` implementado · organizador puede editar todos los campos del torneo desde la UI.
- [x] US-ADJ-10.2 — `PATCH /registro/atletas/me` implementado · atleta puede ver y editar sus datos desde `AtletaMisDatosPage`.
- [x] US-ADJ-10.3 — email de bienvenida enviado al registrar · post-registro redirige directamente al portal sin login manual.
- [x] US-ADJ-10.4 — `AtletaHomePage` muestra sección "Torneos finalizados" con resultados · `AtletaTorneoDetallePage` muestra resultados completos en estado CERRADO.
- [ ] Frontend build/lint OK en todas las US.
- [ ] Tests backend focalizados OK según alcance de cada US (domain · application).
- [ ] DesignReviewer 0 CRITICAL al cierre del SP-ADJ.

---

## Items fuera de alcance

- H-01-02 (panel de administración y gestión de roles) — requiere nuevo BC o módulo admin; diferir a post-v1.0.
- M-04-01 (separación visual de chips en portal público) — baja prioridad, no bloquea funcionalidad.
- M-04-02 (emails externos en Resend) — tarea de configuración de producción en INC-6.7 (Despliegue), no de código.
- Edición de torneo en estados PREPARACION/EJECUCION/PREMIACION — precondición de estado intencional; el organizador no puede modificar datos operativos mientras el torneo está activo.

---

## Riesgos

1. `PUT /torneos/{id}` puede intersectar con validaciones de disciplinas existentes.
   Mitigación: la edición de disciplinas ya tiene endpoint propio; `PUT` toca solo metadatos del torneo.

2. Auto-login en `RegisterPage` puede reutilizar token recibido del endpoint de registro o hacer login programático; la elección afecta la seguridad.
   Mitigación: si el endpoint de registro no devuelve token, hacer `POST /auth/login` inmediatamente con las credenciales — es el mismo flujo que el usuario haría manualmente.

3. `AtletaTorneoDetallePage` con resultados puede generar múltiples queries en páginas que antes eran livianas.
   Mitigación: las queries se montan solo si `torneo.estado === 'CERRADO'` y el atleta tiene inscripción en el torneo.

---

*Creado: 2026-05-14 — hallazgos abiertos UAT INC-6.5 F-01..F-10*
