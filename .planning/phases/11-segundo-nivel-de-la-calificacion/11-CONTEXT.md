# Fase 11: El segundo nivel de la calificación — Contexto

**Recogido:** 2026-08-06
**Estado:** Listo para planear

<domain>
## Frontera de la fase

`curso.yaml` deja de suponer que los rubros suman 100 y ahí termina la calificación.

El enunciado que gobierna la fase:

> **La calificación puede tener dos niveles, y el umbral de exención dice contra cuál se mide.**

Es un rasgo **aditivo**: no toca la aritmética existente y su regla es nueva, así que entra entero
—modelo y regla— en la misma fase. Un curso que no lo declare se comporta exactamente como hoy: el
promedio *es* la calificación.

**Dentro:** las claves nuevas del contrato (`segundo_nivel:` y `exencion_contra:`), sus dataclasses
en `modelo.py`, su declaración en el catálogo de esquemas, y las comprobaciones que R1 hace sobre
ellas.

**Fuera:** el documento (Fase 13 — la tabla de los dos niveles), la rúbrica (Fase 12), y la
reescritura de 38985 (Fase 14). R2 y R3 **no se tocan**: la Fase 10 las dejó cerradas y el segundo
nivel no cambia lo que aporta una meta a un rubro. `grafo.py` tampoco — ver D-21.

</domain>

<decisions>
## Decisiones de implementación

### El contrato del segundo nivel

- **D-01:** El segundo nivel es un **par fijo con claves nombradas**, no una lista.

  ```yaml
  evaluacion:
    segundo_nivel:
      promedio:
        porcentaje: 60
        etiqueta: "Valor del promedio antes del Examen Ordinario"
      ordinario:
        porcentaje: 40
        etiqueta: "Valor del examen Ordinario"
  ```

  Es exactamente lo que define REQ-41 y lo único que contempla el Estatuto: no hay un tercer
  sumando. Se descartó una lista `niveles:` hermana de `rubros:` porque obligaría a R1 a
  **identificar por id cuál de las filas es el promedio** para poder aplicar el criterio 3 —la
  exención se mide contra una fila concreta, no contra «una del montón»— a cambio de admitir una
  generalidad que nadie ha pedido.

- **D-02:** La `etiqueta:` de cada fila es **obligatoria y del contrato**, como `Rubro.etiqueta`.
  Los rótulos del DI de origen —«Valor del promedio antes del Examen Ordinario» y «Valor del examen
  Ordinario»— son redacción de la docente, no vocabulario del proyecto. Así REQ-26 queda intacto en
  la Fase 13: el renderizador imprime, no redacta, y otra docente con otra redacción no necesita
  que se toque código.

  Se descartó `etiqueta:` opcional con texto por defecto del renderizador —es el patrón de
  `Rubro.detalle`, pero aquí crea justo la costura que REQ-26 vigila— y se descartó fijarlos en la
  Fase 13.

- **D-03:** Vive como **dataclasses propios** en `modelo.py`:

  ```python
  @dataclass
  class Nivel:
      porcentaje: float
      etiqueta: str

  @dataclass
  class SegundoNivel:
      promedio: Nivel
      ordinario: Nivel

  # en Curso
  segundo_nivel: SegundoNivel | None = None
  ```

  `None` es «no declarado», así que **el rasgo entero cuelga de un solo `if`** y la no
  contaminación se verifica de un vistazo. Sigue el patrón de `Rubro` y `Horario`. Se descartaron
  campos sueltos (`peso_promedio` / `peso_ordinario` con default) porque «no declarado» se volvería
  indistinguible de «declarado 100 y 0», y REQ-41 exige distinguirlos.

- **D-04 (derivada, no preguntada):** **los dos porcentajes se declaran; ninguno se deriva del
  otro.** El criterio 1 pide que «60 y 30» produzca un error de R1; si el ordinario se calculara
  como `100 − promedio`, ese curso sería inexpresable y el criterio no tendría cómo probarse.
  Coincide con D-05 de la Fase 9 (`total:` obligatorio, no inferido de la suma).

