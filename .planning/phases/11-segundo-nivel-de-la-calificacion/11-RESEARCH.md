# Fase 11: El segundo nivel de la calificación — Investigación

**Investigado:** 2026-08-06
**Dominio:** Modelo de datos (`dataclasses`) y regla de validación aritmética/semántica sobre un
contrato YAML ya abierto. No hay librerías externas nuevas ni ecosistema que explorar: esta fase es
100 % código propio sobre `src/modelo.py` y `src/validar.py`.
**Confianza:** ALTA — las 21 decisiones de `11-CONTEXT.md` ya fijan el diseño; esta investigación
remidió cada afirmación cuantitativa contra el árbol vivo y no encontró ninguna que hubiera
cambiado.

<user_constraints>
## User Constraints (from CONTEXT.md)

`.planning/phases/11-segundo-nivel-de-la-calificacion/11-CONTEXT.md` fija **21 decisiones (D-01 a
D-21)**, ya listas para planear. No se repiten aquí íntegras — viven en el archivo original — pero
se resumen sus tres bloques tal como el planeador debe tratarlos: como decisiones cerradas, como
discreción explícita, y como alcance fuera de la fase.

### Locked Decisions (D-01 a D-21 — no se negocian)

- **D-01/D-02/D-03:** `segundo_nivel:` es un **par fijo** `promedio`/`ordinario`, cada uno con
  `porcentaje` y `etiqueta` (obligatoria, literal del DI de origen). Vive como dataclasses propios
  `Nivel` y `SegundoNivel` en `modelo.py`; `Curso.segundo_nivel: SegundoNivel | None = None`.
- **D-04:** Los dos porcentajes se declaran; ninguno se deriva del otro.
- **D-05:** El catálogo (`zra-contabilidad` en `config/esquemas-evaluacion.yaml`) también declara su
  `segundo_nivel:` con los rótulos **literales** del DI de origen, y su comentario de las líneas
  66-68 se corrige.
- **D-06/D-07:** `exencion_contra:` es clave hermana de `exencion_ordinario:`, vocabulario cerrado
  `promedio | calificacion_final`, obligatoria cuando hay segundo nivel (su ausencia entonces es
  `ErrorModelo`); sin segundo nivel es opcional y ausente significa `promedio`. Sin default
  `"promedio"` en el dataclass — queda `= ""` y se lee `exencion_contra or "promedio"`.
- **D-08:** `exencion_contra: calificacion_final` **con** segundo nivel es **error de R1**, no
  `ErrorModelo`.
- **D-09:** `exencion_contra: calificacion_final` **sin** segundo nivel es **aviso de R1**.
- **D-10:** El renderizador **no cambia nunca** por esta clave (`politicas.yaml:98-103` ya dice
  «promedio»).
- **D-11:** Las comprobaciones nuevas van **dentro de `regla_1`**, después de los rubros duplicados
  y **antes** del bloque de `esquema_id` (`validar.py:154`). Nunca en un método auxiliar — rompería
  la cobertura silenciosa de la guarda `getsource`.
- **D-12:** La suma se compara contra `reglas["suma_exacta"]` de `esquemas-evaluacion.yaml:105`, con
  el mismo `round(..., 2)`.
- **D-13:** 100/0 o 0/100 es **aviso de R1**, no error.
- **D-14:** El contraste contra el catálogo se amplía al segundo nivel (porcentajes y etiquetas),
  aviso, en el mismo `if self.c.esquema_id:` donde ya vive el de los rubros.
- **D-15:** Restricción dura de nombres — el fuente de `regla_1` no puede contener `.base`,
  `a_porcentaje`, `.unidad`, `.total` ni `.valor` (verificado en este documento, ver «La guarda
  `getsource`»).
- **D-16:** `MANIFIESTO.yaml` registra `segundo_nivel` y `exencion_contra` en su bloque
  `evaluacion:` **solo cuando el curso los declara**.
- **D-17:** La clase `NoContaminacion` de `test_validar.py:691-724` se **extiende**, no se duplica.
- **D-18:** 38985 no se toca; su aviso nuevo (9→10 hallazgos) se acepta a propósito.
- **D-19:** El curso de prueba son variantes de `CURSO_VALIDO` por `deepcopy`, con los helpers
  `curso(**cambios)`/`informe(**cambios)` ya existentes.
- **D-20:** El cierre de REQ-48 es `python src/huella.py verificar` a mano.
- **D-21:** `grafo.py` no se toca — confirmado en este documento que no abre el bloque de
  evaluación.

### Claude's Discretion

- La redacción concreta de los mensajes nuevos de R1 (D-08, D-09, D-13, D-14), siguiendo el estilo
  de los existentes.
- Los nombres exactos de `Nivel` y `SegundoNivel`, sujetos a D-15.
- Si el aviso de D-13 distingue 100/0 de 0/100 con mensajes distintos o usa uno solo.
- Si el aviso del contraste de D-14 se emite junto al de los rubros o como hallazgo aparte.
- El orden de los planes de la fase y en cuál se actualiza `AGENTS.md`.

Esta investigación entrega materia prima concreta para las cinco (ver «Materia prima para el
criterio de Claude» y «La guarda `getsource`»), no opciones abiertas nuevas.

### Deferred Ideas (OUT OF SCOPE)

- Registrar `unidad:` y `total:` del rubro en `MANIFIESTO.yaml` — omisión real de la Fase 9,
  ofrecida junto a D-16 y **no adoptada**; candidata a la Fase 13.
- Una lista abierta `niveles:` en vez del par fijo (D-01) — solo pertinente si aparece un esquema
  con un tercer sumando.
- Que R1 juzgue si el umbral de exención tiene sentido dado el peso del ordinario — no lo pide
  ningún requisito.
- Una tolerancia numérica declarada en el config — cerrada también para esta fase (D-12 usa
  `round(..., 2)` existente).
- El prefijo `M0_` de Big Data y los `MANIFIESTO.yaml` sin `.pdf` de los cursos de control — abiertos
  desde la Fase 9, no son de esta fase.
