---
title: "ADR-019: Política de contraseñas y UX de fortaleza"
type: decision
last_updated: "2026-05-20"
sources:
  - docs/adr/ADR-019-politica-contrasenas.md
estado: Aceptada
fecha: 2026-04-24
bcs_afectados: [identidad]
rnf_refs:
  - RNF-05-seguridad-auditoria-inalterable
---

# ADR-019: Política de contraseñas y UX de fortaleza

## Decisión

Tres decisiones de diseño adoptadas en conjunto durante INC-5.4:

1. **Política mínima:** 10 caracteres + 1 mayúscula + 1 número.
2. **Campo de confirmación** en el formulario de registro (validación solo frontend).
3. **Indicador visual de fortaleza** en tiempo real — componente `PasswordStrengthBar.tsx`.

## Por qué

La política original (8 caracteres) era insuficiente para una plataforma con datos de atletas y resultados oficiales. Se prioriza longitud sobre complejidad excesiva (alineado con NIST SP 800-63B): pasar de 8 a 10 caracteres multiplica el espacio de búsqueda por ~10⁴ en ataques de fuerza bruta sobre bcrypt. No se exigen símbolos — los gestores de contraseñas los generan de todos modos; obligarlos penaliza a usuarios sin gestor sin mejorar significativamente la seguridad.

## Niveles del indicador

| Nivel | Color | Criterio |
|-------|-------|----------|
| Débil | Rojo | No cumple alguno de los 3 criterios mínimos |
| Buena | Amarillo | Cumple los 3 criterios (10+, mayúscula, número) |
| Fuerte | Verde | 14+ caracteres + cumple los 3 criterios |

## Consecuencias vigentes

- Política aplicada en: `RegistrarUsuarioHandler`, `CambiarPasswordHandler`, `ResetPasswordHandler`.
- Excepción de dominio: `PasswordDemasiadoCorto` en `identidad/domain/exceptions.py`.
- Indicador aplicado en: `RegistroPage`, `CambiarPasswordPage`, `ResetPasswordPage`.
- Las contraseñas existentes con 8-9 caracteres siguen siendo válidas — la política aplica solo a contraseñas nuevas.
- Tests que usen contraseñas de 8 caracteres (ej: `"apnea123"`) deben actualizarse (ej: `"Apnea1234!"`).

## ADRs relacionados

- [[ADR-013-exception-management]] — `PasswordDemasiadoCorto` sigue la jerarquía de excepciones de dominio
- [[ADR-020-modelo-usuarios-roles]] — el flujo de registro donde aplica la política
