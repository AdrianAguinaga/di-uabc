# Fase 11: El segundo nivel de la calificación — Registro de la discusión

> **Solo traza de auditoría.** No se usa como entrada de los agentes de investigación, planeación ni
> ejecución. Las decisiones viven en `11-CONTEXT.md`; este registro conserva las alternativas que se
> consideraron y se descartaron.

**Fecha:** 2026-08-06
**Fase:** 11 — El segundo nivel de la calificación
**Áreas discutidas:** Forma del contrato · La exención y R1 · Alcance de R1 · Huella y manifiesto
**Modo:** conversacional (sin advisor — no existe `USER-PROFILE.md`)

---

## Selección de áreas

| Opción | Descripción | Elegida |
|---|---|---|
| Forma del contrato | Claves, valores declarados o derivados, etiquetas | ✓ |
| La exención y R1 | Dónde choca el criterio 3 con el precedente D-03 | ✓ |
| Alcance de R1 | Qué comprueba además de la suma; el contraste con el catálogo | ✓ |
| Huella y manifiesto | El cierre de REQ-48 | ✓ |

**Elección:** las cuatro.

---

## Forma del contrato

### ¿Qué forma toma el segundo nivel en `curso.yaml`?

| Opción | Descripción | Elegida |
|---|---|---|
| Par fijo con nombre | `segundo_nivel:` con claves `promedio:` y `ordinario:` | ✓ |
| Lista de niveles | `niveles:` con id, etiqueta y porcentaje, hermana de `rubros:` | |

**Razón registrada:** la lista obliga a R1 a identificar por id cuál fila es el promedio para poder
aplicar el criterio 3, a cambio de una generalidad que el Estatuto no contempla. → D-01

### ¿Las etiquetas son del contrato o las fija la Fase 13?

| Opción | Descripción | Elegida |
|---|---|---|
| Del contrato, obligatorias | Como `Rubro.etiqueta` | ✓ |
| Del contrato, opcionales | Con texto por defecto del renderizador, como `Rubro.detalle` | |
| Las fija la Fase 13 | Rótulos en el renderizador o en `politicas.yaml` | |

**Razón registrada:** REQ-26 queda intacto y otra docente con otra redacción no necesita que se
toque código. → D-02

### ¿Cómo vive en `modelo.py`?

| Opción | Descripción | Elegida |
|---|---|---|
| Dataclass propio | `Nivel` + `SegundoNivel`; `Curso.segundo_nivel: SegundoNivel \| None` | ✓ |
| Campos sueltos en Curso | `peso_promedio` / `peso_ordinario` con default | |

**Razón registrada:** con campos sueltos, «no declarado» se vuelve indistinguible de «declarado 100
y 0», y REQ-41 exige distinguirlos. → D-03

**Restricción presentada con la pregunta:** `test_el_codigo_de_r1_no_menciona_la_unidad_de_ningun_rubro`
prohíbe `.valor`, `.total`, `.base` y `.unidad` en el fuente de R1. → D-15

### ¿Se declara también en el catálogo?

| Opción | Descripción | Elegida |
|---|---|---|
| Solo en `curso.yaml` | El catálogo solo corrige su comentario obsoleto | |
| También en el catálogo | `zra-contabilidad` declara su 60/40 y R1 amplía su contraste | ✓ |

**Razón registrada:** el catálogo queda describiendo el esquema completo. → D-05, y arrastra D-14 y
D-18.

---

## La exención y R1

**Contexto medido y presentado antes de preguntar:**
- `config/politicas.yaml:98-103` ya rinde «obtener un **promedio** igual o mayor a {exencion}».
- D-03 de la Fase 9 (vocabulario cerrado → `ErrorModelo`) habla de valores *desconocidos*, no de
  valores conocidos y prohibidos: el choque aparente con el criterio 3 no es tal.
- Para que R1 pueda explicar la diferencia, el vocabulario tiene que admitir el valor malo.

