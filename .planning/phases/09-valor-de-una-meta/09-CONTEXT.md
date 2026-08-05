# Fase 9: El valor de una meta deja de ser un porcentaje — Contexto

**Recogido:** 2026-08-04
**Estado:** Listo para planear

<domain>
## Frontera de la fase

Abrir el contrato `curso.yaml` en tres puntos —unidad del rubro (REQ-38), componentes de meta
(REQ-39) e identificadores libres (REQ-42)— y construir el instrumento de la no contaminación
(REQ-48) que heredan las cinco fases siguientes.

**Dentro:** el modelo (`src/modelo.py`), su carga y sus validaciones de esquema; el nuevo
`src/huella.py`; una sola concatenación en `src/render_docx.py` (ver D-11); las pruebas.

**Fuera:** la aritmética de las reglas en la unidad declarada (Fase 10), el segundo nivel de la
calificación (Fase 11), la rúbrica (Fase 12), el documento en la unidad real (Fase 13), el
`curso.yaml` de 38985 (Fase 14).

</domain>

<decisions>
## Decisiones de implementación

### Rubro en puntos (REQ-38)

- **D-01:** El rubro declara **dos claves nuevas y explícitas**: `unidad: puntos` y `total: 150`.
  Su ausencia significa porcentaje. El `porcentaje` del rubro sigue existiendo siempre y sigue
  siendo lo que cuenta contra el 100 del esquema.

  ```yaml
  rubros:
    - id: actividades
      etiqueta: "Entrega de actividades en clases y tareas"
      porcentaje: 30      # lo que cuenta contra el 100
      unidad: puntos      # nuevo
      total: 150          # nuevo
    - id: examenes
      etiqueta: "Exámenes"
      porcentaje: 50      # sin `unidad:` -> porcentaje
  ```

  Se descartaron `total_puntos:` (unidad implícita en el nombre del campo) y `escala: {…}`
  (un nivel más de anidamiento) por dejar más trabajo de inferencia a quien lee el YAML.

- **D-02:** `Meta.valor` **sigue siendo un `float` y hereda la unidad de su rubro**. `valor: 10`
  en una meta de «actividades» son 10 pts; en una de «exámenes», 10 %. La unidad se declara en un
  solo sitio, así que meta y rubro nunca pueden contradecirse. La meta **no** lleva `unidad:`
  propia.

- **D-03:** Una `unidad:` que el modelo no conozca es **`ErrorModelo` al cargar**, no un hallazgo
  de regla. Vocabulario cerrado y validado en `__post_init__`, igual que `MODALIDADES` y
  `TIPOS_META` hoy. Es un defecto de esquema, no de aritmética, así que el criterio 1 de la fase
  —«carga sin `ErrorModelo`; lo que se reporte después son hallazgos de reglas»— se respeta: lo
  que debe cargar y luego fallar en validación es el **desajuste de cantidades**, no una unidad
  inexistente.

- **D-04:** La **conversión de puntos a porcentaje entra en esta fase**, expuesta como propiedad
  del modelo (p. ej. `Rubro.a_porcentaje(valor)` o equivalente). Las Fases 10 y 13 la consumen en
  lugar de reinventarla; el cálculo vive en un solo sitio desde el principio.

- **D-05 (derivada, no preguntada):** un rubro con `unidad: puntos` y **sin** `total` es
  `ErrorModelo`. El total **no se infiere de la suma de las metas** — inferirlo haría invisible el
  defecto real del 531 (150 declarados contra 140 sumados), que es justamente lo que la Fase 10
  debe atrapar. Para un rubro en porcentaje, `total` es su propio `porcentaje`.

### Componentes de meta (REQ-39)

