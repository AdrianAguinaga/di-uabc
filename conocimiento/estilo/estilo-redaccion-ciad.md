---
titulo: "Estilo de redacción recomendado CIAD para el Diseño Instruccional"
fuente: "referencias/CIAD_DI_EstiloRedaccionRecomendado_2023.docx"
tipo: estilo
version: "2023"
convertido: 2026-08-03
---

# Estilo de redacción recomendado CIAD

> **Nota de extracción:** este archivo está redactado para ser **directamente accionable por un
> generador automático**: cada regla tipográfica y de conjugación verbal se enuncia como una
> instrucción de renderizado, no sólo como prosa descriptiva. Reproduce el contenido literal del
> `.docx` original (convertido con `pandoc -t markdown --wrap=none`) y añade señalamientos "Regla
> para el renderizador" donde aplica.

## Sobre la descripción de las actividades

Al describir las actividades de una meta (Sección 3 de las plantillas de diseño instruccional),
debe proporcionarse una **secuencia, paso por paso**, de lo que el estudiante deberá hacer para
lograr la meta indicada.

La descripción debe incluir:
- La(s) actividad(es) que se realiza(n).
- Los contenidos y recursos revisados.
- Las herramientas de comunicación, colaboración y/o evaluación utilizadas, y de qué forma.
- Las evidencias o productos a elaborar, con las características que deben cumplir.

**Modalidad semipresencial:** distinguir con una leyenda las actividades del momento no
presencial de las presenciales. Las presenciales pueden enunciarse en lo general; las no
presenciales deben describirse con detalle. Leyendas recomendadas: *"En el salón"*, *"En el
laboratorio/taller"*, *"En plataforma"*, *"Fuera del aula"*, antepuestas a los pasos ubicados en
ese entorno de aprendizaje.

## Sobre el lenguaje: reglas de conjugación verbal (obligatorias para el generador)

| Regla | Sujeto | Tiempo verbal | Ejemplo |
|---|---|---|---|
| Verbos de actividad | — | **Imperativo no formal**, singular o plural según sea individual o colaborativa | *realiza, investiga, entrega, redacta, lee* |
| Actividades del **alumno** | Alumno | **Presente o futuro** | "revisarás junto a tus compañeros…", "En la sesión presencial realizarás ejercicios…" |
| Actividades del **docente** | Docente | **Siempre futuro** | "el profesor conducirá la revisión…" |
| Reflexión de aprendizaje (¿Cómo sabré que logré la meta?) | Alumno, retrospectivo | **Siempre pasado** | *Identifiqué…, Localicé…, Describí…, Analicé…* |

**Regla para el renderizador:** verificar la conjugación generada contra esta tabla antes de
insertar texto en la Sección 3 de un DI. Si el sujeto es el alumno describiendo una actividad
futura, usar presente o futuro; si es la reflexión final, usar siempre pretérito.

## Convenciones tipográficas (obligatorias para el generador)

| Elemento | Formato | Ejemplo |
|---|---|---|
| **Nombres de recursos** (documentos, videos, presentaciones que el docente publica) | **Negrita + cursiva** | ***Meta 1.1_México vive crisis de lectura*** |
| **Tipo de evidencia** a realizar (lo que el alumno debe producir) | **Negrita + subrayado** | **[Mapa conceptual]{.underline}** dentro del texto de la actividad |
| **Meta y su porcentaje** de calificación | **Negrita** | La **meta 1.1** equivale al **5%** de tu calificación final. |
| Espacios de entrega en plataforma (donde se adjunta el archivo) | Negrita | Adjunta tu archivo en el espacio de entrega **Meta 1.1_Mapa Conceptual**. |

## Convención de nombres de recursos y entregables

> **Nota de extracción — discrepancia detectada entre fuentes:** este documento (Estilo de
> redacción) usa consistentemente el prefijo **`Meta 1.1_<Nombre>`** (palabra completa "Meta",
> con espacio) en todos sus ejemplos, mientras que los documentos de instrucciones de llenado
> (`CIAD_DI_Plantilla_Semipresencial_Instrucciones-2025.docx` y
> `CIAD_DI_Plantilla_A_Distancia_Instrucciones-2025.docx`, ver
> `conocimiento/plantillas/instrucciones-llenado.md`) usan el prefijo abreviado **`M1.1_<Nombre>`**
> (sin la palabra "Meta"). Ambas formas aparecen en los documentos oficiales CIAD; no se puede
> afirmar cuál es la "correcta" sin más contexto — se documentan ambas y se deja a criterio del
> proyecto (`AGENTS.md` declara `M1.1_<Nombre>` como la convención vigente para el generador,
> siguiendo el estilo más reciente de instrucciones 2025 sobre el de estilo 2023).

