# AGENTS.md — Contrato de agentes

Archivo **canónico** de instrucciones para cualquier agente que trabaje en este repositorio
(Claude Code, Codex, agy, Gemini CLI, OpenCode). `CLAUDE.md` es un puntero a este archivo.

---

## Qué es este proyecto

Genera el **Diseño Instruccional (DI)** de una unidad de aprendizaje de la UABC en `.docx` y `.pdf`,
a partir de su **PUA** oficial, el **calendario escolar** vigente, el profesor, la modalidad y los
grupos. Rellena las **plantillas CIAD reales**; no reconstruye documentos.

El destinatario final es un profesor que debe entregar el DI a su facultad y darlo a conocer a sus
alumnos el primer día de clase — obligación del **Art. 66 del Estatuto Escolar UABC**. Los errores
de fechas o de porcentajes tienen consecuencias reales frente a los alumnos.

---

## Reglas invariables

Estas reglas no se negocian. Un cambio que las viole está mal aunque los tests pasen.

1. **No inventes fechas.** Toda fecha del documento se deriva de `calendarios/<ciclo>.yaml`, que a
   su vez proviene del PDF oficial guardado en `calendarios/fuente/`. Si falta el calendario de un
   ciclo, pídelo — no lo estimes.
2. **No parafrasees el PUA §I ni §III.** Los datos de identificación y la competencia general se
   copian **literalmente**. Es una regla explícita del CIAD. Lo que sí puede adaptarse: estrategia
   de aprendizaje, evidencias y criterios de evaluación.
3. **No modifiques `referencias/` ni `ejemplos/`.** Son documentos fuente originales. Solo se leen.
   Sus versiones en Markdown viven en `conocimiento/`.
4. **Nunca escribas sobre una plantilla.** Cada documento nace de una **copia fresca** de
   `plantillas/<modalidad>.docx`, obtenida con `plantillas.copia_de_trabajo()`, que verifica el
   sha256 antes de copiar. Generar mil veces el mismo curso debe dejar la plantilla byte por byte
   idéntica. Si una plantilla cambia sin pasar por `src/plantillas.py actualizar`, el renderizado
   **falla**: un formato de origen desconocido no es aceptable en un documento con valor legal.
5. **Los porcentajes suman exactamente 100** y debe haber **≥ 2 exámenes parciales** (Art. 68).
6. **Ninguna entrega cae en día de suspensión** ni después del fin de cursos.
7. **Todo dato es trazable.** Cada DI generado lleva un `MANIFIESTO.yaml` —lo escribe
   `src/generar.py`— que registra el PUA y su hash, el calendario, la versión de plantilla, el
   profesor, el grupo, el esquema, el commit y el sha256 de cada archivo producido.
8. **La asistencia no es criterio de calificación**, pero **sí es requisito de derecho a examen**
   (Arts. 70 y 71). Nunca los mezcles en el documento.
9. **El generador no sustituye el criterio docente.** El resultado es un borrador que el profesor
   debe revisar. No lo presentes como definitivo.

---

## Reparto de trabajo entre modelos

| Etapa | Modelo | Qué hace |
|---|---|---|
| Análisis y planeación | **Opus** | Decide la arquitectura, redacta las metas de aprendizaje, mapea temas del PUA a semanas |
| Ejecución | **Sonnet** | Implementa lo ya decidido, escribe código, renderiza |
| Mapeo y verificación mecánica | Haiku | Checkers, auditorías estructuradas |

Configurado en `.planning/config.json` mediante el perfil GSD `adaptive`.

**El juicio pedagógico es de Opus y queda escrito en `curso.yaml`.** El renderizador es
determinista: toma `curso.yaml` y produce el documento sin inventar contenido. Si el renderizador
necesita "decidir" algo, es señal de que falta un campo en `curso.yaml`.

---

## Arquitectura

