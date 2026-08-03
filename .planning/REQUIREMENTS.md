# Requisitos

## Funcionales

### Ingesta y banco de conocimientos

- **REQ-01** — Convertir un PUA en PDF a Markdown normalizado con front-matter YAML que contenga
  los 9 campos de la §I y las secciones I–X como encabezados.
- **REQ-02** — Reconstruir correctamente la §VI (tabla de prácticas de laboratorio), que
  `pdftotext -layout` desordena.
- **REQ-03** — Mantener `puas/INDICE.md` como registro consultable: clave, nombre, programa, plan,
  ruta y hash SHA-256.
- **REQ-04** — Convertir a Markdown en `conocimiento/` todos los documentos fuente: normatividad,
  las 3 plantillas CIAD, instrucciones de llenado, estilo de redacción, rúbrica IEDI y el ejemplo
  961.
- **REQ-05** — Antes de pedir un PUA al usuario, comprobar si ya está en el índice.

### Calendario

- **REQ-06** — Derivar las semanas numeradas de un ciclo desde `calendarios/<ciclo>.yaml`, cuyo
  origen es el PDF oficial guardado en `calendarios/fuente/`.
- **REQ-07** — El número de semanas lo determina el calendario, no la plantilla. Para 2026-2 son
  **16** (10 ago – 28 nov 2026).
- **REQ-08** — Registrar suspensiones de labores (16 sep, 2 nov, 16 nov de 2026) y periodos de
  examen ordinario (30 nov – 8 dic) y extraordinario (14–17 dic).
- **REQ-09** — Ninguna entrega puede caer en día de suspensión ni después del fin de cursos.

### Generación del documento

- **REQ-10** — Rellenar las plantillas CIAD **reales** conservando logo, estilos y tablas.
- **REQ-11** — Soportar las tres modalidades, con sus diferencias de plantilla: columna `Entrega`
  dividida o no, y presencia o ausencia de los pasos `Primero…Quinto` y de la `Reflexión`.
- **REQ-12** — Copiar **literalmente** del PUA los datos de identificación (§I) y la competencia
  general (§III).
- **REQ-13** — Aplicar las convenciones tipográficas CIAD: recursos en negrita+cursiva, tipo de
  evidencia en negrita+subrayado, meta y porcentaje en negrita.
- **REQ-14** — Generar **un documento por grupo**, idénticos salvo el número de grupo y el bloque
  de firma del jefe de grupo.
- **REQ-15** — Exportar cada documento a `.pdf` además de `.docx`.
- **REQ-16** — Anexar las secciones fusionadas: criterios de evaluación del curso, reglas de
  convivencia con sanciones, fundamento legal y firma del jefe de grupo.

### Orquestación

- **REQ-17** — Orquestador interactivo que pregunta, en orden: ciclo → materia → profesor →
  modalidad → grupos → esquema de evaluación.
- **REQ-18** — Deducir el ciclo de la fecha actual (`AAAA-2` = ago–dic, `AAAA-1` = ene–jun).
- **REQ-19** — Ofrecer el esquema predefinido —Exámenes 20 %, Tareas y actividades 40 %, Proyecto
  final 40 %, exención del ordinario con promedio ≥ 80— o permitir capturar uno propio.
- **REQ-20** — Ofrecer los dos profesores registrados.

### Validación

- **REQ-21** — Los porcentajes del esquema suman exactamente 100 y coinciden con la suma de los
  valores de las metas.
- **REQ-22** — Existen **≥ 2 exámenes parciales** (Art. 68).
- **REQ-23** — Toda unidad del PUA tiene al menos una meta, y toda semana 1..N tiene actividad.
- **REQ-24** — Están presentes las citas legales obligatorias y un bloque de firma por grupo.
- **REQ-25** — Los indicadores **indispensables** del IEDI son verificables sobre el documento
  generado.

### Trazabilidad

- **REQ-26** — `curso.yaml` es la fuente única de verdad de un DI; el renderizador no inventa nada.
- **REQ-27** — Cada salida lleva `MANIFIESTO.yaml` con PUA + hash, calendario, versión de
  plantilla, profesor, grupo, esquema y commit de git.
- **REQ-28** — Regenerar con el mismo `curso.yaml` produce archivos idénticos salvo la marca de
  tiempo.
- **REQ-29** — Nombres de salida `DI-<ciclo>-<clave>-<grupo>.<ext>`.

### Grafo de conocimiento

- **REQ-30** — Grafo del dominio con nodos PUA, Unidad, Competencia, Tema, Meta, Evidencia,
  Criterio, Semana, Artículo, Plantilla, Profesor, Grupo, Curso.
- **REQ-31** — Responder dos preguntas hoy imposibles: qué temas del PUA quedaron sin meta, y qué
  materias comparten competencias.

## No funcionales

- **REQ-32** — Reutilizar el toolchain ya instalado (pandoc, pdftotext, python-docx, Word COM)
  antes que añadir dependencias.
- **REQ-33** — Git local únicamente; sin remoto ni push sin autorización explícita.
- **REQ-34** — `AGENTS.md` como contrato canónico para interoperar con Codex y agy; `CLAUDE.md`
  como puntero.
- **REQ-35** — Opus planifica y redacta las metas; Sonnet ejecuta. Perfil GSD `adaptive`.
- **REQ-36** — No modificar `referencias/` ni `ejemplos/`.
- **REQ-37** — Todo el proyecto en español, incluidos código y nombres de archivo.

## Criterio de aceptación global

Regenerar el DI de Big Data y compararlo contra `ejemplos/961 (1).pdf`. Debe ser equivalente en
estructura, formato y contenido derivable, con las fechas corregidas al ciclo en curso.
