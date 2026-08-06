# Estado del proyecto

**Proyecto**: Generador de Diseño Instruccional UABC (`DI-UABC`)
**Última actualización**: 2026-08-05 (planes de la Fase 10)
**Milestone actual**: **v2.0 — Estructura de calificación variable**
**Fase actual**: Fase 10 — Las reglas cuentan en la unidad declarada (planeada, lista para ejecutar)

## Posición actual

| | |
|---|---|
| Milestone | v2.0 Estructura de calificación variable |
| Fase | 10 — Las reglas cuentan en la unidad declarada |
| Plan | 4 planes en 4 olas, verificados |
| Estado | Fase 9 hecha y verificada; la 10 planeada y lista para ejecutar |
| Última actividad | 2026-08-05 — cuatro planes para la Fase 10 (`d8b4a4c`), verificación en verde |

Se sigue con `/gsd-execute-phase 10`. **El contexto de la Fase 10 ensanchó su alcance respecto al
roadmap, y está razonado en `10-CONTEXT.md`.** El enunciado que gobierna la fase es «toda regla lee
todo aporte a un rubro, en la unidad que ese rubro declara», no «R2 en puntos y R3 con los exámenes
del 531». El motivo se midió: `componentes:` está en el contrato desde la Fase 9 pero **ninguna
regla lo lee** —fuera del modelo solo aparece en `render_docx.py:274`—, así que R2 está mal en
general, no solo para el 531, y los criterios del roadmap solo mencionan componentes para R3.

Tres decisiones de la Fase 10 salieron de medir, no de suponer: convertir aporte a aporte da
`29.99999999999999` sobre 150 pts exactos con 22 metas (se convierte una vez por rubro, D-06); los
cuatro documentos de control validan limpios y **no emiten ni un hallazgo de R2 o R3**, así que la
redacción de sus mensajes es libre y lo que REQ-48 exige es su silencio (D-15); y
`test_el_total_correcto_no_absuelve_al_rubro_incorrecto` se vuelve tautológica si el mensaje global
se reformula (D-07, restricción para el planeador).

En la Fase 9, tres decisiones se apartaron de cómo el roadmap describió la
fase y están razonadas en `09-CONTEXT.md`: la evidencia de un componente toca `render_docx.py`
(D-11); el encuadre de Big Data se renombra de verdad, gastando la primera excepción a REQ-48
(D-14) —con el orden de pasos fijado en D-15/D-24 para que el instrumento demuestre algo antes de
que se le pida esa excepción—; y la forma del `MANIFIESTO.yaml` acabó entrando en la huella (D-27),
que D-19 había dejado fuera.

Las cinco olas no son fruto de optimizar paralelismo: las fija D-15 de la Fase 9. `src/huella.py` y su línea
base van primero, antes de que nada toque el modelo; el renombrado de Big Data es lo último.

**09-01 (paso 1 de D-15) quedó hecho el 5 de agosto de 2026.** `src/huella.py` compara tres hashes
por documento —texto del `.docx`, informe de validación y forma del `MANIFIESTO.yaml` (D-27)— y
`pruebas/huellas.yaml` ya guarda la línea base de los cuatro documentos de control (39056/961,
39056/962, 39062/971, 39062/972), tomada antes de que ningún plan posterior toque `src/modelo.py`.
`huella verificar` corre en verde y deja `cursos/` sin cambios (D-23/D-28: no invoca git, restaura
los bytes que leyó). Detalle en `09-01-SUMMARY.md`.

**La ola 2 —09-02 y 09-03— quedó hecha el 5 de agosto de 2026, en paralelo.** El contrato
`curso.yaml` ya sabe decir «10 pts de 150»: `Rubro` acepta `unidad`, `total` y `base`, y convierte a
porcentaje cuando alguien se lo pide; `Meta` acepta `componentes` con su tipo y su evidencia; y los
identificadores de meta quedaron libres. `src/modelo.py` se extendió, nunca se reemplazó, y
`pruebas/test_modelo.py` nace con 18 pruebas que hasta ahora vivían implícitas dentro de
`test_validar.py`. En el otro frente, R2 gana tres líneas que denuncian dos metas con el mismo id
—el hueco que abrían los ids libres, y que habría hecho que `src/grafo.py` pisara un nodo con
otro—. La aritmética de R1 y R2 no se tocó: contar en la unidad declarada es la Fase 10.

