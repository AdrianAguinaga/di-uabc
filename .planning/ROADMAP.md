# Roadmap: Generador de Diseño Instruccional UABC

## Panorama — v2.0 Estructura de calificación variable

La v1.0 dejó un generador que produce el DI de Adrian de extremo a extremo. Este milestone hace
que produzca también el de **otra docente**, cuya aritmética de la nota no se parece a la suya:
las metas valen puntos, los exámenes viven dentro de la actividad de otra meta, y todo el promedio
del curso vale a su vez el 60 % de la calificación final.

El orden es el mismo que en la v1.0 y por la misma razón: **modelo → validación → renderizado →
ejercicio real**. `curso.yaml` es el contrato; si al llegar al renderizado hiciera falta *decidir*
algo —si estos 10 son puntos o por cientos, si este examen cuenta o no—, es que faltó un campo en
el modelo. Por eso el contrato se abre primero (Fase 9), las reglas se reescriben contra un
contrato ya estable (Fase 10), y el documento se toca al final (Fase 13), cuando ya no queda nada
que inferir.

Dos rasgos —el segundo nivel y la rúbrica— son **aditivos**: no tocan la aritmética existente y su
regla es nueva, así que cada uno entra entero, modelo y regla en la misma fase (11 y 12). Los otros
tres —puntos, componentes, identificadores libres— sí muerden R1, R2 y R3, que ya están escritas y
tienen pruebas; por eso ahí sí se separa el contrato de las reglas.

**El criterio de cierre de todas las fases es el mismo (REQ-48): la no contaminación.** Ningún
rasgo se enciende si el `curso.yaml` no lo declara. Regenerar Big Data (39056) y Patrones (39062)
al terminar cada fase debe dejar su **huella de texto idéntica**, y ni `grafo/` ni
`MANIFIESTO.yaml` deben cambiar de forma. Si cambia un carácter de un documento de Adrian, la fase
está mal aunque las pruebas pasen. Es la misma prueba que se aplicó al registrar los criterios
propios de cada docente, y el instrumento para correrla se construye en la Fase 9 para que las
cinco siguientes lo hereden.

Las 179 pruebas actuales pasan al final de cada fase. Ninguna se rompe; se añaden.

El punto de mayor riesgo es la Fase 13: la tabla de rúbrica es un elemento que **la plantilla CIAD
no trae**. Hay que decidir de qué prototipo del propio documento se clona, porque el renderizado
clona y no construye — y elegir mal el molde no da error, da un documento con el formato torcido.
Todo lo anterior existe para que al llegar ahí los datos ya estén completos y validados.

## Fases

- [x] **Fase 9: El valor de una meta deja de ser un porcentaje** — puntos, componentes e identificadores libres en el contrato *(hecha el 2026-08-05)*
- [x] **Fase 10: Las reglas cuentan en la unidad declarada** — R2 en puntos, R3 con exámenes dentro de la actividad *(hecha el 2026-08-06)*
- [x] **Fase 11: El segundo nivel de la calificación** — promedio 60 % + ordinario 40 %, y la exención contra el promedio *(hecha el 2026-08-06)*
- [x] **Fase 12: La rúbrica en el contrato** — filas, puntos y total declarados, con su regla *(hecha el 2026-08-06)*
- [x] **Fase 13: El documento en la unidad real** — puntos, componentes, dos niveles y la tabla de rúbrica *(hecha el 2026-08-06)*
- [x] **Fase 14: 38985 sin traducirse** — la prueba de fuego del milestone *(hecha el 2026-08-06)*

**Deuda de proceso de las fases 11 a 14.** Se ejecutaron en una sesión con otro agente y su registro
quedó incompleto: un commit aplastado por fase en vez de commits atómicos por tarea, sin
`VERIFICATION.md` en ninguna de las cuatro, sin `SUMMARY.md` de `11-01` ni `11-02`, y la Fase 13 sin
un solo artefacto de planeación. El **código está verificado** —283 pruebas en verde, las cuatro
huellas de control intactas, plantillas íntegras— pero el rastro documental no cumple el estándar de
las fases 9 y 10. Se anota aquí porque no se puede reconstruir a posteriori sin inventar.

