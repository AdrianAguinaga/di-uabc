---
titulo: "Diseño Instruccional — Contabilidad Financiera, grupo 531, ciclo 2026-1"
fuente: "ejemplos/38985-531-2026-1-Rubio Arriaga Zurisaddai.docx"
sha256: "8219ec353697e7137afe2ea4778c7f104ebc7010a3f7344954c759842b32b619"
materia: "Contabilidad Financiera"
clave: "38985"
programa: "Licenciatura en Contaduría"
modalidad: semipresencial
ciclo: "2026-1"
docente: "Dra. Zurisaddai Rubio Arriaga"
correo: "rubio.zurisaddai@uabc.edu.mx"
coordinadora_area: "Dra. Bianca Janeth López Campillo"
etapa: "Básica"
creditos: "CR: 8, HC: 2, HT: 4, HE: 2"
unidades: 6
semanas: 16
extraido: 2026-08-04   # con python-docx; 404 párrafos y 5 tablas
---

# El segundo ejemplo: DI de Contabilidad Financiera 531 (2026-1)

El [ejemplo dorado](961-big-data-2026-1.md) es de Adrian y fija el **formato**. Este es de otra
docente y fija algo distinto: **que el formato admite más de un estilo de evaluación**.

> **No es oráculo de formato.** Para eso está el 961. Este documento se conserva porque de él
> salen los criterios propios de `zra` que hoy viven en `config/politicas.yaml`, y porque muestra
> una estructura de calificación en dos niveles que el 961 no tiene.

Se leyó con `python-docx`. **No abras el `.docx` para consultarlo**: está aquí para eso.

## Lo que este documento tiene y el 961 no

| | 961 (Adrian) | 531 (Zurisaddai) |
|---|---|---|
| Rubros | Exámenes 20 · Tareas 40 · Proyecto 40 | Actividades 30 · **Exámenes 50** · Trabajo final 20 |
| Segundo nivel | — | **Promedio 60 % + Examen ordinario 40 %** |
| Valor de meta | porcentaje (`5%`) | **puntos** (`10 puntos`), 150 en total = 30 % |
| Exámenes | 2 parciales, meta propia | **3**, dentro de la actividad de una meta |
| Numeración | `0` de encuadre, luego `1.1`, `1.2` | cada unidad abre en `.0`: `1.0`, `2.0`… |
| Exención | promedio ≥ 80 | promedio ≥ **90** + 95 % de tareas + trabajo final |
| Trabajo final | proyecto integrador | **requisito de acreditación**: sin él, máximo 50 |
| Rúbrica | — | tabla de 100 puntos para el trabajo final |
| Firma docente | nombre | nombre **con título** («Dra.») |
| Cierre | — | «Nota inamovible» con el código de ética |

## Estructura de la calificación

Es de **dos niveles**, y ahí está la diferencia de fondo con el 961.

Primero, cómo se compone el promedio del curso (tabla 0 del documento):

| No. | Evidencia | Porcentaje |
|---|---|---|
| 1 | Entrega de actividades en clases y tareas (150 puntos) | 30 % |
| 2 | Exámenes parciales | 50 % |
| 3 | Trabajo final completo (observar los requisitos de forma y fondo) | 20 % |
| | **TOTAL** | **100 %** |

Y después, cómo ese promedio se combina con el examen ordinario (tabla 1):

| | |
|---|---|
| Valor del promedio antes del Examen Ordinario | 60 % |
| Valor del examen Ordinario | 40 % |
| Calificación de unidad de aprendizaje | 100 % |

**Ese segundo nivel no existe en el modelo del generador.** `curso.yaml` declara rubros que suman
100 y ahí termina; no hay forma de decir «y todo esto vale el 60 % de la calificación final».

Los tres exámenes reparten el 50 %: **Examen I 15 %** (semana 8), **Examen II 15 %** (semana 12),
**Examen III 20 %** (semana 15).

### Defecto verificado: los puntos no suman

El rubro de actividades declara **150 puntos**, pero solo hay **14 metas de 10 puntos = 140**.
Faltan 10.

Es el mismo tipo de defecto que el 961 tiene en sus rubros, y la razón por la que existe la regla
**R2** —que las metas sumen lo declarado rubro por rubro, no solo en total—. Si al reconstruir
este curso el resultado sale idéntico, defecto incluido, el validador no sirve.

## Criterios de acreditación y evaluación (literal)

Ya están registrados en `config/politicas.yaml` con el filtro `profesores: [zra]`.

