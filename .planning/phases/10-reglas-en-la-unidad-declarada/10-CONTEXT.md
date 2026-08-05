# Fase 10: Las reglas cuentan en la unidad declarada — Contexto

**Recogido:** 2026-08-05
**Estado:** Listo para planear

<domain>
## Frontera de la fase

R2 y R3 dejan de suponer que todo valor es un porcentaje y que todo examen es una meta.

El enunciado general de la fase —fijado en la discusión, por encima de la redacción del roadmap—
es:

> **Toda regla lee todo aporte a un rubro, en la unidad que ese rubro declara.**

No es «R2 en puntos y R3 con los exámenes del 531». Esa formulación describe la *evidencia*, no
la regla. Los dos cursos que la ejercen son la prueba de que funciona, no su alcance.

**Dentro:** el accesor de aportes en el modelo, la aritmética de R2 por rubro y su hallazgo global,
las comprobaciones de integridad de un componente, y el conteo de R3.

**Fuera:** el documento (Fase 13), el segundo nivel de la calificación (Fase 11), la rúbrica
(Fase 12) y la reescritura de 38985 (Fase 14). El contrato de `curso.yaml` ya está abierto y **no
se toca**: la Fase 9 lo dejó cerrado.

</domain>

<hallazgo_de_encuadre>
## Por qué el alcance se ensanchó respecto al roadmap

El roadmap menciona los componentes **solo en el criterio 4, para R3**. Leído al pie de la letra,
R2 se implementaría sumando únicamente `m.valor`.

**Medido:** `componentes:` existe en el contrato desde la Fase 9, pero fuera del propio dataclass
aparece en **un solo sitio** de `src/` — `render_docx.py:274`, concatenando evidencias. Ninguna
regla lo lee. Es decir, hoy:

| Defecto | Qué pasa hoy |
|---|---|
| Componente imputado a un rubro que no existe | Carga limpio, valida limpio, se ignora en silencio |
| Componente con valor negativo | Igual — `validar.py:206` solo mira `m.valor` |
| El valor de un componente | No cuenta para el total de su rubro, nunca |

El tercero no es «el caso del 531»: es que **R2 está mal en general** desde que existe REQ-39.
Cualquier curso donde una meta aporte a dos rubros verá un faltante fantasma en el segundo. El 531
es el primero que lo ejerce, no el único al que le pasa.

Por eso la fase cierra el hueco entero en vez de solo la parte que sus criterios nombran. No es
capacidad nueva —no se añade nada al contrato—: es que las reglas sean correctas sobre un contrato
que ya existe. Decidido con la objeción de alcance sobre la mesa.

</hallazgo_de_encuadre>

<decisions>
## Decisiones de implementación

### El accesor de aportes

- **D-01:** La agregación vive **una sola vez, en el modelo**, como un generador plano que emite
  todos los aportes del curso. Cada consumidor filtra lo suyo. Se descartó un accesor por rubro
  (`aportes_de(rubro_id)`) porque solo le sirve a R2 —R3 agrupa por tipo y la Fase 13 por meta—, y
  se descartó devolver solo la suma porque R2 seguiría derivando en línea la lista de metas
  imputadas para su mensaje.

  ```python
  @dataclass(frozen=True)
  class Aporte:
      meta: Meta
      rubro: str
      valor: float      # en la unidad de SU rubro
      etiqueta: str
      tipo: str
      es_componente: bool

  # en Curso
  def aportes(self) -> Iterator[Aporte]:
      for m in self.metas:
          yield Aporte(m, m.rubro, m.valor, m.etiqueta, m.tipo, False)
          for c in m.componentes:
              yield Aporte(m, c.rubro, c.valor, c.etiqueta, c.tipo, True)
  ```

  Sustituye la derivación en línea de `validar.py:197`
  (`sum(m.valor for m in self.c.metas if m.rubro == r.id)`).