## Detalle

### Fase 9: El valor de una meta deja de ser un porcentaje
**Meta**: que `curso.yaml` pueda decir en qué unidad vale cada meta, a qué rubros aporta y cómo se
llama, sin que nada de eso cambie el significado de un curso que no lo declare.
**Depende de**: nada nuevo — parte del modelo de la Fase 5.
**Requisitos**: REQ-38, REQ-39, REQ-42
**Criterios de éxito**:
1. Un `curso.yaml` que declare «Actividades 30 %» con sus valores **en puntos** y total `150`,
   junto a «Exámenes 50 %» en porcentaje, carga sin `ErrorModelo`. Lo que se reporte después son
   hallazgos de reglas, no un esquema rechazado.
2. Una meta que declare un componente adicional —rubro, valor, etiqueta, tipo— sigue siendo **una
   sola meta con una sola semana**: ni `len(curso.metas)` ni sus semanas cambian respecto a la
   misma meta sin componente.
3. Metas con id `1.0`, `2.0` y `6.0` cargan y conservan el orden en que se declararon. Renombrar
   el encuadre `0` de Big Data a `1.0` deja el documento igual salvo esa cadena: ninguna función
   de `src/` deduce el encuadre por su id ni supone que la primera meta de una unidad termina
   en `.1`.
4. Existe un comando que regenera 39056 y 39062 y compara su huella de texto contra la registrada,
   y corre en verde. Es el instrumento de REQ-48 para las cinco fases siguientes.
5. `python -X utf8 -m unittest discover -s pruebas` pasa: las 179 anteriores intactas más las
   nuevas.
**Planes**: 6 planes en 5 olas. El orden de las olas no es negociable: lo fija D-15/D-24 del
contexto de la fase — la línea base de la huella se registra antes de tocar el modelo y el
renombrado del encuadre va al final.
- [x] 09-01-PLAN.md — `src/huella.py` y la línea base de las cuatro huellas de control (paso 1)
- [x] 09-02-PLAN.md — el contrato: rubro en puntos, componentes de meta, ids libres
- [x] 09-03-PLAN.md — R2 detecta metas con id duplicado
- [x] 09-04-PLAN.md — la evidencia del componente llega a la Sección 2
- [x] 09-05-PLAN.md — verificar, renombrar el encuadre a 1.0, grafo, medir y aceptar (pasos 3 a 7)
- [x] 09-06-PLAN.md — cierre: Word, revisión del diff y la decisión sobre el MANIFIESTO

### Fase 10: Las reglas cuentan en la unidad declarada
**Meta**: que R2 y R3 sigan atrapando lo que atrapaban, y además atrapen el defecto real del 531.
**Depende de**: Fase 9.
**Requisitos**: REQ-40, REQ-45
**Criterios de éxito**:
1. `python src/validar.py` sobre un curso cuyo rubro en puntos declara **150** y cuyas metas suman
   **140** reporta un error de R2 redactado en puntos, no en por cientos. Es el defecto verificado
   del DI de Contabilidad, hermano del que ya se atrapa en el 961.
2. Corregido el total a 140 pts, ese mismo curso pasa R2 aunque el rubro vecino esté en porcentaje:
   R2 compara dentro de cada rubro y **nunca suma unidades distintas entre sí**.
3. `test_detecta_el_defecto_del_ejemplo_961` sigue pasando **sin tocarse**. El defecto en
   porcentajes se sigue denunciando; la regla se amplió, no se reescribió.
4. R3 cuenta los exámenes que viven como componente de la actividad de otra meta: un curso con tres
   componentes `examen_parcial` y **ninguna** meta de ese tipo pasa R3, y con uno solo falla con el
   mensaje del Art. 68. Hay una prueba que lo hace fallar a propósito.
