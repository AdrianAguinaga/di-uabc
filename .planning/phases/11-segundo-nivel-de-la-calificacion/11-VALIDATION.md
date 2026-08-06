---
phase: 11
slug: segundo-nivel-de-la-calificacion
status: planned
nyquist_compliant: true
wave_0_complete: false
created: 2026-08-06
planned: 2026-08-06
---

# Fase 11 — Estrategia de validación

> Contrato de validación de la fase: con qué instrumento se muestrea cada comportamiento durante la
> ejecución. Derivado de `11-RESEARCH.md` §Validation Architecture. La columna **Plan / Tarea** la
> rellenó la planeación (2026-08-06): tres planes en tres olas.

---

## Infraestructura de pruebas

| Propiedad | Valor |
|---|---|
| **Framework** | `unittest` (stdlib) — sin runner de terceros |
| **Archivo de config** | ninguno — convención de directorio `pruebas/`, se descubre con `discover` |
| **Comando rápido** | `python -X utf8 -m unittest pruebas.test_validar -v` (o una clase concreta, p. ej. `pruebas.test_validar.Regla1SegundoNivel`) |
| **Comando completo** | `python -X utf8 -m unittest discover -s pruebas` |
| **Tiempo estimado** | ~16.5 s (**245 pruebas**, remedido en la investigación — la cifra de 179 del ROADMAP es la línea base de la v1.0, no la de hoy) |

**Cuenta de pruebas prevista por plan:** 245 al empezar → 251 tras 11-01 (+6) → 259 tras 11-02
(+8) → **262 al cerrar** tras 11-03 (+3, dos en `test_generar.py` y una en `test_validar.py`; la
ampliación de `test_los_cursos_de_control_no_declaran_nada_de_la_v2` no añade método).

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

Los identificadores `B1`–`B15` son los de `11-RESEARCH.md` §Validation Architecture.

