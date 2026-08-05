---
phase: 09-valor-de-una-meta
plan: 01
subsystem: testing
tags: [python-docx, yaml, sha256, ooxml, regression-guard]

# Dependency graph
requires: []
provides:
  - "src/huella.py: instrumento de la no contaminación (REQ-48), con CLI verificar/registrar"
  - "pruebas/huellas.yaml: línea base de las cuatro huellas de control (39056/961, 39056/962, 39062/971, 39062/972)"
  - "Tres hashes por documento: texto_docx, informe, manifiesto (forma) — D-27"
affects: [09-02, 09-03, 09-04, 09-05, 09-06, 10-reglas-en-la-unidad, 11-segundo-nivel, 12-rubrica, 13-documento-en-unidad-real, 14-38985-sin-traducirse]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "CLI de subcomandos calcado de src/plantillas.py (main(argv), códigos 0/1/2)"
    - "extraer_texto() recorre document.element.body.iterchildren() en vez de doc.paragraphs/doc.tables, para conservar el orden real y evitar la duplicación de vMerge"
    - "forma_del_manifiesto() hashea el YAML con claves volátiles (generado, commit, sha256, bytes) quitadas antes de dumpear — vigila estructura, no valores"
    - "verificar() lee los bytes del MANIFIESTO.yaml antes de generar y los restaura en un finally, sin invocar git (D-28)"

key-files:
  created:
    - src/huella.py
    - pruebas/test_huella.py
    - pruebas/huellas.yaml
  modified:
    - cursos/2026-2/39056-big-data/MANIFIESTO.yaml
    - cursos/2026-2/39062-patrones-de-comportamiento/MANIFIESTO.yaml

key-decisions:
  - "La línea base se registró antes de que ninguna tarea del resto de la fase tocara el modelo (paso 1 de D-15)"
  - "huella verificar restaura los MANIFIESTO.yaml leyendo sus bytes antes de generar, no con git checkout (D-28): es de solo lectura sobre el repo y funciona fuera de git"
  - "registrar() dejó los MANIFIESTO.yaml de 39056 y 39062 reescritos con pdf=False: ya no listan sus .pdf, solo los .docx de esta corrida — coherente con el diseño 'solo los de esta corrida' del manifiesto"

requirements-completed: [REQ-48]

# Metrics
duration: ~20min
completed: 2026-08-05
---

# Fase 9 Plan 1: El instrumento de la no contaminación Summary

**`src/huella.py` con CLI verificar/registrar, tres hashes por documento (texto, informe, forma del MANIFIESTO.yaml) y la línea base de los cuatro documentos de control ya registrada.**

## Performance

- **Duration:** ~20 min
- **Started:** 2026-08-05T16:35Z (aprox.)
- **Completed:** 2026-08-05T16:51:44Z
- **Tasks:** 3
- **Files modified:** 5 (3 creados, 2 modificados)

## Accomplishments
- `src/huella.py`: `extraer_texto()`, `forma_del_manifiesto()`, `sha_texto()`, `cargar()`/`guardar()`, `verificar()`, `registrar()`, `main()` — todo reusando `generar.paquete()`, sin reimplementar validar→renderizar.
- 13 pruebas rápidas y aisladas en `pruebas/test_huella.py`, ninguna invoca `generar.paquete()` (D-18): la suite sigue en ~14-26 s.
- Línea base registrada con el repositorio tal como estaba antes de tocar el modelo: cuatro documentos, tres hashes cada uno (D-27).

## Task Commits

Each task was committed atomically:

1. **Tarea 1: src/huella.py — extracción, registro y CLI** - `68f5160` (feat)
2. **Tarea 2: pruebas/test_huella.py** - `476c5ea` (test)
3. **Tarea 3: Registrar la línea base del repositorio** - `998d005` (chore)

**Plan metadata:** (este commit) `docs(09-01): completa el plan`

## Files Created/Modified
- `src/huella.py` - CLI del instrumento REQ-48: extracción determinista de texto OOXML, forma del manifiesto, registro versionado
- `pruebas/test_huella.py` - 13 pruebas de `extraer_texto`, `forma_del_manifiesto` y el registro, contra fixtures sintéticos
- `pruebas/huellas.yaml` - registro versionado con las cuatro entradas de control
- `cursos/2026-2/39056-big-data/MANIFIESTO.yaml` - reescrito por `huella registrar` (pdf=False)
- `cursos/2026-2/39062-patrones-de-comportamiento/MANIFIESTO.yaml` - reescrito por `huella registrar` (pdf=False)

## Decisions Made
- El orden de los pasos de la Tarea 3 siguió literalmente D-15/D-24: confirmar árbol limpio → `registrar` → `verificar` → comprobar que `verificar` no mueve nada más allá de lo que `registrar` ya dejó escrito → `registrar` de nuevo para confirmar idempotencia → revisión a ojo del YAML.
- Para comprobar que `verificar` es de solo lectura se compararon los hashes sha256 de los dos `MANIFIESTO.yaml` antes y después de una segunda corrida de `verificar` (idénticos), en vez de solo mirar `git status --porcelain cursos/` — ese comando sigue mostrando los archivos como modificados mientras el cambio de `registrar` no esté comprometido en un commit, lo cual es esperado y está anotado en el propio plan (nota del paso 4 de la Tarea 3).

## Deviations from Plan

**1. [Rule 1 - Bug] Docstring de `pruebas/test_huella.py` contenía la cadena prohibida `generar.paquete()`**
- **Found during:** Tarea 2, verificación de criterios de aceptación
- **Issue:** El docstring del módulo mencionaba literalmente `generar.paquete()` para explicar por qué las pruebas no lo invocan. El criterio de aceptación exige que el archivo **no contenga** esa cadena, para que un grep futuro no dé un falso positivo.
- **Fix:** Se reescribió la frase sin nombrar la función literal («abrir dos cursos completos con el generador» en vez de citar `generar.paquete()`).
- **Files modified:** `pruebas/test_huella.py`
- **Verificación:** `grep -n "generar.paquete\|import generar" pruebas/test_huella.py` sale vacío (exit 1); las 13 pruebas siguen en verde.
- **Committed in:** `476c5ea` (Tarea 2, antes del commit — el ajuste se hizo antes de commitear)

---

**Total deviations:** 1 auto-fixed (1 bug de redacción, sin impacto funcional)
**Impact on plan:** Ninguno en el comportamiento; solo texto de un docstring.

## Issues Encountered
Ninguno. Las siete funciones del módulo, las 13 pruebas y el registro de la línea base
salieron según lo especificado en el plan, célula por célula.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- El instrumento REQ-48 queda disponible para las cinco fases siguientes del milestone v2.0.
- La línea base está tomada **antes** de que 09-02 (o cualquier plan posterior) toque `src/modelo.py`, cumpliendo el requisito de orden de D-15.
- `python src/huella.py verificar` corre en verde y `git status --porcelain cursos/` queda vacío después.
- Sin bloqueos para 09-02.

---
*Phase: 09-valor-de-una-meta*
*Completed: 2026-08-05*

## Self-Check: PASSED

Todos los archivos declarados existen (`src/huella.py`, `pruebas/test_huella.py`,
`pruebas/huellas.yaml`, este SUMMARY) y los tres hashes de tarea (`68f5160`, `476c5ea`,
`998d005`) están en el historial de `master`.
