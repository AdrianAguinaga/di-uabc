# Fase 9: El valor de una meta deja de ser un porcentaje - Mapa de patrones

**Mapeado:** 2026-08-05
**Archivos analizados:** 9 (5 nuevos, 4 modificados)
**Análogos encontrados:** 9 / 9

## Clasificación de archivos

| Archivo nuevo/modificado | Rol | Flujo de datos | Análogo más cercano | Calidad del match |
|---|---|---|---|---|
| `src/modelo.py` (`Rubro`, `Meta`, `Componente`, `_construir_meta`, `desde_dict`) | model | transform (YAML → dataclass) | el propio `src/modelo.py` (`Evidencia`, `Sesion.__post_init__`) | exacto — mismo archivo, mismo patrón ya usado 2 veces |
| `src/huella.py` | utility / CLI | batch (generar → hashear → comparar) | `src/plantillas.py` (CLI con subcomandos) | exacto |
| `pruebas/huellas.yaml` | config (dato versionado) | file-I/O (dump YAML) | `plantillas/REGISTRO.yaml` (vía `plantillas.guardar()`) + `MANIFIESTO.yaml` (vía `generar.escribir_manifiesto()`) | exacto |
| `pruebas/test_modelo.py` | test | CRUD (carga de esquema) | `pruebas/test_validar.py` (estructura `unittest.TestCase`, `CURSO_VALIDO`) | exacto |
| `pruebas/test_huella.py` | test | transform (extracción de texto) | `pruebas/test_plantillas.py` (`EnDirectorioTemporal`) + helper `texto()` de `pruebas/test_render_docx.py` | exacto |
| `src/validar.py` (D-17, nueva comprobación en R2) | validation rule | CRUD (conteo/agregación) | el propio `src/validar.py:141` (`Counter` de rubros duplicados en R1) | exacto — mismo archivo, mismo patrón |
| `src/render_docx.py:283-284` (D-11) | renderer | transform (concatenación de texto) | la propia línea, extendida | exacto — una línea, no hace falta análogo externo |
| `cursos/2026-2/39056-big-data/curso.yaml` (D-14) | data (contrato de curso) | CRUD (edición de una clave) | n/a — edición de dato, no de código | n/a |

## Asignaciones de patrón

### `src/modelo.py` — campos nuevos en `Rubro`, `Meta.componentes`, dataclass `Componente`

**Análogo:** el propio `src/modelo.py` — `Evidencia` (líneas 91-95), `Sesion.__post_init__` (109-113),
`Meta.__post_init__` (135-142), `_construir_meta` (241-250), `desde_dict` (260-286).

**Estado actual literal de `Rubro`** (`modelo.py:158-165`, a extender, no reemplazar):
```python
@dataclass
class Rubro:
    id: str
    etiqueta: str
    porcentaje: float
    detalle: str = ""
    parciales: int = 0
```

**Estado actual literal de `Evidencia`** (`modelo.py:91-95` — molde de campo opcional con default,
y molde exacto para que `Componente.evidencia` acepte la forma corta):
```python
@dataclass
class Evidencia:
    nombre: str
    tipo: str = ""
    recurso: str = ""  # p. ej. "M1.1_Mapa conceptual"
```

**Patrón de vocabulario cerrado en `__post_init__`, con mensaje "qué falta + válidos"**
(`modelo.py:109-113`, `Sesion.ambiente`):
```python
def __post_init__(self) -> None:
    if self.ambiente not in AMBIENTES:
        raise ErrorModelo(
            f"Ambiente inválido: {self.ambiente!r}. Válidos: {', '.join(AMBIENTES)}"
        )
```

**Mismo patrón en `Meta.__post_init__`** (`modelo.py:135-142` — dos validaciones en el mismo método,
la segunda con mensaje distinto, sin listar valores porque no es vocabulario cerrado):
```python
def __post_init__(self) -> None:
    if self.tipo not in TIPOS_META:
        raise ErrorModelo(
            f"Meta {self.id}: tipo inválido {self.tipo!r}. "
            f"Válidos: {', '.join(TIPOS_META)}"
        )
    if not self.semanas:
        raise ErrorModelo(f"Meta {self.id}: no tiene semanas asignadas.")
```