212 pruebas en verde después del merge de los dos worktrees.

**09-04 (ola 3) quedó hecho el 5 de agosto de 2026.** El desvío deliberado D-11 ya está construido:
`_evidencias(meta)` concatena las evidencias de una meta con las de sus componentes, y la celda de
evidencias de la Sección 2 la usa en vez de leer `meta.evidencias` directamente. Los dos puntos que
imprimen `f"{meta.valor:g}%"` —columna Valor y Sección 3— quedaron intactos, confirmados línea a
línea contra el diff: son de la Fase 13. `huella verificar` (de solo lectura) confirma que los
cuatro documentos de control siguen con huella intacta, porque ninguno declara `componentes:` —
REQ-48 sostenido sin gastar la excepción que corresponde a 09-05.

216 pruebas en verde.

**09-05 (ola 4) quedó hecho el 5 de agosto de 2026.** La secuencia de D-15/D-24 corrió en su orden:
`huella verificar` en verde tras abrir el contrato (el rasgo nuevo no se activa si el `curso.yaml` no
lo declara), renombrado del encuadre de Big Data de `0` a `1.0` en una sola línea, `src/grafo.py`
regenerado con **la misma forma —377 nodos, 669 aristas—**, `huella verificar` señalando solo 39056 y
dejando 39062 intacto, y `huella registrar` aceptando el cambio.

**Criterio 3 demostrado con medición, no con inspección**: revirtiendo en el texto del `.docx` las
apariciones del identificador, el sha coincide **exacto** con la línea base previa al renombrado, en
961 y en 962. Ninguna función de `src/` deducía el encuadre por su id. Un matiz que el plan no
preveía: el id aparece en **tres** cadenas, no en una —«Meta 1.0.» en la Sección 2, «Meta 1.0.» en la
Sección 3 y «La meta 1.0 equivale al 0%…» en la línea de valor—. Las tres son el identificador
impreso; no hay ninguna otra diferencia.

Dos cosas quedaron anotadas para el cierre de la fase: el recurso `M0_Foro de presentación` sigue
llamándose `M0_` con su meta ya en `1.0` (deliberado, D-14, a acordar con el docente), y
`huella registrar` genera con `pdf=False`, así que los `MANIFIESTO.yaml` **dejaron de listar los
`.pdf`** y los PDFs de 39056 que hay en disco son anteriores al renombrado.

## Progreso de la v2.0

| Fase | Requisitos | Estado |
|---|---|---|
| 9. El valor de una meta deja de ser un porcentaje | REQ-38, REQ-39, REQ-42 | **Hecha** — 6/6 planes, verificada |
| 10. Las reglas cuentan en la unidad declarada | REQ-40, REQ-45 | **Planeada** — 4 planes en 4 olas |
| 11. El segundo nivel de la calificación | REQ-41, REQ-46 | Sin empezar |
| 12. La rúbrica en el contrato | REQ-43, REQ-47 | Sin empezar |
| 13. El documento en la unidad real | REQ-44 | Sin empezar |
| 14. 38985 sin traducirse | REQ-49 | Sin empezar |

El orden es el de la v1.0 y por la misma razón: **modelo → validación → renderizado → ejercicio
real**. `curso.yaml` es el contrato; si el renderizador tuviera que decidir algo, faltaría un campo
en el modelo.

**REQ-48 —la no contaminación— no es una fase, es el criterio de cierre de las seis.** Al terminar
cada una se regeneran 39056 y 39062 y se comprueba que su huella de texto no cambió. El comando que
lo comprueba se construye en la Fase 9. Las 179 pruebas actuales pasan al final de cada fase:
ninguna se rompe, se añaden.

La **v1.0 quedó cerrada** con sus 8 fases hechas y tres materias generadas de extremo a extremo.
Todo lo que sigue es su registro, que se conserva como contexto acumulado.

