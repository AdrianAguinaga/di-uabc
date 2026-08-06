---
phase: 10-reglas-en-la-unidad-declarada
reviewed: 2026-08-06T17:12:49Z
depth: standard
files_reviewed: 4
files_reviewed_list:
  - src/modelo.py
  - src/validar.py
  - pruebas/test_modelo.py
  - pruebas/test_validar.py
findings:
  critical: 0
  warning: 3
  info: 5
  total: 8
status: issues_found
---

# Fase 10: Informe de revisión de código

**Revisado:** 2026-08-06T17:12:49Z
**Profundidad:** standard
**Archivos revisados:** 4
**Estado:** issues_found

## Resumen

Se revisó el diff contra `4e7f2f0`: el dataclass `Aporte` y el generador `Curso.aportes()` en
`src/modelo.py`, la reescritura de `regla_2` y `regla_3` en `src/validar.py`, y las dos suites de
prueba. Las 89 pruebas de ambos archivos pasan (24 + 65).

Los cuatro puntos que el encargo pidió vigilar salen bien, y tres de ellos se comprobaron
ejecutando código, no leyendo:

- **Aritmética de coma flotante.** La conversión una vez por rubro (`validar.py:200-206`) es
  correcta y `test_veintidos_aportes_de_puntos_exactos_no_inventan_un_faltante` la fija con el caso
  medido. La única igualdad exacta sobre flotantes problemática está en WR-01, y es de forma
  heredada, no del reparto por rubro.
- **Unidades mezcladas.** `regla_2` compara siempre dentro de un rubro y contra su propia `base`
  (`validar.py:218-228`); no hay ninguna suma que cruce rubros en unidad cruda. El único punto donde
  se suman rubros distintos (`total_metas`) opera sobre valores ya convertidos a porcentaje.
- **División por cero o por `None`.** `Rubro.__post_init__` garantiza `total > 0` cuando
  `unidad == "puntos"`, y `a_porcentaje` corta con `if not self.base`. Verificado: un rubro con
  `porcentaje: 0` devuelve `0.0` en vez de reventar. (Un `porcentaje: null` explícito sí revienta con
  `TypeError` sin envolver, pero eso es anterior a esta fase y no lo toca el diff.)
- **Aportes a un rubro inexistente.** Se denuncian por separado para metas y componentes y quedan
  fuera de las dos sumas, tal como afirma el comentario de `validar.py:195-199`.

Lo que sí encuentra la revisión son tres huecos: un falso positivo de R2 por redondear solo un lado
de la comparación (WR-01), un agujero nuevo en R3 —un componente `examen_parcial` sin valor ni
evidencia satisface el artículo 68 y el curso entero valida (WR-02)— y un `Aporte` declarado
`frozen=True` que no es hashable (WR-03). Ninguno es de seguridad.

## Advertencias

### WR-01: R2 redondea la suma pero no la base, y denuncia un curso correcto

**Archivo:** `src/validar.py:220-221`
**Problema:** `suma` se redondea a dos decimales y se compara contra `r.base` **sin redondear**.
Si un rubro declara una base con más de dos decimales, la comparación falla aunque los aportes sumen
exactamente lo declarado. Medido sobre este código:

```
Rubro «Exámenes»: sus aportes suman 16.66 % pero el rubro declara 16.665 %.
Aportes imputados: Meta P1, Meta P2.
```

—con `porcentaje: 16.665` y dos metas de `8.3325`, que suman los 16.665 exactos—. Es la misma forma
que tenía la línea antes de la fase (`suma != r.porcentaje`), así que el defecto es heredado; lo que
cambia es que ahora el lado derecho es `base`, que también puede ser un `total` en puntos, y los
totales fraccionarios (`total: 12.5`) son plausibles en un rubro de prácticas.

D-06 descartó a propósito una tolerancia explícita (`math.isclose`, epsilon en configuración). No
hace falta ninguna: basta redondear los dos lados con el mismo criterio, que es lo que la decisión
ya asume al decir «se combina con el `round(..., 2)` que `validar.py` ya usa».

**Arreglo:**

```python
        for r in self.c.rubros:
            aportes = [a for a in self.c.aportes() if a.rubro == r.id]
            suma = round(sum(a.valor for a in aportes), 2)
            base = round(r.base, 2)          # el mismo criterio en los dos lados
            if suma != base:
                unidad = "pts" if r.unidad == "puntos" else "%"
                imputados = ", ".join(a.etiqueta for a in aportes) or "ninguno"
                self.error(
                    "R2",
                    f"Rubro «{r.etiqueta}»: sus aportes suman {suma:g} {unidad} pero el rubro "
                    f"declara {base:g} {unidad}. Aportes imputados: {imputados}.",
                )
```