- **D-05:** El **catálogo también lo declara**. `zra-contabilidad` en
  `config/esquemas-evaluacion.yaml` gana su bloque `segundo_nivel:` con el 60/40 y las etiquetas
  literales del DI de origen, y su comentario de las líneas 66-68 —«Ese segundo nivel NO existe en
  el modelo»— se corrige, porque esta fase lo vuelve falso.

  **Ojo para el planeador:** las etiquetas del catálogo tienen que ser las **literales** del DI de
  origen, o el curso de la Fase 14 arrancará con un aviso espurio en cuanto las declare (ver D-14).

### La exención: contra qué se mide

- **D-06:** Clave **`exencion_contra:`**, hermana de `exencion_ordinario:` dentro de `evaluacion:`,
  con **vocabulario cerrado**: `promedio` | `calificacion_final`.

  ```yaml
  evaluacion:
    exencion_ordinario: 90
    exencion_contra: promedio
  ```

  Un valor fuera de esos dos es `ErrorModelo` al cargar (D-03 de la Fase 9). Se descartó meterla
  dentro de `segundo_nivel:` porque separaría el umbral (fuera) de su referencia (dentro), que son
  la misma decisión partida en dos. Se descartó no tener clave —dejar el significado fijado por
  documentación— porque entonces no hay nada que rechazar y el criterio 3 del roadmap se queda sin
  forma de probarse.

  **Por qué el vocabulario admite el valor malo:** si fuera solo `("promedio",)`, escribir
  `calificacion_final` sería «valor inválido» al cargar y el mensaje pedagógico que pide el criterio
  3 —«explica la diferencia»— se perdería. El valor está en el vocabulario precisamente para que R1
  pueda explicarlo.

- **D-07:** Es **obligatoria cuando hay segundo nivel**; su ausencia entonces es `ErrorModelo`. Sin
  segundo nivel es opcional y ausente significa `promedio`.

  Sigue D-26 de la Fase 9 (`Componente.tipo` obligatorio sin default): el dato que decide el
  significado no se infiere. Y hace lo que el criterio 3 existe para hacer — obligar a enfrentar la
  pregunta justo en el curso donde tiene consecuencias.

  **Restricción derivada sobre el campo:** por eso `Curso.exencion_contra` **no puede llevar
  `"promedio"` como default** en el dataclass. Si lo llevara, «ausente» y «declarado promedio»
  serían indistinguibles y la obligatoriedad no se podría comprobar. Queda `exencion_contra: str = ""`,
  el `__post_init__` de `Curso` levanta `ErrorModelo` si hay segundo nivel y la cadena está vacía, y
  quien la consume lee `exencion_contra or "promedio"`.

  REQ-48 a salvo: 39056 y 39062 no declaran ninguna de las dos claves y su carga no cambia.

- **D-08:** `exencion_contra: calificacion_final` **con** segundo nivel es **error de R1**, no
  `ErrorModelo`. Es lo que dice el criterio 3 literalmente («rechazado por R1») y lo que hace
  D-17/D-08 de las fases anteriores: el curso con el defecto **sigue cargando y se puede
  inspeccionar**, y falla al validar.

  **No hay conflicto real con D-03 de la Fase 9,** aunque lo parezca: D-03 manda `ErrorModelo` para
  un valor que el modelo **no conoce**. Aquí es un valor conocido y prohibido —un juicio semántico,
  no una brecha de vocabulario—, que es el territorio de las reglas.

- **D-09:** `exencion_contra: calificacion_final` **sin** segundo nivel es **aviso de R1**, no
  error. Ahí el promedio *es* la calificación final, así que aritméticamente no está mal: solo está
  dicho de una forma que se volverá falsa el día que el curso añada el segundo nivel. El aviso lo
  señala sin bloquear. REQ-48 intacto: ningún curso de control declara la clave.