| # | Comportamiento | Req / Decisión | Tipo | Nivel de hallazgo | Comando automatizado | ¿Archivo existe? | Plan / Tarea | Estado |
|---|---|---|---|---|---|---|---|---|
| B1 | `segundo_nivel` 60/40 válido → carga y valida sin error nuevo | REQ-41 / criterio 1 / D-01 | unitario | silencio | `python -X utf8 -m unittest pruebas.test_validar.Regla1SegundoNivel -v` | ❌ clase nueva en `test_validar.py` | **11-02 T1** (código) + **T2** (`test_un_segundo_nivel_de_60_40_no_produce_ningun_hallazgo_de_r1`); la carga, en **11-01 T2** | ⬜ pendiente |
| B2 | `segundo_nivel` 60/30 (no suma 100) → error de R1 | REQ-46 / criterio 1 / D-12 | unitario | **error** R1 | idem | ❌ | **11-02 T1** + **T2** (`test_un_segundo_nivel_de_60_30_es_error_de_r1`) | ⬜ pendiente |
| B3 | `segundo_nivel` presente y `exencion_contra` ausente → `ErrorModelo` al cargar | REQ-41 / D-07 | unitario | **error** `ErrorModelo` | `python -X utf8 -m unittest pruebas.test_modelo -v` | ❌ clase nueva en `test_modelo.py` | **11-01 T1** (`Curso.__post_init__`) + **T2** (`ContratoDelSegundoNivel::test_segundo_nivel_sin_exencion_contra_es_error_modelo`) | ⬜ pendiente |
| B4 | `exencion_contra` fuera del vocabulario cerrado → `ErrorModelo` al cargar | REQ-41 / D-06 | unitario | **error** `ErrorModelo` | idem | ❌ | **11-01 T1** (`EXENCION_CONTRA`) + **T2** (`test_exencion_contra_fuera_del_vocabulario_es_error_modelo`, más `test_calificacion_final_carga_aunque_r1_la_rechace` para la frontera de D-08) | ⬜ pendiente |
| B5 | `exencion_contra: calificacion_final` **con** segundo nivel → error de R1 | REQ-46 / criterio 3 / D-08 | unitario | **error** R1 | `python -X utf8 -m unittest pruebas.test_validar.Regla1SegundoNivel -v` | ❌ | **11-02 T1** + **T2** (`test_la_exencion_contra_la_calificacion_final_con_segundo_nivel_es_error`) | ⬜ pendiente |
| B6 | `exencion_contra: calificacion_final` **sin** segundo nivel → aviso de R1 | REQ-46 / D-09 | unitario | **aviso** R1 | idem | ❌ | **11-02 T1** + **T2** (`test_la_exencion_contra_la_calificacion_final_sin_segundo_nivel_es_aviso`) | ⬜ pendiente |
| B7 | Segundo nivel 100/0 → aviso de R1 | D-13 | unitario | **aviso** R1 | idem | ❌ | **11-02 T1** + **T2** (`test_un_segundo_nivel_de_100_0_es_aviso`). **Decidido: dos mensajes distintos**, así que B7 y B8 son dos pruebas, no dos `subTest` | ⬜ pendiente |
| B8 | Segundo nivel 0/100 → aviso de R1 | D-13 | unitario | **aviso** R1 | idem | ❌ | **11-02 T1** + **T2** (`test_un_segundo_nivel_de_0_100_es_aviso`) | ⬜ pendiente |
| B9 | Contraste contra el catálogo: porcentajes y/o etiquetas divergen → aviso de R1 | D-05 / D-14 | unitario | **aviso** R1 | idem | ❌ | **11-01 T3** (el catálogo declara el 60/40 con los rótulos literales) + **11-02 T1** (el contraste, `if` propio dentro del `if self.c.esquema_id:`) + **T2**, con **dos** pruebas: `test_avisa_si_el_segundo_nivel_se_aparta_del_catalogo` y `test_el_segundo_nivel_del_catalogo_no_produce_ningun_aviso` (esta última es la guarda de los rótulos literales) | ⬜ pendiente |
| B10 | Curso sin `segundo_nivel` → cero cambio de comportamiento | REQ-48 / criterio 2 / D-03 | unitario | silencio | `python -X utf8 -m unittest pruebas.test_validar -v` | ✅ `PuntoDePartida` + `NoContaminacion` existentes | **11-01 T2** (`test_un_curso_que_no_lo_declara_lo_deja_en_none` y la ampliación de `LosCursosExistentesNoCambian` con los tres cursos reales) + **11-03 T2** | ⬜ pendiente |
| B11 | El `MANIFIESTO.yaml` registra las dos claves **solo** si el curso las declara | REQ-48 / D-16 | unitario | — (estructural) | `python -X utf8 -m unittest pruebas.test_generar -v` | ⚠ leído en la planeación: **clase nueva** `ManifiestoDelSegundoNivel`, que llama a `generar.manifiesto()` directamente (no a `paquete()`, que renderiza y es caro), y añade `import modelo`/`import validar` al archivo | **11-03 T1**, dos pruebas: sin declararlo, `list(ev) == ["esquema_id", "exencion_ordinario", "rubros"]`; declarándolo, las dos claves con sus etiquetas | ⬜ pendiente |
| B12 | La guarda `getsource` sigue sin ver `.base` / `a_porcentaje` / `.unidad` / `.total` / `.valor` en `regla_1` | D-11 / D-15 | unitario — **estructural** | — | `python -X utf8 -m unittest pruebas.test_validar.Regla1EsInsensibleALaUnidad -v` | ✅ ya existe — **no se toca** | **11-02 T1**: no se modifica, pero es criterio de aceptación explícito de esa tarea, con una comprobación directa además de la prueba (`inspect.getsource` + lista por comprensión que debe imprimir `[]`), porque la guarda es **textual** y un comentario la rompe | ⬜ pendiente |
| B13 | Los cursos de control siguen emitiendo **cero** hallazgos de R1 | REQ-48 / criterio 4 / D-17 | unitario | silencio | idem | ❌ hermana de la de R2/R3 ya existente | **11-03 T2** (`NoContaminacion::test_los_cursos_de_control_no_emiten_un_solo_hallazgo_de_r1`) — **sobre 39056 y 39062 únicamente.** Ver la corrección de abajo | ⬜ pendiente |
| B14 | 39056 / 39062 no declaran `segundo_nivel:` ni `exencion_contra:` en su YAML crudo | REQ-48 / D-17 | unitario — texto crudo | — | idem | ✅ ampliar `test_los_cursos_de_control_no_declaran_nada_de_la_v2` | **11-03 T2**, dos `assertNotIn` más dentro del `subTest` existente | ⬜ pendiente |
| B15 | Cierre REQ-48: huella de texto, informe y manifiesto de 39056 y 39062 intactos | REQ-48 / criterio 4 / D-20 | manual, fuera de la suite | — | `python src/huella.py verificar` | ✅ ya existe | **11-03 T3** | ⬜ pendiente |
| — | Las 245 pruebas anteriores pasan intactas, más las nuevas (262 al cerrar) | criterio 5 heredado | integración | — | `python -X utf8 -m unittest discover -s pruebas` | ✅ ya existe (245/245 en verde) | Verificación de **las nueve tareas**; el conteo final se apunta en **11-03 T3** | ⬜ pendiente |
| — | Ninguna plantilla de `referencias/` fue modificada | invariante del proyecto | integración | — | `python src/plantillas.py verificar` | ✅ ya existe | **11-03 T3** (y en el `<verification>` de los tres planes) | ⬜ pendiente |