### ¿Cómo se declara contra qué se mide la exención?

| Opción | Descripción | Elegida |
|---|---|---|
| Clave `exencion_contra:` | Hermana de `exencion_ordinario:`, vocabulario cerrado | ✓ |
| Dentro de `segundo_nivel:` | Todo el rasgo en un sitio | |
| Sin clave nueva | Significado fijado por documentación | |

**Razón registrada:** meterla dentro del bloque separaría el umbral de su referencia, que son la
misma decisión partida en dos. Sin clave, el criterio 3 se queda sin forma de probarse. → D-06

### ¿Dónde falla `calificacion_final` con segundo nivel?

| Opción | Descripción | Elegida |
|---|---|---|
| Error de R1 | El curso carga, se puede inspeccionar, y falla al validar | ✓ |
| ErrorModelo al cargar | El curso no carga | |

**Razón registrada:** es la letra del criterio 3 y el precedente D-17/D-08. → D-08

### ¿Es obligatoria cuando hay segundo nivel?

| Opción | Descripción | Elegida |
|---|---|---|
| Obligatoria con 2º nivel | Ausente sin segundo nivel = `promedio`; con él, `ErrorModelo` | ✓ |
| Siempre opcional | Ausente = `promedio` en todos los casos | |

**Razón registrada:** sigue D-26 de la Fase 9 y obliga a enfrentar la pregunta justo donde tiene
consecuencias. → D-07

**Consecuencia derivada durante la discusión:** el campo no puede llevar `"promedio"` como default,
o «ausente» y «declarado» serían indistinguibles.

### ¿Y sin segundo nivel?

| Opción | Descripción | Elegida |
|---|---|---|
| Aviso de R1 | No hay diferencia que medir, pero se señala | ✓ |
| Error de R1 | Una sola regla, sin caso especial | |
| Nada | Pasa en silencio | |

**Razón registrada:** aritméticamente no está mal; solo se volverá falso si algún día se añade el
segundo nivel. → D-09

---

## Alcance de R1

**Contexto medido y presentado antes de preguntar:**
- `regla_1` tiene dos salidas tempranas (`validar.py:130` y `:160`); la segunda dispara justo en un
  curso que declara `esquema_id`, que es el perfil del curso motivador.
- La prueba `getsource` solo lee el fuente de `regla_1`: un método auxiliar la dejaría sin cobertura
  en silencio.

### ¿Qué contrasta R1 del segundo nivel contra el catálogo?

| Opción | Descripción | Elegida |
|---|---|---|
| Solo los porcentajes | Mismo trato que `Rubro.etiqueta` y `Rubro.detalle`, que quedan fuera | |
| Porcentajes y etiquetas | El catálogo pasa a ser la redacción canónica del esquema | ✓ |
| Nada | El catálogo lo declara pero R1 no lo mira | |

**Consecuencia señalada al registrar:** `zra-contabilidad` debe llevar los rótulos literales del DI
de origen, o la Fase 14 arrancará con un aviso espurio. → D-14

### ¿Un segundo nivel de 100/0 es válido?

| Opción | Descripción | Elegida |
|---|---|---|
| Aviso de R1 | Suma 100, no hay error, pero se señala | ✓ |
| Error de R1 | Casi siempre es un dedazo | |
| Válido, sin hallazgo | R1 solo comprueba lo que REQ-46 pide | |

→ D-13

### ¿Dónde vive el código de las comprobaciones nuevas?

| Opción | Descripción | Elegida |
|---|---|---|
| Dentro de `regla_1`, arriba | Antes del bloque de `esquema_id`, tras los rubros duplicados | ✓ |
| Método auxiliar | `_segundo_nivel()` llamado desde `regla_1` | |
| Regla propia (R9) | Aísla el rasgo por completo | |

**Razón registrada:** el auxiliar dejaría la guarda `getsource` sin cobertura; R9 cambiaría el
número de reglas del proyecto y haría que el informe de cursos sin segundo nivel mencionara una
regla que no aplica — riesgo contra REQ-48. → D-11

