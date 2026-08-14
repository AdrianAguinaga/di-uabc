# Ejemplos operativos de asesoría académica

Tres registros llenados, aportados por el usuario el 13 de agosto de 2026, permiten contrastar el
formato institucional nuevo con la práctica de la Facultad. Son **ejemplos operativos, no fuentes
normativas**: muestran cómo se ha trabajado el trámite, pero no crean reglas ni corrigen al PUA o al
calendario oficial.

Los originales contienen nombres y matrículas de estudiantes. Por ello no se copiaron a este
repositorio público. Esta nota conserva únicamente hallazgos despersonalizados y los hashes con los
que se puede comprobar la procedencia si el usuario decide custodiar los archivos en otro canal.

| Ejemplo | Ciclo observado | SHA-256 |
|---|---:|---|
| `LC TALLER DE TEMAS SELECTOS EN LA GF- FORMATO OTRAS MODALIDADES DE APRENDIZAJE 2025-1.pdf` | 2025-1 | `4b84eca3072dadc5aad2c5f1b460e51219decb54b90d2f9926f2098ff0a1364c` |
| `LC TALLER DE TEMAS SELECTOS EN LA GF- FORMATO OTRAS MODALIDADES DE APRENDIZAJE 2025-2 (1).doc` | 2025-2 | `f2f669471d674793c7f7322e4a90d5cdc3af8872ed13e959c13d93fc2d14c308` |
| `LAE FORMATO OTRAS MODALIDADES DE APRENDIZAJE .doc` | 2026-1 | `6aa1805d6932cf853eec23b2bd6a41e953c8c7c71f943efbec769b37e325a238` |

## Patrón común comprobado

- Los tres usan literalmente **“Unidad de Aprendizaje por Asesoría Académica”** como tipo de
  modalidad.
- La identificación reúne ciclo, clave, unidad de aprendizaje, horas/créditos, plan, etapa,
  programa educativo, estudiantes y docente responsable.
- La justificación explica por qué la unidad se cursará mediante asesoría; no sustituye la
  competencia ni la descripción de actividades.
- La competencia general procede del Programa de Unidad de Aprendizaje. Las competencias por
  unidad aparecen de manera opcional, tal como indica el formato nuevo.
- Las actividades se organizan por unidad y por rangos de semanas. El formato nuevo pide fechas;
  el renderizador las deriva del calendario oficial y no copia las fechas de un ejemplo anterior.
- La evaluación se presenta con rubros y un total de 100 %. Las referencias bibliográficas se
  toman del programa oficial.
- La nómina de estudiantes cambia entre ciclos aunque la unidad, el responsable y el contenido
  permanezcan. Son datos del registro, no del curso en abstracto.

## Lo que los ejemplos enseñan a no repetir

El ejemplo de Administración declara una unidad básica de registros contables, pero conserva una
justificación de otra materia: habla de etapa terminal, área financiera, pronósticos y maximización
del valor de la empresa. Es evidencia directa de un riesgo de copiar y pegar. Ninguna validación
mecánica puede decidir si una justificación es pedagógicamente correcta; el docente debe comprobar
que nombre, etapa, competencia, actividades y justificación hablan de la misma unidad.

El ejemplo de Contaduría usa los rangos 1–3, 4–6, 6–10 y 11–14: la semana 6 se solapa y no aparecen
las semanas posteriores. Esto no basta para declarar que el registro sea inválido —una actividad
puede abarcar o compartir semanas—, así que el generador no inventa una regla de cobertura exclusiva.

Los rubros de exámenes suman correctamente con los demás rubros, pero el texto no declara cuántos
exámenes parciales habrá. “Exámenes parciales 40 %” no demuestra por sí solo el mínimo de dos del
Art. 68. Mientras la evaluación de este formato siga siendo texto literal, esa comprobación queda
como revisión docente; no debe presentarse como validada automáticamente.

## Flujo reforzado

1. Confirmar que existen el PUA y el calendario oficial del ciclo. Si falta el calendario, detenerse.
2. Capturar un `registro.yaml` por unidad y ciclo. Los estudiantes y responsables son listas; las
   actividades declaran `inicio_semana`/`fin_semana` o un `periodo_calendario`, nunca ambos.
3. Comprobar que `periodo_estudio` coincide con `ciclo`, que las semanas pertenecen al calendario y
   que cada actividad tiene descripción.
4. Renderizar desde una copia fresca y verificada de la plantilla con
   `src/render_registro_modalidades.py`. La salida se sustituye solo cuando el documento completo se
   guardó correctamente.
5. Revisar manualmente la coherencia pedagógica, la literalidad de la competencia, la evaluación y
   la identidad de participantes y responsables. El documento sigue siendo borrador hasta esa
   revisión.

El formato nuevo, registrado como versión `2026-1`, es la autoridad de estructura. Los tres
ejemplos sirven para verificar contenido y flujo, no para regresar a sus rótulos o maquetación
anteriores.
