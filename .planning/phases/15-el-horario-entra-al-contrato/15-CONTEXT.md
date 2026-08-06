# Fase 15: El horario entra al contrato — Contexto

**Recogido:** 2026-08-06
**Estado:** Listo para planear

<domain>
## Frontera de la fase

Un grupo puede declarar **a qué hora** tiene clase cada día y cuáles de esas sesiones son
virtuales, y los cuatro grupos del repositorio dicen por fin la verdad sobre sus días. El horario
del semestre es un dato del semestre: qué grupos van y en qué días cambia cada ciclo, y el contrato
tiene que saber decirlo sin que el código lo adivine.

**Dentro:** `curso.yaml` → `modelo.py` → `validar.py` → `generar.py`/`grafo.py`, la resolución de
fechas, los cuatro `curso.yaml` de control, `pruebas/huellas.yaml` re-registrada a propósito, y
`AGENTS.md` §«Contrato de `curso.yaml`».

**Fuera:** la exportación `.ics` (Fase 16), `render_docx.py` y las plantillas —D-08 deja el `.docx`
sin tocar salvo por las fechas que ya calcula—, el `curso.yaml` de 38985 (no declara bloques y no se
edita), y la materia 932, que está en el horario y no tiene `curso.yaml`.

</domain>

<decisions>
## Decisiones cerradas

### La forma del horario en el contrato

- **D-01 — El bloque es la unidad; `dias_presencial` se deriva.** `Horario` gana
  `bloques: list[Bloque]`, cada uno con día, hora de inicio, hora de fin y ambiente.
  `dias_presencial` deja de escribirse a mano cuando hay bloques: sale de los presenciales, ordenado.

  ```yaml
  grupos:
    - numero: "961"
      horario:
        bloques:
          - {dia: 0, inicio: "12:00", fin: "13:00", ambiente: presencial}
          - {dia: 1, inicio: "12:00", fin: "13:00", ambiente: presencial}
          - {dia: 1, inicio: "16:00", fin: "17:00", ambiente: presencial}
          - {dia: 2, inicio: "11:00", fin: "13:00", ambiente: presencial}
        dia_entrega: 5
        hora_entrega: "23:59"
        aula: "Laboratorio de cómputo"
  ```

  El bloque es lo único que sabe expresar los dos martes de 961 —12:00–13:00 y 16:00–17:00— y el
  martes virtual de 971, que no es día presencial. Una lista de días no puede con ninguno de los dos.
  **El rasgo es aditivo:** un grupo que solo declare `dias_presencial`, como los cuatro de hoy y el
  531 de Contabilidad, sigue cargando sin `ErrorModelo` y con el comportamiento actual intacto.

- **D-02 — Declarar `bloques` y `dias_presencial` a la vez es `ErrorModelo`.** El contrato no admite
  dos verdades sobre el mismo hecho. Es el trato que D-01 de la Fase 12 dio a `meta`/`rubro` en la
  rúbrica: «declara exactamente uno». El mensaje dice cuál sobra. Ningún curso existente los tiene
  juntos, así que la regla nace sin deuda.

- **D-03 — `ambiente: presencial | virtual`, reusando `AMBIENTES`.** Un solo vocabulario en todo el
  proyecto, ya validado en `modelo.py` y ya en uso en `Sesion.ambiente`. Se acepta a sabiendas la
  ambigüedad que introduce —«virtual» significa tramo asincrónico de una meta *y* bloque con hora sin
  aula— y se resuelve nombrando el tipo, no el valor: un `Bloque` no es una `Sesion`. D-08 fija que
  no interactúan.

- **D-04 — Los bloques entran al `MANIFIESTO.yaml` y al grafo.** `generar.py:227` ya escribe
  `dias_presencial` en el manifiesto y `grafo.py:274` en el nodo del grupo. Si el horario es parte
  del contrato, es parte del rastro. El cambio de forma del manifiesto —que la huella vigila por
  D-27 de la Fase 9— suma al cambio deliberado de REQ-52, que de todos modos se re-registra.

- **D-05 — El tercer error de validación es el solapamiento.** El criterio 3 del roadmap pide tres
  errores. Dos siguen en pie: **hora mal formada** y **fin anterior al inicio**. El tercero que ese
  criterio enunciaba —«un día declarado con hora no está en `dias_presencial`»— queda **imposible**
  por D-01: el derivado sale de los bloques y no hay dos listas que puedan discrepar. Se reemplaza
  por **bloques que se solapan el mismo día**, que es la incoherencia real que sobrevive: un grupo
  no puede estar en dos clases a la vez. Los dos martes de 961 no se solapan, así que el caso real
  ejercita el camino feliz y la prueba que falla a propósito usa un fixture.

