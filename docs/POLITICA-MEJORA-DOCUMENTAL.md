# Política de mejora documental — AtaraxiaDive

> Estado documental: vigente
> Fuente de verdad para: criterios de mantenimiento de la documentación
> Última actualización: 2026-05-31

La documentación debe reflejar **lo que efectivamente se implementó**: consistente con el código y los tests, coherente entre documentos, sin duplicidades ni redundancia.

## Principios

1. **Fuente única por tema.** Cada tipo de información tiene una sola fuente de verdad; los demás documentos la resumen o la enlazan, no la reescriben. La autoridad por tema está en [`inventario/FUENTES-DE-VERDAD-DOCUMENTAL.md`](inventario/FUENTES-DE-VERDAD-DOCUMENTAL.md).
2. **Reflejar lo implementado.** Ante contradicción entre documento y código/tests, manda el código. Los documentos vigentes deben actualizarse al estado real.
3. **No reescribir la historia.** Los planes y análisis previos no se corrigen para parecer actuales: se rotulan como *histórico* con la convención de encabezado de FUENTES §5.
4. **Enlazar, no duplicar.** Todo documento derivado enlaza a su fuente principal; se evita copiar tablas, árboles o glosarios que ya viven en otro lugar.

> El procedimiento de adecuación (inventario → fuentes de verdad → mapa → contenido) está en [`PLAN-ADECUACION-DOCUMENTAL.md`](PLAN-ADECUACION-DOCUMENTAL.md).