- `/di-pua` sobre el PUA de 38985 — fuera del roadmap.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Descripción | Soporte de la investigación |
|----|-------------|------------------------------|
| REQ-41 | El esquema puede declarar un segundo nivel: promedio X % + ordinario Y %, X+Y=100; un curso que no lo declare se comporta como hoy. | Confirmado el punto exacto de carga (`modelo.py` `desde_dict`, entre `:400` y `:401`) y el patrón de construcción de `SegundoNivel` a partir de dos sub-dicts anidados (ver «Cómo se carga hoy el bloque `evaluacion:`»). Confirmado que un curso sin la clave no cambia ningún comportamiento (`Curso.segundo_nivel is None`, medido en 39056/39062: 0 hallazgos de R1 hoy y ninguna declaración de la clave). |
| REQ-46 | Con segundo nivel, R1 verifica que promedio+ordinario sumen 100, y que la exención quede declarada contra el promedio, no la calificación final. | Confirmados los dos puntos de inserción exactos en `regla_1` (`validar.py:126-169`, entre `:152` y `:154`) y la lista completa de tokens prohibidos que la guarda `getsource` vigila, con el contraste explícito de cada nombre de campo propuesto contra esa lista (ver «La guarda `getsource`»). Confirmada la forma real del contraste de catálogo que D-14 debe replicar (comparación de dos dicts completos, un solo aviso agregado). |
| REQ-48 | No contaminación: ningún rasgo de la v2.0 se activa si `curso.yaml` no lo declara; 39056/39062 producen la misma huella tras la fase. | Reproducidas las líneas base exactas (39056: 5 hallazgos, 0 de R1; 39062: 5, 0 de R1; 38985: 9, 0 de R1 — los tres válidos) corriendo `validar.py` de verdad. Confirmado que `grafo.py` no abre el bloque `evaluacion:` (grep completo del archivo, un solo punto de contacto en `:299` con `m.rubro`/`m.valor`). Documentadas las dos rutas de verificación (unit test rápido vs. `huella verificar` manual) y qué cubre cada una, en «Validation Architecture». |
| REQ-26 | `curso.yaml` es la fuente única de verdad; el renderizador no inventa nada. | Confirmado que `render_docx.py` no se toca en esta fase (D-10: la plantilla de `politicas.yaml` ya imprime la única frase que puede ser cierta) y que el `MANIFIESTO.yaml` (D-16) solo refleja lo que el curso declara explícitamente, sin inferir ni rellenar valores por defecto — ver «El MANIFIESTO y D-16». |
</phase_requirements>

## Resumen

Todo lo medido en `11-CONTEXT.md` se sostiene tal cual contra el código de hoy: los tres números de
línea citados en `validar.py` son exactos, los dos bloques citados en `esquemas-evaluacion.yaml` y
`politicas.yaml` son exactos, la clase `NoContaminacion` y la guarda `getsource` están donde se
dice, y las líneas base de hallazgos (0 de R1 en los tres cursos; 5/5/9 hallazgos totales) se
reprodujeron corriendo `validar.py` de verdad. La única línea que no cuadra al carácter es la cita a
`test_validar.py:104-112` para los helpers `curso()`/`informe()`: hoy viven en `:110-118` (drift de
6 líneas, sin consecuencia porque el contenido citado es correcto). En `modelo.py`, `desde_dict`
—donde entran las dos claves nuevas del bloque `evaluacion:`— vive en `:382-408`, no en `:395-405`
como cita el `<canonical_refs>` de la Fase 9; el rango citado cae *dentro* de la función real, así
que no hay contradicción, solo un rango más estrecho que el cuerpo completo.

**Recomendación primaria:** implementar D-01 a D-21 literalmente. No hay nada que investigar fuera
del propio código — el trabajo de esta fase es escribir dos dataclasses, extender un `__post_init__`,
insertar ~6 comprobaciones dentro de `regla_1` (nunca en un helper, por la guarda `getsource`), y
extender el contraste de catálogo y el `MANIFIESTO.yaml` con una inclusión condicional. El mayor
riesgo real no es de diseño sino de higiene textual: **cualquier comentario dentro de `regla_1` que
mencione `a_porcentaje` por contraste rompe la guarda** aunque el código en sí sea correcto.

## Mapa de responsabilidad arquitectónica

| Capacidad | Nivel primario | Nivel secundario | Razón |
|---|---|---|---|
| Declarar `segundo_nivel:` y `exencion_contra:` | Modelo (`modelo.py` — dataclasses + `__post_init__`) | Carga (`desde_dict`) | El contrato vive en el dataclass; la carga solo traduce YAML → objeto |
| Vocabulario cerrado de `exencion_contra` | Modelo (`ErrorModelo` si el valor no está en el vocabulario) | — | Defecto de esquema, no de aritmética (D-06/D-07, sigue D-03 Fase 9) |
| Suma 60+40=100, 100/0, 0/100, catálogo | Validación (`_Validador.regla_1`) | — | Aritmética e identidad son hallazgo de regla, nunca `ErrorModelo` |
| `exencion_contra: calificacion_final` con segundo nivel | Validación (`regla_1`, error) | — | Valor conocido y prohibido — juicio semántico, territorio de reglas (D-08) |
| Registrar en `MANIFIESTO.yaml` | Cierre (`generar.py:manifiesto()`) | — | Trazabilidad (regla invariable 7); solo si se declara (D-16) |
| Imprimir la exención en el documento | Renderizado — **no toca esta fase** | — | `politicas.yaml:98-103` ya dice «promedio»; D-10 lo congela |
| Grafo de dominio | **No aplica** — `grafo.py` no abre `evaluacion:` | — | D-21, medido: solo lee `m.rubro`/`m.valor` |

No hay tier de "Browser/Frontend/API/CDN/DB" en este proyecto: es un generador de documentos de
escritorio. La tabla anterior sustituye esa taxonomía por las cinco capas reales del proyecto
(modelo → carga → validación → cierre/manifiesto → renderizado), que es la arquitectura declarada en
`AGENTS.md`.

## Qué verifiqué contra el código vivo

### Líneas citadas en `validar.py` — exactas, sin drift

```
$ Read src/validar.py:1-240
```

- `Validador.error()` / `.aviso()`: **`:118-122`** — coincide exacto con la cita de `11-CONTEXT.md`.
- `regla_1` completa: **`:126-169`** — coincide exacto.
  - Salida temprana sin rubros: **`:130`** (`return` tras `self.error("R1", "El curso no declara rubros de evaluación.")`) — exacta.
  - Umbral de exención: **`:145-152`** — exacto.
  - Salida temprana por `esquema_id` desconocido: **`:160`** (`return` dentro del `except modelo.ErrorModelo`) — exacta.
  - Contraste contra el catálogo: **`:155-169`** — exacto, y el bloque abre en `:154` con el comentario
    `# Si se declaró un esquema del catálogo, debe coincidir con lo capturado.` — el límite que
    `11-CONTEXT.md` usa como frontera de D-11 es correcto: las comprobaciones nuevas van **antes**
    de la línea `154`.