5. Cierre (REQ-48): 39056 y 39062 conservan su huella de texto y sus informes de validación no
   cambian ni un hallazgo.
**Planes**: 4 planes en 4 olas. El enunciado que gobierna la fase es «toda regla lee todo aporte a
un rubro, en la unidad que ese rubro declara»; el alcance se ensanchó respecto a estos criterios y
está razonado en `10-CONTEXT.md`.
- [x] 10-01-PLAN.md — el accesor único de aportes en el modelo (`Aporte` + `Curso.aportes()`)
- [x] 10-02-PLAN.md — R2 cuenta todo aporte, en la unidad de su rubro, y denuncia el componente mal declarado
- [x] 10-03-PLAN.md — R3 cuenta los exámenes parciales se declaren donde se declaren
- [x] 10-04-PLAN.md — cierre: auditoría de R1, no contaminación en el ciclo rápido y huella a mano

### Fase 11: El segundo nivel de la calificación
**Meta**: que un curso pueda declarar que todo lo anterior vale el 60 % y el examen ordinario el
40 %, y que la exención se entienda contra el promedio y no contra la nota final.
**Depende de**: Fase 9 (contrato estable). No depende de la Fase 10: es aritmética nueva sobre
reglas nuevas.
**Requisitos**: REQ-41, REQ-46
**Criterios de éxito**:
1. Un curso que declare promedio 60 % + ordinario 40 % valida; con 60 y 30, R1 reporta error
   diciendo que el segundo nivel no suma 100.
2. Un curso que **no** declara segundo nivel se comporta exactamente como hoy —el promedio *es* la
   calificación—: 39056 y 39062 producen el mismo informe y el mismo documento, carácter por
   carácter.
3. Un `curso.yaml` con segundo nivel que declare la exención contra la **calificación final** es
   rechazado por R1, con un mensaje que explica la diferencia. La exención de 90 de `zra` se lee
   contra el promedio del curso, que es lo que dice su DI.
4. Cierre (REQ-48): huella de 39056 y 39062 sin cambios; `grafo/` y `MANIFIESTO.yaml` conservan su
   forma.
**Planes**: 3 planes en 3 olas. El enunciado que gobierna la fase es «la calificación puede tener
dos niveles, y el umbral de exención dice contra cuál se mide»; es un rasgo **aditivo** que entra
entero —modelo y regla— y cuelga de un solo `if` (`Curso.segundo_nivel is None`), razonado en
`11-CONTEXT.md`.
- [x] 11-01-PLAN.md — el contrato aprende a decir «dos niveles»: `Nivel`/`SegundoNivel`,
      `exencion_contra` con vocabulario cerrado, el catálogo de `zra-contabilidad` y §Contrato
      *(sin `SUMMARY.md` — ver la deuda de proceso arriba)*
- [x] 11-02-PLAN.md — R1 comprueba la suma de los dos niveles y contra qué se mide la exención, sin
      sacar un cálculo a un método auxiliar *(sin `SUMMARY.md`)*
- [x] 11-03-PLAN.md — cierre: el `MANIFIESTO.yaml` condicional, la no contaminación de R1 en el
      ciclo rápido y la huella a mano

### Fase 12: La rúbrica en el contrato
**Meta**: que la rúbrica del trabajo final se pueda **declarar** y verificar, sin que el generador
redacte un solo criterio.
**Depende de**: Fase 9 solo por orden de trabajo; toca claves nuevas del contrato, no las que
cambiaron antes.
**Requisitos**: REQ-43, REQ-47
**Criterios de éxito**:
1. `curso.yaml` declara una rúbrica —concepto, puntos y descripción por fila, con su total— asociada
   a una meta o al trabajo final del curso, y el modelo la carga.
2. `python src/validar.py` reporta error cuando las filas suman 98 o 102 contra un total declarado
   de 100. Hay una prueba que lo hace fallar a propósito.
