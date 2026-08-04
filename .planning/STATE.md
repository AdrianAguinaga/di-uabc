# Estado del proyecto

**Proyecto**: Generador de Diseño Instruccional UABC (`DI-UABC`)
**Última actualización**: 2026-08-03
**Fase actual**: 7 — Orquestador

## Progreso

| Fase | Estado | Commit |
|---|---|---|
| 1. Cimientos y normalización | Hecha | `3ab58e1` |
| 2. Banco de conocimientos | Hecha | `66ffee4` |
| 3. Motor de calendario | Hecha | `4e02016` |
| 4. Ingesta de PUA | Hecha | `4385ea3` |
| 5. Modelo y validación | Hecha | `0e30def` |
| 6. Renderizado docx + pdf | Hecha | `745f20e` |
| 7. Orquestador | En curso | — |
| 8. Grafo de conocimiento | Pendiente | — |

153 pruebas, todas pasan: `python -X utf8 -m unittest discover -s pruebas`.

De la Fase 7 ya está la cadena: `/di-nuevo` (menú de seis pasos, con su panel ASCII) y
`src/generar.py`, que valida → renderiza por grupo → exporta a PDF → escribe `MANIFIESTO.yaml`.
Big Data 2026-2 con los grupos 961 y 962 produce los cuatro archivos y el manifiesto.

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

Cerrar la Fase 7 corriendo `/di-nuevo` de extremo a extremo sobre una materia **nueva** (una que
todavía no tenga `curso.yaml`): es lo único que aún no se ha probado del menú —el descubrimiento
de PUAs, el paso de ingesta cuando falta, y la redacción de las metas desde cero—. Luego, Fase 8:
el grafo de cobertura PUA↔metas.