---

## Progreso de la v1.0

| Fase | Estado | Commit |
|---|---|---|
| 1. Cimientos y normalización | Hecha | `3ab58e1` |
| 2. Banco de conocimientos | Hecha | `66ffee4` |
| 3. Motor de calendario | Hecha | `4e02016` |
| 4. Ingesta de PUA | Hecha | `4385ea3` |
| 5. Modelo y validación | Hecha | `0e30def` |
| 6. Renderizado docx + pdf | Hecha | `745f20e` |
| 7. Orquestador | Hecha | `cb903c5` |
| 8. Grafo de conocimiento | Hecha | `ca6efd4` |

171 pruebas, todas pasan: `python -X utf8 -m unittest discover -s pruebas`.

Fase 7: `/di-nuevo` (menú de seis pasos con su panel ASCII) y `src/generar.py`, que valida →
renderiza por grupo → exporta a PDF → escribe `MANIFIESTO.yaml`. Corrido de extremo a extremo
sobre Big Data 2026-2.

Fase 8: `src/grafo.py` → `grafo/grafo.json`, `grafo/index.html` y `grafo/AUDITORIA.md`.
290 nodos y 542 aristas con dos PUAs y dos cursos. La auditoría cierra en **0 huecos y 0 anclas
rotas**.

Con dos materias en el grafo, la segunda pregunta de REQ-31 —qué materias comparten
competencias— ya tiene con qué contrastar y responde «nada»: Big Data y Patrones declaran
competencias distintas. Es la respuesta correcta. La comparación es por texto literal
normalizado, nunca por parecido semántico, así que solo se enciende cuando alguien copió y
pegó una competencia entre programas, que es justo para lo que se hizo.

## Cierre de la cobertura temática (4 de agosto de 2026)

La auditoría de la Fase 8 destapó 41 temas y 1 práctica sin meta. No era un fallo del grafo: el
`curso.yaml` solo declaraba `temas` en la unidad I —el grafo los leía del PUA— y casi ninguna meta
declaraba `cubre_temas`. Se cerró así:

- Las unidades II–V ya traen sus `temas` copiados literales del PUA §V, con sus defectos de
  numeración de origen (la unidad IV repite el `4.6.`).
- Las 16 metas declaran `cubre_temas`; los 52 temas quedan cubiertos.
- La **Práctica 3** —la única del PUA sin horas asignadas— se ejerce en la meta 2.3, sobre las
  fuentes de datos del caso de estudio. Decisión del profesor, 4 de agosto de 2026.

Ni `temas` ni `cubre_temas` ni `practica_pua` llegan al documento: el renderizador solo lee
`numero`, `nombre` y `competencia` de cada unidad. La cobertura es materia de validación y grafo,
no del entregable. Aun así se regeneró el DI para que el `sha256` del `MANIFIESTO.yaml` vuelva a
corresponder al `curso.yaml` (regla invariable 7).

## Materia nueva, ejercida de extremo a extremo (4 de agosto de 2026)

Era lo último que quedaba abierto. Se corrió con **Patrones de Comportamiento de Datos**
(clave 39062, etapa terminal, HC:2 HL:2), desde el PDF hasta el `.pdf` firmable:

1. Ingesta: 10 secciones completas, 5 unidades, 9 prácticas. La §VI —la frágil— salió íntegra;
   sus duraciones suman 32 h, que es HL:2 por 16 semanas, y cuadra con el propio encabezado.
2. Esquema de evaluación **`pua-39062`** nuevo en `config/esquemas-evaluacion.yaml`: 20/10/30/40.
   Lo dicta la §VIII del programa; frente a un alumno inconforme la defensa es el PUA, no el
   catálogo interno del proyecto.
3. `curso.yaml` desde cero: 16 metas sobre 16 semanas, los 36 temas cubiertos, las 9 prácticas
   ancladas. **Validó a la primera**, sin un solo error.
4. Documento generado y exportado a PDF. Tabla de 39 filas × 7 columnas, 16 semanas distintas.