3. Los textos de la rúbrica salen tal cual del `curso.yaml`: no hay ninguna ruta del código que
   componga, complete o reformule una descripción (sigue vigente REQ-26).
4. Cierre (REQ-48): un curso sin `rubrica:` no cambia en nada; 39056 y 39062 conservan su huella.
**Planes**: 3 planes en 3 olas.
- [x] 12-01-PLAN.md — `Rubrica`/`FilaRubrica` en el modelo y su carga
- [x] 12-02-PLAN.md — la regla: las filas suman el total declarado
- [x] 12-03-PLAN.md — cierre: manifiesto, no contaminación y huella

### Fase 13: El documento en la unidad real
**Meta**: que lo que el alumno lee diga lo que el `curso.yaml` declara — puntos donde hay puntos,
los dos niveles de la nota, y la rúbrica como tabla.
**Depende de**: Fases 10, 11 y 12.
**Requisitos**: REQ-44
**Criterios de éxito**:
1. El `.docx` abre en Word y la columna Valor de una meta en puntos dice «10 pts»; las metas de un
   rubro en porcentaje siguen diciendo «%», en el mismo documento.
2. La Sección 3 de una meta con componente imprime las dos cosas: su valor en la unidad de su
   rubro y el componente con su etiqueta y su valor —«Examen I, 15 %»— sin partir la meta en dos.
3. «Criterios de evaluación del curso» imprime los dos niveles: los rubros que suman 100 y, debajo,
   promedio 60 % + examen ordinario 40 % = 100 %.
4. La tabla de rúbrica aparece con sus filas y su renglón de total, con los bordes y la tipografía
   de las demás tablas del documento, clonada de un prototipo del propio documento y no construida
   desde cero. Word la abre sin pedir reparar el archivo.
5. `python src/plantillas.py verificar` pasa después de generar, y cierre (REQ-48): la huella de
   39056 y 39062 no cambia ni un carácter.
**Planes**: ninguno — la fase se ejecutó **sin artefactos de planeación**. No hay `13-CONTEXT.md`,
ni plan, ni resumen; solo el commit `f5068f2`. El criterio 4 —el más riesgoso del milestone— sí se
cumplió como se pedía: `_tabla_rubrica()` clona la tabla de la propia plantilla CIAD con `deepcopy`
y le vacía las filas, en vez de construirla desde cero.

### Fase 14: 38985 sin traducirse
**Meta**: la prueba de fuego. El curso de Zurisaddai, con su estructura real, validado y generado
sin haber tenido que reescribir su forma de calificar.
**Depende de**: Fase 13.
**Requisitos**: REQ-49
**Criterios de éxito**:
1. `cursos/2026-2/38985-contabilidad-financiera/curso.yaml` declara la estructura de su DI de
   origen: «Actividades 30 %» en puntos, «Exámenes 50 %» y «Trabajo final 20 %» en porcentaje,
   segundo nivel 60/40, metas `1.0`…`6.1`, los tres exámenes como componentes de las metas 2.4, 3.3
   y 6.0, y la rúbrica de 100 puntos del trabajo final.
2. `python src/validar.py` sobre ese archivo reporta **el defecto de origen y no otra cosa**: el
   rubro de actividades declara 150 pts y sus metas suman 140. Ni se reproduce en silencio ni se
   disimula repartiendo los puntos.
3. Resuelto el defecto por decisión documentada —declarar 140 o añadir la meta que falta—,
   `python src/generar.py` produce el `.docx` y el `.pdf` del grupo 531 con su `MANIFIESTO.yaml`.
4. Los `avisos:` de ese `curso.yaml` ya no mencionan ninguna traducción: quedan solo el ciclo
   2026-2 —porque su calendario 2026-1 ya pasó— y las metas redactadas por el agente, pendientes de
   revisión de la docente.