- **D-06:** Una meta declara sus aportes adicionales en una lista **`componentes:`**, cada entrada
  con `rubro`, `valor`, `etiqueta`, `tipo` y `evidencia`. Reusa el vocabulario que la meta ya usa
  para lo suyo. El aporte principal sigue en `rubro:`/`valor:` de la meta — no se unifica en una
  lista `valores:`, que habría roto las tres materias ya escritas y sus pruebas.

  ```yaml
  metas:
    - id: "2.4"
      unidad: "2"
      rubro: actividades
      valor: 10                 # 10 pts (unidad de SU rubro)
      semanas: [7]
      enunciado: "..."
      componentes:
        - rubro: examenes
          valor: 15             # 15 % (unidad de SU rubro)
          etiqueta: "Examen I"
          tipo: examen_parcial
          evidencia:
            nombre: "Examen I resuelto"
            tipo: "examen"
            recurso: "M2.4_Examen I"
  ```

- **D-07:** El `valor` de un componente se lee **en la unidad del rubro al que se imputa**, que
  puede ser distinto al de su meta. Es el caso de la 2.4 del 531: 10 pts en «actividades» y 15 %
  en «exámenes», en la misma meta.

- **D-08:** El `tipo` de un componente usa un **vocabulario propio y cerrado**, distinto de
  `TIPOS_META`:

  ```python
  TIPOS_COMPONENTE = ("examen_parcial", "examen_ordinario", "actividad", "proyecto")
  ```

  Solo `examen_parcial` cambia el comportamiento hoy (lo contará R3 en la Fase 10); los otros tres
  describen. Un valor fuera de la lista es `ErrorModelo`, para que un typo como `examen_partial`
  no se traduzca en un examen que nadie cuenta y en un DI que valida estando mal.

- **D-09:** Un componente lleva su propia `evidencia`, con la forma completa del dataclass
  `Evidencia` que ya existe (`nombre`, `tipo`, `recurso`).

- **D-10:** El componente **no entra en el grafo** en esta fase. No se crean nodos
  `meta:…:comp:{i}`. `grafo/` conserva su forma exacta, que es lo que REQ-48 exige comprobar al
  cerrar. Si más adelante conviene ver los exámenes en el grafo, es su propia decisión.

- **D-11 — desvío deliberado del «solo contrato»:** la evidencia de un componente **se concatena
  ya en esta fase** a las de su meta en la columna de evidencias de la Sección 2
  (`src/render_docx.py:283`). El roadmap definió la Fase 9 como contrato y el documento como
  Fase 13; esto lo cruza a propósito.

  Se decidió con la objeción sobre la mesa. Queda acotado así: es **contenido, no formato**, no
  toca plantillas ni estilos, y REQ-48 lo cubre —un curso sin `componentes:` no cambia ni un
  carácter—. La Fase 13 sigue siendo dueña de todo lo demás del documento: la columna Valor en
  puntos, el componente impreso en la Sección 3 («Examen I, 15 %») y los dos niveles.

### Identificadores libres (REQ-42)

- **D-12:** Nada en `src/` ordena las metas hoy — el orden declarado ya se conserva. **Confirmado
  por inspección:** no hay `sorted()` ni `.sort()` sobre `curso.metas` en ningún módulo. La fase
  lo fija con una prueba, no lo implementa.

- **D-13:** El encuadre ya se distingue por **`tipo`, no por id** (`src/validar.py:394`
  —`m.tipo not in ("encuadre", "cierre")`—). Es la única suposición encontrada y es la correcta.
  Se registra la auditoría de `src/` en el plan y se fija con la prueba de D-15.

- **D-14:** **El encuadre `0` de Big Data se renombra a `1.0` de verdad**, en
  `cursos/2026-2/39056-big-data/curso.yaml`, y el cambio de huella se acepta con
  `huella registrar`. Se descartó hacerlo sobre una copia en memoria.

  **Objeción registrada, decisión mantenida:** esto gasta la primera —y hasta ahora única—
  excepción a REQ-48 dentro de la misma fase que construye el instrumento para vigilarlo. Por eso
  el orden de los pasos deja de ser indiferente y queda fijado en D-15.

- **D-15:** **Orden obligatorio de los pasos de la fase.** El renombrado va al final, no al
  principio:

  ```
  1. huella registrar            # línea base del repo tal como está HOY
  2. …contrato: unidad, total, componentes, conversión…
  3. huella verificar            # ✓ nada cambió — el instrumento demuestra algo
  4. renombrar 0 -> 1.0 en Big Data
  5. huella verificar            # ! cambió 39056
     git diff                    # solo "Meta 0." -> "Meta 1.0."
  6. huella registrar            # se acepta, con el diff como constancia
  ```

  Registrar la línea base **después** del renombrado dejaría el único cambio de huella del
  milestone sin medir. El planeador no puede reordenar estos pasos.