**Conclusión:** el planeador puede citar estos números tal cual; no hay que remedirlos al escribir
el plan.

### Líneas citadas en `modelo.py`

- `Rubro`: **`:188-229`** — exacto (clase completa, incluyendo `a_porcentaje`).
- `Curso`: **`:271-333`** — exacto (dataclass + métodos hasta `nombre_archivo`).
- La carga desde YAML: la cita de `09-CONTEXT.md`/`11-CONTEXT.md` da `:395-405`, pero la función real
  `desde_dict` es **`:382-408`**. El rango citado (395-405) cae *dentro* de la función, cubriendo
  desde `contenido=d.pop(...)` hasta `avisos=d.pop("avisos", [])` — que incluye las dos líneas que
  hoy leen el bloque `evaluacion:` (`exencion_ordinario` en `:400`, `esquema_id` en `:401`). No es un
  drift real: es un rango parcial de una función que se movió un poco desde que Fase 9 escribió la
  cita original. **Para el plan: el punto exacto donde insertar la lectura de `segundo_nivel:` y
  `exencion_contra:` es entre `:400` y `:401`, dentro de la llamada a `Curso(...)`.**

  ```python
  # src/modelo.py:388-408 — Curso(...) tal como construye desde_dict() hoy
  return Curso(
      ciclo=meta["ciclo"],
      clave=str(meta["clave"]),
      nombre=d.pop("nombre", "") or ident.get("nombre", ""),
      modalidad=ident.get("modalidad", ""),
      profesor_id=d.pop("profesor", meta.get("profesor", "")),
      identificacion=ident,
      contenido=d.pop("contenido", {}),
      unidades=[Unidad(**u) for u in d.pop("unidades", [])],
      metas=[_construir_meta(dict(m)) for m in d.pop("metas", [])],
      rubros=[Rubro(**r) for r in evaluacion.get("rubros", [])],
      grupos=[_construir_grupo(g) for g in d.pop("grupos", [])],
      exencion_ordinario=evaluacion.get("exencion_ordinario", 80),
      esquema_id=evaluacion.get("esquema_id", ""),
      tolerancia_minutos=d.pop("tolerancia_minutos", 15),
      practica=ident.get("practica", False),
      citas=d.pop("citas", []),
      pua_ref=meta.get("pua_ref", ""),
      pua_sha256=meta.get("pua_sha256", ""),
      avisos=d.pop("avisos", []),
  )
  ```

- El comentario de `zra-contabilidad` en `esquemas-evaluacion.yaml`: **`:66-68`**, dice literalmente
  `"...un segundo nivel: el promedio vale 60 % y el examen ordinario 40 %. Ese segundo nivel NO
  existe en el modelo..."` — exacto, y D-05 lo vuelve falso.

### Líneas citadas en `config/`

- `esquemas-evaluacion.yaml`: bloque `zra-contabilidad` **`:59-82`** — exacto. Bloque `reglas` con
  `suma_exacta` **`:103-108`** — exacto (`suma_exacta: 100` en `:105`).
- `politicas.yaml`: criterio `exencion` **`:98-103`** — exacto, y su plantilla ya dice literalmente
  «obtener un **promedio** igual o mayor a {exencion}» (línea 100). Confirma D-10: no hace falta
  tocar este archivo nunca por `exencion_contra`, porque el único valor válido de esa clave en un
  curso que valida es siempre `promedio`.

### Líneas citadas en `pruebas/test_validar.py`

- `test_el_codigo_de_r1_no_menciona_la_unidad_de_ningun_rubro`: **`:287-292`** — exacto.
- `test_poner_un_rubro_en_puntos_no_altera_lo_que_r1_comprueba`: **`:281-285`** — exacto.
- Clase `NoContaminacion`: **`:691-724`** — exacto.
- Helpers `curso()` / `informe()`: la cita dice `:104-112`; en el árbol vivo son **`:110-118`**
  (`curso()` en `110-114`, `informe()` en `117-118`). Drift de 6 líneas — sin consecuencia para el
  plan, porque el contenido citado (la forma de los dos helpers) es idéntico; solo cambia el número.

### Líneas citadas en `src/generar.py`, `src/grafo.py`

- Bloque `evaluacion:` del manifiesto: **`:177-181`** — exacto (`"evaluacion": {"esquema_id": ...,
  "exencion_ordinario": ..., "rubros": [...]}`).
- `grafo.py`: el único punto donde se toca algo de la evaluación de una meta es **`:299`**
  (`{"clase": m.tipo, "rubro": m.rubro, "valor": m.valor, "semanas": m.semanas}`) — exacto. Grep de
  `evaluacion|rubro|esquema_id` en todo `grafo.py` no encuentra ningún otro punto que abra el bloque
  `evaluacion:` del curso. **D-21 queda confirmado, no solo repetido.**

### Las líneas base medidas — reproducidas de verdad

Comandos corridos (Windows, `python` sin `-X utf8`; la salida sale con mojibake por la consola CP1252
pero el conteo de líneas y hallazgos es correcto y no depende de la codificación):

```
$ python src/validar.py cursos/2026-2/39056-big-data/curso.yaml
5 hallazgos: [IEDI 2.4] [IEDI 3.1] [IEDI 3.2] [IEDI 3.5] [IEDI 4.1]  →  VÁLIDO
  R1: 0 hallazgos

$ python src/validar.py cursos/2026-2/39062-patrones-de-comportamiento/curso.yaml
5 hallazgos: [IEDI 2.4] [IEDI 3.1] [IEDI 3.2] [IEDI 3.5] [IEDI 4.1]  →  VÁLIDO
  R1: 0 hallazgos

$ python src/validar.py cursos/2026-2/38985-contabilidad-financiera/curso.yaml
9 hallazgos: 4 avisos [PUA] + 5 recordatorios [IEDI 2.4/3.1/3.2/3.5/4.1]  →  VÁLIDO
  R1: 0 hallazgos
```

Coincide exacto con D-17: **39056 y 39062 con 5 hallazgos cada uno, 38985 con 9, los tres con cero
hallazgos de R1 y los tres válidos.** El planeador puede escribir la prueba de no contaminación de
R1 sobre estos números sin volver a medir.

```
$ python -X utf8 -m unittest discover -s pruebas
Ran 245 tests in 16.550s
OK
```

