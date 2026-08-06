---
phase: 11
slug: segundo-nivel-de-la-calificacion
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-06
---

# Fase 11 — Estrategia de validación

> Contrato de validación de la fase: con qué instrumento se muestrea cada comportamiento durante la
> ejecución. Derivado de `11-RESEARCH.md` §Validation Architecture.

---

## Infraestructura de pruebas

| Propiedad | Valor |
|---|---|
| **Framework** | `unittest` (stdlib) — sin runner de terceros |
| **Archivo de config** | ninguno — convención de directorio `pruebas/`, se descubre con `discover` |
| **Comando rápido** | `python -X utf8 -m unittest pruebas.test_validar -v` (o una clase concreta, p. ej. `pruebas.test_validar.Regla1SegundoNivel`) |
| **Comando completo** | `python -X utf8 -m unittest discover -s pruebas` |
| **Tiempo estimado** | ~16.5 s (**245 pruebas**, remedido en la investigación — la cifra de 179 del ROADMAP es la línea base de la v1.0, no la de hoy) |

---

## Frecuencia de muestreo

- **Tras cada commit de tarea:** `python -X utf8 -m unittest discover -s pruebas`
  (la suite completa son 16.5 s — no hace falta un comando rápido separado).
- **Tras cada ola:** suite completa en verde.
- **Antes de cerrar la fase:** suite completa **+** `python src/huella.py verificar` en verde, en ese
  orden (D-20). Las dos rutas son necesarias y no se solapan del todo — ver §REQ-48 abajo.
- **Latencia máxima de retroalimentación:** 20 s.

---

## Mapa de verificación por comportamiento

Los identificadores `B1`–`B15` son los de `11-RESEARCH.md` §Validation Architecture. La columna
**Plan / Tarea** la rellena el planeador; se deja explícita para que ningún comportamiento quede sin
dueño.

| # | Comportamiento | Req / Decisión | Tipo | Nivel de hallazgo | Comando automatizado | ¿Archivo existe? | Plan / Tarea | Estado |
|---|---|---|---|---|---|---|---|---|
| B1 | `segundo_nivel` 60/40 válido → carga y valida sin error nuevo | REQ-41 / criterio 1 / D-01 | unitario | silencio | `python -X utf8 -m unittest pruebas.test_validar.Regla1SegundoNivel -v` | ❌ Ola 0 — clase nueva en `test_validar.py` | TBD | ⬜ pendiente |
| B2 | `segundo_nivel` 60/30 (no suma 100) → error de R1 | REQ-46 / criterio 1 / D-12 | unitario | **error** R1 | idem | ❌ Ola 0 | TBD | ⬜ pendiente |
| B3 | `segundo_nivel` presente y `exencion_contra` ausente → `ErrorModelo` al cargar | REQ-41 / D-07 | unitario | **error** `ErrorModelo` | `python -X utf8 -m unittest pruebas.test_modelo -v` | ❌ Ola 0 — clase nueva en `test_modelo.py` | TBD | ⬜ pendiente |
| B4 | `exencion_contra` fuera del vocabulario cerrado → `ErrorModelo` al cargar | REQ-41 / D-06 | unitario | **error** `ErrorModelo` | idem | ❌ Ola 0 | TBD | ⬜ pendiente |
| B5 | `exencion_contra: calificacion_final` **con** segundo nivel → error de R1 | REQ-46 / criterio 3 / D-08 | unitario | **error** R1 | `python -X utf8 -m unittest pruebas.test_validar.Regla1SegundoNivel -v` | ❌ Ola 0 | TBD | ⬜ pendiente |
| B6 | `exencion_contra: calificacion_final` **sin** segundo nivel → aviso de R1 | REQ-46 / D-09 | unitario | **aviso** R1 | idem | ❌ Ola 0 | TBD | ⬜ pendiente |
| B7 | Segundo nivel 100/0 → aviso de R1 | D-13 | unitario | **aviso** R1 | idem | ❌ Ola 0 | TBD | ⬜ pendiente |
| B8 | Segundo nivel 0/100 → aviso de R1 | D-13 | unitario | **aviso** R1 | idem | ❌ Ola 0 | TBD | ⬜ pendiente |
| B9 | Contraste contra el catálogo: porcentajes y/o etiquetas divergen → aviso de R1 | D-05 / D-14 | unitario | **aviso** R1 | idem | ❌ Ola 0 | TBD | ⬜ pendiente |
| B10 | Curso sin `segundo_nivel` → cero cambio de comportamiento | REQ-48 / criterio 2 / D-03 | unitario | silencio | `python -X utf8 -m unittest pruebas.test_validar -v` | ✅ `PuntoDePartida` + `NoContaminacion` existentes | TBD | ⬜ pendiente |
| B11 | El `MANIFIESTO.yaml` registra las dos claves **solo** si el curso las declara | REQ-48 / D-16 | unitario | — (estructural) | `python -X utf8 -m unittest pruebas.test_generar -v` | ⚠ leer `test_generar.py` antes de decidir clase | TBD | ⬜ pendiente |
| B12 | La guarda `getsource` sigue sin ver `.base` / `a_porcentaje` / `.unidad` / `.total` / `.valor` en `regla_1` | D-11 / D-15 | unitario — **estructural** | — | `python -X utf8 -m unittest pruebas.test_validar -v` | ✅ ya existe — **no se toca** | — (falla sola) | ⬜ pendiente |
| B13 | 39056 / 39062 / 38985 siguen emitiendo **cero** hallazgos de R1 | REQ-48 / criterio 4 / D-17 | unitario | silencio | idem | ❌ Ola 0 — hermana de la de R2/R3 ya existente | TBD | ⬜ pendiente |
| B14 | 39056 / 39062 no declaran `segundo_nivel:` ni `exencion_contra:` en su YAML crudo | REQ-48 / D-17 | unitario — texto crudo | — | idem | ✅ ampliar `test_los_cursos_de_control_no_declaran_nada_de_la_v2` | TBD | ⬜ pendiente |
| B15 | Cierre REQ-48: huella de texto, informe y manifiesto de 39056 y 39062 intactos | REQ-48 / criterio 4 / D-20 | manual, fuera de la suite | — | `python src/huella.py verificar` | ✅ ya existe | TBD | ⬜ pendiente |
| — | Las 245 pruebas anteriores pasan intactas, más las nuevas | criterio 5 heredado | integración | — | `python -X utf8 -m unittest discover -s pruebas` | ✅ ya existe (245/245 en verde) | TBD | ⬜ pendiente |
| — | Ninguna plantilla de `referencias/` fue modificada | invariante del proyecto | integración | — | `python src/plantillas.py verificar` | ✅ ya existe | TBD | ⬜ pendiente |