Convención de nombrado (según `AGENTS.md`, tomando la forma abreviada de las instrucciones
2025 como la vigente para el generador):

- **Recurso publicado por el docente:** `M1.1_<Nombre del recurso>`
- **Archivo que entrega el alumno:** `M1.1_Apellido_Nombre` (ejemplo del propio documento de
  estilo: *"Meta 1.1_Apellido_Nombre (Ej: Meta 1.1_Torres_Bodet)"*; ejemplo de las instrucciones:
  *"M2.7_Apellido_Nombre (Ej: M2.7_Garrido_Canabal_Tomás)"*)

## Ejemplos de redacción por tipo de actividad (literal del documento fuente)

### Revisión de materiales

> A) Revisa las lecturas disponibles para el desarrollo de esta meta:
> - ***Meta 1.1_México vive crisis de lectura*.**
> - ***Meta 1.1_México Lee: Programa de fomento para el libro y la lectura*.**
>
> B) Lee el documento "***Meta 1.1_México vive crisis de lectura***", en el cual...

*Nota del documento: se pone en negritas y cursiva los nombres de recursos.*

### Búsqueda documental

> A) Realiza una búsqueda documental, en fuentes confiables, donde/sobre localices los
> principales indicadores en materia educativa del Sistema Educativo Mexicano, tanto Nivel
> Nacional como Internacional.
>
> B) Investiga, en fuentes confiables de internet, sobre los principales indicadores en materia
> educativa del Sistema Educativo Mexicano, tanto Nivel Nacional como Internacional.

### Elaboración de evidencias

> A) Elabora un **[Mapa conceptual]{.underline}** donde integres los siguientes conceptos:
> Aprendizaje, Teoría, Conducta, Definición, características, tipos y estilos de aprendizaje. Para
> ello, consulta el documento **Características de Evidencias** y dirígete a características de
> mapa conceptual para que puedas realizarlo.

*Nota del documento: se escribe subrayado y en negritas el tipo de evidencia a realizar, y en
negritas los documentos que complementan la actividad.*

### Realización de actividades en el aula (se redactan en futuro singular)

> A) En la sesión presencial revisarás junto a tus compañeros información acerca de los
> principales indicadores en materia educativa del Sistema Educativo Mexicano, tanto Nivel
> Nacional como Internacional.
>
> B) En la sesión presencial realizarás ejercicios para comprender mejor el tema de los
> principales indicadores en materia educativa del Sistema Educativo Mexicano, tanto Nivel
> Nacional como Internacional.
>
> C) En la sesión presencial realizarás prácticas en el laboratorio que te permitirán
> experimentar y comprender mejor el tema de reacciones químicas.

### Envío y publicación de evidencias (en plataforma)

> A) Adjunta tu archivo en el espacio de entrega **Meta 1.1_Mapa Conceptual**. Recuerda guardarlo
> con el siguiente formato: Meta 1.1_Apellido_Nombre (Ej: Meta 1.1_Torres_Bodet).
>
> B) Publica tu actividad en el espacio de entrega **Meta 5.3_Blog.** Recuerda guardarlo con el
> siguiente formato: Meta 5.3_Apellido_Nombre (Ej: Meta 5.3_Torres_Bodet).

### Entrega de evidencias (en el aula)

> A) Entrega tu ejercicio impreso en la siguiente sesión presencial en el aula. Recuerda
> entregarlo en hojas de re-uso, sin portada, con tus datos de identificación y respetando las
> características dispuestas por el docente.

### Criterios de evaluación y calificación de la meta

> A) Puedes consultar la rúbrica de calificación en el espacio de entrega de la actividad.
>
> B) Puedes consultar los criterios de evaluación dentro del formato de elaboración.
>
> C) Los criterios de evaluación que deberá cumplir la evidencia son:

### Valor de la meta

> La **meta 1.1** equivale al **5%** de tu calificación final.

*Nota del documento: se escribe en negrita la meta y el porcentaje de calificación que se le
asigne específicamente a esa meta.* **Esta es la frase de valor exacta que el generador debe
reproducir por cada meta**, sustituyendo el número de meta y el porcentaje correspondiente.

### "Sabré que logré la meta si…" (reflexión de aprendizaje)

> - Identifiqué las características que describen a la diversidad como un valor (Enunciado sobre
>   el aprendizaje obtenido al revisar las lecturas obligatorias)
> - Localicé las condiciones generales de atención a los problemas de diversidad en las escuelas,
>   por medio de la búsqueda en fuentes confiables de internet (Enunciado sobre el aprendizaje al
>   realizar una búsqueda documental)
> - Describí los aspectos más relevantes sobre diversidad, basándome en las experiencias vividas
>   en mi contexto escolar (Enunciado sobre el aprendizaje que se obtiene al elaborar un producto)
> - Analicé el desarrollo histórico del concepto educación inclusiva (Enunciado ligado
>   directamente con la competencia de nuestra meta [Meta 3.1_Analizar las bases
>   histórico-conceptuales sobre educación inclusiva])