**245 pruebas en verde**, coincide con `STATE.md` («245 pruebas en verde» al cerrar la Fase 10). No
hay drift entre el cierre de la Fase 10 y el arranque de la Fase 11 — nada tocó `pruebas/` entre
medio. Este es el número contra el que medir cuántas pruebas añade la Fase 11.

## Los rótulos literales

Fuente: `conocimiento/ejemplos/531-contabilidad-financiera-2026-1.md`, sección «Estructura de la
calificación» (`:46-80`; la tabla 1 con los rótulos exactos está en `:61-65`).

Tabla 1 del documento original, transcrita **carácter por carácter**, incluida la capitalización
irregular real del DI de origen:

| | |
|---|---|
| Valor del promedio antes del Examen Ordinario | 60 % |
| Valor del examen Ordinario | 40 % |
| Calificación de unidad de aprendizaje | 100 % |

Los dos rótulos que D-01/D-02/D-05 exigen como literales para `zra-contabilidad` en
`esquemas-evaluacion.yaml`:

```
"Valor del promedio antes del Examen Ordinario"
"Valor del examen Ordinario"
```

**Detalle que un agente corregiría por instinto y no debe corregir:** en el primer rótulo «Examen
Ordinario» lleva mayúscula en ambas palabras; en el segundo, «examen Ordinario» lleva la «e» de
«examen» en minúscula y solo «Ordinario» en mayúscula. Es una inconsistencia real de la docente en
su propio documento, no un error de transcripción de este repositorio. Si el catálogo «corrige» la
minúscula del segundo rótulo, deja de ser literal y D-05 advierte exactamente sobre ese riesgo: el
`curso.yaml` de la Fase 14 arrancaría con un aviso espurio de R1 en el contraste de D-14 el día que
declare el segundo nivel con el rótulo «corregido» y el catálogo no coincida.

La tercera fila («Calificación de unidad de aprendizaje», 100 %) **no** entra en `segundo_nivel:`:
D-01 fija el par como `promedio`/`ordinario` exclusivamente porque es lo único que el Estatuto
contempla; esa tercera fila es la suma derivada (100 %) y no un tercer sumando.

## La guarda `getsource`

`pruebas/test_validar.py:287-292`, transcrita:

```python
def test_el_codigo_de_r1_no_menciona_la_unidad_de_ningun_rubro(self):
    """La afirmación, escrita como prueba: si alguien mete aritmética de unidades en R1,
    esto se rompe y le obliga a decidirlo en vez de colarlo."""
    fuente = inspect.getsource(validar._Validador.regla_1)
    for termino in (".base", "a_porcentaje", ".unidad", ".total", ".valor"):
        self.assertNotIn(termino, fuente, f"R1 pasó a leer «{termino}»")
```

**Lista real de tokens prohibidos:** `.base`, `a_porcentaje`, `.unidad`, `.total`, `.valor` (cinco
literales, cada uno buscado como substring de todo el texto fuente de `regla_1`, **incluidos sus
comentarios y docstrings** — `inspect.getsource` devuelve el texto completo, no solo el código
ejecutable).

### Contraste con los nombres propuestos por D-03/D-15

| Nombre propuesto | ¿Colisiona? | Por qué |
|---|---|---|
| `porcentaje` (en `Nivel.porcentaje`) | No | Ya lo usa R1 hoy con los rubros (`r.porcentaje`); ningún token prohibido es substring de `porcentaje` |
| `etiqueta` | No | Sin relación con ningún token |
| `promedio` | No | Sin relación |
| `ordinario` | No | Sin relación |
| `segundo_nivel` | No | Sin relación — ni siquiera comparte letras con `.unidad`/`.total`/`.valor`/`.base` de forma que forme el substring exacto |
| `exencion_contra` | No | Sin relación |
| `Nivel` / `SegundoNivel` (nombres de clase) | No | Ninguno contiene los cinco tokens como substring |
| `self.c.segundo_nivel.promedio.porcentaje` (expresión completa) | **No** | No contiene `.total`, `.valor`, `.base`, `.unidad` ni `a_porcentaje` como substring literal — se verificó carácter por carácter |

**Ninguno de los ocho nombres colisiona.** El único punto real de riesgo, y el que `11-CONTEXT.md`
no señala explícitamente, es **textual, no de nombres de campo**:

> Si al escribir el código o un comentario dentro de `regla_1` alguien redacta una frase como *«a
> diferencia de R2, aquí no usamos `a_porcentaje` porque el segundo nivel ya está en
> porcentaje»* — esa frase **rompe la guarda**, aunque el código sea correcto y aunque el
> razonamiento sea cierto. `assertNotIn` no distingue código de comentario. El mismo riesgo existe
> con `.total` si alguien escribe, por ejemplo, `# el total de ambos niveles debe ser 100` usando la
> palabra sin punto — eso **no** rompe la guarda porque el token exacto es `.total` (con punto), no
> `total`. Pero escribir `Rubro.total` en un comentario explicando por qué R1 no lo necesita **sí**
> la rompe.

Ninguna variable local con estos nombres —`total = ...`, `total_segundo_nivel = ...`— rompe la
guarda: los cinco tokens llevan el punto o el prefijo exacto (`a_porcentaje`), y una variable local
sin punto delante no coincide. Solo hay que evitar escribir literalmente `.total`, `.valor`,
`.unidad`, `.base` o `a_porcentaje` en cualquier parte del texto de la función, código o prosa.

## Cómo se carga hoy el bloque `evaluacion:`

`desde_dict()` (`modelo.py:382-408`) hace `evaluacion = d.pop("evaluacion", {})` en `:385` y luego
lee de ahí dos claves sueltas al construir `Curso(...)`:

```python
exencion_ordinario=evaluacion.get("exencion_ordinario", 80),
esquema_id=evaluacion.get("esquema_id", ""),
```

Es el patrón exacto que D-06/D-07 deben replicar para `segundo_nivel:` y `exencion_contra:`. Falta
además construir el objeto `SegundoNivel` a partir del sub-dict (`evaluacion.get("segundo_nivel")`,
un dict con `promedio:` y `ordinario:`, cada uno `{"porcentaje": ..., "etiqueta": ...}`), lo que
requiere una pequeña función constructora — del mismo estilo que `_construir_componente` (`:339`) o
`_construir_grupo` (`:375`) — no una línea suelta, porque hay que convertir dos sub-dicts anidados en
dos `Nivel` antes de envolverlos en `SegundoNivel`. Ejemplo de la forma esperada:

```python
def _construir_segundo_nivel(sn: dict | None) -> SegundoNivel | None:
    if sn is None:
        return None
    return SegundoNivel(
        promedio=Nivel(**sn["promedio"]),
        ordinario=Nivel(**sn["ordinario"]),
    )
```

Y en `Curso(...)`:

```python
segundo_nivel=_construir_segundo_nivel(evaluacion.get("segundo_nivel")),
exencion_contra=evaluacion.get("exencion_contra", ""),
```

### El patrón de vocabulario cerrado que D-06 debe mirar

No hay que inventar el patrón: **ya existe dos veces** en `modelo.py`.

1. **A nivel de módulo, en `Curso.__post_init__`** (`:299-305`), el molde más directo para
   `exencion_contra` porque valida un campo de `Curso`, no de un dataclass anidado:

   ```python
   def __post_init__(self) -> None:
       if self.modalidad not in MODALIDADES:
           raise ErrorModelo(
               f"Modalidad inválida: {self.modalidad!r}. Válidas: {', '.join(MODALIDADES)}"
           )
       if not self.grupos:
           raise ErrorModelo("El curso debe tener al menos un grupo.")
   ```

   D-06/D-07 añaden aquí dos comprobaciones más: `exencion_contra` fuera del vocabulario cerrado (si
   no está vacía) es `ErrorModelo`, y `exencion_contra` vacía **con** `segundo_nivel is not None` es
   `ErrorModelo` (la obligatoriedad condicional de D-07).

2. **A nivel de dataclass anidado, en `Rubro.__post_init__`** (`:198-215`), el molde para cómo un
   dataclass se autovalida con un mensaje que explica qué falta y por qué — el patrón que D-03 dice
   seguir para `Nivel`/`SegundoNivel` si se decide que valen la pena sus propias comprobaciones
   (aunque D-01/D-02 ya hacen `etiqueta` y `porcentaje` obligatorios sin default, así que un
   `__post_init__` en `Nivel` probablemente no tiene nada que comprobar más allá de lo que el tipo ya
   garantiza — a menos que se quiera rechazar un `porcentaje` negativo, que ningún criterio del
   roadmap pide).

El vocabulario cerrado en sí se declara como constante de módulo, siguiendo `MODALIDADES`,
`TIPOS_META`, `UNIDADES_RUBRO`, `TIPOS_COMPONENTE` (todas en `:31-36`):

```python
EXENCION_CONTRA = ("promedio", "calificacion_final")  # el segundo es válido pero R1 lo rechaza (D-08)
```

## El MANIFIESTO y D-16

`generar.py:manifiesto()` (`:136-181`, el bloque `evaluacion:` en `:177-181`) construye **un único
`return {...}` literal** — no hay una variable intermedia que se vaya llenando ni un helper que
compone el dict por partes. Es exactamente la forma que hace que la inclusión condicional de D-16 sea
**una adición pequeña y localizada, no un refactor**: Python permite `**({...} if condición else {})`
dentro de un dict literal, así que el bloque `evaluacion:` pasa de:

```python
"evaluacion": {
    "esquema_id": curso.esquema_id,
    "exencion_ordinario": curso.exencion_ordinario,
    "rubros": [{"id": r.id, "porcentaje": r.porcentaje} for r in curso.rubros],
},
```

a:

```python
"evaluacion": {
    "esquema_id": curso.esquema_id,
    "exencion_ordinario": curso.exencion_ordinario,
    "rubros": [{"id": r.id, "porcentaje": r.porcentaje} for r in curso.rubros],
    **(
        {
            "segundo_nivel": {
                "promedio": {
                    "porcentaje": curso.segundo_nivel.promedio.porcentaje,
                    "etiqueta": curso.segundo_nivel.promedio.etiqueta,
                },
                "ordinario": {
                    "porcentaje": curso.segundo_nivel.ordinario.porcentaje,
                    "etiqueta": curso.segundo_nivel.ordinario.etiqueta,
                },
            },
            "exencion_contra": curso.exencion_contra or "promedio",
        }
        if curso.segundo_nivel is not None
        else {}
    ),
},
```

No hace falta `dataclasses.asdict()` (que además volcaría objetos anidados de más si algún día
`Nivel` gana más campos): construir el dict a mano deja explícito qué dos claves entran, que es
justo lo que D-16 pide («solo cuando el curso los declara»). No hay ningún otro punto de
`generar.py` que necesite cambiar: `manifiesto()` es la única función que arma este bloque, y ningún
llamador la envuelve.

**Confirmación cruzada con `huella.py`:** `forma_del_manifiesto()` (`huella.py:103-118`) hashea el
manifiesto completo salvo `generado`/`commit`/`sha256`/`bytes`. Con la inclusión condicional de
arriba, un curso de control que no declara `segundo_nivel:` sigue produciendo el mismo dict —sin
las claves nuevas— así que su hash de forma no cambia. Esto es la comprobación mecánica de que D-16
no rompe D-27 de la Fase 9.

## Materia prima para el criterio de Claude

### Los mensajes reales de R1 (verbatim, `validar.py:126-169`)

Los cuatro que existen hoy, todos f-strings, todos terminan en punto, todos interpolan valores
concretos del curso:

```python
"El curso no declara rubros de evaluación."

f"Los porcentajes del esquema suman {total:g}, no {exacta}: {desglose}."
# desglose = " + ".join(f"{r.etiqueta} {r.porcentaje:g}" for r in self.c.rubros)

f"Rubros duplicados: {', '.join(sorted(repetidos))}."

f"El umbral de exención ({ex}) queda fuera de "
f"[{reglas['exencion_minima']}, {reglas['exencion_maxima']}]. "
f"No puede ser menor que la calificación mínima aprobatoria (Art. 65)."

f"Los rubros del curso no coinciden con el esquema «{self.c.esquema_id}» "
f"del catálogo ({catalogo} contra {propio}). Si el cambio es "
f"intencional, quita `esquema_id` o registra un esquema nuevo."
```

Registro de estilo para los mensajes nuevos (D-08, D-09, D-13, D-14):

- Siempre f-string, siempre termina en punto.
- Interpola los valores reales del curso, no solo dice «está mal» (el mensaje del umbral de
  exención muestra `ex` y el rango válido; el del catálogo muestra los dos dicts completos).
- Cuando hay una salida, sugiere la acción (`"Si el cambio es intencional, quita \`esquema_id\`..."`).
  D-08 pide explícitamente «explicar la diferencia» entre medir contra el promedio y contra la
  calificación final — el molde de la última línea del mensaje del catálogo es el más cercano: decir
  qué pasó y qué hacer.
