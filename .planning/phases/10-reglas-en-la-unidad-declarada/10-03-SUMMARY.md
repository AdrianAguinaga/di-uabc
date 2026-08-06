---
phase: 10-reglas-en-la-unidad-declarada
plan: 03
subsystem: validation
tags: [validar, r3, examen_parcial, aportes, curso.yaml]

# Dependency graph
requires:
  - phase: 10-reglas-en-la-unidad-declarada
    provides: "dataclass Aporte y Curso.aportes() en src/modelo.py (plan 10-01); regla_2
      reescrita sobre el mismo accesor (plan 10-02)"
provides:
  - "regla_3 reescrita: cuenta aportes de tipo examen_parcial, vengan de una meta o de un
    componente de la actividad de otra meta"
  - "fixture CURSO_CON_EXAMENES_EN_COMPONENTES en pruebas/test_validar.py, con cuatro pruebas
    nuevas en Regla3Parciales"
  - "el aviso de parciales: reformulado (D-11), ya no habla de metas de tipo examen_parcial"
  - "fila de R3 en AGENTS.md al día con el comportamiento real"
affects: ["13"]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "R3 filtra Curso.aportes() por tipo en vez de derivar su propia suma sobre las metas —
      mismo patrón que R2 desde el plan 10-02, así que R2 y R3 comparten una sola definición
      de aporte"

key-files:
  created: []
  modified:
    - src/validar.py
    - pruebas/test_validar.py
    - AGENTS.md

key-decisions:
  - "D-03/D-10/D-11 de 10-CONTEXT.md se siguieron al pie de la letra: R3 consume el mismo
    accesor filtrando por tipo, cada aporte cuenta uno sin deduplicar por meta, y el aviso de
    parciales: sigue siendo aviso, solo se reformula el texto"

patterns-established: []

requirements-completed: [REQ-40]

# Metrics
duration: 6min
completed: 2026-08-05
---

# Fase 10 Plan 03: R3 en la unidad declarada Summary

**`regla_3` reescrita sobre `Curso.aportes()`: cuenta cada aporte de tipo `examen_parcial`
venga de una meta propia o de un componente dentro de la actividad de otra meta, y el aviso
de `parciales:` deja de mentir sobre dónde vive el examen.**

## Performance

- **Duration:** 6 min (entre el commit 0576d5d y el 6a85549)
- **Started:** 2026-08-05T20:02:08-07:00
- **Completed:** 2026-08-05T20:03:26-07:00
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments
- `regla_3` deja de derivar `[m for m in self.c.metas if m.tipo == "examen_parcial"]` — que
  ignoraba cualquier examen declarado como componente de otra meta — y pasa a filtrar
  `Curso.aportes()` por `tipo`, exactamente el mismo patrón que R2 desde el plan 10-02 (D-03).
- El defecto real que la fase existe para admitir —los tres exámenes del DI de Contabilidad
  (531) viven dentro de la actividad de las metas 2.4, 3.3 y 6.0, y ninguna meta es de tipo
  `examen_parcial`— ahora lo cuenta correctamente R3: antes contaba cero y el documento no
  validaba.
- D-10 queda fijado con su propia prueba: una meta de tipo `examen_parcial` con un componente
  del mismo tipo cuenta dos, sin deduplicación por meta.
- El aviso de `parciales:` (D-11) se reformuló: deja de decir «hay N metas de tipo
  `examen_parcial`» y habla de exámenes parciales declarados, «contando los que viven como
  componente de la actividad de otra meta». Sigue siendo `self.aviso`, no `self.error` — su
  severidad no cambió.
- Fixture `CURSO_CON_EXAMENES_EN_COMPONENTES`: `CURSO_VALIDO` sin las metas `P1`/`P2`, con sus
  semanas absorbidas por `1.2` y `2.2`, y tres componentes `examen_parcial` (7+7+6 = 20, el
  20 % que el rubro «Exámenes» ya declaraba). Cuatro pruebas nuevas en `Regla3Parciales`
  ejercen el criterio 4 del roadmap en sus dos mitades, D-10 y D-11.
- `AGENTS.md` §«Las ocho reglas de validación» describe el comportamiento real de R3.
- Los cuatro documentos de control (39056×2, 39062×2) siguen validando limpios, sin un solo
  hallazgo de R3 ni R2 — verificado con `python src/huella.py verificar`.