**Estilo exacto de los mensajes de `ErrorModelo` existentes en todo el módulo** (3 ejemplos
literales, para replicar el tono en los mensajes nuevos de D-03/D-05/D-08/D-26):
```python
# modelo.py:62 — Config.profesor(), lista lo disponible
disponibles = ", ".join(p["id"] for p in self.profesores["profesores"])
raise ErrorModelo(f"Profesor desconocido: {id_}. Disponibles: {disponibles}")

# modelo.py:72-74 — Config.plantilla(), dice qué es inválido y qué vale
raise ErrorModelo(
    f"Modalidad desconocida: {modalidad}. Válidas: {', '.join(MODALIDADES)}"
)

# modelo.py:80-84 — Config.articulo(), explica *por qué* es inválido, no solo que lo es
raise ErrorModelo(
    f"Cita legal inexistente: {cita}. "
    f"Ningún texto del documento puede citar un artículo que no esté "
    f"registrado en config/politicas.yaml."
)
```
El patrón: `f"{Sujeto} {identificador}: {qué está mal} {valor!r}. Válidos: {lista}"` o, cuando el
error es estructural (falta un campo, no un valor fuera de vocabulario), una frase que dice qué
falta y qué se esperaba en su lugar (ver el ejemplo de `Config.articulo`). Los mensajes nuevos de
D-03 (`unidad` inválida), D-05 (`total` faltante), D-08 (`tipo` de componente inválido) y D-26
(componente sin `tipo`) deben seguir esta forma literal — el borrador de RESEARCH.md ya la sigue:

```python
# RESEARCH.md — borrador ya alineado con el estilo, para copiar tal cual
raise ErrorModelo(
    f"Rubro {self.id}: unidad inválida {self.unidad!r}. "
    f"Válidas: {', '.join(UNIDADES_RUBRO)} (o ausente, para porcentaje)."
)
raise ErrorModelo(
    f"Rubro {self.id}: declara unidad «puntos» sin `total`. "
    f"Un rubro en puntos debe declarar su total (p. ej. `total: 150`)."
)
raise ErrorModelo(
    f"Componente «{self.etiqueta}»: tipo inválido {self.tipo!r}. "
    f"Válidos: {', '.join(TIPOS_COMPONENTE)}."
)
```

**Patrón 2 — lista de sub-objetos poppeada antes de `**kwargs`**, patrón exacto de
`_construir_meta` (`modelo.py:241-250`) a extender con `componentes`:
```python
def _construir_meta(d: dict) -> Meta:
    sesiones = [Sesion(**s) for s in d.pop("sesiones", [])]
    evidencias = [
        Evidencia(**e) if isinstance(e, dict) else Evidencia(nombre=e)
        for e in d.pop("evidencias", [])
    ]
    semanas = d.pop("semanas", None)
    if semanas is None and (s := d.pop("semana", None)) is not None:
        semanas = [s]
    return Meta(semanas=semanas or [], sesiones=sesiones, evidencias=evidencias, **d)
```
La rama `isinstance(e, dict)` (línea 244) es exactamente lo que D-09 pide reusar para que
`Componente.evidencia` acepte la forma corta (cadena en vez de mapa).

**Punto de integración — `desde_dict`** (`modelo.py:260-286`), donde `Rubro(**r)` (línea 276) y
`_construir_meta(dict(m))` (línea 275) construyen desde el YAML; cualquier clave nueva sin default
revienta con `TypeError`, capturado en `cargar()`:
```python
def cargar(ruta: Path | str) -> Curso:
    ...
    try:
        return desde_dict(datos)
    except KeyError as e:
        raise ErrorModelo(f"{ruta}: falta el campo obligatorio {e}") from e
    except TypeError as e:
        raise ErrorModelo(f"{ruta}: campo inesperado o faltante — {e}") from e
```

**Comentario a actualizar** — `Meta.valor` (`modelo.py:123`) trae hoy `# porcentaje de la
calificación final`; deja de ser literalmente cierto con D-02 (hereda la unidad de su rubro) y debe
reescribirse al tocar la línea.

---

### `src/huella.py` (CLI nuevo, batch)

**Análogo:** `src/plantillas.py` completo (CLI con subcomandos `registrar`/`verificar`).

**Molde exacto de `main()` con dispatch y códigos de salida** (`plantillas.py:303-337`):
```python
def main(argv: list[str]) -> int:
    orden = argv[1] if len(argv) > 1 else "verificar"
    try:
        if orden == "registrar":
            for a in registrar() or ["Nada que hacer: el registro ya estaba al día."]:
                print(a)
            _imprimir_registro()
        elif orden == "verificar":
            if problemas := verificar():
                for p in problemas:
                    print(f"✗ {p}", file=sys.stderr)
                return 1
            print("Las plantillas coinciden con su registro.")
            _imprimir_registro()
        else:
            print(f"Orden desconocida: {orden}", file=sys.stderr)
            return 2
    except ErrorPlantilla as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
```

