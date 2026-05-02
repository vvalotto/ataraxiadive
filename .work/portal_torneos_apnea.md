# Portal Público de Torneos de Apnea

## Interpretación consolidada de los apuntes

## Objetivo general

Construir un portal público de torneos de apnea que permita visualizar
el calendario de competencias planificadas y ofrecer acceso diferenciado
según el rol del usuario.

El sistema debe permitir que los torneos sean creados previamente por
organizadores autorizados, de modo que luego puedan ser consultados
públicamente por atletas, jueces, entrenadores o cualquier interesado.

------------------------------------------------------------------------

## Concepto principal

El portal debe funcionar como un punto central de consulta y gestión de
torneos.

Debe existir:

-   una vista pública de torneos planificados
-   acceso mediante login para usuarios registrados
-   posibilidad de registro de nuevos usuarios
-   administración de torneos por parte de organizadores autorizados

Esto implica definir claramente quién puede crear, modificar y
administrar torneos.

------------------------------------------------------------------------

## Pregunta clave de diseño

### ¿Conviene que los organizadores sean también los administradores?

Esta es una decisión funcional importante.

### Opción 1: Organizadores = Administradores

Ventajas:

-   modelo más simple
-   menos burocracia
-   menos intermediación
-   mayor velocidad operativa

Desventajas:

-   menos control
-   mayor riesgo de inconsistencias
-   menor supervisión central

### Opción 2: Organizadores ≠ Administradores

Ventajas:

-   mayor control institucional
-   validación centralizada
-   mejor trazabilidad

Desventajas:

-   mayor complejidad
-   más pasos administrativos
-   posible lentitud operativa

Esta decisión impacta directamente en el diseño de roles y permisos.

------------------------------------------------------------------------

## Gestión por roles

De acuerdo al rol del usuario, se dirigirá al portal correspondiente.

Es decir, el sistema deberá presentar diferentes accesos o paneles según
el perfil:

-   visitante público
-   atleta
-   organizador
-   juez

Cada rol tendrá acciones y permisos distintos.

------------------------------------------------------------------------

## Acciones desde cada torneo en el portal público

Cada torneo publicado debe permitir distintas acciones según su estado.

### Si el torneo está abierto

Acción:

-   visualizar datos del torneo


### Si el torneo está disponible para inscripción

Acción:

-   ir al formulario de inscripción

El usuario debe poder registrarse como participante y completar los
datos requeridos.

------------------------------------------------------------------------

### Si el torneo está en ejecución

Acción:

-   ir al panel del torneo

