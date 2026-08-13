# Banco de conocimientos

Los documentos institucionales que rigen este proyecto, convertidos a Markdown para que estén en
git y cualquier agente pueda consultarlos sin abrir un `.docx`, un `.xlsx` ni un PDF.

**Los originales viven en `referencias/` y `ejemplos/` y no se modifican nunca.** Si el CIAD o la
Universidad publican una versión nueva, se reemplaza el original y se reconvierte el Markdown —
no se edita el Markdown a mano.

## Normatividad

| Documento | Qué aporta | Original |
|---|---|---|
| [Estatuto Escolar — Título Tercero](normatividad/estatuto-escolar.md) | Artículos 63–75 verbatim: escala de calificación, mínimo aprobatorio, deber de informar criterios, mínimo de parciales, exención, porcentajes de asistencia para ordinario y extraordinario. **El fundamento legal de todo el documento generado.** | `Estatuto EscolarUABC Reforma May 202021.pdf` |
| [Propiedad intelectual](normatividad/propiedad-intelectual.md) | Uso de recursos de terceros en educación virtual; sanciones por plagio (RPIDA art. 59). Sustenta la regla de honestidad académica. | `propiedad-intelectual-de-terceros-en-la-educacion-virtual.pdf` |
| [Políticas de curso FCA](normatividad/politicas-curso-fca.md) | Redacción que la Facultad ya usa para políticas de cursos semipresenciales y a distancia. Base de `config/politicas.yaml`. | `POLITICAS DE CURSO SEMI DISTANCIA 2025.docx` |
| [Formato escolarizada de la Facultad](normatividad/formato-escolarizada-facultad.md) | El formato propio de la FCA para modalidad escolarizada, con logo. De aquí sale el bloque de firmas. | `Diseño Instruccional Modalidad Escolarizada con logo.docx` |

## Plantillas CIAD

| Documento | Qué aporta | Original |
|---|---|---|
| [Semipresencial](plantillas/ciad-semipresencial.md) | Estructura de las 3 secciones, 17 filas de semana, 7 columnas de rejilla, entrega dividida. | `CIAD_DI_Plantilla_Semipresencial-2025.docx` |
| [A distancia](plantillas/ciad-a-distancia.md) | Igual, sin sesión presencial: 6 columnas y entrega única. | `CIAD_DI_Plantilla_A_Distancia-2025.docx` |
| [Escolarizada / Presencial](plantillas/ciad-presencial.md) | 14 filas de semana, sin pasos ordinales ni reflexión. Trae erratas de origen. | `CIAD_DI_Plantilla_PRESENCIAL.docx` |
| [Deltas entre modalidades](plantillas/deltas-entre-modalidades.md) | Qué cambia exactamente de una plantilla a otra. Lo que el renderizador debe parametrizar. | Las tres |
| [Instrucciones de llenado](plantillas/instrucciones-llenado.md) | Cómo espera el CIAD que se llene cada campo, con su ejemplo de referencia. | `CIAD_DI_Plantilla_*_Instrucciones-2025.docx` |

## Modalidades de acreditación diversas

| Documento | Qué aporta | Original |
|---|---|---|
| [Índice y pertinencia de fuentes](modalidades_acreditacion/INDICE.md) | Mapa de las seis fuentes nuevas, con qué regula cada una y cuáles aplican directamente al Registro de Modalidades de Acreditación Diversas. | `referencias/modalidades_acreditacion/` |
| [Modalidades de aprendizaje y obtención de créditos](modalidades_acreditacion/Modalidades_de_Aprendizaje_2021.md) | Fuente principal: modalidades del Art. 155, requisitos y flujos de registro de OMA y PVVC. | `Modalidades_de_Aprendizaje_2021.pdf` |

## Estilo y rúbrica

| Documento | Qué aporta | Original |
|---|---|---|
| [Estilo de redacción CIAD](estilo/estilo-redaccion-ciad.md) | Tiempos verbales, ordinales, énfasis tipográfico por tipo de elemento, reflexión en pasado. La guía de voz del documento. | `CIAD_DI_EstiloRedaccionRecomendado_2023.docx` |
| [IEDI v2023-1](rubricas/iedi-2023-1.md) | Los 38 indicadores con los que el CIAD evalúa un DI, clasificados en indispensable / necesario / recomendable por modalidad. Es la base de la regla R8. | `CIAD_IEDI_v2023-1.xlsx` |

## Ejemplos

| Documento | Qué aporta | Original |
|---|---|---|
| [Big Data 961, ciclo 2026-1](ejemplos/961-big-data-2026-1.md) | El DI real que el generador debe saber reproducir: su anatomía, sus convenciones de redacción y **sus dos defectos verificados**. | `ejemplos/961 (1).pdf` |

> El 961 es **oráculo de formato, no de contenido**. Sus porcentajes por rubro no cuadran con el
> esquema que él mismo declara, y sus metas divergen entre la Sección 2 y la Sección 3. La capa de
> validación existe para atrapar exactamente eso; si al regenerarlo el resultado saliera idéntico,
> el validador no serviría.

## Qué archivo consultar según lo que necesites

| Necesitas… | Ve a |
|---|---|
| Citar un artículo | `normatividad/estatuto-escolar.md` y `config/politicas.yaml` |
| Saber cómo se ve el documento terminado | `ejemplos/961-big-data-2026-1.md` |
| Redactar una meta | `estilo/estilo-redaccion-ciad.md` + la Sección 3 del ejemplo |
| Saber qué cambia entre modalidades | `plantillas/deltas-entre-modalidades.md` |
| Saber si el DI cumple | `rubricas/iedi-2023-1.md` y `python src/validar.py` |
| Fechas | **Nunca aquí.** Solo `calendarios/<ciclo>.yaml`. |