**Utilidad de hash a reusar, no reimplementar** (`plantillas.py:55-60`):
```python
def sha256(ruta: Path) -> str:
    h = hashlib.sha256()
    with ruta.open("rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()
```
Para hashear texto en memoria (el `texto_docx`/`informe` de D-19) no se reusa esta función —
opera sobre `Path`, no sobre `str` — sino un one-liner nuevo: `hashlib.sha256(texto.encode("utf-8")).hexdigest()`.

**Patrón de excepción propia + captura en `main()`** (`plantillas.py:51-52`):
```python
class ErrorPlantilla(Exception):
    """La plantilla no está donde debe, o no es la que se registró."""
```
`huella.py` necesita su propia `ErrorHuella` con el mismo rol.

**Cómo `src/comprobar.py` redacta salida "qué falta y qué hacer"** (D-18 pide el mismo espíritu),
docstring del módulo y una línea del bucle de paquetes:
```python
# comprobar.py:1-9 — docstring del módulo, el espíritu a replicar
"""Comprueba que la máquina tiene todo lo que el generador necesita.
Existe para que montar el proyecto en otra computadora no acabe en un rastro de
excepciones. Cada comprobación dice qué falta y cómo instalarlo, no solo que falló.
"""

# comprobar.py:50-52 — mensaje concreto: qué falta + qué comando corre
except ImportError:
    _linea(False, paquete, f"falta — pip install {paquete}")
    faltan.append(paquete)
```
Y el mensaje real de `plantillas.verificar()` (`plantillas.py:251-257`) ya sigue exactamente este
espíritu — es el modelo más cercano para el mensaje de `huella verificar` cuando algo cambió:
```python
problemas.append(
    f"{mod}: el archivo cambió ({e.sha256[:12]} → {h[:12]}). "
    f"Alguien escribió sobre la plantilla. Restaura con "
    f"`git checkout plantillas/{e.archivo}` o registra el cambio con "
    f"`python src/plantillas.py actualizar {mod} <ruta>`."
)
```
`huella verificar` debe decir **qué documento** cambió y **qué mirar** (`git diff`), en esa misma
forma: `"{clave} grupo {grupo}: cambió ({hash_viejo} → {hash_nuevo}). Revisa con git diff ..."`.

**Cómo `src/generar.py` expone la generación de un curso (reusar, no reimplementar)** —
firma verificada (`generar.py:221-226`):
```python
def paquete(
    ruta_curso: Path | str,
    pdf: bool = True,
    traza=None,
    grupos: list[str] | None = None,
) -> Paquete:
```
`Paquete` (`generar.py:52-57`) expone `.archivos: list[Path]` — de ahí `huella.py` toma los `.docx`
generados para pasarlos a `extraer_texto()`, y `.informe: validar.Informe` — de ahí toma
`informe.texto()` para el hash del informe. Uso real ya existente de esta firma en pruebas
(`pruebas/test_generar.py:51-53`):
```python
cls.paquete = generar.paquete(
    cls.ruta, pdf=False, traza=lambda *a: cls.pasos.append(a)
)
```
`huella.py` debe llamar igual: `generar.paquete(ruta_curso, pdf=False, grupos=[...])` — nunca
reconstruir validar→renderizar a mano (anti-patrón explícito de RESEARCH.md).

**Riesgo a resolver en el CLI (D-23):** `generar.paquete()` reescribe `generado:`/`commit:` en
`MANIFIESTO.yaml` de los cursos de control en cada corrida. `huella verificar` debe restaurarlos
con `git checkout` sobre esos archivos al terminar, para quedar de solo lectura sobre el repo.

---

### `pruebas/huellas.yaml` (registro versionado nuevo)

**Análogo:** el dump de `plantillas.guardar()` (`plantillas.py:106-122`) y de
`generar.escribir_manifiesto()` (`generar.py:212-215`) — mismo estilo de YAML en todo el repo.

**Estilo de `dump` exacto a replicar** (`plantillas.py:121` / `generar.py:213`):
```python
texto = yaml.safe_dump(cuerpo, allow_unicode=True, sort_keys=False, default_flow_style=False)
```