### Corrección de B13 hecha en la planeación

B13 se escribió como «39056 / 39062 / **38985** siguen emitiendo cero hallazgos de R1». **Eso es
incompatible con D-18**, que mide y acepta que 38985 —que declara `esquema_id: zra-contabilidad` y
**no** declara segundo nivel— gane un aviso de R1 en cuanto el catálogo declare el suyo, pasando de
9 a 10 hallazgos y siguiendo válido.

Resolución, coherente con §«Verificaciones solo manuales» de este mismo archivo:

- **Automatizado (11-03 T2):** el silencio de R1 se fija sobre **39056 y 39062**, los
  `CURSOS_DE_CONTROL` que D-13 de la Fase 10 delimita y que son los de la huella (D-22 de la Fase 9).
- **Manual (11-03 T3):** el 9 → 10 de 38985 se comprueba a mano y se transcribe en el SUMMARY.
  Automatizar ese 10 congelaría un número que la Fase 14 va a cambiar.

Una prueba escrita con los tres cursos **falla**. Está avisado en el `<context>` del plan 11-03.

---

## Pruebas existentes que NO deben romperse

Las dos primeras son **guardas estructurales frágiles**: pueden dejar de vigilar sin fallar.

| Prueba | Por qué es frágil | Qué la protege |
|---|---|---|
| `test_el_codigo_de_r1_no_menciona_la_unidad_de_ningun_rubro` (`test_validar.py:287-292`) | Si el plan saca la aritmética nueva a un método auxiliar, **deja de cubrir nada en silencio** — no falla, solo deja de vigilar (D-11 lo dice explícitamente). Es además una guarda **textual**: un comentario dentro de `regla_1` que mencione la palabra `a_porcentaje`, aunque sea para explicar por qué no se usa, la rompe | 11-02 T1 escribe todo dentro de `regla_1`, nunca en un helper, no nombra ningún token prohibido ni en comentarios, y usa `suma` como variable en vez de `total` para no tener que pensarlo |
| `test_poner_un_rubro_en_puntos_no_altera_lo_que_r1_comprueba` (`test_validar.py:281-285`) | Compara los mensajes de R1 con y sin rubros en puntos. Si el segundo nivel introdujera algo que lee la unidad de un rubro, esto aparece como cambio de mensajes — hay que leer el diff, no confiar en el verde | El código del segundo nivel no referencia `Rubro.unidad` / `.base` / `.total`: solo `self.c.segundo_nivel` y `self.c.exencion_contra` |
| `test_el_total_correcto_no_absuelve_al_rubro_incorrecto` | Exige el prefijo literal `"El valor de las metas suma"` (D-07 de la Fase 10). Esta fase no toca ese mensaje | R2 está fuera del alcance de esta fase |
| `test_detecta_el_defecto_del_ejemplo_961` | Solo comprueba que aparezcan dos etiquetas — es holgada, no una garantía fuerte | R2 está fuera del alcance de esta fase |

---

## Requisitos de Ola 0

Los tres se cubren dentro de los planes, en la ola en la que vive el código que fijan:

- [ ] **Ampliación de `pruebas/test_validar.py`** — clase `Regla1SegundoNivel` con ocho pruebas
      (B1–B9) en **11-02 T2**; la prueba de silencio de R1 (B13) y la ampliación de
      `test_los_cursos_de_control_no_declaran_nada_de_la_v2` (B14) dentro de la clase
      `NoContaminacion` existente (`:691-724`) en **11-03 T2**. Los fixtures se construyen con los
      helpers `curso(**cambios)` / `informe(**cambios)` que ya existen —hoy en **`:110-118`**, no
      `:104-112` como decía el CONTEXT.md— por `deepcopy` de `CURSO_VALIDO` (D-19).
- [ ] **Ampliación de `pruebas/test_modelo.py`** — clase `ContratoDelSegundoNivel` con seis pruebas
      (B3, B4, B10) en **11-01 T2**, más las dos afirmaciones nuevas dentro de
      `LosCursosExistentesNoCambian`. Molde: `RubroEnPuntos` y `ComponentesDeMeta`, ya en ese
      archivo con el mismo estilo de fixture por `deepcopy`.