**Tasa de muestreo (Nyquist) de esta fase.** 15 comportamientos distintos: 9 son la aritmética y el
vocabulario del segundo nivel (B1–B9), 3 son **silencio puro** (B10, B13, B14 — los más difíciles,
porque «no pasó nada» no es observable sin comparar contra una línea base, que es justo lo que
REQ-48 exige), 1 es estructural y ya está construida (B12, herencia de la Fase 10), 1 es la forma del
manifiesto (B11) y 1 es el cierre manual (B15). El mínimo que cubre cada comportamiento una vez es la
tabla completa; en pruebas reales eso son **10–12 pruebas nuevas**, no 15, porque B7/B8 pueden
resolverse con `subTest` en un solo test si D-13 termina usando un mensaje parametrizado.

---

## Pruebas existentes que NO deben romperse

Las dos primeras son **guardas estructurales frágiles**: pueden dejar de vigilar sin fallar.

| Prueba | Por qué es frágil | Qué la protege |
|---|---|---|
| `test_el_codigo_de_r1_no_menciona_la_unidad_de_ningun_rubro` (`test_validar.py:287-292`) | Si el plan saca la aritmética nueva a un método auxiliar, **deja de cubrir nada en silencio** — no falla, solo deja de vigilar (D-11 lo dice explícitamente). Es además una guarda **textual**: un comentario dentro de `regla_1` que mencione la palabra `a_porcentaje`, aunque sea para explicar por qué no se usa, la rompe | Escribir todo dentro de `regla_1`, nunca en un helper, y no nombrar los tokens prohibidos ni en comentarios |
| `test_poner_un_rubro_en_puntos_no_altera_lo_que_r1_comprueba` (`test_validar.py:281-285`) | Compara los mensajes de R1 con y sin rubros en puntos. Si el segundo nivel introdujera algo que lee la unidad de un rubro, esto aparece como cambio de mensajes — hay que leer el diff, no confiar en el verde | No referenciar `Rubro.unidad` / `.base` / `.total` desde el código del segundo nivel |
| `test_el_total_correcto_no_absuelve_al_rubro_incorrecto` | Exige el prefijo literal `"El valor de las metas suma"` (D-07 de la Fase 10). Esta fase no toca ese mensaje | R2 está fuera del alcance de esta fase |
| `test_detecta_el_defecto_del_ejemplo_961` | Solo comprueba que aparezcan dos etiquetas — es holgada, no una garantía fuerte | R2 está fuera del alcance de esta fase |

