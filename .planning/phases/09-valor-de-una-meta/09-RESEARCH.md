# Fase 9: El valor de una meta deja de ser un porcentaje - Investigación

**Investigado:** 2026-08-04
**Dominio:** Modelo de datos (dataclasses de `src/modelo.py`), validación de esquema y un
instrumento de fingerprinting de documentos (`src/huella.py`) sobre un generador de DI en Python.
**Confianza:** ALTA — todo lo afirmado abajo se verificó leyendo el código real y ejecutando
comandos contra el repositorio, no contra memoria de entrenamiento.

## Resumen

Esta fase abre `curso.yaml` en tres puntos del modelo (`src/modelo.py`) y construye un instrumento
nuevo (`src/huella.py`). No hay librería externa que investigar: todo el trabajo es Python estándar
(`dataclasses`, `python-docx` 1.2.0, `PyYAML` 6.0.3, `hashlib`) sobre patrones que el propio
repositorio ya usa en tres sitios distintos (`_construir_meta`, `plantillas.py`, `generar.py`).

La auditoría de ids de meta que pedía el CONTEXT.md se hizo por grep dirigido y confirma
exactamente lo que D-12/D-13 afirmaban: no hay `sorted()`/`.sort()` sobre `curso.metas` en ningún
módulo, y la única suposición real sobre el encuadre está en `validar.py:394` y usa `m.tipo`, no
`m.id`. No apareció ningún hallazgo nuevo.

La parte con más riesgo de sorpresa no es el modelo — es la extracción de texto determinista de un
`.docx` (D-19). Se verificó empíricamente contra un documento real ya generado
(`DI-2026-2-39056-961.docx`) que **`row.cells[i].text` de python-docx resuelve las celdas con
`vMerge` y devuelve el texto de la celda de origen duplicado en cada fila que la celda fusionada
abarca**, aunque el XML de esas celdas continuación no tenga ningún `<w:t>`. Esto no rompe la
huella (es determinista), pero sí puede confundir a quien lea el texto extraído pensando que hay
una duplicación real. La receta recomendada evita el problema iterando el OOXML crudo en vez de la
API de alto nivel.

**Recomendación principal:** los cinco campos nuevos (`Rubro.unidad`, `Rubro.total`, la lista
`Meta.componentes`, el dataclass `Componente`, y `Rubro.a_porcentaje`) se añaden como campos
*opcionales con default* siguiendo exactamente el patrón que ya usan `Evidencia`/`Sesion`/
`_construir_meta`; `src/huella.py` se escribe como un cuarto CLI con subcomandos, calcando
`src/plantillas.py`, y reutiliza `generar.paquete(ruta, pdf=False, grupos=[...])` para generar sin
depender de Word COM.

## Mapa de responsabilidad arquitectónica

| Capacidad | Tier primario | Tier secundario | Justificación |
|---|---|---|---|
| Esquema de `curso.yaml` (Rubro/Meta/Componente) | Modelo de datos (`src/modelo.py`) | — | Es el contrato; toda validación y renderizado lo consume, nunca lo redefine |
| Cierre de vocabulario (`unidad`, `tipo` de componente) | Modelo de datos (`__post_init__`) | Validación (`src/validar.py`) | `ErrorModelo` es un defecto de esquema (carga), no de regla (aritmética) — D-03/D-08 |
| Conteo/suma en la unidad declarada (R1/R2) | Validación (`src/validar.py`) | — | Fuera de alcance de esta fase (Fase 10); solo se audita qué tocarían los campos nuevos |
| Concatenación de evidencias de componente | Renderizado (`src/render_docx.py:283`) | — | Único punto de renderizado que esta fase toca (D-11); contenido, no formato |
| Grafo de dominio | `src/grafo.py` | — | No se toca: D-10 excluye los componentes del grafo |
| Instrumento de no contaminación | CLI nuevo (`src/huella.py`) | Generación (`src/generar.py`, reusada) | Vive fuera de `pruebas/`; corre a mano, no en cada test run (D-18) |
| Registro de huellas | `pruebas/huellas.yaml` (dato versionado) | — | Vive junto a las pruebas por convención de ruta, pero no es una prueba unitaria |

## Requisitos de la fase

| ID | Descripción | Soporte de la investigación |
|----|-------------|------------------------------|
| REQ-38 | Rubro en puntos (`unidad: puntos`, `total: N`), convive con rubros en porcentaje | §"Rubro en puntos" abajo — dataclass `Rubro`, `__post_init__`, `desde_dict`, líneas confirmadas |
| REQ-39 | Meta con componentes adicionales, sigue siendo una sola meta con una sola semana | §"Componentes de meta" — dataclass `Componente`, `_construir_meta`, D-10/D-11 |
| REQ-42 | Identificador de meta libre dentro de su unidad | §"Auditoría de suposiciones sobre ids" — grep confirmado, sin hallazgos nuevos |
| REQ-48 (cierre) | No contaminación: 39056 y 39062 no cambian de huella | §"Instrumento de la no contaminación" — `src/huella.py`, `pruebas/huellas.yaml`, riesgos de generación |

## Standard Stack

No hay dependencias nuevas que instalar. Todo lo que esta fase necesita ya está en el entorno,
verificado con `python -X utf8 src/comprobar.py`:

### Core (ya instalado, verificado en esta máquina)

| Librería | Versión instalada | Propósito en esta fase | Por qué no cambia |
|---|---|---|---|
| `python-docx` | 1.2.0 `[VERIFIED: pip show]` | D-19 — extracción de texto del `.docx` para la huella | Ya es la librería del renderizador; REQ-32 pide reusar el toolchain instalado |
| `PyYAML` | 6.0.3 `[VERIFIED: pip show]` | Lectura/escritura de `pruebas/huellas.yaml` | Mismo loader/dumper que usa `modelo.py`, `plantillas.py` y `generar.py` |
| `hashlib` (stdlib) | — | sha256 del texto extraído y del informe | `plantillas.sha256()` ya es la utilidad de hash del proyecto — se reusa, no se reimplementa |
| `dataclasses` (stdlib) | Python 3.11.9 `[VERIFIED: python --version]` | `Componente`, campos nuevos de `Rubro`/`Meta` | Es el único mecanismo de modelo que usa el proyecto |

### No hay "Alternativas Consideradas" que investigar

Esta fase no introduce ningún problema con más de una solución razonable en el ecosistema Python
—no hay biblioteca de "diffing de documentos" ni "esquema declarativo" que evaluar—: es extender
dataclasses ya existentes y escribir un CLI que sigue un molde ya escrito tres veces en el
repositorio (`plantillas.py`, `generar.py`, `comprobar.py`).

**Instalación:** ninguna. `pip show python-docx PyYAML` confirma 1.2.0 y 6.0.3 ya presentes.

## Architecture Patterns

### Diagrama de flujo — instrumento de no contaminación