- **D-16:** El renombrado alcanza **solo al encuadre** de Big Data. `1.1`, `1.2`, … se quedan
  igual: la unidad 1 abre en `.0` y sigue en `.1`, que es exactamente el patrón del 531. No se
  renumera Big Data entero ni se toca Patrones (39062), que queda como documento de control con
  su huella intacta durante toda la fase.

- **D-17:** Dos metas con el mismo id pasan a ser **error de regla en R2**, no `ErrorModelo`. Hoy
  no se comprueba: `validar.py:141` usa `Counter` para ids de rubro repetidos, pero no hay nada
  equivalente para metas. Con identificadores libres el riesgo de colisión sube y el grafo
  construye sus nodos a partir del id (`grafo.py:297`). El curso con el typo sigue cargando y se
  puede inspeccionar; falla al validar.

### Instrumento de la no contaminación (REQ-48)

- **D-18:** El instrumento es **`src/huella.py` con CLI**, siguiendo el patrón que ya existe en
  `src/plantillas.py verificar`. Dos subcomandos:

  ```
  python src/huella.py verificar    # compara contra el registro
  python src/huella.py registrar    # acepta el estado actual como nueva línea base
  ```

  No se mete en `pruebas/` ni en `src/comprobar.py`: la generación completa de dos DIs no debe
  colgarse del ciclo de las pruebas unitarias, que hoy son rápidas y no dependen de las
  plantillas. Se corre a mano al cerrar cada fase.

- **D-19:** La huella la componen **el texto del `.docx` y el informe de validación**:

  | Qué | Cómo |
  |---|---|
  | `texto_docx` | sha256 del texto extraído con `python-docx` — párrafos y celdas de tabla, en orden |
  | `informe` | sha256 de la salida de `validar.py` para ese curso |

  **No** se hashea el `.docx` binario: su zip lleva marcas de tiempo y cambiaría en cada corrida.
  **No** entra el `.pdf`: exportarlo necesita Word por COM y el instrumento debe correr en
  cualquier máquina. El informe entra porque la Fase 10 es de reglas: un cambio que altere un
  hallazgo sin tocar el documento pasaría inadvertido si solo se mirara el `.docx`.

  La «forma» del `MANIFIESTO.yaml` no entra en la huella. REQ-48 la menciona, pero el manifiesto
  lleva fecha y commit en cada corrida y definir «forma» abre una decisión que esta fase no
  necesita. Se comprueba a ojo al cerrar. **Si el planeador considera que esto deja REQ-48
  incompleto, que lo levante en el plan en vez de resolverlo por su cuenta.**

- **D-20:** El registro vive en **`pruebas/huellas.yaml`**, versionado, con una entrada por curso y
  grupo. Está en git, así que `git diff` muestra quién cambió una huella y en qué commit — que es
  medio instrumento por sí solo. No se dispersa junto a cada curso ni se mete en `.planning/`.

- **D-21:** Actualizar una huella legítima es un acto deliberado: **`huella registrar`**, un
  subcomando que solo se corre a propósito y cuyo efecto queda en el diff. No se edita el YAML a
  mano pegando hashes. La variante que muestra el diff del texto y pide confirmación se consideró
  y se descartó por código de más en una herramienta interna — `git diff` ya lo da.

- **D-22:** Los documentos de control son **39056 (Big Data, grupos 961 y 962) y 39062 (Patrones)**,
  los de Adrian. 38985 no entra: es el curso que va a cambiar.

### Resueltas tras la investigación (2026-08-05)

- **D-23:** `huella verificar` **restaura los `MANIFIESTO.yaml`** de los cursos de control al
  terminar (`git checkout` sobre esos archivos). `generar.paquete()` reescribe `generado:` y
  `commit:` en cada corrida y ambos archivos están versionados, así que sin esto cada verificación
  ensuciaría el árbol. Con esto, **`verificar` es de solo lectura sobre el repo**: si `git status`
  sale sucio después de verificar, es señal de verdad. `huella registrar` **sí** los deja escritos
  — ahí el cambio es deliberado y debe quedar en el commit.

