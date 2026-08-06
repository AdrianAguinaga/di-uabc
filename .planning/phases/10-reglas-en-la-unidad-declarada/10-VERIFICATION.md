---
phase: 10-reglas-en-la-unidad-declarada
verified: 2026-08-06T18:00:00Z
status: passed
score: 5/5 criterios de éxito del roadmap verificados (más los must_haves de los 4 planes)
overrides_applied: 0
---

# Fase 10: Las reglas cuentan en la unidad declarada — Reporte de verificación

**Meta de la fase:** que R2 y R3 sigan atrapando lo que atrapaban, y además atrapen el defecto real
del 531 — generalizado por `10-CONTEXT.md` a «toda regla lee todo aporte a un rubro, en la unidad
que ese rubro declara».
**Verificado:** 2026-08-06
**Estado:** passed
**Re-verificación:** No — verificación inicial.

## Goal Achievement

### Criterios de éxito del roadmap (literales, §«Fase 10»)

| # | Criterio | Estado | Evidencia |
|---|----------|--------|-----------|
| 1 | Un curso cuyo rubro en puntos declara 150 y cuyas metas suman 140 reporta error de R2 en puntos | ✓ VERIFICADO | Reproducido de forma independiente (no solo vía suite): `python -X utf8` sobre `CURSO_EN_PUNTOS` volcado a `mkdtemp` da `codigo 1` y el mensaje `Rubro «Tareas y actividades de clase»: sus aportes suman 140 pts pero el rubro declara 150 pts.` Prueba unitaria hermana: `CriterioUnoPorLaLinea.test_la_cli_reporta_el_faltante_en_puntos_y_sale_con_uno` (`pruebas/test_validar.py:731`). |
| 2 | Corregido el total a 140 pts, el curso pasa R2 aunque el rubro vecino esté en porcentaje | ✓ VERIFICADO | Reproducido de forma independiente: mismo curso con `total: 140` da `codigo 0`, `VÁLIDO`, sin ninguna línea `R2`. Prueba hermana: `test_corregido_el_total_el_curso_en_puntos_valida` (`pruebas/test_validar.py`). |
| 3 | `test_detecta_el_defecto_del_ejemplo_961` sigue pasando sin tocarse | ✓ VERIFICADO | `git diff 4e7f2f0 -- pruebas/test_validar.py` no borra ninguna línea entre 169-186 del archivo original; la prueba corre y pasa dentro de la suite completa (245 pruebas, código 0). |
| 4 | R3 cuenta los exámenes que viven como componente de la actividad de otra meta (3 componentes y cero metas pasan; uno solo falla con el Art. 68) | ✓ VERIFICADO | Reproducido de forma independiente sobre `CURSO_CON_EXAMENES_EN_COMPONENTES`: cero metas de tipo `examen_parcial`, cero errores de R3, curso válido. `test_un_solo_examen_en_componente_no_basta` fija la otra mitad con la subcadena «68». |
| 5 | Cierre (REQ-48): 39056 y 39062 conservan su huella de texto y sus informes de validación no cambian ni un hallazgo | ✓ VERIFICADO | `python -X utf8 src/huella.py verificar` (solo lectura, corrido por mí) → `Todo intacto. 4 documentos comparados.`, código 0. `python -X utf8 src/validar.py` sobre los dos cursos de control → `VÁLIDO`, código 0, sin `R2` ni `R3` en la salida. |

**Puntaje:** 5/5 criterios verificados.

### Must-haves de los 4 planes (verificación de código, no de SUMMARY)

