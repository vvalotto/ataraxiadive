# US-4.6.5: UAT SP4 — Validación integral de la plataforma

**Estado**: `Movida` → ver `docs/specs/sp-adj-06/US-ADJ-6.7.md`
**Sprint original**: SP4 — INC-4.6
**Razón del movimiento**: el UAT es el gate de cierre de SP-ADJ-06 (pre-BL-004)

---

## Descripción

Como **equipo de desarrollo**,
quiero **validar la plataforma completa con datos reales antes de cerrar BL-004**
para **confirmar que INC-4.4 (offline), INC-4.5 (notificaciones email) e INC-4.6 (auditoría/exportación) funcionan integrados en condiciones reales de uso**.

---

## Contexto

Este UAT es el cierre de validación del SP4 completo. Consolida los UATs pendientes de INC-4.4 (diferidos al final del SP) con la validación de INC-4.5 e INC-4.6. Se ejecuta con el dataset real de Buenos Aires 2025.

**Prerrequisitos:**
- UAT-SP4-Capa1 (HTTP automático) ya superada en INC-4.3
- Seed de datos BA 2025 ejecutado (`tests/uat/sp4/seed_sp4.py`)
- Backend corriendo: `uv run uvicorn src.app:app --reload --env-file .env`
- Frontend corriendo: `cd frontend && npm run dev`
- `.env` incluye `RESEND_API_KEY` y `NOTIFICACIONES_EMAIL_FROM=onboarding@resend.dev`
- Dispositivo móvil real (iPhone o Android) conectado a la misma red WiFi
- Cuenta en resend.com con acceso al dashboard de email logs

---

## Área 1 — Offline-first INC-4.4 (casos pendientes)

### Caso 2.1 — Operación completa en modo avión

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| 1 | Abrir la app y precargar una disciplina (grilla visible) | Grilla cargada con datos del servidor |
| 2 | Activar modo avión en el celular | Indicador offline visible en la app |
| 3 | Ejecutar un atleta completo: llamar → confirmar → OT → RP → tarjeta blanca | Cada paso responde sin demora — los comandos se encolan localmente |
| 4 | Verificar en la grilla que el atleta muestra el estado actualizado (sin conexión) | El estado local es consistente |
| 5 | Desactivar modo avión | Indicador online; sync automático inicia en ≤5 segundos |
| 6 | Verificar en el backend que los eventos llegaron | GET `/competencia/{id}/progreso` refleja el atleta completado |

**Resultado esperado global:** ningún dato perdido; el backend tiene exactamente los mismos eventos registrados.

---

### Caso 2.2 — Pérdida de conexión a mitad de un atleta

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| 1 | Iniciar un atleta (paso 1 — Llamar) con conexión activa | Comando enviado al servidor |
| 2 | Cortar WiFi manualmente (o activar avión) | Indicador offline visible |
| 3 | Continuar el flujo: confirmar presencia, OT, RP | Pasos siguen funcionando offline |
| 4 | Asignar tarjeta | Completado local |
| 5 | Restablecer conexión | Sync automático — los comandos pendientes se sincronizan |
| 6 | Verificar en backend | Todos los eventos del atleta están en el store |

---

### Caso 2.3 — Sync manual (reconexión sin sync automático)

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| 1 | Generar comandos offline (2+ atletas completados sin conexión) | Cola de comandos con ≥2 entradas |
| 2 | Reconectar sin esperar sync automático | Indicador online aparece |
| 3 | Pulsar el botón de sync manual (si existe) o esperar el sync automático | Sync se ejecuta |
| 4 | Verificar que la grilla local coincide con el backend | Consistencia total |

---

### Caso 3.1 — App recarga con datos offline pendientes

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| 1 | Generar comandos offline sin sync | Cola no vacía |
| 2 | Cerrar completamente el browser/tab y volver a abrir la app | La app retoma los comandos pendientes de IndexedDB |
| 3 | Al reconectar: sync automático | Los comandos se sincronizan correctamente |

---

### Caso 3.2 — Dos atletas simultáneos (dos dispositivos)

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| 1 | Abrir la app en dos dispositivos (juez 1 y juez 2) | Ambos ven la misma grilla |
| 2 | Juez 1 trabaja con atleta A; juez 2 trabaja con atleta B (offline ambos) | Sin conflicto — distintos atletas |
| 3 | Ambos reconectan y sincronizan | Ambos conjuntos de comandos llegan al servidor sin colisión |
| 4 | El backend tiene los eventos de A y B | Sin pérdida de datos |

---

### Caso 3.3 — Resiliencia: servidor caído durante sync

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| 1 | Comandos pendientes en cola | Cola no vacía |
| 2 | Reconnectar — el servidor está caído (Ctrl+C en uvicorn) | El sync falla silenciosamente — no hay crash en la app |
| 3 | La app muestra indicador de "sync pendiente" o similar | UX no bloqueante |
| 4 | Reiniciar el servidor | Sync automático retoma y completa |

---

