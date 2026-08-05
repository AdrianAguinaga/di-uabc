---
phase: 09-valor-de-una-meta
plan: 02
subsystem: model
tags: [dataclasses, yaml-schema, pyyaml]

# Dependency graph
requires:
  - phase: 09-01
    provides: "src/huella.py y la línea base del repositorio, registrada antes de tocar el modelo (D-15)"
provides:
  - "Rubro.unidad/total, con validación de vocabulario cerrado y total obligatorio (REQ-38)"
  - "Rubro.a_porcentaje(valor): la conversión de puntos a porcentaje en un solo sitio, lista para las Fases 10 y 13"
  - "dataclass Componente y Meta.componentes: una meta puede aportar a un rubro adicional sin dejar de ser una meta con una semana (REQ-39)"
  - "pruebas/test_modelo.py: 18 pruebas nuevas del esquema de curso.yaml, separadas de las pruebas de reglas"
  - "Confirmación por prueba de que los identificadores libres cargan y conservan el orden declarado (REQ-42), sin tocar código de src/"
affects: [09-03, 09-04, 09-05, 09-06, 10-reglas-en-la-unidad, 13-documento-en-unidad-real]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Vocabulario cerrado validado en __post_init__ con mensaje 'qué está mal + qué vale', calcado del patrón ya usado en Sesion.ambiente y Meta.tipo"
    - "Construcción de sub-objetos: d.pop('componentes', []) mapeado con un constructor propio (_construir_componente), mismo patrón que evidencias/sesiones en _construir_meta"
    - "La forma corta de evidencia (cadena en vez de mapa) se reusa tal cual para Componente.evidencia"

key-files:
  created:
    - pruebas/test_modelo.py
  modified:
    - src/modelo.py

key-decisions:
  - "Import de la fixture compartida con fallback: 'from test_validar import ...' funciona bajo unittest discover; 'from pruebas.test_validar import ...' cubre la invocación pruebas.test_modelo -v (namespace package sin __init__.py) — ambas formas de correr la suite quedan cubiertas"
  - "Componente.tipo sin valor por omisión (D-26): un default silencioso convertiría un typo en un componente que nadie cuenta"
  - "No se tocó desde_dict, src/validar.py ni src/grafo.py: los campos nuevos llevan default y las claves nuevas se resuelven en los constructores de sub-objeto, tal como pedía el plan"

requirements-completed: [REQ-38, REQ-39, REQ-42]

# Metrics
duration: ~35min
completed: 2026-08-05
---

# Fase 9 Plan 2: El contrato de curso.yaml se abre en tres puntos Summary

**`Rubro` gana `unidad`/`total` con conversión a porcentaje en un solo método, `Meta` gana `componentes` (misma semana, otro rubro), y los identificadores libres quedan fijados con prueba — sin tocar `desde_dict`, `validar.py` ni los tres `curso.yaml` existentes.**

## Performance

- **Duration:** ~35 min
- **Started:** 2026-08-05T16:55Z (aprox., tras corregir la base del worktree)
- **Completed:** 2026-08-05T17:30Z (aprox.)
- **Tasks:** 3
- **Files modified:** 2 (1 creado, 1 modificado)

## Accomplishments
- `pruebas/test_modelo.py` nuevo: 18 pruebas en cuatro clases (`RubroEnPuntos`, `ComponentesDeMeta`, `IdentificadoresLibres`, `LosCursosExistentesNoCambian`), escritas antes de la implementación y verificadas en rojo antes de las tareas 2 y 3.
- `src/modelo.py` extendido, no reemplazado: `UNIDADES_RUBRO`, `Rubro.unidad`/`total`/`base`/`a_porcentaje()`, `TIPOS_COMPONENTE`, `dataclass Componente`, `Meta.componentes`, `_construir_componente`.
- Los tres `curso.yaml` reales (39056, 39062, 38985) siguen cargando sin tocarse: sus rubros quedan en `unidad == ""` y sus metas en `componentes == []`, confirmado por prueba con `subTest` por curso.
- Suite completa: 210 pruebas en verde (179 previas a la fase + 13 de `test_huella` de 09-01 + 18 de `test_modelo`).

## Task Commits

Each task was committed atomically:

1. **Tarea 1: pruebas/test_modelo.py — la Ola 0 del contrato nuevo** - `d80c830` (test)
2. **Tarea 2: Rubro en puntos y la conversión a porcentaje (REQ-38)** - `399296c` (feat)
3. **Tarea 3: Componentes de meta e identificadores libres (REQ-39, REQ-42)** - `5e87c6d` (feat)

