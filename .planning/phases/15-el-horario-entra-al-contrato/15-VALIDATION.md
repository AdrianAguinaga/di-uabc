---
phase: 15
slug: el-horario-entra-al-contrato
status: complete
nyquist_compliant: true
wave_0_complete: true
created: 2026-08-06
---

# Fase 15 — Estrategia de validación

> Contrato de validación de la fase: con qué señal observable se comprueba cada criterio, y cada
> cuánto se muestrea durante la ejecución.
>
> Derivado de `15-RESEARCH.md` §`## Validation Architecture` (todo verificado contra el código real)
> y de las decisiones `D-01`…`D-16` de `15-CONTEXT.md`.

---

## Infraestructura de pruebas

| Propiedad | Valor |
|----------|-------|
| **Framework** | `unittest` (stdlib) — no hay pytest ni configuración |
| **Archivo de config** | ninguno — sin `pytest.ini` ni `conftest.py`; cada archivo de prueba hace su propio `sys.path.insert` |
| **Comando rápido** | `python -X utf8 -m unittest discover -s pruebas` |
| **Comando de suite completa** | el mismo — 283 pruebas hoy, corre en segundos |
| **Runtime estimado** | ~10 s |
| **Convención de fixtures** | `CURSO_VALIDO` + helpers `curso(**cambios)` / `informe(**cambios)` en `pruebas/test_validar.py:32-118`; `test_modelo.py` los reusa con `from test_validar import CURSO_VALIDO, _meta` |
| **Instrumento de huella** (fuera del ciclo rápido, a mano) | `python src/huella.py verificar` · `python src/huella.py registrar` |

---

## Frecuencia de muestreo

- **Después de cada commit de tarea:** `python -X utf8 -m unittest discover -s pruebas`
- **Después de cada ola:** el mismo comando + `python src/huella.py verificar`
- **Antes de `/gsd-verify-work`:** suite completa en verde y `python src/plantillas.py verificar` en verde
- **Latencia máxima de retroalimentación:** ~10 s

**Excepción declarada, y es el eje de la fase:** `huella verificar` deja de dar 4/4 intacto en cuanto
se editan los `curso.yaml` de control. A partir de ese punto la señal deja de ser «4/4 intacto» y pasa
a ser **«el diff coincide con el informe de medición de D-11, escrito antes»**. Ver §«Secuencia de
huella» abajo.

---

## Mapa de criterios → verificación

Los IDs de tarea los asigna el planeador; esta tabla fija **qué** hay que poder observar.