```
┌─────────────────┐     ┌──────────────────┐      ┌───────────────────────┐
│ curso.yaml       │────▶│ generar.paquete() │─────▶│ .docx en cursos/…/    │
│ (39056, 39062)   │     │  pdf=False        │      │ salida/ (gitignored)  │
└─────────────────┘     │  grupos=[…]       │      └───────────┬───────────┘
                         └────────┬──────────┘                  │
                                  │ informe.texto()              │ python-docx
                                  ▼                              ▼
                         ┌──────────────────┐      ┌───────────────────────┐
                         │ sha256(informe)   │      │ extraer_texto(docx)   │
                         └────────┬──────────┘      │ (orden OOXML crudo)   │
                                  │                 └───────────┬───────────┘
                                  │                             │ sha256(texto)
                                  ▼                             ▼
                         ┌─────────────────────────────────────────────┐
                         │      huella = {texto_docx, informe}          │
                         └───────────────────┬───────────────────────────┘
                                              │
                          ┌───────────────────┴────────────────────┐
                          ▼                                        ▼
              huella verificar                          huella registrar
     compara contra pruebas/huellas.yaml          escribe pruebas/huellas.yaml
     ✓/✗ por curso+grupo, sin tocar el YAML        (acto deliberado, D-21)
```

### Recommended flujo del modelo (dónde entran los campos nuevos)

```
curso.yaml (YAML)
   │
   ▼
desde_dict(d)                     ← modelo.py:260
   │  evaluacion.get("rubros", []) ──▶ Rubro(**r)         ← modelo.py:276  (+unidad, +total)
   │  d.pop("metas", [])           ──▶ _construir_meta(m) ← modelo.py:241
   │                                        │
   │                                        ├─ pop sesiones   → [Sesion(**s) ...]
   │                                        ├─ pop evidencias → [Evidencia(**e)|Evidencia(nombre=e)]
   │                                        ├─ pop componentes → [Componente(**c) ...]  ← NUEVO
   │                                        └─ Meta(semanas=…, sesiones=…, evidencias=…,
   │                                                 componentes=…, **d)
   ▼
Curso(rubros=[...], metas=[...])   ← cualquier clave sobrante en r/m revienta con TypeError,
                                       capturado en modelo.cargar() → ErrorModelo (línea 322-323)
```

### Patrón 1: Campo opcional con default para no contaminar cursos existentes

**Qué:** cada campo nuevo de un dataclass que se construye con `**kwargs` desde YAML lleva un
default. Es la mitad de REQ-48 resuelta por construcción: un `curso.yaml` que no declare la clave
nueva sigue construyendo el mismo objeto que hoy.

**Cuándo usarlo:** siempre que se añade una clave al contrato de `curso.yaml` en esta fase.

**Ejemplo (patrón ya existente, molde a seguir):**
```python
# Fuente: src/modelo.py:92-95 (Evidencia) — el patrón exacto a replicar en Rubro/Meta
@dataclass
class Evidencia:
    nombre: str
    tipo: str = ""
    recurso: str = ""  # p. ej. "M1.1_Mapa conceptual"
```

Aplicado a `Rubro` (extensión, no reemplazo — se **verificó** que hoy solo tiene `id, etiqueta,
porcentaje, detalle="", parciales=0` en `modelo.py:159-165`):
```python
@dataclass
class Rubro:
    id: str
    etiqueta: str
    porcentaje: float
    detalle: str = ""
    parciales: int = 0
    unidad: str = ""       # "" (ausente) = porcentaje; "puntos" = D-01
    total: float | None = None   # obligatorio si unidad == "puntos" (D-05)

    def __post_init__(self) -> None:
        if self.unidad and self.unidad not in UNIDADES_RUBRO:
            raise ErrorModelo(
                f"Rubro {self.id}: unidad inválida {self.unidad!r}. "
                f"Válidas: {', '.join(UNIDADES_RUBRO)} (o ausente, para porcentaje)."
            )
        if self.unidad == "puntos" and self.total is None:
            raise ErrorModelo(
                f"Rubro {self.id}: declara unidad «puntos» sin `total`. "
                f"Un rubro en puntos debe declarar su total (p. ej. `total: 150`)."
            )
```
`UNIDADES_RUBRO = ("puntos",)` junto a `MODALIDADES`/`TIPOS_META` (D-03: vocabulario cerrado). El
mensaje de error sigue el estilo pedido en `<decisions>` ("Criterio de Claude"): dice qué falta y
cuáles son los valores válidos.

### Patrón 2: Lista de sub-objetos poppeada antes de `**kwargs`

**Qué:** cuando un campo del dict es una lista de mapas que debe convertirse en una lista de
dataclasses, se saca (`d.pop(...)`) del dict **antes** de pasar `**d` al constructor del
dataclass contenedor — igual que ya se hace con `sesiones` y `evidencias`.

**Ejemplo (patrón exacto de `_construir_meta`, `modelo.py:241-250`, para replicar con
`componentes`):**
```python
# Fuente: src/modelo.py:241-250 — patrón verificado a extender con componentes
def _construir_meta(d: dict) -> Meta:
    sesiones = [Sesion(**s) for s in d.pop("sesiones", [])]
    evidencias = [
        Evidencia(**e) if isinstance(e, dict) else Evidencia(nombre=e)
        for e in d.pop("evidencias", [])
    ]
    componentes = [_construir_componente(c) for c in d.pop("componentes", [])]  # NUEVO
    semanas = d.pop("semanas", None)
    if semanas is None and (s := d.pop("semana", None)) is not None:
        semanas = [s]
    return Meta(
        semanas=semanas or [], sesiones=sesiones, evidencias=evidencias,
        componentes=componentes, **d,
    )


def _construir_componente(c: dict) -> Componente:
    c = dict(c)
    ev = c.pop("evidencia", None)
    evidencia = (
        Evidencia(**ev) if isinstance(ev, dict)
        else Evidencia(nombre=ev) if ev
        else None
    )
    return Componente(evidencia=evidencia, **c)
```
D-09 pide que el componente acepte la evidencia en forma corta (una cadena), igual que
`_construir_meta` ya hace con la lista `evidencias` de la meta (línea 244) — el fragmento arriba
replica exactamente esa rama `isinstance(e, dict)`.

`Componente` (nuevo dataclass, junto a `Evidencia`/`Sesion` en `modelo.py`):
```python
TIPOS_COMPONENTE = ("examen_parcial", "examen_ordinario", "actividad", "proyecto")  # D-08


@dataclass
class Componente:
    rubro: str
    valor: float
    etiqueta: str
    tipo: str = "actividad"
    evidencia: Evidencia | None = None

    def __post_init__(self) -> None:
        if self.tipo not in TIPOS_COMPONENTE:
            raise ErrorModelo(
                f"Componente «{self.etiqueta}»: tipo inválido {self.tipo!r}. "
                f"Válidos: {', '.join(TIPOS_COMPONENTE)}."
            )
```

