# Fase 10: Las reglas cuentan en la unidad declarada — Registro de la discusión

> **Solo rastro de auditoría.** No es entrada para los agentes de investigación, planeación ni
> ejecución. Las decisiones están en `10-CONTEXT.md`; este registro conserva las alternativas que
> se consideraron y por qué se descartaron.

**Fecha:** 2026-08-05
**Fase:** 10 — Las reglas cuentan en la unidad declarada
**Áreas discutidas:** Encuadre del alcance · Forma del accesor de aportes · La suma global de R2 ·
Qué ve una regla dentro de un componente · La evidencia y la huella

---

## Nota de arranque

`gsd-sdk query init.phase-op 10` devolvió `phase_found: false`. Su parser busca encabezados en
inglés (`### Phase N`) y `.planning/ROADMAP.md` está en español (`### Fase 10`). La fase existe y
está completamente definida; las rutas se resolvieron a mano. **No es un defecto del proyecto** y
volverá a pasar en las Fases 11 a 14.

## Encuadre del alcance

Interrupción del usuario tras la primera propuesta de áreas: *«creo que nos estamos enfocando como
si siempre fuéramos a hacer estos, y la idea es hacerlo lo más general posible; ¿esta fase es para
esto o se está apegando mucho a que solo fueran las que ya tenemos?»*

Se verificó antes de responder. `grep` sobre `src/`: `componentes` aparece fuera del modelo en un
solo sitio, `render_docx.py:274`. Ninguna regla lo lee. `validar.py:179` solo comprueba `m.rubro`
y `:206` solo `m.valor < 0`.

| Opción | Descripción | Elegida |
|---|---|---|
| General: toda regla lee todo aporte | La agregación vive una vez en el modelo; se cierran además los huecos sin dueño que abrió `componentes:` | ✓ |
| Literal al roadmap | Solo los cinco criterios; R2 sigue ignorando el valor de los componentes | |
| Intermedio | Agregación general y R2 sumando componentes, pero difiriendo las validaciones de integridad | |

**Notas:** se registró el contrapeso — ensanchar es alcance que el roadmap no asignó. Se sostuvo
porque no es capacidad nueva: es que las reglas sean correctas sobre un contrato que ya existe.
También se dejó claro qué **no** hacía falta ensanchar: `Rubro.base` + `a_porcentaje` ya es
aritmética agnóstica de la unidad, y que `TIPOS_COMPONENTE` sea cerrado es deliberado y correcto.

Se reconoció además que el estrechamiento venía en parte del encuadre propio —las cuatro áreas
iniciales colgaban del 531 y del 961 en vez de colgar del invariante—, y las áreas se reformularon.

## Selección de áreas

Las cuatro reformuladas se seleccionaron todas: Forma del accesor de aportes · La suma global de R2
· Qué ve una regla dentro de un componente · La evidencia y la huella.

---

## Forma del accesor de aportes

### ¿Qué forma tiene el accesor?

| Opción | Descripción | Elegida |
|---|---|---|
| Generador plano, cada consumidor filtra | Una función emite todos los aportes; R2 filtra por rubro, R3 por tipo, la Fase 13 por meta | ✓ |
| Accesor por rubro | `aportes_de(rubro_id)`; exactamente lo que R2 necesita y nada más | |
| Solo la suma | `suma_de(rubro_id) -> float`; lo mínimo que hace pasar el criterio 1 | |

**Notas:** se presentó con código concreto de las tres, no con descripciones. El accesor por rubro
se descartó porque R3 agrupa por tipo y la Fase 13 por meta, así que ninguno de los dos lo
aprovecha. «Solo la suma» se descartó porque R2 seguiría derivando en línea la lista de metas
imputadas que su mensaje necesita.

### ¿En qué unidad devuelve el valor?

| Opción | Descripción | Elegida |
|---|---|---|
| Cruda, como se declaró | Quien necesite % llama a `Rubro.a_porcentaje()`, que ya existe (D-04 de la Fase 9) | ✓ |
| Convertida a porcentaje | Homogéneo para quien suma | |
| Las dos, como campos del aporte | `valor` y `porcentaje` en el mismo objeto | |

**Notas:** convertir antes le quitaría a R2 justo lo que necesita para comparar contra `base` y
para redactar el error en puntos. Llevar las dos se descartó por ser un derivado desincronizable.