- **D-24:** El rename de D-14 arrastra **`python src/grafo.py`** como paso explícito de la
  secuencia de D-15, inmediatamente después del renombrado y antes de `huella registrar`.
  `grafo/grafo.json` está versionado y dice «Meta 0. Encuadre del curso.» dos veces; sin
  regenerar, el repo queda mencionando una meta que ya no existe con ese id. **No contradice
  D-10:** D-10 protege la *forma* del grafo —su esquema de nodos y aristas, que no cambia y sigue
  sin conocer los componentes—; lo que cambia aquí es una cadena de texto, igual que en el `.docx`.
  La secuencia de D-15 queda así:

  ```
  1. huella registrar            # línea base del repo tal como está HOY
  2. …contrato: unidad, total, componentes, conversión…
  3. huella verificar            # ✓ nada cambió
  4. renombrar 0 -> 1.0 en Big Data
  5. python src/grafo.py         # el grafo sigue al curso.yaml
  6. huella verificar            # ! cambió 39056
     git diff                    # solo "Meta 0." -> "Meta 1.0." (+ grafo/)
  7. huella registrar            # se acepta, con el diff como constancia
  ```

- **D-25:** Los documentos de control son **cuatro**: 39056 grupos **961** y **962**, y 39062
  grupos **971** y **972**. El «39062 grupo 1» del ejemplo de salida de `<specifics>` es
  ilustrativo y no corresponde a ningún grupo real —39062 declara 971 y 972 en su `curso.yaml`—.
  Vigilar los cuatro cuesta lo mismo y evita que un cambio que solo afecte al 972 pase inadvertido.

- **D-26:** `Componente.tipo` es **obligatorio, sin default**. Es el mismo razonamiento de D-08: un
  default silencioso `"actividad"` convertiría un typo en un componente que nadie cuenta, que es
  justo lo que D-08 quiso evitar. Quien declara un componente declara de qué tipo es.

- **D-27 — corrige la salvedad de D-19:** **la forma del `MANIFIESTO.yaml` sí entra en la huella**,
  como un tercer hash por documento, calculado sobre el manifiesto con las claves volátiles fuera:
  `generado`, `commit`, y los `sha256`/`bytes` de los archivos. Lo que se vigila es su **forma** —qué
  claves emite y con qué estructura—, no sus valores por corrida.

  D-19 lo había dejado fuera porque «definir forma abre una decisión que esta fase no necesita», y
  pidió que el planeador lo levantara si veía REQ-48 incompleto. Lo levantó: hoy el manifiesto está
  protegido **por construcción** —`generar.py` arma su bloque de rubros como
  `[{"id": r.id, "porcentaje": r.porcentaje}]`, filtrando explícitamente, y las metas ni aparecen—,
  pero eso es una propiedad del código actual, no una promesa verificada. Las Fases 11 y 12 añaden
  segundo nivel y rúbrica, y cualquiera podría querer reflejarlos ahí sin que nada lo señalara.
  «Se revisa a ojo al cerrar» es la comprobación que deja de hacerse a la tercera fase.

  Se decide **antes** de ejecutar 09-01 porque cambia el formato de `pruebas/huellas.yaml` y la
  línea base. Sale de `<deferred>`.

- **D-28:** `huella verificar` restaura los `MANIFIESTO.yaml` **leyendo sus bytes antes de generar
  y reescribiéndolos después**, no con `git checkout`. Cumple lo que D-23 pedía —que `verificar`
  sea de solo lectura sobre el repo— y además no destruye una edición sin commitear que ya
  estuviera en el archivo. `huella.py` no invoca git, así que funciona igual fuera de un repo.

### Criterio de Claude

- El nombre exacto de la propiedad de conversión de D-04, la firma de las funciones de
  `src/huella.py`, y la disposición interna de `pruebas/huellas.yaml`.