| Plan | Must-have | Estado | Evidencia |
|---|---|---|---|
| 10-01 | `Aporte` (frozen, 6 campos) y `Curso.aportes()` generador plano | ✓ VERIFICADO | `src/modelo.py:250-268` (`Aporte`), `:...` `def aportes(self) -> Iterator[Aporte]` presente; campos en el orden exacto `meta, rubro, valor, etiqueta, tipo, es_componente`. `class Aportes` en `pruebas/test_modelo.py:265` con 6 métodos `test_`. |
| 10-01 | Aporte lleva la meta entera (enlace a Fase 13) | ✓ VERIFICADO | `meta: Meta` (no id) en el dataclass; prueba `test_desde_el_aporte_se_llega_a_la_meta_que_lo_declaro` usa `a.meta.semanas`. |
| 10-02 | R2 lee `Curso.aportes()`, compara contra `Rubro.base`, nunca mezcla unidades | ✓ VERIFICADO | `src/validar.py:186-228`: `for a in self.c.aportes()`, `if suma != r.base`, conversión `r.a_porcentaje(...)` una vez por rubro. Prueba `test_veintidos_aportes_de_puntos_exactos_no_inventan_un_faltante` fija el caso de coma flotante medido en D-06. |
| 10-02 | Componente en rubro inexistente o con valor negativo es error de R2; mismo rubro que su meta no genera nada | ✓ VERIFICADO | `src/validar.py:186-193` (rubro inexistente) y `:232-237` (negativo). `test_un_componente_en_el_mismo_rubro_que_su_meta_no_genera_hallazgo` confirma D-09. |
| 10-02 | El hallazgo global conserva el prefijo literal «El valor de las metas suma» | ✓ VERIFICADO | `grep -c "El valor de las metas suma" src/validar.py` → 1. `test_el_total_correcto_no_absuelve_al_rubro_incorrecto` intacta. |
| 10-02 | Fila de R2 en `AGENTS.md` actualizada | ✓ VERIFICADO | `AGENTS.md:173` contiene «en la unidad de ese rubro» y el párrafo siguiente menciona `Rubro.base` y «una vez». |
| 10-03 | R3 cuenta aportes de tipo `examen_parcial`, vengan de donde vengan | ✓ VERIFICADO | `src/validar.py:250`: `parciales = [a for a in self.c.aportes() if a.tipo == "examen_parcial"]`. Ya no queda `[m for m in self.c.metas if m.tipo == "examen_parcial"]`. |
| 10-03 | El aviso de `parciales:` deja de hablar solo de metas | ✓ VERIFICADO | `grep -n "metas de tipo" src/validar.py` → vacío. Mensaje nuevo en `:260-265` habla de «examen(es) parcial(es)» y menciona explícitamente los que «viven como componente de la actividad de otra meta». |
| 10-03 | Fila de R3 en `AGENTS.md` — contiene la cadena `o como componente de otra meta` | ⚠️ VERIFICADO CON MATIZ | Ver «Punto a juzgar 1» abajo — el texto real es «o como componente de la actividad de otra meta», más preciso que la cadena literal pedida por el must_have. No es un hueco de comportamiento. |
| 10-04 | R1 auditada e insensible a la unidad, fijada con pruebas | ✓ VERIFICADO | `class Regla1EsInsensibleALaUnidad` (`pruebas/test_validar.py:258`), 4 pruebas incluida una que usa `inspect.getsource(validar._Validador.regla_1)` y comprueba ausencia de `.base`, `a_porcentaje`, `.unidad`, `.total`, `.valor`. |
| 10-04 | No contaminación: 39056/39062 sin `componentes:`/`unidad:`, cero hallazgos de R2/R3 | ✓ VERIFICADO | `class NoContaminacion` (`:691`), 3 pruebas; corrida independiente de `huella.py verificar` y `validar.py` sobre ambos cursos confirma el silencio. |
| 10-04 | Criterio 1 ejercido literalmente por la CLI, sin ensuciar `cursos/` | ✓ VERIFICADO | `class CriterioUnoPorLaLinea` usa `tempfile.mkdtemp` + `yaml.safe_dump`; `git status --porcelain cursos/` vacío. |

### Artefactos requeridos

| Artefacto | Esperado | Estado | Detalle |
|---|---|---|---|
| `src/modelo.py` | `Aporte` + `Curso.aportes()` | ✓ VERIFICADO | Presente, correcto, usado por R2 y R3. |
| `src/validar.py` | R2 y R3 reescritas sobre `Curso.aportes()` | ✓ VERIFICADO | Ambas reglas leen el accesor; ninguna deriva su propia suma. |
| `pruebas/test_modelo.py` | `class Aportes` | ✓ VERIFICADO | 6 pruebas, 24 pruebas totales en el archivo. |
| `pruebas/test_validar.py` | fixtures `CURSO_EN_PUNTOS`, `CURSO_CON_EXAMENES_EN_COMPONENTES`, clases de prueba de las 4 fases | ✓ VERIFICADO | Todos presentes; 65 métodos `test_` en el archivo. |
| `AGENTS.md` | filas de R2 y R3 actualizadas | ✓ VERIFICADO (con el matiz del punto 1) | Ambas filas describen el comportamiento real. |

### Verificación de enlaces clave (wiring)

