---
phase: 09-valor-de-una-meta
plan: 05
subsystem: cursos
tags: [huella, renombrado, grafo, REQ-42, REQ-48]

# Dependency graph
requires:
  - phase: 09-01
    provides: "src/huella.py y la línea base de pruebas/huellas.yaml"
  - phase: 09-02
    provides: "Identificadores de meta libres en el modelo (REQ-42)"
  - phase: 09-03
    provides: "R2 detecta metas con id duplicado"
  - phase: 09-04
    provides: "La evidencia de un componente en la Sección 2"
provides:
  - "El encuadre de Big Data declarado como 1.0, con el grafo siguiéndolo"
  - "Línea base de huellas actualizada: el único cambio de huella del milestone, aceptado a propósito"
  - "Constancia medida de que el renombrado no cambió el documento más allá del identificador"
affects: [09-06, 13-documento-en-unidad-real]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Medir antes de aceptar: verificar en verde → cambio → verificar señalando → registrar"

key-files:
  created: []
  modified:
    - cursos/2026-2/39056-big-data/curso.yaml
    - cursos/2026-2/39056-big-data/MANIFIESTO.yaml
    - cursos/2026-2/39062-patrones-de-comportamiento/MANIFIESTO.yaml
    - grafo/grafo.json
    - grafo/index.html
    - grafo/AUDITORIA.md
    - pruebas/huellas.yaml

key-decisions:
  - "El identificador de una meta aparece en TRES cadenas del documento, no en una: «Meta 1.0.» en la tabla de la Sección 2, «Meta 1.0.» como encabezado de la Sección 3, y «La meta 1.0 equivale al 0%…» en la línea de valor. La comprobación del plan solo revertía la primera forma; se amplió a las tres y entonces el sha coincidió exactamente con la línea base previa al renombrado"
  - "El recurso M0_Foro de presentación NO se renombró, a propósito (D-14): meter un cambio más habría contaminado la medición del criterio 3. Queda pendiente acordarlo con el docente"
  - "generar.paquete() invocado a mano NO restaura el MANIFIESTO.yaml; huella verificar tampoco lo repara, porque restaura el archivo tal como estaba al empezar. La forma de dejarlo consistente es huella registrar, que regenera con la lista completa de grupos de CONTROL"

requirements-completed: [REQ-42, REQ-48]

# Metrics
duration: ~40min (con una interrupción entre la Tarea 2 y la Tarea 3)
completed: 2026-08-05
---

# Fase 9 Plan 5: El renombrado como prueba de fuego Summary

**El encuadre de Big Data se llama `1.0` y el documento quedó idéntico salvo las tres apariciones del identificador — ninguna función de `src/` deducía el encuadre por su id. El instrumento de huella demostró sus dos modos: dijo «nada cambió» tras abrir el contrato, y señaló exactamente qué cambió tras el renombrado.**

## Performance

- **Duration:** ~40 min
- **Tasks:** 3
- **Files modified:** 7 (ninguno creado)

## Accomplishments

**Paso 3 — el contrato no contaminó nada.** Con los planes 09-02, 09-03 y 09-04 ya integrados,
`python -X utf8 src/huella.py verificar` salió 0 con `Todo intacto. 4 documentos comparados.`
Abrir el contrato en tres puntos —rubro en puntos, componentes de meta, ids libres— no cambió ni un
carácter de los cursos que no declaran nada de eso, ni la forma de su manifiesto. REQ-48 cumplido
para toda la ola previa.

**Pasos 4 y 5 — renombrado y grafo.** Una sola línea de
`cursos/2026-2/39056-big-data/curso.yaml` (`id: "0"` → `id: "1.0"`), confirmada con
`git diff --numstat` reportando `1	1`. `python src/grafo.py` regeneró los tres archivos de `grafo/`:
**377 nodos y 669 aristas, idéntico a antes**. `AUDITORIA.md` sigue cerrando sin huecos nuevos —el
único hueco listado es el ya conocido y correcto de «Contabilidad Financiera · 2026-2», cuyo PUA no
está ingerido. `src/validar.py` imprime `VÁLIDO` sobre el curso renombrado.

**Pasos 6 y 7 — medir y aceptar.** `huella verificar` señaló los dos grupos de 39056 con dos líneas
cada uno (texto del documento + forma del MANIFIESTO.yaml, esta última esperada porque el manifiesto
registra el `sha256` del `curso.yaml`), y dejó 39062 intacto en sus cuatro campos. `huella registrar`
escribió la línea base nueva: en `git diff pruebas/huellas.yaml` cambian exactamente cuatro valores,
los `texto_docx` y `manifiesto` de 961 y 962, y ninguno de 39062.

**La constancia del criterio 3.** Regenerando el `.docx` y revirtiendo en su texto las tres
apariciones del identificador, el sha resultante coincide **exactamente** con el `texto_docx` que
estaba registrado antes del renombrado, en ambos grupos:

| Grupo | sha con el id revertido | Línea base previa | |
|---|---|---|---|
| 961 | `d33cea2e…90c7f8` | `d33cea2e…90c7f8` | igual |
| 962 | `3ba6984a…c0e1892` | `3ba6984a…c0e1892` | igual |

