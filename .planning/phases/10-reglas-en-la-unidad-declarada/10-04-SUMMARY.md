---
phase: 10-reglas-en-la-unidad-declarada
plan: 04
subsystem: validation
tags: [validar, r1, r2, r3, huella, cierre-de-fase]

# Dependency graph
requires:
  - phase: 10-reglas-en-la-unidad-declarada
    provides: "regla_2 y regla_3 reescritas sobre Curso.aportes() (planes 10-02, 10-03)"
provides:
  - "auditoría de R1 fijada con cuatro pruebas: ninguna de sus cuatro comprobaciones lee
    Meta.valor ni ninguna clave de unidad de Rubro"
  - "prueba de no contaminación en el ciclo rápido: los cursos de control no declaran nada
    de la v2 y siguen sin emitir un solo hallazgo de R2 ni de R3"
  - "criterio 1 del roadmap ejercido literalmente por la CLI, con el curso en mkdtemp"
  - "REQ-48 cerrado: huella de texto de 39056 y 39062 verificada intacta a mano"
affects: []

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "las afirmaciones sobre el código que no se implementan se fijan con
      inspect.getsource() sobre el método concreto, no solo con pruebas de comportamiento
      (estilo D-12/D-13 de la Fase 9, aplicado aquí a R1)"

key-files:
  created:
    - .planning/phases/10-reglas-en-la-unidad-declarada/10-04-SUMMARY.md
  modified:
    - pruebas/test_validar.py

key-decisions:
  - "D-14: REQ-48 se cierra en dos niveles — una prueba unitaria (NoContaminacion) en el
    ciclo rápido, y `python src/huella.py verificar` a mano, fuera de la suite"
  - "Dos fragmentos del texto literal del plan chocaban con sus propios criterios de
    aceptación (las cadenas «38985» y «huella» en docstrings de NoContaminacion). Se
    siguió el criterio de aceptación explícito y se reformuló el docstring sin esas
    palabras, conservando el significado — ver Deviations"

requirements-completed: [REQ-45, REQ-48]

# Metrics
duration: 15min (aprox., con una interrupción de API entre la Tarea 3 y la escritura de
  este SUMMARY)
completed: 2026-08-05
---

# Fase 10 Plan 04: Cierre de la fase — R1 auditada, no contaminación y huella Summary

**R1 queda fijada como insensible a la unidad con cuatro pruebas (incluida una sobre su
propio código fuente), los cursos de control quedan protegidos en el ciclo rápido contra
cualquier hallazgo nuevo de R2/R3, y `huella verificar` confirma a mano que los cuatro
documentos de control no cambiaron ni un carácter.**

## Performance

- **Duration:** ~15 min de ejecución efectiva (interrumpida por un error de API justo
  antes de escribir este SUMMARY; retomada y verificada de nuevo desde cero)
- **Completed:** 2026-08-05
- **Tasks:** 3 (dos con commit de código de prueba, una de solo verificación manual)
- **Files modified:** 1 (`pruebas/test_validar.py`)

## Resultado de la auditoría de R1

**R1 es insensible a la unidad.** Se recorrió `src/validar.py:126-169` línea a línea: sus
cuatro comprobaciones son (a) la suma de `r.porcentaje` de cada rubro contra
`reglas["suma_exacta"]`, (b) los ids de rubro duplicados vía `Counter`, (c)
`self.c.exencion_ordinario` contra `[exencion_minima, exencion_maxima]`, y (d) el
contraste de `{r.id: r.porcentaje}` contra el catálogo de `esquema_id`. Ninguna de las
cuatro lee `Meta.valor`, `Rubro.unidad`, `Rubro.total`, `Rubro.base` ni
`Rubro.a_porcentaje`. La conclusión provisional que dejó `10-CONTEXT.md` queda confirmada,
no contradicha, y ahora está fijada con pruebas — incluida una que lee la fuente de
`regla_1` con `inspect.getsource()` para que una futura mezcla de unidades en R1 rompa la
suite en vez de colarse en silencio.

## Accomplishments

- **Tarea 1 — `Regla1EsInsensibleALaUnidad`** (commit `26a44e9`): cuatro pruebas nuevas
  en `pruebas/test_validar.py`, a continuación de `Regla1Porcentajes`:
  - el curso en puntos (`CURSO_EN_PUNTOS`, 150 declarados / 140 sumados) no produce ningún
    hallazgo de R1 — el defecto es enteramente de R2;
  - duplicar el valor de todas las metas del curso rompe R2 y deja a R1 callado;
  - los mensajes de R1 son idénticos con y sin un rubro en puntos — `porcentaje` es lo
    único que R1 mira, también en puntos;
  - `inspect.getsource(validar._Validador.regla_1)` no contiene `.base`, `a_porcentaje`,
    `.unidad`, `.total` ni `.valor`.
  - Se añadió `import inspect` al bloque de la biblioteca estándar, en orden alfabético
    (`copy, inspect, sys, unittest`).