- [ ] **`pruebas/test_generar.py`** — **abierto y leído en la planeación.** Veredicto: el manifiesto
      condicional necesita **clase nueva** (`ManifiestoDelSegundoNivel`), porque ninguna de las
      cuatro existentes encaja: `PaqueteDeBigData` renderiza dos `.docx` en `setUpClass` y es cara,
      `UnCursoInvalidoNoProduceNada` y `UnGrupoSuelto` prueban la cadena completa y `Panel` es la
      caja ASCII. La clase nueva llama a `generar.manifiesto()` directamente —firma
      `(curso, ruta_curso, informe, archivos, cfg, cal)`, con `archivos=[]`— y **no renderiza
      nada**. Hay que añadir `import modelo` y `import validar` al archivo, que hoy no los tiene.
      Va en **11-03 T1**.
- [ ] Ningún framework nuevo, ninguna dependencia nueva. `unittest` cubre todo. Nada de esto vive en
      `cursos/` (D-12 de la Fase 10, vigente): los fixtures son diccionarios y, cuando hace falta un
      archivo, se vuelca a `mkdtemp`.

---

## REQ-48 — las dos rutas de verificación y qué atrapa cada una

| Ruta | Qué cubre | Qué NO cubre |
|---|---|---|
| **Unit test** (`NoContaminacion`, ciclo rápido) | El silencio de R1 sobre 39056/39062 (cero hallazgos) y que su YAML crudo no declare las dos claves nuevas. Corre en cada `discover`, segundos | El texto del `.docx` renderizado — `NoContaminacion` no genera documentos (D-18 de la Fase 9: la generación completa es lenta y depende de las plantillas) |
| **`python src/huella.py verificar`** (manual, D-20) | Los tres hashes por documento —`texto_docx`, `informe`, `manifiesto`— de los cuatro documentos de control. Es la única ruta que ve el `.docx` y la **forma del manifiesto**, así que es la única que atraparía una regresión de D-16 | No corre en cada commit, así que una regresión de R1 puede vivir varios commits antes de verse |

**No se solapan.** El plan de cierre (11-03 T3) corre **las dos**, en ese orden: suite completa,
luego `huella verificar`. Y después `plantillas verificar`, por el invariante 4 del proyecto.

---

## Verificaciones solo manuales

| Comportamiento | Requisito | Por qué es manual | Instrucciones | Plan / Tarea |
|---|---|---|---|---|
| `huella verificar` en verde contra los 4 documentos de control | REQ-48 / criterio 4 | D-18 de la Fase 9 lo aparta del ciclo unitario a propósito: genera dos cursos completos y depende de las plantillas de `referencias/` | `python src/huella.py verificar` → los 4 documentos intactos, salida 0. Después `git status --porcelain` vacío (D-23 de la Fase 9) | **11-03 T3** |
| 38985 pasa de **9 a 10 hallazgos**, el nuevo es un aviso de R1 por diferir del catálogo, y sigue siendo válido | D-18 | Es una consecuencia aceptada a propósito, no un defecto. Automatizarla congelaría un número que la Fase 14 va a cambiar | Correr `validar.py` sobre 38985 antes y después de la fase; confirmar 9 → 10, que el hallazgo nuevo es de R1 y de nivel aviso, y que el curso sigue siendo válido. Su huella no se vigila (D-22 de la Fase 9) | **11-01 T3** deja escrito que sigue en 9; **11-02 T1** lo lleva a 10; **11-03 T3** lo transcribe |
| `grafo/` conserva su forma | REQ-48 / criterio 4 | D-21, medido: `src/grafo.py` no abre el bloque `evaluacion:`. Se comprueba **sin regenerar**, porque regenerar reescribiría archivos que esta fase no tiene por qué tocar | `grep -c "segundo_nivel\|exencion" src/grafo.py` → 0, y `git status --porcelain grafo/` vacío | **11-03 T3** |

---

## Firma de validación

- [x] Toda tarea tiene verificación `<automated>` (las nueve; la manual de cierre usa
      `python -X utf8 src/huella.py verificar`, que es un comando con código de salida)
- [x] Continuidad de muestreo: no hay 3 tareas seguidas sin verificación automatizada — las nueve
      corren la suite completa o `huella verificar`
- [x] Ola 0 cubre todas las referencias marcadas ❌, y la ⚠ de `test_generar.py` quedó resuelta
      leyendo el archivo durante la planeación
- [x] Ningún comando en modo watch
- [x] Latencia de retroalimentación < 20 s (suite completa: 16.5 s)
- [x] Cada uno de B1–B15 tiene un plan y una tarea asignados en la columna **Plan / Tarea**
- [x] `nyquist_compliant: true` en el frontmatter

**Aprobación:** planeada 2026-08-06 — tres planes, tres olas (11-01 modelo y catálogo, 11-02 R1,
11-03 cierre).
