# Fase 9: El valor de una meta deja de ser un porcentaje — Registro de la discusión

> **Solo rastro de auditoría.** No se usa como entrada de los agentes de investigación, planeación
> ni ejecución. Las decisiones están en `09-CONTEXT.md`; este archivo conserva las alternativas
> que se consideraron y se descartaron.

**Fecha:** 2026-08-04
**Fase:** 09 — El valor de una meta deja de ser un porcentaje
**Áreas discutidas:** Rubro en puntos · Componentes de meta · Instrumento de la huella ·
Identificadores libres (las cuatro propuestas, las cuatro elegidas)

---

## Selección de áreas

| Área | Descripción | Elegida |
|---|---|---|
| Rubro en puntos | Cómo declara un rubro que sus metas van en puntos | ✓ |
| Componentes de meta | La forma del aporte adicional de una meta a otro rubro | ✓ |
| Instrumento de la huella | Qué es el comando de REQ-48 y qué compara | ✓ |
| Identificadores libres | REQ-42: qué queda por hacer si el encuadre ya se detecta por `tipo` | ✓ |

---

## Rubro en puntos

### Cómo se declara

| Opción | Descripción | Elegida |
|---|---|---|
| `unidad` + `total` | Dos claves explícitas: `unidad: puntos` y `total: 150` | ✓ |
| Solo `total_puntos` | Una clave; su presencia implica puntos | |
| `escala:` anidada | Un mapa `{unidad, total}` que agrupa el rasgo nuevo | |

**Razón:** es la que menos obliga a inferir a quien lee el YAML. `total_puntos` deja la unidad
implícita en el nombre del campo; `escala:` añade un nivel de anidamiento en el YAML y en el
dataclass.

### La unidad del `valor` de una meta

| Opción | Descripción | Elegida |
|---|---|---|
| Hereda del rubro | `Meta.valor` sigue siendo float; la unidad la pone el rubro | ✓ |
| La meta la declara | La meta puede llevar `unidad:` propia | |

**Razón:** un solo sitio declara la unidad, así que meta y rubro no pueden contradecirse — y no
hace falta una regla nueva que vigile la contradicción.

### Unidad desconocida (`unidad: creditos`)

| Opción | Descripción | Elegida |
|---|---|---|
| `ErrorModelo` al cargar | Vocabulario cerrado como `MODALIDADES` y `TIPOS_META` | ✓ |
| Hallazgo de regla | Carga y lo reporta `validar.py` | |

**Nota:** se discutió si esto choca con el criterio 1 de la fase («carga sin `ErrorModelo`»).
No choca: ese criterio protege lo **aritmético** —150 declarados contra 140 sumados debe cargar y
fallar en validación—, no una unidad que no existe.

### La conversión puntos → porcentaje

| Opción | Descripción | Elegida |
|---|---|---|
| Sí, como propiedad del modelo | La Fase 9 la expone; 10 y 13 la consumen | ✓ |
| No, solo el contrato | Cada fase la resuelve por su cuenta | |

**Razón:** evita que las Fases 10 y 13 la reinventen distinto.

---

## Componentes de meta

### La forma del aporte adicional

| Opción | Descripción | Elegida |
|---|---|---|
| `componentes:` lista | Lista con rubro, valor, etiqueta, tipo — el vocabulario de la meta | ✓ |
| `aporta:` lista | Lo mismo bajo una clave que nombra la relación | |
| `valores:` incluye el principal | Elimina la asimetría; el principal es la primera entrada | |

**Razón:** `valores:` era la más uniforme pero habría roto `rubro:`/`valor:` en las tres materias
ya escritas y en todas sus pruebas.

### El vocabulario del `tipo`

| Opción | Descripción | Elegida |
|---|---|---|
| El mismo `TIPOS_META` | `encuadre \| aprendizaje \| examen_parcial \| cierre` | |
| Vocabulario propio | Un conjunto aparte | ✓ |
| Libre, sin validar | Cadena cualquiera; solo R3 mira si dice `examen_parcial` | |

**Seguimiento — cuál es el conjunto:**

| Opción | Descripción | Elegida |
|---|---|---|
| `examen_parcial \| otro` | Mínimo: solo lo que una regla necesita contar | |
| `examen_parcial \| examen_ordinario \| actividad \| proyecto` | Nombra lo que un componente puede ser en un DI real | ✓ |

