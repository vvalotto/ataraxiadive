# Escenarios — Fase F-04: Inscripción Abierta

## Criterio de Entrada

- [x] F-03 cerrada: Seed-B ejecutado · 31 atletas inscriptos con APs correctas
- [x] Torneo en estado `INSCRIPCION_ABIERTA`

## Escenarios

| ID | Actor | Dispositivo | Acción | Resultado esperado | Resultado real | Estado | Hallazgo |
|----|-------|-------------|--------|--------------------|----------------|--------|----------|
| F04-S01 | Organizador | Desktop | Verificar que el torneo ya está en `INSCRIPCION_ABIERTA` (abierto por Seed-B) | Estado `INSCRIPCION_ABIERTA` visible en panel del organizador | Estado "Inscripción Abierta" confirmado | ✅ PASS | — |
| F04-S02 | Portal (visitante) | Desktop | Acceder a `/portalapnea` y verificar torneo | Torneo muestra estado "Inscripción abierta" · chips de disciplinas/categorías visibles | Torneo visible · badge correcto · chips presentes | ✅ PASS | M-04-01 |
| F04-S03 | Visitante | Desktop | Clic en "Inscribirse" sin estar logueado | Redirige a login · post-login regresa al formulario de inscripción | Redirigió a login · post-login llegó al formulario (fix H-04-02) | ✅ PASS | H-04-02 |
| F04-S03b | Visitante nuevo | Desktop | Registrar cuenta nueva y completar inscripción al torneo | Cuenta creada · perfil atleta generado en primer wizard · inscripción confirmada | Flujo completo OK tras fixes H-04-03/04/05 · email falló (M-04-02) | ✅ PASS | H-04-03 H-04-04 H-04-05 |
| F04-S04 | Atleta (Guadalupe Fardi) | Móvil | Editar AP en DYN desde portal atleta | AP editable · nuevo valor guardado · visible en Mis Inscripciones | AP editada correctamente tras fix H-04-01 | ✅ PASS | H-04-01 |
| F04-S05 | Organizador | Desktop | Ver lista inscriptos DYN · verificar Guadalupe Fardi | Categoría "JUNIOR" legible · AP en metros | Aparece · categoría y AP correctos | ✅ PASS | — |

## Criterio de Salida

- [x] F04-S01: torneo verificado en `INSCRIPCION_ABIERTA`
- [x] Todos los escenarios 🔴 (S01..S04) en PASS
- [x] Guadalupe Fardi aparece en inscriptos DYN con AP declarada
- [x] Verificación cruzada organizador confirma la inscripción de Guadalupe Fardi
