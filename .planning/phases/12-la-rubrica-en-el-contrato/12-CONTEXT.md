# Fase 12: La rúbrica en el contrato — Contexto

**Recogido:** 2026-08-06
**Estado:** Listo para planear

<domain>
## Frontera de la fase

La rúbrica es una parte declarativa del juicio docente: enumera qué se evalúa, sus puntos y la
descripción literal de cada concepto. El generador no la completa ni redacta. Esta fase abre ese
contrato, lo valida y lo deja trazable; la Fase 13 lo convertirá en una tabla del documento y la
Fase 14 lo declarará en Contabilidad Financiera.

**Dentro:** `curso.yaml` → modelo → R2 → `MANIFIESTO.yaml`, pruebas y documentación contractual.

**Fuera:** `render_docx.py`, plantillas, documentos producidos, `curso.yaml` de 38985,
`config/esquemas-evaluacion.yaml` y `grafo.py`. No se regenera `grafo/`: hoy no contiene un nodo de
rúbrica y el requisito exige conservar su forma cuando el rasgo no se declara.

</domain>

<decisions>
## Decisiones cerradas

- **D-01 — Una rúbrica opcional, no una lista.** `Curso.rubrica: Rubrica | None = None` representa
  una rúbrica de trabajo final. REQ-43 la pide en singular y solo hay una fuente institucional que
  justifique el contrato. Añadir una lista sería generalidad sin caso de uso.

- **D-02 — Forma declarativa.** Dentro de `curso.yaml`, la clave vive en el nivel superior:

  ```yaml
  rubrica:
    meta: M4.1                 # o rubro: trabajo_final; exactamente uno
    total: 100
    filas:
      - concepto: Portada
        puntos: 2
        descripcion: "…texto literal de la docente…"
  ```

  `meta` asocia la rúbrica con una actividad concreta; `rubro` permite asociarla con el trabajo
  final definido por la evaluación del curso. Exactamente una de las dos referencias es obligatoria.
  No se infiere del nombre de una meta ni del rubro `trabajo_final`.

- **D-03 — Dataclasses propias.** `FilaRubrica(concepto, puntos, descripcion)` y
  `Rubrica(total, filas, meta="", rubro="")` viven en `modelo.py`. El contrato exige los tres
  datos de cada fila y un total explícito; `None` significa “no declarada”.

- **D-04 — El modelo cuida la forma; R2, el significado.** Falta de filas, total no positivo,
  puntos negativos, asociación ausente o doble asociación son `ErrorModelo`. Que una referencia
  conocida no exista en este curso y que la suma de filas no corresponda a `total` son hallazgos
  de R2: el YAML sigue pudiendo cargarse e inspeccionarse.

- **D-05 — R2 se amplía; no nace R9.** R2 ya comprueba sumas de la estructura de evaluación. La
  rúbrica agrega otra suma declarada, por lo que un 98 o 102 contra 100 será **error R2**. Se
  conserva el contrato estable de ocho reglas.

- **D-06 — La suma compara puntos con puntos.** `sum(fila.puntos)` se compara con `rubrica.total`
  usando el redondeo a dos decimales ya empleado por el validador. No se convierte a porcentaje ni
  se vincula aritméticamente al porcentaje de la meta o del rubro: una rúbrica de 100 puntos puede
  evaluar un trabajo que pesa 40 % del curso.

- **D-07 — Referencias verificables.** Si se declara `meta`, R2 exige que exista una meta con ese
  `id`; si se declara `rubro`, que exista un rubro de evaluación con ese `id`. Los errores nombran
  la referencia declarada. No se exige que la meta y el rubro coincidan entre sí, porque la rúbrica
  declara una asociación, no un reparto de calificación.

- **D-08 — Literalidad.** Modelo, validador y manifiesto trasladan `concepto` y `descripcion` sin
  transformarlos. El único texto creado por código son mensajes técnicos de validación. Los textos
  visibles de la rúbrica entran en el barrido `ESTILO`, para que una abreviatura interna no alcance
  el futuro documento.

- **D-09 — Trazabilidad condicional.** `generar.manifiesto()` registra la rúbrica tal como el curso
  la declara, únicamente si existe. El manifiesto de cursos sin `rubrica:` conserva exactamente su
  forma; satisface a la vez la regla invariable de trazabilidad y REQ-48.

- **D-10 — No contaminación.** Ningún curso existente declara `rubrica:` en esta fase. Se prueba
  la ausencia en YAML crudo, la carga como `None`, cero cambio de R2 en 39056/39062 y
  `python -X utf8 src/huella.py verificar` al cierre. 38985 no se modifica hasta la Fase 14.

</decisions>

<source_evidence>
## Fuente y literalidad

La fuente de la forma es el DI original de Contabilidad Financiera 531. La tabla contiene
`Concepto`, `Puntos` y `Descripción`, con total declarado de 100. El Markdown de conocimiento
resume sus conceptos y puntos, pero la inspección de sólo lectura del `.docx` original confirmó que
cada fila también trae la descripción. Esas descripciones se copiarán de forma literal únicamente
cuando la Fase 14 declare el curso; esta fase usa fixtures aislados y no reescribe ese archivo.

</source_evidence>

<criterion>
## Discreción acotada

- La redacción exacta de los mensajes R2, siguiendo el estilo de los hallazgos existentes.
- Si la asociación válida se nombra `meta`/`rubro` en el mensaje o como “meta”/“rubro de
  evaluación”; el YAML queda fijado por D-02.
- La división de tareas y el orden de actualización de `AGENTS.md`.

</criterion>

<deferred>
## Diferido expresamente

- Dibujar la tabla de rúbrica y ubicarla en el DI (Fase 13).
- Declarar la rúbrica literal de 531 en 38985 y reproducir su salida (Fase 14).
- Representar rúbricas en `grafo.py`; no es requisito de esta fase y el grafo actual no abre esta
  sección del curso.
- Múltiples rúbricas por curso, rúbricas anidadas o cálculo automático de descriptores.

</deferred>