**Nota:** de los cuatro, solo `examen_parcial` cambia el comportamiento hoy. Los otros tres
describen, y dejan sitio a que la Fase 13 imprima distinto según el tipo.

### Qué más lleva un componente

| Opción | Descripción | Elegida |
|---|---|---|
| Solo etiqueta | Lo mínimo que la Fase 13 necesita imprimir | |
| Etiqueta + criterios | Sus propios `criterios_evaluacion:` | |
| Etiqueta + evidencia | Una evidencia propia, para la columna de la Sección 2 | ✓ |

**Seguimiento — forma de la evidencia y quién decide su impresión:**

| Opción | Descripción | Elegida |
|---|---|---|
| `Evidencia` completa, impresión a la Fase 13 | Se carga y se deja disponible | |
| Solo el nombre, impresión a la Fase 13 | Una cadena, como la forma corta que ya acepta el modelo | |
| `Evidencia` completa y ya se suma en Sección 2 | La Fase 9 fija la concatenación en `render_docx.py:283` | ✓ |

**Objeción planteada y respuesta:** se advirtió en la propia opción que esto cierra una decisión de
renderizado en una fase que el roadmap definió como solo contrato. El usuario la eligió con la
advertencia delante. Queda acotada en el CONTEXT como D-11: es contenido y no formato, no toca
plantillas, y REQ-48 la cubre porque sin `componentes:` declarados no cambia nada.

### El componente en el grafo

| Opción | Descripción | Elegida |
|---|---|---|
| No entra en esta fase | `grafo/` conserva su forma exacta | ✓ |
| Nodo derivado del índice | `meta:…:{id}:comp:{i}` | |
| El componente lleva su id | Declarado en el `curso.yaml` | |

---

## Instrumento de la huella

### Dónde vive

| Opción | Descripción | Elegida |
|---|---|---|
| `src/huella.py` con CLI | Módulo propio con subcomandos, como `src/plantillas.py verificar` | ✓ |
| Prueba en `pruebas/` | Entra en `unittest discover` y se comprueba sola | |
| Las dos cosas | Lógica en el módulo, prueba delgada que lo llama | |

**Razón:** el patrón ya existe en el repo, y no ata la generación completa de dos DIs al ciclo de
unas pruebas unitarias que hoy son rápidas y no dependen de las plantillas.

### Qué entra en la huella

| Opción | Descripción | Elegida |
|---|---|---|
| Texto del `.docx` + informe | sha256 del texto extraído y de la salida de `validar.py` | ✓ |
| Texto del `.docx` solamente | Literalmente lo que dice REQ-48 | |
| Texto + informe + forma del `MANIFIESTO` | Cubre el enunciado entero de REQ-48 | |

**Razón:** el informe entra porque la Fase 10 es de reglas — un cambio que altere un hallazgo sin
tocar el documento pasaría inadvertido. La forma del `MANIFIESTO` se dejó fuera porque exige
definir «forma» frente a valores que cambian por diseño (fecha, commit); queda aplazada y señalada
al planeador.

### Dónde se registra

| Opción | Descripción | Elegida |
|---|---|---|
| `pruebas/huellas.yaml` versionado | En git: `git diff` dice quién la cambió y cuándo | ✓ |
| Junto a cada curso | `cursos/…/HUELLA.yaml` | |
| En `.planning/` | Junto al estado del proyecto | |

### Cómo se actualiza una huella legítima

| Opción | Descripción | Elegida |
|---|---|---|
| Subcomando explícito | `huella registrar`, solo se corre a propósito | ✓ |
| A mano en el YAML | Se pega el hash que imprimió `verificar` | |
| Con diff del texto antes de aceptar | Muestra las líneas que cambiaron y pide confirmación | |

**Razón:** la tercera se descartó por código de más en una herramienta interna — `git diff` ya
enseña lo mismo.

---

## Identificadores libres

### El renombrado del encuadre contra REQ-48

Se planteó el choque: el criterio 3 de la fase pide renombrar el encuadre `0` de Big Data a `1.0`,
pero REQ-48 exige que la huella de 39056 no cambie.