### ¿Contra qué 100 se comprueba la suma?

| Opción | Descripción | Elegida |
|---|---|---|
| El `suma_exacta` del config | El mismo número que gobierna la suma de los rubros | ✓ |
| Una regla propia en el config | Por si los dos niveles divergen algún día | |
| 100 literal en el código | Aritmética de porcentajes, no criterio configurable | |

→ D-12

---

## Huella y manifiesto

**Contexto medido y presentado antes de preguntar:**
- `grafo.py:299` solo lee `m.rubro` y `m.valor`: el segundo nivel no lo toca. → D-21
- La Fase 9 **no** extendió el manifiesto con `unidad:` ni `total:`: hay precedente de que un rasgo
  nuevo del contrato no llegue allí.
- Como `calificacion_final` es siempre error, un curso válido tiene siempre `exencion_contra:
  promedio` — que es lo que la plantilla de `politicas.yaml` ya afirma. El renderizador no cambia. → D-10

### ¿El segundo nivel llega al `MANIFIESTO.yaml`?

| Opción | Descripción | Elegida |
|---|---|---|
| Entra si se declara | Condicional; los cursos de control no cambian ni un byte | ✓ |
| No entra | Precedente de la Fase 9; cero riesgo y cero código | |
| Entra, y se corrige la Fase 9 | Además, `unidad:` y `total:` del rubro | |

**Nota:** la opción de entrada incondicional no se ofreció — rompería REQ-48. La tercera se ofreció
marcada como trabajo fuera de los requisitos de la fase y **no se adoptó**; queda como idea
diferida. → D-16

### ¿Qué se fija en el ciclo rápido de pruebas?

| Opción | Descripción | Elegida |
|---|---|---|
| Extender la prueba de la 10 | Añadir las claves nuevas a la clase `NoContaminacion` | ✓ |
| Prueba hermana propia | Específica del segundo nivel | |
| Solo `huella verificar` | Sin cobertura en el ciclo rápido | |

**Medición hecha después de elegir, para que la prueba no se escriba a ojo:** hoy 39056, 39062 y
38985 emiten **cero hallazgos de R1** y los tres son válidos (5, 5 y 9 hallazgos en total). → D-17

### ¿Qué hacemos con el aviso nuevo sobre 38985?

| Opción | Descripción | Elegida |
|---|---|---|
| Se acepta el aviso | D-13 de la Fase 10 sigue valiendo; el aviso dice la verdad | ✓ |
| Quitarle el `esquema_id` | Su informe queda limpio | |
| Declararle el segundo nivel ya | Un paso más cerca de su forma real | |

**Razón registrada:** las otras dos tocan el archivo blindado o le comen a la Fase 14 parte de su
criterio 1. → D-18

### ¿Cómo se organiza el curso de prueba?

| Opción | Descripción | Elegida |
|---|---|---|
| Variantes de `CURSO_VALIDO` | `deepcopy` con los helpers existentes | ✓ |
| Fixture propio | `CURSO_CON_SEGUNDO_NIVEL` hermano de los de la Fase 10 | |

**Razón registrada:** el rasgo es aditivo y ortogonal a los rubros. → D-19

---

## Criterio de Claude

Registrado en `11-CONTEXT.md` §«Criterio de Claude»: la redacción de los mensajes nuevos de R1, los
nombres exactos de los dataclasses (sujetos a D-15), si el aviso de extremos distingue 100/0 de
0/100, si el aviso del contraste se emite junto al de los rubros, y el orden de los planes de la
fase.

## Ideas apartadas

Registradas en `11-CONTEXT.md` §«Ideas apartadas». La única que surgió de esta discusión y no venía
de fases anteriores es **registrar `unidad:` y `total:` del rubro en el manifiesto** — la omisión de
la Fase 9, ofrecida y no adoptada.