- **D-10 (derivada, y quita trabajo a la Fase 13):** **el renderizador no cambia nunca por esta
  clave.** `config/politicas.yaml:98-103` ya rinde «obtener un **promedio** igual o mayor a
  {exencion}», y como `calificacion_final` es siempre error (D-08), un curso válido tiene siempre
  `exencion_contra: promedio`. El texto que ya se imprime es el único que puede ser cierto.

### R1 — qué comprueba y dónde

- **D-11:** Las comprobaciones nuevas van **dentro de `regla_1`**, después de los rubros duplicados
  y **antes** del bloque de `esquema_id` (`validar.py:154`).

  **Medido:** `regla_1` tiene dos salidas tempranas —`return` si el curso no declara rubros
  (`:130`) y `return` si `esquema_id` no existe en el catálogo (`:160`)—. Puestas al final, un curso
  con el `esquema_id` mal escrito **no recibiría** las comprobaciones del segundo nivel, y ese es
  justo el perfil del curso de Zurisaddai, que sí declara `esquema_id`.

  Se descartó un método auxiliar: la prueba `test_el_codigo_de_r1_no_menciona_la_unidad_de_ningun_rubro`
  (`test_validar.py:287-292`) solo lee el fuente de `regla_1`, así que sacar la aritmética a un
  helper haría que **la guarda dejara de cubrirla en silencio**, sin que nada fallara. Se descartó
  una regla propia (R9) por cambiar el número de reglas del proyecto, obligar a reescribir
  AGENTS.md §«las ocho reglas» y hacer que el informe de cursos sin segundo nivel mencionara una
  regla que no aplica — riesgo directo contra REQ-48.

- **D-12:** La suma se comprueba contra **`reglas["suma_exacta"]`** de
  `config/esquemas-evaluacion.yaml:105`, el mismo número que ya gobierna la suma de los rubros, con
  el mismo `round(..., 2)` que usa el resto de `validar.py`. Un solo sitio donde vive el 100 del
  proyecto. Se descartó una clave nueva en el config (abre una divergencia que el Estatuto no
  contempla) y se descartó un 100 literal (el mismo número en dos sitios con dos naturalezas).

- **D-13:** Un segundo nivel de **100/0 o 0/100 es aviso de R1**, no error. Suma 100, así que no hay
  defecto aritmético, pero declarar 100/0 es decir «no hay segundo nivel» por el camino largo y
  0/100 es decir que las metas del curso no valen nada. Se señala sin bloquear porque puede ser
  deliberado.

- **D-14:** El contraste contra el catálogo (`validar.py:155-169`) se amplía al segundo nivel y
  compara **porcentajes y etiquetas**, emitiendo **aviso** como el de los rubros.

  Es una divergencia deliberada respecto al trato de los rubros, donde `etiqueta` y `detalle` quedan
  fuera del contraste: aquí el catálogo pasa a ser también la redacción canónica del esquema. La
  consecuencia está medida y aceptada en D-18.

  Este contraste **se queda donde ya vive el de los rubros**, dentro del `if self.c.esquema_id:`.
  No es el mismo sitio que D-11 y no tiene por qué serlo.

- **D-15 — restricción dura sobre los nombres de campo.**
  `test_el_codigo_de_r1_no_menciona_la_unidad_de_ningun_rubro` afirma que el fuente de `regla_1` no
  contiene `.base`, `a_porcentaje`, `.unidad`, `.total` ni `.valor`. Los nombres elegidos en D-03
  —`porcentaje`, `etiqueta`, `promedio`, `ordinario`— **no chocan con ninguno**, y `porcentaje` ya
  lo usa R1 hoy con los rubros. Si el planeador renombra algo, comprueba esto antes: un campo
  llamado `valor` rompe esa prueba sin que haya nada mal.

### Cierre y no contaminación (REQ-48)