**Patrón de cabecera en comentario "no lo edites a mano"** (`plantillas.py:40-48`, molde literal):
```python
CABECERA = (
    "# Registro de las plantillas de trabajo. Lo genera src/plantillas.py: no lo edites\n"
    "# a mano. El sha256 se verifica antes de cada renderizado; si no coincide, el\n"
    "# renderizado falla en vez de producir un documento de origen desconocido.\n"
    "#\n"
    "# Para cambiar una plantilla:\n"
    "#     python src/plantillas.py actualizar <modalidad> <ruta.docx> --version <ver>\n"
    "# La anterior no se pierde: se archiva en plantillas/historico/.\n"
)
...
REGISTRO.write_text(CABECERA + texto, encoding="utf-8")
```
`pruebas/huellas.yaml` necesita la misma cabecera, adaptada: qué comando lo regenera
(`huella registrar`) y qué comando lo compara (`huella verificar`).

**Patrón de "guardar ordenado, con default de campo opcional"** (`plantillas.py:106-120`, aplicable
a cómo `huella.py` serializa el diccionario de entradas):
```python
def guardar(entradas: dict[str, Entrada]) -> None:
    cuerpo = {
        "plantillas": {
            mod: {
                "archivo": e.archivo,
                ...
                **({"historial": e.historial} if e.historial else {}),
            }
            for mod, e in sorted(entradas.items())
        }
    }
    texto = yaml.safe_dump(cuerpo, allow_unicode=True, sort_keys=False, default_flow_style=False)
    REGISTRO.write_text(CABECERA + texto, encoding="utf-8")
```
`sorted(entradas.items())` asegura que el diff de `pruebas/huellas.yaml` sea estable entre
corridas — importante porque D-20 depende de que `git diff` sea legible.

---

### `pruebas/test_modelo.py` (nuevo)

**Análogo:** `pruebas/test_validar.py` completo — estructura de clase, `CURSO_VALIDO`, estilo de
nombres de método, docstrings.

**Cabecera de módulo, el tono a replicar** (`test_validar.py:1-9`):
```python
"""Pruebas de la capa de validación.

El método es siempre el mismo: se parte de un curso válido y se rompe **una** cosa.
Si la regla no protesta, la regla no sirve.
"""
```

**Imports y bootstrap de `sys.path`** (`test_validar.py:11-23`, idéntico en todos los archivos de
`pruebas/`):
```python
from __future__ import annotations

import copy
import sys
import unittest
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

import modelo  # noqa: E402
import validar  # noqa: E402
```

**Helper de meta completa + diccionario `CURSO_VALIDO`** (`test_validar.py:26-79`) — el molde para
construir un curso de prueba válido al que `test_modelo.py` puede sumar `unidad`/`total`/
`componentes` sin reescribir toda la fixture:
```python
def _meta(id_, unidad, semanas, valor, rubro, tipo="aprendizaje"):
    """Una meta completa: con pasos, evidencia y criterios, como exige el IEDI."""
    return {
        "id": id_, "unidad": unidad, "semanas": list(semanas), "valor": valor,
        "rubro": rubro, "tipo": tipo, "enunciado": f"Meta {id_} de la unidad {unidad}.",
        ...
    }

CURSO_VALIDO = {
    "meta": {"ciclo": "2026-2", "clave": "39056", "pua_ref": "puas/md/39056-big-data.md"},
    ...
    "metas": [
        _meta("0", "I", [1], 0, "tareas", tipo="encuadre"),
        _meta("1.1", "I", [2], 10, "tareas"),
        ...
    ],
}
```

**Nombres de método en español, descriptivos, con docstring que dice qué defiende**
(`test_validar.py:169-170`):
```python
def test_detecta_el_defecto_del_ejemplo_961(self):
    """El total suma 100 pero los rubros no: el error real del ejemplo dorado."""
```
`test_modelo.py` debe seguir esta forma exacta: `test_rubro_en_puntos_carga_sin_error`,
`test_rubro_puntos_sin_total_es_error_modelo`, `test_componente_hereda_unidad_de_su_propio_rubro`,
`test_ids_libres_conservan_el_orden_declarado`, cada uno con docstring de una línea que explica qué
defecto real evita la prueba (siguiendo el estilo de `test_registrar_dos_veces_no_cambia_nada` en
`test_plantillas.py:58-62`, que también nombra la garantía, no solo la acción).

