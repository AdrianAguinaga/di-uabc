# Fase 15: El horario entra al contrato — Bitácora de la discusión

> **Solo rastro de auditoría.** No se usa como entrada de los agentes de investigación, planeación
> ni ejecución. Las decisiones viven en `15-CONTEXT.md`; esta bitácora conserva las alternativas
> que se consideraron y se descartaron.

**Fecha:** 2026-08-06
**Fase:** 15 — El horario entra al contrato
**Áreas discutidas:** forma del horario · qué día fija la fecha · bloque virtual vs sesión virtual ·
grupo que no se imparte

---

## Forma del horario en el contrato

### Cómo se declara el horario de un grupo

| Opción | Descripción | Elegida |
|---|---|---|
| `bloques:` lista, `dias_presencial` se deriva | Una sola fuente de verdad; el bloque expresa dos martes y un martes virtual | ✓ |
| Los dos declarados, una regla los cruza | Lo que pedía literal el criterio 3; obliga a sincronizar dos listas a mano | |
| Un mapa día → horas | Cambio más pequeño; no sabe expresar dos bloques el mismo día ni un virtual fuera de `dias_presencial` | |

**Elección:** bloques como unidad. → **D-01**

### Si un grupo declara `bloques:` y `dias_presencial:` a la vez

| Opción | Descripción | Elegida |
|---|---|---|
| `ErrorModelo` | Como `meta`/`rubro` de la rúbrica: «declara exactamente uno» | ✓ |
| Mandan los bloques, el otro se ignora | Cómodo para migrar; deja un campo mintiendo en el archivo | |
| Cargan, y la validación avisa | Aquí no hay dos significados: hay un derivado escrito a mano | |

**Elección:** `ErrorModelo`. → **D-02**

### Vocabulario del ambiente del bloque

| Opción | Descripción | Elegida |
|---|---|---|
| `ambiente: presencial \| virtual` | Reusa `AMBIENTES`; un solo vocabulario en el proyecto | ✓ |
| `ambiente: salon \| virtual` | El vocabulario de `horarios/2026-2.md`; deja claro que un bloque no es una sesión | |
| `aula: true \| false` | Imposible de confundir; choca de nombre con el `aula:` que ya existe | |

**Elección:** reusar `AMBIENTES`. **Nota:** se aceptó a sabiendas que «virtual» pasa a tener dos
sentidos, resuelto por tipo (`Bloque` ≠ `Sesion`) y por D-08, que fija que no interactúan. → **D-03**

### Trazabilidad de los bloques

| Opción | Descripción | Elegida |
|---|---|---|
| Al `MANIFIESTO.yaml` y al grafo | Si el horario es contrato, es rastro; el cambio de forma suma al de REQ-52 | ✓ |
| Solo al manifiesto | Conserva la forma del grafo, como D-10 de la Fase 12 hizo con la rúbrica | |
| A ninguno | Minimiza el diff; deja el rastro sin el dato que la Fase 16 exportará | |

**Elección:** a los dos. → **D-04**

### El tercer error de validación del criterio 3

Contexto: D-01 vuelve **imposible** el error que el criterio enunciaba («un día declarado con hora
no está en `dias_presencial`»), porque el derivado sale de los bloques.

| Opción | Descripción | Elegida |
|---|---|---|
| Bloques que se solapan el mismo día | La incoherencia real que sobrevive; comprobable con una prueba que falla a propósito | ✓ |
| Día fuera de lunes–sábado | Forma pura; pertenece a `__post_init__`, y entonces el validador se queda sin su tercer error | |
| Grupo con bloques pero ninguno presencial | Choca con el área 4: eso podría significar «no se imparte» | |
| Los tres a la vez | Cubre todo; engorda una fase que ya mueve cuatro documentos de control | |

**Elección:** solapamiento. → **D-05**

---

## Qué día fija la fecha

**Medición previa:** los dos cursos declaran exactamente una sesión presencial por semana, las 16
semanas. La pregunta no era cómo repartir varias sesiones, sino cuál de los días reales se lleva la
única que hay.

| Opción | Descripción | Elegida |
|---|---|---|
| El primero de la semana, `Sesion.dia` como escape | Es lo que `resolver_fechas` ya hace; el campo de escape ya existe y nadie lo usa | ✓ |
| El último de la semana | Invierte el sesgo: la clase instruye y luego se entrega. Igual de arbitraria | |
| Cada sesión declara su día, obligatorio | Máxima fidelidad; 16 días a mano por curso, y las sesiones son compartidas entre grupos | |
| Reparto cíclico entre los días | Distribuye sin escribir nada; produce un calendario impredecible para el alumno | |

**Elección:** primer día + escape declarado. → **D-06**

### Cuando una sesión presencial cae en suspensión

Contexto medido: las tres suspensiones caen en miércoles 16 sep, lunes 2 nov y lunes 16 nov, justo
sobre los días nuevos. `calendario.fecha_de` recorre al día siguiente sin mirar el horario, así que
971 y 972 imprimirían «En clase» en un día sin aula.