| Opción | Descripción | Elegida |
|---|---|---|
| Prueba sobre una copia | Renombrar en memoria; el `curso.yaml` no se toca | |
| Curso sintético en `pruebas/` | Un YAML pequeño con ids `1.0`, `2.0`, `6.0` | |
| Renombrar de verdad y re-registrar | Se acepta el cambio de huella con `huella registrar` | ✓ |

**Objeción planteada y respuesta:** se advirtió que esto gasta la primera excepción a REQ-48 dentro
de la misma fase que construye el instrumento para vigilarlo. El usuario mantuvo la decisión. La
consecuencia —que el orden de los pasos deja de ser indiferente— se resolvió en la pregunta
siguiente.

**Seguimiento — orden de los pasos:**

| Opción | Descripción | Elegida |
|---|---|---|
| Registrar, renombrar, re-registrar | Línea base de hoy → contrato → verificar → renombrar → aceptar | ✓ |
| Renombrar primero, luego registrar | La línea base nace ya renombrada | |

**Razón:** es la única secuencia en la que el instrumento demuestra algo antes de que se le pida
una excepción. Registrar después habría dejado el único cambio de huella del milestone sin medir.

**Seguimiento — alcance del renombrado:**

| Opción | Descripción | Elegida |
|---|---|---|
| Solo el encuadre | `0` → `1.0`; `1.1`, `1.2`, … se quedan | ✓ |
| Todas las unidades abren en `.0` | Renumerar Big Data entero | |
| También Patrones (39062) | El mismo cambio en las dos materias de Adrian | |

**Razón:** el cambio mínimo y coherente. Patrones queda como documento de control con su huella
intacta durante toda la fase.

### Ids de meta duplicados

| Opción | Descripción | Elegida |
|---|---|---|
| Error de regla, en R2 | Como el `Counter` que R1 ya usa para rubros | ✓ |
| `ErrorModelo` al cargar | Se rechaza en `desde_dict` | |
| Nada, como hoy | Fuera de alcance | |

**Contexto aportado a la pregunta:** hoy `validar.py:141` comprueba ids de rubro repetidos, pero no
hay nada equivalente para metas — y el grafo construye sus nodos a partir del id.

### Cómo se fija que nadie deduzca el encuadre por su id

| Opción | Descripción | Elegida |
|---|---|---|
| Auditoría registrada + prueba | Se anota lo encontrado en `src/` y la prueba lo fija | ✓ |
| Solo la prueba | Si pasa, nadie lo deduce — la prueba es la auditoría | |
| Auditoría + comentario en el modelo | Además, se documenta en `Meta.id` | |

---

## Verificaciones hechas durante la discusión

Estas se comprobaron contra el código antes de preguntar, para no plantear falsas disyuntivas:

| Qué se verificó | Resultado |
|---|---|
| ¿Algo ordena las metas? | No. Sin `sorted()` ni `.sort()` sobre `curso.metas` en ningún módulo — el orden declarado ya se conserva |
| ¿Se deduce el encuadre por su id? | No. `validar.py:394` usa `m.tipo`, que es lo correcto. Única suposición encontrada |
| ¿Existe ya el instrumento de la huella? | No. `_huella()` en `grafo.py:128` es otra cosa (hash de texto de temas). Las comprobaciones de agosto se hicieron a mano |
| ¿Hay control de ids duplicados? | Solo para rubros (`validar.py:141`), no para metas |
| ¿Qué emite el `MANIFIESTO` por rubro? | `{"id", "porcentaje"}` (`generar.py:180`) — relevante para el alcance de la huella |

---

## Criterio de Claude

- Nombres de funciones y propiedades: la conversión puntos→porcentaje, la firma de `src/huella.py`,
  la disposición de `pruebas/huellas.yaml`.
- Cómo se recorre el `.docx` para extraer texto en orden estable.
- La redacción de los mensajes de `ErrorModelo` nuevos.

## Ideas aplazadas

- Componentes como nodos del grafo.
- La forma del `MANIFIESTO.yaml` dentro de la huella.
- Que `di-nuevo` pregunte por la unidad de cada rubro.
- Rubros en puntos en el catálogo `config/esquemas-evaluacion.yaml`.
- Renumerar Big Data y Patrones enteros al esquema `.0`.