**Patrón de "romper una cosa y esperar `ErrorModelo`"** — aplicar `assertRaises` sobre `modelo.cargar`
o `modelo.desde_dict`, análogo al de `test_plantillas.py:135-136,139-141`:
```python
with self.assertRaises(plantillas.ErrorPlantilla):
    plantillas.copia_de_trabajo("escolarizada", self.tmp / "x.docx")
...
with self.assertRaises(plantillas.ErrorPlantilla) as ctx:
    plantillas.copia_de_trabajo("hibrida", self.tmp / "x.docx")
self.assertIn("hibrida", str(ctx.exception))
```

---

### `pruebas/test_huella.py` (nuevo, acotado a `extraer_texto()`)

**Análogo:** `pruebas/test_plantillas.py` — clase base `EnDirectorioTemporal` (líneas 23-35), y el
helper `texto()` de `pruebas/test_render_docx.py:33-42` como precedente literal del mismo recorrido
OOXML crudo que `extraer_texto()` va a implementar.

**Clase base `EnDirectorioTemporal`, molde exacto de setUp/tearDown que redirige rutas de módulo**
(`test_plantillas.py:23-35`):
```python
class EnDirectorioTemporal(unittest.TestCase):
    """Trabaja sobre una copia desechable: nunca toca plantillas/ de verdad."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="di-plantillas-"))
        self._original = (plantillas.DIR, plantillas.REGISTRO, plantillas.HISTORICO)
        plantillas.DIR = self.tmp
        plantillas.REGISTRO = self.tmp / "REGISTRO.yaml"
        plantillas.HISTORICO = self.tmp / "historico"

    def tearDown(self):
        plantillas.DIR, plantillas.REGISTRO, plantillas.HISTORICO = self._original
        shutil.rmtree(self.tmp, ignore_errors=True)
```
`test_huella.py` replica esto para no tocar `pruebas/huellas.yaml` real: una clase
`EnDirectorioTemporal` propia que redirige el equivalente de `huella.REGISTRO` (o como se llame la
constante de ruta en `huella.py`) a un `tempfile.mkdtemp()`.

**Precedente literal del recorrido OOXML crudo** — ya existe en el repo, casi idéntico a la receta
de D-19 propuesta en RESEARCH.md (`test_render_docx.py:33-42`):
```python
def texto(doc) -> str:
    """Todo el texto del documento: párrafos y tablas."""
    partes = [p.text for p in doc.paragraphs]
    partes += [
        "".join(t.text or "" for t in tc.iter(qn("w:t")))
        for tabla in doc.tables
        for tr in tabla._tbl.tr_lst
        for tc in tr.findall(qn("w:tc"))
    ]
    return "\n".join(partes)
```
Esto confirma empíricamente que `tc.iter(qn("w:t"))` sobre celdas crudas (`tr.findall(qn("w:tc"))`)
ya es un patrón usado y probado en el repo — `huella.extraer_texto()` (RESEARCH.md, receta
completa) sigue el mismo enfoque, solo que despachando sobre `document.element.body.iterchildren()`
en vez de `doc.tables`/`doc.paragraphs` por separado, para preservar el orden real del documento
(que `test_render_docx.py.texto()` no necesita porque solo compara contenido, no orden).

**Único documento sintético en memoria (sin `generar.paquete`)** — D-18/D-19 exigen que
`test_huella.py` no dependa de generación completa. No hay análogo directo de "construir un
`.docx` sintético de 2-3 párrafos en memoria" en el repo hoy; se construye directamente con
`docx.Document()` (crear, añadir párrafos/tabla, guardar en `self.tmp`), siguiendo el mismo import
`from docx.oxml.ns import qn` que ya usa `test_render_docx.py:20`.

---

### `src/validar.py` (D-17 — metas duplicadas, R2)

**Análogo:** el propio `src/validar.py` — el `Counter` de rubros duplicados en R1
(`validar.py:141-143`), a replicar en R2 para metas.

