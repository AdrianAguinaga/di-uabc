---
phase: 10-reglas-en-la-unidad-declarada
plan: 02
subsystem: validation
tags: [validar, r2, curso.yaml, aportes, componentes]

# Dependency graph
requires:
  - phase: 10-reglas-en-la-unidad-declarada
    provides: "dataclass Aporte y Curso.aportes() en src/modelo.py (plan 10-01)"
provides:
  - "regla_2 reescrita: lee Curso.aportes(), compara por rubro contra Rubro.base en la unidad
    de ese rubro, y convierte el hallazgo global a porcentaje una vez por rubro"
  - "fixture CURSO_EN_PUNTOS en pruebas/test_validar.py, con nueve pruebas nuevas de R2"
  - "un componente imputado a un rubro inexistente o con valor negativo es error de R2"
  - "fila de R2 y su párrafo en AGENTS.md al día con el comportamiento real"
affects: ["10-03", "13"]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "R2 filtra Curso.aportes() por rubro en vez de derivar su propia suma sobre las metas"
    - "la conversión a porcentaje ocurre una sola vez por rubro, sobre la suma cruda, nunca
      aporte a aporte (evita acumulación de error de coma flotante)"

key-files:
  created: []
  modified:
    - src/validar.py
    - pruebas/test_validar.py
    - AGENTS.md

key-decisions:
  - "D-04/D-06/D-07 de 10-CONTEXT.md se siguieron al pie de la letra: comparación contra
    r.base, conversión una vez por rubro, prefijo literal «El valor de las metas suma»"
  - "D-08/D-09: componente en rubro inexistente o negativo es error de R2 y el curso carga
    igual; componente en el mismo rubro que su meta no genera ningún hallazgo"

patterns-established:
  - "Las comprobaciones de integridad de un componente son hermanas de las de la meta, en el
    mismo sitio de R2, mismo trato (D-08, precedente D-17 de la Fase 9)"

requirements-completed: [REQ-45]

# Metrics
duration: 25min
completed: 2026-08-05
---

# Fase 10 Plan 02: R2 en la unidad declarada Summary

**`regla_2` reescrita sobre `Curso.aportes()`: compara cada rubro contra `Rubro.base` en su
propia unidad, cuenta también los componentes, y convierte el hallazgo global a porcentaje
una vez por rubro para no acumular error de coma flotante.**

## Performance

- **Duration:** 25 min (aprox.)
- **Started:** 2026-08-05 (aprox.)
- **Completed:** 2026-08-05
- **Tasks:** 3
- **Files modified:** 3

## Accomplishments
- `regla_2` deja de derivar `sum(m.valor for m in self.c.metas if m.rubro == r.id)` — que
  ignoraba los componentes y comparaba contra `r.porcentaje` sin sentido para un rubro en
  puntos — y pasa a filtrar `Curso.aportes()` por rubro, comparando contra `r.base`.
- El hallazgo global («El valor de las metas suma…») se conserva con su prefijo literal
  (D-07) y ahora habla en porcentaje, convertido **una vez por rubro** con
  `Rubro.a_porcentaje()` — evita el defecto de coma flotante medido en 10-CONTEXT.md
  (21 aportes de 7 pts más uno de 3 sobre 150 pts dan `29.99999999999999` si se convierte
  aporte a aporte).
- El defecto real del DI de Contabilidad (531) —un rubro que declara 150 pts y cuyos aportes
  suman 140— ahora lo detecta R2, redactado en puntos.
- Un componente imputado a un rubro inexistente o con valor negativo es ahora error de R2,
  hermano de las comprobaciones que ya existían para las metas; el curso con el defecto sigue
  cargando (D-08, precedente D-17 de la Fase 9). Un componente en el mismo rubro que su meta
  sigue sin generar ningún hallazgo (D-09).
- Fixture `CURSO_EN_PUNTOS` (Tareas en puntos, 150 declarados, 140 sumados) y nueve pruebas
  nuevas en `Regla2Metas` que ejercen los criterios 1 y 2 del roadmap, la no mezcla de
  unidades entre rubros vecinos, el componente que cuenta para su rubro, D-09 y D-06.