5. Cierre (REQ-48): 39056 y 39062 regenerados conservan su huella de texto, y la suite completa
   —283 pruebas al cerrar el milestone— pasa.
**Planes**: ninguno — la fase se ejecutó sin artefactos de planeación, igual que la 13.

**Desviación documentada del criterio 4.** Ese criterio enumera **dos** avisos, y el `curso.yaml`
conserva **tres**: se mantiene «El PUA 38985 no está ingerido». No es un aviso de traducción —la
categoría que el criterio quería eliminar— sino un hecho vigente y comprobable: `pua_ref` está
vacío, 38985 no figura en `puas/INDICE.md` y no hay PDF en `puas/fuente/`. Se quitó durante la
ejecución y se **restauró** después: un DI que no dice que le faltan los temas de sus unidades
oculta una limitación real al lector. El criterio se lee cumplido en su intención, no en su
enumeración literal.

**Corrección posterior a la ejecución.** El renderizador había ganado una función `_sin_ordinal()`
que le quitaba el prefijo «Primero. » al texto de los pasos, porque los 59 pasos del `curso.yaml`
traían el ordinal dentro de la cadena y el renderizador lo prepende por posición. Se arregló en los
**datos** y se retiró la función: REQ-26 dice que el renderizador imprime, no redacta, y esa función
habría borrado en silencio un ordinal legítimo de cualquier curso futuro. Los 59 prefijos coincidían
exactamente con la posición que el renderizador calcula, así que el documento no cambió de texto.

---

## Panorama — v2.1 El horario real del semestre

La v2.0 dejó un generador que expresa **cómo se califica** cualquiera de las dos docentes. Este
milestone atiende algo que ha estado falso desde el principio y que nadie había mirado: **los días y
las horas de clase**. Los cuatro grupos del repositorio declaran `dias_presencial` de relleno —dos
dicen martes, dos dicen jueves— y ninguno coincide con la carga académica real. Las fechas de todos
los documentos generados hasta hoy están calculadas sobre ese relleno.

El enunciado que gobierna el milestone:

> **El horario del semestre es un dato del semestre, no del curso.** Qué materias se imparten, en
> qué grupos, en qué días y cuáles de esas sesiones son virtuales cambia cada ciclo, y el documento
> y la agenda tienen que salir de ahí.

Dos consecuencias que ordenan el trabajo. La primera: `Horario` **no guarda horas de clase**, solo
`hora_entrega`. Sin horas no hay agenda posible, así que el contrato se abre antes de exportar nada
—el mismo orden que la v2.0: modelo → validación → salida—. La segunda: **corregir los días cambia
las fechas de 39056 y 39062, y con ellas su huella registrada.** REQ-48 sigue vigente para todo lo
demás, pero aquí el cambio de huella es el objetivo, no el defecto: la Fase 15 lo mide, lo acepta y
lo re-registra explícitamente, como la Fase 9 hizo con el renombrado del encuadre. Es la única
excepción del milestone y está acotada a esos dos cursos.

La transcripción del horario 2026-2 ya existe en `horarios/2026-2.md`, con los salones marcados como
pendientes de confirmar. Es documentación, no una fuente que el código cargue: `curso.yaml` sigue
siendo el contrato.

## Fases

- [x] **Fase 15: El horario entra al contrato** — días y horas de clase por grupo, sesiones virtuales distinguidas, y la huella de control re-registrada a propósito
- [ ] **Fase 16: Mis clases en Google Calendar** — un `.ics` con las clases del semestre, sobre el calendario escolar

## Detalle

### Fase 15: El horario entra al contrato
**Meta**: que un grupo pueda declarar **a qué hora** tiene clase cada día y cuáles de esas sesiones
son virtuales, y que los cuatro grupos del repositorio digan por fin la verdad sobre sus días.
**Depende de**: nada nuevo — parte del modelo de la v2.0.
**Requisitos**: REQ-50, REQ-51, REQ-52
**Criterios de éxito**:
1. `Horario` acepta **horas de clase por día** —no solo `dias_presencial`— y distingue las sesiones
   **presenciales** de las **virtuales**. Un grupo que solo declare `dias_presencial`, como los hay
   hoy, sigue cargando sin `ErrorModelo`: el rasgo es aditivo.