- **D-16:** El `MANIFIESTO.yaml` registra `segundo_nivel` y `exencion_contra` en su bloque
  `evaluacion:` (`generar.py:177-181`) **solo cuando el curso los declara**. Los dos cursos de
  control no los declaran, así que su manifiesto no cambia ni un byte y D-27 de la Fase 9 —la forma
  del manifiesto entra en la huella— queda respetada. Sirve a la Restricción 4 del PROJECT.md: cada
  salida registra su esquema.

  Se descartó no registrarlo, aunque hay precedente (la Fase 9 no llevó allí `unidad:` ni `total:`),
  porque un DI de 38985 generado no dejaría rastro de que se calificó a dos niveles. Ese precedente
  queda como idea diferida, no adoptado.

- **D-17:** La clase **`NoContaminacion`** de `pruebas/test_validar.py:691-724` **se extiende**, no
  se duplica:
  - `test_los_cursos_de_control_no_declaran_nada_de_la_v2` añade `segundo_nivel:` y
    `exencion_contra:` a su lista de ausencias.
  - El silencio de **R1** sobre los cursos de control se fija igual que ya se fija el de R2 y R3.

  **Línea base medida antes de planear, para que la prueba no se escriba a ojo:** hoy 39056, 39062 y
  38985 emiten **cero hallazgos de R1** y los tres son válidos. 39056 y 39062 tienen 5 hallazgos en
  total (los cinco recordatorios IEDI de D-15 de la Fase 10); 38985 tiene 9.

  Se descartó una prueba hermana propia —cuatro pruebas casi idénticas al cerrar el milestone— y se
  descartó dejarlo solo para `huella verificar`, que tarda hasta el cierre en ver una regresión.

- **D-18 — 38985 no se toca, y su aviso nuevo se acepta.** Con D-05 y D-14, ese curso —que declara
  `esquema_id: zra-contabilidad` y **no** declara segundo nivel— pasará de **9 hallazgos a 10**: un
  aviso de R1 por diferir del catálogo. Seguirá siendo válido.

  Se acepta a propósito. D-13 de la Fase 10 blindó ese archivo hasta la Fase 14, su huella no se
  vigila (D-22 de la Fase 9), y el aviso **dice la verdad**: ese `curso.yaml` está traducido y le
  falta el segundo nivel. Es el recordatorio automático de la deuda que la Fase 14 cierra.

  Se descartó quitarle el `esquema_id` (toca el archivo blindado y pierde el contraste que hoy sí
  vale para sus rubros) y se descartó declararle el segundo nivel ya (le come a la Fase 14 parte de
  su criterio 1, que es su prueba de fuego).

- **D-19:** El curso de prueba son **variantes de `CURSO_VALIDO` por `deepcopy`**, con los helpers
  `curso(**cambios)` / `informe(**cambios)` que ya existen (`test_validar.py:104-112`). El rasgo es
  aditivo y ortogonal a los rubros: no hace falta un curso base distinto. Se descartó un
  `CURSO_CON_SEGUNDO_NIVEL` hermano de `CURSO_CON_EXAMENES_EN_COMPONENTES` por ser otro curso base
  que mantener al día. Sigue vigente D-12 de la Fase 10: nada de esto vive en `cursos/`.

- **D-20 (heredada):** El cierre de REQ-48 es **`python src/huella.py verificar` a mano**,
  conservando D-18 de la Fase 9 y D-14 de la Fase 10 — la huella no cuelga del ciclo unitario, que
  hoy es rápido y no depende de las plantillas.

- **D-21 (derivada, medida):** **`grafo.py` no se toca.** Lee `m.rubro` y `m.valor` por meta
  (`grafo.py:299`) y no abre el bloque de evaluación en ningún punto. La parte de REQ-48 que habla
  de la forma de `grafo/` se cumple por construcción, no por cuidado.

### Criterio de Claude

- La redacción concreta de los mensajes nuevos de R1, siguiendo el estilo de los existentes: decir
  qué falta y con qué valores. El de D-08 tiene una exigencia de fondo —«explicar la diferencia»
  entre medir contra el promedio y medir contra la nota final— pero su texto es libre.