```
PUA (pdf) ──ingesta_pua.py──> puas/md/<clave>.md ─┐
                                                   ├─> curso.yaml ──render_docx.py──> .docx
calendarios/<ciclo>.yaml ──calendario.py──────────┤        │                              │
config/*.yaml ────────────────────────────────────┘        │                    export_pdf.py
                                                       validar.py                          │
                                                     (8 reglas)                          .pdf
```

`src/generar.py` encadena los tres últimos pasos —valida, renderiza un documento por grupo,
exporta a PDF— y cierra escribiendo `MANIFIESTO.yaml`. Si la validación falla, **no escribe nada**:
un DI con errores no debe llegar a existir en disco, porque en cuanto existe alguien lo entrega.
Es el único comando que necesita el orquestador `/di-nuevo`.

`curso.yaml` es **el contrato** entre la etapa de planeación y la de renderizado. Su esquema está
en `src/modelo.py`. Todo lo que aparece en el documento sale de ahí.

Cuatro decisiones de diseño que sostienen las reglas invariables:

1. **El horario vive en el grupo, no en el curso.** Si dos grupos tienen días de clase distintos,
   *todas* las fechas divergen. Cada entrada de `grupos:` lleva su `horario` (días de sesión, día
   y hora de entrega, aula) y su jefe de grupo; el motor de semanas corre una vez por grupo. Si
   los horarios coinciden, los documentos difieren en tres cadenas; si no, difieren en todas las
   fechas — y el sistema lo maneja igual.

2. **Opus nunca escribe fechas.** Escribe marcadores que `calendario.py` resuelve después de
   asignar las semanas: `{{fecha_presencial}}`, `{{fecha_entrega}}`, `{{fecha_entrega_larga}}`,
   `{{fecha_tabla}}`. Esto elimina de raíz la peor clase de error del sistema —una fecha inventada
   en un documento con valor legal— y hace trivial validarlo.

3. **El énfasis es semántico, no tipográfico.** En `curso.yaml` se escribe
   `{t: "M1.1_Mapa conceptual", enfasis: recurso}`, y el mapa a negrita/cursiva/subrayado vive
   **solo** en `src/estilo.py`. Si el CIAD cambia su guía de estilo se toca una tabla.

4. **El renderizado clona prototipos, no construye elementos.** Cada párrafo y cada fila que se
   añade es un `deepcopy` de uno que ya trae la plantilla, con el contenido cambiado. Así hereda
   sangría, espaciado, bordes y tipografía sin que el código tenga que conocerlos. Corolario: el
   prototipo tiene que ser el correcto — usar el párrafo «Versión» como molde centra todo el
   anexo, porque ese párrafo está centrado.

Además, cada meta declara `cubre_temas` y `practica_pua` referidos al PUA. Es el ancla
anti-alucinación: la validación rechaza referencias a temas o prácticas que no existen.

### Anatomía del documento generado

| Bloque | De dónde sale |
|---|---|
| Portada + Sección 1 | Plantilla CIAD; los campos se rellenan con `add_run()` sobre los runs que ya trae |
| Sección 2 (tabla) | Una fila separadora por unidad, dos subfilas por meta (presencial + virtual) |
| Sección 3 | Un bloque por meta, armado clonando prototipos, cerrado con `------------------------` |
| Criterios de evaluación del curso | `config/esquemas-evaluacion.yaml` + periodos de examen del calendario |
| Reglas de convivencia | `config/politicas.yaml`, cada regla con su sanción |
| Fundamento normativo | Los artículos de `citas:`, verbatim |
| `Versión <ciclo>.` + `Firma Jefe Grupo ____` | Uno por grupo |

Los últimos cuatro bloques **no vienen en la plantilla CIAD**: son la fusión que reproduce el
ejemplo 961. El pie de instrucciones del CIAD («Para descargar instrucciones de llenado…») se
**elimina**: es una nota para quien llena la plantilla, no parte del entregable.

### Contrato de `curso.yaml`

Las claves de primer nivel, tal como las lee `modelo.desde_dict()`:

```yaml
meta:            {ciclo, clave, pua_ref, pua_sha256}
profesor:        "ara"                      # id de config/profesores.yaml
identificacion:  {nombre, modalidad, practica, …}   # literal del PUA §I
contenido:       {competencia_general, proposito_general, estrategia_general,
                  evidencias_desempeno, criterios_evaluacion}
unidades:        [{numero, nombre, competencia, duracion_horas, temas}]
metas:           [{id, unidad, semanas, valor, rubro, tipo, enunciado,
                   sesiones, evidencias, criterios_evaluacion, reflexion,
                   cubre_temas, practica_pua, caracter, que_voy_a_aprender}]
evaluacion:      {esquema_id, exencion_ordinario, rubros:[{id, etiqueta,
                                                           porcentaje, detalle, parciales}]}
grupos:          [{numero, horario:{dias_presencial, dia_entrega, hora_entrega, aula},
                   jefe_grupo, plataforma}]     # o la forma corta: ["961", "962"]
citas:           [EE-65, EE-66, …]           # deben resolver en config/politicas.yaml
tolerancia_minutos: 15
avisos:          []                          # arrastrados desde la ingesta del PUA
```

`tipo` de meta: `encuadre · aprendizaje · examen_parcial · cierre`.
`ambiente` de sesión: `presencial · virtual`. Solo `encuadre` y `cierre` pueden valer 0 %.

### Las ocho reglas de validación (`src/validar.py`)

| # | Qué verifica | Fundamento |
|---|---|---|
| R1 | Los porcentajes del esquema suman exactamente 100; la exención cae en [60, 100]. | Arts. 65 y 67 |
| R2 | Las metas suman lo declarado **rubro por rubro**, no solo en total. | Art. 67 |
| R3 | Hay al menos dos exámenes parciales. | Art. 68 |
| R4 | Toda unidad del PUA tiene meta; ninguna meta cuelga de una unidad inexistente. | — |
| R5 | Toda semana 1..N tiene actividad; ninguna meta cae fuera del ciclo. | Calendario |
| R6 | Ninguna entrega cae en suspensión ni después del fin de cursos. | Calendario |
| R7 | Citas obligatorias presentes, cada regla de convivencia con sanción, firma por grupo. | Art. 66 |
| R8 | Indicadores indispensables del IEDI v2023-1 comprobables sobre el documento. | CIAD |

Tres niveles de hallazgo: **error** (bloquea), **aviso** (decisión del docente) y
**recordatorio** (indicador del IEDI que depende de Blackboard, no del documento).

**R2 es la regla que justifica la capa entera.** El ejemplo dorado `ejemplos/961 (1).pdf` suma
100 en total pero sus rubros no cuadran con su propio esquema declarado. Un validador que solo
revise el total deja pasar ese error; este lo atrapa, y hay una prueba dedicada a demostrarlo
(`test_detecta_el_defecto_del_ejemplo_961`).

### Custodia de las plantillas (`src/plantillas.py`)

Tres capas, cada una con un dueño distinto:

```
referencias/<lo que subió el usuario>   ← original intocable. Solo el usuario lo repone.
plantillas/<modalidad>.docx             ← juego de trabajo, con sha256 en REGISTRO.yaml
cursos/<…>/salida/DI-….docx             ← copia desechable, es la que se rellena
```

`plantillas/` y su `REGISTRO.yaml` **están versionados en git**: quien clone el repositorio
obtiene exactamente las plantillas con las que se generaron los documentos existentes.

| Necesitas… | Comando |
|---|---|
| Comprobar que nadie las tocó | `python src/plantillas.py verificar` |
| Recrear el juego desde `referencias/` | `python src/plantillas.py registrar` (idempotente) |
| Meter una versión nueva del CIAD | `python src/plantillas.py actualizar <modalidad> <ruta.docx> --version <ver>` |
| Copiar para rellenar (desde código) | `plantillas.copia_de_trabajo(modalidad, destino)` |

