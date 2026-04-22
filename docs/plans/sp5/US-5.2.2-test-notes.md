# US-5.2.2 — Notas de Testing

**Fecha:** 2026-04-22

## Validaciones ejecutadas

```bash
./.venv/bin/pytest \
  tests/unit/competencia/domain/test_competencia_finalizar.py \
  tests/unit/competencia/application/test_p08_finalizacion.py \
  tests/unit/competencia/application/test_finalizar_competencia_manual.py \
  tests/integration/competencia/test_competencia_finalizada_integration.py
```

Resultado: `25 passed`.

```bash
npm run build
```

Resultado: OK.

```bash
npm run lint
```

Resultado: OK.

## Cobertura funcional

- Dominio: payload manual y compatibilidad de eventos historicos.
- Aplicacion: cierre manual exitoso, rechazo con pendientes y no-op si ya estaba
  finalizada.
- P-08: cierre automatico conserva comportamiento y registra origen automatico.
- Frontend: validacion estatica por build/lint; no hay harness automatizado de UI
  para esta pantalla.