> **Criterios de acreditación:** Desarrollar, presentar y cumplir en tiempo y forma con las
> actividades descritas en cada una de las metas del curso, como pueden ser: trabajos de
> investigación; solución de casos prácticos (los requisitos y características se detallan en cada
> actividad).
>
> El trabajo final completo es requisito para acreditar la materia, en caso no entregarse
> completo, la calificación máxima será de 50. En los casos que el motivo de reprobación sea el no
> entregar el trabajo final en tiempo y forma, será requisitos para presentar examen
> extraordinario, además de los establecidos en el estatuto universitario.

> **Evaluación.** El alumno deberá seguir los siguientes lineamientos para tener derecho a su
> calificación final:
>
> - Todas las tareas virtuales deberán ser entregadas a más tardar el día y hora asignada mediante
>   la plataforma blackboard (no se recibirán por correo electrónico).
> - Las tareas asignadas en clases presenciales tienen que entregarse durante dicho horario,
>   recibiendo un sello de la actividad por parte del docente en curso para que se pueda
>   contabilizar como actividad entregada.
> - La asistencia a clase no forma parte de los criterios para evaluar el curso (debe contar con
>   el 80 % para tener derecho a calificación).

> **La exención del examen final queda a juicio del maestro**, siempre y cuando: el alumno reúna
> cuando menos el 80 % de asistencia; tenga promedio igual o superior de **90** en exámenes
> parciales; haya cubierto el **95 %** de las tareas y trabajos durante el semestre; y entregue el
> trabajo final completo en tiempo y forma.

> **Derecho a examen ordinario:** 80 % de asistencia y entregar el trabajo final completo; en caso
> de no entregarse, la calificación máxima del curso será de 50.
>
> **Derecho a examen extraordinario:** 60 % de asistencia. Haber entregado el trabajo final en
> periodo ordinario completo; en caso contrario, se asignará un nuevo trabajo final para elaborar
> y ser entregado en la fecha y horario del examen extraordinario.

> **Nota inamovible:** Conducirse dentro y fuera de la Universidad Autónoma de Baja California de
> acuerdo con el código de ética vigente que cita los siguientes valores: Confianza, Democracia,
> Honestidad, Humildad, Justicia, Lealtad, Libertad, Perseverancia, Respeto, Responsabilidad y
> Solidaridad.

Se buscó esa «nota inamovible» en las cuatro plantillas CIAD, en las instrucciones de llenado y en
las políticas de curso 2025: **no está en ninguna**. Es aportación suya.

## Plan de actividades

Seis unidades en dieciséis semanas. Cada unidad abre con una meta `.0`.

| Meta | Sem | Actividad evaluada | Valor |
|---|---|---|---|
| 1.0 Presentar el encuadre del curso | 1 | Examen diagnóstico | 0 |
| 1.1 Identificar las fórmulas de asignación de costos | 2 | Registro en libro diario y tarjetas de almacén | 10 pts |
| 1.2 Distinguir y comparar los sistemas | 3 | Cuadro comparativo | 10 pts |
| 2.0 Registrar operaciones especiales | 4 | Investigación documental | 10 pts |
| 2.1 Registrar las operaciones | 5 | Registros contables y tarjetas auxiliares | 10 pts |
| 2.2 Registrar las operaciones | 6 | Registros contables y tarjetas auxiliares | 10 pts |
| 2.3 Registrar las operaciones | 7 | Registros contables y tarjetas auxiliares | 10 pts |
| 2.4 Reconocer las ventas | 8 | Investigación documental **/ Examen I** | 10 pts / 15 % |
| 3.0 Identificar la estimación | 9 | Investigación documental | 10 pts |
| 3.1 Comparar los métodos | 10 | Investigación documental | 10 pts |
| 3.2 Identificar los métodos | 11 | Investigación documental | 10 pts |
| 3.3 Registrar gastos y productos | 12 | Investigación documental **/ Examen II** | 10 pts / 15 % |
| 4.0 Elaborar saldos ajustados | 13 | Hoja de trabajo individual | 10 pts |
| 5.0 Registrar los valores ajenos | 14 | Registros contables | 10 pts |
| 6.0 Elaborar el estado de resultados | 15 | Estado de resultados y balance **/ Examen III** | 10 pts / 20 % |
| 6.1 Entregar trabajo final | 16 | Entrega del trabajo final | 20 % |