`Meta` gana `componentes: list[Componente] = field(default_factory=list)` — ni `len(curso.metas)`
ni `m.semanas` cambian (criterio de éxito 2 de la fase), porque el componente vive *dentro* de la
meta, no al lado.

### Patrón 3: CLI con subcomandos (molde de `src/huella.py`)

**Qué:** `src/plantillas.py` ya resuelve exactamente el problema de D-18 — dos verbos
(`verificar`/`registrar`), salida legible, código de salida 1 si algo no coincide.

**Ejemplo (molde verificado, `src/plantillas.py:303-337`):**
```python
# Fuente: src/plantillas.py:303-337 — estructura exacta a replicar en huella.py
def main(argv: list[str]) -> int:
    orden = argv[1] if len(argv) > 1 else "verificar"
    try:
        if orden == "registrar":
            ...
        elif orden == "verificar":
            if problemas := verificar():
                for p in problemas:
                    print(f"✗ {p}", file=sys.stderr)
                return 1
            print("...")
        else:
            print(f"Orden desconocida: {orden}", file=sys.stderr)
            return 2
    except ErrorPlantilla as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    return 0
```
`src/huella.py` reusa `plantillas.sha256` (ya importable como `plantillas.sha256(ruta_o_texto)` —
ojo: hoy solo hashea archivos, `sha256(ruta: Path)`; para hashear texto en memoria hay que abrir su
propia función `hashlib.sha256(texto.encode("utf-8")).hexdigest()`, un one-liner, no justifica
duplicar `plantillas.sha256`).

### Patrón 4: reusar `generar.paquete()` sin Word

**Qué:** `generar.paquete(ruta_curso, pdf=False, grupos=[...])` (firma verificada en
`src/generar.py:221-226`) valida, renderiza el `.docx` por grupo **y no exporta a PDF**. Esto
resuelve directamente la pregunta crítica de D-19: sí se puede generar el `.docx` sin Word COM.

```python
# Fuente: src/generar.py:221-300 — firma y comportamiento verificados
def paquete(
    ruta_curso: Path | str,
    pdf: bool = True,
    traza=None,
    grupos: list[str] | None = None,
) -> Paquete:
    ...
```
`huella.py` llama a esto por cada curso de control, con `pdf=False` y `grupos=[g.numero]` uno a la
vez (o sin filtro, para los dos grupos de 39056 en una sola llamada). `Paquete.archivos` devuelve
la lista de `Path` a los `.docx` generados — de ahí se extrae el texto.

### Estructura de proyecto (sin cambios de directorio)

```
src/
├── modelo.py       # Rubro/Meta/Componente — se edita
├── validar.py       # NO se edita (solo se lee/audita)
├── render_docx.py   # una sola línea nueva (D-11) — se edita
├── huella.py        # NUEVO — CLI con subcomandos
├── plantillas.py     # molde de huella.py — no se edita
└── generar.py        # se reusa, no se edita
pruebas/
├── huellas.yaml      # NUEVO — registro versionado
└── test_modelo.py    # posible archivo nuevo, o ampliar test_validar.py — ver "Validation Architecture"
```

### Anti-patrones a evitar

- **Reimplementar la generación dentro de `huella.py`.** El plan debe llamar a
  `generar.paquete()`, no reconstruir validar→renderizar a mano. `AGENTS.md` es explícito: es el
  único comando que necesita el orquestador, y duplicar su lógica en un segundo sitio es exactamente
  el tipo de deuda que la Fase 9 no debería introducir.
- **Usar `row.cells[i].text` de python-docx como fuente de verdad para el texto de una tabla con
  celdas fusionadas.** Ver la sección "Extracción determinista" abajo — produce duplicación
  silenciosa que no es un error, pero confunde el diagnóstico. Preferir el recorrido OOXML crudo.
- **Inferir `total` de un rubro en puntos sumando las metas.** D-05 lo prohíbe explícitamente:
  haría invisible el defecto real del 531 que la Fase 10 debe atrapar.
- **Comparar o parsear `Meta.id` en cualquier función nueva.** REQ-42 lo prohíbe; la auditoría de
  abajo confirma que hoy no ocurre — no lo introduzcas al escribir el código de esta fase.

## Don't Hand-Roll

| Problema | No construir | Usar en su lugar | Por qué |
|---|---|---|---|
| Hash de un archivo | Una función `sha256()` nueva | `plantillas.sha256(ruta)` (`src/plantillas.py:55-60`) | Ya existe, ya está probada, evita dos implementaciones del mismo hash en el repo |
| Generar el `.docx`/`.pdf` de un curso | Llamar a `validar.validar()` + `render_docx.generar()` a mano | `generar.paquete(ruta, pdf=False, grupos=[...])` | Encapsula el orden correcto (validar antes de renderizar) y ya maneja el caso sin Word |
| Dump de YAML legible y estable | `json.dumps` o un dumper custom | `yaml.safe_dump(cuerpo, allow_unicode=True, sort_keys=False, default_flow_style=False)` | Es exactamente lo que usan `plantillas.guardar()` y `generar.escribir_manifiesto()` — mismo estilo en todo el repo |
| Vocabulario cerrado con mensaje de error útil | Un `if valor not in [...]: raise ValueError(...)` genérico | El patrón de `__post_init__` + `ErrorModelo` con "Válidos: ..." (`modelo.py:109-113`, `:135-140`) | Mantiene consistencia de mensajes y de excepción capturable por `modelo.cargar()` |

**Idea clave:** esta fase no tiene ningún problema "difícil" de los que justifican una librería —
es disciplina de seguir el mismo patrón tres veces más. El riesgo no es la complejidad del código,
es la inconsistencia si alguien inventa una cuarta forma de hacer lo mismo.

## Rubro en puntos (REQ-38) — verificación de código

- `Rubro` (`modelo.py:158-165`) hoy solo tiene `id, etiqueta, porcentaje, detalle="", parciales=0`.
  **Confirmado por lectura directa**, no por el número de línea del CONTEXT.md (aunque coincide).
- Se construye con `Rubro(**r) for r in evaluacion.get("rubros", [])` en `desde_dict`
  (`modelo.py:276`). Cualquier clave del YAML que no sea un campo del dataclass produce
  `TypeError: __init__() got an unexpected keyword argument`, capturado en `modelo.cargar()`
  (`modelo.py:322-323`) y reempaquetado como `ErrorModelo`. Esto es lo que hoy pasaría si alguien
  escribe `unidad:`/`total:` sin haber tocado el dataclass — confirma por qué D-03/D-05 exigen
  `ErrorModelo`, no un fallo silencioso: **ya es el comportamiento por defecto**, la fase solo
  necesita que el mensaje sea legible en vez de un `TypeError` crudo.
- `generar.py:180` construye el bloque `evaluacion.rubros` del `MANIFIESTO.yaml` con
  `{"id": r.id, "porcentaje": r.porcentaje}` — una comprensión que **extrae solo esas dos claves**.
  Añadir `unidad`/`total` a `Rubro` **no cambia la forma de `MANIFIESTO.yaml`**, porque esta línea
  ya filtra explícitamente. Esto respalda a D-19 en su nota de que la "forma" del manifiesto no
  necesita entrar en la huella: para los rubros, ya está protegida por construcción.