**El grupo quedó como marcador** (`POR-DEFINIR`): número, aula y día presencial hay que
capturarlos antes de entregar nada. El propio `curso.yaml` lo declara en `avisos:` y la
validación lo repite en cada corrida.

Dos defectos reales que solo aparecieron al usar un PUA distinto del de Big Data:

- **El detector de numeración repetida truncaba a dos niveles**, así que `1.2.1` se denunciaba
  como duplicado de su padre `1.2`. Cuatro avisos falsos aquí y tres en Big Data, que llevaban
  ahí desde la Fase 4 sin que nadie los mirara. Arreglado en `109c1d5`.
- **El panel de `/di-nuevo` pegaba la etiqueta al detalle** cuando el grupo pasaba de 15
  caracteres. Cosmético, arreglado.

## Falla metodológica corregida (4 de agosto de 2026)

Al asignar la Práctica 3 a la meta 2.3 de Big Data quedó declarada en el modelo pero **ausente
del documento**: ninguna sesión la instruía. Se evaluaba algo que al alumno nunca se le pedía.
Corregido: la sesión presencial de la semana 6 es ahora «Práctica 3: analítica de datos en tiempo
real», la virtual pide su reporte, y el reporte es evidencia junto al protocolo.

El barrido que lo encontró también revisó las otras metas con práctica. Las de Big Data 3.3, 4.3
y 5.1 sí la instruyen —lo hacen desde `actividad_tabla`, no desde los pasos— y las nueve de
Patrones también. No queda ninguna práctica declarada sin instruir en los dos cursos.

## Hallazgo abierto: la unidad V va comprimida en los dos cursos

Contrastando las horas que el PUA asigna a cada unidad contra las semanas que el DI le da:

| Curso | Unidad V | Semanas esperadas | Asignadas |
|---|---|---|---|
| Big Data | 4 h de 20 · 10 temas | 3.2 | **2** (15, 16) |
| Patrones | 6 h de 32 · 11 temas | 3.0 | **2** (15, 16) |

En ambos, las unidades II y IV salen infladas porque el parcial se contabiliza contra la unidad
que evalúa, y la V —que es donde cae el proyecto final— se queda con dos semanas. Puede ser
deliberado: la unidad V es sobre todo integración y presentación. **No se tocó**: rebalancear
mueve el calendario de documentos ya generados y es decisión del profesor, no del generador.

## Jerga interna impresa en el documento (4 de agosto de 2026)

El usuario detectó `§` en el documento de 39062. No era codificación: era la taquigrafía que
`AGENTS.md` usa para mapear secciones del PUA (`§I`, `§VI`) escrita dentro de un campo que **sí
se imprime** — `detalle: "nueve prácticas conforme a la §VI del PUA"`. Big Data tenía cero
ocurrencias; la fuga se introdujo al registrar el esquema `pua-39062`.

Barrido completo de los dos documentos, carácter por carácter. Todo lo demás está justificado:

| Carácter | Origen | Veredicto |
|---|---|---|
| `_` × 98/93 | nombres de recurso `M2.1_…` | convención CIAD |
| `►` × 68 | viñetas de la plantilla | plantilla |
| `\|` × 32 | encabezados «Actividad \| ¿Cómo lo voy a aprender?» | plantilla |
| `«»` × 2 | cita literal del Artículo 65 | Estatuto |
| `§` × 2 | **jerga propia** | corregido |

Para evitar que vuelva: `Validador.estilo` barre todo el texto imprimible y avisa bajo la
etiqueta `ESTILO`. Cuatro pruebas nuevas (175 en total). Documentado en `AGENTS.md`.

## Grupos de 39062

**971 y 972**, presencial martes y jueves. Los dos documentos difieren solo en «Grupo 971/972»
y en las fechas, que es lo que exige REQ-14. Ninguna de las tres suspensiones del ciclo cae en
martes ni en jueves.

## Criterios de Zurisaddai Rubio Arriaga (4 de agosto de 2026)

