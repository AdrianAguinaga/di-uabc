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
5. **El push es del usuario.** El remoto existe —`github.com/AdrianAguinaga/di-uabc`, público desde
   el 3 de agosto de 2026— pero commitear es reversible y publicar no: se empuja solo a petición
   explícita. Ningún PUA ni dato de un tercero se versiona sin preguntar antes.
6. **Opus planifica, Sonnet ejecuta.** Perfil GSD `adaptive`.

## Alcance de la v1

Las tres modalidades (semipresencial, escolarizada, a distancia), ciclo 2026-2, los dos profesores,
multi-grupo, salida `.docx` + `.pdf`, banco de conocimientos en Markdown, grafo de conocimiento del
dominio.

**Fuera de alcance por ahora:** publicación automática en Blackboard, redacción automática del
contenido de una rúbrica.

## Milestone actual: v2.0 Estructura de calificación variable

**Meta:** que el generador soporte el esquema de calificación de un segundo docente sin que el de
Adrian cambie ni un carácter — lo mismo que hizo el filtro `profesores:` con los criterios de
acreditación, pero ahora en la aritmética de la nota.

**Rasgos a construir:**

| # | Rasgo | Qué asumía el modelo | Estado |
|---|---|---|---|
| 1 | Segundo nivel de calificación: promedio de metas **60 %** + examen ordinario **40 %** | Los rubros suman 100 y ahí termina | Fase 11, sin empezar |
| 2 | Metas en **puntos** (`10 pts`), con R1 y R2 operando en la unidad declarada | `valor` es siempre porcentaje | **Validación hecha** (Fases 9 y 10); falta el renderizado (Fase 13) |
| 3 | Numeración de metas **`1.0`, `2.0`** — cada unidad abre en `.0` | `0` de encuadre y luego `1.1`, `1.2` | **Hecho** (Fase 9) |
| 4 | **Varios exámenes parciales dentro de la actividad** de una meta, contables por R3 | R3 contaba metas de tipo `examen_parcial`; así contaría cero y fallaría | **Hecho** (Fase 10) |
| 5 | **Tabla de rúbrica** del trabajo final, 100 puntos, renderizada en el documento | No existe | Fases 12 y 13, sin empezar |

**Estado al 6 de agosto de 2026:** las Fases 9 y 10 están hechas y verificadas. El contrato
`curso.yaml` ya admite puntos, componentes e identificadores libres, y **las reglas ya los leen**:
`Curso.aportes()` es la única definición de «lo que cuenta para un rubro», R2 compara contra
`Rubro.base` y R3 cuenta los exámenes parciales se declaren donde se declaren. Lo que queda es
aritmética nueva (Fase 11), la rúbrica (Fase 12), el documento (Fase 13) y la prueba de fuego
(Fase 14).

**Origen:** el DI real de Zurisaddai Rubio Arriaga
(`ejemplos/38985-531-2026-1-Rubio Arriaga Zurisaddai.docx`, Contabilidad Financiera 38985, grupo
531, 2026-1, semipresencial). Al reconstruirlo con el generador
(`cursos/2026-2/38985-contabilidad-financiera/`) hubo que **traducir** su estructura —puntos a
porcentajes, exámenes a metas propias— para que validara. Esa traducción es la deuda que cierra
este milestone.

**Criterio de aceptación del milestone entero — la no contaminación:** regenerar Big Data (39056) y
Patrones (39062) después de cada fase debe dejar la **huella de texto idéntica**. Si cambia algo de
un documento de Adrian, el trabajo está mal aunque las pruebas pasen. Es la misma prueba que se
aplicó al registrar los criterios propios de cada docente.

**Restricciones heredadas que no se relajan:**

- El renderizador **no inventa** (REQ-26): la rúbrica se **declara** en `curso.yaml` y se imprime.
  Redactar sus criterios sigue siendo del docente, y por eso «rúbricas detalladas» sale de
  *fuera de alcance* solo como renderizado, no como generación de contenido.
- R2 debe seguir atrapando el defecto del ejemplo 961 —`test_detecta_el_defecto_del_ejemplo_961`—
  y su análogo en puntos: el rubro de trabajos de ella declara **150 pts cuando solo suman 140**.
- Las pruebas actuales pasan. Ninguna se rompe; se añaden. Eran 179 al abrir el milestone y son
  **245** tras la Fase 10.

**Prueba de fuego:** reescribir el `curso.yaml` de 38985 a su **estructura real** —puntos, 60/40,
metas `1.0`, exámenes dentro de la actividad— y que valide sin traducirlo.

## Evolution

Este documento evoluciona en las transiciones de fase y en las fronteras de milestone.

**Tras cada transición de fase** (vía `/gsd-transition`):
1. ¿Algún requisito quedó invalidado? → a *Fuera de alcance*, con su razón
2. ¿Algún requisito quedó validado? → a *Validados*, con la fase que lo validó
3. ¿Surgieron requisitos nuevos? → a *Activos*
4. ¿Hay decisiones que registrar? → a *Decisiones clave*
5. ¿«Qué es» sigue siendo exacto? → corregir si derivó

**Tras cada milestone** (vía `/gsd-complete-milestone`):
1. Revisión completa de todas las secciones
2. Comprobar el valor central — ¿sigue siendo la prioridad correcta?
3. Auditar *Fuera de alcance* — ¿siguen valiendo las razones?
4. Actualizar el contexto al estado real

## Lo que el sistema no hace

No sustituye el criterio docente. Estructura, fecha y valida; la redacción pedagógica de las metas
la produce Opus y **requiere revisión del profesor** antes de entregarse.
