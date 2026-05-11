# Escenarios — Fase F-01: Setup: Usuarios y Portal Público

## Criterio de Entrada

- [ ] Base de datos limpia de datos BA 2025 (o vacía)
- [ ] Seed-A ejecutado: `uv run python tests/uat/sp6/seed_ba2025_usuarios.py`
- [ ] Servidor backend y frontend levantados

## Escenarios

| ID | Actor | Dispositivo | Acción | Resultado esperado | Resultado real | Estado | Hallazgo |
|----|-------|-------------|--------|--------------------|----------------|--------|----------|
| F01-S01 | Visitante | Cualquier browser | Acceder a `/portalapnea` sin login | Portal carga · lista de torneos visible (puede estar vacía) · sin error | — | ⬜ PENDIENTE | — |
| F01-S02 | Visitante | Cualquier browser | Explorar portal sin autenticación | Ningún redirect a login · ningún error 401 | — | ⬜ PENDIENTE | — |
| F01-S03 | Organizador | Desktop | Login con `organizador@ba2025.uat` / `Ba2025uat!` | Redirige a portal organizador · header "En línea" | — | ⬜ PENDIENTE | — |
| F01-S04 | Juez 1 | Móvil | Login con `juez1@ba2025.uat` / `Ba2025uat!` | Redirige a portal juez · sección "Mis asignaciones" visible | — | ⬜ PENDIENTE | — |
| F01-S04b | Juez 3 | Móvil | Login con `juez3@ba2025.uat` / `Ba2025uat!` | Redirige a portal juez correctamente | — | ⬜ PENDIENTE | — |
| F01-S05 | Atleta | Móvil | Login con `victor.valotto@ba2025.uat` / `Ba2025uat!` | Redirige a portal atleta · sin cartel "Hola" incorrecto | — | ⬜ PENDIENTE | — |
| F01-S06 | Visitante | Cualquier browser | Intentar acción que requiere auth (ej. inscribirse) | Redirige a login · post-login regresa al destino correcto | — | ⬜ PENDIENTE | — |
| F01-S07 | Visitante | Desktop | Completar formulario de registro como nuevo atleta (`nuevo.atleta@ba2025.uat`) | Cuenta creada · redirige a portal atleta · sin error | registro UI | 🔴 |
| F01-S08 | Admin | Desktop | Login como `admin@ba2025.uat` · cambiar rol de `nuevo.atleta@ba2025.uat` a JUEZ | Rol actualizado · próximo login del usuario refleja nuevo rol y redirige a portal juez | cambio de rol | 🟡 |

## Criterio de Salida

- [ ] Todos los escenarios 🔴 en PASS (S01, S02, S03, S04, S06, S07)
- [ ] Usuarios autenticables: organizador, juez1, juez2, juez3, atletas
- [ ] Portal público accesible sin autenticación
- [ ] Registro de usuario desde UI funcional
- [ ] No existe torneo BA 2025 en el sistema