### ¿Qué hace R3 con este accesor?

| Opción | Descripción | Elegida |
|---|---|---|
| Consume el mismo, filtrando por tipo | Un examen parcial es un aporte de ese tipo, se declare donde se declare | ✓ |
| Su propia derivación | Metas por `tipo` más componentes aparte | |

**Notas:** se verificó después el acoplamiento que esto crea. `TIPOS_META` (`modelo.py:31`) y
`TIPOS_COMPONENTE` (`:35`) comparten exactamente un valor: `examen_parcial`. El filtro de R3
funciona por ese solapamiento, y quedó anotado en el contexto.

---

## La suma global de R2

Se presentó junto con un hallazgo de la lectura de las pruebas:
`test_el_total_correcto_no_absuelve_al_rubro_incorrecto` (`test_validar.py:180-186`) afirma
`assertNotIn("El valor de las metas suma", mensajes)`. Si el hallazgo global desaparece, la prueba
sigue pasando pero deja de probar nada.

| Opción | Descripción | Elegida |
|---|---|---|
| Se convierte y se conserva | Los aportes se llevan a % y se compara contra la suma de porcentajes | ✓ |
| Se retira por redundante | La comprobación por rubro ya lo implica; R1 vigila que los porcentajes sumen 100 | |
| Se conserva solo si no hay puntos | Mínimo cambio; garantiza que el informe de los de control no se mueve | |

**Notas:** la tercera se descartó explícitamente por ser el tipo de bifurcación por curso que el
encuadre general de la fase quiere evitar.

### ¿Cómo se compara la suma convertida?

La elección anterior obligó a medir antes de seguir. Ejecutado sobre los cursos reales: 39056 y
39062 convierten exacto (`100.0`). Ejecutado sobre casos construidos: **21 metas de 7 pts más una
de 3 —150 pts exactos— convierten a `29.99999999999999` contra 30 %.** Un curso correcto emitiría
un error falso, y esa forma —un rubro de 150 repartido en muchas entregas pequeñas— es la de
«catorce entregas» del 38985.

| Opción | Descripción | Elegida |
|---|---|---|
| Convertir por rubro, no por aporte | Una división por rubro; `a_porcentaje(150) == 30.0` exacto | ✓ |
| Convertir por aporte y redondear a 2 | Tapa el caso medido hasta el segundo decimal | |
| Tolerancia explícita | `math.isclose` o epsilon en la configuración | |

**Notas:** la tolerancia explícita se descartó por introducir un concepto que ninguna otra regla
usa. La segunda, porque el error sigue acumulándose con el número de metas y solo queda tapado.

---

## Qué ve una regla dentro de un componente

Antes de preguntar se midió qué emiten hoy los cursos de control, porque es lo que la huella
hashea. Resultado: **ambos VÁLIDO**, con la cabecera, cinco recordatorios IEDI (2.4, 3.1, 3.2, 3.5,
4.1) y cero hallazgos de R2 o R3. Ambos declaran `parciales: 2` con dos metas de ese tipo, así que
el aviso tampoco dispara.

Esto **corrigió el peso que se le había dado a REQ-48** en el planteamiento inicial: la redacción de
los mensajes de R2 y R3 es libre. Lo que hay que preservar es el silencio de esas reglas sobre esos
cursos.

### Meta `examen_parcial` con componente `examen_parcial`: ¿cuántos cuenta R3?

| Opción | Descripción | Elegida |
|---|---|---|
| Dos — cada aporte cuenta | Sale solo del accesor plano; son dos aportes con etiqueta y valor propios | ✓ |
| Uno — se deduplica por meta | Protege contra declarar el mismo examen dos veces | |
| Dos, pero con aviso | Cuenta dos y deja rastro del caso raro | |

### El aviso de `parciales:` (`validar.py:224-230`)

| Opción | Descripción | Elegida |
|---|---|---|
| Se reformula a «exámenes parciales» | Deja de hablar de «metas de tipo» | ✓ |
| Se deja tal cual | Cero riesgo sobre la huella | |
| Pasa a ser error | Más estricto | |

**Notas:** se descartó dejarlo tal cual porque en 38985 —tres exámenes dentro de otras metas— el
texto actual sería engañoso justo en el curso que la fase existe para admitir. Pasar a error se
descartó por ser un cambio de severidad que ni REQ-40 ni REQ-45 piden.