| # criterio (roadmap) | Comportamiento | Requisito | Tipo | Comando / patrón concreto | ¿Existe hoy? |
|---|---|---|---|---|---|
| 1 | Un curso que solo declara `dias_presencial` sigue cargando sin `ErrorModelo` y con `bloques == []` | REQ-50 | unit | Extender `LosCursosDeControlNoCambian` (`pruebas/test_modelo.py:485-505`); afirmarlo siempre sobre `531` y `38985`, que nunca declaran bloques | ❌ nueva |
| 1 | Un curso con `bloques:` deriva el mismo `dias_presencial` que si se escribiera a mano | REQ-50 | unit | `Horario(bloques=[…4 bloques reales de 961…]).dias_presencial == [0, 1, 2]` — ordenado y sin duplicar el martes | ❌ nueva |
| 2 | Un grupo con 2 bloques presenciales + 1 virtual produce **las mismas fechas** que sin el virtual | REQ-51 | unit (par de fixtures) | Dos `Grupo` con el mismo `Horario.bloques` salvo el bloque virtual; `resolver_fechas` sobre **copias independientes** del curso (`copy.deepcopy` — muta `Sesion.fecha` in-place y las sesiones son compartidas, `modelo.py:523`); comparar las fechas presenciales | ❌ nueva |
| 3 | Hora mal formada es error | REQ-50 | unit | Fixture con `inicio: "25:99"`; `reglas_con_error(informe(...))` incluye la regla | ❌ nueva |
| 3 | `fin` anterior a `inicio` es error | REQ-50 | unit | Fixture con `inicio: "13:00", fin: "12:00"` | ❌ nueva |
| 3 (D-05) | Bloques solapados el mismo día son error; los dos martes de 961 (12–13 y 16–17) **no** lo son | REQ-50 | unit — caso feliz real + caso roto a propósito | Feliz: los 4 bloques reales de 961 no disparan nada. Roto: `{dia:1, inicio:"12:30", fin:"13:30"}` contra `{dia:1, inicio:"12:00", fin:"13:00"}` | ❌ nueva |
| — (D-07) | La suspensión recorre al siguiente día **con bloque presencial** dentro de la semana | REQ-50 | unit, calendario real (`cargar("2026-2")`, determinista) | 961 sem. 13 → **3 nov**; 961 sem. 15 → **17 nov** | ❌ nueva |
| — (D-15) | Sin día presencial en la semana, el recorrido **no cruza de semana** | REQ-50 | unit | 971 sem. 13 y 15, y 972 sem. 6: la fecha **no** es 9 nov / 23 nov / 23 sep. Es la prueba que fija el límite | ❌ nueva |
| — (D-15) | `validar.py` reporta la semana sin día presencial | REQ-50 | unit | Hallazgo del tipo «semana N: el grupo G no tiene ningún día con bloque presencial (D suspendido)» para los tres casos de 39062. **Computado con horario + calendario, sin resolver sesiones** — ver trampa 1 | ❌ nueva |
| — (D-07) | Un grupo **sin** bloques conserva el comportamiento de hoy, intacto | REQ-50 | unit | Protege al 531 de Contabilidad y a cualquier curso futuro sin horario declarado | ❌ nueva |
| 5 (D-09/D-12) | `imparte: false` saca al grupo de la generación por defecto; pedirlo explícitamente lo devuelve | REQ-52 | unit | `generar.paquete(ruta)` no produce archivo para el grupo; `generar.paquete(ruta, grupos=["X"])` sí — el mismo trato que `huella.py` da hoy al 962 | ❌ nueva |
| 4 (D-10) | El `.docx` de 962 sale byte por byte igual | REQ-52 | huella | `huella verificar` reporta `texto_docx` **e** `informe` iguales para `39056:962`. Su `manifiesto` **sí** cambia — D-16, esperado | instrumento existe |
| 4 (D-11/D-14) | El cambio de fechas se mide **antes** de aceptarse | REQ-52 | manual + artefacto de fase | Informe `.md` en el directorio de la fase, campo por campo; ver §«Secuencia de huella» | ❌ nuevo artefacto |
| 6 | La suite completa pasa | todos | automatizado | `python -X utf8 -m unittest discover -s pruebas` — 283 anteriores intactas + las nuevas | comando existe |
| cierre | Las plantillas siguen sin tocarse | invariante del proyecto | automatizado | `python src/plantillas.py verificar` | comando existe |

---

## Secuencia de huella (D-11 / D-14 / D-16)

El orden importa: es lo que hace defendible el cambio. Precedente en la Fase 9 (D-14/D-15/D-24).

1. `python src/huella.py verificar` → **4/4 intacto**. Confirma la línea base; no hay que crearla, la
   v2.0 la dejó registrada y verificada.
2. Se construye el contrato (D-01…D-05, D-07, D-15) **sin tocar ningún `curso.yaml` real**.
3. `unittest discover` en verde **y** `huella verificar` **sigue en 4/4**. Es la prueba de que el
   rasgo es aditivo — si aquí se movió algo, se rompió el criterio 1 y hay que parar.
4. Se editan los `curso.yaml` de 961, 971, 972 y se marca `imparte: false` en 962.
5. **Se escribe el informe de medición (D-11)** — antes de correr nada más.
6. `python src/grafo.py` (el grafo sigue al `curso.yaml`, precedente D-24).
7. `python src/huella.py verificar` → reporta `!`. **Serán cuatro líneas, no tres** (D-16: el
   `manifiesto` de 962 se mueve por acoplamiento de archivo). Se leen contra el informe ya escrito.
