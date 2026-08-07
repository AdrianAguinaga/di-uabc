# Generador de Diseño Instruccional — UABC

Genera el **Diseño Instruccional (DI)** de una unidad de aprendizaje en `.docx` y `.pdf` a partir
de su **PUA** oficial, el **calendario escolar UABC** vigente, el profesor, la modalidad y los
grupos.

Rellena las **plantillas CIAD reales** (no las reconstruye), de modo que el formato institucional
se conserva intacto.

> **¿Montándolo en otra computadora?** Sigue **[INSTALACION.md](INSTALACION.md)** y termina con
> `python src/comprobar.py`, que revisa Python, los paquetes, `pdftotext`, Word y las plantillas,
> y dice exactamente qué falta.

Cada documento nace de una **copia fresca** de la plantilla: nunca se escribe sobre ella. El
`sha256` de las tres plantillas está registrado y se verifica antes de cada copia, así que generar
mil documentos las deja byte por byte idénticas. Si alguna cambiara sin pasar por el mecanismo de
actualización, el renderizado falla en vez de producir un documento de origen desconocido.

```
python src/plantillas.py verificar    # ¿siguen intactas?
python src/plantillas.py actualizar semipresencial <nueva.docx> --version 2026-1
```

La versión sustituida se archiva en `plantillas/historico/`, de modo que un DI generado hace un
año se puede reproducir con la plantilla que realmente se usó.

## Qué produce

Un documento por grupo, fusionando:

1. **Secciones 1–3 de la plantilla CIAD** — descripción general, plan de actividades y descripción
   de cada meta.
2. **Criterios de evaluación del curso** — con el umbral de exención del ordinario.
3. **Reglas de convivencia** — cada una con su sanción.
4. **Fundamento legal** — citas al Estatuto Escolar UABC (Arts. 66, 68, 70, 71) para que ningún
   alumno pueda alegar desconocimiento.
5. **Bloque de firma del jefe de grupo**.

## Uso

```
/di-pua puas/fuente/<archivo>.pdf   # ingiere un PUA nuevo → Markdown + índice
/di-nuevo                            # orquestador interactivo → genera el DI
/di-validar cursos/<ciclo>/<clave>   # valida un DI ya generado
```

El orquestador pregunta: **ciclo → materia → profesor → modalidad → grupos → esquema de evaluación**.
Si el PUA de la materia todavía no está en `puas/md/`, lo pide y ofrece ingerirlo en el momento.

### El grafo del dominio

```
python src/grafo.py     # → grafo/index.html, grafo.json y AUDITORIA.md
```

Recorre los PUAs y los cursos y arma el grafo de cómo se engancha todo: PUA, unidad, tema,
competencia, práctica, curso, meta, evidencia, criterio, semana, artículo, plantilla, profesor y
grupo. `grafo/index.html` se abre en el navegador y no depende de nada externo.

Contesta lo que ningún archivo por separado puede contestar: **qué temas del PUA quedaron sin
meta**, qué prácticas no las realiza ninguna meta, qué semanas están vacías y **qué materias
comparten competencias**. No infiere relaciones: cada arista sale de un campo declarado.

### Agenda de clases

```powershell
python src/exportar_ics.py 2026-2
# → horarios/salida/Clases-2026-2.ics
```

Exporta solo los **bloques de clase** de grupos que se imparten: no agrega entregas, exámenes,
tutorías ni actividades del DI. Respeta el inicio, fin y suspensiones del calendario oficial; cada
clase presencial lleva el aula y cada clase virtual queda marcada sin ubicación física. Una materia
sin `curso.yaml` queda fuera y un grupo sin bloques se omite con aviso, sin inventar horarios ni
impedir las otras clases.