- Los nombres exactos de `Nivel` y `SegundoNivel`, sujetos a D-15.
- Si el aviso de D-13 distingue el caso 100/0 del 0/100 con mensajes distintos o usa uno solo.
- Si el aviso del contraste de D-14 se emite junto al de los rubros o como hallazgo aparte.
- El orden de los planes de la fase y en cuál se actualiza AGENTS.md.

</decisions>

<canonical_refs>
## Referencias canónicas

**Los agentes de investigación y planeación DEBEN leerlas antes de planear o implementar.**

### Requisitos y encuadre
- `.planning/REQUIREMENTS.md` — REQ-41 (segundo nivel), REQ-46 (R1 con segundo nivel y la exención
  contra el promedio), REQ-48 (no contaminación), REQ-26 (el renderizador no inventa).
- `.planning/ROADMAP.md` §«Fase 11» — meta, dependencias y los cuatro criterios de éxito.
- `.planning/phases/09-valor-de-una-meta/09-CONTEXT.md` — D-03 (vocabulario cerrado →
  `ErrorModelo`), D-05 (se declara, no se infiere), D-17 (defectos de identidad como hallazgo de
  regla), D-22 (38985 fuera de la huella), D-26 (`tipo` obligatorio sin default), D-27 (la forma del
  `MANIFIESTO.yaml` entra en la huella). Los seis se citan arriba.
- `.planning/phases/10-reglas-en-la-unidad-declarada/10-CONTEXT.md` — **de lectura obligada.** D-12
  (fixtures de diccionario, nada en `cursos/`), D-13 (38985 blindado hasta la Fase 14), D-14 y D-15
  (el cierre a mano y la línea base medida).
- `conocimiento/ejemplos/531-contabilidad-financiera-2026-1.md` §«Estructura de la calificación»
  (líneas 46-71) — **la fuente de los rótulos literales de D-02 y D-05.** La tabla 1 del DI de
  origen, con sus tres filas.

### El contrato y el modelo
- `AGENTS.md` §«Contrato de `curso.yaml`» — **se actualiza en el mismo plan que añada las claves.**
- `AGENTS.md` §«Las ocho reglas de validación (`src/validar.py`)» — **R1 cambia de comportamiento,
  así que esta sección se actualiza en el mismo plan.**
- `AGENTS.md` §«Reglas invariables» — no negociables del proyecto.
- `src/modelo.py:188-229` (`Rubro`, el patrón de dataclass con `__post_init__` que D-03 sigue),
  `:271-333` (`Curso`, donde entra `segundo_nivel`), `:395-405` (la carga desde el YAML, donde
  entran las dos claves nuevas).
- `config/esquemas-evaluacion.yaml:59-82` (`zra-contabilidad`, que D-05 amplía y cuyo comentario de
  las líneas 66-68 se corrige) y `:103-108` (`reglas`, con el `suma_exacta` de D-12).

### La regla
- `src/validar.py:126-169` — `regla_1` entera: las dos salidas tempranas de D-11 (`:130`, `:160`),
  el umbral de exención (`:145-152`) y el contraste contra el catálogo que D-14 amplía (`:155-169`).
- `config/politicas.yaml:98-103` — el criterio `exencion`, cuya plantilla ya dice «promedio». Es la
  base de D-10: **no se toca en esta fase.**

### Pruebas que condicionan el trabajo
- `pruebas/test_validar.py:287-292` — `test_el_codigo_de_r1_no_menciona_la_unidad_de_ningun_rubro`,
  la guarda de D-11 y D-15.
- `pruebas/test_validar.py:281-285` —
  `test_poner_un_rubro_en_puntos_no_altera_lo_que_r1_comprueba`, que fija la insensibilidad de R1 a
  la unidad y no debe romperse.