**Plan metadata:** (este commit) `docs(09-02): completa el plan`

## Files Created/Modified
- `pruebas/test_modelo.py` - 18 pruebas del esquema nuevo: rubro en puntos, componentes de meta, identificadores libres, y la mitad de REQ-48 (los tres cursos reales no cambian)
- `src/modelo.py` - `Rubro` gana `unidad`/`total`/`base`/`a_porcentaje()`; `Componente` nuevo; `Meta.componentes`; `_construir_componente`

## Decisions Made
- El import de la fixture compartida (`CURSO_VALIDO`, `_meta`) desde `test_validar` necesitaba cubrir dos formas distintas de invocar la suite: `python -m unittest discover -s pruebas` (que añade el directorio `pruebas/` directamente a `sys.path`, así que `from test_validar import ...` funciona) y `python -m unittest pruebas.test_modelo -v` (que importa `pruebas` como paquete de espacio de nombres desde el cwd, así que necesita `from pruebas.test_validar import ...`). Se resolvió con un `try/except ImportError` que intenta la primera forma y cae a la segunda — exactamente la alternativa que el propio plan anticipaba en el texto de la Tarea 1, solo que confirmada como necesaria en la práctica y no solo como salvaguarda.
- La clase `LosCursosExistentesNoCambian` de la Tarea 1 comprueba tanto `unidad`/`total` (Tarea 2) como `componentes` (Tarea 3) en una sola prueba con `subTest`. Esto significa que el criterio de aceptación de la Tarea 2 que pide `LosCursosExistentesNoCambian -v` en verde no se cumple literalmente hasta terminar la Tarea 3 — es una dependencia esperada entre tareas del mismo plan, no un defecto: la clase RubroEnPuntos (que sí es exclusiva de la Tarea 2) pasó en verde, y `LosCursosExistentesNoCambian` pasa en verde tras la Tarea 3, como confirma la corrida final de `discover -s pruebas`.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] El worktree estaba basado en un commit anterior a 09-01**
- **Found during:** Verificación inicial de rama (paso obligatorio antes de leer el plan)
- **Issue:** `git merge-base HEAD <base esperada>` no coincidía; el worktree se había creado desde `master` antes de que 09-01 existiera, así que `src/huella.py`, `pruebas/test_huella.py` y `pruebas/huellas.yaml` no estaban presentes.
- **Fix:** `git reset --hard` a la base esperada, con el árbol de trabajo confirmado limpio antes de la operación (sin pérdida de trabajo).
- **Files modified:** ninguno (operación de git sobre el estado del worktree)
- **Commit:** n/a (no genera commit)

**2. [Rule 1 - Bug] El import de la fixture de pruebas fallaba con una de las dos formas de invocación**
- **Found during:** Tarea 1, verificación con `python -X utf8 -m unittest pruebas.test_modelo -v`
- **Issue:** `from test_validar import CURSO_VALIDO, _meta` funciona bajo `discover -s pruebas` pero no bajo `unittest pruebas.test_modelo -v` (el plan de Tarea 2/3 usa esta segunda forma en su comando `<verify>`).
- **Fix:** `try: from test_validar import ...; except ImportError: from pruebas.test_validar import ...` — el propio plan ya anticipaba esta alternativa como salvaguarda; se aplicó porque resultó necesaria en la práctica.
- **Files modified:** `pruebas/test_modelo.py`
- **Commit:** `d80c830` (incluido en la Tarea 1, antes del commit)

---

**Total deviations:** 2 auto-fijadas (1 de rama del worktree, 1 de import) — ninguna afectó el diseño ni el contrato final.
**Impact on plan:** Ninguno en el comportamiento final; ambas se resolvieron dentro de la misma tarea donde se detectaron.

## Issues Encountered
Ninguno más allá de las dos desviaciones documentadas arriba.

## User Setup Required
None - no se necesita configuración externa.

## Next Phase Readiness
- El contrato `curso.yaml` queda abierto en los tres puntos de la fase: unidad del rubro, componentes de meta e identificadores libres.
- `Rubro.a_porcentaje()` está listo para que la Fase 10 (reglas en la unidad declarada) y la Fase 13 (documento en unidad real) lo consuman sin reinventar la conversión.
- `src/validar.py`, `src/grafo.py` y `src/render_docx.py` no se tocaron en este plan — quedan intactos para 09-03 (que trabaja en paralelo sobre `src/validar.py`) y para los planes de renderizado posteriores de esta misma fase.
- Sin bloqueos para 09-03 ni para el resto de la Fase 9.

---
*Phase: 09-valor-de-una-meta*
*Completed: 2026-08-05*