## Componentes de meta (REQ-39) — verificación de código

- `Meta` (`modelo.py:116-133`) no tiene `componentes` hoy; se confirma que `Meta.valor` (línea 123)
  trae el comentario `# porcentaje de la calificación final` tal como cita el CONTEXT.md — ese
  comentario debería actualizarse al tocar la línea, porque D-02 ya no es cierto literalmente (la
  unidad la hereda del rubro, puede ser puntos).
- `_construir_meta` (`modelo.py:241-250`) ya tiene el patrón exacto a replicar (ver Patrón 2
  arriba), incluida la rama de forma corta para evidencias que D-09 pide reusar.
- `grafo.py:295-322` construye nodos de evidencia y criterio con claves
  `evidencia:{ciclo}:{clave}:{m.id}:{i}` y `criterio:{ciclo}:{clave}:{m.id}:{i}` — **ninguno de
  estos recorre `componentes`**, así que D-10 (el componente no entra al grafo) se cumple por
  omisión: basta con **no** añadir un bucle nuevo sobre `m.componentes` en `grafo.py`. No hace
  falta ningún cambio defensivo ahí.
- `render_docx.py:283-284` (D-11) es la única línea de renderizado que cambia:
  ```python
  # Fuente: src/render_docx.py:283-284 — línea exacta que D-11 toca
  _celda(tr, 5 if dividida else 4,
         ", ".join(e.nombre for e in meta.evidencias) if ultima else "")
  ```
  pasa a incluir también las evidencias de `meta.componentes` (cada `Componente.evidencia`, si
  existe). Un curso sin `componentes:` produce la misma lista vacía de siempre → mismo texto, honra
  REQ-48. Las líneas 286 y 408 (`f"{meta.valor:g}%"`) **no se tocan** — confirmado, pertenecen a la
  Fase 13.

## Auditoría de suposiciones sobre ids de meta (REQ-42 / D-12, D-13)

Se hizo un grep dirigido a los cuatro patrones que pide el CONTEXT.md: ordenar, deducir semántica
del id, usarlo como clave, o construir rutas/nombres a partir de él. Resultado por archivo:

| Archivo | Patrón buscado | Hallazgo |
|---|---|---|
| Todo `src/` | `.sort(`, `sorted(` sobre `curso.metas` o `m` | **Ninguno.** El único `sorted()` de todo el árbol relevante es `export_pdf.py:90`, que ordena nombres de archivo `.docx` en disco, no metas. |
| Todo `src/` | `min(`/`max(` sobre metas | Ninguno encontrado; `render_docx.py:277` usa `min(meta.semanas)` — es sobre semanas, no sobre ids. |
| Todo `src/` | `.id.split`, `startswith`, comparación con `"0"`/`.1"` | **Ninguno.** |
| `src/validar.py:394` | Distinción del encuadre | **Confirmado: usa `m.tipo not in ("encuadre", "cierre")`, no `m.id`.** Es dentro de `regla_8` (IEDI 1.5), no de R1/R2 como podría sugerir una lectura superficial del roadmap. |
| `src/modelo.py:231` | `metas_de(unidad)` | `return [m for m in self.metas if m.unidad == unidad]` — filtra por campo `unidad`, preserva el orden de `self.metas` (list comprehension no reordena). Confirma D-12: el orden declarado en YAML se conserva porque `yaml.safe_load` preserva orden de listas y nada lo reordena después. |
| `src/grafo.py:296-322` | Uso del id como clave | `f"meta:{ciclo}:{clave}:{m.id}"`, `f"evidencia:...:{m.id}:{i}"`, `f"criterio:...:{m.id}:{i}"` — el id se usa como **parte de una clave de nodo**, no para deducir semántica. Esto es exactamente por lo que **D-17 importa**: dos metas con el mismo id producirían la misma clave de nodo y una pisaría a la otra en el grafo silenciosamente. Confirmado empíricamente al leer el diccionario de nodos de `Grafo` (`g.nodo()` sobrescribe si la clave ya existe — no se verificó el cuerpo exacto de `g.nodo()`, pero la construcción de la clave con el id crudo es suficiente para el riesgo). |

**Veredicto: la auditoría confirma D-12 y D-13 sin hallazgos nuevos.** No hay ninguna otra
suposición sobre el id de una meta en `src/`. El plan puede fijar esto con una prueba (D-12/D-13) en
vez de tener que corregir código.

## Extracción determinista de texto de un `.docx` (D-19)

**Verificado empíricamente contra un documento real** (`cursos/2026-2/39056-big-data/salida/
DI-2026-2-39056-961.docx`, generado con `python-docx` 1.2.0, 470 párrafos, 1 tabla de 39×7,
sin tablas anidadas, sin contenido en encabezado/pie):

1. **`document.paragraphs` y `document.tables` NO están en orden del documento.** Son listas
   separadas. El orden real está en `document.element.body`, cuyos hijos directos son `<w:p>`,
   `<w:tbl>` y `<w:sectPr>` (verificado: 472 hijos, `tbl` en la posición 65). La receta correcta
   recorre `document.element.body.iterchildren()` y despacha por `tag`.

2. **Las celdas fusionadas verticalmente (`vMerge`) se duplican al leerlas con la API de alto
   nivel.** Prueba directa: `tabla.rows[4].cells[0].text` devuelve el mismo texto que
   `tabla.rows[3].cells[0].text` ("Meta 0. Encuadre…") aunque la fila 4 es la subfila virtual de la
   misma meta. Inspeccionando el XML crudo de esa celda (`tr.tc_lst[0]`), se confirmó que tiene
   `<w:tcPr><w:vMerge/></w:tcPr>` y **cero** elementos `<w:t>` — el texto que python-docx devuelve
   es resuelto/heredado de la celda de origen del merge, no está en el XML de esa celda. Es
   determinista (no varía entre corridas), pero es una duplicación artificial de la API, no del
   documento. **Recomendación: no usar `row.cells[i].text` para la huella.** Recorrer
   `tabla._tbl.tr_lst` y, por cada `tr`, sus `tc_lst` crudos, extrayendo solo los `<w:t>` que
   realmente están dentro de cada `<w:tc>` con `tc.iter(qn("w:t"))`. Esto da texto vacío en las
   celdas de continuación — más fiel al documento real y sin el efecto de duplicación a explicar.
   No hay tablas anidadas en los documentos de control hoy, pero si aparecieran, este recorrido
   crudo tampoco las perdería (a diferencia de `_Cell.text`, que solo concatena los párrafos
   propios de la celda e ignora tablas anidadas dentro de ella).
3. **Encabezados y pies de página están vacíos hoy** (`sections[0].header/footer` con un párrafo
   vacío cada uno) — el renderizador no los usa. Incluirlos en la extracción es gratis (una cadena
   vacía más) y deja el instrumento preparado si algún día se usan; omitirlos también sería
   correcto hoy. Se recomienda incluirlos por robustez, con un comentario explicando que hoy no
   aportan nada.