`actualizar` archiva la plantilla saliente en `plantillas/historico/<modalidad>-<ver>-<sha8>.docx`
y deja el rastro en `historial`, de modo que un DI generado hace un año se puede reproducir con la
plantilla que realmente se usó. **Después de actualizar, vuelve a verificar los hechos
estructurales de `config/plantillas.yaml`** (columnas de rejilla, filas de semana, pasos
ordinales): dejan de ser ciertos en silencio.

## Mapa de directorios

| Ruta | Qué es | ¿Se edita? |
|---|---|---|
| `referencias/` | Plantillas CIAD, Estatuto, IEDI — originales | **No** |
| `ejemplos/` | DI reales de referencia | **No** |
| `plantillas/` | Juego de trabajo con sha256 registrado | Solo vía `src/plantillas.py` |
| `plantillas/historico/` | Plantillas sustituidas, para reproducir DI viejos | Generado |
| `conocimiento/` | Los anteriores en Markdown, para consulta de agentes | Solo al reconvertir |
| `puas/fuente/` | PDFs de PUA que deja el usuario | Solo el usuario |
| `puas/md/` | PUAs normalizados | Generado |
| `puas/INDICE.md` | Registro de PUAs disponibles | Generado |
| `calendarios/` | Calendarios por ciclo + PDFs oficiales | Al abrir un ciclo nuevo |
| `config/` | Profesores, esquemas, políticas, plantillas | Sí |
| `src/` | Código del generador | Sí |
| `cursos/` | Salida por ciclo y materia | Generado |
| `grafo/` | Grafo de conocimiento | Generado |
| `.planning/` | Artefactos GSD | Vía comandos GSD |

## Comandos

```bash
python src/ingesta_pua.py puas/fuente/<archivo>.pdf   # PDF → puas/md/ + INDICE
python src/calendario.py 2026-2                        # imprime las semanas del ciclo
python src/validar.py cursos/2026-2/<clave>/curso.yaml # 8 reglas de validación
python src/render_docx.py cursos/2026-2/<clave>/curso.yaml
python src/export_pdf.py <archivo>.docx                # requiere Word (Windows)

python src/generar.py cursos/2026-2/<clave>/curso.yaml # la cadena completa, con panel
                                                       #   [--sin-pdf]     si no hay Word
                                                       #   [--grupo 961]   rehace un solo grupo

python src/plantillas.py verificar                     # ¿siguen intactas? (sha256)
python src/plantillas.py registrar                     # (re)crea el juego — idempotente
python src/plantillas.py actualizar <modalidad> <ruta.docx> --version <ver>
```

Skills equivalentes en Claude Code: `/di-pua`, `/di-nuevo`, `/di-validar`.

---

## Contexto de dominio imprescindible

### Ciclos escolares
`AAAA-2` = agosto–diciembre · `AAAA-1` = enero–junio.

**Ciclo vigente: 2026-2.** Clases del **10 de agosto al 28 de noviembre de 2026** = **16 semanas**.
Suspensiones: 16 sep, 2 nov, 16 nov. Ordinarios 30 nov – 8 dic; extraordinarios 14–17 dic.

Ojo: las plantillas CIAD traen 17 filas de semana (14 la presencial). **El número de semanas lo
manda el calendario, no la plantilla.** Para 2026-2 sobra un par de filas y debe eliminarse.

### Modalidades

| | Escolarizada | Semipresencial | A distancia |
|---|---|---|---|
| Plantilla | `CIAD_DI_Plantilla_PRESENCIAL.docx` | `..._Semipresencial-2025.docx` | `..._A_Distancia-2025.docx` |
| Columna `Entrega` | dividida Presencial/Virtual | dividida Presencial/Virtual | **sin dividir** |
| Sección 3 con pasos `Primero…Quinto` y `Reflexión` | no | sí | sí |
| Sección 2 en Blackboard | — | tabla o imagen | **archivo descargable** (Ultra no acepta tablas) |