- Cómo se recorre el `.docx` para extraer su texto en orden estable (párrafos del cuerpo, celdas
  de tabla, encabezados) — con la única condición de que sea determinista entre corridas.
- El texto de los mensajes de `ErrorModelo` nuevos, siguiendo el estilo de los existentes: decir
  qué falta y cuáles son los valores válidos, no solo que falló.

</decisions>

<canonical_refs>
## Referencias canónicas

**Los agentes de investigación y planeación deben leer esto antes de planear o implementar.**

### Reglas del proyecto
- `AGENTS.md` — archivo canónico: reglas invariables, arquitectura, contexto de dominio, estilo
  CIAD y notas técnicas. Se lee primero.
- `CLAUDE.md` — lo específico de Claude Code: skills, reparto de modelos, la prohibición de tocar
  las plantillas de `referencias/`.

### Requisitos y alcance
- `.planning/REQUIREMENTS.md` §Estructura de calificación variable — REQ-38, REQ-39, REQ-42 son de
  esta fase; REQ-48 es su criterio de cierre.
- `.planning/ROADMAP.md` §Fase 9 — los cinco criterios de éxito, que son la definición de hecho.
- `.planning/PROJECT.md` §Milestone actual — los cinco rasgos de la v2.0 y qué asume el modelo hoy
  sobre cada uno.

### El código que se toca
- `src/modelo.py` — `Rubro` (:159, solo `porcentaje`), `Meta.valor` (:123, comentado como
  «porcentaje de la calificación final»), `_construir_meta` (:241) y `desde_dict` (:260), que
  construyen con `Rubro(**r)` y `Meta(**d)`: cualquier clave nueva revienta ahí con `TypeError`.
  Es el punto exacto donde entra el contrato nuevo.
- `src/validar.py` — R1 (:126) y R2 (:173), que suman `porcentaje` y `valor` sin unidad. **No se
  reescriben en esta fase** (son Fase 10), pero hay que leerlas para no romperlas. `:141` es el
  `Counter` de rubros duplicados, el molde de D-17. `:394` es la única suposición sobre el
  encuadre y ya usa `tipo`.
- `src/render_docx.py:283` — la concatenación de evidencias de D-11. `:286` y `:408` imprimen
  `f"{meta.valor:g}%"` con el `%` fijo: **son de la Fase 13, no se tocan aquí.**
- `src/grafo.py:297` — los nodos de meta se construyen con `m.id`; explica por qué D-17 importa.
- `src/plantillas.py` — el patrón de CLI con subcomandos que D-18 replica.
- `src/generar.py:180` — el `MANIFIESTO.yaml` emite `{"id", "porcentaje"}` por rubro. Ver la
  salvedad de D-19.

### El curso que motiva todo esto
- `conocimiento/ejemplos/531-contabilidad-financiera-2026-1.md` — el espejo en Markdown del DI de
  Zurisaddai: de dónde salen los 150 pts, la meta 2.4 y los tres exámenes dentro de la actividad.
- `ejemplos/38985-531-2026-1-Rubio Arriaga Zurisaddai.docx` — el original.
- `cursos/2026-2/38985-contabilidad-financiera/curso.yaml` — la reconstrucción **traducida**, con
  la deuda declarada en sus `avisos:`. **No se toca en esta fase** (es la 14); se lee para saber
  qué hay que dejar de traducir.
- `.planning/STATE.md` §Reconstrucción del curso de Zurisaddai — la tabla de las tres traducciones
  que se hicieron y por qué.

### Los documentos de control
- `cursos/2026-2/39056-big-data/curso.yaml` — el encuadre `0` de D-14.
- `cursos/2026-2/39062-patrones-de-comportamiento/curso.yaml` — control intacto toda la fase.

</canonical_refs>

<code_context>
## Lo que ya existe

### Reutilizable
- **`Evidencia`** (`modelo.py:92`) — el dataclass del componente en D-09 ya está escrito.
  `_construir_meta` (:243) además acepta la forma corta (una cadena en vez de un mapa); conviene
  que el componente la acepte igual.
- **Validación en `__post_init__`** (`modelo.py:109`, `:135`) — el patrón de vocabulario cerrado
  que D-03 y D-08 replican: comprueba, y en el mensaje de error lista los válidos.
