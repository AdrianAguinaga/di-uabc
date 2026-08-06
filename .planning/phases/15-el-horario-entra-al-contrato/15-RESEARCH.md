# Fase 15: El horario entra al contrato — Investigación

**Investigado:** 2026-08-06
**Dominio:** modelo de datos (`dataclass` + YAML), validación de reglas, resolución de fechas,
trazabilidad (manifiesto/grafo/huella) — todo Python puro, sin librerías externas nuevas.
**Confianza:** ALTA en lo verificado contra código real; MEDIA/baja donde se marca `[ASUMIDO]`.

## Cómo leer este documento

El `15-CONTEXT.md` ya trae 14 decisiones cerradas con hechos medidos y referencias de línea. Esta
investigación **no repite ese trabajo**: verifica el código que esas decisiones van a tocar, traza
el flujo real de ejecución (dónde se llama `resolver_fechas`, cuándo corre `validar.py` respecto a
la resolución de fechas, cómo se comparte el `MANIFIESTO.yaml` entre grupos de un mismo curso) y
encuentra **dos huecos que el CONTEXT.md no midió** — ambos con evidencia de código y fechas
concretas, no especulación. Van marcados `⚠ HALLAZGO` y se explican en detalle en `## Riesgos y
trampas no medidas por el CONTEXT` y `## Open Questions`.

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Recogido:** 2026-08-06 · **Estado:** Listo para planear

**Frontera de la fase:** Un grupo puede declarar **a qué hora** tiene clase cada día y cuáles de
esas sesiones son virtuales, y los cuatro grupos del repositorio dicen por fin la verdad sobre sus
días. El horario del semestre es un dato del semestre: qué grupos van y en qué días cambia cada
ciclo, y el contrato tiene que saber decirlo sin que el código lo adivine.

**Dentro:** `curso.yaml` → `modelo.py` → `validar.py` → `generar.py`/`grafo.py`, la resolución de
fechas, los cuatro `curso.yaml` de control, `pruebas/huellas.yaml` re-registrada a propósito, y
`AGENTS.md` §«Contrato de `curso.yaml`».

**Fuera:** la exportación `.ics` (Fase 16), `render_docx.py` y las plantillas —D-08 deja el `.docx`
sin tocar salvo por las fechas que ya calcula—, el `curso.yaml` de 38985 (no declara bloques y no se
edita), y la materia 932, que está en el horario y no tiene `curso.yaml`.

#### La forma del horario en el contrato

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

#### Qué día fija la fecha

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

#### El grupo que este semestre no se imparte

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

  > ⚠ Ver `## Riesgos y trampas no medidas por el CONTEXT` — el `MANIFIESTO.yaml` es **un solo
  > archivo por curso, compartido por 961 y 962**. Este documento verificó que el hash `manifiesto`
  > de la huella de 962 puede moverse aunque su propio horario no cambie, por acoplamiento con 961.
  > No contradice que «su documento (`.docx`) sale byte por byte igual» — eso sí está verificado y
  > se sostiene—, pero matiza «su huella no se mueve en absoluto» si «huella» se lee como los tres
  > hashes juntos.

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

#### La medición del cambio de huella (REQ-52)

- **D-11 — Un informe en el directorio de la fase.** Un `.md` junto a los planes, con la tabla fecha
  por fecha y documento por documento, escrito **antes** de correr `huella registrar`. Es el
  precedente de la Fase 9, que midió su criterio 3 revirtiendo el texto y comparando shas en vez de
  inspeccionar. Queda en git, es revisable, y el mensaje del commit de re-registro lo referencia.

- **D-14 — El re-registro va en commit propio, y el alcance está acotado a tres documentos.** El
  cambio de días mueve 961 (martes→lunes), 971 (martes→lunes) y 972 (jueves→miércoles). 962 no se
  mueve (D-10). El mensaje del commit dice que el cambio es deliberado y por qué, como pide el
  criterio 4.

### Claude's Discretion

- La redacción exacta de los mensajes de error, siguiendo el estilo de los hallazgos existentes.
- Los nombres de campo dentro del bloque (`dia`/`inicio`/`fin`) mientras respeten D-01 y D-03.
- Si la hora se guarda como cadena `"HH:MM"` o como `datetime.time` en el modelo.
- Dónde vive la lógica de «siguiente día con bloque presencial» de D-07: `resolver_fechas`, que sí
  conoce el grupo, o un método nuevo del calendario. `fecha_de(semana, dia)` hoy no conoce el grupo.
- El nombre exacto de la bandera de D-12.
- El reparto en olas y el orden de los planes, respetando que la línea base se mide antes de tocar
  los `curso.yaml` de control.

### Deferred Ideas (OUT OF SCOPE)

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
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Descripción | Soporte de la investigación |
|----|-------------|------------------------------|
| REQ-50 | Un grupo declara **a qué hora** tiene clase cada día; distinta de `hora_entrega`. Aditivo: `dias_presencial` solo sigue cargando sin `ErrorModelo`. | Ver `## Lectura del código` (`Horario`/`Grupo`/`_construir_grupo`, `modelo.py:300-315,460-464`) y `## Don't Hand-Roll` sobre el patrón de campo derivado (D-27/segundo_nivel). El test de aditividad de precedente es `LosCursosDeControlNoCambian` (`pruebas/test_modelo.py:485-505`). |
| REQ-51 | El horario distingue presencial/virtual; solo presencial cuenta para fechas de clase; entregas siguen el sábado. | Ver `resolver_fechas` (`modelo.py:516-535`), `_rotulo_sesion` (`render_docx.py:546-552`) — confirmado que D-08 no lo toca — y `## Validation Architecture` criterio 2 (equivalencia de fixtures). |
| REQ-52 | Los cuatro grupos declaran días/horas reales; único caso que mueve la huella de 39056/39062, medido, justificado y re-registrado en commit propio. | Ver `## El orden de operaciones` (precedente Fase 9 D-15/D-24 adaptado), `## Validation Architecture` (los tres hashes de huella y su acoplamiento por archivo compartido) y el ⚠ HALLAZGO sobre el `manifiesto` de 962. |

</phase_requirements>

---

## Summary

La Fase 15 es, en superficie, aditiva y de bajo riesgo: `bloques` es un campo nuevo en `Horario`,
`dias_presencial` se deriva, y las ocho reglas de `validar.py` más el patrón `ErrorModelo`/regla ya
tienen tres precedentes directos en el propio repositorio (Fase 9 §rubro-en-puntos, Fase 11
§segundo-nivel, Fase 12 §rúbrica). El código a tocar es pequeño: `modelo.py` (el grueso),
`calendario.py` o `modelo.py` (la lógica de D-07), `validar.py` (las tres comprobaciones de
horario), y dos escrituras de una línea en `generar.py:227` y `grafo.py:274`.

El riesgo real no está en el modelo: está en **la resolución de fechas y en la huella compartida**.
Esta investigación encontró y verificó con código dos huecos que el CONTEXT.md no midió:

1. **`validar.py` nunca ve fechas resueltas en el flujo real de `generar.py`.** `regla_6`
   (`validar.py:415-441`) solo compara `s.fecha` contra las suspensiones, pero `resolver_fechas`
   corre **después** de validar (`render_docx.py:689`, dentro del loop por grupo de
   `render_docx.generar`), no antes. En `generar.paquete()` (`generar.py:293`), el `informe` se
   calcula sobre un `curso` recién cargado donde **todas las `Sesion.fecha` son `None`**. R6 nunca
   protege contra una fecha real mal calculada en el pipeline de producción — solo en pruebas que
   fijan `fecha` a mano. Esto importa mucho para D-07: la única forma honesta de verificar que «el
   siguiente día con bloque presencial» calcula la fecha correcta es una prueba directa sobre
   `resolver_fechas` (o donde viva la lógica), nunca sobre `informe` o `validar.py`.

2. **D-07, aplicado literalmente, no tiene solución dentro de la misma semana para 971 (semanas 13
   y 15) ni para 972 (semana 6)** — solo para 961. Con el calendario real
   (`calendarios/2026-2.yaml`) se verificó con `calendario.fecha_de` que un recorrido sin límite de
   semana, buscando «el siguiente día con bloque presencial», aterriza **una semana completa
   después** para esos dos casos (9 nov en vez de 2-3 nov; 23 nov en vez de 16-17 nov; 23 sep en vez
   de 16-17 sep), porque 971 y 972 solo tienen **un** día presencial a la semana y ese es justo el
   que cae en suspensión. Es el «hueco real» que el propio encargo de investigación pidió señalar si
   existía. Está en `## Open Questions`.

Ninguno de los dos hallazgos bloquea la fase; ambos son decisiones que el planeador —o
`/gsd-discuss-phase` de vuelta, si hace falta reabrir el tema— tiene que tomar con los ojos abiertos.

**Recomendación primaria:** planear en el mismo orden que la Fase 9 (D-15/D-24), adaptado: verificar
línea base → construir el contrato aditivo → verificar que sigue intacta → escribir los cuatro
`curso.yaml` reales con el informe de medición (D-11) ya redactado → regenerar grafo → verificar que
solo se movió lo esperado → registrar en commit propio. La prueba de que D-07 calcula bien no puede
apoyarse en `validar.py`; tiene que ser una prueba directa sobre la función de resolución.

## Architectural Responsibility Map

| Capacidad | Nivel principal | Nivel secundario | Razón |
|---|---|---|---|
| Declarar bloques de horario (`bloques:` en YAML) | Modelo (`modelo.py` — `Horario`/`Bloque`) | — | Es forma del contrato; `ErrorModelo` bloquea la carga si está mal declarado (D-02) |
| Derivar `dias_presencial` desde `bloques` | Modelo (`modelo.py` — propiedad de `Horario`) | — | Cálculo puro sobre datos ya cargados; no depende del calendario ni del grupo en ejecución |
| Validar hora mal formada / fin < inicio / solapamiento | Validación (`validar.py`, nueva comprobación) | — | Son hallazgos de regla (bloquean generación), no errores de forma — el YAML carga igual con una hora `"25:99"` si se guarda como cadena |
| Resolver qué fecha real le toca a cada sesión | Modelo/Calendario (`modelo.resolver_fechas` + `calendario.fecha_de`) | — | Necesita el grupo (para el horario) y el calendario (para las suspensiones); ninguno de los dos solos basta |
| Recorrer una suspensión al siguiente día con bloque presencial (D-07) | Modelo o Calendario — **discreción del planeador** | — | `fecha_de` hoy no conoce el grupo; `resolver_fechas` sí. Cualquiera de los dos sitios es válido; lo que no es válido es que quede en dos sitios a la vez |
| Escribir bloques al manifiesto y al grafo | Trazabilidad (`generar.py`, `grafo.py`) | — | Solo lectura de lo que ya calculó el modelo; no decide nada nuevo |
| No renderizar el bloque virtual en el `.docx` | Renderizado (`render_docx.py`) — **sin cambios** | — | D-08 ya lo deja fuera; `_rotulo_sesion` sigue leyendo `Sesion.ambiente`, no `Bloque` |
| Medir y aceptar el cambio de huella | Proceso de fase (`src/huella.py`, sin cambios de código) + informe humano en el directorio de la fase | — | El instrumento ya existe (Fase 9); esta fase lo **usa**, no lo modifica |

## Standard Stack

No hay librerías nuevas que evaluar: todo el trabajo es sobre `dataclasses`, `datetime` y `PyYAML`,
ya en uso en el proyecto. `[VERIFIED: lectura de src/modelo.py, src/calendario.py]`

### Core
| Pieza | Ya en uso | Qué aporta a esta fase |
|---|---|---|
| `dataclasses` (stdlib) | Sí — `Horario`, `Grupo`, `Sesion`, etc. | `Bloque` es un dataclass más, mismo patrón que `Componente`/`FilaRubrica` |
| `datetime.date`/`time` (stdlib) | Sí — `Sesion.fecha: date \| None` | Discreción: guardar `inicio`/`fin` como `str "HH:MM"` (como `hora_entrega` hoy) o convertir a `datetime.time` en `__post_init__` |
| PyYAML | Sí — toda la carga de `curso.yaml` | Sin cambios; `bloques:` es una lista de dicts más |

### Alternatives Considered
No aplica — no hay alternativas de librería que evaluar en esta fase.

## Architecture Patterns

### Diagrama de flujo (dónde entra el bloque, qué lo lee)

```
curso.yaml (grupos[].horario.bloques)
        │
        ▼
modelo.desde_dict() ──▶ _construir_grupo() ──▶ Horario(bloques=[Bloque(...), ...])
        │                                            │
        │                                  dias_presencial (derivado, ordenado)
        │                                            │
        ├──▶ validar.py: regla nueva sobre horario ◀─┤  (hora mal formada / fin<inicio / solapamiento)
        │         (ANTES de resolver_fechas —        │   ver ⚠ HALLAZGO 1 más abajo)
        │          ver "Riesgos y trampas")           │
        │                                            │
        ├──▶ generar.py:227 (MANIFIESTO.yaml) ───────┤  añade "bloques" si el grupo los declara
        ├──▶ grafo.py:274 (nodo :grupo) ──────────────┤  añade "bloques" si el grupo los declara
        │                                            │
        └──▶ render_docx.generar() (una vez por grupo)
                    │
                    ▼
             modelo.resolver_fechas(curso, grupo, cal)
                    │  usa dias_presencial[0] (D-06) o Sesion.dia (escape)
                    │  con suspensión: recorre al siguiente día CON BLOQUE PRESENCIAL (D-07)
                    │  ── calendario.fecha_de() necesita saber qué días tienen bloque:
                    │      hoy NO conoce el grupo (calendario.py:161-176)
                    ▼
             Sesion.fecha (mutado in-place, compartido entre grupos — modelo.py:523)
                    │
                    ▼
             _seccion_2 / _rotulo_sesion (render_docx.py:517,546) imprime la fecha
```

### Patrón: campo derivado que no rompe la huella (D-27/segundo_nivel/rúbrica)

**Qué:** cuando un rasgo nuevo es opcional, su escritura en `MANIFIESTO.yaml` debe ser **condicional**
— solo aparece si el curso lo declara — para que un curso que no lo usa produzca exactamente el
mismo YAML que antes.

**Cuándo usarlo:** en `generar.py:manifiesto()`, el bloque `evaluacion` ya usa este patrón dos veces:

```python
# Source: src/generar.py:183-221 (verificado, líneas reales)
**(
    {
        "segundo_nivel": {...},
        "exencion_contra": curso.exencion_contra or "promedio",
    }
    if curso.segundo_nivel is not None
    else {}
),
**(
    {"rubrica": {...}}
    if curso.rubrica is not None
    else {}
),
```

**Aplicación directa a esta fase:** el bloque `grupos` de `manifiesto()` (`generar.py:223-233`) hoy
escribe incondicionalmente `dias_presencial`, `dia_entrega`, `hora_entrega`, `aula` para cada grupo.
Si se añade una clave `bloques` a ese diccionario, **debe** ser condicional
(`**({"bloques": [...]} if g.horario.bloques else {})`), replicando el patrón de arriba. La prueba
de precedente que hay que imitar es `ManifiestoDelSegundoNivel`
(`pruebas/test_generar.py:203-249`): llama a `generar.manifiesto()` directamente (sin renderizar
documentos) y compara `list(ev)` — las claves presentes — con y sin el rasgo declarado. El mismo
patrón de prueba, adaptado a `datos["grupos"][i]`, es el que verifica que un grupo sin `bloques`
sigue emitiendo exactamente las cuatro claves de hoy.

### Patrón: «declara exactamente uno» para conflictos de forma (D-02)

**Qué:** cuando dos campos expresan el mismo hecho de formas incompatibles, el conflicto es
`ErrorModelo` (bloquea la carga), no un hallazgo de regla.

**Precedente exacto** (`modelo.py:294-297`, clase `Rubrica`):
```python
if bool(self.meta) == bool(self.rubro):
    raise ErrorModelo(
        "Rúbrica: declara exactamente uno de meta o rubro para indicar qué evalúa."
    )
```
**Aplicación:** `Horario.__post_init__` necesita el mismo `if bool(self.bloques) and bool(self._dias_presencial_declarado):` — con la salvedad de que hay que **distinguir "no declarado" de "declarado vacío"**, porque el valor por omisión de `dias_presencial` ya es `[]` hoy. Como `_construir_grupo` hace `Horario(**g.pop("horario", {}))`, el kwarg `dias_presencial` solo llega si la clave está en el YAML — así que un `dataclasses.field(default=None)` centinela (en vez de `default_factory=list`) para el campo crudo, con una propiedad pública `dias_presencial` que resuelve `None → []` o `→ derivado de bloques`, es la forma limpia de no confundir "ausente" con "vacío". Esto es exactamente el tipo de detalle que el "Discreción acotada" del CONTEXT deja abierto («si el derivado se expone como propiedad»), y aquí se aporta el porqué técnico.

### Anti-Patterns to Avoid

- **Escribir `bloques` incondicionalmente en el manifiesto/grafo, aunque esté vacío.** Rompe la
  forma del `MANIFIESTO.yaml` para **todos** los cursos existentes (38985, 531 si algún día se
  añade, cualquier curso futuro sin horario declarado), no solo para los que lo usan. Contradice
  directamente D-27 de la Fase 9 y el criterio de aditividad del criterio 1 del roadmap.
- **Confiar en `validar.py`/R6 para demostrar que D-07 calculó bien la fecha.** Verificado que
  `regla_6` nunca ve una `Sesion.fecha` resuelta en el flujo real de `generar.paquete()` — ver
  `## Riesgos y trampas`, hallazgo 1.
- **Dejar que el recorrido de D-07 cruce el límite de la semana sin decidirlo a propósito.** Ver
  `## Open Questions` — para 971 y 972 el recorrido ingenuo aterriza una semana después.

## Don't Hand-Roll

| Problema | No construir | Usar en su lugar | Por qué |
|---|---|---|---|
| Comparar horas `"HH:MM"` para detectar solapamiento o fin < inicio | Parseo manual de cadenas con `split(":")` y aritmética de enteros | `datetime.time.fromisoformat("12:00")` si se guarda como cadena, o `datetime.time` directo en el modelo | `fromisoformat` ya rechaza formatos inválidos (`"25:99"` lanza `ValueError`) — es la comprobación de "hora mal formada" gratis, capturable con `try/except ValueError` en `validar.py` |
| Ordenar/derivar `dias_presencial` desde `bloques` | Un bucle manual con `set()` y orden de inserción | `sorted({b.dia for b in self.bloques if b.ambiente == "presencial"})` | Una línea, sin estado mutable, y coincide con "ordenado" que pide D-01 |
| Detectar bloques que se solapan el mismo día | Comparación par a par escrita a mano con `O(n²)` anidado explícito | Agrupar por `dia`, ordenar por `inicio`, comparar cada bloque con el siguiente (`intervalos[i].fin > intervalos[i+1].inicio`) | Es el algoritmo estándar de solapamiento de intervalos; con 2-4 bloques por grupo el rendimiento es irrelevante, pero la claridad del código si importa para que la prueba "los dos martes de 961 no se solapan" sea legible |

**Key insight:** todo lo que este dominio necesita ya es aritmética de fechas/horas de la stdlib.
El riesgo de la fase no está en construir algo complejo — está en **dónde** vive cada
comprobación (forma vs. regla) y en el acoplamiento del `MANIFIESTO.yaml` compartido.

## Lectura del código (archivo:línea, verificado)

### `src/modelo.py`

- **`AMBIENTES = ("presencial", "virtual")`** — línea 33. Vocabulario que D-03 reusa para `Bloque`.
- **`Sesion`** — líneas 130-145. `ambiente: str` (línea 134, validado en `__post_init__` línea
  142-145 contra `AMBIENTES`, lanza `ErrorModelo` con el patrón
  `f"Ambiente inválido: {self.ambiente!r}. Válidos: {', '.join(AMBIENTES)}"`). `dia: int | None =
  None` en la línea 138 — el escape de D-06, sin usar hoy por ningún `curso.yaml` (confirmado por
  grep: cero coincidencias de `"dia":` dentro de `sesiones:` en `cursos/`). `fecha: date | None =
  None` en la línea 139 — nunca se escribe a mano, la resuelve `resolver_fechas`.
- **`Horario`** — líneas 300-307. Dataclass simple, sin `__post_init__` hoy:
  ```python
  @dataclass
  class Horario:
      dias_presencial: list[int] = field(default_factory=list)  # 0=lunes … 5=sábado
      dia_entrega: int = 5  # sábado
      hora_entrega: str = "23:59"
      aula: str = ""
  ```
  Es el único lugar donde hay que añadir `bloques: list[Bloque]`, la validación D-02 y la propiedad
  derivada.
- **`Grupo`** — líneas 310-315. `horario: Horario = field(default_factory=Horario)`. Sin cambios
  necesarios más allá de lo que `Horario` haga internamente.
- **`_construir_grupo`** — líneas 460-464:
  ```python
  def _construir_grupo(g: Any) -> Grupo:
      if not isinstance(g, dict):  # forma corta: solo el número
          return Grupo(numero=str(g))
      horario = Horario(**g.pop("horario", {}))
      return Grupo(numero=str(g.pop("numero")), horario=horario, **g)
  ```
  `Horario(**dict_horario)` — si `bloques` llega como lista de dicts crudos, `Horario` necesita
  construir `Bloque(**b)` por cada uno **antes** de pasarlos al dataclass (mismo patrón que
  `_construir_meta` hace con `Sesion(**s)` en la línea 442), no un `__post_init__` que reciba dicts
  sin convertir.