### Estructura del PUA (secciones I–X)
`I. DATOS DE IDENTIFICACIÓN` (9 campos) · `II. PROPÓSITO` · `III. COMPETENCIA GENERAL` ·
`IV. EVIDENCIA(S) DE APRENDIZAJE` · `V. DESARROLLO POR UNIDADES` · `VI. ESTRUCTURA DE LAS PRÁCTICAS
DE LABORATORIO` · `VII. MÉTODO DE TRABAJO` · `VIII. CRITERIOS DE EVALUACIÓN` · `IX. REFERENCIAS` ·
`X. PERFIL DEL DOCENTE`.

Mapeo PUA → DI: §I → identificación · §III → competencia general · §II → propósito ·
§IV → evidencias de desempeño · §V → unidades y metas · §VIII → criterios de acreditación.

### Estilo de redacción CIAD
- Verbos en **imperativo informal**: *realiza, investiga, entrega, redacta, lee*.
- Actividades del **alumno** en presente o futuro; las del **docente** siempre en futuro.
- La reflexión *"¿cómo sabré que logré la meta?"* siempre en **pasado**: *Identifiqué…, Analicé…*
- Las metas empiezan con **verbo en infinitivo** (taxonomía de Bloom) y responden *qué* aprenderá
  el estudiante — nunca la actividad ni la evidencia.
- Tipografía: recursos en **negrita + cursiva**; tipo de evidencia en **negrita + subrayado**; la
  meta y su porcentaje en **negrita**.
- Nombres de recurso `M1.1_<Nombre>`; archivos que entrega el alumno `M1.1_Apellido_Nombre`.
- Valor de la meta: *«La meta 1.1 equivale al 5% de tu calificación final.»*

### Fundamento legal (Estatuto Escolar UABC, reforma 20 may 2021)

| Art. | Contenido |
|---|---|
| 65 | Escala 0–100; mínima aprobatoria **60** en licenciatura; nomenclaturas NP y SD |
| **66** | El profesor **debe** dar a conocer al inicio del curso el programa, la metodología y los criterios de evaluación |
| 67 | Los criterios deben definir aspectos y porcentajes, medios y momentos de evaluación |
| **68** | Evaluación permanente; **mínimo 2 exámenes parciales**; la exención del ordinario la decide el profesor; el alumno inconforme puede exigirlo |
| **70** | Derecho a ordinario con **≥ 80 % de asistencias** |
| **71** | Derecho a extraordinario con **≥ 60 % de asistencias** |
| 74 | Unidades predominantemente prácticas **no se evalúan en extraordinario** |
| 75 | Semipresencial y no presencial se rigen por el plan de clase aprobado |
| RPIDA 59 | Sanciones por plagio |

El umbral de exención de **80** es decisión del profesor amparada en el Art. 68. Los formatos
institucionales *recomiendan* 90 pero no lo imponen. Decláralo como criterio del docente, nunca
como norma universitaria.

---

## Notas técnicas

Todo lo de esta sección está **verificado contra los archivos reales**, no supuesto.

### Extracción
- `pdftotext` **requiere `-enc UTF-8`**; sin él produce mojibake (`AUT�NOMA`).
- La §VI del PUA (tabla de prácticas) se desordena con `pdftotext -layout` → usar
  `pdfplumber.extract_tables()`. La práctica 3 se parte entre las páginas 8 y 9: las filas de
  continuación llegan con el número vacío y hay que coserlas a la anterior.
- Los PUA oficiales traen **defectos de origen**. El de Big Data repite la numeración de temas en
  las cinco unidades y deja sin duración la práctica 3. **Se conservan literales y se avisa** —
  renumerar o rellenar rompería la trazabilidad contra el documento oficial.

### python-docx
- **Sección 1**: los campos vienen con los runs ya separados —
  `Clave:` es `[('Clave', bold=True), (': ', None)]`. Añade el valor con `add_run()`;
  **nunca** asignes `paragraph.text`, porque colapsa todos los runs y destruye el formato.
  Localiza los campos **por el texto de su etiqueta**, nunca por índice.