Fuente: su propio DI, `ejemplos/38985-531-2026-1-Rubio Arriaga Zurisaddai.docx` —Contabilidad
Financiera 38985, grupo 531, ciclo 2026-1, semipresencial. Solo lectura; `ejemplos/` no se toca.

Hasta ahora todo el sistema codificaba los criterios de Adrian. Ya no: `config/politicas.yaml`
acepta el filtro **`profesores:`**, hermano de los `modalidades:` y `solo_si_practica:` que ya
existían. Sin filtro el criterio es de todos; con él, solo de quien lo declara. **Añade, nunca
reemplaza.**

Registrado de `zra`:

| Dato | Valor |
|---|---|
| Correo | `rubio.zurisaddai@uabc.edu.mx` (llevaba `null` desde la Fase 5) |
| Firma | «Dra. Zurisaddai Rubio Arriaga», con título |
| Exención | **90**, no 80 |
| Coordinadora de área | Dra. Bianca Janeth López Campillo |

Y seis criterios propios: trabajo final como requisito de acreditación (sin él, máximo 50);
entrega solo por plataforma, nunca por correo; sello del docente en las tareas presenciales;
95 % de tareas cubiertas para exentar; trabajo final nuevo para el extraordinario; y el código
de ética con sus once valores.

Ese último aparece en su DI rotulado «Nota inamovible». Se buscó en las cuatro plantillas CIAD,
en las instrucciones de llenado y en las políticas de curso 2025: **no está en ninguna**. Es
aportación suya, así que se registró como criterio propio y no como obligatorio.

Verificado que no contamina: se regeneraron Big Data y Patrones y **la huella del texto no
cambió**. Cuatro pruebas nuevas lo fijan (179 en total).

## Reconstrucción del curso de Zurisaddai (4 de agosto de 2026)

`cursos/2026-2/38985-contabilidad-financiera/` — su DI pasado por el generador, para ver cómo
queda. **Validó a la primera**, y con sus criterios impresos: exención en 90, trabajo final como
requisito, sello en presenciales, 95 % de tareas, código de ética y firma con título. Los
documentos de Adrian se regeneraron y su huella de texto no cambió.

Lo que se apartó del original, declarado en `avisos:` del propio `curso.yaml`:

| Cambio | Razón |
|---|---|
| Ciclo 2026-2, no 2026-1 | Solo existe `calendarios/2026-2.yaml`; el suyo ya pasó |
| Los tres exámenes son metas propias | En su DI van dentro de la actividad; así, R3 contaría cero y no validaría |
| Valores en porcentaje, no en puntos | Su rubro declara 150 pts y solo hay 140. No se reproduce el defecto |

La auditoría del grafo reporta **un hueco: «Contabilidad Financiera · 2026-2»** en cursos cuyo PUA
no está ingerido. Es correcto —falta el PUA 38985— y desaparece en cuanto se ingiera.

Antes de esto se escribió `conocimiento/ejemplos/531-contabilidad-financiera-2026-1.md`, el espejo
en Markdown de su documento. El banco de conocimientos existe para no abrir binarios y yo llevaba
tres turnos leyendo el `.docx` con `python-docx` en cada consulta.

## Lo de Zurisaddai que NO cabe en el modelo actual

Su DI usa una estructura de calificación distinta de la de Adrian. Esto **no** se construyó:
sin un curso suyo que generar sería especulación, y toca el renderizador.

| Su estructura | Qué asume el modelo hoy |
|---|---|
| Promedio 60 % + examen ordinario 40 % | Los rubros suman 100; no existe ese segundo nivel |
| Metas en **puntos** (`10 pts`) | `valor` es porcentaje |
| Metas `1.0`, `2.0`… (cada unidad abre en `.0`) | `0` de encuadre y luego `1.1`, `1.2` |
| **Tres** exámenes dentro de la actividad de una meta | R3 cuenta metas de tipo `examen_parcial`; así contaría cero y fallaría |
| Rúbrica del trabajo final, tabla de 100 puntos | No hay tabla de rúbrica |

El cuarto punto es el que muerde: un DI suyo redactado a su estilo **no pasaría la validación**.

## Instalación en otra máquina (4 de agosto de 2026)