8. `git diff cursos/` confirma que el diff es el que el informe predijo.
9. `python src/huella.py registrar` — acepta el cambio.
10. Commit propio (D-14) cuyo mensaje dice que el cambio es deliberado y **distingue los tres campos
    movidos a propósito del cuarto movido por acoplamiento**.

---

## Requisitos de la ola 0

- [ ] Ninguno de infraestructura — `unittest` ya está, los helpers de fixtures ya existen en
      `pruebas/test_validar.py:32-118` y `test_modelo.py` ya los importa.
- [ ] Sí hace falta **medir la línea base primero**: el paso 1 de la secuencia de arriba es
      precondición de todo lo demás y no depende de ningún código nuevo.

*La infraestructura existente cubre todos los requisitos de la fase.*

---

## Trampas que invalidan una verificación (medidas en el RESEARCH)

1. **`validar.py` nunca ve fechas resueltas en el pipeline real.** `generar.paquete()` valida en
   `generar.py:293`, *antes* de que `render_docx.generar()` llame a `resolver_fechas`
   (`render_docx.py:689`). Cualquier prueba de que D-07 calculó bien una fecha tiene que atacar la
   resolución de fechas **directamente**, nunca la salida de `validar.py`. El hallazgo de D-15 se
   libra de esto solo porque se computa con horario + calendario y no necesita sesiones resueltas —
   si quien implemente lo escribe leyendo `Sesion.fecha`, **deja de dispararse en el pipeline real** y
   la prueba unitaria seguiría pasando. Es la trampa más cara de la fase.
2. **`resolver_fechas` muta `Sesion.fecha` in-place y las sesiones son compartidas entre los grupos
   del curso** (`modelo.py:523`). Una prueba de equivalencia que no use `copy.deepcopy` compara un
   objeto consigo mismo y pasa siempre.
3. **`MANIFIESTO.yaml` es por curso, no por grupo.** Un hash `manifiesto` intacto para 962 no es un
   criterio de aceptación válido — D-16 ya lo descartó.

---

## Verificaciones solo manuales

| Comportamiento | Requisito | Por qué manual | Instrucciones |
|----------|-------------|------------|-------------------|
| El informe de medición predice el cambio real | REQ-52 | Es un juicio sobre un documento en prosa, no una aserción | Leer el informe de D-11 contra la salida de `huella verificar` del paso 7 y el `git diff` del paso 8: cada fecha que cambió tiene que estar en el informe, y cada fecha del informe tiene que haber cambiado |
| El mensaje del commit de re-registro dice qué cambió y por qué | REQ-52 | Criterio 4 del roadmap, redacción | Revisar antes de `git push`; tiene que distinguir los tres cambios deliberados del cuarto acoplado (D-16) |
| `AGENTS.md` §«Contrato de `curso.yaml`» lista `bloques:` e `imparte:` | REQ-50, REQ-52 | Documentación | Además cierra la deuda de la Fase 9 (`componentes:`, `unidad`/`total`) o declara por qué no |

---

## Firma de validación

- [x] Toda tarea tiene verificación `<automated>` o dependencia declarada de la ola 0
- [x] Continuidad de muestreo: no hay 3 tareas seguidas sin verificación automatizada
- [x] Ninguna prueba de D-07/D-15 depende de la salida de `validar.py` para una fecha resuelta (trampa 1)
- [x] Ninguna prueba de equivalencia comparte objetos `Sesion` entre las dos ramas (trampa 2)
- [x] Sin flags de watch-mode
- [x] Latencia de retroalimentación < 15 s
- [x] `nyquist_compliant: true` en el frontmatter

**Aprobación:** completada el 2026-08-06; el re-registro de huella se ejecutó tras la aprobación explícita del usuario.