**Bloque exacto de R1 con `Counter`, y cómo construye/añade el hallazgo** (`validar.py:124-143`):
```python
def regla_1(self) -> None:
    reglas = self.cfg.esquemas["reglas"]
    if not self.c.rubros:
        self.error("R1", "El curso no declara rubros de evaluación.")
        return

    total = round(sum(r.porcentaje for r in self.c.rubros), 2)
    exacta = reglas["suma_exacta"]
    if total != exacta:
        desglose = " + ".join(f"{r.etiqueta} {r.porcentaje:g}" for r in self.c.rubros)
        self.error(
            "R1",
            f"Los porcentajes del esquema suman {total:g}, no {exacta}: {desglose}.",
        )

    cuenta = Counter(r.id for r in self.c.rubros)
    if repetidos := [i for i, n in cuenta.items() if n > 1]:
        self.error("R1", f"Rubros duplicados: {', '.join(sorted(repetidos))}.")
```
`Counter` ya está importado en el módulo (usado en esta misma función). D-17 replica exactamente
las dos últimas líneas dentro de `regla_2()`, sobre `m.id for m in self.c.metas`:
```python
cuenta = Counter(m.id for m in self.c.metas)
if repetidos := [i for i, n in cuenta.items() if n > 1]:
    self.error("R2", f"Metas duplicadas: {', '.join(sorted(repetidos))}.")
```

**Estructura del hallazgo y cómo se añade** — método `_add`/`error`/`aviso` (`validar.py:115-122`):
```python
def _add(self, regla: str, nivel: str, mensaje: str) -> None:
    self.hallazgos.append(Hallazgo(regla, nivel, mensaje))

def error(self, regla: str, mensaje: str) -> None:
    self._add(regla, ERROR, mensaje)

def aviso(self, regla: str, mensaje: str) -> None:
    self._add(regla, AVISO, mensaje)
```
D-17 exige `error`, no `aviso`: dos metas con el mismo id es bloqueante, no decisión del docente.

**Regla existente que ya distingue el encuadre por `tipo`, no por id** (confirma D-13,
`validar.py:394` — dentro de la comprobación IEDI 1.5, no de R1/R2 como podría sugerir el roadmap):
```python
if m.valor == 0 and m.tipo not in ("encuadre", "cierre"):
    self.error("IEDI 1.5", f"{m.etiqueta} no tiene valor porcentual.")
```
No se toca — sirve como referencia de que el patrón correcto (`tipo`, no `id`) ya existe en el
código y no hay que introducirlo.

**Precedente de prueba para R2** (`test_validar.py:168-177`, clase `Regla2Metas`, molde exacto para
la prueba de D-17):
```python
class Regla2Metas(unittest.TestCase):
    def test_detecta_el_defecto_del_ejemplo_961(self):
        """El total suma 100 pero los rubros no: el error real del ejemplo dorado."""
        metas = copy.deepcopy(CURSO_VALIDO["metas"])
        for m in metas:
            m["rubro"] = "tareas"
        inf = informe(metas=metas)
        self.assertIn("R2", reglas_con_error(inf))
        mensajes = " ".join(h.mensaje for h in inf.errores if h.regla == "R2")
        self.assertIn("Proyecto final", mensajes)
```
Esta prueba **no se toca** (RESEARCH.md lo confirma: no usa `Meta.id` de forma sensible al valor) —
la prueba nueva de D-17 se añade como método hermano en la misma clase `Regla2Metas`.

---

### `src/render_docx.py` (D-11 — concatenación de evidencias de componente)

**Análogo:** la propia línea, extendida con el mismo estilo de comprensión de lista.

**Línea exacta a tocar, con su contexto inmediato** (`render_docx.py:266-288`,
función `_filas_de_meta`):
```python
def _filas_de_meta(meta: Meta, proto: list, cal, dividida: bool) -> list:
    """Las filas de la tabla que corresponden a una meta (dos si la entrega se divide)."""
    sesiones = meta.sesiones or []
    filas = []
    for n, plantilla_tr in enumerate(proto):
        tr = deepcopy(plantilla_tr)
        s = sesiones[n] if n < len(sesiones) else None
        ultima = n == len(proto) - 1

        _celda(tr, 0, [{"t": meta.etiqueta + ".", "enfasis": "meta"},
                       {"t": f" {meta.enunciado}"}] if n == 0 else "")
        _celda(tr, 1, str(min(meta.semanas)) if n == 0 else "")
        if dividida:
            _celda(tr, 2, "Presencial / Sincrónico" if n == 0 else "Virtual / Asincrónico")
        _celda(tr, 3 if dividida else 2,
               calendario.texto_fecha_corta(s.fecha) if s and s.fecha else "")
        _celda(tr, 4 if dividida else 3, s.actividad_tabla if s else "")
        _celda(tr, 5 if dividida else 4,
               ", ".join(e.nombre for e in meta.evidencias) if ultima else "")
        _celda(tr, 6 if dividida else 5,
               f"{meta.valor:g}%" if ultima else "")
        filas.append(tr)
    return filas
```
**Solo la línea 283-284 se toca** (D-11): la comprensión `", ".join(e.nombre for e in
meta.evidencias)` debe incluir también las evidencias de `meta.componentes` (cada
`Componente.evidencia`, si existe y no es `None`). Ejemplo de extensión que preserva el
comportamiento actual cuando no hay componentes (REQ-48):
```python
_celda(tr, 5 if dividida else 4,
       ", ".join(
           [e.nombre for e in meta.evidencias]
           + [c.evidencia.nombre for c in meta.componentes if c.evidencia]
       ) if ultima else "")
```
**Las líneas 286 y 408 (`f"{meta.valor:g}%"`) NO se tocan** — confirmado en CONTEXT.md y
RESEARCH.md: son de la Fase 13.