**Receta concreta recomendada:**
```python
# Diseño propuesto para src/huella.py — no verificado contra Context7 (no aplica: es
# manipulación directa de OOXML con python-docx, ya usada así en render_docx.py)
from docx import Document
from docx.oxml.ns import qn

def _texto_de(elemento) -> str:
    """Todo el texto (`<w:t>`) dentro de un elemento OOXML, en orden de aparición."""
    return "".join(t.text or "" for t in elemento.iter(qn("w:t")))

def extraer_texto(ruta_docx) -> str:
    doc = Document(ruta_docx)
    bloques = []
    for sec in doc.sections:
        for p in sec.header.paragraphs:
            if p.text.strip():
                bloques.append(p.text)
    for hijo in doc.element.body.iterchildren():
        tag = hijo.tag.rsplit("}", 1)[-1]
        if tag == "p":
            bloques.append(_texto_de(hijo))
        elif tag == "tbl":
            for tr in hijo.iter(qn("w:tr")):
                celdas = [_texto_de(tc) for tc in tr.findall(qn("w:tc"))]
                bloques.append(" | ".join(celdas))
    for sec in doc.sections:
        for p in sec.footer.paragraphs:
            if p.text.strip():
                bloques.append(p.text)
    return "\n".join(bloques)
```
Esto es determinista entre corridas (mismo `curso.yaml` + mismo commit → mismo texto), no depende
de metadatos del zip del `.docx` (D-19 ya descarta hashear el binario por eso), y no arrastra el
efecto de duplicación de `row.cells`.

## Formato de `pruebas/huellas.yaml` (D-20)

`generar.escribir_manifiesto` y `plantillas.guardar` usan el mismo estilo de dump —
`yaml.safe_dump(cuerpo, allow_unicode=True, sort_keys=False, default_flow_style=False)`— y ambos
antecede el cuerpo con una cabecera en comentarios que dice "no lo edites a mano" y qué comando
lo regenera. `src/huella.py` debería seguir exactamente ese molde para no introducir un cuarto
estilo de YAML en el repo.

Identificación de un documento: `ciclo` + `clave` + `grupo` (los mismos tres campos que ya usa
`Curso.nombre_archivo(grupo, ext)` para nombrar el `.docx`/`.pdf`). Propuesta de disposición,
consistente con la especificación de la sección `<additional_context>` (entrada por curso+grupo,
con `texto_docx` e `informe`):

```yaml
# pruebas/huellas.yaml — registro de huellas de no contaminación (REQ-48).
# Lo escribe `python src/huella.py registrar`: no lo edites a mano. Compáralo con
# `python src/huella.py verificar` antes de cada cierre de fase.
documentos:
  "2026-2:39056:961":
    ciclo: "2026-2"
    clave: "39056"
    grupo: "961"
    texto_docx: 8f14e45fceea167a...   # sha256 del texto extraído (ver extraer_texto)
    informe: 2c624232cdd221771...     # sha256 de informe.texto()
    registrado: "2026-08-04"
  "2026-2:39056:962":
    ...
  "2026-2:39062:971":
    ...
  "2026-2:39062:972":
    ...
```
La clave compuesta `"{ciclo}:{clave}:{grupo}"` como string es más simple de comparar en `git diff`
que un mapa anidado de tres niveles, y sigue el mismo espíritu de claves compuestas que ya usa
`grafo.py` (`f"meta:{ciclo}:{clave}:{id}"`).

**Nota importante para el plan:** el `informe.texto()` de `validar.validar()` es **por curso**, no
por grupo (incluye "grupos 961, 962" en la cabecera pero es un solo texto para ambos). Si se guarda
una entrada por curso+grupo, el campo `informe` tendrá el **mismo hash repetido** en las entradas de
961 y 962 de un mismo curso. Es correcto y esperado, no un bug — pero el planeador debe decidir
explícitamente si prefiere una entrada por curso (con lista de grupos) en vez de una por
curso+grupo, para no duplicar el campo `informe` sin necesidad. La especificación del
`<additional_context>` pide "entrada por curso+grupo", así que esta nota queda como aclaración, no
como objeción.

## Riesgo de la generación dentro de `huella.py`

1. **Genera sobre `cursos/…/salida/` real**, no un directorio temporal — es lo que hace
   `generar.paquete()` hoy y es deseable: es la misma ruta que produciría `/di-nuevo`, así que la
   huella mide exactamente lo que un profesor recibiría. `cursos/**/salida/` está en `.gitignore`
   `[VERIFIED: git ls-files]`, así que los `.docx` generados **no ensucian `git status`**.
2. **`MANIFIESTO.yaml` SÍ está versionado** (`git ls-files cursos/2026-2/39056-big-data/` lo
   confirma) y `generar.paquete()` lo **reescribe en cada corrida** con un `generado:` (timestamp) y
   `commit:` (con sufijo `-sucio` si el árbol tiene cambios sin commitear) nuevos —
   `generar.py:294-298`. **Esto significa que correr `huella verificar` o `huella registrar` deja
   `MANIFIESTO.yaml` de 39056 y 39062 modificado en `git status`**, aunque el documento y el informe
   no hayan cambiado en absoluto. No es un riesgo nuevo introducido por esta fase — ya ocurre hoy
   cada vez que alguien corre `python src/generar.py` a mano — pero el plan debe decidir
   explícitamente qué hacer con ese diff después de `huella verificar` (¿se descarta con
   `git checkout` los MANIFIESTOs de control, o se acepta y se commitea junto con el resto de la
   fase?). Queda como pregunta abierta abajo.
3. **`plantillas.copia_de_trabajo()` verifica el sha256 antes de copiar** en cada llamada
   (`plantillas.py:268-286`) — generar dos cursos seguidos (39056 y 39062) implica dos
   verificaciones de sha256 de las plantillas, no una sola compartida. Es rápido (sha256 de un
   `.docx` de pocos MB) y no representa un riesgo de tiempo real.
4. **Tiempo:** con `pdf=False` no hay export a Word COM (el paso más lento del pipeline, según
   `AGENTS.md` §Word COM — abre y cierra la aplicación por cada documento). Generar los 4 `.docx`
   de control (39056×2, 39062×2) debería tomar segundos, no minutos. No se midió con cronómetro en
   esta investigación porque no se ejecutó `huella.py` (no existe aún); es una proyección razonable
   basada en que el pipeline completo con PDF de un curso ya corrido históricamente (ver
   `STATE.md`) no reporta tiempos largos.
5. **Basura en el repo:** ninguna, dado el `.gitignore` de `salida/`. El único archivo que puede
   quedar "sucio" es `MANIFIESTO.yaml` de los cursos de control (punto 2).

## La suite de pruebas actual

