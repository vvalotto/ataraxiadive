# Validacion BDD - US-5.5.1

## Feature

`tests/features/US-5.5.1-inscripcion-atleta-ap.feature`

## Resultado

Cobertura BDD materializada en archivo feature, con **waiver de automatizacion UI**.

La historia redefine un flujo React multipantalla (`S-01..S-06`) y el repositorio no
cuenta hoy con harness browser para ejecutar estos escenarios end-to-end con Router,
React Query y mocks HTTP integrados.

## Escenarios cubiertos

- wizard de inscripcion de 3 pasos;
- bloqueo de envio sin adjuntos obligatorios;
- declaracion de AP desde pantalla dedicada;
- modificacion de AP mientras el periodo sigue abierto;
- estado de solo lectura `AP cerrado` tras cierre del periodo.

## Validacion aplicada

- revision manual contra la spec `docs/specs/sp5/US-5.5.1.md`;
- verificacion de rutas y build TypeScript/Vite;
- test unitario focalizado del cambio semantico en `RegistrarAPHandler`.

## Riesgo residual

Sin browser automation, los escenarios UI quedan validados por inspeccion de codigo
y build, no por simulacion automatizada de clicks/navegacion.