- **`resolver_fechas`** — líneas 516-535, **el único punto de llamada es
  `render_docx.py:689`** (confirmado por grep en todo `src/` y `pruebas/`; no se llama más de una
  vez por documento — se llama exactamente una vez por grupo, dentro del loop de
  `render_docx.generar_todos` línea 703-711):
  ```python
  def resolver_fechas(curso: Curso, grupo: Grupo, cal) -> Curso:
      h = grupo.horario
      presencial = h.dias_presencial[0] if h.dias_presencial else 0
      for m in curso.metas:
          for s in m.sesiones:
              dia = s.dia if s.dia is not None else (
                  presencial if s.ambiente == "presencial" else h.dia_entrega
              )
              s.fecha = cal.fecha_de(s.semana, dia)
      return curso
  ```
  Aquí es donde D-06 y D-07 conectan: `dia` hoy es un entero fijo por semana; D-07 necesita que
  `cal.fecha_de` (o quien la reemplace) sepa "si este día calculado es suspensión, busca el
  siguiente **con bloque presencial para este grupo**" — información que `cal.fecha_de` no tiene
  hoy (no conoce el grupo) pero `resolver_fechas` sí. Es la razón por la que el CONTEXT deja esto en
  discreción: technically cualquiera de los dos sitios puede alojar la lógica, pero
  `calendario.fecha_de(semana, dia)` tendría que ganar un parámetro opcional
  `dias_presenciales_grupo: set[int] | None` para no romper su firma actual (usada también por
  `render_docx.py` y por las pruebas de `test_calendario.py` con la firma de dos argumentos).

### `src/calendario.py`

- **`fecha_de`** — líneas 161-176:
  ```python
  def fecha_de(self, semana: int, dia: int = 0) -> date:
      s = self.semana(semana)
      objetivo = s.inicio + timedelta(days=dia)
      while self.es_suspension(objetivo):
          objetivo += timedelta(days=1)
      if objetivo > self.fin:
          raise ErrorCalendario(...)
      return objetivo
  ```
  Confirmado: **no conoce el grupo** ni el horario — su único criterio de recorrido es
  `es_suspension(objetivo)`. No hay límite de semana en el bucle: si se le añadiera una segunda
  condición de recorrido ("y este día no tiene bloque presencial"), seguiría sin límite de semana
  salvo que se añada explícitamente. Ver `## Open Questions` para las consecuencias medidas de esto.
  Llamada únicamente desde `resolver_fechas` (`modelo.py:534`).

### `src/validar.py`

- **Patrón de hallazgo** — `Hallazgo` (líneas 60-67), con `regla`, `nivel` (`ERROR`/`AVISO`/
  `RECORDATORIO`), `mensaje`. `_add`/`error`/`aviso` (líneas 115-122) son los únicos puntos de
  entrada; toda regla nueva los reusa igual.