### Componente con rubro inexistente o valor negativo

| Opción | Descripción | Elegida |
|---|---|---|
| R2, hermano de lo que ya hace con las metas | Mismo sitio, mismo trato; precedente de D-17 de la Fase 9 | ✓ |
| Repartido: negativo al cargar, rubro en R2 | Más preciso conceptualmente | |
| Se difiere | La fase solo hace que cuenten | |

**Notas:** el reparto se descartó por dejar el mismo tipo de defecto en dos sitios y tratar al
componente distinto que a la meta.

### Componente imputado al mismo rubro que su meta

| Opción | Descripción | Elegida |
|---|---|---|
| Legítimo, se suma y ya | Caso real: dos piezas calificadas por separado en la misma meta y rubro | ✓ |
| Legítimo pero con aviso | Deja constancia por si fue un descuido | |
| Error | Un componente existe para aportar a otro rubro | |

**Notas:** el error se descartó porque prohibiría algo razonable que la Fase 13 sabría imprimir
bien. El aviso, por ser ruido permanente en un curso correcto.

---

## La evidencia y la huella

Se verificó antes la convención del repo: `pruebas/` no guarda archivos de datos —lo único no-`.py`
es `huellas.yaml`—; los tests construyen diccionarios y vuelcan a `tempfile.mkdtemp()` cuando
necesitan un archivo (`test_generar.py:38-39`, `test_grafo.py:111-112`).

### ¿Dónde vive el curso de 150/140?

| Opción | Descripción | Elegida |
|---|---|---|
| Fixture de diccionario en `test_validar.py` | Hermano de `CURSO_VALIDO`; la convención del repo | ✓ |
| Curso sintético versionado en `cursos/` | Ejemplo vivo del rasgo nuevo | |
| Reescribir ya 38985 a puntos | El defecto donde nació | |

**Notas:** reescribir 38985 se descartó por doble coste — es literalmente el criterio 2 de la
Fase 14, y dejaría el curso inválido durante las Fases 11, 12 y 13. Se hizo notar que REQ-48 **no**
lo impediría (38985 no está entre los documentos de control, D-22 de la Fase 9): lo impide el orden
de trabajo, no la huella.

### ¿Cómo se cierra REQ-48?

| Opción | Descripción | Elegida |
|---|---|---|
| `huella verificar` a mano + prueba que fija los hallazgos actuales | Conserva D-18 y detecta regresiones en el ciclo rápido | ✓ |
| Solo `huella verificar` a mano | Respeta D-18 sin añadir nada | |
| Además meter la huella en la suite | Cobertura máxima | |

**Notas:** meter la huella en la suite revertiría D-18 por decisión explícita —las pruebas pasarían
a generar cuatro documentos y a depender de las plantillas—. Al ofrecer la opción intermedia se
señaló el riesgo real de que una prueba de «nada cambió» se vuelva tautológica, como acababa de
pasarle a la de la línea 180.

---

## Criterio de Claude

- Nombres exactos de `Curso.aportes()` y del dataclass `Aporte`, y si guarda la `Meta` entera o su id.
- Redacción de los mensajes nuevos de R2 y R3, sujeta a la restricción de D-07 en el caso del global.
- Si el hallazgo por rubro en puntos menciona además el equivalente en porcentaje.
- Organización interna del fixture `CURSO_EN_PUNTOS`.

## Ideas apartadas

- Los componentes en el grafo (sigue vigente D-10 de la Fase 9).
- Que el aviso de `parciales:` pase a ser error.
- Un banco de cursos de ejemplo versionado en `cursos/`.
- Una tolerancia numérica declarada en `config/esquemas-evaluacion.yaml` — vuelve a ser pertinente
  si la Fase 11 introduce aritmética con más acumulación de error.
- El prefijo `M0_` del recurso de Big Data y los `.pdf` ausentes de los `MANIFIESTO.yaml`, ambos
  heredados del cierre de la Fase 9.

## No discutido a fondo

R1 y REQ-45. Las cuatro comprobaciones de `regla_1` (`validar.py:126-169`) ya operan en porcentaje
y ninguna toca un valor de meta, así que la conclusión provisional es que no necesita cambio. Se
registró en el contexto con instrucción explícita al planeador de auditarlo y levantarlo si
encuentra algo sensible a la unidad, en vez de resolverlo por su cuenta.
