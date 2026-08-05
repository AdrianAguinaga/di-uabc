---
phase: 09-valor-de-una-meta
plan: 06
subsystem: verificacion
tags: [word, diff, cierre-de-fase, REQ-48]

# Dependency graph
requires:
  - phase: 09-05
    provides: "El encuadre renombrado a 1.0, el grafo regenerado y la huella aceptada"
provides:
  - "Confirmación humana de que el .docx renombrado abre en Word y dice «Meta 1.0.»"
  - "Revisión humana del diff completo de la fase"
affects: [10-reglas-en-unidad-declarada]

# Tech tracking
tech-stack:
  added: []
  patterns: []

key-files:
  created: []
  modified: []

key-decisions:
  - "El usuario aprobó el cierre de la fase el 5 de agosto de 2026 tras abrir el documento en Word"
  - "Los dos cabos sueltos detectados (el prefijo M0_ del recurso y los .pdf ausentes del MANIFIESTO.yaml) se presentaron en el punto de verificación y quedan registrados como pendientes, no como bloqueos de la Fase 9"

requirements-completed: [REQ-48]

# Metrics
duration: ~5min
completed: 2026-08-05
---

# Fase 9 Plan 6: El cierre que ninguna prueba puede hacer Summary

**El usuario abrió el `.docx` de Big Data renombrado en Word, comprobó que dice «Meta 1.0.» donde decía «Meta 0.» y revisó el diff completo de la fase. Aprobado.**

## Performance

- **Duration:** ~5 min
- **Tasks:** 1 (checkpoint human-verify, bloqueante)
- **Files modified:** 0

## Accomplishments

Antes de convocar al usuario se dejó el terreno preparado, como pedía la tarea: se regeneró el
documento con `python -X utf8 src/generar.py cursos/2026-2/39056-big-data/curso.yaml --sin-pdf` y se
recogió el diff completo de la fase (`f28a773..HEAD`), separando lo que toca `cursos/` de lo demás.

Se presentó al usuario el estado comprobable por máquina:

| Comprobación | Resultado |
|---|---|
| `unittest discover -s pruebas` | 216 pruebas OK |
| `src/huella.py verificar` | `Todo intacto. 4 documentos comparados.` |
| `src/plantillas.py verificar` | Las tres plantillas coinciden con su registro |
| `src/validar.py` sobre 39056 | `VÁLIDO` |
| `grafo/grafo.json` | 377 nodos / 669 aristas — misma forma |
| `git diff --numstat` de `39056/curso.yaml` | `1  1` |
| `39062/curso.yaml`, `38985/curso.yaml` | intactos |
| `referencias/`, `ejemplos/`, `plantillas/` | fuera del diff de la fase |

Y las cuatro comprobaciones que solo una persona puede hacer: que Word abre el archivo sin pedir
reparación, que la Sección 2 y la Sección 3 dicen «Meta 1.0.», y que `grafo/index.html` no conserva
ninguna «Meta 0.» de 39056.

**Respuesta del usuario: «aprobado».**

## Task Commits

1. **Tarea 1: El documento renombrado abre en Word y el diff es el que se prometió** — sin commit
   (checkpoint de verificación; no modifica archivos)

## Files Created/Modified

Ninguno. El plan declara `files_modified: []` y así se ejecutó.

## Decisions Made

- Se presentaron al usuario, dentro del propio punto de verificación, los dos hallazgos que el plan
  09-05 dejó anotados, para que entraran en su juicio del diff en vez de descubrirse después.

## Deviations from Plan

Uno, menor. El plan pedía revisar el alcance con `git diff --stat` y `git diff cursos/` sobre el
árbol de trabajo, pero para cuando este plan corrió todo el trabajo de la fase ya estaba
commiteado, así que el árbol estaba limpio y esos comandos salían vacíos. Se presentó el diff
equivalente sobre el rango de la fase (`f28a773..HEAD`), que es lo que el criterio quería medir.

Al regenerar el `.docx` con `generar.py --sin-pdf` (paso 1 de la tarea) se reescribió el
`MANIFIESTO.yaml` de 39056 con un `sha256` de documento nuevo. Se restauró con `git checkout` para
que el árbol quedara idéntico al estado aceptado en 09-05: el `sha256` del `.docx` cambia en cada
generación y no forma parte de lo que la fase acordó.

## Issues Encountered

Ninguno nuevo. Los dos que se presentaron venían de 09-05:

1. **El recurso `M0_Foro de presentación`** conserva el prefijo viejo con su meta ya en `1.0`. Fue
   deliberado (D-14) para no contaminar la medición del criterio 3, que ya está hecha.
2. **Los `MANIFIESTO.yaml` de los dos cursos de control dejaron de listar los `.pdf`**, porque
   `huella registrar` genera con `pdf=False`. Los PDFs siguen en disco, pero los de 39056 son
   anteriores al renombrado y todavía dicen «Meta 0.».

Ninguno bloquea la Fase 9; ambos quedan anotados en STATE.md.

## User Setup Required

Dos decisiones pendientes del docente, ninguna urgente:

- Si el recurso `M0_Foro de presentación` debe renombrarse ahora que su meta se llama `1.0`.
- Si conviene que `huella.py` genere con PDF —o que el manifiesto de control se escriba aparte— para
  que los `.pdf` vuelvan a estar declarados y regenerados.

## Next Phase Readiness

- Los cinco criterios del ROADMAP §Fase 9 quedan verificados: los cuatro primeros por los planes
  09-01 a 09-05, el quinto (`unittest discover`) en cada uno de ellos, y el entregable comprobado por
  una persona en la aplicación en la que se abre de verdad.
- El contrato `curso.yaml` queda abierto en sus tres puntos y el instrumento de no contaminación en
  verde. La Fase 10 —las reglas contando en la unidad declarada— puede empezar.

---
*Phase: 09-valor-de-una-meta*
*Completed: 2026-08-05*

## Self-Check: PASSED

- FOUND: .planning/phases/09-valor-de-una-meta/09-06-SUMMARY.md
- CONFIRMED: aprobación del usuario, 2026-08-05
- NO-OP: el plan declara `files_modified: []` y no modificó ninguno