2. Una sesión declarada virtual **no cuenta como sesión de clase** para las fechas del documento;
   cuenta como bloque de tareas y asignaciones. Un grupo con dos bloques presenciales y uno virtual
   produce las mismas fechas de clase que el mismo grupo sin el bloque virtual.
3. `python src/validar.py` reporta error cuando una hora de clase está mal formada, cuando el fin es
   anterior al inicio, y cuando dos bloques del mismo día se solapan. Hay una prueba que lo hace
   fallar a propósito. El tercer error se enunciaba como «un día declarado con hora no está en
   `dias_presencial`»; **D-05 lo reemplazó por el solapamiento** porque D-01 volvió imposible el
   primero: con bloques, `dias_presencial` se deriva de ellos y no hay dos listas que discrepen.
4. Los cuatro grupos —39056·961, 39056·962, 39062·971, 39062·972— declaran los días y horas de
   `horarios/2026-2.md`. El cambio de fechas resultante se **mide antes de aceptarse**: se lista qué
   fechas cambian en cada documento y por qué, y `pruebas/huellas.yaml` se re-registra en un commit
   propio cuyo mensaje dice que el cambio es deliberado.
5. Queda resuelto y escrito qué significa **un grupo declarado que este semestre no se imparte**
   (39056·962): si se retira del `curso.yaml`, si se marca inactivo, o si el horario del semestre es
   el que decide. La decisión aplica al caso general —cada semestre cambia qué grupos hay—, no solo
   al 962.
6. `python -X utf8 -m unittest discover -s pruebas` pasa: las 283 anteriores intactas más las nuevas.
**Planes**: 7 planes en 6 olas

- [x] `15-01-PLAN.md` — El bloque entra al contrato: `Bloque`, `Horario.bloques`, `Grupo.imparte` (ola 1)
- [x] `15-02-PLAN.md` — La suspensión recorre al siguiente día con clase, sin salir de la semana (ola 2)
- [x] `15-03-PLAN.md` — El horario entra al rastro: manifiesto, grafo y el grupo no impartido (ola 2)
- [x] `15-04-PLAN.md` — R6 comprueba el horario y avisa de la semana sin día de clase (ola 3)
- [x] `15-05-PLAN.md` — Los cuatro grupos dicen la verdad, y el cambio se mide antes de aceptarse (ola 4)
- [x] `15-06-PLAN.md` — Re-registro de la huella en commit propio (ola 5)
- [x] `15-07-PLAN.md` — El contrato canónico y las skills al día; cierre de la fase (ola 6)

### Fase 16: Mis clases en Google Calendar
**Meta**: que el profesor pueda meter sus clases del semestre en su agenda sin transcribirlas a mano.
**Depende de**: Fase 15 (sin horas de clase no hay evento posible).
**Requisitos**: REQ-53
**Criterios de éxito**:
1. Existe un comando que produce un archivo **`.ics`** con las clases del semestre y que Google
   Calendar importa sin error.
2. Cada clase presencial aparece con su materia, su grupo, su hora de inicio y fin, y su salón como
   ubicación. Las sesiones **virtuales** aparecen marcadas como tales y sin ubicación física.
3. El `.ics` respeta el calendario escolar: los eventos van del inicio al fin de clases de
   `calendarios/2026-2.yaml` y **no se genera ninguno en las tres suspensiones** (16 sep, 2 nov,
   16 nov). Hay una prueba que cuenta los eventos de una semana con suspensión y de una sin ella.
4. El `.ics` lleva **solo clases**. No hay eventos de tareas, entregas, exámenes, horas de
   investigación, coordinación ni tutorías. Hay una prueba que lo afirma sobre el archivo generado.
