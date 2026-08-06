---
phase: 10-reglas-en-la-unidad-declarada
plan: 01
subsystem: modelo
tags: [dataclass, generator, curso.yaml, aportes]

# Dependency graph
requires:
  - phase: 09-valor-de-una-meta
    provides: "Componente, Meta.componentes, Rubro.base y Rubro.a_porcentaje() en src/modelo.py"
provides:
  - "dataclass Aporte (frozen) con meta, rubro, valor, etiqueta, tipo, es_componente"
  - "Curso.aportes(): generador plano que emite el aporte de cada meta y luego el de cada
    uno de sus componentes, en la unidad cruda del rubro al que se imputa"
affects: ["10-02", "10-03", "13"]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Accesor único de agregación en el modelo (Curso.aportes()), consumido por filtro
      (rubro, tipo o meta) en vez de que cada regla derive su propia suma en línea"

key-files:
  created: []
  modified:
    - src/modelo.py
    - pruebas/test_modelo.py

key-decisions:
  - "D-01: la agregación vive una sola vez, en el modelo, como generador plano"
  - "D-02: el aporte sale en la unidad cruda de su rubro, sin convertir"

patterns-established:
  - "Aporte lleva la Meta entera (no su id), para que consumidores futuros (Fase 13) lleguen
    desde un aporte a su semana, sesiones y evidencias"

requirements-completed: [REQ-40, REQ-45]

# Metrics
duration: 12min
completed: 2026-08-05
---

# Fase 10 Plan 01: Accesor único de aportes en el modelo Summary

**dataclass `Aporte` (frozen) y generador plano `Curso.aportes()` en `src/modelo.py`, que
enumeran meta y componentes en la unidad cruda de su rubro — sin que ninguna regla los use
todavía.**

## Performance

- **Duration:** 12 min
- **Started:** 2026-08-05T00:00:00Z (aprox.)
- **Completed:** 2026-08-05
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments
- `Aporte` como dataclass congelado con seis campos, en el orden que fija el plan.
- `Curso.aportes()` emite, para cada meta, su propio aporte y luego el de cada componente,
  respetando el orden declarado.
- Seis pruebas nuevas fijan el contrato: aporte por meta sin `componentes:`, copia de
  rubro/valor/tipo, aporte propio del componente, orden meta-luego-componente, enlace de
  vuelta a la meta (`a.meta.semanas`) y valor sin convertir.
- Ninguna regla de `src/validar.py` ni `src/render_docx.py` se tocó: la suite queda verde con
  seis pruebas más, sin cambiar el comportamiento de ninguna regla existente.

## Task Commits

Each task was committed atomically:

1. **Tarea 1: dataclass `Aporte` y accesor `Curso.aportes()`** - `24c9d95` (feat)
2. **Tarea 2: pruebas del accesor plano** - `3f8170e` (test)

_Nota: el plan no pedía TDD; el orden feat→test refleja que las pruebas se escribieron después
de construir el accesor, tal como especifica el plan._

## Files Created/Modified
- `src/modelo.py` - añade `from collections.abc import Iterator`, el dataclass `Aporte`
  (entre `Grupo` y `Curso`) y el método `Curso.aportes()` (entre `metas_de()` y
  `nombre_archivo()`).
- `pruebas/test_modelo.py` - añade la clase `Aportes` con seis pruebas, antes de
  `LosCursosExistentesNoCambian`.

## Decisions Made
None — el plan fija el nombre del dataclass, sus campos, la posición del código y el texto
literal de las pruebas (D-01, D-02, D-03 de `10-CONTEXT.md`); se siguió tal cual.

## Deviations from Plan

None - plan ejecutado exactamente como estaba escrito.

## Issues Encountered

None.

## User Setup Required

None - no requiere configuración de servicios externos.

## Next Phase Readiness

`Curso.aportes()` queda disponible para que el plan 10-02 (R2, aritmética por rubro) y el
10-03 (R3, conteo de exámenes parciales) lo consuman filtrando por `rubro` y por `tipo`
respectivamente, sin derivar su propia suma. La Fase 13 podrá filtrar por `meta` cuando llegue,
usando `a.meta` para llegar a la semana y las evidencias.

Verificación de cierre del plan:
- `python -X utf8 -m unittest discover -s pruebas` → 224 pruebas, exit 0 (218 previas + 6
  nuevas).
- `python -X utf8 src/validar.py cursos/2026-2/39056-big-data/curso.yaml` → `VÁLIDO`, exit 0,
  cinco recordatorios IEDI, cero hallazgos de R2/R3 (línea base D-15 intacta).
- `python -X utf8 src/validar.py cursos/2026-2/39062-patrones-de-comportamiento/curso.yaml` →
  igual, `VÁLIDO`, exit 0.
- `git diff 4e7f2f0 --name-only -- src pruebas` → exactamente `src/modelo.py` y
  `pruebas/test_modelo.py`, sin tocar `src/validar.py` ni `src/render_docx.py`.

---
*Phase: 10-reglas-en-la-unidad-declarada*
*Completed: 2026-08-05*

## Self-Check: PASSED

- FOUND: src/modelo.py
- FOUND: pruebas/test_modelo.py
- FOUND: .planning/phases/10-reglas-en-la-unidad-declarada/10-01-SUMMARY.md
- FOUND: commit 24c9d95
- FOUND: commit 3f8170e