## Task Commits

Each task was committed atomically:

1. **Tarea 1: R3 cuenta aportes, no metas** - `0576d5d` (feat)
2. **Tarea 2: el curso con los exámenes dentro de otras metas, y AGENTS.md al día** - `6a85549` (test)

## Files Created/Modified
- `src/validar.py` - `regla_3` reescrita: filtra `self.c.aportes()` por `tipo ==
  "examen_parcial"`, conserva el mensaje de error con la subcadena «68», y reformula el
  aviso de divergencia entre `parciales:` y los exámenes declarados.
- `pruebas/test_validar.py` - fixture `CURSO_CON_EXAMENES_EN_COMPONENTES` + helpers
  `curso_con_examenes()`, `informe_con_examenes()`; cuatro pruebas nuevas en
  `Regla3Parciales`.
- `AGENTS.md` - fila de R3 de la tabla de las ocho reglas, puesta al día con el
  comportamiento real desde la Fase 10.

## Decisions Made
Ninguna nueva — el plan fija la redacción exacta del código y de las pruebas (D-03, D-10,
D-11 de `10-CONTEXT.md`); se siguió tal cual, incluida la restricción literal sobre la
subcadena «68» del mensaje de error.

## Deviations from Plan

None - plan ejecutado exactamente como estaba escrito.

## Issues Encountered

Una corrida de la suite completa mostró un fallo transitorio (`FAILED (failures=1)`) sin
detalle de traza, coincidiendo con escrituras concurrentes a archivos temporales en el mismo
bloque de comandos. Tres corridas sucesivas posteriores, ya sin esa contención, dieron
`OK` con 237 pruebas. No se encontró ninguna prueba que falle de forma reproducible; se trató
como un flake del entorno, no del código de este plan.

## User Setup Required

None - no requiere configuración de servicios externos.

## Next Phase Readiness

R2 y R3 comparten ahora una sola definición de aporte (`Curso.aportes()`), sin que ninguna
derive la suya — el objetivo declarado en `<success_criteria>` de este plan. La Fase 13
(el documento) puede apoyarse en el mismo accesor para imprimir cada examen por separado,
con etiqueta y valor propios, tal como D-10 anticipa.

Verificación de cierre del plan:
- `python -X utf8 -m unittest discover -s pruebas` → 237 pruebas, exit 0 (233 previas + 4
  nuevas), sin tocar ninguna prueba existente.
- `python -X utf8 src/validar.py cursos/2026-2/39056-big-data/curso.yaml` → `VÁLIDO`, exit 0,
  sin la subcadena `R3` en la salida.
- `python -X utf8 src/validar.py cursos/2026-2/39062-patrones-de-comportamiento/curso.yaml` →
  igual, `VÁLIDO`, exit 0, sin `R3`.
- `python -X utf8 src/huella.py verificar` → 4 documentos comparados, huella intacta
  (REQ-48, D-15).
- `grep -n "metas de tipo" src/validar.py` → vacío (el aviso reformulado no menciona ya
  «metas de tipo»).
- `grep -c "def test_un_solo" pruebas/test_validar.py` → 2 (el nombre nuevo no pisó al
  existente).
- `git diff AGENTS.md | grep "^-" | grep -v "^---"` → una sola línea borrada, la fila vieja
  de R3.
- `git diff 4e7f2f0 --name-only -- src pruebas AGENTS.md` → `src/validar.py`,
  `pruebas/test_validar.py`, `AGENTS.md` de este plan, más `src/modelo.py` y
  `pruebas/test_modelo.py` del plan 10-01 previo. Ninguna línea de las pruebas 351-364
  originales de `Regla3Parciales` se borró.

---
*Phase: 10-reglas-en-la-unidad-declarada*
*Completed: 2026-08-05*

## Self-Check: PASSED

- FOUND: src/validar.py
- FOUND: pruebas/test_validar.py
- FOUND: AGENTS.md
- FOUND: .planning/phases/10-reglas-en-la-unidad-declarada/10-03-SUMMARY.md
- FOUND: commit 0576d5d
- FOUND: commit 6a85549
