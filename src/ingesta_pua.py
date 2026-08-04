"""Ingesta de PUA: PDF oficial → Markdown normalizado + registro en el índice.

El PUA (Programa de Unidad de Aprendizaje) es el documento oficial del que se
deriva todo el Diseño Instruccional. Este módulo lo convierte a Markdown
consultable sin perder nada de lo que el DI necesita copiar **literalmente**.

Estrategia de extracción:
  - Secciones I–V y VII–X: `pdftotext -layout -enc UTF-8` (el `-enc` es
    obligatorio; sin él salen mojibake).
  - Sección VI (tabla de prácticas de laboratorio): `pdfplumber`, porque
    `pdftotext -layout` intercala las columnas y la vuelve ilegible.

Uso:
    python src/ingesta_pua.py puas/fuente/36.-39056-Big-Data.pdf
    python src/ingesta_pua.py puas/fuente/*.pdf
"""

from __future__ import annotations

import hashlib
import re
import subprocess
import sys
import unicodedata
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import pdfplumber

RAIZ = Path(__file__).resolve().parent.parent
DIR_MD = RAIZ / "puas" / "md"
INDICE = RAIZ / "puas" / "INDICE.md"

# Encabezados de sección del PUA, en orden. El texto es literal del documento
# oficial; se tolera variación de acentos y espacios al buscarlos.
SECCIONES = [
    ("I", "DATOS DE IDENTIFICACIÓN"),
    ("II", "PROPÓSITO DE LA UNIDAD DE APRENDIZAJE"),
    ("III", "COMPETENCIA GENERAL DE LA UNIDAD DE APRENDIZAJE"),
    ("IV", "EVIDENCIA(S) DE APRENDIZAJE"),
    ("V", "DESARROLLO POR UNIDADES"),
    ("VI", "ESTRUCTURA DE LAS PRÁCTICAS DE LABORATORIO"),
    ("VII", "MÉTODO DE TRABAJO"),
    ("VIII", "CRITERIOS DE EVALUACIÓN"),
    ("IX", "REFERENCIAS"),
    ("X", "PERFIL DEL DOCENTE"),
]

# Los 9 campos numerados de la sección I.
CAMPOS_ID = [
    (1, "unidad_academica", "Unidad Académica"),
    (2, "programa_educativo", "Programa Educativo"),
    (3, "plan_estudios", "Plan de Estudios"),
    (4, "nombre", "Nombre de la Unidad de Aprendizaje"),
    (5, "clave", "Clave"),
    (6, "horas", "Horas y créditos"),
    (7, "etapa_formacion", "Etapa de Formación a la que Pertenece"),
    (8, "caracter", "Carácter de la Unidad de Aprendizaje"),
    (9, "requisitos", "Requisitos para Cursar la Unidad de Aprendizaje"),
]

RUIDO = re.compile(
    r"^\s*(UNIVERSIDAD AUTÓNOMA DE BAJA CALIFORNIA|"
    r"COORDINACIÓN GENERAL DE FORMACIÓN PROFESIONAL|"
    r"PROGRAMA DE UNIDAD DE APRENDIZAJE|\d+\s*)\s*$"
)


class ErrorIngesta(Exception):
    """El PDF no tiene la estructura esperada de un PUA."""


# -- utilidades --------------------------------------------------------------


def slug(texto: str) -> str:
    """`Big Data` → `big-data`."""
    sin_acentos = "".join(
        c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn"
    )
    return re.sub(r"[^a-z0-9]+", "-", sin_acentos.lower()).strip("-")


