---
phase: 09-valor-de-una-meta
plan: 03
subsystem: validation
tags: [python, collections.Counter, unittest, validacion-de-reglas]

# Dependency graph
requires:
  - phase: 09-01
    provides: "línea base de huella.py y pruebas/huellas.yaml registrada antes de tocar el modelo"
provides:
  - "R2 detecta ids de meta duplicados con Counter, mismo patrón que R1 usa para rubros"
  - "Dos pruebas hermanas en Regla2Metas que fijan el comportamiento: error de regla (no ErrorModelo) y carga sin reventar"
affects: [09-04, 09-05, 09-06, 10-reglas-en-la-unidad]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Counter(m.id for m in self.c.metas) al final de regla_2, calcado del Counter de rubros duplicados en regla_1 (validar.py:141)"

key-files:
  created: []
  modified:
    - src/validar.py
    - pruebas/test_validar.py

key-decisions:
  - "self.error, no self.aviso: dos metas con el mismo id bloquean el curso, no es decisión del docente (D-17)"
  - "No se tocó la aritmética de R1/R2 ni la distinción de encuadre por tipo (validar.py:394) — contar en la unidad declarada es Fase 10"

requirements-completed: [REQ-42]

# Metrics
duration: ~15min
completed: 2026-08-05
---

# Fase 9 Plan 3: R2 detecta metas con id duplicado Summary

**`Counter(m.id for m in self.c.metas)` en `regla_2`, calcado del patrón que R1 ya usa para rubros duplicados: dos metas con el mismo id ahora bloquean la validación en vez de pisar en silencio el mismo nodo del grafo.**

## Performance

- **Duration:** ~15 min
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments
- `src/validar.py`: `regla_2` gana tres líneas al final que cuentan ids de meta repetidos y reportan `error` de R2, exactamente el mismo molde que `regla_1` usa para `Rubros duplicados`.
- `pruebas/test_validar.py`: dos pruebas nuevas en `Regla2Metas` — `test_dos_metas_con_el_mismo_id_son_error_de_regla` (RED antes de la Tarea 2, verde después) y `test_el_curso_con_ids_repetidos_carga_igual` (confirma que es defecto de regla, no de esquema: el curso carga con `modelo.desde_dict` aunque tenga ids repetidos).
- Ninguna línea existente se tocó ni se reordenó: `git diff` de ambos archivos muestra solo inserciones (18 en la prueba, 3 en `validar.py`).

## Task Commits

Each task was committed atomically:

1. **Tarea 1: La prueba de las metas duplicadas** - `a385eb1` (test)
2. **Tarea 2: R2 cuenta los ids repetidos** - `a74ffdf` (feat)

**Plan metadata:** (este commit) `docs(09-03): completa el plan 3 de la Fase 9`

## Files Created/Modified
- `pruebas/test_validar.py` - dos métodos nuevos en `Regla2Metas`, byte por byte compatibles con los cinco existentes (incluyendo `test_detecta_el_defecto_del_ejemplo_961`, que no se tocó)
- `src/validar.py` - tres líneas al final de `regla_2`: `Counter` de ids de meta + `self.error("R2", ...)` si hay repetidos

## Decisions Made
- Se verificó primero que la Tarea 1 fallara **solo** en la prueba nueva de la colisión (`test_dos_metas_con_el_mismo_id_son_error_de_regla`), y que las otras cinco pruebas de `Regla2Metas` —incluida `test_el_curso_con_ids_repetidos_carga_igual`, que no depende de la comprobación nueva— siguieran en verde. Esto confirmó que el fallo venía de lo que falta implementar, no de un error en la prueba.
- El bloque nuevo de `regla_2` se insertó **sin** una línea en blanco extra entre él y el bloque de `negativas` que lo precede, reusando la línea en blanco que ya separaba `regla_2` de `regla_3` como único separador. Así el diff queda en exactamente 3 líneas añadidas y 0 eliminadas, tal como pide el criterio de aceptación de la Tarea 2.

## Deviations from Plan
None - plan executed exactly as written.

## Issues Encountered
- `python -X utf8 -m unittest discover -s pruebas` mostró una falla intermitente en
  `pruebas.test_export_pdf.ConversionReal.test_no_deja_procesos_de_word_huerfanos` (detecta
  `WINWORD.EXE` en `tasklist` tras correr la suite completa). Al correr esa prueba sola, pasa en
  verde. No tiene relación con `src/validar.py` ni `pruebas/test_validar.py` — los únicos archivos
  de este plan — y coincide con la ejecución en paralelo del plan 09-02 en otro worktree de la
  misma máquina, que también dispara Word por COM. Fuera de alcance según la regla de límite del
  executor; documentado en
  `.planning/phases/09-valor-de-una-meta/deferred-items.md` para revisarlo al cerrar la fase, sin
  ejecución paralela.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- `python -X utf8 -m unittest pruebas.test_validar -v` sale con código 0 (44 pruebas).
- `python -X utf8 src/validar.py cursos/2026-2/39056-big-data/curso.yaml` y
  `.../39062-patrones-de-comportamiento/curso.yaml` imprimen `VÁLIDO`: el informe de los dos
  documentos de control no cambió, así que la huella del plan 09-05 no debería moverse por este
  plan.
- La aritmética de R1/R2 y la distinción de encuadre por `tipo` (`validar.py:394`) quedan
  intactas, listas para que la Fase 10 las reescriba en la unidad declarada.
- Sin bloqueos para 09-04.

---
*Phase: 09-valor-de-una-meta*
*Completed: 2026-08-05*

## Self-Check: PASSED

`src/validar.py`, `pruebas/test_validar.py` y este SUMMARY existen; los dos hashes de tarea
(`a385eb1`, `a74ffdf`) están en el historial del worktree.