- **D-02:** El aporte sale **en la unidad cruda de su rubro** — `10` significa 10 pts o 10 %, según
  el rubro. Convertir es cosa de `Rubro.a_porcentaje()`, que ya existe desde la Fase 9 (D-04). R2
  necesita el valor crudo para comparar contra `base` y para redactar el error en puntos;
  convertir antes le quitaría justo lo que necesita. Se descartó llevar los dos valores como campos
  del `Aporte` por ser un derivado que puede desincronizarse.

- **D-03:** **R3 consume el mismo accesor**, filtrando por `tipo`. El invariante queda escrito una
  vez: un examen parcial es un aporte de ese tipo, no importa dónde se declaró. Se descartó que R3
  mantuviera su propia derivación, que dejaría dos definiciones de «examen parcial» que hay que
  mantener de acuerdo.

  **Acoplamiento implícito que esto crea, y que hay que respetar:** `examen_parcial` es el único
  valor que comparten `TIPOS_META` (`modelo.py:31`) y `TIPOS_COMPONENTE` (`modelo.py:35`). El
  filtro de R3 funciona por ese solapamiento. Si alguna de las dos listas cambia, R3 cambia con
  ella sin decirlo.

### R2 — la aritmética

- **D-04:** La comprobación **por rubro** compara la suma de sus aportes contra `r.base`
  (`modelo.py:217`), no contra `r.porcentaje`. `base` ya devuelve `total` si el rubro está en
  puntos y `porcentaje` si no, así que la regla se escribe una sola vez para las dos unidades y
  **nunca suma unidades distintas entre sí** (criterio 2).

- **D-05:** El **hallazgo global** de `validar.py:186-193` —«el valor de las metas suma X, el
  esquema declara Y»— **se conserva, convertido a porcentaje**. Con unidades mixtas su forma actual
  suma peras con manzanas; convertido vuelve a significar algo y vale igual para cursos mixtos.

  Se descartó retirarlo por redundante —la comprobación por rubro lo implica— porque deja al curso
  sin un mensaje de cabecera que diga de un vistazo cuánto le falta al total, y porque volvería
  tautológica la prueba de `test_validar.py:180` (ver D-07).

- **D-06 — cómo se convierte, y por qué importa:** se suman los aportes **en su unidad cruda dentro
  de cada rubro** y se convierte **esa suma, una vez por rubro**. No se convierte aporte a aporte.

  ```python
  # correcto: una división por rubro
  total = sum(r.a_porcentaje(sum(a.valor for a in aportes_de(r))) for r in rubros)
  ```

  **Medido durante la discusión, no supuesto:** convirtiendo aporte a aporte, un rubro de 150 pts
  repartido en 21 metas de 7 pts más una de 3 —150 exactos— suma `29.99999999999999` contra los
  30 % declarados. Un curso correcto emitiría un error falso. Y no es un caso rebuscado: «catorce
  entregas» del 38985 tiene esa forma. Convirtiendo una vez por rubro, `a_porcentaje(150) == 30.0`
  exacto.

  Se combina con el `round(..., 2)` que `validar.py` ya usa en R1 y R2. Se descartó una tolerancia
  explícita (`math.isclose` o un epsilon en `config/esquemas-evaluacion.yaml`) por introducir un
  concepto que ninguna otra regla usa.

  **Comprobado además:** con la conversión por rubro, 39056 y 39062 dan `100.0` exacto. Hoy no hay
  riesgo sobre la huella; la decisión es para que siga sin haberlo con cursos que aún no existen.

- **D-07 — restricción sobre el texto del mensaje global:**
  `test_el_total_correcto_no_absuelve_al_rubro_incorrecto` (`pruebas/test_validar.py:180-186`)
  afirma `assertNotIn("El valor de las metas suma", mensajes)`. Existe para probar que el hallazgo
  global **no** absuelve al rubro mal cuadrado.

  El mensaje **debe conservar ese prefijo literal**. Si se reformula al hablar en porcentajes
  convertidos, la prueba sigue pasando pero deja de probar nada — se vuelve tautológica en
  silencio, sin que nada falle. Si el planeador prefiere reformular el mensaje, **tiene que
  actualizar esa prueba en el mismo plan**, no dejarla pasando en vacío.

