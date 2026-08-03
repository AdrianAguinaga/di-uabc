# Generador de Diseño Instruccional — UABC

## Qué es

Sistema que genera el **Diseño Instruccional (DI)** de una unidad de aprendizaje de la UABC en
`.docx` y `.pdf`, a partir de su **PUA** oficial, el **calendario escolar** vigente, el profesor,
la modalidad y los grupos. Rellena las **plantillas CIAD reales** para conservar el formato
institucional.

## Problema que resuelve

Hoy cada DI se redacta a mano en Word: se copian los datos del PUA, se recalculan las fechas contra
el calendario escolar, se reparten los porcentajes y se repiten las políticas de curso para cada
grupo. El ejemplo `ejemplos/961 (1).pdf` (Big Data, semipresencial, 2026-1) son ~874 líneas de
documento derivadas casi mecánicamente de un PUA de 10 secciones, un calendario y un esquema de
evaluación.

El trabajo mecánico domina al trabajo de criterio. Y los errores de fecha o de porcentaje tienen
consecuencias reales frente a los alumnos.

## Para quién

Dos profesores de la UABC:
- **Adrian Rodriguez Aguiñaga** (adrian.aguinaga@uabc.edu.mx)
- **Zurisaddai Rubio Arriaga**

Una misma materia puede impartirse a varios grupos (961, 962, …); cada grupo necesita su propio
documento con su bloque de firma de jefe de grupo.

## Resultado esperado

Pasar de *"redactar un DI"* a *"responder seis preguntas y revisar el borrador"*.

El documento generado es **fusionado**: plantilla CIAD (Secciones 1–3) + criterios de evaluación
del curso + reglas de convivencia con sanciones + fundamento legal + firma del jefe de grupo.

## Restricciones

1. **Formato institucional intacto.** Se rellenan las plantillas CIAD reales; no se reconstruyen.
2. **Fechas del calendario oficial.** Nunca estimadas. El ciclo 2026-2 tiene **16 semanas**
   (10 ago – 28 nov 2026), no las 17 que asume la plantilla.
3. **Respaldo legal explícito.** Citas al Estatuto Escolar (Arts. 66, 68, 70, 71) para que ningún
   alumno pueda alegar desconocimiento.
4. **Trazabilidad total.** Cada salida registra su PUA y hash, calendario, versión de plantilla,
   profesor, grupo, esquema y commit.
5. **Git local únicamente.** Sin remoto, sin push.
6. **Opus planifica, Sonnet ejecuta.** Perfil GSD `adaptive`.

## Alcance de la v1

Las tres modalidades (semipresencial, escolarizada, a distancia), ciclo 2026-2, los dos profesores,
multi-grupo, salida `.docx` + `.pdf`, banco de conocimientos en Markdown, grafo de conocimiento del
dominio.

**Fuera de alcance por ahora:** publicación automática en Blackboard, generación de rúbricas
detalladas, remoto git.

## Lo que el sistema no hace

No sustituye el criterio docente. Estructura, fecha y valida; la redacción pedagógica de las metas
la produce Opus y **requiere revisión del profesor** antes de entregarse.
