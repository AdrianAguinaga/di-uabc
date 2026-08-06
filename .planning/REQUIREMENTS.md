# Requisitos

> **REQ-01 a REQ-37 son de la v1.0** y están validados: las 8 fases cerraron y hay tres materias
> generadas de extremo a extremo. **REQ-38 en adelante son del milestone v2.0.**

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
- **REQ-33** — El push es del usuario. El remoto `github.com/AdrianAguinaga/di-uabc` existe y es
  público desde el 3 de agosto de 2026; se empuja solo a petición explícita, y ningún PUA ni dato
  de un tercero se versiona sin preguntar antes.
- **REQ-34** — `AGENTS.md` como contrato canónico para interoperar con Codex y agy; `CLAUDE.md`
  como puntero.
- **REQ-35** — Opus planifica y redacta las metas; Sonnet ejecuta. Perfil GSD `adaptive`.
- **REQ-36** — No modificar `referencias/` ni `ejemplos/`.
- **REQ-37** — Todo el proyecto en español, incluidos código y nombres de archivo.

## Criterio de aceptación global (v1.0)

Regenerar el DI de Big Data y compararlo contra `ejemplos/961 (1).pdf`. Debe ser equivalente en
estructura, formato y contenido derivable, con las fechas corregidas al ciclo en curso.

---

# Milestone v2.0 — Estructura de calificación variable

Origen: el DI real de Zurisaddai Rubio Arriaga, espejado en
`conocimiento/ejemplos/531-contabilidad-financiera-2026-1.md`. Al reconstruirlo con el generador
hubo que **traducir** su estructura para que validara. Estos requisitos cierran esa deuda.

## Composición de la calificación

- **REQ-38** — Un **rubro** puede expresar los valores de sus metas en **puntos** en lugar de
  porcentaje, declarando su total (`150 pts`). El porcentaje del rubro sigue siendo lo que cuenta
  contra el 100 del esquema. Rubros en puntos y rubros en porcentaje **conviven en el mismo
  curso**: en el 531, «Actividades 30 %» va en puntos y «Exámenes 50 %» en porcentaje.
- **REQ-39** — Una meta puede aportar a **más de un rubro**: su valor principal más componentes
  adicionales, cada uno con su rubro, su valor y su etiqueta. Es lo que hace la meta 2.4 del 531
  —«10 pts / Examen I 15 %»— sin dejar de ser una sola meta con una sola semana.
- **REQ-40** — Un componente de meta puede ser de tipo `examen_parcial`, y **R3 lo cuenta igual
  que a una meta de ese tipo**. Los tres exámenes del 531 viven dentro de la actividad de las
  metas 2.4, 3.3 y 6.0; hoy R3 contaría cero y el documento no validaría.
- **REQ-41** — El esquema puede declarar un **segundo nivel**: el promedio del curso vale X % y el
  examen ordinario Y %, con X + Y = 100. Un curso que no lo declare se comporta exactamente como
  hoy — el promedio *es* la calificación.
- **REQ-42** — El identificador de una meta es **libre dentro de su unidad**: `1.0`, `2.0`, `1.1`,
  `0`. Ni las reglas ni el renderizado pueden asumir que la primera meta de una unidad es `.1`, ni
  que el encuadre se llama `0`.

## Rúbricas

- **REQ-43** — `curso.yaml` puede declarar una **rúbrica**: filas de concepto, puntos y
  descripción, con su total declarado. Se asocia a una meta o al trabajo final del curso.
- **REQ-44** — La rúbrica se renderiza como tabla en el documento, con el formato de las demás
  tablas del DI. El renderizador **no redacta** sus criterios: los imprime. Sigue vigente REQ-26.

## Validación

- **REQ-45** — R1 y R2 operan **en la unidad de cada rubro**. Un rubro en puntos que declara 150 y
  cuyas metas suman 140 es un **error** — es el defecto real del 531, hermano del defecto en
  porcentajes del 961 que ya atrapa `test_detecta_el_defecto_del_ejemplo_961`.
- **REQ-46** — Con segundo nivel, R1 verifica además que promedio + ordinario sumen 100, y que la
  exención quede declarada **contra el promedio del curso**, no contra la calificación final.
- **REQ-47** — Los puntos de una rúbrica suman su total declarado.

## No contaminación

- **REQ-48** — Ningún rasgo de la v2.0 se activa si el `curso.yaml` no lo declara. Regenerar 39056
  y 39062 tras **cada fase** produce la **misma huella de texto**, y ni `grafo/` ni
  `MANIFIESTO.yaml` cambian de forma. Es el criterio de aceptación del milestone entero.

## Criterio de aceptación global (v2.0)

- **REQ-49** — El `curso.yaml` de 38985 se reescribe a la **estructura real** de su DI de origen
  —rubro en puntos, segundo nivel 60/40, metas `1.0`, tres exámenes dentro de la actividad, rúbrica
  de 100 puntos— y **valida sin traducirse**, con el defecto de los 150/140 puntos reportado como
  error y no reproducido en silencio.

## Trazabilidad

Cada requisito de la v2.0 se entrega en **una sola** fase. La numeración continúa la de la v1.0,
cuyas ocho fases cerraron (REQ-01 a REQ-37, validados).

| Requisito | Fase | Estado |
|---|---|---|
| REQ-38 · rubro en puntos | Fase 9 — El valor de una meta deja de ser un porcentaje | **Validado** (2026-08-05) |
| REQ-39 · meta con componentes | Fase 9 | **Validado** (2026-08-05) |
| REQ-42 · identificador de meta libre | Fase 9 | **Validado** (2026-08-05) |
| REQ-40 · R3 cuenta componentes `examen_parcial` | Fase 10 — Las reglas cuentan en la unidad declarada | **Validado** (2026-08-06) |
| REQ-45 · R1 y R2 en la unidad de cada rubro | Fase 10 | **Validado** (2026-08-06) |
| REQ-41 · segundo nivel promedio + ordinario | Fase 11 — El segundo nivel de la calificación | Pendiente |
| REQ-46 · R1 con segundo nivel y exención contra el promedio | Fase 11 | Pendiente |
| REQ-43 · rúbrica declarada en `curso.yaml` | Fase 12 — La rúbrica en el contrato | Pendiente |
| REQ-47 · los puntos de la rúbrica suman su total | Fase 12 | Pendiente |
| REQ-44 · la rúbrica se renderiza como tabla | Fase 13 — El documento en la unidad real | Pendiente |
| REQ-49 · 38985 valida sin traducirse | Fase 14 — 38985 sin traducirse | Pendiente |
| **REQ-48 · no contaminación** | **Criterio de cierre de las seis fases** | Pendiente |

**REQ-48 no es una fase.** Es la condición de cierre de cada una: al terminar la 9, la 10, la 11,
la 12, la 13 y la 14 se regeneran 39056 y 39062 y se comprueba que su huella de texto no cambió.
Su instrumento —el comando que compara— se construye en la Fase 9 y lo heredan las demás.

El renderizado de los puntos, de los componentes y del segundo nivel no lleva requisito propio:
son la cara visible de REQ-38, REQ-39 y REQ-41, y se entregan en la Fase 13 junto a REQ-44, que sí
es exclusivamente de renderizado. Ninguno de los tres se da por cerrado hasta que aparece
correctamente en el documento.

**Cobertura: 12/12 requisitos de la v2.0 mapeados. Ningún huérfano, ningún duplicado.**