| De | A | Vía | Estado | Detalle |
|---|---|---|---|---|
| `Curso.aportes()` | `Meta.componentes` | bucle anidado | ✓ WIRED | `for c in m.componentes: yield Aporte(...)` |
| `regla_2` | `Curso.aportes()` | comprensiones filtrando por `rubro` | ✓ WIRED | 4 puntos de consumo en `validar.py:186-234` |
| `regla_2` | `Rubro.base` / `Rubro.a_porcentaje` | comparación y conversión | ✓ WIRED | `if suma != r.base`, `r.a_porcentaje(...)` |
| `regla_3` | `Curso.aportes()` | filtro por `tipo` | ✓ WIRED | `a.tipo == "examen_parcial"` |

### Comprobaciones conductuales (Paso 7b) — reproducidas de forma independiente, no solo vía suite

| Comportamiento | Comando | Resultado | Estado |
|---|---|---|---|
| Criterio 1: 150 declarados/140 sumados → error en puntos | curso volcado a `mkdtemp`, `validar.main()` | `código 1`, «140 pts»/«150 pts» en la salida | ✓ PASS |
| Criterio 2: total corregido a 140 → pasa aunque el vecino esté en % | ídem con `total: 140` | `código 0`, `VÁLIDO`, sin `R2` | ✓ PASS |
| Criterio 4: 3 componentes examen y 0 metas de ese tipo → pasa R3 | `validar.validar()` sobre `CURSO_CON_EXAMENES_EN_COMPONENTES` | `R3 errores: []`, `valido: True` | ✓ PASS |
| REQ-48: huella de 39056/39062 intacta | `python src/huella.py verificar` (solo lectura) | `Todo intacto. 4 documentos comparados.`, código 0 | ✓ PASS |
| Suite completa | `python -X utf8 -m unittest discover -s pruebas` | `Ran 245 tests ... OK` | ✓ PASS |

### Cobertura de requisitos

| Requisito | Plan(es) | Descripción | Estado | Evidencia |
|---|---|---|---|---|
| REQ-40 | 10-03 | R3 cuenta componentes `examen_parcial` igual que metas de ese tipo | ✓ SATISFECHO | Ver criterio 4 arriba. |
| REQ-45 | 10-01, 10-02, 10-04 | R1 y R2 operan en la unidad de cada rubro | ✓ SATISFECHO | R2 compara contra `Rubro.base` por rubro; R1 auditada e insensible a la unidad (fijada con `inspect.getsource`). |
| REQ-48 | 10-04 (criterio de cierre transversal) | No contaminación: 39056/39062 conservan huella e informes | ✓ SATISFECHO | `huella verificar` sin diferencias; `NoContaminacion` en el ciclo rápido. |

Sin requisitos huérfanos: los tres declarados en el encargo (REQ-40, REQ-45, REQ-48) están cubiertos
por al menos un plan de la fase.

### Anti-patrones encontrados (de `10-REVIEW.md`, contrastados contra el código)

Ninguno de los tres avisos de la revisión de código es un bloqueador; los tres se reprodujeron y
se juzgan aquí contra los criterios de éxito y los must_haves de los planes, no contra un ideal
abstracto.

- **WR-01** (`validar.py:220-221`, redondeo asimétrico: `suma` se redondea, `r.base` no) — defecto
  heredado de antes de la fase (`suma != r.porcentaje` ya tenía esta forma). No lo ejercita ningún
  curso real ni ningún must_have de los 4 planes: todos los rubros de 39056, 39062 y de los
  fixtures declaran totales de dos decimales o menos. No es un hueco de esta fase; es candidato a
  una corrección de una línea, sin decisión de diseño pendiente.
- **WR-03** (`Aporte` `frozen=True` pero no hashable porque `Meta` no lo es) — trampa latente para
  un consumidor futuro (la Fase 13, que el propio docstring invita a agrupar por `a.meta`). Hoy
  nadie mete un `Aporte` en un `set`, así que no afecta ningún comportamiento verificado en esta
  fase.

## Dos puntos a juzgar con criterio

### 1. AGENTS.md:174 — «...o como componente **de la actividad** de otra meta» vs. el `contains` literal del must_have

**Dictamen: coincidencia literal fallida, no hueco real.**

El must_have del plan 10-03 pedía la cadena `o como componente de otra meta`. El texto real es
`o como componente de la actividad de otra meta`. La cadena pedida no es substring del texto real
(el inserto «de la actividad» rompe la coincidencia literal).