Los exámenes **no tienen meta propia**: viven dentro de la actividad de la meta de esa semana.
Es la diferencia que más pesa para el generador, porque **R3 cuenta metas de tipo
`examen_parcial`** — con este trazado contaría cero y el curso no validaría.

### Unidades

1. **Fórmulas de asignación de costos** — Formular los estados financieros y sus notas, a partir
   de la balanza de comprobación, la técnica y normatividad contable.
2. **Operaciones especiales** — Elaborar registros contables pertinentes mediante la aplicación de
   las operaciones especiales.
3. **Ajustes** — Identificar las cuentas sujetas a ajustes por los procedimientos de registro de
   inventario perpetuo y analítico.
4. **Elaboración de la hoja de trabajo** — Elaborar la hoja de trabajo a partir de la balanza de
   comprobación y la incorporación de los ajustes.
5. **Cuentas de orden** — Identificar la aplicación de las cuentas de orden en los registros
   contables.
6. **Estados financieros** — Elaborar un paquete de información financiera a partir de la hoja de
   trabajo.

## Anatomía de una meta (Sección 3)

El orden de los bloques difiere del 961: aquí **el valor va antes de la reflexión**, no después.

```
Meta 1.1. Identificar las fórmulas de asignación de costos de inventarios
En clase / sesión síncrona (03 de Febrero)

► ¿Qué voy a aprender?
► Actividad de aprendizaje | ¿Cómo lo voy a aprender?
    Carácter de la actividad: individual y/o colaborativa.
    Primero. …  Segundo. …  Tercero. …
    Fuera de clase / actividad asincrónica
    Quinto. …  Sexto. …  Octavo. …
► Fechas de vencimiento/entrega:
► Valor de la actividad:
► Reflexión de aprendizaje | ¿Cómo sabré que logré la meta?
```

Tres rasgos suyos de redacción:

1. **Los pasos se numeran con ordinales en palabra** —«Primero», «Segundo», «Tercero»— y la
   numeración **es continua entre lo presencial y lo asincrónico**. En el DI real salta: la meta
   1.1 va Primero, Segundo, Tercero, luego Quinto, Sexto y Octavo. Faltan el cuarto y el séptimo.
2. **Cada meta declara el carácter de la actividad** en la primera línea de la actividad:
   «Carácter de la actividad: individual y/o colaborativa.»
3. **Las referencias bibliográficas van dentro de la actividad**, en APA y a cuerpo entero, no
   como recurso aparte.

Y la hora de entrega no es la medianoche del 961, sino **«Sábado 07 de Febrero, antes de las 10:00
horas»**.

## Rúbrica del trabajo final

Cien puntos. No hay nada equivalente en el 961 ni en la plantilla CIAD.

| Concepto | Puntos |
|---|---|
| Portada | 2 |
| Introducción | 2 |
| Catálogo de cuentas | 2 |
| Redacción del caso práctico | 2 |
| **Libro diario** | **40** |
| Libro Mayor | 10 |
| Hoja de trabajo | 10 |
| Tarjetas de almacén | 5 |
| Auxiliares de moneda extranjera | 5 |
| Estado de resultados y sus notas | 10 |
| Balance general y sus notas | 10 |
| Conclusión | 2 |
| **Puntos totales** | **100** |

Cada concepto lleva su descripción en el documento. Varias piden **hipervínculos entre
documentos** —del libro diario al mayor, del mayor a la hoja de trabajo—, que es un requisito de
forma propio de esta materia y probablemente no generalizable a otras suyas.

## Bloque de firma

Cuatro filas: jefe de grupo (nombre, correo, teléfono, firma), docente (nombre y correo, firma) y
**coordinador de área**, que en el 961 no aparece.

```
Nombre jefe de grupo: ____   Firma ____
Nombre Docente: Dra. Zurisaddai Rubio Arriaga   ·   rubio.zurisaddai@uabc.edu.mx   Firma ____
Nombre del coordinador de área: Dra. Bianca Janeth López Campillo
```

## Qué falta para poder reproducirlo

- **El PUA 38985 no está ingerido.** Sin él no hay `pua_ref` ni `pua_sha256`, y los temas de cada
  unidad —que salen de la §V del programa— no existen en el repositorio. Este DI trae las
  competencias de unidad, pero no sus temas.
- **El calendario 2026-1 tampoco está.** Solo hay `calendarios/2026-2.yaml`.
- Del modelo faltan el segundo nivel 60/40, los valores en puntos y la tabla de rúbrica.