- `AGENTS.md` §«Las ocho reglas de validación» describe el comportamiento real de R2.
- Los cuatro documentos de control (39056×2, 39062×2) siguen validando limpios, sin un solo
  hallazgo de R2 — verificado con `python src/huella.py verificar`.

## Task Commits

Each task was committed atomically:

1. **Tarea 1: R2 cuenta todo aporte, en la unidad de su rubro** - `74f68eb` (feat)
2. **Tarea 2: el fixture en puntos y las pruebas de la aritmética** - `b5364b6` (test)
3. **Tarea 3: la integridad de un componente, y AGENTS.md al día** - `a5f55a4` (feat)

## Files Created/Modified
- `src/validar.py` - `regla_2` reescrita: filtra `self.c.aportes()` por rubro, compara contra
  `r.base`, convierte el global una vez por rubro con `r.a_porcentaje()`, y añade las dos
  comprobaciones de integridad de un componente (rubro inexistente, valor negativo).
- `pruebas/test_validar.py` - fixture `CURSO_EN_PUNTOS` + helpers `curso_en_puntos()`,
  `informe_en_puntos()`, `_rubro()`, `_meta_de()`; nueve pruebas nuevas en `Regla2Metas`.
- `AGENTS.md` - fila de R2 de la tabla de las ocho reglas y el párrafo que la justifica,
  puestos al día con el comportamiento real desde la Fase 10.

## Decisions Made
Ninguna nueva — el plan fija la redacción exacta del código y de las pruebas (D-04 a D-09,
D-12 de `10-CONTEXT.md`); se siguió tal cual, incluida la restricción literal de D-07 sobre el
mensaje global.

## Deviations from Plan

None - plan ejecutado exactamente como estaba escrito.

## Issues Encountered

None.

## User Setup Required

None - no requiere configuración de servicios externos.

## Next Phase Readiness

`Curso.aportes()` ya tiene dos consumidores reales (R2 aquí, y el 10-01 que lo dejó listo).
El plan 10-03 puede filtrar el mismo accesor por `tipo` para el conteo de exámenes parciales
de R3 (D-03, D-10 de `10-CONTEXT.md`), sin derivar su propia suma.

Verificación de cierre del plan:
- `python -X utf8 -m unittest discover -s pruebas` → 233 pruebas, exit 0 (224 previas + 9
  nuevas), sin tocar ninguna prueba existente.
- `python -X utf8 src/validar.py cursos/2026-2/39056-big-data/curso.yaml` → `VÁLIDO`, exit 0,
  sin la subcadena `R2` en la salida.
- `python -X utf8 src/validar.py cursos/2026-2/39062-patrones-de-comportamiento/curso.yaml` →
  igual, `VÁLIDO`, exit 0, sin `R2`.
- `python -X utf8 src/huella.py verificar` → 4 documentos comparados, huella intacta
  (REQ-48, D-15).
- `grep -c "El valor de las metas suma" src/validar.py` → 1 (D-07 intacto).
- `git diff 4e7f2f0 --name-only -- src pruebas AGENTS.md` → `src/validar.py`,
  `pruebas/test_validar.py`, `AGENTS.md` de este plan, más `src/modelo.py` y
  `pruebas/test_modelo.py` del plan 10-01 previo. Ninguna línea de las pruebas 169-217
  originales de `Regla2Metas` se borró.

---
*Phase: 10-reglas-en-la-unidad-declarada*
*Completed: 2026-08-05*

## Self-Check: PASSED

- FOUND: src/validar.py
- FOUND: pruebas/test_validar.py
- FOUND: AGENTS.md
- FOUND: .planning/phases/10-reglas-en-la-unidad-declarada/10-02-SUMMARY.md
- FOUND: commit 74f68eb
- FOUND: commit b5364b6
- FOUND: commit a5f55a4
