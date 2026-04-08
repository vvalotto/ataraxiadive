# Decisiones de Diseño — Registro y Roles

> Artefacto INC-4.0 · Decisiones específicas del flujo de registro, identidad multirol e invitaciones
> Complementa: `wireframes-registro-roles.md`, `prototipo-registro-roles.html`
> Fecha: 2026-04-08

---

## Contexto

El flujo de registro y gestión de roles en AtaraxiaDive tiene particularidades que no son
evidentes en los wireframes. Este documento captura las decisiones de diseño tomadas al
producir `prototipo-registro-roles.html` y las razones detrás de cada una.

---

## Decisiones

### D-RR-01 — El rol de juez no es autoasignable

**Decisión:** no existe botón "Quiero ser juez" en el onboarding. El rol de juez se obtiene
exclusivamente por invitación de un organizador.

**Justificación:**
- Evita que cualquier usuario se declare juez sin validación
- El organizador es responsable de verificar las credenciales del juez antes de invitarlo
- El dashboard vacío (S-04) explica explícitamente esta restricción con copy informativo

**Implementación:** la pantalla S-04 muestra el camino "Soy juez" como `path-card` deshabilitada
con texto explicativo — visible pero sin CTA.

---

### D-RR-02 — Las certificaciones de juez son auto-declaradas

**Decisión:** el usuario puede registrar sus certificaciones (organización, nivel, número, fecha)
sin validación por parte de la plataforma.

**Justificación:**
- La verificación física de credenciales es responsabilidad del organizador, no de la plataforma
- La plataforma almacena la declaración y la expone al organizador en el momento de la invitación
- Un aviso inline explícito en S-09 informa: "Esta certificación es declarada por vos; el organizador
  puede solicitarte el carnet original antes del torneo"

**Niveles soportados:** 1 estrella (Juez Nacional), 2 estrellas (Juez Continental), 3 estrellas
(Juez Internacional) — alineado con la nomenclatura CMAS.

---

### D-RR-03 — Los datos deportivos son opcionales al alta

**Decisión:** club, federación y número de licencia no bloquean el registro. Se muestran con
prompt suave "Completar después" en S-06 Perfil.

**Justificación:**
- Un usuario puede registrarse para explorar la plataforma antes de decidir si compite
- Los datos son obligatorios en el flujo de inscripción (S-04 del portal atleta), no en el alta
- Reduce la fricción del onboarding

**Comportamiento:** campos muestran estado `No completado` con acción `+ Agregar`.
El flujo de inscripción a un torneo los requiere y redirige a completarlos si faltan.

---

### D-RR-04 — Compatibilidad atleta + juez en el mismo torneo

**Decisión:** un usuario puede ser juez y atleta en el mismo torneo, siempre que no haya
colisión de disciplinas/andariveles.

**Justificación:**
- En competencias pequeñas (FAAS regionales) es común que jueces también compitan
- La pantalla S-08 (Invitación de juez) detecta la coexistencia y la informa explícitamente
- La compatibilidad se resuelve por disciplina y andarivel asignado, no globalmente

**Implementación:** la card "Compatibilidad de roles" en S-08 muestra si hay solapamiento
y cómo se resuelve (disciplinas separadas, andariveles distintos).

---

### D-RR-05 — Los roles se materializan por torneo, no son globales

**Decisión:** un usuario no tiene "su rol" a nivel cuenta. Tiene roles dentro de torneos
específicos. El dashboard (S-05) los agrupa por torneo con badges: `Organizador`, `Juez`, `Atleta`.

**Justificación:**
- Refleja la realidad del dominio: Victor organiza un torneo, juzga en otro, compite en un tercero
- Evita el problema de "selector de rol al login" (UX confusa, común en plataformas multirol)
- El BC Identidad ya maneja roles por torneo en el dominio (rol asignado en contexto de torneo)

**Comportamiento en login:** el usuario ingresa con email + contraseña. El sistema deriva
la vista de inicio según los torneos activos donde participa, no según un "rol activo" global.

---

### D-RR-06 — Verificación de email es obligatoria antes del primer acceso funcional

**Decisión:** el registro crea la cuenta pero deja al usuario en estado `pendiente_verificacion`.
Hasta confirmar el email, el acceso está restringido a la pantalla S-03 (Verificar Email).

**Justificación:**
- Garantiza que el email es válido antes de enviar notificaciones (BC Notificaciones)
- Previene registros fantasma
- El flujo de re-envío de email está disponible en S-03

---

### D-RR-07 — La bandeja de notificaciones es unificada por roles

**Decisión:** todas las alertas de todos los roles del usuario llegan a una única bandeja (S-07),
diferenciadas por tipo e ícono.

**Justificación:**
- El usuario no tiene que navegar entre vistas de rol para ver sus alertas pendientes
- Tipos de notificación en el mock: invitación de juez, inscripción confirmada, torneo publicado,
  resultados disponibles
- La invitación de juez es el único tipo que requiere acción inline (Aceptar / Rechazar)

---

## Componentes implicados (BC Identidad)

Estas decisiones impactan directamente en el BC Identidad y su API:

| Decisión | Impacto en BC Identidad |
|----------|------------------------|
| D-RR-01 | No existe endpoint `POST /usuarios/rol/juez`; el rol emerge de `POST /torneos/{id}/jueces/invitar` |
| D-RR-02 | `POST /usuarios/certificaciones` — sin validación server-side, solo persistencia |
| D-RR-05 | `GET /usuarios/me/torneos` devuelve lista con roles por torneo |
| D-RR-06 | `POST /usuarios/verificar-email` — token enviado por BC Notificaciones |

---

*Artefacto generado: 2026-04-08 — INC-4.0 UX Design*
*Capa IEDD: 3 — Especificación de decisiones de diseño*