### R2 — la integridad de un componente

- **D-08:** Un componente imputado a un **rubro inexistente** y un componente con **valor
  negativo** pasan a ser **error de R2**, hermanos de los que ya emite para las metas
  (`validar.py:179-184` y `:206`). Mismo sitio, mismo trato.

  Sigue el precedente de D-17 de la Fase 9, que puso los ids de meta duplicados en R2 y no en
  `ErrorModelo`: el curso con el defecto **sigue cargando y se puede inspeccionar**, y falla al
  validar. Se descartó repartirlo —valor negativo como `ErrorModelo` porque el componente puede
  juzgarlo solo, rubro inexistente en R2— por dejar el mismo tipo de defecto en dos sitios y tratar
  al componente distinto que a la meta.

- **D-09:** Un componente imputado **al mismo rubro que su meta es legítimo**. Se suma como
  cualquier otro aporte y no genera ningún hallazgo, ni error ni aviso.

  Es un caso real: una actividad con dos piezas calificadas por separado —«Reporte 5 pts» y
  «Presentación 5 pts»— dentro de la misma meta y el mismo rubro. REQ-39 dice que una meta *puede*
  aportar a más de un rubro, no que deba. Un aviso sería ruido permanente en un curso correcto.

### R3 — qué cuenta como examen parcial

- **D-10:** **Cada aporte de tipo `examen_parcial` cuenta uno.** Una meta de ese tipo que además
  lleve un componente del mismo tipo cuenta **dos**: son dos aportes distintos, con etiqueta y
  valor propios, que el documento imprimirá por separado. Sin deduplicación por meta — sale solo
  del accesor plano y mantiene la regla en una línea.

  Con esto se cumple el criterio 4 sin caso especial: tres componentes `examen_parcial` y ninguna
  meta de ese tipo dan 3 y pasan; uno solo da 1 y falla con el mensaje del Art. 68.

- **D-11:** El aviso de `parciales:` (`validar.py:224-230`) **se reformula**: deja de decir «hay N
  metas de tipo `examen_parcial`» y habla de **exámenes parciales declarados**, que es lo que ahora
  cuenta vengan de donde vengan. Sigue siendo **aviso, no error** — cambiar su severidad no lo pide
  ni REQ-40 ni REQ-45.

  **Medido:** ni 39056 ni 39062 lo emiten —los dos declaran `parciales: 2` y tienen 2 metas de ese
  tipo—, así que reformularlo no toca la huella. En 38985 el texto actual sería engañoso justo en el
  curso que la fase existe para admitir.

### La evidencia y el cierre

- **D-12:** El curso que declara **150 pts y suma 140** vive como **fixture de diccionario en
  `pruebas/test_validar.py`**, hermano del `CURSO_VALIDO` que ya existe, con sus variantes por
  `deepcopy`. Es la convención del repo: `pruebas/` no guarda archivos de datos —lo único no-`.py`
  ahí es `huellas.yaml`— y los tests que necesitan un archivo lo vuelcan a un `tempfile.mkdtemp()`
  con `yaml.safe_dump` (`test_generar.py:38-39`, `test_grafo.py:111-112`). Si el criterio 1 quiere
  ejercerse literalmente por la CLI, se usa ese mismo patrón.

  Se descartó un curso sintético versionado en `cursos/` —dejaría de contener solo materias reales
  y el grafo lo recogería como una materia más.

- **D-13 — 38985 no se toca en esta fase.** Reescribirlo a puntos le quitaría a la Fase 14 su
  criterio 2, que es literalmente su prueba de fuego, y lo dejaría **inválido de forma permanente**
  durante las Fases 11, 12 y 13, porque el defecto no se resuelve hasta la 14. Su huella no se
  vigila (D-22 de la Fase 9), así que REQ-48 no lo impediría: lo impide el orden de trabajo.