5. Una materia sin `curso.yaml` no bloquea la exportación de las demás.
6. Cierre: la suite completa pasa y `python src/plantillas.py verificar` sigue en verde.
**Planes**: 3 planes en 3 olas (verificación externa pendiente)

- [x] `16-01-PLAN.md` — Núcleo iCalendar: bloques + calendario oficial → `VEVENT`, con pruebas RFC y de calendario
- [x] `16-02-PLAN.md` — CLI, salida regenerable y documentación de importación manual
- [ ] `16-03-PLAN.md` — Verificación local cerrada; pendiente confirmar la importación en Google Calendar

---

## Milestone v1.0 — cerrado

Ocho fases hechas, tres materias generadas de extremo a extremo. Se conserva el detalle porque es
el registro de lo que cada fase prometió y de contra qué se verificó.

### Panorama

De un PDF de PUA a un DI firmable en `.docx` y `.pdf`. Se construye de abajo hacia arriba: primero
los cimientos y el banco de conocimientos que da contexto a los agentes, luego los dos motores que
aportan los datos duros (calendario y PUA), después el modelo que los une y lo valida, y al final
el renderizado, el orquestador que lo hace usable y el grafo que lo hace consultable.

El punto de mayor riesgo fue la Fase 6: rellenar las plantillas CIAD reales sin destruir su
formato. Por eso todo lo anterior existía — para que cuando se llegara ahí, los datos ya estuvieran
completos y validados.

### Fases

- [x] **Fase 1: Cimientos y normalización** — repositorio, árbol, contratos de agentes
- [x] **Fase 2: Banco de conocimientos** — todos los documentos fuente a Markdown
- [x] **Fase 3: Motor de calendario** — ciclo → semanas numeradas, saltando suspensiones
- [x] **Fase 4: Ingesta de PUA** — PDF → Markdown normalizado + índice
- [x] **Fase 5: Modelo y validación** — `curso.yaml` y las 8 reglas
- [x] **Fase 6: Renderizado docx + pdf** — rellenar las plantillas CIAD reales
- [x] **Fase 7: Orquestador** — `/di-nuevo`, multi-grupo, de extremo a extremo
- [x] **Fase 8: Grafo de conocimiento** — cobertura PUA↔metas

### Fase 1: Cimientos y normalización
**Meta**: repositorio listo y contratos de agentes escritos.
**Depende de**: nada.
**Requisitos**: REQ-33, REQ-34, REQ-36, REQ-37
**Criterios de éxito**:
1. `git init` hecho, `.gitignore` excluye salidas regenerables pero versiona `curso.yaml`.
2. El árbol completo existe y `referecnias/` → `referencias/`, `ejmplos/` → `ejemplos/`.
3. `AGENTS.md` contiene las reglas invariables, el contexto de dominio y las notas técnicas.
4. `.planning/config.json` fija el perfil `adaptive`.

### Fase 2: Banco de conocimientos
**Meta**: que cualquier agente pueda consultar la normatividad y las plantillas sin abrir binarios.
**Depende de**: Fase 1.
**Requisitos**: REQ-04
**Criterios de éxito**:
1. `conocimiento/normatividad/` tiene el Estatuto (arts. 63–75), propiedad intelectual y las
   políticas de curso de la Facultad.
2. `conocimiento/plantillas/` tiene el espejo de las 3 plantillas CIAD y las instrucciones de
   llenado, con los deltas entre modalidades explícitos.
3. `conocimiento/estilo/` recoge las reglas de redacción y las convenciones tipográficas.
4. `conocimiento/rubricas/iedi-2023-1.md` lista los indicadores con su clasificación I/N/R.
5. `conocimiento/ejemplos/` tiene el 961 como referencia dorada.