- `pruebas/test_validar.py:691-724` — la clase `NoContaminacion` que D-17 extiende.
- `pruebas/test_validar.py:104-112` — los helpers `curso()` / `informe()` que D-19 reutiliza.

### Cierre
- `src/huella.py` — `verificar` / `registrar`. En esta fase **solo `verificar`**: nada debe cambiar.
- `pruebas/huellas.yaml` — la línea base de los cuatro documentos de control.
- `src/generar.py:177-181` — el bloque `evaluacion:` del `MANIFIESTO.yaml` que D-16 amplía.

</canonical_refs>

<code_context>
## Lo que ya existe

### Reutilizable — no se reimplementa
- **El patrón de dataclass con `__post_init__`** de `Rubro` (`modelo.py:198-215`): valida su propia
  forma al construirse y levanta `ErrorModelo` con un mensaje que explica qué falta y por qué. D-03
  y D-07 lo siguen.
- **`Validador.error()` / `.aviso()`** (`validar.py:118-122`) — el canal de hallazgos. Los cuatro
  mensajes nuevos (D-08, D-09, D-13, D-14) entran por ahí.
- **`reglas["suma_exacta"]`** (`validar.py:127`, ya cargado al principio de `regla_1`) — D-12 lo
  reutiliza sin leer nada nuevo del config.
- **El contraste `catalogo != propio`** (`validar.py:161-169`) — D-14 lo amplía; su forma de emitir
  aviso y su redacción son el molde.
- **Los helpers de fixture de `test_validar.py`** (`:104-112`) — D-19 los extiende.

### Patrones establecidos que acotan el trabajo
- Los defectos de **esquema y vocabulario** son `ErrorModelo` al cargar; los de **aritmética,
  identidad y semántica** son hallazgos de regla. D-07 cae del primer lado, D-08 del segundo.
- Los vocabularios son **cerrados** y un valor fuera de la lista es `ErrorModelo` (D-03/D-08 de la
  Fase 9). D-06 declara el suyo con dos valores, uno de los cuales R1 rechaza.
- `validar.py` redondea a 2 decimales y compara por igualdad exacta. D-12 se apoya en eso.
- Un rasgo nuevo del contrato **no cambia nada si el curso no lo declara**. En esta fase eso se
  concentra en `Curso.segundo_nivel is None` (D-03).

### Puntos de integración
- `Curso` (`modelo.py:271-333`) — donde entra `segundo_nivel` y `exencion_contra`, junto a
  `exencion_ordinario` que ya vive ahí (`:288`).
- `modelo.cargar` (`:395-405`) — donde se leen las dos claves del bloque `evaluacion:`.
- `_Validador.regla_1` (`validar.py:126-169`) — el único consumidor de esta fase. `regla_2` y
  `regla_3` **no se tocan**.
- `src/generar.py:177-181` — el bloque `evaluacion:` del manifiesto (D-16).

### Lo que NO se toca, y por qué está escrito aquí
- **`src/render_docx.py`** — la tabla de los dos niveles es la Fase 13. Y por D-10, la plantilla de
  exención de `politicas.yaml` no necesita cambiar **nunca** por `exencion_contra`.
- **`src/grafo.py`** — D-21, medido: no abre el bloque de evaluación.
- **`cursos/2026-2/38985-.../curso.yaml`** — D-18, blindado hasta la Fase 14.
- **R2 y R3** — la Fase 10 las cerró; el segundo nivel no cambia lo que aporta una meta a un rubro.

</code_context>

<specifics>
## Ideas concretas de la discusión

- **La forma «par fijo» ganó por un argumento de regla, no de estética.** Una lista genérica obliga
  a R1 a buscar por id cuál de las filas es el promedio antes de poder aplicar el criterio 3. El par
  con claves nombradas hace que esa pregunta no exista.