- **D-14:** El cierre de REQ-48 es **`python src/huella.py verificar` a mano**, conservando D-18 de
  la Fase 9 —la huella no cuelga del ciclo unitario, que hoy es rápido y no depende de las
  plantillas—, **más una prueba unitaria** que fija los hallazgos de un curso que no declara ni
  `componentes:` ni `unidad:`. Así una regresión en los hallazgos se ve en el ciclo rápido y no
  solo al cerrar la fase.

  Se descartó meter `huella verificar` en la suite: revertiría D-18 y haría que las pruebas generen
  cuatro documentos y dependan de las plantillas.

- **D-15 — la línea base medida, para que la prueba de D-14 no se escriba a ojo:** hoy los cuatro
  documentos de control validan **limpios**. Su informe contiene la cabecera, **cinco recordatorios
  IEDI** (2.4, 3.1, 3.2, 3.5, 4.1) y `VÁLIDO`. **Cero hallazgos de R2 y cero de R3.**

  De ahí se sigue algo que conviene tener claro antes de planear: **la redacción de los mensajes de
  R2 y R3 es libre.** Lo que REQ-48 exige es que estos cursos sigan emitiendo *cero* hallazgos de
  esas reglas, no que un texto se conserve. La única restricción de texto viva es D-07, y viene de
  una prueba, no de la huella.

  El criterio 3 del roadmap tampoco aprieta: `test_detecta_el_defecto_del_ejemplo_961`
  (`test_validar.py:169-178`) solo comprueba que la regla sea «R2» y que aparezcan las etiquetas
  «Proyecto final» y «Exámenes» en el mensaje. Conservarla **sin tocarse** es holgado.

### Criterio de Claude

- El nombre exacto de `Curso.aportes()` y del dataclass `Aporte`, y si `Aporte` guarda la `Meta`
  entera o solo su id — con la condición de que la Fase 13 pueda llegar desde un aporte a su meta.
- La redacción concreta de los mensajes nuevos de R2 y R3, siguiendo el estilo de los existentes:
  decir qué falta y con qué valores, nombrando la unidad. Sujeta a D-07 en el caso del global.
- Si el hallazgo por rubro en puntos menciona además el equivalente en porcentaje.
- Cómo se organiza el fixture `CURSO_EN_PUNTOS` y sus variantes dentro de `test_validar.py`.

</decisions>

<canonical_refs>
## Referencias canónicas

**Los agentes de investigación y planeación DEBEN leerlas antes de planear o implementar.**

### Requisitos y encuadre
- `.planning/REQUIREMENTS.md` — REQ-40 (R3 cuenta componentes `examen_parcial`), REQ-45 (R1 y R2
  en la unidad de cada rubro), REQ-48 (no contaminación), REQ-26 (el renderizador no inventa).
- `.planning/ROADMAP.md` §«Fase 10» — meta, dependencias y los cinco criterios de éxito.
- `.planning/phases/09-valor-de-una-meta/09-CONTEXT.md` — **de lectura obligada.** D-01 a D-09 son
  el contrato que esta fase consume; D-04 (`a_porcentaje`), D-05 (`total` obligatorio, no
  inferido), D-08/D-26 (`TIPOS_COMPONENTE` cerrado, `tipo` sin default) y D-17 (defectos de
  identidad como error de regla, no `ErrorModelo`) se citan directamente arriba.
- `.planning/phases/09-valor-de-una-meta/09-VERIFICATION.md` — qué quedó demostrado de la Fase 9.

### Reglas y modelo
- `AGENTS.md` §«Las ocho reglas de validación (`src/validar.py`)» (líneas 168-199) — el contrato de
  las reglas. **Si R2 o R3 cambian de comportamiento, esta sección se actualiza en el mismo plan.**