### Qué día fija la fecha

- **D-06 — El primer día presencial de la semana, y `Sesion.dia` como escape declarado.**
  `resolver_fechas` (`modelo.py:528`) ya hace exactamente esto con `dias_presencial[0]`. Con el
  derivado ordenado, la regla deja de ser un accidente heredado para ser una decisión escrita, y no
  cuesta una línea de código nuevo en la resolución de fechas. `Sesion.dia` ya existe en el modelo
  (`modelo.py:139`) y **ningún `curso.yaml` lo usa**: queda como la salida para la sesión que deba
  caer en otro día, con validación de que ese día tenga bloque presencial.

  **Medido antes de decidir:** los dos cursos declaran **exactamente una sesión presencial por
  semana**, las 16 semanas. La pregunta nunca fue cómo repartir varias sesiones entre varios días
  —era cuál de los días reales se lleva la única que hay.

  **Restricción que hereda quien planee:** las sesiones son compartidas por todos los grupos del
  curso (`modelo.py:523`), así que un `dia:` fijo en la sesión ataría 961 y 962 al mismo día. Por eso
  es escape y no mecanismo principal.

- **D-07 — Una suspensión recorre al siguiente día **con bloque presencial**.** Hoy
  `calendario.fecha_de` (`calendario.py:169`) recorre al día siguiente hábil sin mirar el horario.
  Eso no se notaba porque los cuatro grupos decían martes o jueves y ninguna suspensión caía ahí.
  Con los días reales sí cae, y dos de los tres grupos activos imprimirían «En clase / sesión
  síncrona» en un día sin aula:

  | Grupo | Día nuevo | Suspensión | Hoy recorre a | ¿Hay salón? |
  |---|---|---|---|---|
  | 39056·961 | lunes | 2 nov, 16 nov | martes 3 y 17 nov | **Sí** — martes es salón |
  | 39062·971 | lunes | 2 nov, 16 nov | martes 3 y 17 nov | **No** — martes es virtual |
  | 39062·972 | miércoles | 16 sep | jueves 17 sep | **No** — 972 no tiene jueves |

  Recorrer a un día con bloque presencial usa exactamente el dato que esta fase acaba de meter al
  contrato. **Un grupo sin bloques conserva el comportamiento de hoy, intacto** — eso protege al 531
  de Contabilidad y a cualquier curso futuro que no declare horario.

- **D-08 — El bloque virtual no toca el `.docx`.** La sesión `ambiente: virtual` del DI sigue
  cayendo en `dia_entrega` (sábado) y sigue imprimiéndose «antes del sábado …». REQ-51 lo dice
  literal —«las entregas siguen venciendo el sábado al final del día»— y el criterio 2 del roadmap
  pide que un grupo con bloque virtual produzca las mismas fechas que sin él. El bloque virtual entra
  al contrato, al manifiesto y al grafo (D-04), y la Fase 16 lo exporta al `.ics`. **Ninguna huella
  cambia por este motivo**, y `render_docx.py` no se toca.

### El grupo que este semestre no se imparte

- **D-09 — `imparte: false` en el grupo, por defecto `true`.** Un booleano explícito, hermano de
  `plataforma:` y `jefe_grupo:`. Cada ciclo se voltea la bandera de los grupos que no van y se
  conservan sus datos —aula, plataforma, número— para cuando vuelvan. Es la traducción directa del
  enunciado del milestone: el horario del semestre decide quién va, y el `curso.yaml` lo declara en
  vez de que el código lo adivine.

  **Se descartó inferirlo de la ausencia de bloques.** Choca de frente con el criterio 1: un grupo
  que solo declare `dias_presencial` tiene que seguir cargando y generando, así que el silencio
  significaría dos cosas distintas.

- **D-10 — 962 conserva su horario y su huella, y se sigue generando.** No hay día real con qué
  sustituir su `dias_presencial: [3]`, así que **no se toca** y su documento sale byte por byte
  igual. Eso convierte al 962 en el **testigo de que la excepción de REQ-52 está acotada**: tres
  huellas se mueven a propósito, una no se mueve en absoluto. Retirarlo de `pruebas/huellas.yaml`
  gastaría ese testigo.