| Opción | Descripción | Elegida |
|---|---|---|
| Al siguiente día con bloque presencial | Usa el dato que la fase acaba de meter al contrato; sin bloques, comportamiento intacto | ✓ |
| Se queda como está | Alcance más estrecho; deja el defecto escrito en tres documentos entregables | |
| Esa semana no tiene sesión presencial | Lo más fiel; deja una meta sin sesión y toca `render_docx` y probablemente R6 | |

**Elección:** recorrer al siguiente día con bloque presencial. → **D-07**

---

## Bloque virtual frente a sesión `ambiente: virtual`

| Opción | Descripción | Elegida |
|---|---|---|
| No — el bloque es dato, el documento no cambia | REQ-51 y el criterio 2 lo piden literal; ninguna huella se mueve por esto | ✓ |
| Sí — la sesión virtual cae en el día del bloque | Más fiel al horario; contradice REQ-51 y adelanta las entregas de 971 y 972 | |
| No mueve la fecha, pero sí el rótulo | Respeta REQ-51 y avisa del bloque; toca `render_docx.py:546` y mueve dos huellas más | |

**Elección:** el bloque no toca el `.docx`. → **D-08**

---

## Grupo que este semestre no se imparte

### Cómo lo declara el contrato

| Opción | Descripción | Elegida |
|---|---|---|
| `imparte: false` en el grupo | Booleano explícito; conserva los datos del grupo para cuando vuelva | ✓ |
| Ausencia de bloques = no se imparte | Choca con el criterio 1: el silencio significaría dos cosas | |
| `ciclos:` en el grupo | Guarda la historia; hay que mantener una lista hacia adelante | |
| Se retira del `curso.yaml` | Cero contrato nuevo; pierde aula y plataforma, y borra un documento de control | |

**Elección:** `imparte: false`. → **D-09**

### La línea base de 962 en `pruebas/huellas.yaml`

| Opción | Descripción | Elegida |
|---|---|---|
| Se conserva y se sigue generando bajo petición | 962 no cambia de horario, así que su huella queda intacta y es el testigo del acotamiento de REQ-52 | ✓ |
| Se retira de `huellas.yaml` | Barato; gasta el único testigo intacto que tenía la fase | |
| Se conserva congelada, sin generar | Conserva el registro; cuesta una rama nueva en `huella.py` y nadie vuelve a comprobar esa línea | |

**Elección:** conservar y generar bajo petición. → **D-10**

### Cómo se genera un grupo con `imparte: false`

| Opción | Descripción | Elegida |
|---|---|---|
| Una bandera del generador | Se salta por defecto; la suite de huellas la pasa siempre | ✓ |
| Se genera siempre; el campo solo se declara | Cero cambios en `generar.py`; el profesor imprime un DI de un grupo que no dará | |
| Se pide por número de grupo | Sin bandera nueva; hay que revisar cómo invoca la suite de huellas | |

**Elección:** bandera del generador. → **D-12**

---

## Medición del cambio de huella (REQ-52)

| Opción | Descripción | Elegida |
|---|---|---|
| Un informe en el directorio de la fase | Precedente de la Fase 9; queda en git y el commit lo referencia | ✓ |
| En el mensaje del commit de re-registro | Todo atado a la línea base; mensaje muy largo y fuera del alcance de una búsqueda | |
| Un comando `huella diff` | Reutilizable en fases futuras; hoy la huella compara shas, no textos — trabajo nuevo de verdad | |

**Elección:** informe en el directorio de la fase. → **D-11**, **D-14**

---

## Conflicto detectado durante la discusión

Al escribir D-13 se midió que `Curso.avisos` no se imprime en el `.docx` pero **sí entra al informe
de validación** (`validar.py:629`), y que la huella hashea ese informe — que es **por curso,
compartido entre los grupos** (`huella.py:50`). Meter el aviso en `avisos:` de 39056 habría movido
el hash `informe` del 962, quitándole a D-10 uno de sus tres campos intactos.

| Opción | Descripción | Elegida |
|---|---|---|
| Comentario YAML, no `avisos:` | No se carga, no entra al informe, no mueve ningún hash; D-10 sobrevive entero | ✓ |
| `avisos:` y D-10 se enuncia con precisión | La validación lo repite cada corrida; D-10 pasa a hablar solo de texto y manifiesto | |
| Ni comentario ni aviso | Cero riesgo; deja el jueves de relleno sin nada que lo explique | |

**Elección:** comentario YAML. → **D-13**

---

## Discreción de Claude

Redacción de los mensajes de error · nombres de campo dentro del bloque · hora como cadena o como
`datetime.time` · dónde vive la lógica de «siguiente día con bloque presencial» · nombre de la
bandera de D-12 · reparto en olas y orden de los planes.

## Ideas diferidas

Reescribir el DI de 961 para instruir sus cuatro sesiones semanales (decisión pedagógica del
profesor) · la materia 932, sin `curso.yaml` ni PUA · la exportación `.ics` (Fase 16) · el aula por
bloque · los salones pendientes de confirmar · WR-01 y WR-02 de `10-REVIEW.md`.