- **`Counter`** (`validar.py:141`) — ya importado y en uso para rubros duplicados; D-17 lo repite
  para metas.
- **CLI con subcomandos** (`src/plantillas.py`) — el molde de `src/huella.py`. `plantillas.sha256()`
  ya existe como utilidad de hash.
- **`src/generar.py`** — genera un curso completo (validar → renderizar por grupo → PDF →
  manifiesto). `huella.py` lo invoca en vez de reimplementar la generación.

### Patrones que condicionan
- **El renderizador no inventa** (REQ-26): todo lo que aparece en el documento sale del
  `curso.yaml`. Por eso el componente declara su etiqueta y su evidencia en vez de que el código
  las componga.
- **Los dataclasses se construyen con `**kwargs`** desde el YAML. Los campos nuevos necesitan
  default para que los tres `curso.yaml` existentes sigan cargando sin tocarse — es la mitad de
  REQ-48 resuelta por construcción.
- **Las plantillas de `referencias/` no se modifican.** Esta fase no debería acercarse a ellas;
  si algo lo intenta, `python src/plantillas.py verificar` lo delata.

### Puntos de integración
- `desde_dict` / `_construir_meta` (`modelo.py:241-286`) — por donde entra todo el contrato nuevo.
- `render_docx.py:283` — el único punto de renderizado que esta fase toca (D-11).
- `pruebas/test_validar.py` — donde viven las pruebas de reglas; `test_detecta_el_defecto_del_ejemplo_961`
  debe seguir pasando sin tocarse.

</code_context>

<specifics>
## Ideas concretas

- El YAML de D-01 y D-06 es literal: así se escriben. Los ejemplos salen de la meta 2.4 y del
  rubro «Entrega de actividades en clases y tareas» del 531 real, no son inventados.
- La salida de `huella verificar` que se quiere ver:

  ```
  python src/huella.py verificar

    ✓ 39056 grupo 961   huella intacta
    ✓ 39056 grupo 962   huella intacta
    ✓ 39062 grupo 1     huella intacta

  Todo intacto. 3 documentos comparados.
  ```

  Cuando algo cambia, tiene que decir **qué** documento y bastar para ir a mirarlo. Mismo espíritu
  que `src/comprobar.py`: decir qué falta y qué hacer, no solo que falló.

- La prueba del renombrado, en la forma que se discutió:

  ```python
  # única diferencia admitida: "Meta 0." -> "Meta 1.0."
  assert texto_a.replace("Meta 0.", "Meta 1.0.") == texto_b
  ```

</specifics>

<deferred>
## Ideas aplazadas

- **Los componentes como nodos del grafo** (D-10). Haría visible cada examen como entidad
  consultable, pero cambia la forma de `grafo/` y REQ-48 la quiere intacta durante todo el
  milestone. Es su propia decisión, después de la v2.0.
- ~~**La «forma» del `MANIFIESTO.yaml` dentro de la huella** (D-19)~~ — **entra en la Fase 9**.
  Ver D-27: el planeador levantó que REQ-48 quedaba incompleto sin ella y se decidió añadirla.
  «Forma» quedó definido como el manifiesto sin `generado`, `commit`, `sha256` ni `bytes`.
- **Que `di-nuevo` pregunte por la unidad de cada rubro.** El orquestador seguirá produciendo
  rubros en porcentaje; un curso en puntos se escribe a mano por ahora. Cuando el rasgo esté
  probado de extremo a extremo (Fase 14), tiene sentido subirlo al menú.
- **Rubros en puntos en el catálogo `config/esquemas-evaluacion.yaml`.** Ningún esquema del
  catálogo los declara hoy y el aviso de R1 (`validar.py:164`) compara `{id: porcentaje}`, que
  sigue siendo válido. Se revisa cuando algún esquema del catálogo lo necesite.
- **Renumerar Big Data y Patrones enteros al esquema `.0`** (descartado en D-16). Es una decisión
  de estilo que REQ-42 no pide.

</deferred>

---

*Fase: 09-valor-de-una-meta*
*Contexto recogido: 2026-08-04*
