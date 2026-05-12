# Escenarios — Fase F-01: Setup: Usuarios y Portal Público

## Criterio de Entrada

- [x] Base de datos limpia de datos BA 2025 (o vacía)
- [x] Seed-A ejecutado: `uv run python tests/uat/sp6/seed_ba2025_usuarios.py`
- [x] Servidor backend y frontend levantados

## Escenarios

| ID | Actor | Dispositivo | Acción | Resultado esperado | Resultado real | Estado | Hallazgo |
|----|-------|-------------|--------|--------------------|----------------|--------|----------|
| F01-S01 | Visitante | Cualquier browser | Acceder a `/portalapnea` sin login | Portal carga · lista de torneos visible (puede estar vacía) · sin error | Portal carga correctamente · lista vacía · sin errores 401 | ✅ PASS | — |
| F01-S02 | Visitante | Cualquier browser | Explorar portal sin autenticación | Ningún redirect a login · ningún error 401 | Sin redirects ni errores al navegar | ✅ PASS | — |
| F01-S03 | Organizador | Desktop | Login con `organizador@ba2025.uat` / `Ba2025uat!` | Redirige a portal organizador · header "En línea" | Redirección correcta a portal organizador | ✅ PASS | — |
| F01-S04 | Juez 1 | Móvil | Login con `juez1@ba2025.uat` / `Ba2025uat!` | Redirige a portal juez · sección "Mis asignaciones" visible | Portal juez correcto · asignaciones visible (vacías sin torneo) | ✅ PASS | — |
| F01-S04b | Juez 3 | Móvil | Login con `juez3@ba2025.uat` / `Ba2025uat!` | Redirige a portal juez correctamente | Portal juez correcto | ✅ PASS | — |
| F01-S05 | Atleta | Móvil | Login con `victor.valotto@ba2025.uat` / `Ba2025uat!` | Redirige a portal atleta · sin cartel "Hola" incorrecto | Portal atleta carga · estado vacío sin error (sin inscripciones aún) | ✅ PASS | — |
| F01-S06 | Visitante | Cualquier browser | Intentar acción que requiere auth (ej. inscribirse) | Redirige a login · post-login regresa al destino correcto | Redirect a login correcto · post-login vuelve al destino | ✅ PASS | — |
| F01-S07 | Visitante | Desktop | Completar formulario de registro como nuevo atleta (`nuevo.atleta@ba2025.uat`) | Cuenta creada · redirige a portal atleta · sin error | Cuenta creada · portal atleta mostraba error genérico → corregido (UX) | ✅ PASS | H-01-05 🔴 ✅ Resuelto |
| F01-S08 | Admin | Desktop | Login como `admin@ba2025.uat` · cambiar rol de `nuevo.atleta@ba2025.uat` a JUEZ | Rol actualizado · próximo login del usuario refleja nuevo rol | Login admin corregido (página en blanco → portal) · panel de gestión de usuarios no existe | ❌ FAIL | H-01-01 🟡 ✅ · H-01-02 🟡 Abierto |
| F01-S09 | Visitante | Desktop | Registrar nuevo usuario desde la UI | Llega email de confirmación de registro a la casilla indicada | Email no enviado — handler no invoca EmailPort | ❌ FAIL | H-01-03 🟡 Abierto |

## Criterio de Salida

- [x] Todos los escenarios 🔴 en PASS — H-01-05 (único 🔴) resuelto
- [x] Usuarios autenticables: organizador, juez1, juez2, juez3, atletas (Seed-A)
- [x] Portal público accesible sin autenticación
- [x] Auto-registro atleta funcional (portal muestra estado vacío correcto)
- [x] No existe torneo BA 2025 en el sistema
- [ ] Gestión de roles admin (S08): requiere US-IEDD — diferido
- [ ] Email de bienvenida (S09): requiere US-IEDD — diferido
