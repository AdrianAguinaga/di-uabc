# Generador de Diseño Instruccional — UABC

Genera el **Diseño Instruccional (DI)** de una unidad de aprendizaje en `.docx` y `.pdf` a partir
de su **PUA** oficial, el **calendario escolar UABC** vigente, el profesor, la modalidad y los
grupos.

Rellena las **plantillas CIAD reales** (no las reconstruye), de modo que el formato institucional
se conserva intacto.

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

### Esquema de evaluación predefinido

| Concepto | Valor |
|---|---|
| Exámenes (mínimo 2 parciales, Art. 68) | 20 % |
| Tareas y actividades de clase | 40 % |
| Proyecto final | 40 % |

Exención del examen ordinario con promedio **≥ 80**. Configurable por curso.

## Estructura

| Directorio | Contenido |
|---|---|
| `referencias/` | Documentos fuente originales (plantillas CIAD, Estatuto, IEDI). **No se modifican.** |
| `ejemplos/` | DI reales ya elaborados, usados como referencia de calidad |
| `plantillas/` | Juego de trabajo con su `sha256` registrado, más las versiones sustituidas en `historico/` |
| `conocimiento/` | Banco de conocimientos: todo lo anterior convertido a Markdown para consulta |
| `puas/` | `fuente/` los PDF oficiales · `md/` normalizados · `INDICE.md` el registro |
| `calendarios/` | Calendarios escolares por ciclo + los PDF oficiales de origen |
| `config/` | Profesores, esquemas de evaluación, políticas y mapa de plantillas |
| `src/` | Código Python del generador |
| `cursos/` | Salida: un directorio por ciclo y materia |
| `grafo/` | Grafo de conocimiento del dominio |
| `.planning/` | Artefactos GSD del propio proyecto |

## Convenciones

- **Ciclos**: `AAAA-2` = agosto–diciembre · `AAAA-1` = enero–junio.
- **Nombres de salida**: `DI-<ciclo>-<clave>-<grupo>.<ext>` — p. ej. `DI-2026-2-39056-961.docx`.
- La **clave del PUA** es el identificador primario en todo el sistema.

## Requisitos

Python 3.11 · `python-docx` · `pdfplumber` · `PyYAML` · `pdftotext` (poppler) · Microsoft Word
(para exportar a PDF por COM; solo Windows).

```powershell
python -m pip install -r requirements.txt
```

## Ciclo vigente

**2026-2** — clases del 10 de agosto al 28 de noviembre de 2026 (**16 semanas**).
Ver `calendarios/2026-2.yaml`.
