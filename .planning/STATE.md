# Estado del proyecto

**Proyecto**: Generador de Diseño Instruccional UABC (`DI-UABC`)
**Última actualización**: 2026-08-03
**Fase actual**: 1 — Cimientos y normalización (en curso)

## Progreso

| Fase | Estado |
|---|---|
| 1. Cimientos y normalización | En curso |
| 2. Banco de conocimientos | Pendiente |
| 3. Motor de calendario | Pendiente |
| 4. Ingesta de PUA | Pendiente |
| 5. Modelo y validación | Pendiente |
| 6. Renderizado docx + pdf | Pendiente |
| 7. Orquestador | Pendiente |
| 8. Grafo de conocimiento | Pendiente |

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

Terminar la Fase 1 (commit inicial) y continuar con la Fase 2 — banco de conocimientos.