El proyecto se va a copiar a la computadora de Zurisaddai, así que se documentó el montaje:

- **`INSTALACION.md`** — paso a paso para Windows. El punto que más falla es Poppler: `pdftotext`
  no viene con Python, hay que registrar su carpeta `Library\bin` en el PATH y abrir una terminal
  nueva. También cubre qué hacer sin Word y qué NO tocar (`referencias/`, `ejemplos/`).
- **`src/comprobar.py`** — revisa Python, los cinco paquetes, `pdftotext`, Word, los archivos de
  configuración y la integridad de las plantillas. Sale con código 1 si falta algo indispensable.
- **`README.md`** — actualizado: los tres esquemas de evaluación, el filtro `profesores:`, los
  requisitos reales y los cursos ya generados.
- Sin Poppler, la ingesta reventaba con un `WinError 2` que no decía qué faltaba. Ahora explica
  qué instalar y remite a `INSTALACION.md`.

`pandoc` figuraba en REQ-32 como parte del toolchain, pero **no se usa en ningún punto del
código**. No se listó como requisito.

## Lo que queda abierto

**Decidido el 4 de agosto de 2026**: se construye la estructura completa de la tabla de arriba —no
solo el 60/40 y la rúbrica—, en el **milestone v2.0**. Los cinco rasgos están entrelazados: si las
metas valen puntos, el segundo nivel tiene que saber convertirlos, y mientras R3 solo cuente metas
de tipo `examen_parcial`, un DI suyo redactado a su estilo sigue sin validar.

Sigue abierto, y no es del roadmap:

- **El PDF del PUA 38985 no está en `puas/fuente/`.** Sin él las unidades de Contabilidad van sin
  temas, el manifiesto queda sin hash de PUA y la auditoría del grafo reporta el hueco
  «Contabilidad Financiera · 2026-2» — correctamente. No bloquea la v2.0: el `curso.yaml` de 38985
  ya existe.
- **Las metas 2.1 a 6.0 de Contabilidad las redactó el agente**, a partir de los títulos y
  actividades de la tabla de su DI, porque su Sección 3 no las detalla todas con el nivel de la
  1.1. El contenido es plausible para Contabilidad **pero no es de ella**: tiene que revisarlas
  antes de usarlas. Está declarado en `avisos:` del `curso.yaml`.
- Si la unidad V se rebalancea o los dos cursos de Adrian se quedan como están.
- Confirmar con Zurisaddai que sus criterios se registraron bien: se dedujeron de un DI de
  Contabilidad, y puede que algunos sean de esa materia y no suyos en general.

## Repositorio

Remoto: **https://github.com/AdrianAguinaga/di-uabc**, rama `master`, **público** desde el
3 de agosto de 2026 por decisión del usuario. El push se hace solo a petición explícita.

## Decisiones tomadas

| Fecha | Decisión | Razón |
|---|---|---|
| 2026-08-03 | **16 semanas reales** para 2026-2, no las 17 de la plantilla | El calendario oficial fija clases del 10 ago al 28 nov 2026. Las fechas deben ser defendibles frente a los alumnos. |
| 2026-08-03 | **Documento fusionado**, como el ejemplo 961 | Es lo que el profesor ya produce a mano: CIAD + políticas + reglas + firma en un solo entregable. |
| 2026-08-03 | Soportar **las tres modalidades** desde el inicio | Las tres plantillas ya están disponibles y los deltas entre ellas están mapeados. |
| 2026-08-03 | **Git local únicamente** | Los PUAs y los datos de los profesores no salen de esta máquina sin autorización. |
| 2026-08-03 | Perfil GSD **`adaptive`** | Opus planifica y redacta las metas; Sonnet ejecuta; Haiku verifica. Es el reparto que pidió el usuario. |
| 2026-08-03 | **`AGENTS.md` canónico**, `CLAUDE.md` como puntero | Interoperar con Codex y agy sin duplicar contenido. |
| 2026-08-03 | Rellenar las plantillas reales con `python-docx`, no reconstruirlas | Conservar el formato institucional es requisito duro. |
| 2026-08-03 | PDF vía **Word COM** | Word 16.0 ya está instalado; máxima fidelidad y cero dependencias nuevas. |