- `AGENTS.md` §«Contrato de `curso.yaml`» (líneas 142-167) — el contrato que la Fase 9 amplió.
- `AGENTS.md` §«Reglas invariables» (líneas 20-48) — no negociables del proyecto.
- `src/modelo.py:31-35` (`TIPOS_META`, `TIPOS_COMPONENTE`, `UNIDADES_RUBRO`), `:101-123`
  (`Componente`), `:145-186` (`Meta`), `:188-228` (`Rubro`, con `base` y `a_porcentaje`).
- `src/validar.py:173-210` (R2, las tres comprobaciones) y `:214-230` (R3).
- `config/esquemas-evaluacion.yaml:106` — `parciales_minimos: 2` (Art. 68).

### Pruebas que condicionan el trabajo
- `pruebas/test_validar.py:169-178` — `test_detecta_el_defecto_del_ejemplo_961`, que el criterio 3
  exige conservar **sin tocarse**.
- `pruebas/test_validar.py:180-186` — `test_el_total_correcto_no_absuelve_al_rubro_incorrecto`,
  sujeta a D-07.
- `pruebas/test_generar.py:38-39` y `pruebas/test_grafo.py:111-112` — el patrón de volcado a
  `mkdtemp` que D-12 reutiliza.

### Cierre
- `src/huella.py` — `verificar` / `registrar`. En esta fase **solo `verificar`**: nada debe cambiar.
- `pruebas/huellas.yaml` — la línea base de los cuatro documentos de control.

</canonical_refs>

<code_context>
## Lo que ya existe

### Reutilizable — no se reimplementa
- **`Rubro.base`** (`modelo.py:217`) — `total` si el rubro está en puntos, `porcentaje` si no. Es
  contra esto que compara R2 (D-04); no hace falta ninguna bifurcación por unidad en la regla.
- **`Rubro.a_porcentaje(valor)`** (`modelo.py:221`) — la conversión de D-04 de la Fase 9. La
  consume el hallazgo global (D-05/D-06). No se reinventa.
- **`Componente`** (`modelo.py:101-123`) con `rubro`, `valor`, `etiqueta`, `tipo`, `evidencia`, y
  `tipo` validado contra `TIPOS_COMPONENTE` al construir.
- **`Meta.componentes`** (`modelo.py:157`) — ya se carga desde el YAML (`:328`).
- **`Validador.error()` / `.aviso()`** (`validar.py:118-123`) — el canal de hallazgos. Los mensajes
  nuevos entran por ahí, con su regla y su nivel.
- **El patrón de fixture de `test_validar.py`** — `CURSO_VALIDO` + `copy.deepcopy` + helpers
  `curso(**cambios)` e `informe(**cambios)` (`:104-112`). D-12 lo extiende.

### Patrones establecidos que acotan el trabajo
- `validar.py` redondea a 2 decimales y compara por igualdad exacta (`round(x, 2) != y`). D-06 se
  apoya en esa convención en vez de introducir una tolerancia nueva.
- Los defectos de **esquema** son `ErrorModelo` al cargar; los de **aritmética e identidad** son
  hallazgos de regla. D-08 sigue esa línea.
- Los vocabularios son **cerrados** y un valor fuera de la lista es `ErrorModelo` (D-03/D-08 de la
  Fase 9). R3 se apoya en que `examen_parcial` significa lo que dice.

### Puntos de integración
- `Curso` (`modelo.py:~261-296`) — donde entra `aportes()`, junto a `unidad()` y `metas_de()`, que
  ya son accesores del mismo estilo.
- `Validador.regla_2` y `.regla_3` (`validar.py:173`, `:214`) — los dos únicos consumidores de esta
  fase. `regla_1` **no se toca** (ver abajo).
- `src/render_docx.py:274` — el único sitio de `src/` que hoy lee `componentes`, para las
  evidencias (D-11 de la Fase 9). **No se toca**: el resto del documento es la Fase 13.

### Sobre R1, que REQ-45 nombra
REQ-45 dice «R1 y R2 operan en la unidad de cada rubro», pero **todo lo que R1 mira ya está en
porcentaje**: la suma de `r.porcentaje` contra 100, los ids de rubro duplicados, el umbral de
exención y el contraste contra el catálogo de esquemas (`validar.py:126-169`). Ninguna de esas
cuatro comprobaciones toca un valor de meta.