- **El aparente choque entre el criterio 3 y D-03 de la Fase 9 se disolvió al mirarlo de cerca.**
  D-03 habla de valores que el modelo *no conoce*; `calificacion_final` es un valor conocido y
  prohibido. Son dos categorías distintas de defecto y el proyecto ya las trata distinto desde D-17.
  El vocabulario tiene que admitir el valor malo justamente para que R1 pueda explicarlo — un
  vocabulario de un solo valor convertiría el mensaje pedagógico del criterio 3 en un «valor
  inválido» sin contenido.

- **La obligatoriedad de `exencion_contra` con segundo nivel obligó a que el campo no tenga
  default.** Es una consecuencia que solo se ve al escribirla: `= "promedio"` haría indistinguibles
  «ausente» y «declarado», y la obligatoriedad se volvería incomprobable. El campo queda `= ""` y el
  valor efectivo se lee como `exencion_contra or "promedio"`.

- **Las dos salidas tempranas de `regla_1` decidieron dónde va el código.** Puesto al final, un
  `esquema_id` mal escrito se saltaría toda la comprobación del segundo nivel — y el curso que
  motiva la fase es precisamente uno que declara `esquema_id`.

- **La prueba `getsource` de la Fase 10 resultó ser también una trampa para esta fase.** Sacar la
  aritmética nueva a un método auxiliar no rompería nada: simplemente dejaría de estar vigilada, en
  silencio. Por eso D-11 la mantiene dentro de `regla_1` en vez de refactorizar.

- **El coste de D-14 sobre 38985 se midió antes de aceptarlo.** No es «probablemente saldrá un
  aviso»: hoy ese curso emite 9 hallazgos y cero de R1, y tras esta fase emitirá 10 y uno de R1,
  siguiendo válido. Se acepta porque el aviso dice la verdad sobre un archivo que está a propósito
  traducido.

- **`grafo.py` y el renderizador salieron de la fase por medición, no por supuesto.** El primero no
  abre el bloque de evaluación; el segundo ya imprime la única frase que puede ser cierta.

</specifics>

<deferred>
## Ideas apartadas

- **Registrar `unidad:` y `total:` del rubro en el `MANIFIESTO.yaml`.** Es una omisión real de la
  Fase 9: el rubro ganó las dos claves pero el manifiesto sigue escribiendo solo
  `{"id", "porcentaje"}`. Ningún curso de control está en puntos, así que arreglarlo no tocaría la
  huella. Se ofreció junto a D-16 y **no se adoptó**: es trabajo fuera de los requisitos de esta
  fase. Candidato natural para la Fase 13, que es la que lleva los puntos al documento.

- **Una lista abierta `niveles:` en vez del par fijo.** Descartada en D-01. Vuelve a ser pertinente
  solo si aparece un esquema con un tercer sumando, cosa que el Estatuto no contempla hoy.

- **Que R1 juzgue si el umbral de exención tiene sentido dado el peso del ordinario** —por ejemplo,
  advertir cuando exentar sea aritméticamente casi imposible—. No se planteó como decisión porque
  ningún requisito lo pide; se anota por si alguna vez se quiere.

- **Una tolerancia numérica declarada en `config/esquemas-evaluacion.yaml`.** La Fase 10 la descartó
  en su D-06 y señaló el segundo nivel como candidato a reabrirla. **Medido aquí: no hace falta.**
  Los dos porcentajes son enteros declarados y su suma no acumula error; D-12 usa el `round(..., 2)`
  existente. Queda cerrada también para esta fase.

- **El prefijo `M0_` del recurso «Foro de presentación» de Big Data** y **los `MANIFIESTO.yaml` de
  los cursos de control que dejaron de listar los `.pdf`.** Los dos siguen abiertos desde la Fase 9
  y ninguno es de esta fase.

- **`/di-pua` sobre el PUA de 38985.** Fuera del roadmap, pendiente de que el usuario deje el PDF en
  `puas/fuente/`. No bloquea esta fase; la Fase 14 sale más completa con él.

</deferred>

---

*Fase: 11-segundo-nivel-de-la-calificacion*
*Contexto recogido: 2026-08-06*