Con una prueba que lo fije, hermana de la de D-06: un rubro cuya base lleva tres decimales y cuyos
aportes la igualan no debe producir hallazgo de R2.

### WR-02: un componente `examen_parcial` sin valor ni evidencia cumple el artículo 68

**Archivo:** `src/validar.py:250` (y `src/validar.py:429-433`, IEDI 1.5, que se quedó atrás)
**Problema:** R3 pasó a contar aportes, pero ninguna regla exige que un componente tenga sustancia.
Antes de la fase, un examen solo podía ser una meta, y una meta de tipo `examen_parcial` con
`valor: 0` la atrapaba IEDI 1.5 («no tiene valor porcentual»). Esa comprobación sigue recorriendo
`self.c.metas` y no ve los componentes, así que la definición ampliada de «examen» entró sin su
guardia.

Comprobado ejecutando el validador sobre `CURSO_VALIDO` con los dos exámenes convertidos en
aprendizaje y dos componentes fantasma:

```python
_meta_de(d, "1.1")["componentes"] = [
    {"rubro": "tareas", "valor": 0, "etiqueta": "Examen fantasma I", "tipo": "examen_parcial"},
    {"rubro": "tareas", "valor": 0, "etiqueta": "Examen fantasma II", "tipo": "examen_parcial"},
]
# → errores de R3: []   ·   errores de IEDI 1.5: []   ·   informe.valido: True
```

Un curso sin un solo examen que valga nada sale VÁLIDO. `test_una_meta_de_examen_y_un_componente_de_examen_cuentan_dos`
(`pruebas/test_validar.py:475-484`) usa justamente `"valor": 0` para su «Examen I bis», así que la
suite fija hoy el comportamiento permisivo. D-10 decide que cada aporte cuenta uno —eso no está en
discusión—, pero no dice nada sobre aportes vacíos; el hueco no se consideró.

**Arreglo:** extender la comprobación de sustancia a los componentes, en el mismo sitio donde ya
vive para las metas.

```python
        # IEDI 1.5 — toda meta con evidencia y valor porcentual
        for m in self.c.metas:
            ...
        for a in self.c.aportes():
            if a.es_componente and a.valor == 0:
                self.error(
                    "IEDI 1.5",
                    f"{a.meta.etiqueta}: el componente «{a.etiqueta}» no tiene valor. "
                    f"Un aporte que no vale nada no es un aporte.",
                )
```

Si se prefiere no tocar IEDI 1.5, la alternativa es que R3 solo cuente parciales con `valor > 0`;
en ese caso hay que cambiar el `"valor": 0` de la prueba de D-10 por un valor real, porque si no la
prueba pasa a fijar lo contrario.

### WR-03: `Aporte` es `frozen=True` pero no se puede meter en un `set`

**Archivo:** `src/modelo.py:250-268`
**Problema:** `@dataclass(frozen=True)` genera `__hash__`, lo que anuncia que el objeto es usable
como clave de diccionario o elemento de conjunto. No lo es: el campo `meta: Meta` apunta a un
dataclass mutable con `eq=True`, cuyo `__hash__` es `None`. Comprobado:

```
hash(Aporte) -> TypeError: unhashable type: 'Meta'
set de aportes -> TypeError: unhashable type: 'Meta'
```

El docstring invita explícitamente a la Fase 13 a consumir `a.meta`, y agrupar aportes por rubro o
por semana con un `set`/`dict` es exactamente lo que hará quien pinte la tabla. Hoy nadie lo hace,
así que es una trampa latente, no un fallo activo. Además, el `__eq__` que sí funciona compara la
meta entera —listas de sesiones, pasos y evidencias— cada vez.

**Arreglo:** decidirlo explícitamente. Si se quiere que sea agrupable, identidad:

```python
@dataclass(frozen=True, eq=False)   # identidad: hashable pese a llevar la meta entera
class Aporte:
```

Si se prefiere dejarlo como está, que el docstring lo diga («no es hashable: lleva la meta entera;
agrupa por `a.meta.id`»), para que quien lo intente no se entere con un `TypeError`.

## Info