- **Tarea 2 — no contaminación y criterio 1 por la CLI** (commit `c335a57`): dos clases
  nuevas al final de `pruebas/test_validar.py`.
  - `NoContaminacion`: confirma que ni `39056-big-data/curso.yaml` ni
    `39062-patrones-de-comportamiento/curso.yaml` declaran `componentes:` ni
    `unidad: puntos`; que ninguno de los dos emite un solo hallazgo de R2 o R3 (línea base
    D-15: cero de cada uno); y que ambos siguen siendo válidos.
  - `CriterioUnoPorLaLinea`: vuelca `CURSO_EN_PUNTOS` a un `tempfile.mkdtemp()` con
    `yaml.safe_dump` (patrón D-12, tomado de `test_generar.py:38-39`) y ejerce
    `python src/validar.py` **literalmente** vía `validar.main()`, capturando `stdout` con
    `contextlib.redirect_stdout`. Confirma código de salida 1, la subcadena `R2` y los dos
    valores en puntos (`140 pts`, `150 pts`) en la salida.
  - Se añadieron `contextlib`, `io`, `tempfile` a la biblioteca estándar y `yaml` como
    import de tercero, antes de `import modelo`.

- **Tarea 3 — cierre de REQ-48, a mano** (sin commit de código: es de solo lectura).
  Los cinco comandos del plan se corrieron y su salida se transcribe abajo. Ninguno
  modificó `cursos/`, ninguno gastó una excepción, y no se corrió
  `python src/huella.py registrar` en ningún momento.

## Salida literal de `python -X utf8 src/huella.py verificar`

```
  ✓ 39056 grupo 961      huella intacta
  ✓ 39056 grupo 962      huella intacta
  ✓ 39062 grupo 971      huella intacta
  ✓ 39062 grupo 972      huella intacta

Todo intacto. 4 documentos comparados.
```

Código de salida: `0`. Sin la subcadena `difiere` ni `cambió` en ningún lugar de la salida.
Los tres hashes de los cuatro documentos —texto del `.docx`, informe y forma del
`MANIFIESTO.yaml`— coinciden con `pruebas/huellas.yaml`. No se gastó ninguna excepción:
ningún curso de control declara `componentes:` ni `unidad:`.

## Task Commits

Cada tarea de código se commiteó atómicamente; la Tarea 3 no modifica archivos:

1. **Tarea 1: auditar R1 y fijar el resultado con pruebas** — `26a44e9` (test)
2. **Tarea 2: no contaminación en el ciclo rápido y el criterio 1 por la CLI** — `c335a57`
   (test)
3. **Tarea 3: cierre de REQ-48 — la huella, a mano** — sin commit (solo verificación)

## Files Created/Modified

- `pruebas/test_validar.py` — `import inspect`; clase `Regla1EsInsensibleALaUnidad` (4
  pruebas); `CURSOS_DE_CONTROL`, clase `NoContaminacion` (3 pruebas) y clase
  `CriterioUnoPorLaLinea` (1 prueba); imports nuevos `contextlib`, `io`, `tempfile`, `yaml`.
- `.planning/phases/10-reglas-en-la-unidad-declarada/10-04-SUMMARY.md` — este documento.

`src/` **no se tocó**: `git diff --name-only 4e7f2f0 -- src pruebas AGENTS.md` lista
exactamente `AGENTS.md`, `pruebas/test_modelo.py`, `pruebas/test_validar.py`,
`src/modelo.py`, `src/validar.py` — los cinco archivos de toda la fase (planes 01 a 04),
ninguno fuera de esa lista.

## Decisions Made

Ninguna nueva de diseño — el plan fija la redacción exacta de las pruebas (D-12, D-14,
D-15 de `10-CONTEXT.md`). Sí hubo dos ajustes de redacción sobre el texto literal que
traía el plan, documentados abajo como desviaciones.

## Deviations from Plan

### Auto-corregidas (Rule 1 — contradicción interna del plan)

**1. El docstring de `NoContaminacion` que trae el plan contiene la cadena `38985`,
pero el criterio de aceptación de la Tarea 2 exige `pruebas/test_validar.py` **no**
contenga `38985` (y la verificación general del plan, punto 3, pide
`grep -c "38985" pruebas/test_validar.py` → 0, por D-13).**
- **Encontrado durante:** Tarea 2, al copiar el bloque de código del plan.
- **Conflicto:** el propio texto de la acción («38985 queda fuera a propósito: declara
  sus valores en porcentaje…») contradice el criterio de aceptación de la misma tarea.
- **Corrección:** se reformuló la frase sin el número, con la convención que ya usa el
  archivo en otros lugares («el DI de Contabilidad (531)»), sin cambiar el sentido.
- **Archivo:** `pruebas/test_validar.py`.
- **Commit:** `c335a57`.