## Hallazgos que condicionan el diseño

1. **El ciclo 2026-2 tiene 16 semanas, no 17.** 10 ago (lunes) – 28 nov (sábado) 2026. Las
   plantillas CIAD semipresencial y a distancia traen 17 filas de semana; sobra un par y debe
   eliminarse, no rellenarse.
2. **La tabla de la Sección 2 tiene 7 columnas de rejilla, no 6.** El encabezado `Semana` está
   fusionado horizontalmente. Mapa real:
   `0=Meta · 1=Semana · 2=modo · 3=Entrega · 4=Actividad · 5=Evidencia(s) · 6=Valor`.
3. **Los runs de la Sección 1 vienen ya separados** —`Clave:` es `[('Clave', bold), (': ', None)]`—
   así que basta `add_run()`. Asignar `paragraph.text` destruiría el formato.
4. **La plantilla presencial trae un error de origen**: dice `Diseño Instruccional para la modalidad
   semipresencial:` aun siendo la escolarizada.
5. **La §VI del PUA se desordena** con `pdftotext -layout`; requiere `pdfplumber`.
6. **`pdftotext` necesita `-enc UTF-8`**, si no produce mojibake.
7. **El ejemplo 961 es oráculo de formato, no de contenido.** Sus porcentajes por rubro no cuadran
   con el esquema que él mismo declara (Exámenes 20 ✓, pero Proyecto queda en 2 % o 22 % según
   dónde se impute el portafolio, contra 40 % declarado), aunque el total sí sume 100. Además, las
   metas divergen en redacción entre la Sección 2 y la Sección 3. De ahí que cada meta declare su
   `rubro` y que su enunciado se escriba una sola vez.
8. **De los 12 indicadores indispensables del IEDI, solo siete son comprobables sobre el
   documento**; los otros cinco (2.4, 3.1, 3.2, 3.5, 4.1) dependen de cómo el docente monte el
   curso en Blackboard. Se reportan como recordatorio, no como verificados.
9. **El `curso.yaml` de Big Data solo copió los temas de la Unidad I.** Lo destapó el grafo en la
   Fase 8: de los 52 temas del PUA, 41 no tienen ninguna meta que los cubra, y las unidades II–V
   traen `temas: []`. La validación no podía verlo —R4 compara `cubre_temas` contra los temas que
   el propio `curso.yaml` declara, así que una lista vacía pasa en silencio—. Es el hueco que
   justifica que el grafo lea el PUA y no solo el curso. **Pendiente de decidir con el docente**:
   completar los temas y repartirlos entre las metas existentes.

## Riesgos abiertos

| Riesgo | Mitigación |
|---|---|
| Clonar XML con `deepcopy` es frágil | La Fase 6 se valida contra el ejemplo 961 antes de seguir |
| Word COM es Windows-only y deja procesos huérfanos | `try/finally` con `Quit()`; LibreOffice como ruta alterna si hiciera falta |
| La calidad pedagógica de las metas no es automatizable | El resultado es un borrador; requiere revisión del profesor |

## Pendiente de confirmar con el usuario

- `~/.gsd/defaults.json` tiene `resolve_model_ids: "omit"`, lo que impediría que GSD asigne modelos
  por agente y anularía el reparto Opus/Sonnet. Es configuración **global**, fuera de este
  proyecto; no se ha tocado.

## Siguiente paso

`/gsd-execute-phase 10` — cuatro planes en cuatro olas, commit `d8b4a4c`, verificación en verde.

| Ola | Plan | Qué construye | Archivos |
|---|---|---|---|
| 1 | 10-01 | `Aporte` y `Curso.aportes()`: la única definición de «lo que cuenta para un rubro» | `modelo.py`, `test_modelo.py` |
| 2 | 10-02 | R2 cuenta todo aporte contra `Rubro.base`; global convertido una vez por rubro; componente mal declarado | `validar.py`, `test_validar.py`, `AGENTS.md` |
| 3 | 10-03 | R3 cuenta aportes `examen_parcial` se declaren donde se declaren; aviso de `parciales:` reformulado | íd. |
| 4 | 10-04 | R1 fijada con pruebas, no contaminación en el ciclo rápido, criterio 1 por CLI, huella a mano | `test_validar.py` |

