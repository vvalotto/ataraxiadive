# Plan de Implementación — US-ADJ-1.3

**US:** US-ADJ-1.3 — Consolidar _build_stream_id en módulo compartido
**Sprint:** SP-ADJ-01
**Branch:** feature/SP-ADJ-01
**Estimado:** 20 min
**BDD:** omitido (refactor técnico puro)

---

## Tareas

| ID | Tarea | Archivo | Est. |
|----|-------|---------|------|
| T1 | Crear `_stream_ids.py` con `performance_stream_id` + `competencia_stream_id` | `src/competencia/application/commands/_stream_ids.py` | 5 min |
| T2 | Actualizar 6 handlers Performance (registrar_ap, llamar_atleta, registrar_resultado, registrar_dns, corregir_resultado, asignar_tarjeta) | `application/commands/` | 8 min |
| T3 | Actualizar 5 handlers Competencia (generar_grilla, ajustar_grilla, confirmar_grilla, iniciar_competencia, configurar_intervalo_ot) | `application/commands/` | 7 min |
| T4 | Verificar que no queda ningún `_build_stream_id` en src/ | — | 2 min |
| T5 | Correr suite completa — validar 0 fallos | — | 5 min |

---

## Issues resueltos

- **ADJ-02** — 11 copias de `_build_stream_id` → 2 funciones canónicas en módulo compartido

---

*Generado: 2026-03-28 — Fase 2 /implement-us US-ADJ-1.3*