La conclusión provisional es que **R1 no necesita cambio alguno**, y que la parte de REQ-45 que le
corresponde ya la cumple por construcción. No se discutió a fondo. Se registra al estilo de D-12 y
D-13 de la Fase 9 —afirmaciones sobre el código que se fijan con una prueba en vez de
implementarse—, pero **la auditoría concreta le toca al plan**: si el planeador encuentra en R1
algo sensible a la unidad, que lo levante en vez de resolverlo por su cuenta.

</code_context>

<specifics>
## Ideas concretas de la discusión

- **La forma del accesor se eligió sobre código, no sobre descripciones.** El generador plano ganó
  porque una sola función da las tres vistas que hacen falta —`if a.rubro ==` para R2,
  `if a.tipo ==` para R3, `if a.meta is` para la Fase 13— sin código de más en ninguna.

- **El defecto de coma flotante se encontró midiendo, y cambió la decisión.** La conversión aporte
  a aporte parecía correcta hasta que se probó con 22 metas: `29.99999999999999` sobre 150 pts
  exactos. La conversión por rubro no es una micro-optimización, es lo que evita un error falso en
  un curso correcto. Y dice algo más honesto: lo que aporta un rubro al 100 es el total del rubro.

- **Dos pruebas existentes resultaron más frágiles de lo que aparentan.** La de la línea 180 se
  vuelve tautológica si el mensaje global se reformula (D-07). La del 961, que el roadmap manda
  conservar intacta, resultó ser holgada: solo mira que aparezcan dos etiquetas. Conservarla no
  restringe casi nada — la restricción real es D-07, y viene de la otra.

- **El peso de REQ-48 sobre esta fase es menor de lo que parecía al empezar.** Se creyó que la
  redacción de los mensajes estaba congelada por la huella del informe (D-19/D-27 de la Fase 9).
  Medido: los cursos de control validan limpios y no emiten ni un hallazgo de R2 o R3, así que los
  textos son libres. Lo que hay que preservar es el *silencio* de esas reglas sobre esos cursos.

</specifics>

<deferred>
## Ideas apartadas

- **Los componentes en el grafo.** Sigue vigente D-10 de la Fase 9: no se crean nodos
  `meta:…:comp:{i}`. `grafo/` conserva su forma. Esta fase no lo cambia.

- **Que el aviso de `parciales:` pase a ser error.** Se consideró en D-11 y se descartó: es un
  cambio de severidad que ninguno de los dos requisitos de la fase pide. Si algún día se quiere,
  es su propia decisión.

- **Un curso de ejemplo del rasgo nuevo, versionado en `cursos/`.** Descartado en D-12 por meter en
  `cursos/` algo que no es una materia real y que el grafo recogería como tal. Si alguna vez hace
  falta un banco de cursos de ejemplo, necesita su propio sitio y su propia decisión.

- **Una tolerancia numérica declarada en `config/esquemas-evaluacion.yaml`,** junto a
  `suma_exacta` y `exencion_minima`. Descartada en D-06 a favor del `round(..., 2)` existente.
  Vuelve a ser pertinente si alguna fase futura introduce aritmética con más acumulación de error
  —el segundo nivel de la Fase 11 es candidato—.

- **El prefijo `M0_` del recurso «Foro de presentación» de Big Data,** que quedó con su meta ya
  renombrada a `1.0` (D-14 de la Fase 9). Sigue pendiente de acordar con el docente. No es de esta
  fase.

- **Los `MANIFIESTO.yaml` de los cursos de control dejaron de listar los `.pdf`** porque
  `huella registrar` genera con `pdf=False`, y los PDFs en disco de 39056 son anteriores al
  renombrado. Anotado al cerrar la Fase 9; sigue abierto y no lo toca esta fase.

</deferred>

---

*Fase: 10-reglas-en-la-unidad-declarada*
*Contexto recogido: 2026-08-05*