**2. El mismo docstring menciona `huella` dos veces («la huella del `.docx`»,
`python src/huella.py verificar`), pero el criterio de aceptación de la Tarea 2 exige
que `pruebas/test_validar.py` **no** contenga `huella`.**
- **Encontrado durante:** Tarea 2, mismo bloque.
- **Conflicto:** igual que el anterior — el texto de la acción se contradice con su
  propio criterio de aceptación.
- **Corrección:** se reformuló para referirse a «el texto del `.docx`… se comprueba a
  mano en la Tarea 3 de este plan», sin la palabra `huella`, conservando el porqué (D-18
  de la Fase 9, conservado por D-14 de la Fase 10).
- **Archivo:** `pruebas/test_validar.py`.
- **Commit:** `c335a57`.

En ambos casos se priorizó el criterio de aceptación explícito y verificable por encima
del texto literal de la acción, siguiendo la instrucción del propio plan de que **no**
toca `src/` ni cambia comportamiento — el ajuste es puramente de redacción de comentario,
no de la lógica de ninguna prueba.

### Interrupción de la sesión

La ejecución se cortó por un error de API justo después de terminar la Tarea 3 y antes de
escribir este SUMMARY. El árbol de trabajo no se vio afectado — los dos commits de código
(`26a44e9`, `c335a57`) ya estaban hechos, y `git status --porcelain` solo listaba
`.planning/STATE.md` y `.planning/config.json`, ajenos a este plan. Al retomar, se
volvieron a correr las cinco verificaciones de la Tarea 3, cada una en su propio bloque de
comandos, en vez de confiar en la salida de antes del corte — todos los resultados
transcritos arriba son de la corrida posterior a la interrupción.

## Issues Encountered

Ninguno más allá de la interrupción de API ya descrita y las dos contradicciones internas
del texto del plan, ambas resueltas como desviaciones documentadas arriba.

## User Setup Required

Ninguno — no requiere configuración de servicios externos.

## Next Phase Readiness

Con este plan se cierra la Fase 10. Los cinco criterios de éxito quedan cubiertos:

1. **Criterio 1** (rubro en puntos denuncia el faltante en puntos) — ejercido por la
   CLI literal en `CriterioUnoPorLaLinea`, además de la prueba unitaria del plan 10-02.
2. **Criterio 2** (nunca se mezclan unidades entre rubros) — fijado en el plan 10-02
   (`test_r2_nunca_suma_unidades_distintas_entre_si`).
3. **Criterio 3** (el defecto del ejemplo 961 se sigue detectando) —
   `test_detecta_el_defecto_del_ejemplo_961` no se tocó.
4. **Criterio 4** (exámenes dentro de componentes cuentan para R3) — fijado en el
   plan 10-03.
5. **Criterio 5 / REQ-48** (no contaminación) — cerrado en este plan, en los dos niveles
   que manda D-14: prueba unitaria (`NoContaminacion`) y `huella verificar` a mano.

La Fase 11 (segundo nivel de calificación) puede apoyarse en `Curso.aportes()` y en
`Rubro.base`/`Rubro.a_porcentaje()` sin que R1, R2 o R3 necesiten volver a tocarse por
razón de unidad — es exactamente lo que esta fase deja fijado.

Verificación de cierre del plan (todas corridas en bloques independientes, después de la
interrupción):
- `python -X utf8 -m unittest discover -s pruebas` → **245 pruebas, exit 0** (237 previas
  de los planes 01-03 + 4 de la Tarea 1 + 4 de la Tarea 2).
- `python -X utf8 src/huella.py verificar` → **exit 0**, salida transcrita arriba, sin
  `difiere` ni `cambió`.
- `python -X utf8 src/validar.py cursos/2026-2/39056-big-data/curso.yaml` → `VÁLIDO`,
  exit 0, sin `R2` ni `R3` en la salida.
- `python -X utf8 src/validar.py cursos/2026-2/39062-patrones-de-comportamiento/curso.yaml`
  → igual, `VÁLIDO`, exit 0, sin `R2` ni `R3`.
- `git status --porcelain` → solo `.planning/STATE.md` y `.planning/config.json`
  (del orquestador, no de este plan); nada bajo `cursos/`.
- `git diff --name-only 4e7f2f0 -- src pruebas AGENTS.md` → `AGENTS.md`,
  `pruebas/test_modelo.py`, `pruebas/test_validar.py`, `src/modelo.py`, `src/validar.py` —
  exactamente los cinco archivos de la fase entera.
- `grep -c "38985" pruebas/test_validar.py` → 0 (D-13 respetado).

---
*Phase: 10-reglas-en-la-unidad-declarada*
*Completed: 2026-08-05*

## Self-Check: PASSED

- FOUND: pruebas/test_validar.py
- FOUND: .planning/phases/10-reglas-en-la-unidad-declarada/10-04-SUMMARY.md
- FOUND: commit 26a44e9
- FOUND: commit c335a57