**Las olas van en serie a propósito, no por falta de paralelismo.** 10-02, 10-03 y 10-04 tocan los
mismos tres archivos; forzarlos a la misma ola produciría conflictos en `regla_2`/`regla_3` y en la
tabla de `AGENTS.md`. Es lo contrario de la Fase 9, donde la serialización venía de D-15.

**La auditoría de R1 quedó resuelta, no levantada.** El planeador leyó `validar.py:126-169` línea a
línea: las cuatro comprobaciones son la suma de `r.porcentaje` contra `suma_exacta`, los ids de rubro
duplicados, `exencion_ordinario` contra su intervalo y el contraste contra el catálogo de esquemas.
Ninguna lee `Meta.valor`, `Rubro.unidad`, `Rubro.total`, `Rubro.base` ni `a_porcentaje`. Confirma la
conclusión provisional del `<code_context>`: **R1 no necesita cambio**. Se fija con cuatro pruebas en
10-04, una de las cuales lee la fuente de `regla_1` con `inspect.getsource` y falla si alguien mete
ahí un término sensible a la unidad. Detalle: `regla_1` tiene una variable local `total`, así que los
términos se buscan con punto delante.

**D-07 se cumple sin tocar la prueba.** El mensaje global conserva el prefijo literal `El valor de las
metas suma` y solo añade ` %` detrás de las cifras, ahora convertidas. Así
`test_el_total_correcto_no_absuelve_al_rubro_incorrecto` sigue probando lo que dice en vez de quedar
pasando en vacío. Está fijado con `grep -c` como criterio de aceptación en 10-02.

**Hueco documental que dejó la Fase 9, deliberadamente fuera de estos planes:** `AGENTS.md`
§«Contrato de `curso.yaml`» (líneas 146-163) todavía no lista `componentes:` en las metas ni
`unidad`/`total` en los rubros, aunque la Fase 9 los añadió al modelo. El contexto de la Fase 10 solo
obliga a actualizar §«Las ocho reglas», así que no se metió en ningún plan sin consultarlo. Candidato
para el cierre de la fase o para la 12, que sí toca el contrato.

Se saltaron a propósito la investigación y el VALIDATION.md de Nyquist: el `10-CONTEXT.md` ya traía
los puntos de integración con número de línea, las mediciones y la línea base de la huella. La
estrategia de validación son los cinco criterios del roadmap más las pruebas unitarias.

Nota de herramienta: `gsd-sdk query init.phase-op` devuelve `phase_found: false` para las fases de
este milestone. Su parser busca `### Phase N` en inglés y el roadmap dice `### Fase N`. Las rutas se
resuelven a mano; volverá a pasar en las Fases 11 a 14.

Dos pendientes que dejó la Fase 9, ninguno bloqueante:

- El recurso `M0_Foro de presentación` de Big Data conserva el prefijo viejo con su meta ya
  renombrada a `1.0`. Fue deliberado (D-14) para no contaminar la medición del criterio 3, que ya
  está hecha. Queda por acordar con el docente.
- `huella registrar` genera con `pdf=False`, así que los `MANIFIESTO.yaml` de los dos cursos de
  control **dejaron de listar los `.pdf`**, y los PDFs de 39056 que hay en disco son anteriores al
  renombrado: todavía dicen «Meta 0.». Hay un `.pdf` en disco que contradice al `.docx` de al lado.

Fuera del roadmap, en cuanto el usuario deje el PDF en `puas/fuente/`: `/di-pua` sobre el PUA 38985.
Eso no pasa por GSD — es poner en marcha lo que ya existe. No bloquea la v2.0, pero la Fase 14 sale
más completa con él: sin el PUA, las unidades de Contabilidad van sin temas y el manifiesto sin hash.
