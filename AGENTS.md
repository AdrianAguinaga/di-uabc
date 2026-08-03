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
4. **Los porcentajes suman exactamente 100** y debe haber **≥ 2 exámenes parciales** (Art. 68).
5. **Ninguna entrega cae en día de suspensión** ni después del fin de cursos.
6. **Todo dato es trazable.** Cada DI generado lleva un `MANIFIESTO.yaml` que registra el PUA y su
   hash, el calendario, la versión de plantilla, el profesor, el grupo, el esquema y el commit.
7. **La asistencia no es criterio de calificación**, pero **sí es requisito de derecho a examen**
   (Arts. 70 y 71). Nunca los mezcles en el documento.
8. **El generador no sustituye el criterio docente.** El resultado es un borrador que el profesor
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

`curso.yaml` es **el contrato** entre la etapa de planeación y la de renderizado. Su esquema está
en `src/modelo.py`. Todo lo que aparece en el documento sale de ahí.

## Mapa de directorios

| Ruta | Qué es | ¿Se edita? |
|---|---|---|
| `referencias/` | Plantillas CIAD, Estatuto, IEDI — originales | **No** |
| `ejemplos/` | DI reales de referencia | **No** |
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

- `pdftotext` **requiere `-enc UTF-8`**; sin él produce mojibake (`AUT�NOMA`).
- La §VI del PUA (tabla de prácticas) se desordena con `pdftotext -layout` → usar
  `pdfplumber.extract_table()`.
- **python-docx, Sección 1**: los campos vienen con los runs ya separados —
  `Clave:` es `[('Clave', bold=True), (': ', None)]`. Usa `add_run()`; **nunca** asignes
  `paragraph.text`, porque colapsa los runs y destruye el formato.
- **python-docx, Sección 2**: la tabla tiene **7 columnas de rejilla**, no las 6 lógicas del
  encabezado (`Semana` está fusionada horizontalmente). Mapa real:
  `0=Meta · 1=Semana · 2=modo · 3=Entrega · 4=Actividad · 5=Evidencia(s) · 6=Valor`.
  Opera sobre columnas de rejilla. Clona filas con `copy.deepcopy(tr._tr)` +
  `tbl._tbl.insert()`.
- **Word COM**: `Visible=False`, `DisplayAlerts=False`, rutas **absolutas**, y `try/finally` con
  `Quit()` para no dejar procesos `WINWORD.EXE` huérfanos.
- La plantilla presencial trae un **error de origen**: dice `Diseño Instruccional para la modalidad
  semipresencial:` aun siendo la escolarizada. Se reproduce corregido; queda constancia en
  `conocimiento/plantillas/`.

## Git

Repositorio **local únicamente**. No hay remoto y **no se hace push** sin autorización explícita
del usuario. Commits atómicos: uno por PUA ingerido, uno por fase GSD.