### Caso 3.4 — Cache offline después de actualización de datos

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| 1 | Precargar grilla con AP de atletas | Cache local tiene los APs |
| 2 | Cambiar el AP de un atleta directamente en el backend (simulación de corrección del organizador) | Backend actualizado |
| 3 | Recargar la grilla en la app (con conexión) | La app descarga el nuevo AP del servidor y actualiza el cache local |
| 4 | Ir offline y verificar | El cache tiene el AP actualizado, no el anterior |

---

## Área 2 — Notificaciones INC-4.5 (smoke test email real)

### Caso N.1 — Email real de confirmación de inscripción

**Setup:** `.env` tiene `RESEND_API_KEY` configurada y `NOTIFICACIONES_EMAIL_FROM=onboarding@resend.dev`

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| 1 | Registrar un atleta nuevo con email `vvalotto@gmail.com` | Atleta creado |
| 2 | Inscribir al atleta a una disciplina del torneo de prueba | POST `/registro/{atleta_id}/inscripciones` → 201 |
| 3 | Verificar en el event store de notificaciones | `NotificacionSolicitada` + `NotificacionEnviada` presentes |
| 4 | Verificar en el dashboard de Resend | Email registrado en el log de envíos |
| 5 | Revisar inbox de vvalotto@gmail.com | Email recibido con asunto correcto y datos del torneo |

**Resultado esperado:** el email contiene nombre del atleta, nombre del torneo, fecha, sede y disciplinas inscriptas.

---

### Caso N.2 — Idempotencia: doble inscripción no genera doble email

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| 1 | Usar el mismo atleta e inscripción del caso N.1 | Estado: ya inscripto y notificado |
| 2 | Forzar un segundo disparo del handler de P-10 con el mismo `evento_fuente_id` | El aggregate detecta `NotificacionEnviada` ya presente |
| 3 | Verificar en el event store | Solo un `NotificacionEnviada` para ese `evento_fuente_id` |
| 4 | Revisar inbox | Solo un email (no duplicado) |

---

## Área 3 — Auditoría y Exportación INC-4.6

### Caso A.1 — Audit log via UI

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| 1 | Iniciar sesión como organizador | Acceso a panel organizador |
| 2 | Navegar a Auditoría de la competencia DNF | Lista de atletas con resultado final |
| 3 | Seleccionar un atleta con corrección (si existe) | Traza muestra todos los eventos incluyendo la corrección |
| 4 | Verificar orden cronológico | El evento más antiguo aparece primero |
| 5 | Verificar que un juez NO puede acceder a la URL de auditoría | Redirección o 403 |

---

### Caso A.2 — Hash SHA-256 visible al cerrar disciplina

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| 1 | Cerrar una disciplina desde la API: `POST /competencias/{id}/cerrar` | `CompetenciaCerrada` emitido con `hash_sha256` |
| 2 | Navegar a la pantalla de auditoría de esa disciplina | El hash aparece en el encabezado |
| 3 | Verificar que el hash tiene 64 caracteres hexadecimales | Formato correcto |
| 4 | Copiar el hash con el botón | Clipboard tiene el hash completo |

---

### Caso A.3 — Exportación JSON

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| 1 | `GET /resultados/{torneo_id}/export?format=json` como organizador | 200 OK + descarga |
| 2 | Verificar estructura del JSON | Contiene `disciplinas` y `overall` |
| 3 | Verificar que disciplinas cerradas incluyen `hash_sha256` | Hash presente |
| 4 | Verificar que disciplinas en ejecución muestran resultados parciales | Sin hash, resultados disponibles |

---

### Caso A.4 — Exportación CSV

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| 1 | `GET /resultados/{torneo_id}/export?format=csv` como organizador | 200 OK + descarga |
| 2 | Abrir en Excel / Numbers | El separador `;` es reconocido correctamente |
| 3 | Verificar columnas y datos de al menos 3 atletas | Datos coherentes con los vistos en el ranking |

---

## Criterios de cierre del UAT

El UAT está aprobado cuando:

- [ ] Todos los casos de Área 1 (2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 3.4) pasan sin pérdida de datos
- [ ] Caso N.1: email real recibido en vvalotto@gmail.com
- [ ] Caso N.2: idempotencia confirmada (un solo email)
- [ ] Caso A.1: audit log visible y de solo lectura
- [ ] Caso A.2: hash SHA-256 visible y copiable
- [ ] Caso A.3: exportación JSON correcta con hash en disciplinas cerradas
- [ ] Caso A.4: exportación CSV abre correctamente en hoja de cálculo
- [ ] 0 errores no manejados en consola del browser durante todo el recorrido

Los hallazgos se registran en `quality/reports/uat/SP4/uat-sp4-cierre.md`.

---

## Referencias

- Plan SP4 §INC-4.4, §INC-4.5, §INC-4.6
- `tests/uat/sp4/run_uat.sh` — Capa 1 HTTP (ya ejecutada en INC-4.3)
- `scripts/reset_uat_4_4_fixture.py` — reset de fixture para los casos de Área 1
- US-4.4.1, US-4.4.2, US-4.4.3 — offline-first (implementadas)
- US-4.5.3, US-4.5.5 — políticas de notificación (implementadas)
- US-4.6.1, US-4.6.2, US-4.6.3, US-4.6.4 — auditoría y exportación

---

*Redactado: 2026-04-15 — INC-4.6, cierre SP4*