---

## Requisitos de Ola 0

- [ ] **Ampliación de `pruebas/test_validar.py`** — clase nueva (`Regla1SegundoNivel` o el nombre que
      el plan elija) para B1–B9, más la prueba de silencio de R1 sobre los tres cursos de control
      (B13) dentro de la clase `NoContaminacion` existente (`:691-724`), y la extensión de
      `test_los_cursos_de_control_no_declaran_nada_de_la_v2` (B14). Los fixtures se construyen con los
      helpers `curso(**cambios)` / `informe(**cambios)` que ya existen —hoy en **`:110-118`**, no
      `:104-112` como decía el CONTEXT.md— por `deepcopy` de `CURSO_VALIDO` (D-19).
- [ ] **Ampliación de `pruebas/test_modelo.py`** — clase nueva para `Nivel` / `SegundoNivel` /
      `exencion_contra` (B3, B4). Molde: las clases `RubroEnPuntos` y `ComponentesDeMeta` ya viven en
      ese archivo con el mismo estilo de fixture por `deepcopy`.
- [ ] **`pruebas/test_generar.py`** — **abrir y leer antes de planear la tarea de B11.** Hay que
      decidir si el manifiesto condicional entra en una clase existente o necesita una nueva; la
      investigación no lo abrió porque D-16 no lo cita como referencia obligatoria.
- [ ] Ningún framework nuevo, ninguna dependencia nueva. `unittest` cubre todo. Nada de esto vive en
      `cursos/` (D-12 de la Fase 10, vigente).

---

## REQ-48 — las dos rutas de verificación y qué atrapa cada una

| Ruta | Qué cubre | Qué NO cubre |
|---|---|---|
| **Unit test** (`NoContaminacion`, ciclo rápido) | El silencio de R1 sobre 39056/39062/38985 (cero hallazgos) y que su YAML crudo no declare las dos claves nuevas. Corre en cada `discover`, segundos | El texto del `.docx` renderizado — `NoContaminacion` no genera documentos (D-18 de la Fase 9: la generación completa es lenta y depende de las plantillas) |
| **`python src/huella.py verificar`** (manual, D-20) | Los tres hashes por documento —`texto_docx`, `informe`, `manifiesto`— de los cuatro documentos de control. Es la única ruta que ve el `.docx` y la **forma del manifiesto**, así que es la única que atraparía una regresión de D-16 | No corre en cada commit, así que una regresión de R1 puede vivir varios commits antes de verse |

**No se solapan.** El plan de cierre corre **las dos**, en ese orden: suite completa, luego
`huella verificar`.

---

## Verificaciones solo manuales

| Comportamiento | Requisito | Por qué es manual | Instrucciones |
|---|---|---|---|
| `huella verificar` en verde contra los 4 documentos de control | REQ-48 / criterio 4 | D-18 de la Fase 9 lo aparta del ciclo unitario a propósito: genera dos cursos completos y depende de las plantillas de `referencias/` | `python src/huella.py verificar` → los 4 documentos intactos, salida 0. Después `git status --porcelain` vacío (D-23 de la Fase 9) |
| 38985 pasa de **9 a 10 hallazgos**, el nuevo es un aviso de R1 por diferir del catálogo, y sigue siendo válido | D-18 | Es una consecuencia aceptada a propósito, no un defecto. Automatizarla congelaría un número que la Fase 14 va a cambiar | Correr `validar.py` sobre 38985 antes y después de la fase; confirmar 9 → 10, que el hallazgo nuevo es de R1 y de nivel aviso, y que el curso sigue válido. Su huella no se vigila (D-22 de la Fase 9) |

---

## Firma de validación

- [ ] Toda tarea tiene verificación `<automated>` o depende de Ola 0
- [ ] Continuidad de muestreo: no hay 3 tareas seguidas sin verificación automatizada
- [ ] Ola 0 cubre todas las referencias marcadas ❌
- [ ] Ningún comando en modo watch
- [ ] Latencia de retroalimentación < 20 s
- [ ] Cada uno de B1–B15 tiene un plan y una tarea asignados en la columna **Plan / Tarea**
- [ ] `nyquist_compliant: true` en el frontmatter

**Aprobación:** pendiente