**Precedente de prueba de regresión** — `test_render_docx.py` ya tiene el helper `texto(doc)`
(líneas 33-42, citado arriba) que sirve directamente para verificar que un curso sin
`componentes:` no cambia ni un carácter del texto renderizado (REQ-48): comparar `texto(doc)` antes
y después de añadir el campo `componentes: []` (vacío) a una meta de prueba.

---

## Patrones compartidos (cross-cutting)

### Vocabulario cerrado con `ErrorModelo`
**Fuente:** `src/modelo.py:109-113` (`Sesion.ambiente`), `:135-140` (`Meta.tipo`)
**Aplica a:** `Rubro.unidad` (D-03), `Componente.tipo` (D-08)
```python
if self.campo not in VOCABULARIO:
    raise ErrorModelo(
        f"{Sujeto} {id}: {campo} inválido {self.campo!r}. Válidos: {', '.join(VOCABULARIO)}"
    )
```

### CLI con subcomandos y códigos de salida (0 = ok, 1 = problema, 2 = uso incorrecto)
**Fuente:** `src/plantillas.py:303-337`
**Aplica a:** `src/huella.py`

### Dump de YAML — un solo estilo en todo el repo
**Fuente:** `plantillas.py:121`, `generar.py:213`
**Aplica a:** `pruebas/huellas.yaml`
```python
yaml.safe_dump(cuerpo, allow_unicode=True, sort_keys=False, default_flow_style=False)
```

### Reusar `generar.paquete()`, nunca reimplementar validar→renderizar
**Fuente:** `src/generar.py:221-300`, uso en `pruebas/test_generar.py:51-53`
**Aplica a:** `src/huella.py`

### Estructura de prueba: romper una cosa, `assertRaises`, mensaje verificado con `assertIn`
**Fuente:** `pruebas/test_plantillas.py:135-141`, `pruebas/test_validar.py:169-177`
**Aplica a:** `pruebas/test_modelo.py`, ampliación de `pruebas/test_validar.py`

### Clase base de aislamiento con `tempfile.mkdtemp()` + redirección de constantes de módulo
**Fuente:** `pruebas/test_plantillas.py:23-35` (`EnDirectorioTemporal`)
**Aplica a:** `pruebas/test_huella.py`

## Sin análogo directo

Ninguno. Los nueve archivos en juego tienen un análogo exacto o casi exacto: la fase completa
—según ya adelantaba RESEARCH.md— es disciplina de repetir tres veces un patrón que el repositorio
ya usa, no construir algo sin precedente.

## Metadata

**Alcance de la búsqueda de análogos:** `src/` completo, `pruebas/` completo, dos `curso.yaml` de
control (39056, 39062).
**Archivos leídos íntegra o parcialmente:** `src/modelo.py` (completo), `src/plantillas.py`
(completo), `src/generar.py` (completo), `src/validar.py` (líneas 100-200, 380-410),
`src/render_docx.py` (líneas 255-305), `src/comprobar.py` (completo), `pruebas/test_validar.py`
(líneas 1-80, 160-178), `pruebas/test_plantillas.py` (completo), `pruebas/test_render_docx.py`
(líneas 1-60), `pruebas/test_generar.py` (fragmentos), `cursos/2026-2/39056-big-data/curso.yaml`
(líneas 195-225), `cursos/2026-2/39062-patrones-de-comportamiento/curso.yaml` (líneas 182-188).
**Fecha de extracción:** 2026-08-05