### Fase 3: Motor de calendario
**Meta**: fechas correctas, derivadas del calendario oficial.
**Depende de**: Fase 1.
**Requisitos**: REQ-06, REQ-07, REQ-08, REQ-09
**Criterios de éxito**:
1. `calendarios/2026-2.yaml` refleja el PDF oficial guardado en `calendarios/fuente/`.
2. `python src/calendario.py 2026-2` imprime **16** semanas con sus rangos de fecha.
3. Las semanas 6, 13 y 15 quedan marcadas con su suspensión.
4. Una fecha que cae en suspensión se recorre al siguiente día hábil.
5. Una fecha posterior al 28 nov 2026 es rechazada.

### Fase 4: Ingesta de PUA
**Meta**: convertir PUAs a Markdown consultable, de forma incremental.
**Depende de**: Fase 2.
**Requisitos**: REQ-01, REQ-02, REQ-03, REQ-05
**Criterios de éxito**:
1. `python src/ingesta_pua.py` sobre el PUA de Big Data produce `puas/md/39056-big-data.md`.
2. El front-matter trae los 9 campos de §I; las secciones I–X son encabezados.
3. La §VI se reconstruye con sus 10 prácticas y sus 5 columnas.
4. `puas/INDICE.md` registra clave, nombre, programa, plan, ruta y hash.
5. Reingerir el mismo PDF no duplica el registro.

### Fase 5: Modelo y validación
**Meta**: el contrato entre planeación y renderizado, con sus reglas.
**Depende de**: Fases 3 y 4.
**Requisitos**: REQ-19, REQ-20, REQ-21, REQ-22, REQ-23, REQ-24, REQ-25, REQ-26
**Criterios de éxito**:
1. `src/modelo.py` carga y valida un `curso.yaml` contra su esquema.
2. `config/profesores.yaml`, `esquemas-evaluacion.yaml`, `politicas.yaml` y `plantillas.yaml`
   existen y se cargan.
3. Las 8 reglas están implementadas y cada una tiene una prueba que la hace fallar a propósito.
4. Un esquema que suma 99 es rechazado; uno con un solo parcial también (Art. 68).

### Fase 6: Renderizado docx + pdf
**Meta**: el documento, con el formato institucional intacto.
**Depende de**: Fase 5.
**Requisitos**: REQ-10, REQ-11, REQ-12, REQ-13, REQ-14, REQ-15, REQ-16, REQ-28, REQ-29
**Criterios de éxito**:
1. El `.docx` abre en Word conservando logo, estilos y tablas de la plantilla.
2. La Sección 1 reproduce literalmente la identificación del PUA.
3. La Sección 2 tiene tantas filas-semana como semanas reales, ni una más.
4. La Sección 3 repite el bloque por meta con sus convenciones tipográficas.
5. Las secciones fusionadas y el bloque de firma aparecen al final.
6. El `.pdf` se genera sin dejar procesos `WINWORD.EXE` huérfanos.
7. Comparado contra `ejemplos/961 (1).pdf`, es equivalente en estructura y formato.

### Fase 7: Orquestador
**Meta**: que generar un DI sean seis preguntas.
**Depende de**: Fase 6.
**Requisitos**: REQ-14, REQ-17, REQ-18, REQ-27
**Criterios de éxito**:
1. `/di-nuevo` pregunta en orden y con defaults sensatos.
2. Si el PUA no está en el índice, lo pide y ofrece ingerirlo en el momento.
3. Big Data 2026-2 con grupos 961 y 962 produce cuatro archivos.
4. Los dos documentos difieren solo en el número de grupo y el bloque de firma.
5. `MANIFIESTO.yaml` permite reconstruir el origen de cada dato.

### Fase 8: Grafo de conocimiento
**Meta**: hacer consultable lo que hoy está disperso.
**Depende de**: Fase 7.
**Requisitos**: REQ-30, REQ-31
**Criterios de éxito**:
1. `grafo/` contiene HTML navegable, JSON y un informe de auditoría.
2. El grafo responde qué temas del PUA quedaron sin meta.
3. El grafo responde qué materias comparten competencias.