Todos los verbos de este bloque están en **pretérito** (pasado): *Identifiqué, Localicé,
Describí, Analicé.* Confirma la regla de conjugación de la tabla anterior.

## Ejemplo completo de descripción de meta semipresencial (del documento fuente)

### Meta 2.7 Analizar los avances en materia educativa durante el gobierno de Manuel Ávila Camacho (1940-1946).

**► ¿Qué voy a aprender?**
- Identificar los principales momentos históricos en materia educativa en el periodo de gobierno
  (1940-1946).
- Analizar el "proyecto educativo de unidad nacional", sus fundamentos y consecuencias.
- Contrastar el proyecto educativo del periodo en comparación al del gobierno de Lázaro Cárdenas
  del Río.

**► Actividad de aprendizaje | ¿Cómo lo voy a aprender?**

Carácter de la actividad: individual.

**En clase (25 de septiembre)**

**Primero**. En la clase, el profesor conducirá la revisión de las principales acciones que se
dieron en materia educativa durante el gobierno de Manuel Ávila Camacho (1940 a 1946), resaltando
la reforma al artículo 3ro, el proyecto educativo de unidad nacional, etc.
- ***Meta 2.7_Gobierno de Ávila Camacho y educación (presentación).***

**Segundo**. Adicionalmente, verás el documental:
- ***Meta 2.7_Manuel Ávila Camacho - La Unidad Nacional.***
  Krauze, E. (1999). El sexenio de Lázaro Cárdenas (Vol. 1). *Clío*. Recuperado de:
  https://www.youtube.com/watch?v=YC3-NGq_IV8

**Tercero**. Llenarás un formato en clase sobre lo aprendido del tema y compartirán algunas
primeras conclusiones grupales.

**Fuera de clase (antes del 27 de septiembre)**

**Cuarto**. Revisa los siguientes materiales:
- ***Meta 2.7_Educación para las ciudades. Las políticas educativas 1940-1982 (pp.2-4).***
  Lazarín, F. (1996). Educación para las ciudades. Las políticas educativas 1940-1982. *Revista
  Mexicana de Investigación Educativa, 1 (1)*. Recuperado de:
  http://www.redalyc.org/articulo.oa?id=14000112
- ***Meta 2.7_La escuela del amor en 1946. La ilusión por la educación de la unidad nacional,
  armónica y democrática.***
  Ortiz-Cirilo, A. (2015). *Laicidad y reformas educativas en México: 1917-1992*. México, D.F.:
  Universidad Nacional Autónoma de México, Instituto de Investigaciones Jurídicas.

**Quinto**. Posteriormente, descarga el **formato PNI**, y respóndelo a partir de cuáles fueron
las características del proyecto educativo de unidad nacional y su impacto.
- ***Meta 2.7_Cuadro PNI.***
- ***Meta 2.7_Cuadro PNI (tutorial).***

**Sexto**. Adjunta tu archivo en **Meta 2.7_Cuadro PNI_Proyecto educativo de unidad nacional**, a
más tardar el jueves **27 de septiembre a las 9am**. Recuerda guardarlo con el siguiente formato:
Meta 2.7_Apellido_Nombre (Ej: Meta 2.7_Garrido_Canabal_Tomás).

**En clase (27 de septiembre)**

**Séptimo**. Preséntate a la clase y participa en las actividades y discusión planteadas por el
docente.

**► Fechas de vencimiento/entrega:**
- **Meta 2.7_Cuadro PNI**, a más tardar el ***jueves 27 de septiembre a las 9am***.

**► Reflexión de aprendizaje | ¿Cómo sabré que logré la meta?**
- Identifiqué los principales avances en materia educativa durante el gobierno del presidente
  Manuel Ávila Camacho (1940-1946).
- Elaboré los ejercicios solicitados en clase y de tarea.
- Participé activamente en las actividades en clase.

La **meta 2.7** equivale al **10 %** de tu calificación final.

> **Nota de extracción:** este mismo ejemplo (con variaciones menores de redacción: "En clase" vs
> "En clase / sesión síncrona", "verás" vs "se verá") aparece repetido casi textualmente en
> `CIAD_DI_Plantilla_Semipresencial_Instrucciones-2025.docx` como el "Ejemplo de llenado" de la
> Sección 3 — confirma que el documento de estilo y el de instrucciones comparten el mismo caso
> de referencia (Meta 2.7, gobierno de Ávila Camacho).