- Las citas de artículo van entre paréntesis al final: `"(Art. 65)"`. Si D-08/D-09 quieren anclar al
  Art. 68 (el que rige la exención), el molde es `"... (Art. 68)."`.

### D-13 — 100/0 y 0/100: ¿un mensaje o dos?

Los mensajes existentes de R1 son homogéneos en un aspecto: **cada comprobación tiene su propio
mensaje**, incluso cuando dos comprobaciones (rubros duplicados y suma incorrecta) podrían fundirse.
No hay precedente de un solo mensaje que cubra dos casos disjuntos con textos distintos según cuál
ocurrió — cuando el código distingue casos, el proyecto ha preferido mensajes separados
(`Rubros duplicados` vs. `Los porcentajes... suman`, aunque ambos vengan de la misma sección de
código). Un mensaje único con interpolación condicional («100/0» dice «no hay segundo nivel real»,
«0/100» dice «las metas no valen nada») rompería ese patrón. **Dato para el plan, no decisión
tomada:** el estilo existente favorece dos mensajes distintos (uno por caso), pero D-13 deja esto
explícitamente al criterio de Claude.

### D-14 — la forma real del contraste de catálogo (para decidir si se junta o no)

El contraste actual (`validar.py:161-169`) emite **un solo aviso agregado**, no uno por rubro
divergente:

```python
catalogo = {r["id"]: r["porcentaje"] for r in esquema["rubros"]}
propio = {r.id: r.porcentaje for r in self.c.rubros}
if catalogo != propio:
    self.aviso(
        "R1",
        f"Los rubros del curso no coinciden con el esquema «{self.c.esquema_id}» "
        f"del catálogo ({catalogo} contra {propio}). Si el cambio es "
        f"intencional, quita `esquema_id` o registra un esquema nuevo.",
    )
```

Es **una comparación de dos dicts completos**, no un bucle rubro por rubro: si tres rubros
divergieran, sale **un** aviso con los dos dicts enteros, no tres avisos. Esto es directamente
relevante para el criterio de Claude sobre D-14: «¿el aviso del segundo nivel se junta al de los
rubros o va aparte?». La forma natural que **mejor sigue el patrón existente** es un segundo `if`
independiente, con su propio par `catalogo`/`propio` construido sobre `segundo_nivel` en vez de
`rubros`, y su propio aviso — exactamente como el bloque de rubros, pero no fusionado dentro del
mismo `if`, porque el molde ya trata «divergencia de rubros» como una sola condición atómica y mezclar
las dos fuentes de divergencia en un mismo dict comparado oscurecería cuál de las dos cambió. La
alternativa —un solo aviso que compare ambos a la vez— exigiría construir un dict combinado
artificial solo para poder compararlo de un tirón, complejidad que el molde actual no tiene.

## Validation Architecture

### Framework de pruebas

| Propiedad | Valor |
|---|---|
| Framework | `unittest` (stdlib) — sin runner de terceros |
| Config | Ninguna — se descubre con `discover` |
| Comando rápido | `python -X utf8 -m unittest pruebas.test_validar -v` (o una clase concreta, p. ej. `pruebas.test_validar.Regla1Porcentajes`) |
| Suite completa | `python -X utf8 -m unittest discover -s pruebas` — **245 pruebas, 16.5 s hoy** |

### Comportamientos introducidos → mapa de pruebas

| # | Comportamiento | Tipo | Nivel de hallazgo | Comando (clase sugerida) | ¿Archivo existe? |
|---|---|---|---|---|---|
| B1 | `segundo_nivel` 60/40 válido → carga y valida sin error nuevo | unit | silencio | `Regla1SegundoNivel::test_60_40_valida` | ❌ clase nueva en `test_validar.py` |
| B2 | `segundo_nivel` 60/30 (no suma 100) | unit | **error** R1 | `Regla1SegundoNivel::test_60_30_es_error` | ❌ nueva |
| B3 | `segundo_nivel` presente, `exencion_contra` ausente | unit | **error** `ErrorModelo` al cargar | `test_modelo.py::SegundoNivel::test_exencion_contra_obligatoria` | ❌ nueva |
| B4 | `exencion_contra` fuera de vocabulario (ni `promedio` ni `calificacion_final`) | unit | **error** `ErrorModelo` al cargar | `test_modelo.py::SegundoNivel::test_vocabulario_cerrado` | ❌ nueva |
| B5 | `exencion_contra: calificacion_final` **con** segundo nivel | unit | **error** R1 | `Regla1SegundoNivel::test_calificacion_final_con_segundo_nivel_es_error` | ❌ nueva |
| B6 | `exencion_contra: calificacion_final` **sin** segundo nivel | unit | **aviso** R1 | `Regla1SegundoNivel::test_calificacion_final_sin_segundo_nivel_es_aviso` | ❌ nueva |
| B7 | 100/0 | unit | **aviso** R1 | `Regla1SegundoNivel::test_100_0_es_aviso` | ❌ nueva |
| B8 | 0/100 | unit | **aviso** R1 | `Regla1SegundoNivel::test_0_100_es_aviso` | ❌ nueva |
| B9 | Contraste catálogo: porcentajes y/o etiquetas divergen | unit | **aviso** R1 | `Regla1SegundoNivel::test_avisa_si_diverge_del_catalogo` | ❌ nueva |
| B10 | Curso sin `segundo_nivel` → cero cambio de comportamiento | unit | silencio | ya cubierto por `PuntoDePartida` + `NoContaminacion` existentes | ✓ existe, se extiende |
| B11 | Manifiesto registra `segundo_nivel`/`exencion_contra` solo si se declaran | unit | — (estructural) | `test_generar.py::Manifiesto::test_registra_segundo_nivel_solo_si_se_declara` | ❌ nueva (o clase existente de `test_generar.py`, a confirmar leyendo ese archivo) |
| B12 | La guarda `getsource` sigue sin ver `.base`/`a_porcentaje`/`.unidad`/`.total`/`.valor` | unit — **estructural** | — | `test_el_codigo_de_r1_no_menciona_la_unidad_de_ningun_rubro` | ✓ existe, **no se toca**; falla sola si el plan mete un token prohibido |
| B13 | 39056/39062/38985 no cambian su conteo de hallazgos de R1 (0/0/0) tras esta fase | unit | silencio | `NoContaminacion::test_los_cursos_de_control_no_emiten_un_solo_hallazgo_de_r1` | ❌ nueva (hermana de la de R2/R3 ya existente) |
| B14 | 39056/39062 no declaran ni `segundo_nivel:` ni `exencion_contra:` en su YAML | unit — texto crudo | — | extiende `test_los_cursos_de_control_no_declaran_nada_de_la_v2` | ✓ existe, se extiende (D-17) |
| B15 | Cierre REQ-48: huella de texto/informe/manifiesto de 39056 y 39062 intacta | manual, fuera de la suite | — | `python src/huella.py verificar` | ✓ existe, D-20 |