Pero el propio objetivo del plan 10-03 (línea 39 de `10-03-PLAN.md`) ya dice textualmente: «como
meta de tipo `examen_parcial` o **como componente de la actividad de otra meta**» — la redacción
que terminó en `AGENTS.md` reproduce con exactitud el lenguaje que el plan usa para describirse a
sí mismo, no una desviación inventada por el ejecutor. Es además más precisa: «actividad» es la
palabra que el contrato de `curso.yaml` usa para el rubro donde vive un componente de una meta
distinta (REQ-39, `Meta.componentes`), y omitirla deja ambiguo si el componente pertenece a la
meta o a algo suelto. El comportamiento que la fila describe —R3 cuenta el componente sin importar
en qué meta vive— está correctamente implementado y verificado en la tabla de arriba.

No se sugiere una entrada de `overrides:` formal porque este `contains` es una comprobación de
artefacto interna al plan 10-03, no uno de los cinco criterios de éxito del roadmap ni un
must_have de otro plan que dependa de esa cadena exacta; ningún consumidor de `AGENTS.md` (código,
prueba o documento) depende de la subcadena literal. Se registra aquí como discrepancia de
redacción, sin impacto en el estado de la fase.

### 2. WR-02 — IEDI 1.5 sigue recorriendo solo `self.c.metas`; dos componentes `examen_parcial` con `valor: 0` dan un curso válido

**Dictamen: hallazgo real y correctamente clasificado como fuera del alcance de esta fase — no
incumple ningún criterio de éxito ni ningún must_have de los 4 planes.**

Reproducido de forma independiente (no solo leyendo el código): un curso con dos metas de examen
convertidas a `aprendizaje` y dos componentes `examen_parcial` de `valor: 0` da `R3 errores: []`,
`IEDI 1.5 errores: []`, `valido: True`. El curso «pasa» sin un solo examen que valga algo.

Razones para no tratarlo como gap de la Fase 10:

- **IEDI 1.5 vive en `regla_8` (R8)**, no en R2 ni en R3. Los cinco criterios de éxito del roadmap
  hablan exclusivamente de R2 y R3; ninguno menciona R8 ni el IEDI.
- **Ninguno de los 4 planes (10-01 a 10-04) declara un must_have sobre R8 o IEDI 1.5.** El
  `10-CONTEXT.md` delimita el «Dentro» de la fase como «el accesor de aportes, la aritmética de R2
  por rubro y su hallazgo global, las comprobaciones de integridad de un componente [en R2, D-08],
  y el conteo de R3» — R8 no aparece ni en el «Dentro» ni en ninguna decisión D-01 a D-15.
- **D-10 decide explícitamente** que «cada aporte de tipo `examen_parcial` cuenta uno», sin
  deduplicar por meta, pero no dice nada sobre aportes vacíos — el propio `10-CONTEXT.md` reconoce
  que ese caso «no se discutió a fondo» en ningún punto de la fase.

Dicho esto, el hallazgo es genuino y coherente con el enunciado general que gobierna la fase
(«toda regla lee todo aporte a un rubro, en la unidad que ese rubro declara») — R8 es una regla
más, y hoy no lee todo aporte. Es trabajo real, correctamente señalado por la revisión de código,
que corresponde decidir explícitamente en una fase futura (candidata natural: donde se toque R8 o
las comprobaciones de sustancia de un componente) y no colarlo por inercia en el cierre de esta.
No se crea un gap en este VERIFICATION.md porque no hay un must_have que lo reclame; se dejaría
como ítem de seguimiento fuera del mecanismo de gaps (que sirve para cerrar must_haves declarados,
no para abrir alcance nuevo).

## Verificación Requerida por Humano

Ninguna. Todo lo verificable en esta fase es lógica de validación determinista (dataclasses,
generadores, reglas puras sobre `curso.yaml`) ejercitada por CLI y por la suite; no hay
renderizado, UI, ni servicio externo que requiera inspección visual o de flujo de usuario.

## Resumen de huecos

Ningún gap bloquea el cierre de la Fase 10. Los cinco criterios de éxito del roadmap y los
must_haves de los cuatro planes están verificados contra el código real, no contra lo que afirman
los SUMMARY. Los tres avisos de `10-REVIEW.md` (WR-01, WR-02, WR-03) son reales pero ninguno
incumple un criterio de éxito ni un must_have declarado; quedan documentados arriba como
candidatos a decisión explícita en una fase futura, no como trabajo pendiente de esta.

---

_Verificado: 2026-08-06_
_Verificador: Claude (gsd-verifier)_