`python -X utf8 -m unittest discover -s pruebas` → **179 pruebas, todas pasan** `[VERIFIED:
ejecutado en esta sesión]`, confirmando el número que cita el ROADMAP.md.

Archivos en `pruebas/`: `test_calendario.py`, `test_export_pdf.py`, `test_generar.py`,
`test_grafo.py`, `test_ingesta_pua.py`, `test_plantillas.py`, `test_render_docx.py`,
`test_validar.py`. **No existe `test_modelo.py` hoy** — las pruebas de esquema/carga viven
implícitamente dentro de `test_validar.py` (que construye cursos válidos con un diccionario
`CURSO_VALIDO` y los pasa por `modelo.desde_dict`).

Convención confirmada: `unittest.TestCase`, nombres de método en español y descriptivos
(`test_detecta_el_defecto_del_ejemplo_961`, `test_registrar_dos_veces_no_cambia_nada`), docstrings
que explican **qué defiende** la prueba, no solo qué hace. `test_plantillas.py` usa una clase base
`EnDirectorioTemporal` que redirige `plantillas.DIR/REGISTRO/HISTORICO` a un `tempfile.mkdtemp()` en
`setUp` y restaura en `tearDown` — **este es el patrón a replicar para probar `huella.py`** sin
tocar `pruebas/huellas.yaml` de verdad durante los tests unitarios (si se decide probar la
lectura/escritura del registro con pruebas unitarias rápidas, separadas de la generación completa
que D-18 aparta del ciclo de pruebas).

`test_detecta_el_defecto_del_ejemplo_961` (`pruebas/test_validar.py:169-178`) construye un curso
donde todas las metas se imputan al mismo rubro y verifica que R2 reporte el error con "Proyecto
final" y "Exámenes" en el mensaje. **No usa `Meta.id` de ninguna forma sensible al valor** — solo
copia `CURSO_VALIDO["metas"]` y cambia `rubro`. Añadir `componentes`, o cambiar el default de
`unidad`/`total` en `Rubro`, no debería afectar esta prueba **siempre que los defaults no cambien
el comportamiento de un rubro que no declara `unidad`** (que es justamente D-01/D-05). No hace
falta tocarla.

Dónde encajarían las pruebas nuevas: un `pruebas/test_modelo.py` nuevo (carga de rubro en puntos,
`ErrorModelo` si falta `total`, componente con vocabulario cerrado, orden de metas con ids libres,
D-17 vía `test_validar.py` porque es una regla de R2) es más limpio que sobrecargar
`test_validar.py`, que ya tiene 200+ líneas centradas en las 8 reglas. `src/huella.py` en sí **no
lleva pruebas dentro de `pruebas/`** por decisión D-18 — a lo sumo, una prueba unitaria rápida de
`extraer_texto()` contra un `.docx` sintético de 2-3 párrafos armado en memoria (sin pasar por
`generar.paquete`), si el plan decide que vale la pena aislar esa función.

## Riesgo del orden obligatorio D-15 — barrido de menciones a "Meta 0" de Big Data

Búsqueda dirigida en todo el árbol (excluyendo binarios `.docx`/`.pdf`, que se regeneran y no se
pueden grepear):

| Archivo | Menciona "Meta 0" / `id: "0"` | Acción cuando se renombre a `1.0` |
|---|---|---|
| `cursos/2026-2/39056-big-data/curso.yaml:209` | `id: "0"` (declaración real) | Se edita: es el cambio mismo de D-14 |
| `grafo/grafo.json` (líneas 1464, 1672) | `"etiqueta": "Meta 0. Encuadre del curso."` ×2 | **Se regenera** con `python src/grafo.py` — es un artefacto versionado en git (`git ls-files grafo/` lo confirma: `grafo.json`, `index.html`, `AUDITORIA.md` están trackeados). El plan debe incluir `python src/grafo.py` como paso, o el `grafo.json` commiteado quedará con el texto viejo tras el rename, violando en la letra (aunque no en el espíritu) la promesa de D-10 de que "`grafo/` conserva su forma exacta" — su *forma* (esquema de nodos/aristas) no cambia, pero su *contenido* sí debe reflejar el rename. |
| `.planning/phases/09-valor-de-una-meta/09-CONTEXT.md` | Menciona "Meta 0" como texto descriptivo | No es código ni documento generado — no requiere acción |
| `puas/md/39056-big-data.md` | No contiene "Meta 0" — el PUA no habla de metas del DI, solo de temas/prácticas del programa oficial | Ninguna acción — confirmado, no hay mención |
| `MANIFIESTO.yaml` de 39056 | No contiene "Meta 0" literal (solo `sha256` del curso.yaml, que sí cambiará de valor) | Se regenera junto con la generación normal — su *forma* no cambia (ver nota D-19 sobre `generar.py:180`) |
| `.docx`/`.pdf` en `cursos/2026-2/39056-big-data/salida/` | Contienen "Meta 0." en texto (verificado leyendo el `.docx` real) | Se regeneran con `generar.py` — es lo que la huella debe detectar cambiando (paso 5 de D-15) |

