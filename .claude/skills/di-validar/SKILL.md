---
name: di-validar
description: Aplica las 8 reglas de validación a un Diseño Instruccional. Úsala antes de renderizar un DI a Word/PDF y después de editar a mano un curso.yaml. Acepta la ruta a un curso.yaml o al directorio del curso.
---

# Validar un Diseño Instruccional

Ejecuta `src/validar.py` sobre un `curso.yaml` y reporta los hallazgos.

## Uso

```
python src/validar.py cursos/<ciclo>/<clave>-<slug>/curso.yaml
```

Si el usuario da un directorio en vez de un archivo, agrégale `/curso.yaml`. Si no da nada,
lista los cursos disponibles con `ls cursos/*/*/curso.yaml` y pregunta cuál.

El código de salida es `1` cuando hay errores y `0` cuando no. **No renderices un DI cuyo
informe tenga errores.**

## Cómo leer el informe

| Nivel | Símbolo | Qué significa |
|---|---|---|
| error | `✗` | Bloquea la generación. Hay que corregir el `curso.yaml`. |
| aviso | `!` | No bloquea, pero requiere decisión del docente. |
| recordatorio | `·` | Indicador del IEDI que depende de la plataforma, no del documento. Se le informa al docente; el generador no puede comprobarlo. |

## Las ocho reglas

| # | Qué verifica | Fundamento |
|---|---|---|
| R1 | Los porcentajes del esquema suman exactamente 100; la exención cae en [60, 100]. | Arts. 65 y 67 |
| R2 | Las metas suman lo que declara el esquema — **rubro por rubro**, no solo en total. | Art. 67 |
| R3 | Hay al menos dos exámenes parciales. | Art. 68 |
| R4 | Toda unidad del PUA tiene al menos una meta; ninguna meta cuelga de una unidad inexistente. | — |
| R5 | Toda semana 1..N del calendario tiene actividad; ninguna meta cae fuera del ciclo. | Calendario oficial |
| R6 | Ninguna entrega cae en día de suspensión ni después del fin de cursos. | Calendario oficial |
| R7 | Están las citas legales obligatorias, cada regla de convivencia trae sanción, y cada grupo tiene su bloque de firma. | Art. 66 |
| R8 | Los indicadores indispensables del IEDI v2023-1 comprobables sobre el documento. | CIAD |

R2 es la que importa más de lo que parece: el ejemplo dorado `ejemplos/961 (1).pdf` suma 100
en total pero sus rubros no cuadran (Proyecto ~22 % contra 40 % declarado). Un validador que
solo revise el total deja pasar ese error.

## Al corregir

Corrige el `curso.yaml`, **nunca el informe ni el validador**. Si una regla te parece
equivocada, dilo antes de tocarla: las ocho están ancladas al Estatuto Escolar o al calendario
oficial, y relajarlas convierte el documento en algo que no se sostiene ante un alumno
inconforme.

Referencias: `conocimiento/rubricas/iedi-2023-1.md`, `config/politicas.yaml`,
`config/esquemas-evaluacion.yaml`, `calendarios/<ciclo>.yaml`.