**Tasa de muestreo (Nyquist) de esta fase:** 15 comportamientos distintos, de los cuales 8 son
combinaciones de la aritmética/vocabulario del segundo nivel (B1-B9 sin contar B10), 2 son silencio
puro (B10, B14 — los más difíciles de verificar porque «no pasó nada» no es observable sin comparar
contra una línea base, que es justo lo que REQ-48 exige) y 1 es estructural (B12, ya construida en
la Fase 10). El mínimo que cubre cada comportamiento **una vez** es exactamente la tabla de arriba:
9 pruebas nuevas de `regla_1`, 2 de `modelo.py` (vocabulario y obligatoriedad), 1 de `generar.py`
(manifiesto condicional), 1 nueva de no-contaminación en R1, y la extensión de la prueba de texto
crudo existente. **10-12 pruebas nuevas es la cifra realista**, no 15 — varias de la tabla se
resuelven con `subTest` dentro de una sola clase (p. ej. B7/B8 como dos `subTest` de un mismo test de
100/0 y 0/100 si D-13 termina usando un mensaje parametrizado, o dos tests si usa mensajes
distintos — ver el hallazgo de la sección anterior).

### Cuáles pruebas existentes NO deben romperse, y cuáles son guardas estructurales frágiles

| Prueba | Por qué es frágil | Qué la protege |
|---|---|---|
| `test_el_codigo_de_r1_no_menciona_la_unidad_de_ningun_rubro` | Si el plan saca la aritmética nueva a un método auxiliar, **deja de cubrir nada, en silencio** — no falla, solo deja de vigilar (D-11 lo señala explícitamente) | Escribir todo dentro de `regla_1`, nunca en un helper |
| `test_poner_un_rubro_en_puntos_no_altera_lo_que_r1_comprueba` | Compara mensajes de R1 con/sin rubros en puntos; si el segundo nivel introduce algo que sí lee la unidad de un rubro, esta prueba lo detecta como cambio de mensajes, no como fallo explícito — hay que leer el diff, no solo el resultado en verde | No referenciar `Rubro.unidad`/`.base`/`.total` desde el código del segundo nivel |
| `test_el_total_correcto_no_absuelve_al_rubro_incorrecto` (Fase 10, `:180-186`) | Ya es frágil por D-07 de la Fase 10: exige el prefijo literal `"El valor de las metas suma"`. Esta fase no toca ese mensaje, pero si algún refactor de R1 lo rozara sin querer, la prueba se volvería tautológica sin fallar | No tocar el hallazgo global de R2 en esta fase — no es su territorio |
| `test_detecta_el_defecto_del_ejemplo_961` | Solo comprueba que aparezcan las etiquetas «Proyecto final» y «Exámenes» — es holgada, no una garantía fuerte. No la toca esta fase, pero si algún día se reformula el mensaje de R2 hay que releerla con cuidado | Fuera del alcance de esta fase (R2 no se toca) |

### REQ-48 — las dos rutas de verificación y qué atrapa cada una

| Ruta | Qué cubre | Qué NO cubre |
|---|---|---|
| Unit test (`NoContaminacion`, ciclo rápido) | El **silencio** de R1 sobre 39056/39062: cero hallazgos, y que su YAML crudo no declare las dos claves nuevas. Corre en cada `unittest discover`, segundos. | El texto del `.docx` renderizado — `NoContaminacion` no genera documentos (D-18 de la Fase 9: la generación completa es lenta y depende de las plantillas) |
| `python src/huella.py verificar` (manual, D-20) | El texto **completo** del `.docx` de los cuatro documentos de control, el informe de validación completo (no solo R1) y la **forma** del `MANIFIESTO.yaml` (D-27) — es la única ruta que verificaría que D-16 no metió `segundo_nivel`/`exencion_contra` en el manifiesto de un curso de control que no los declara | Corre a mano, no en CI/pre-commit; si se olvida, una regresión de forma del manifiesto pasa inadvertida hasta que alguien lo corra |

**Ambas rutas son necesarias y no se solapan del todo**: el unit test es la única que corre siempre
(atrapa una regresión de R1 en cada commit); `huella verificar` es la única que ve el `.docx` y la
forma del manifiesto (atrapa una regresión de D-16 que el unit test, al no invocar `generar.paquete`
sobre los cursos de control, no vería). El plan de cierre de la fase debe correr **las dos**, en ese
orden.

### Huecos de Wave 0

- `pruebas/test_validar.py` — no existe todavía una clase `Regla1SegundoNivel` (o el nombre que el
  plan elija): es donde van B1-B9 y B13.
- `pruebas/test_modelo.py` — no existe todavía una clase para `Nivel`/`SegundoNivel`/
  `exencion_contra` (molde: las clases `RubroEnPuntos` y `ComponentesDeMeta` ya existen en ese
  archivo con el mismo estilo de fixture por `deepcopy`).
- `pruebas/test_generar.py` — hay que leer su contenido actual antes de decidir si el manifiesto
  condicional (B11) entra en una clase existente o necesita una nueva; no se leyó en esta
  investigación porque D-16 no lo cita como referencia obligatoria, pero el plan debe abrirlo.
- Ningún framework nuevo, ninguna dependencia nueva. Los fixtures se construyen con el patrón
  `curso(**cambios)` / `informe(**cambios)` que D-19 ya fija como decisión, no como hueco.

**No hay ninguna instalación de framework pendiente** — `unittest` ya cubre todo.

## Riesgos y trampas

1. **La trampa textual de la guarda `getsource` (ver sección dedicada arriba).** Es el riesgo más
   real de la fase porque no se detecta leyendo el diseño: solo se ve corriendo la prueba. Cualquier
   comentario que compare el segundo nivel con la conversión de puntos usando la palabra
   `a_porcentaje` la rompe en silencio de intención, ruidosamente en ejecución (falla con un mensaje
   claro) — así que en la práctica **no pasa inadvertida**, pero puede consumir un ciclo de
   corrección evitable si no se sabe de antemano.