- **D-12 — Una bandera del generador para los no impartidos.** `generar.py` salta por defecto los
  grupos con `imparte: false`; la bandera —`--incluir-no-impartidos` o equivalente— los incluye. La
  suite de huellas la pasa siempre, así que 962 sigue siendo documento de control sin que nadie lo
  genere por accidente al preparar el semestre. El manifiesto declara qué grupos se saltaron y por qué.

- **D-13 — El relleno del 962 se explica en un comentario YAML, no en `avisos:`.** El porqué del
  jueves heredado va como comentario `#` junto al horario del 962, donde lo lee quien edite el
  archivo.

  **La razón es medida, no estética.** `Curso.avisos` no se imprime en el `.docx`, pero sí entra al
  informe de validación (`validar.py:629`), y la huella hashea ese informe — que además **es por
  curso, compartido entre los grupos** (`huella.py:50`). Meterlo en `avisos:` de 39056 movería el
  hash `informe` del 962 y le quitaría a D-10 uno de sus tres campos intactos. El comentario no se
  carga, no entra al informe y no mueve ningún hash.

### La medición del cambio de huella (REQ-52)

- **D-11 — Un informe en el directorio de la fase.** Un `.md` junto a los planes, con la tabla fecha
  por fecha y documento por documento, escrito **antes** de correr `huella registrar`. Es el
  precedente de la Fase 9, que midió su criterio 3 revirtiendo el texto y comparando shas en vez de
  inspeccionar. Queda en git, es revisable, y el mensaje del commit de re-registro lo referencia.

- **D-14 — El re-registro va en commit propio, y el alcance está acotado a tres documentos.** El
  cambio de días mueve 961 (martes→lunes), 971 (martes→lunes) y 972 (jueves→miércoles). 962 no se
  mueve (D-10). El mensaje del commit dice que el cambio es deliberado y por qué, como pide el
  criterio 4.

### Lo que la investigación destapó (decidido el 2026-08-06, después del RESEARCH)

- **D-15 — El recorrido de D-07 se acota a la semana, y el silencio se vuelve ruido.** La
  investigación midió que D-07 **no tiene solución** para 971 (semanas 13 y 15) ni para 972
  (semana 6): esas semanas el grupo no tiene ningún día con bloque presencial, porque la suspensión
  cae justo sobre su único día. Un recorrido sin límite aterriza una semana después —9 nov, 23 nov,
  23 sep— y la fila «semana 13» del documento imprimiría una fecha de la semana 14.

  El recorrido **se detiene al terminar la semana**. No inventa fecha fuera de ella. Y una
  comprobación nueva de `validar.py` reporta el caso: «semana N: el grupo G no tiene ningún día con
  bloque presencial (D suspendido)». Quien planee decide qué fecha conserva la celda —lo natural es
  la del día suspendido—, pero **el hallazgo es obligatorio**: el generador nunca imprime en
  silencio una fecha que el grupo no tiene.

  **Por qué esta comprobación sí corre, y la del HALLAZGO 1 no.** El RESEARCH midió que
  `generar.paquete()` valida (`generar.py:293`) *antes* de que `render_docx` resuelva fechas
  (`render_docx.py:689`), así que ninguna regla que dependa de fechas resueltas se dispara en el
  pipeline real. Esta no depende de ellas: «¿tiene este grupo algún día con bloque presencial en
  una semana con suspensión?» se computa con **horario + calendario** y nada más. Quien planee debe
  escribirla así, sin resolver sesiones.

  **Se descartó recorrer al bloque virtual.** Contradice D-08 —el bloque virtual no toca el
  `.docx`— y de todos modos no salva a 972: su martes virtual es *anterior* al miércoles suspendido.