- **La plantilla tiene nombres de estilo duplicados**: `Heading 1`–`Heading 6`, `Title` y
  `Subtitle` aparecen **dos veces** en `doc.styles`. `doc.styles['Heading 2']` es ambiguo.
  **Prohibido asignar estilos por nombre**; los estilos se heredan clonando (`pPr/pStyle` viaja
  en el `deepcopy`).
- **Sección 2**: la tabla tiene **7 columnas de rejilla**, no las 6 lógicas del encabezado
  (`Semana` está fusionada horizontalmente). Mapa real:
  `0=Meta · 1=Semana · 2=modo · 3=Entrega · 4=Actividad · 5=Evidencia(s) · 6=Valor`.
  Opera sobre columnas de rejilla. Clona filas con `copy.deepcopy(tr._tr)`.
  - `tbl.tr_lst` reconsulta el XML en cada acceso: **haz snapshot con `list()`** antes de borrar,
    o al iterar y borrar a la vez te saltas filas.
  - Un `<w:tc>` **debe** terminar con al menos un `<w:p>`, o Word pide reparar el archivo.
  - `vMerge` va en una posición fija dentro de `<w:tcPr>` según el esquema: usa
    `get_or_add_vMerge()`, nunca `tcPr.append()`.
  - No toques `<w:tblGrid>`: con `tblLayout=fixed` los anchos salen de ahí.
- **Sección 3**: los dos bloques de meta de la plantilla **no son iguales**. El primero va de los
  párrafos 59 a 89 y termina en el separador `------------------------`; el segundo (90–130) trae
  un párrafo extra y **no** lleva separador. **Clona siempre el primero.**
- Al borrar contenido de un `<w:p>`, elimina **solo** los `qn('w:r')`. Un `<w:p>` también contiene
  `bookmarkStart/End`, `proofErr` e `hyperlink`; borrar un `bookmarkStart` sin su `End` hace que
  Word pida reparar el archivo.
- El espacio duro `\xa0` aparece literalmente en la plantilla (`'Primero.\xa0 '`). No lo
  normalices: cambia el renderizado.

### Word COM
- Usa **`DispatchEx`**, no `Dispatch`: `Dispatch` se adhiere a la instancia de Word que el usuario
  tenga abierta y `Quit()` le cerraría sus documentos.
- `Visible=False`, `DisplayAlerts=0`, rutas **absolutas**, y `try/finally` con `Quit()`.
- `word.Hwnd` vale 0 con `Visible=False`, así que no sirve para localizar el proceso. Para no dejar
  huérfanos: toma un snapshot de los PID de `WINWORD.EXE` antes de arrancar y mata solo el nuevo.
- Corre el export en un **subproceso con timeout**: un Word colgado en un diálogo invisible no debe
  poder trabar el pipeline.
- Requisito previo: Word debe haberse abierto interactivamente al menos una vez, o el diálogo de
  primera ejecución cuelga COM indefinidamente.

### Erratas conocidas de los documentos institucionales
- La plantilla **presencial** dice `Diseño Instruccional para la modalidad semipresencial:` aun
  siendo la escolarizada. Se reproduce corregido; queda constancia en `conocimiento/plantillas/`.
- La plantilla presencial trae una fila 33 huérfana (`vMerge=continue`, vacía). No la uses como
  prototipo.
- La rúbrica IEDI repite el id `4.6` dos veces.
- **El ejemplo 961 es oráculo de formato, no de contenido.** Tiene dos defectos reales: la semana 7
  no lleva meta ni número de semana, y los porcentajes por rubro no cuadran con su propio esquema
  declarado (Proyecto 22 % contra 40 % declarado, Tareas 58 % contra 40 %), aunque el total sí sume
  100. La capa de validación debe **detectar** esos dos defectos: es la prueba de que sirve.

## Git

Repositorio **local únicamente**. No hay remoto y **no se hace push** sin autorización explícita
del usuario. Commits atómicos: uno por PUA ingerido, uno por fase GSD.