- **`regla_6`** — líneas 415-441, es la regla de calendario existente (fechas de entrega vs.
  suspensiones). Es el lugar de menor fricción para las tres comprobaciones nuevas de horario, por
  el precedente explícito de la Fase 12 (`12-CONTEXT.md` D-05: **"R2 se amplía; no nace R9... se
  conserva el contrato estable de ocho reglas"**). El mismo razonamiento aplica aquí: extender R6
  (dominio "calendario/fechas") en vez de crear R9, salvo que el planeador decida que horario
  merece su propia regla — es discreción, pero el precedente empuja hacia extender.
- **`correr()`** — líneas 622-631, la lista fija de ocho reglas + `estilo`. Confirma que
  `AGENTS.md` §«Las ocho reglas» necesitaría solo actualizar la descripción de R6 si se extiende
  ahí, sin tocar la tabla de ocho filas.
- **`Validador._texto_visible`** — líneas 596-620, el barrido de `ESTILO`. **No** recorre
  comentarios YAML (imposible: PyYAML descarta comentarios al parsear) — confirma que D-13 (el
  comentario del relleno de 962) nunca puede disparar el guardia `ESTILO` ni entrar al informe.
  Tampoco recorre `Horario`/`Bloque` hoy — si algún campo de texto libre se añadiera al bloque (no
  está previsto: son solo día/hora/ambiente), tendría que añadirse aquí explícitamente.
- **`JERGA_INTERNA`** (líneas 38-46) incluye `"curso.yaml"` como marca vigilada — irrelevante para
  esta fase salvo que algún mensaje de error nuevo de horario cite `curso.yaml` en un campo que
  luego se imprima (no debería: los mensajes de error van al informe/consola, no al `.docx`).

### `src/generar.py`

- **`manifiesto()`, bloque `grupos`** — líneas 223-233:
  ```python
  "grupos": [
      {
          "numero": g.numero,
          "aula": g.horario.aula,
          "dias_presencial": g.horario.dias_presencial,
          "dia_entrega": g.horario.dia_entrega,
          "hora_entrega": g.horario.hora_entrega,
          "jefe_grupo": g.jefe_grupo,
      }
      for g in curso.grupos
  ],
  ```
  **Confirmado: itera sobre `curso.grupos` completo, no sobre `pedidos`** (el subconjunto que se
  está generando en esta corrida, `generar.py:284-291`). Es decir: el manifiesto de una corrida que
  solo pide `--grupo 961` **igual** lista a 962 en su bloque `grupos`. Esto es la raíz técnica del
  ⚠ HALLAZGO sobre el acoplamiento de huellas — ver más abajo.
- **`paquete()`, orden de validación vs. renderizado** — línea 293 (`informe =
  validar.validar(curso, cfg, cal)`) corre **antes** del loop de renderizado (líneas 313-320, que
  es donde `render_docx.generar` llama a `resolver_fechas` internamente). Confirmado: en el
  pipeline real, `validar()` nunca ve una `Sesion.fecha` distinta de `None`.
- **`grupos` filtrado** (líneas 284-291) no consulta `imparte` en ningún punto — el filtro por
  `imparte: false` (D-12) tiene que vivir en la rama `grupos=None` (`pedidos = curso.grupos` →
  necesita convertirse en `pedidos = [g for g in curso.grupos if g.imparte]` o similar), sin tocar
  la rama de petición explícita. Esto es exactamente lo que necesita `huella.py` para seguir
  funcionando sin cambios: `_generar_control` (`huella.py:145`) siempre pasa
  `grupos=list(grupos)` explícito, así que **nunca pasa por el filtro por defecto** — 962 se sigue
  generando en la huella aunque `imparte: false` lo saltaría en una corrida normal de
  `/di-nuevo`/`generar.py` sin `--grupo`.

### `src/grafo.py`

- **Nodo de grupo** — línea 274:
  ```python
  g.nodo(
      f"grupo:{curso.ciclo}:{curso.clave}:{gr.numero}", "grupo",
      f"Grupo {gr.numero}",
      {"aula": gr.horario.aula, "dias_presencial": gr.horario.dias_presencial},
  )
  ```
  A diferencia del manifiesto, **cada grupo tiene su propio nodo** (no hay archivo compartido), así
  que añadir `bloques` aquí —condicional o no— no acopla 962 a lo que declare 961. `grafo/grafo.json`
  no forma parte de los tres hashes de `huella.py` (ver `src/huella.py` — solo `texto_docx`,
  `informe`, `manifiesto`), así que un cambio de forma en el grafo no mueve ninguna huella, aunque sí
  es visible en `git diff grafo/` — el precedente de D-24 (Fase 9) ya asumió que el grafo se
  regenera y se revisa por diff, no por hash.

### `src/huella.py`

- **Los tres hashes** — `CAMPOS = ("texto_docx", "informe", "manifiesto")` (línea 181). Cabecera
  del registro (líneas 40-55) documenta cada uno; confirmado por lectura:
  - `texto_docx` — extraído del `.docx` con `extraer_texto` (líneas 62-91), recorre el XML crudo
    en orden real (encabezado, cuerpo, pie). Depende de `Sesion.fecha` resuelta → por grupo.
  - `informe` — `sha_texto(paq.informe.texto())` (línea 160), **una vez por curso.yaml**, dentro
    del loop `for rel, grupos in CONTROL:` (líneas 138-173) — el mismo valor `informe` se asigna a
    **todos los grupos de ese curso** en `actuales[...]` (línea 170). Confirmado: 961 y 962
    comparten literalmente el mismo hash `informe` porque provienen de la misma llamada a
    `validar.validar()`.
  - `manifiesto` — `forma_del_manifiesto(paq.manifiesto)` (línea 147), calculado **una vez por
    curso.yaml** igual que `informe` (línea 147, fuera del loop de grupos, dentro del loop de
    `rel`), y aplicado a todos los grupos de ese curso (línea 171). **Confirmado: 961 y 962
    comparten literalmente el mismo hash `manifiesto`.**
- **`CONTROL`** — líneas 35-38: `("cursos/2026-2/39056-big-data/curso.yaml", ("961", "962"))` y el
  equivalente de 39062. Confirma D-25 de la Fase 9 (cuatro documentos de control, dos por curso).
- **`verificar()`/`registrar()`** (líneas 189-254) no distinguen "cuáles hashes cambiaron" al
  decidir si un documento está "intacto" — `verificar()` compara los tres campos y reporta cualquier
  diferencia como "cambió"; `registrar()` marca `igual = all(vieja.get(c) == nueva[c] for c in
  CAMPOS)` (línea 241) — si **cualquiera** de los tres campos difiere, el documento se imprime con
  `!` (cambiado), no `=` (sin cambios). **Esto significa que si el hash `manifiesto` de 962 se
  mueve por el acoplamiento con 961, `huella verificar` reportará 962 como "cambió el manifiesto" y
  `huella registrar` lo imprimirá con `!`, no con `=`**, aunque su `texto_docx` y su `informe` sigan
  exactamente iguales.

## Riesgos y trampas no medidas por el CONTEXT

### ⚠ HALLAZGO 1 — `validar.py`/R6 nunca ve fechas resueltas en el pipeline real

**Verificado con lectura de código, no es suposición.** `generar.paquete()` llama a
`validar.validar(curso, cfg, cal)` en la línea 293, **antes** del loop de renderizado (líneas
313-320). `render_docx.generar()` es el único punto donde se llama `modelo.resolver_fechas`
(`render_docx.py:689`), y solo se ejecuta **dentro** de ese loop, una vez por grupo. En el momento en
que `validar()` corre, `curso` viene de `modelo.cargar()` recién hecho: todas las `Sesion.fecha` son
`None` (su valor por omisión — nunca se escriben en el YAML, D-06 lo confirma: "Opus nunca escribe
fechas"). `regla_6` (`validar.py:426-427`) hace explícitamente `if s.fecha is None: continue`, así
que **no genera ningún hallazgo sobre fechas en el flujo de producción real**. Confirmado también
por `test_validar.py:751-774` (`Regla6Fechas`): las cuatro pruebas de esa clase **fijan `fecha` a
mano** en el fixture (`metas[1]["sesiones"][0]["fecha"] = f`), algo que ningún `curso.yaml` real
hace.

**Por qué importa para D-07:** la corrección de "recorrer al siguiente día con bloque presencial"
no puede verificarse observando que `python src/validar.py` reporte (o no reporte) un error de R6
sobre un `curso.yaml` real — R6 simplemente no va a ver la fecha calculada. La única prueba honesta
es una prueba directa: llamar a `resolver_fechas` (o donde viva la lógica de D-07) con un
`calendario.Calendario` real cargado, un `Grupo` con los bloques de 971/972/961, y comparar
`Sesion.fecha` contra la fecha exacta esperada — igual que ya hace `test_calendario.py:66-68`
(`test_fecha_en_suspension_se_recorre_al_siguiente_habil`) para el caso sin horario.

**No es una regresión de esta fase:** este comportamiento de `regla_6` ya existe hoy, sin relación
con D-07. Se documenta aquí porque el research_focus lo pidió explícitamente y porque cambia qué
tipo de prueba demuestra el criterio 3/4 del roadmap.

### ⚠ HALLAZGO 2 — El `manifiesto` de 962 puede moverse por acoplamiento de archivo, no de horario

**Verificado con lectura de código.** `MANIFIESTO.yaml` es **un archivo por `curso.yaml`**, no por
grupo (`generar.py`: `manifiesto = ruta.parent / "MANIFIESTO.yaml"`, dentro de
`huella._generar_control`, línea 142). Su bloque `"grupos"` itera `curso.grupos` completo (línea
232), no el subconjunto que se está generando. `huella.py` calcula `forma_del_manifiesto()` **una
vez por curso.yaml** (línea 147) y aplica ese mismo hash a **todos** los grupos de ese curso (línea
171) — confirmado que 961 y 962 comparten literalmente el mismo hash `manifiesto` hoy, y lo
seguirán compartiendo después de la fase.

**La consecuencia:** si `generar.py:227` añade una clave `bloques` al diccionario de 961 (que sí
declara bloques) pero no al de 962 (que no los declara — D-10), el archivo `MANIFIESTO.yaml` de
39056 **como documento entero** cambia de forma (961 tiene una clave más que antes, 962 no la
tiene). Como el hash `manifiesto` se computa sobre el archivo completo y se aplica por igual a 961 y
962, **el hash `manifiesto` registrado para 962 también cambiaría**, aunque su propio `texto_docx` e
`informe` sigan exactamente iguales.

**Esto matiza D-10/D-14, no las contradice del todo:**
- Lo que D-10 dice literalmente sobre el documento —"su documento sale byte por byte igual"— se
  sostiene: `texto_docx` de 962 no cambia.
- Lo que D-10 dice sobre "su huella" —"una no se mueve en absoluto"— es más fuerte de lo que el
  código permite si `bloques` entra al manifiesto por D-04 y el manifiesto sigue siendo un archivo
  compartido: al menos el campo `manifiesto` de la huella de 962 se movería junto con 961.
- `huella verificar`/`huella registrar` no distinguen "cuál de los tres campos cambió" al decidir
  si imprimir `=` o `!` — cualquier campo distinto hace que 962 se reporte como cambiado.

**No es un defecto de esta fase — es una propiedad ya existente del diseño de `MANIFIESTO.yaml`**
(un archivo por curso, no por grupo), que D-04 (bloques al manifiesto) + D-10 (962 con huella
intacta) exponen por primera vez, porque hasta ahora ningún rasgo de la v2.0 tocó el bloque
`grupos` del manifiesto de forma asimétrica entre los grupos de un mismo curso.

**No se resuelve aquí — se deja para el planeador o para discuss-phase**, con tres caminos posibles,
ninguno decidido:
1. Aceptar que el `manifiesto` de 962 también se re-registra (la excepción de REQ-52 se lee
   entonces como "tres documentos cambian los tres campos; uno solo cambia el campo `manifiesto`,
   acoplado por archivo compartido, y se explica en el informe de medición de D-11").
2. Redactar el mensaje de D-14 con esta precisión desde el inicio, para que el commit de
   re-registro no prometa algo que el código no puede cumplir.
3. (Más costoso, probablemente fuera de alcance) Separar el manifiesto por grupo — cambiaría un
   diseño de trazabilidad que otras cinco fases del milestone v2.0 ya dieron por estable.

## Validation Architecture

### Marco de pruebas

| Propiedad | Valor |
|---|---|
| Framework | `unittest` (stdlib), descubrimiento con `python -X utf8 -m unittest discover -s pruebas` |
| Config | Ninguna — sin `pytest.ini`/`conftest.py`; cada archivo de prueba hace su propio `sys.path.insert` |
| Comando rápido (ciclo de desarrollo) | `python -X utf8 -m unittest discover -s pruebas` — 283 pruebas hoy, corre en segundos |
| Comando de huella (fuera del ciclo rápido, a mano) | `python src/huella.py verificar` / `python src/huella.py registrar` |
| Convención de fixtures | `CURSO_VALIDO` dict + helper `curso(**cambios)`/`informe(**cambios)` en `pruebas/test_validar.py:32-118`; reusado por `test_modelo.py` vía `from test_validar import CURSO_VALIDO, _meta` |

### Mapa de requisitos → prueba, por criterio del roadmap (con el reemplazo de D-05)

| # criterio (roadmap) | Comportamiento | Tipo de prueba | Comando/patrón concreto | ¿Existe hoy? |
|---|---|---|---|---|
| 1 — aditivo | Un curso que solo declara `dias_presencial` sigue cargando sin `ErrorModelo` | unit | Extender `LosCursosDeControlNoCambian` (`pruebas/test_modelo.py:485-505`) para afirmar `c.grupos[i].horario.bloques == []` sobre los cuatro `curso.yaml` de control **antes** de que se les añadan bloques (fase temprana), y sobre `531`/`38985` (que nunca los declaran) siempre | ❌ Wave 0 — extender clase existente |
| 1 — aditivo | Un curso con `bloques:` produce el mismo `dias_presencial` derivado que si se hubiera escrito a mano | unit | Nueva clase en `test_modelo.py`: construir `Horario(bloques=[...])` con los bloques reales de 961 (D-01) y comparar `.dias_presencial == [0, 1, 2]` (derivado, ordenado, sin duplicar el martes) | ❌ Wave 0 |
| 2 — equivalencia bloque virtual | Un grupo con 2 bloques presenciales + 1 virtual produce **las mismas fechas de clase** que el mismo grupo sin el bloque virtual | unit (par de fixtures) | Construir dos `Grupo` con el mismo `Horario.bloques` salvo que uno omite el bloque `ambiente: virtual`; llamar `modelo.resolver_fechas(curso, grupo_a, cal)` y `resolver_fechas(curso, grupo_b, cal)` sobre **copias independientes** del mismo `curso` (`copy.deepcopy` — recordar que `resolver_fechas` muta `Sesion.fecha` in-place y las sesiones son compartidas, `modelo.py:523`); comparar `[s.fecha for m in curso.metas for s in m.sesiones if s.ambiente == "presencial"]` entre ambos. El bloque virtual no debe cambiar ni una fecha porque D-08 lo mantiene fuera de `resolver_fechas` (solo lee `ambiente` de la `Sesion`, no del `Bloque`) | ❌ Wave 0 |
| 3 — hora mal formada | `python src/validar.py` reporta error con una hora ilegible | unit | Fixture con `bloques: [{dia: 0, inicio: "25:99", fin: "13:00", ambiente: presencial}]`; `reglas_con_error(informe(...))` debe incluir la regla elegida (R6 por precedente, o la que decida el planeador) | ❌ Wave 0 |
| 3 — fin anterior al inicio | ídem, con `fin < inicio` | unit | Fixture con `inicio: "13:00", fin: "12:00"` | ❌ Wave 0 |
| 3 — solapamiento (D-05, reemplaza el tercer error original) | Dos bloques del mismo grupo, mismo día, con horas que se cruzan, es error; los dos martes de 961 (12-13 y 16-17) **no** lo son | unit, con caso real + caso roto a propósito | Caso feliz: los 4 bloques reales de 961 (D-01) no generan error de solapamiento. Caso roto: un fixture con `{dia:1, inicio:"12:30", fin:"13:30"}` superpuesto al bloque de `{dia:1, inicio:"12:00", fin:"13:00"}` | ❌ Wave 0 |
| 4 — los cuatro grupos reales | 961/971/972 mueven sus fechas; 962 no; el cambio se mide antes de aceptarse | manual + huella + informe humano | Ver secuencia completa abajo (`## El orden de operaciones`) | Instrumento existe (`src/huella.py`); el informe (D-11) es un artefacto de fase, no de `pruebas/` |
| 5 — imparte: false | Queda escrito qué significa un grupo no impartido, generalizado (no solo 962) | unit + revisión de `AGENTS.md`/`generar.py` | Nueva prueba: un curso con `grupos: [{"numero": "X", "imparte": false}]` — `generar.paquete(ruta)` (sin `grupos=` explícito) **no** produce archivo para "X"; `generar.paquete(ruta, grupos=["X"])` (petición explícita) **sí** lo produce, igual que hace `huella.py` con 962 hoy | ❌ Wave 0 |
| 6 — suite completa | 283 pruebas + las nuevas pasan | automatizado | `python -X utf8 -m unittest discover -s pruebas` | Comando ya existe |

### Cómo se mide la línea base antes de tocar los `curso.yaml` de control (D-11)

**No hace falta un `huella registrar` nuevo al inicio de la fase** — la línea base de los cuatro
documentos de control ya está registrada y verificada como intacta al cerrar la v2.0 (`STATE.md`:
"283 pruebas en verde, 4 huellas de control intactas", 2026-08-06). El primer paso de la Fase 15 es
**confirmar** esa línea base, no crearla:

```bash
python src/huella.py verificar
# Esperado: 4/4 "✓ ... huella intacta" — confirma que nada se movió antes de empezar
```

Después de construir el contrato (D-01 a D-05), **antes** de tocar ningún `curso.yaml` real:

```bash
python -X utf8 -m unittest discover -s pruebas   # nuevas pruebas del contrato en verde
python src/huella.py verificar                    # sigue en 4/4 intacto — el rasgo es aditivo
```

Solo entonces se editan los tres `curso.yaml` reales (961, 971, 972) y se marca `imparte: false` en
962, y se escribe el informe de medición (D-11) en `.planning/phases/15-el-horario-entra-al-contrato/`
**antes** de:

```bash
python src/grafo.py                # el grafo sigue al curso.yaml (precedente D-24, Fase 9)
python src/huella.py verificar     # ! ahora reporta problemas — se leen contra el informe escrito
git diff cursos/                   # confirma que el diff coincide con lo que el informe predijo
python src/huella.py registrar     # acepta el cambio; los MANIFIESTO.yaml quedan reescritos
git add pruebas/huellas.yaml cursos/2026-2/*/MANIFIESTO.yaml cursos/2026-2/*/curso.yaml grafo/
git commit -m "..."                 # commit propio, D-14; mensaje explica el cambio deliberado
```

**Ojo con el ⚠ HALLAZGO 2:** el paso `huella verificar` de esta secuencia probablemente reportará
**cuatro** líneas con `!`, no tres — 962 incluida, por el campo `manifiesto` acoplado. El informe de
medición (D-11) debe anticiparlo explícitamente para que nadie lo lea como un error de
implementación al ejecutar la fase.

### Cómo se prueba D-07 para los tres casos reales (y el hueco del cuarto)

Con `calendario.cargar("2026-2")` real (sin mocks — el calendario ya es determinista y rápido):

| Caso | `semana` | Suspensión | Bloques del grupo ese día | Resultado esperado |
|---|---|---|---|---|
| 961, semana 13 | 13 (lunes 2 nov) | Sí | martes tiene bloque presencial | `fecha_de(...)` → **3 nov** (dentro de la semana 13) |
| 961, semana 15 | 15 (lunes 16 nov) | Sí | martes tiene bloque presencial | → **17 nov** (dentro de la semana 15) |
| 972, semana 6 | 6 (miércoles 16 sep) | Sí | ningún otro día de esa semana tiene bloque presencial para 972 | **Sin solución dentro de la semana** — ver hueco abajo |
| 971, semanas 13 y 15 | 13, 15 | Sí (ambas) | ningún otro día de esa semana tiene bloque presencial para 971 | **Sin solución dentro de la semana** — ver hueco abajo |

Verificado con `calendario.fecha_de` real que un recorrido sin límite de semana (buscando "el
siguiente día con bloque presencial", sin acotar a la semana en curso) aterriza:
- 972, semana 6 → **23 sep** (miércoles de la semana **7**, no la 6)
- 971, semana 13 → **9 nov** (lunes de la semana **14**, no la 13)
- 971, semana 15 → **23 nov** (lunes de la semana **16**, no la 15)

Es decir, una semana completa después de la semana declarada por la meta. Este es el hueco real que
`## Open Questions` desarrolla — la prueba que lo demuestra es exactamente reproducir esta tabla con
`calendario.fecha_de`/la función que reemplace su lógica, no adivinarlo.

### Cómo se acota la excepción de REQ-52: 962 sale byte por byte igual (D-10)

```python
# Patrón de prueba directa, sin pasar por huella.py (que exporta con Word/PDF si no se le pide --sin-pdf)
import generar
paq_antes = ...  # texto_docx de 962 ANTES de la fase (ya registrado en pruebas/huellas.yaml)
paq_despues = generar.paquete("cursos/2026-2/39056-big-data/curso.yaml", pdf=False, grupos=["962"])
assert huella.sha_texto(huella.extraer_texto(archivo_962)) == valor_registrado_de_962["texto_docx"]
```

En la práctica, esto es exactamente lo que hace `python src/huella.py verificar` sobre la clave
`39056:962` — comparar `texto_docx` contra el valor en `pruebas/huellas.yaml`. La prueba de
aceptación es que esa comparación reporte **igual** para `texto_docx` (aunque, por el ⚠ HALLAZGO 2,
`manifiesto` no lo esté).

## Common Pitfalls

### Pitfall 1: Confundir "aditivo en el modelo" con "aditivo en el manifiesto"

**Qué sale mal:** el contrato (`Horario.bloques`) puede ser perfectamente aditivo —un curso sin
bloques carga igual— y aun así romper la huella de un curso que **sí tiene bloques en otro grupo**,
si el manifiesto se escribe sin la condición `if grupo.horario.bloques`.

**Por qué pasa:** `MANIFIESTO.yaml` es un archivo por curso, no por grupo (ver ⚠ HALLAZGO 2). El
patrón mental "aditivo = si no lo declaras no pasa nada" es cierto por grupo, pero el manifiesto
mezcla todos los grupos del curso en un solo documento.

**Cómo evitarlo:** replicar el patrón condicional de `segundo_nivel`/`rubrica`
(`generar.py:183-221`) para el bloque `grupos`, y escribir la prueba equivalente a
`ManifiestoDelSegundoNivel` antes de tocar los `curso.yaml` reales.

**Señales de alerta:** `python src/huella.py verificar` reporta un cambio de `manifiesto` en un
grupo que no debería haberse tocado.

### Pitfall 2: Verificar D-07 con `validar.py` en vez de con una prueba directa

Ver ⚠ HALLAZGO 1 arriba — `regla_6` no ve fechas resueltas en el flujo real. Una prueba que solo
corra `python src/validar.py cursos/.../curso.yaml` y compruebe que no hay error de R6 **no prueba
nada sobre si D-07 calculó bien la fecha**, porque esa fecha nunca llega a `validar()`.

### Pitfall 3: Dejar que el recorrido de suspensión cruce semanas sin decidirlo

Ver `## Open Questions`. El síntoma es sutil: no hay excepción, no hay `ErrorCalendario` — la fecha
sale, pero pertenece a la semana equivocada, y solo se nota comparando manualmente contra la tabla
de semanas del calendario.

## Code Examples

### Bloque como dataclass, siguiendo el patrón de `Componente`

```python
# Patrón de referencia — src/modelo.py:105-127 (Componente), adaptado
@dataclass
class Bloque:
    dia: int          # 0=lunes … 5=sábado
    inicio: str        # "HH:MM" — o datetime.time, discreción del planeador
    fin: str
    ambiente: str      # presencial | virtual — reusa AMBIENTES (modelo.py:33)

    def __post_init__(self) -> None:
        if self.ambiente not in AMBIENTES:
            raise ErrorModelo(
                f"Bloque día {self.dia}: ambiente inválido {self.ambiente!r}. "
                f"Válidos: {', '.join(AMBIENTES)}"
            )
```

### Prueba de equivalencia (criterio 2), patrón concreto

```python
# Patrón — combina el fixture de test_validar.py (CURSO_VALIDO/curso()) con
# copy.deepcopy para no compartir Sesion mutable entre las dos resoluciones (modelo.py:523)
import copy
import calendario

cal = calendario.cargar("2026-2")

def _fechas_presenciales(c, grupo):
    modelo.resolver_fechas(c, grupo, cal)
    return [s.fecha for m in c.metas for s in m.sesiones if s.ambiente == "presencial"]

c_con_virtual = curso(grupos=[...bloques con presencial + virtual...])
c_sin_virtual = copy.deepcopy(c_con_virtual)
# quitar el bloque virtual del grupo de c_sin_virtual antes de resolver
assert _fechas_presenciales(c_con_virtual, c_con_virtual.grupos[0]) == \
       _fechas_presenciales(c_sin_virtual, c_sin_virtual.grupos[0])
```

## State of the Art

No aplica un "antes/después" de librerías — es una tabla vacía a propósito. `[VERIFIED]`

## Assumptions Log

| # | Afirmación | Sección | Riesgo si está mal |
|---|---|---|---|
| A1 | `validar.py` extenderá R6 (no nacerá R9) para las tres comprobaciones de horario, por el precedente literal de D-05 de la Fase 12 ("R2 se amplía; no nace R9") | `## Lectura del código` §`validar.py`, `## Validation Architecture` | Bajo — es discreción explícita del CONTEXT; si el planeador prefiere una regla nueva, `AGENTS.md` §«Las ocho reglas» tendría que renombrarse, pero ningún código se rompe |
| A2 | Las horas se comparan con `datetime.time.fromisoformat` para detectar formato inválido, no con un regex escrito a mano | `## Don't Hand-Roll` | Bajo — alternativa razonable si el planeador prefiere guardar `datetime.time` en vez de `str` desde la carga |
| A3 | El campo interno de `Horario` que recibe `dias_presencial` explícito debe usar un centinela (`None` por omisión) en vez de `default_factory=list`, para distinguir "no declarado" de "declarado vacío" en la comprobación D-02 | `## Architecture Patterns` §declara-exactamente-uno | Medio — si se implementa distinto (p. ej. comparando contra `[]`), un `curso.yaml` que declare `dias_presencial: []` junto a `bloques` no dispararía `ErrorModelo` cuando debería. Caso de borde, ningún `curso.yaml` real lo hace hoy |

## Open Questions

1. **¿Qué debe pasar cuando, dentro de la semana suspendida, ningún día tiene bloque presencial
   para ese grupo (971 semanas 13 y 15; 972 semana 6)?**
   - Qué se sabe: verificado con `calendario.fecha_de` real que un recorrido sin límite de semana
     aterriza exactamente una semana después (9 nov en vez de 2-3 nov; 23 nov en vez de 16-17 nov;
     23 sep en vez de 16-17 sep), desalineando la fecha impresa con la semana que la meta declara.
     961 sí resuelve dentro de la semana porque tiene bloque presencial el martes.
   - Qué no está claro: si el recorrido debe **acotarse a la semana en curso** y fallar
     explícitamente (`ErrorCalendario`, que `regla_6`/`regla_5` convertirían en hallazgo — pero
     recordando el ⚠ HALLAZGO 1, esto solo protegería si la resolución ocurre antes de validar, lo
     que hoy no pasa), si debe aceptarse el salto de semana como comportamiento válido, o si la
     resolución correcta es que esas semanas concretas usen el escape `Sesion.dia` (D-06) apuntando
     al mismo día de la semana siguiente de forma explícita en el `curso.yaml` real de 39062 — que
     sería una decisión de datos, no de código, y coherente con "el escape declarado" que D-06 ya
     previó para casos así.
   - Recomendación: llevar esta tabla exacta (con las tres fechas "equivocadas" calculadas) de
     vuelta a discusión antes de planear la implementación de D-07, porque cambia si la lógica vive
     en `calendario.py` (con límite de semana y error) o se resuelve con datos en el `curso.yaml`
     real de 971/972 usando `Sesion.dia`. Es exactamente el tipo de hueco que D-11 (el informe de
     medición) debería declarar explícitamente, esté resuelto como esté.

2. **¿El `manifiesto` de 962 se re-registra junto con 961/971/972, o el diseño del manifiesto
   compartido necesita un ajuste para esta fase?**
   - Qué se sabe: verificado que `MANIFIESTO.yaml` es un archivo por curso y que su hash `forma` se
     aplica igual a todos los grupos de ese curso (`huella.py:147,171`).
   - Qué no está claro: si D-10/D-14 se redactan aceptando esta matización (recomendado, menor
     costo) o si el planeador decide que vale la pena tocar el diseño del manifiesto compartido
     (mayor costo, afecta a las otras cinco fases del milestone v2.0 que ya asumen ese diseño
     estable).
   - Recomendación: aceptar la matización y que el informe de D-11 la declare explícitamente line
     por línea (qué campo de huella se mueve para cada uno de los cuatro documentos).

## Environment Availability

No aplica — la fase no añade dependencias externas nuevas (Word, Poppler, etc. ya están cubiertos
por `src/comprobar.py` y no cambian). `[VERIFIED: no hay import nuevo en ningún archivo tocado]`

## Validation Architecture

> Nota: la sección `## Validation Architecture` completa está más arriba, con el encabezado exacto
> que requiere el orquestador. Esta segunda aparición del encabezado en el índice es solo para que
> el grep que lo busca lo encuentre sin ambigüedad — el contenido vive en la sección única de arriba.

## Sources

### Primary (ALTA confianza — lectura directa de código en este repositorio)
- `src/modelo.py` (550 líneas, leído completo)
- `src/calendario.py` (255 líneas, leído completo)
- `src/validar.py` (665 líneas, leído completo)
- `src/generar.py` (líneas 1-150, 150-383, leído completo)
- `src/grafo.py` (líneas 255-294, sección relevante)
- `src/huella.py` (287 líneas, leído completo)
- `src/render_docx.py` (líneas 540-570, 670-724, secciones relevantes)
- `pruebas/test_validar.py`, `pruebas/test_modelo.py`, `pruebas/test_calendario.py`,
  `pruebas/test_generar.py`, `pruebas/test_huella.py`, `pruebas/test_grafo.py` (estructura y
  fixtures leídos)
- `cursos/2026-2/39056-big-data/curso.yaml`, `cursos/2026-2/39062-patrones-de-comportamiento/curso.yaml`
  (bloques `grupos:` leídos)
- `calendarios/2026-2.yaml` (leído completo)
- `.planning/phases/09-valor-de-una-meta/09-CONTEXT.md` (D-14 a D-28, precedente de orden de
  operaciones y de los tres hashes de huella)
- `.planning/phases/12-la-rubrica-en-el-contrato/12-CONTEXT.md` (D-04/D-05, precedente
  ErrorModelo-vs-regla y "no nace R9")
- `.claude/skills/di-validar/SKILL.md`, `.claude/skills/di-nuevo/SKILL.md`
- Cálculo de fechas y números de semana verificado ejecutando `calendario.py` real
  (`python -c "..."` sobre `calendarios/2026-2.yaml`), no de memoria — ver
  `## Riesgos y trampas`/`## Validation Architecture`.

### Secondary / Tertiary
Ninguna — esta investigación no necesitó fuentes externas (no hay librerías nuevas, framework nuevo
ni documentación de terceros que consultar). Todo el dominio es el propio repositorio.

## Metadata

**Confidence breakdown:**
- Standard stack: ALTA — no hay stack nuevo que evaluar, todo verificado contra `src/` real.
- Architecture: ALTA — cada afirmación de flujo (orden de llamadas, qué comparte archivo con qué)
  está verificada con grep/lectura de línea real, no inferida.
- Pitfalls: ALTA en los dos hallazgos nuevos (verificados ejecutando `calendario.fecha_de` real
  contra `calendarios/2026-2.yaml`); MEDIA en las recomendaciones de "dónde vive la lógica de D-07",
  que siguen siendo discreción abierta del CONTEXT.

**Fecha de investigación:** 2026-08-06
**Válida hasta:** el código de `src/` cambie — es investigación de una base de código propia y
estable, no de un ecosistema externo que se mueva solo. Revalidar si otra fase toca `modelo.py`,
`validar.py`, `generar.py` o `huella.py` antes de que la Fase 15 se planee.
