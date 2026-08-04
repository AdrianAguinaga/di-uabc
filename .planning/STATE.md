# Estado del proyecto

**Proyecto**: Generador de Diseño Instruccional UABC (`DI-UABC`)
**Última actualización**: 2026-08-04
**Fase actual**: ninguna — las 8 fases del roadmap están hechas

## Progreso

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

## Lo que queda abierto

Nada del roadmap. Dos cosas menores, ambas decisiones del usuario y no del generador:

- Capturar el grupo real de 39062 y regenerar.
- El correo de `zra` sigue en `null` en `config/profesores.yaml`.

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

Decidir con el docente qué se hace con el hallazgo 9: completar los temas de las unidades II–V en
el `curso.yaml` de Big Data y repartirlos entre las metas, o aceptar la cobertura actual. Es
juicio pedagógico, no mecánico.

Después, con el PDF de otra materia en `puas/fuente/`, correr `/di-nuevo` sobre ella para ejercer
el único tramo del menú que sigue sin probarse: descubrir el PUA, ingerirlo en caliente y redactar
las metas desde cero.