- **D-16 — El `manifiesto` de 962 se mueve, y el informe lo declara campo por campo.** La
  investigación verificó que `MANIFIESTO.yaml` es un archivo **por curso, no por grupo**
  (`generar.py:142`, itera `curso.grupos` completo en la 232) y que `huella.py` computa su hash una
  vez por curso (`:147`) y lo aplica a todos sus grupos (`:171`). Meter `bloques` al manifiesto de
  961 (D-04) mueve por acoplamiento el campo `manifiesto` de 962.

  **D-10 se mantiene, con la precisión que el código permite:** el `.docx` de 962 sale byte por byte
  igual —`texto_docx` intacto— y su `informe` tampoco se mueve. Lo que cambia es solo `manifiesto`.
  962 sigue siendo el testigo de que la excepción de REQ-52 está acotada; el testimonio es de dos
  campos de tres, no de tres de tres.

  **Consecuencias operativas que quien planee no debe redescubrir:**
  - `python src/huella.py verificar` reportará **cuatro** líneas con `!` después de editar los
    `curso.yaml`, no tres. El informe de D-11 tiene que anticiparlo o alguien lo leerá como un
    defecto de implementación.
  - El informe de D-11 se escribe **campo por campo** —`texto_docx`, `informe`, `manifiesto`— para
    los cuatro documentos, no documento por documento. Es la única forma de que la tabla distinga
    los tres cambios deliberados del cuarto acoplado.
  - El mensaje del commit de D-14 se redacta con esa precisión desde el inicio: no puede prometer
    que una huella no se movió cuando uno de sus tres campos sí lo hizo.

  **Se descartó sacar `bloques` del manifiesto** (revertiría D-04 y dejaría el horario fuera del
  rastro) **y separar el manifiesto por grupo** (cambia un diseño de trazabilidad que las cinco
  fases anteriores de la v2.0 dieron por estable, y movería el hash de los cuatro grupos igual).

### Discreción acotada

- La redacción exacta de los mensajes de error, siguiendo el estilo de los hallazgos existentes.
- Los nombres de campo dentro del bloque (`dia`/`inicio`/`fin`) mientras respeten D-01 y D-03.
- Si la hora se guarda como cadena `"HH:MM"` o como `datetime.time` en el modelo.
- Dónde vive la lógica de «siguiente día con bloque presencial» de D-07: `resolver_fechas`, que sí
  conoce el grupo, o un método nuevo del calendario. `fecha_de(semana, dia)` hoy no conoce el grupo.
- El nombre exacto de la bandera de D-12.
- El reparto en olas y el orden de los planes, respetando que la línea base se mide antes de tocar
  los `curso.yaml` de control.

</decisions>

<canonical_refs>
## Referencias canónicas

**Los agentes de investigación y planeación deben leer esto antes de trabajar.**

### Lo que la fase promete
- `.planning/ROADMAP.md` §«Fase 15: El horario entra al contrato» — los seis criterios de éxito. Ojo:
  el tercer error del criterio 3 quedó reemplazado por D-05, razonado arriba.
- `.planning/REQUIREMENTS.md` §«v2.1 — El horario real del semestre» — REQ-50, REQ-51, REQ-52 y el
  enunciado «el horario es un dato del semestre».

### La fuente del horario
- `horarios/2026-2.md` — la transcripción de la carga académica 2026-2. **Días y horas se consideran
  leídos con confianza**; los salones están pendientes de confirmar y no importan aquí (el horario no
  registra salón por decisión del 2026-08-06; el aula la declara el grupo). Es **referencia**, no una
  fuente que el código cargue: si discrepa de un `curso.yaml`, manda el `curso.yaml`.
- `calendarios/2026-2.yaml` — inicio 10 ago, fin 28 nov, 16 semanas, tres suspensiones
  (16 sep miércoles · 2 nov lunes · 16 nov lunes).

### Precedentes que esta fase reusa
- `.planning/phases/09-valor-de-una-meta/09-CONTEXT.md` — D-14/D-15/D-24 son el precedente del cambio
  de huella deliberado y del orden de pasos que lo hace defendible; D-27 fija los tres hashes que
  componen una huella (`texto_docx`, `informe`, `manifiesto`).
- `.planning/phases/12-la-rubrica-en-el-contrato/12-CONTEXT.md` — D-01 «declara exactamente uno» es
  el patrón que D-02 reusa; D-04 es la línea entre `ErrorModelo` (forma) y hallazgo de regla
  (significado), que esta fase mantiene.

### Lo que hay que actualizar
- `AGENTS.md` §«Contrato de `curso.yaml`» — tiene que listar `bloques:` e `imparte:`. Está en deuda
  desde la Fase 9: todavía no lista `componentes:` en las metas ni `unidad`/`total` en los rubros.
  Esta fase toca el contrato, así que le toca cerrar también eso o declarar por qué no.

</canonical_refs>

<code_context>
## Lo que ya existe