Para importarlo, en Google Calendar abre **Configuración → Importar y exportar**, elige el archivo
`.ics`, selecciona el calendario de destino y pulsa **Importar**. Es una copia inicial: los cambios
posteriores en el repositorio no se sincronizan solos. Consulta la
[guía oficial de Google Calendar](https://support.google.com/calendar/answer/37118?hl=es).

### Esquemas de evaluación

Viven en `config/esquemas-evaluacion.yaml`. El orquestador ofrece el predeterminado y admite uno
capturado a mano; la validación exige, sea cual sea, que **sume exactamente 100** y que haya
**al menos dos parciales** (Art. 68).

| Esquema | Reparto |
|---|---|
| `estandar-2026` *(predeterminado)* | Exámenes 20 · Tareas y actividades 40 · Proyecto final 40 |
| `practica-laboratorio` | Parciales 20 · Prácticas 45 · Tareas 15 · Portafolio 20 |
| `pua-39062` | Parciales 20 · Tareas 10 · Prácticas 30 · Proyecto 40 |

El tercero sale de la sección VIII del PUA de Patrones de Comportamiento. Cuando el programa
oficial ya fijó los porcentajes conviene usarlos: frente a un alumno inconforme, lo que se
defiende es el PUA y no un catálogo interno.

### Cada docente, sus criterios

Los criterios de acreditación de `config/politicas.yaml` se filtran por `modalidades:`,
`solo_si_practica:` y **`profesores:`**. Sin filtro, el criterio aplica a todo el mundo; con
`profesores: [zra]`, solo a quien lo declara. **Añade, nunca reemplaza:** lo común —escala 0–100,
derechos a ordinario y extraordinario— lo conserva todo el mundo.

Así conviven en el mismo repositorio docentes con exigencias distintas. Hoy hay dos registrados,
con umbral de exención propio: 80 y 90. Al añadir criterios a alguien, **regenera los documentos
de los demás y compara el texto**: si cambia algo ajeno, falta el filtro.

## Estructura

| Directorio | Contenido |
|---|---|
| `referencias/` | Documentos fuente originales (plantillas CIAD, Estatuto, IEDI). **No se modifican.** |
| `ejemplos/` | DI reales ya elaborados, usados como referencia de calidad |
| `plantillas/` | Juego de trabajo con su `sha256` registrado, más las versiones sustituidas en `historico/` |
| `conocimiento/` | Banco de conocimientos: todo lo anterior convertido a Markdown para consulta |
| `puas/` | `fuente/` los PDF oficiales · `md/` normalizados · `INDICE.md` el registro |
| `calendarios/` | Calendarios escolares por ciclo + los PDF oficiales de origen |
| `horarios/` | Referencia del horario por ciclo + agenda `.ics` regenerable en `salida/` |
| `config/` | Profesores, esquemas de evaluación, políticas y mapa de plantillas |
| `src/` | Código Python del generador |
| `pruebas/` | Suite de pruebas — `python -X utf8 -m unittest discover -s pruebas` |
| `cursos/` | Salida: un directorio por ciclo y materia |
| `grafo/` | Grafo de conocimiento del dominio |
| `.planning/` | Artefactos GSD del propio proyecto |

## Convenciones

- **Ciclos**: `AAAA-2` = agosto–diciembre · `AAAA-1` = enero–junio.
- **Nombres de salida**: `DI-<ciclo>-<clave>-<grupo>.<ext>` — p. ej. `DI-2026-2-39056-961.docx`.
- La **clave del PUA** es el identificador primario en todo el sistema.

## Requisitos

Python **3.11 o mayor** · `python-docx` · `pdfplumber` · `PyYAML` · `openpyxl` · `pywin32` ·
`pdftotext` (viene en **Poppler**, es un programa aparte) · Microsoft Word, solo para exportar a
PDF por COM en Windows.

```powershell
python -m pip install -r requirements.txt
python src/comprobar.py                 # ¿está todo? dice qué falta
```

Sin Word se generan igual los `.docx`; lo único que se pierde es el `.pdf`. Sin `pdftotext` no se
puede ingerir un PUA. **Paso a paso en [INSTALACION.md](INSTALACION.md)**, incluido el registro de
Poppler en el PATH, que es lo que más suele fallar.

## Ciclo vigente

**2026-2** — clases del 10 de agosto al 28 de noviembre de 2026 (**16 semanas**).
Ver `calendarios/2026-2.yaml`.

Las plantillas CIAD semipresencial y a distancia traen 17 filas de semana; **para 2026-2 sobra
una**. El número de semanas lo manda el calendario oficial, no la plantilla: las fechas tienen
que sostenerse frente a un alumno.

## Cursos generados

| Ciclo | Clave | Materia | Grupos |
|---|---|---|---|
| 2026-2 | 39056 | Big Data | 961, 962 |
| 2026-2 | 39062 | Patrones de Comportamiento de Datos | 971, 972 |

Todo documento sale marcado como **borrador**: requiere la revisión del profesor antes de
entregarse a la facultad o publicarse a los alumnos (Art. 66 del Estatuto Escolar).