Esa igualdad es la demostración pedida: el renombrado no movió nada más del documento.

## Task Commits

1. **Tarea 1: Paso 3 — el contrato no contaminó nada** — sin commit (la tarea solo mide, no escribe)
2. **Tarea 2: Pasos 4 y 5 — renombrar el encuadre y regenerar el grafo** — `90bca69` (feat)
3. **Tarea 3: Pasos 6 y 7 — medir el cambio y aceptarlo** — `926ff41` (feat)

## Files Created/Modified

- `cursos/2026-2/39056-big-data/curso.yaml` — una línea: el id del encuadre.
- `grafo/grafo.json`, `grafo/index.html`, `grafo/AUDITORIA.md` — regenerados; misma forma, cadenas
  y claves de nodo actualizadas (`meta:2026-2:39056:0` → `meta:2026-2:39056:1.0`).
- `pruebas/huellas.yaml` — línea base nueva para los dos grupos de 39056.
- Los dos `MANIFIESTO.yaml` de control — reescritos por `registrar`, como está documentado.

## Decisions Made

- **El id aparece en tres cadenas, no en una.** El plan proponía comprobar el alcance del cambio
  revirtiendo `"Meta 1.0."` → `"Meta 0."` en el texto extraído. Con esa sola sustitución el sha **no**
  coincidía. El documento tiene además la línea `"La meta 1.0 equivale al 0% de tu calificación
  final."`, que también deriva del id. Revirtiendo las dos formas, el sha coincide exacto. No es un
  fallo del criterio: las tres apariciones son el identificador impreso, y no hay ninguna otra
  diferencia en el documento. El criterio 3 queda demostrado; lo que estaba incompleto era la
  comprobación escrita en el plan.
- **`grep -c "Meta 0\." grafo/grafo.json` devuelve 1, no 0.** El criterio de aceptación esperaba 0.
  La aparición que queda es `meta:2026-2:39062:0` — el encuadre del curso de control, que sigue
  llamándose `0` porque no debía tocarse. No queda ningún nodo `meta:2026-2:39056:0`. El criterio
  correcto es ese, no el conteo global.
- **El recurso `M0_Foro de presentación` no se tocó** (D-14). Con la meta ya renombrada a `1.0`, el
  nombre del recurso queda descoordinado. Es deliberado: cambiarlo habría metido una diferencia más
  en el documento y contaminado la medición. **Pendiente de acordar con el docente.**

## Deviations from Plan

1. **Comprobación del criterio 3 ampliada** — descrita arriba. La sustitución del plan era
   incompleta; se añadió la segunda forma del identificador. El resultado es el que el plan pedía.
2. **Criterio `grep -c "Meta 0\."` reinterpretado** — descrito arriba. Se comprobó lo que el criterio
   quería decir (ningún nodo de 39056 con el id viejo) en vez de su forma literal.
3. **Un `registrar` extra** — al ejecutar la comprobación del criterio 3, las llamadas directas a
   `generar.paquete(..., grupos=['962'])` dejaron el `MANIFIESTO.yaml` de 39056 listando un solo
   grupo. `huella verificar` no lo repara (restaura el archivo tal como estaba al empezar, que ya
   era el roto). Se corrigió corriendo `huella registrar` de nuevo, que regenera con la lista
   completa de `CONTROL` y reportó `sin cambios` en las cuatro huellas — es decir, la corrección no
   movió ningún hash: solo devolvió el archivo a su forma completa.

## Issues Encountered

El punto 3 de arriba. Vale la pena anotarlo para las cinco fases siguientes: **`generar.paquete()`
llamado a mano escribe el `MANIFIESTO.yaml` con los grupos que le pases y no lo restaura**. Si se usa
para diagnosticar, hay que cerrar con `huella registrar` (o `git checkout` del manifiesto) antes de
commitear.

## User Setup Required

Ninguna configuración externa. Sí queda **una decisión pendiente para el docente**: si el recurso
`M0_Foro de presentación` debe renombrarse ahora que su meta se llama `1.0`.

## Next Phase Readiness

- Criterio 3 del ROADMAP §Fase 9 demostrado sobre el repositorio real.
- Criterio 4 ejercido en sus dos modos: el instrumento supo callar y supo señalar.
- El instrumento vuelve a estar en verde —`verificar` sale 0, `git status --porcelain cursos/`
  vacío— para las cinco fases siguientes.
- `python src/plantillas.py verificar` en verde: nada escribió sobre las plantillas.
- 216 pruebas en verde.
- El plan 09-06 (comprobación humana del documento) puede empezar.

---
*Phase: 09-valor-de-una-meta*
*Completed: 2026-08-05*

## Self-Check: PASSED

- FOUND: cursos/2026-2/39056-big-data/curso.yaml (`id: "1.0"`, 1 ocurrencia)
- FOUND: pruebas/huellas.yaml (clave `documentos:`)
- FOUND: grafo/grafo.json (`Meta 1.0.`, 377 nodos / 669 aristas)
- FOUND: .planning/phases/09-valor-de-una-meta/09-05-SUMMARY.md
- FOUND: commit 90bca69
- FOUND: commit 926ff41