### Se reusa
- **`Sesion.dia: int | None`** (`modelo.py:139`) — la puerta de D-06 ya está abierta y sin usar por
  ningún `curso.yaml`. No hay que inventarla.
- **`AMBIENTES`** (`modelo.py:142`) — la lista de valores válidos que D-03 reusa.
- **`resolver_fechas`** (`modelo.py:516`) — ya toma `dias_presencial[0]`. D-06 no cambia la regla,
  la documenta; D-07 sí le añade el filtro por bloque presencial.
- **`src/huella.py`** — el instrumento de REQ-48 que la Fase 9 construyó. D-11 y D-14 lo usan tal
  cual; no necesita modo diff.

### Consumidores de `dias_presencial` que hay que revisar
- `generar.py:227` — lo escribe en el `MANIFIESTO.yaml`. D-04 le añade los bloques.
- `grafo.py:274` — lo escribe en el nodo del grupo. D-04 le añade los bloques.
- Si el derivado de D-01 se expone como propiedad que devuelve `list[int]`, los dos siguen leyendo
  sin cambiar de forma. Es la ruta de menor fricción, no una decisión cerrada.

### Trampas medidas
- **`calendario.fecha_de`** (`calendario.py:161`) recorre una suspensión al día siguiente sin mirar
  el horario, y no conoce el grupo. Es la trampa que D-07 desactiva.
- **El informe de validación es por curso, no por grupo** (`huella.py:50`), así que cualquier
  hallazgo nuevo mueve el hash `informe` de **todos** los grupos del curso. Es lo que forzó D-13.
- **`avisos:` no se renderiza** en el `.docx` —`render_docx.py` no lo lee— pero sí entra al informe
  (`validar.py:629`). Un aviso no es gratis.
- **`_rotulo_sesion`** (`render_docx.py:546`) es el único punto que distingue presencial de virtual
  en el documento. D-08 lo deja intacto a propósito.

</code_context>

<specifics>
## Hechos medidos que la planeación no debe volver a deducir

- **Una sesión presencial por semana, las 16, en los dos cursos.** 39056 y 39062 declaran
  exactamente una `ambiente: presencial` por semana. 961 tiene **cuatro bloques reales** de clase a
  la semana y su DI instruye una sola sesión.
- **El cambio de días, grupo por grupo:**

  | Grupo | Declarado hoy | Según el horario | Efecto |
  |---|---|---|---|
  | 39056·961 | `[1]` martes | lun 12–13, mar 12–13, mar 16–17, mié 11–13 · salón | primer día → **lunes** |
  | 39056·962 | `[3]` jueves | **no se imparte este semestre** | `imparte: false`, sin cambio |
  | 39062·971 | `[1]` martes | lun 10–12 salón · mar 17–19 virtual | primer día → **lunes** |
  | 39062·972 | `[3]` jueves | mar 10–12 virtual · mié 18–19 salón | primer día → **miércoles** |

- **Las tres suspensiones caen en miércoles 16 sep, lunes 2 nov y lunes 16 nov** — es decir, sobre
  los días nuevos de los tres grupos activos. Antes no pegaban a ninguno.

</specifics>

<deferred>
## Diferido expresamente

- **El DI de 961 instruye una sesión presencial a la semana y el grupo tiene cuatro bloques de
  clase.** Reescribir las 16 metas para que instruyan las cuatro sesiones es decisión pedagógica del
  profesor sobre el contenido, no del generador, y reharía el `curso.yaml` entero.
- **Análisis de Procesos y Datos de Negocios (932)** — está en el horario, no tiene `curso.yaml`, y
  le falta PUA y esquema de evaluación. Fuera de esta fase. La Fase 16 ya lleva criterio propio (5)
  para que su ausencia no bloquee la exportación.
- **La exportación `.ics`** — Fase 16 entera. Esta fase solo deja el dato en el contrato.
- **El aula por bloque.** Hoy `aula` vive en el grupo y el horario no registra salón, por decisión
  del profesor del 2026-08-06. Si algún día un grupo cambia de aula entre bloques, será otra fase.
- **Los salones pendientes de confirmar** de `horarios/2026-2.md`. No bloquean: el aula la sigue
  declarando cada grupo en su `curso.yaml`.
- **WR-01 y WR-02** de `10-REVIEW.md` siguen abiertos y no son de esta fase.

</deferred>

---

*Fase: 15-el-horario-entra-al-contrato*
*Contexto recogido: 2026-08-06*