2. **`desde_dict` no valida contra `TypeError` de forma amigable si `segundo_nivel:` llega con una
   forma inesperada** (p. ej. `promedio:` sin `porcentaje:`). Hoy `cargar()` (`:433-446`) atrapa
   `TypeError` y lo traduce a `ErrorModelo(f"{ruta}: campo inesperado o faltante — {e}")`
   genéricamente — es el mismo mecanismo que ya protege `Rubro(**r)` y `_construir_meta`, así que no
   hace falta nada nuevo, pero el mensaje resultante para un YAML mal formado será genérico
   («campo inesperado o faltante») y no el mensaje pedagógico específico de D-06/D-07. Es aceptable
   —sigue el patrón existente— pero el plan no debe prometer un mensaje específico para *cualquier*
   forma mal escrita, solo para los dos casos que D-06/D-07 nombran explícitamente (vocabulario y
   obligatoriedad).

3. **El `SKILL.md` de `di-validar` ya está desincronizado desde la Fase 10, y esta fase lo profundiza
   si no se toca.** `.claude/skills/di-validar/SKILL.md:34-35` reproduce una tabla resumen de las
   ocho reglas que describe R1 como «Los porcentajes del esquema suman exactamente 100; la exención
   cae en [60, 100]» y R2 como «Las metas suman lo que declara el esquema — rubro por rubro, no solo
   en total» — **esta última frase ya no refleja la Fase 10** (que añadió componentes y unidad de
   rubro a R2) y nadie la actualizó entonces. `di-validar` en sí **no necesita cambio funcional**:
   invoca `src/validar.py` como subproceso y solo reporta lo que sale, así que las comprobaciones
   nuevas de R1 llegan automáticamente al usuario sin tocar el skill. Lo que sí queda como deuda
   documental, igual que el hueco que la Fase 10 dejó abierto en `AGENTS.md` §Contrato: si el plan
   de esta fase actualiza `AGENTS.md` §«Las ocho reglas» (que el `<canonical_refs>` de
   `11-CONTEXT.md` exige en el mismo plan), sería consistente actualizar también esta tabla — pero
   no es un requisito de la fase y `11-CONTEXT.md` no lo pide. Se anota para que el planeador decida
   con la información completa, no para forzar una tarea nueva.

4. **`Curso.exencion_ordinario` y `Curso.exencion_contra` son conceptualmente una sola decisión
   partida en dos campos** (D-06 lo reconoce explícitamente: «separaría el umbral (fuera) de su
   referencia (dentro)»). El riesgo de implementación es que alguien lea `exencion_ordinario` sin
   comprobar `exencion_contra` en algún punto futuro (Fase 13, el renderizado de la tabla de dos
   niveles) y asuma silenciosamente que siempre es contra el promedio. D-10 ya blinda esto para el
   renderizador actual (la plantilla de `politicas.yaml` es fija), pero **cualquier código nuevo que
   lea `exencion_ordinario` en fases futuras debe leer también `exencion_contra` o heredar la
   garantía de que un curso válido siempre la tiene en `promedio`** — es una invariante que vive en
   R1, no en el tipo, así que no hay protección del compilador.

5. **`total_metas`/`total_rubros` en R2 ya usan la palabra `total` como nombre de variable local**
   (`validar.py:200,207`) sin que eso rompa nada en R1: son de `regla_2`, no de `regla_1`, y la
   guarda `getsource` solo inspecciona `regla_1`. No es un riesgo real, pero vale la pena que el
   planeador sepa que la palabra suelta `total` (sin punto) es segura en cualquier parte del
   proyecto — solo `.total` (con punto, como atributo) está vigilado, y solo dentro de `regla_1`.

6. **Nada de esta fase depende de herramientas externas** (no hay Word, no hay PDF, no hay
   plantillas) — la sección «Environment Availability» no aplica y se omite deliberadamente.

## Fuentes

### Primarias (confianza ALTA — leídas directamente del árbol vivo)

- `AGENTS.md` completo — contrato canónico, arquitectura, contexto de dominio.
- `.planning/phases/11-segundo-nivel-de-la-calificacion/11-CONTEXT.md` — las 21 decisiones.
- `.planning/phases/10-reglas-en-la-unidad-declarada/10-CONTEXT.md` y
  `.planning/phases/09-valor-de-una-meta/09-CONTEXT.md` — decisiones heredadas citadas arriba.
- `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md` (Fase 11), `.planning/STATE.md`.
- `src/modelo.py`, `src/validar.py`, `src/generar.py`, `src/grafo.py`, `src/huella.py` — leídos en
  los rangos exactos citados en `11-CONTEXT.md` y verificados carácter por carácter donde se indica.
- `config/esquemas-evaluacion.yaml`, `config/politicas.yaml`.
- `pruebas/test_validar.py`, `pruebas/test_modelo.py` — leídos y grepeados para confirmar clases y
  fixtures existentes.
- `conocimiento/ejemplos/531-contabilidad-financiera-2026-1.md:46-80` — los rótulos literales.
- `.claude/skills/di-validar/SKILL.md` — para responder la pregunta explícita sobre si necesita
  actualizarse.
- `.planning/config.json` — `nyquist_validation: true`, `security_enforcement: false`.
- Ejecución real: `python src/validar.py` sobre los tres cursos, y
  `python -X utf8 -m unittest discover -s pruebas` (245 pruebas, verde).

### Secundarias / terciarias

Ninguna. Esta fase no requirió Context7, WebSearch ni ninguna fuente externa: es código propio del
repositorio y el diseño ya está fijado por `11-CONTEXT.md`.

## Metadata

**Desglose de confianza:**
- Stack estándar: N/A — no hay librerías nuevas.
- Arquitectura: ALTA — las 21 decisiones de `11-CONTEXT.md` ya fijan cada punto de integración, y
  todos los números de línea que citan se remidieron exactos (salvo el drift menor y sin consecuencia
  de `:104-112` → `:110-118` en un helper de prueba).
- Pitfalls: ALTA — el riesgo principal (la guarda `getsource`) se verificó leyendo el código real de
  la prueba, no se infirió del contexto.

**Fecha de investigación:** 2026-08-06
**Válida hasta:** mientras nadie toque `src/validar.py`, `src/modelo.py` o
`pruebas/test_validar.py` fuera de esta fase — es decir, hasta que se planee o ejecute la Fase 11.
Si otra fase se planea antes (fuera de orden), remedir antes de usar este documento.