**Hallazgo nuevo relevante:** `grafo/grafo.json` (y por construcción `grafo/index.html` y
`grafo/AUDITORIA.md`, que `python src/grafo.py` reescribe siempre los tres juntos) están
**versionados en git** y contienen el texto "Meta 0. Encuadre del curso." dos veces. El plan de
D-15 necesita un paso explícito de `python src/grafo.py` después del rename (paso 4 o 5 de la
secuencia), o el criterio de éxito 3 del ROADMAP ("renombrar el encuadre 0 de Big Data a 1.0 deja
el documento igual salvo esa cadena") queda satisfecho para el `.docx` pero no para el grafo
commiteado, que seguiría diciendo "Meta 0" en git aunque el curso.yaml ya diga "1.0".

## Validation Architecture

`workflow.nyquist_validation: true` en `.planning/config.json` `[VERIFIED: leído directamente]` —
sección obligatoria.

### Marco de pruebas

| Propiedad | Valor |
|---|---|
| Framework | `unittest` (stdlib), sin config file — se descubre con `discover` |
| Config | ninguno — convención de directorio `pruebas/`, sin `pytest.ini` ni `setup.cfg` |
| Comando rápido | `python -X utf8 -m unittest pruebas.test_modelo -v` (o el archivo que se cree) |
| Comando completo | `python -X utf8 -m unittest discover -s pruebas` |

### Mapa de requisitos → pruebas

| Req / Criterio | Comportamiento | Tipo | Comando automatizado | ¿Archivo existe? |
|---|---|---|---|---|
| REQ-38 / criterio 1 | Rubro en puntos (`unidad: puntos`, `total: 150`) carga sin `ErrorModelo`; junto a un rubro en porcentaje en el mismo curso | unitario | `python -X utf8 -m unittest pruebas.test_modelo.RubroEnPuntos -v` | ❌ Wave 0 — crear `pruebas/test_modelo.py` |
| REQ-38 (D-03/D-05) | Rubro con `unidad` desconocida, o `unidad: puntos` sin `total`, es `ErrorModelo` | unitario | idem | ❌ Wave 0 |
| REQ-39 / criterio 2 | Meta con `componentes:` sigue siendo una sola meta con una sola semana (`len(curso.metas)` y `m.semanas` no cambian) | unitario | `python -X utf8 -m unittest pruebas.test_modelo.ComponentesDeMeta -v` | ❌ Wave 0 |
| REQ-39 (D-08) | `tipo` de componente fuera de `TIPOS_COMPONENTE` → `ErrorModelo` | unitario | idem | ❌ Wave 0 |
| REQ-39 (D-11) | Curso sin `componentes:` no cambia la columna de evidencias de la Sección 2 (regresión de `test_render_docx.py`) | unitario | `python -X utf8 -m unittest pruebas.test_render_docx -v` | ✅ ampliar archivo existente |
| REQ-42 / criterio 3 | Metas con id `1.0`, `2.0`, `6.0` cargan y conservan el orden declarado | unitario | `python -X utf8 -m unittest pruebas.test_modelo.IdentificadoresLibres -v` | ❌ Wave 0 |
| REQ-42 (D-17) | Dos metas con el mismo id → error de R2 (no `ErrorModelo`) | unitario | `python -X utf8 -m unittest pruebas.test_validar -v` | ✅ ampliar `test_validar.py` |
| REQ-42 (D-12/D-13) | Ninguna función de `src/` ordena/deduce semántica del id (fijado como regresión, no como código nuevo) | unitario | prueba dedicada que audite ausencia de `sorted()`/`.sort` — o, más simple, una prueba funcional que cargue un curso con ids fuera de orden numérico y verifique que `curso.metas` preserva el orden del YAML | ❌ Wave 0 |
| Criterio 4 (instrumento REQ-48) | `huella verificar` corre en verde contra 39056 y 39062 recién generados | integración / manual | `python src/huella.py verificar` (no vive en `pruebas/`, D-18) | N/A — es deliberadamente manual, ver nota abajo |
| Criterio 5 | Las 179 pruebas anteriores siguen pasando, más las nuevas | integración | `python -X utf8 -m unittest discover -s pruebas` | ✅ ya existe, corrido y confirmado en verde (179/179) |
| D-15 (rename Big Data) | `texto_a.replace("Meta 0.", "Meta 1.0.") == texto_b` | integración | prueba dedicada que use `huella.extraer_texto()` sobre el `.docx` antes/después — o una prueba manual con el snippet del CONTEXT.md, corrida a mano durante el paso 5 de D-15 (no automatizable sin generar dos veces el documento completo) | ❌ Wave 0 (si se automatiza) o manual (si no) |

### Frecuencia de muestreo

- **Por commit de tarea:** `python -X utf8 -m unittest discover -s pruebas` (13 segundos hoy con
  179 pruebas — verificado; añadir ~10-20 pruebas de modelo no debería subir sensiblemente el
  tiempo, porque no tocan disco ni red).
- **Por cierre de fase:** además de la suite completa, correr `python src/huella.py verificar`
  (fuera del ciclo de pruebas, a mano — D-18) y `git diff` sobre los MANIFIESTOs de control si
  quedaron modificados (ver "Riesgo de la generación").
- **Puerta de fase:** suite completa en verde + `huella verificar` en verde + revisión a ojo de
  `grafo/AUDITORIA.md` si se corrió `python src/grafo.py` (D-15 lo requiere).

### Huecos de Wave 0

- [ ] `pruebas/test_modelo.py` — nuevo archivo. Cubre REQ-38 (rubro en puntos, `ErrorModelo` en sus
  dos variantes), REQ-39 (componentes, vocabulario cerrado, no-contaminación de
  `len(metas)`/`semanas`), REQ-42 (ids libres, orden preservado).
- [ ] Ampliación de `pruebas/test_validar.py` — una prueba para D-17 (dos metas con mismo id → error
  R2) y opcionalmente una para D-12/D-13 (ausencia de suposiciones sobre orden/semántica del id).
- [ ] Ampliación de `pruebas/test_render_docx.py` — una prueba de regresión para D-11 (evidencia de
  componente se concatena; su ausencia no cambia nada).
- [ ] `src/huella.py` en sí **no** necesita un archivo de prueba dentro de `pruebas/` por D-18. Si
  el plan quiere una prueba rápida y aislada de `extraer_texto()` contra un `.docx` sintético
  armado en memoria (sin pasar por `generar.paquete`), puede vivir en `pruebas/test_huella.py`
  como excepción acotada — pero **nunca** una prueba que invoque `generar.paquete()` completo
  dentro de la suite rápida, porque D-18 lo prohíbe explícitamente ("no debe colgarse del ciclo de
  las pruebas unitarias, que hoy son rápidas").

## Security Domain

Omitido: `security_enforcement: false` en `.planning/config.json` `[VERIFIED: leído
directamente]`. No aplica — esta fase no toca autenticación, sesiones, ni entrada de usuario
expuesta a red; es un cambio de esquema de datos internos y un instrumento de línea de comandos
local.

## Assumptions Log

| # | Afirmación | Sección | Riesgo si es incorrecta |
|---|---|---|---|
| A1 | `Componente.tipo` debería tener default `"actividad"` cuando no se declara | Patrón 2 (Componentes de meta) | Bajo — D-06 no especifica un default explícito para `tipo`; si el planeador prefiere que sea obligatorio (sin default), es un cambio de una línea |
| A2 | El nombre de la clave compuesta de `pruebas/huellas.yaml` debería ser `"{ciclo}:{clave}:{grupo}"` como string plano | Formato de `pruebas/huellas.yaml` | Bajo — es una propuesta de "Criterio de Claude" (D-20 delega la disposición interna); cualquier esquema equivalente (mapa anidado) sirve igual, solo cambia la ergonomía del `git diff` |
| A3 | El tiempo de generación de los 4 documentos de control con `pdf=False` es de segundos, no minutos | Riesgo de la generación (punto 4) | Medio — no se cronometró en esta sesión porque `huella.py` no existe aún; si resultara lento, el plan debería considerarlo al decidir la frecuencia de `huella verificar` |
| A4 | Un `Componente` sin `tipo` declarado explícitamente en el YAML debería fallar (obligatorio) en vez de tomar un default silencioso, para evitar que un typo pase inadvertido igual que ya se cuidó con `TIPOS_COMPONENTE` | Patrón 2 | Bajo-medio — si el default silencioso "actividad" oculta un typo real, contradice el espíritu de D-08 ("un typo… no se traduzca en un examen que nadie cuenta"); el planeador debería decidir si `tipo` es obligatorio sin default |

**Nota:** ningún supuesto de esta tabla afecta el esquema de `curso.yaml` ya cerrado por D-01 a
D-22; son detalles de implementación explícitamente delegados a "Criterio de Claude" en el
CONTEXT.md.

## Open Questions

1. **¿Qué hacer con `MANIFIESTO.yaml` de los cursos de control después de `huella verificar`?**
   - Qué sabemos: `generar.paquete()` siempre reescribe `generado:`/`commit:`, y esos dos archivos
     están versionados en git. Correr la verificación deja un diff aunque nada haya cambiado
     semánticamente.
   - Qué no está claro: si el plan debe incluir un paso de `git checkout` sobre esos dos
     MANIFIESTOs después de cada `huella verificar`, o si se acepta el ruido y se commitea junto
     con el resto (como ya ocurre hoy cada vez que se regenera un curso, según el historial de
     `STATE.md`).
   - Recomendación: que el plan decida explícitamente una de las dos opciones y la documente en el
     propio `src/huella.py` (mensaje de salida) para que quien lo corra sepa qué esperar en
     `git status`.

2. **¿El paso de rename (D-15, paso 4) debe incluir `python src/grafo.py`?**
   - Qué sabemos: `grafo/grafo.json` está versionado y contiene "Meta 0. Encuadre del curso." dos
     veces; el criterio de éxito 3 del ROADMAP habla del "documento", pero D-10 también habla de la
     "forma" del grafo.
   - Qué no está claro: si regenerar el grafo es parte del criterio de cierre de la Fase 9 o si se
     deja para cuando el grafo se toque explícitamente (ninguna fase de la v2.0 lo tiene como
     entregable propio).
   - Recomendación: incluir `python src/grafo.py` como paso explícito del rename (D-15), para que
     el repositorio no quede con un `grafo.json` commiteado que menciona una meta que ya no existe
     con ese id.

3. **¿Los cuatro documentos de control son 3 (39056-961, 39056-962, 39062-un-solo-grupo) o 4
   (39056-961, 39056-962, 39062-971, 39062-972)?**
   - Qué sabemos: D-22 dice "39056 (grupos 961 y 962) y 39062 (Patrones)", sin precisar grupos para
     39062. El ejemplo de salida en `<specifics>` del CONTEXT.md muestra literalmente
     "39062 grupo 1", que **no corresponde a ningún grupo real** — `39062` declara los grupos
     `971` y `972` `[VERIFIED: cursos/2026-2/39062-patrones-de-comportamiento/curso.yaml:182-186]`.
   - Qué no está claro: si el ejemplo de salida es solo ilustrativo (y en la práctica son 4
     documentos, uno por cada grupo real de cada curso de control) o si deliberadamente solo se
     vigila un grupo representativo de 39062.
   - Recomendación: tratar el ejemplo del CONTEXT.md como ilustrativo y vigilar los 4 documentos
     reales (961, 962, 971, 972) — es más protección por el mismo costo, y evita que un cambio que
     solo afecte al grupo 972 pase inadvertido.

4. **¿`Componente.tipo` es obligatorio o tiene default?** Ver Assumption A4 — D-08 no lo especifica
   explícitamente y el estilo de "vocabulario cerrado" del resto del modelo (`Sesion.ambiente`,
   `Meta.tipo`) no usa default salvo `Meta.tipo = "aprendizaje"`. El planeador debe decidir con el
   mismo criterio que D-08 ya razonó para el resto del vocabulario.

## Sources

### Primaria (confianza ALTA — leído/ejecutado directamente en esta sesión)

- `src/modelo.py` — dataclasses `Evidencia`, `Sesion`, `Meta`, `Rubro`, `Curso`; `_construir_meta`,
  `_construir_grupo`, `desde_dict`, `cargar` — líneas citadas verificadas una a una.
- `src/validar.py` — las 8 reglas completas, `Counter` en R1, la línea 394 de `regla_8`.
- `src/render_docx.py` — `_seccion_2`, `_filas_de_meta` (líneas 260-288), bloque de Sección 3
  (líneas 380-411).
- `src/plantillas.py` — módulo completo (CLI, `sha256`, `cargar`/`guardar`, `copia_de_trabajo`).
- `src/generar.py` — módulo completo (`paquete`, `manifiesto`, `escribir_manifiesto`).
- `src/grafo.py` (líneas 280-322) — construcción de nodos de meta/evidencia/criterio.
- `src/comprobar.py` — módulo completo, ejecutado con `python -X utf8 src/comprobar.py`.
- `python -X utf8 -m unittest discover -s pruebas` — ejecutado, 179/179 en verde.
- `pip show python-docx PyYAML` — versiones 1.2.0 y 6.0.3 confirmadas.
- `python --version` — 3.11.9 confirmado.
- Inspección directa con `python-docx` de
  `cursos/2026-2/39056-big-data/salida/DI-2026-2-39056-961.docx` — orden de `document.element.body`,
  comportamiento de `row.cells` sobre celdas `vMerge`, XML crudo de la celda fusionada, contenido
  de encabezado/pie.
- `grep`/`git ls-files`/`git status` sobre todo `src/`, `grafo/`, `cursos/` y `.gitignore` — auditoría
  de ids de meta y de menciones a "Meta 0".
- `.planning/config.json` — `nyquist_validation: true`, `security_enforcement: false`.
- `.planning/phases/09-valor-de-una-meta/09-CONTEXT.md`, `.planning/REQUIREMENTS.md`,
  `.planning/ROADMAP.md`, `.planning/STATE.md`, `AGENTS.md`, `CLAUDE.md`,
  `.claude/skills/di-validar/SKILL.md`.

### Secundaria / Terciaria

Ninguna. Esta fase no requirió WebSearch, WebFetch ni Context7: no hay librería externa nueva ni
comportamiento de framework que verificar contra documentación en línea — todo lo relevante está en
el propio repositorio y se verificó por lectura y ejecución directa.

## Metadata

**Desglose de confianza:**
- Standard stack: ALTA — no hay dependencias nuevas; versiones confirmadas con `pip show`.
- Arquitectura (patrones de modelo/CLI): ALTA — cada patrón citado tiene su línea de origen leída
  directamente, no recordada.
- Extracción de `.docx` (D-19): ALTA — comportamiento de `vMerge` verificado empíricamente contra
  un documento real, no asumido de memoria de entrenamiento sobre python-docx.
- Auditoría de ids de meta (REQ-42): ALTA — grep exhaustivo ejecutado, cero hallazgos nuevos frente
  a lo que CONTEXT.md ya afirmaba.
- Riesgo de MANIFIESTO/grafo versionados (D-15): ALTA — confirmado con `git ls-files` y `grep`
  directo sobre el JSON commiteado.

**Fecha de investigación:** 2026-08-04
**Válida hasta:** sin fecha de caducidad práctica — no depende de versiones de librerías externas
que puedan cambiar; depende del estado del propio repositorio, que solo cambia cuando esta fase (u
otra) lo modifique. Si la Fase 9 tarda más de unas semanas en planearse/ejecutarse, vale la pena
repetir `python -X utf8 -m unittest discover -s pruebas` y `git status` antes de arrancar, para
confirmar que el número de pruebas y el estado del árbol no cambiaron entre tanto.