### IN-01: `regla_2` recorre `aportes()` 2 + 2N veces y eso es una trampa para el próximo cambio

**Archivo:** `src/validar.py:186`, `:202`, `:219`, `:234`
**Problema:** cada llamada crea un generador nuevo, así que hoy el resultado es correcto. Pero la
corrección depende de que `Curso.aportes()` siga siendo una función generadora: el día que alguien
lo convierta en propiedad cacheada o devuelva un iterador ya construido, las sumas de dentro del
bucle darán `0` **en silencio** y R2 denunciará todos los rubros de todos los cursos.
**Arreglo:** materializar una vez al principio del método y filtrar sobre la lista.

```python
        aportes = list(self.c.aportes())
        por_rubro = {r.id: [a for a in aportes if a.rubro == r.id] for r in self.c.rubros}
```

### IN-02: el mensaje de R2 no dice de qué meta sale cada componente

**Archivo:** `src/validar.py:223`
**Problema:** `imputados` usa `a.etiqueta` a secas. Para una meta da «Meta 2.2», que se localiza en
el YAML; para un componente da «Presentación», que puede repetirse en varias metas y no lleva a
ninguna parte. El mensaje de valores negativos de la misma regla (`validar.py:233-236`) sí cualifica
con `f"{a.meta.etiqueta} · {a.etiqueta}"`: dos redacciones distintas para la misma cosa dentro del
mismo método.
**Arreglo:** usar la misma forma en los dos sitios.

```python
                imputados = ", ".join(
                    a.etiqueta if not a.es_componente else f"{a.meta.etiqueta} · {a.etiqueta}"
                    for a in aportes
                ) or "ninguno"
```

### IN-03: la prueba de la CLI deja un directorio temporal por ejecución

**Archivo:** `pruebas/test_validar.py:737`
**Problema:** `tempfile.mkdtemp(prefix="di-r2-puntos-")` nunca se borra; cada corrida de la suite
deja un directorio con un `curso.yaml` dentro. Con el ciclo de GSD la suite corre muchas veces.
**Arreglo:** el gestor de contexto de la biblioteca estándar lo limpia solo.

```python
        with tempfile.TemporaryDirectory(prefix="di-r2-puntos-") as tmp:
            ruta = Path(tmp) / "curso.yaml"
            ...
```

### IN-04: `Aporte.tipo` fusiona dos vocabularios que `modelo.py` declara distintos

**Archivo:** `src/modelo.py:267` y `src/modelo.py:35-36`
**Problema:** el comentario de `TIPOS_COMPONENTE` insiste en que es «vocabulario propio, distinto de
`TIPOS_META`», y `Aporte` los mete a los dos en un único campo `tipo`. Funciona porque
`examen_parcial` existe en ambos por diseño, pero quien lea el dataclass no puede saber contra qué
vocabulario filtrar sin mirar `es_componente`. Un tipo que solo exista en uno de los dos
(`actividad`, `encuadre`) da resultados asimétricos sin que nada lo avise.
**Arreglo:** una línea en el docstring de `Aporte`: «`tipo` se lee en `TIPOS_META` si
`es_componente` es falso y en `TIPOS_COMPONENTE` si es cierto; `examen_parcial` es el único valor
compartido, y de eso vive R3.»

### IN-05: el renderizado y el grafo todavía ignoran los componentes

**Archivos:** `src/render_docx.py:298`, `src/render_docx.py:420`, `src/grafo.py:299`
**Problema:** R2 y R3 ya cuentan «todo aporte a un rubro, en la unidad que ese rubro declara», pero
los consumidores siguen leyendo `meta.valor` y lo imprimen con `f"{meta.valor:g}%"`. La consecuencia
es que a partir de esta fase un curso con un rubro en puntos y componentes **valida** mientras el
`.docx` imprime puntos con el signo de porcentaje y omite el valor del componente. Está asignado a la
Fase 13 —los docstrings de `Aporte` y `aportes()` la nombran— así que **no es un defecto de esta
fase**; se anota para que la brecha entre «lo que valida» y «lo que se imprime» quede registrada
mientras dure.
**Arreglo:** ninguno aquí. Que la Fase 13 consuma `Curso.aportes()` y `Rubro.a_porcentaje()` en vez
de `meta.valor`.

---

_Revisado: 2026-08-06T17:12:49Z_
_Revisor: Claude (gsd-code-reviewer)_
_Profundidad: standard_