def sha256(ruta: Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


def _texto_plano(pdf: Path) -> str:
    try:
        r = subprocess.run(
            ["pdftotext", "-layout", "-enc", "UTF-8", str(pdf), "-"],
            capture_output=True,
            check=True,
        )
    except FileNotFoundError as e:
        # En una máquina recién montada esto es lo primero que falla, y el error de
        # Windows —«El sistema no puede encontrar el archivo especificado»— no dice
        # cuál. Ver INSTALACION.md.
        raise ErrorIngesta(
            "No se encontró `pdftotext`, que es lo que lee el PDF del PUA.\n"
            "    Viene en Poppler. En Windows: descarga poppler-windows, descomprime\n"
            "    y añade su carpeta `Library\\bin` al PATH.\n"
            "    Comprueba con: pdftotext -v\n"
            "    Detalle en INSTALACION.md."
        ) from e
    return r.stdout.decode("utf-8")


def _limpiar(bloque: str) -> str:
    """Quita encabezados de página repetidos y colapsa líneas en blanco."""
    lineas = [l.rstrip() for l in bloque.splitlines() if not RUIDO.match(l)]
    salida, vacia = [], False
    for l in lineas:
        if not l.strip():
            if not vacia and salida:
                salida.append("")
            vacia = True
        else:
            salida.append(l.strip())
            vacia = False
    return "\n".join(salida).strip()


# -- modelo ------------------------------------------------------------------


@dataclass
class Unidad:
    numero: str  # romano: I, II, III…
    nombre: str
    competencia: str = ""
    duracion_horas: int | None = None
    contenido: list[str] = field(default_factory=list)


@dataclass
class Practica:
    numero: str
    nombre: str
    procedimiento: str
    recursos: str
    duracion: str
    unidad: str = ""


@dataclass
class PUA:
    clave: str
    nombre: str
    identificacion: dict[str, str]
    secciones: dict[str, str]
    unidades: list[Unidad]
    practicas: list[Practica]
    origen: Path
    sha256: str
    avisos: list[str] = field(default_factory=list)

    @property
    def archivo_md(self) -> str:
        return f"{self.clave}-{slug(self.nombre)}.md"


# -- extracción --------------------------------------------------------------


def _partir_secciones(texto: str) -> dict[str, str]:
    """Corta el texto plano en los bloques I…X."""
    marcas: list[tuple[str, int, int]] = []
    for romano, titulo in SECCIONES:
        patron = re.compile(
            rf"^\s*{romano}\.\s+{re.escape(titulo)}\s*$", re.MULTILINE | re.IGNORECASE
        )
        if m := patron.search(texto):
            marcas.append((romano, m.start(), m.end()))

    if not marcas:
        raise ErrorIngesta(
            "No se encontró ningún encabezado de sección (I. DATOS DE IDENTIFICACIÓN…). "
            "¿Seguro que este PDF es un PUA?"
        )

    marcas.sort(key=lambda x: x[1])
    bloques: dict[str, str] = {}
    for i, (romano, _, fin) in enumerate(marcas):
        corte = marcas[i + 1][1] if i + 1 < len(marcas) else len(texto)
        bloques[romano] = _limpiar(texto[fin:corte])
    return bloques


def _identificacion(bloque: str) -> dict[str, str]:
    """Extrae los 9 campos numerados de la sección I."""
    datos: dict[str, str] = {}
    for i, (num, llave, etiqueta) in enumerate(CAMPOS_ID):
        if llave == "horas":
            if m := re.search(r"6\.\s*(HC:.*?)(?=\n\s*7\.|\Z)", bloque, re.S):
                datos["horas"] = " ".join(m.group(1).split())
            continue
        siguiente = CAMPOS_ID[i + 1][0] if i + 1 < len(CAMPOS_ID) else None
        alto = rf"(?=\n\s*{siguiente}\.\s)" if siguiente else r"(?=\n\s*Equipo de diseño|\Z)"
        patron = rf"{num}\.\s*{re.escape(etiqueta)}\s*:\s*(.*?){alto}"
        if m := re.search(patron, bloque, re.S):
            datos[llave] = " ".join(m.group(1).split())
    return datos


def _horas_a_dict(horas: str) -> dict[str, int]:
    """`HC: 01 HT: 00 … CR: 06` → `{'HC': 1, 'HT': 0, …}`."""
    return {k: int(v) for k, v in re.findall(r"(HC|HT|HL|HPC|HCL|HE|CR):\s*(\d+)", horas)}


def _unidades(bloque: str) -> list[Unidad]:
    """Parte la sección V en unidades con competencia, duración y contenido."""
    partes = re.split(r"^\s*UNIDAD\s+([IVXL]+)\.\s*(.*?)\s*$", bloque, flags=re.MULTILINE)
    unidades: list[Unidad] = []
    for i in range(1, len(partes), 3):
        numero, nombre, cuerpo = partes[i], partes[i + 1], partes[i + 2]
        u = Unidad(numero=numero, nombre=nombre.rstrip("."))

        if m := re.search(r"Competencia:\s*(.*?)(?=\n\s*Contenido:|\Z)", cuerpo, re.S):
            u.competencia = " ".join(m.group(1).split())
        if m := re.search(r"Duración:\s*(\d+)\s*horas?", cuerpo, re.I):
            u.duracion_horas = int(m.group(1))
        if m := re.search(r"Contenido:.*?$(.*)", cuerpo, re.S | re.MULTILINE):
            u.contenido = [
                " ".join(l.split())
                for l in m.group(1).splitlines()
                if re.match(r"^\s*\d+\.\d+", l)
            ]
        unidades.append(u)
    return unidades


def _practicas(pdf: Path) -> list[Practica]:
    """Sección VI vía pdfplumber.

    `pdftotext -layout` intercala las columnas de esta tabla y la vuelve
    inservible. Las filas que continúan en la página siguiente llegan con el
    número vacío y se pegan a la anterior.
    """
    practicas: list[Practica] = []
    unidad_actual = ""
    encabezado_visto = False

    with pdfplumber.open(pdf) as doc:
        for pagina in doc.pages:
            for tabla in pagina.extract_tables():
                if not tabla or len(tabla[0]) != 5:
                    continue
                for fila in tabla:
                    celdas = [(c or "").strip() for c in fila]
                    primera = celdas[0]

                    if "ESTRUCTURA DE LAS PRÁCTICAS" in primera.upper():
                        encabezado_visto = True
                        continue
                    if primera == "No." or not encabezado_visto:
                        continue
                    if (m := re.match(r"^UNIDAD\s*\|?\s*([IVXL]+)", primera.replace("\n", " "))):
                        unidad_actual = m.group(1)
                        continue
                    if not any(celdas):
                        continue

                    limpias = [" ".join(c.split()) for c in celdas]
                    if re.fullmatch(r"\d+", primera):
                        practicas.append(
                            Practica(
                                numero=limpias[0],
                                nombre=limpias[1],
                                procedimiento=limpias[2],
                                recursos=limpias[3],
                                duracion=limpias[4],
                                unidad=unidad_actual,
                            )
                        )
                    elif practicas:  # continuación de la práctica anterior
                        p = practicas[-1]
                        for attr, valor in zip(
                            ("nombre", "procedimiento", "recursos", "duracion"), limpias[1:]
                        ):
                            if valor:
                                actual = getattr(p, attr)
                                setattr(p, attr, f"{actual} {valor}".strip())
    return practicas


def leer(pdf: Path) -> PUA:
    pdf = pdf.resolve()
    if not pdf.exists():
        raise ErrorIngesta(f"No existe el archivo: {pdf}")

    secciones = _partir_secciones(_texto_plano(pdf))
    ident = _identificacion(secciones.get("I", ""))

    faltantes = [e for _, ll, e in CAMPOS_ID if ll not in ident]
    if "clave" not in ident or "nombre" not in ident:
        raise ErrorIngesta(
            f"No se pudieron leer la clave y el nombre de la unidad de aprendizaje "
            f"en {pdf.name}. Campos leídos: {sorted(ident)}"
        )

    avisos = []
    if faltantes:
        avisos.append(f"Campos de la sección I no encontrados: {', '.join(faltantes)}.")
    for romano, titulo in SECCIONES:
        if romano not in secciones:
            avisos.append(f"Sección {romano}. {titulo} no encontrada en el PDF.")

    unidades = _unidades(secciones.get("V", ""))
    if not unidades:
        avisos.append("No se detectó ninguna unidad en la sección V.")

    # Algunos PUA oficiales traen la numeración de temas repetida (el de Big Data
    # repite 1.2 y 1.3 en la Unidad I). Se conserva literal y se avisa: renumerar
    # rompería la trazabilidad contra el documento oficial.
    #
    # El número se toma completo. Truncarlo a dos niveles hacía que «1.2.1» colapsara
    # en «1.2» y se denunciara como repetido a su propio padre: un subtema no es un
    # duplicado. Patrones de Comportamiento, que anida hasta «1.2.1.1», daba cuatro
    # avisos falsos.
    for u in unidades:
        numeros = [m[1] for c in u.contenido if (m := re.match(r"(\d+(?:\.\d+)*)\.?\s", c))]
        repetidos = sorted({n for n in numeros if numeros.count(n) > 1})
        if repetidos:
            avisos.append(
                f"La unidad {u.numero} repite la numeración de temas "
                f"({', '.join(repetidos)}) en el PUA oficial. Se conserva literal."
            )

    practicas = _practicas(pdf) if "VI" in secciones else []
    if "VI" in secciones and not practicas:
        avisos.append("La sección VI existe pero no se extrajo ninguna práctica.")

    # No se inventan datos ausentes: si el PUA oficial deja una celda vacía, se
    # reporta para que el docente la complete.
    if sin_duracion := [p.numero for p in practicas if not p.duracion.strip()]:
        una = len(sin_duracion) == 1
        avisos.append(
            f"{'La práctica' if una else 'Las prácticas'} {', '.join(sin_duracion)} "
            f"no {'trae' if una else 'traen'} duración en el PUA oficial. "
            f"Se deja vacía; confírmala con el programa impreso."
        )

    return PUA(
        clave=ident["clave"],
        nombre=ident["nombre"],
        identificacion=ident,
        secciones=secciones,
        unidades=unidades,
        practicas=practicas,
        origen=pdf,
        sha256=sha256(pdf),
        avisos=avisos,
    )


# -- escritura ---------------------------------------------------------------


def _yaml_str(v: str) -> str:
    return '"' + v.replace("\\", "\\\\").replace('"', '\\"') + '"'


def a_markdown(pua: PUA) -> str:
    ident = pua.identificacion
    horas = _horas_a_dict(ident.get("horas", ""))
    try:
        ruta_origen = pua.origen.relative_to(RAIZ).as_posix()
    except ValueError:  # el PDF vive fuera del repositorio
        ruta_origen = pua.origen.as_posix()

    l: list[str] = ["---"]
    l.append(f"clave: {_yaml_str(pua.clave)}")
    l.append(f"nombre: {_yaml_str(pua.nombre)}")
    for llave in (
        "programa_educativo",
        "plan_estudios",
        "unidad_academica",
        "etapa_formacion",
        "caracter",
        "requisitos",
    ):
        if llave in ident:
            l.append(f"{llave}: {_yaml_str(ident[llave])}")
    if horas:
        l.append("horas:")
        l.extend(f"  {k}: {v}" for k, v in horas.items())
        if "CR" in horas:
            l.append(f"creditos: {horas['CR']}")
    l.append(f"unidades: {len(pua.unidades)}")
    l.append(f"practicas: {len(pua.practicas)}")
    l.append(f"fuente: {_yaml_str(ruta_origen)}")
    l.append(f"sha256: {_yaml_str(pua.sha256)}")
    l.append(f"convertido: {date.today().isoformat()}")
    l.append("---")
    l.append("")
    l.append(f"# PUA {pua.clave} — {pua.nombre}")
    l.append("")
    l.append(
        "> Convertido automáticamente desde el PDF oficial con `src/ingesta_pua.py`.\n"
        "> Las secciones I y III se copian **literalmente** al Diseño Instruccional; "
        "no las parafrasees."
    )
    l.append("")

    if pua.avisos:
        l.append("> **Notas de extracción:**")
        l.extend(f"> - {a}" for a in pua.avisos)
        l.append("")

    for romano, titulo in SECCIONES:
        if romano not in pua.secciones:
            continue
        l.append(f"## {romano}. {titulo}")
        l.append("")

        if romano == "I":
            l.append("| # | Campo | Valor |")
            l.append("|---|---|---|")
            for num, llave, etiqueta in CAMPOS_ID:
                valor = ident.get(llave, "—")
                l.append(f"| {num} | {etiqueta} | {valor} |")
            l.append("")
            if m := re.search(
                r"(Equipo de diseño de PUA.*)", pua.secciones["I"], re.S
            ):
                l.append("### Equipo de diseño y visto bueno")
                l.append("")
                l.append("```")
                l.append(m.group(1).strip())
                l.append("```")
                l.append("")

        elif romano == "V":
            for u in pua.unidades:
                l.append(f"### UNIDAD {u.numero}. {u.nombre}")
                l.append("")
                if u.competencia:
                    l.append(f"**Competencia:** {u.competencia}")
                    l.append("")
                if u.duracion_horas is not None:
                    l.append(f"**Duración:** {u.duracion_horas} horas")
                    l.append("")
                if u.contenido:
                    l.append("**Contenido:**")
                    l.append("")
                    l.extend(f"- {c}" for c in u.contenido)
                    l.append("")

        elif romano == "VI":
            if pua.practicas:
                l.append("| No. | Unidad | Nombre de la Práctica | Procedimiento | Recursos de Apoyo | Duración |")
                l.append("|---|---|---|---|---|---|")
                for p in pua.practicas:
                    celdas = [
                        p.numero,
                        p.unidad,
                        p.nombre,
                        p.procedimiento,
                        p.recursos,
                        p.duracion,
                    ]
                    l.append("| " + " | ".join(c.replace("|", "\\|") for c in celdas) + " |")
                l.append("")
            else:
                l.append("> **Nota de extracción:** no se pudo reconstruir la tabla de prácticas.")
                l.append("")

        else:
            l.append(pua.secciones[romano])
            l.append("")

    return "\n".join(l).rstrip() + "\n"


# -- índice ------------------------------------------------------------------

_CABECERA_INDICE = """# Índice de PUAs

Registro de los Programas de Unidad de Aprendizaje disponibles como contexto.

**Antes de pedirle un PUA al usuario, consulta esta tabla.** Si la materia ya está
aquí, usa el Markdown de `puas/md/`. Si no, pide el PDF oficial, déjalo en
`puas/fuente/` e ingiérelo con `/di-pua` o:

```
python src/ingesta_pua.py puas/fuente/<archivo>.pdf
```

| Clave | Nombre | Programa educativo | Plan | Créditos | Unidades | Markdown | SHA-256 |
|---|---|---|---|---|---|---|---|
"""


def _fila_indice(pua: PUA) -> str:
    ident = pua.identificacion
    horas = _horas_a_dict(ident.get("horas", ""))
    return (
        f"| `{pua.clave}` | {pua.nombre} | {ident.get('programa_educativo', '—')} "
        f"| {ident.get('plan_estudios', '—')} | {horas.get('CR', '—')} "
        f"| {len(pua.unidades)} | [`{pua.archivo_md}`](md/{pua.archivo_md}) "
        f"| `{pua.sha256[:12]}…` |"
    )


def actualizar_indice(pua: PUA) -> str:
    """Inserta o reemplaza la fila del PUA. Reingerir no duplica el registro."""
    filas: dict[str, str] = {}
    if INDICE.exists():
        for linea in INDICE.read_text(encoding="utf-8").splitlines():
            if m := re.match(r"^\|\s*`(\d+)`\s*\|", linea):
                filas[m.group(1)] = linea

    accion = "actualizado" if pua.clave in filas else "registrado"
    filas[pua.clave] = _fila_indice(pua)

    cuerpo = "\n".join(filas[k] for k in sorted(filas))
    INDICE.write_text(_CABECERA_INDICE + cuerpo + "\n", encoding="utf-8")
    return accion


# -- CLI ---------------------------------------------------------------------


def ingerir(pdf: Path) -> PUA:
    pua = leer(pdf)
    DIR_MD.mkdir(parents=True, exist_ok=True)
    (DIR_MD / pua.archivo_md).write_text(a_markdown(pua), encoding="utf-8")
    accion = actualizar_indice(pua)

    print(f"  {pdf.name}")
    print(f"    → puas/md/{pua.archivo_md}  ({accion} en el índice)")
    print(
        f"    {pua.clave} · {pua.nombre} · {len(pua.unidades)} unidades · "
        f"{len(pua.practicas)} prácticas"
    )
    for a in pua.avisos:
        print(f"    ⚠ {a}")
    return pua


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2

    rutas = [Path(a) for a in argv[1:]]
    fallos = 0
    for ruta in rutas:
        try:
            ingerir(ruta)
        except (ErrorIngesta, subprocess.CalledProcessError) as e:
            print(f"  {ruta.name}\n    Error: {e}", file=sys.stderr)
            fallos += 1
    return 1 if fallos else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
