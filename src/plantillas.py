"""Custodia de las plantillas CIAD.

Tres capas, y cada una tiene un dueño distinto:

    referencias/<lo que subió el usuario>   ← original intocable. Solo el usuario.
    plantillas/<modalidad>.docx             ← juego de trabajo, con sha256 registrado.
    cursos/<…>/salida/DI-….docx             ← copia desechable que se rellena.

**Nunca se escribe sobre una plantilla.** Cada documento nace de una copia fresca, así que
generar el mismo curso mil veces deja la plantilla idéntica: es la única forma de garantizar
que el formato institucional no se degrada de una generación a la siguiente.

El registro (`plantillas/REGISTRO.yaml`) guarda el sha256 de cada plantilla. Antes de copiar
se recalcula: si no coincide, el renderizado **falla de forma ruidosa** en vez de producir un
documento con un formato que ya nadie sabe de dónde salió.

Uso:
    python src/plantillas.py verificar
    python src/plantillas.py registrar
    python src/plantillas.py actualizar semipresencial <ruta.docx> [--version 2026-1]
"""

from __future__ import annotations

import hashlib
import shutil
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parent.parent
DIR = RAIZ / "plantillas"
HISTORICO = DIR / "historico"
REGISTRO = DIR / "REGISTRO.yaml"
CONFIG = RAIZ / "config" / "plantillas.yaml"

CABECERA = (
    "# Registro de las plantillas de trabajo. Lo genera src/plantillas.py: no lo edites\n"
    "# a mano. El sha256 se verifica antes de cada renderizado; si no coincide, el\n"
    "# renderizado falla en vez de producir un documento de origen desconocido.\n"
    "#\n"
    "# Para cambiar una plantilla:\n"
    "#     python src/plantillas.py actualizar <modalidad> <ruta.docx> --version <ver>\n"
    "# La anterior no se pierde: se archiva en plantillas/historico/.\n"
)


class ErrorPlantilla(Exception):
    """La plantilla no está donde debe, o no es la que se registró."""


def sha256(ruta: Path) -> str:
    h = hashlib.sha256()
    with ruta.open("rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()


@dataclass
class Entrada:
    modalidad: str
    archivo: str
    origen: str
    version: str
    sha256: str
    bytes: int
    registrado: str
    historial: list[dict]

    @property
    def ruta(self) -> Path:
        return DIR / self.archivo


# -- registro ----------------------------------------------------------------


def _config() -> dict:
    return yaml.safe_load(CONFIG.read_text(encoding="utf-8"))["modalidades"]


def cargar() -> dict[str, Entrada]:
    """Lee `plantillas/REGISTRO.yaml`. Devuelve {} si aún no existe."""
    if not REGISTRO.exists():
        return {}
    datos = yaml.safe_load(REGISTRO.read_text(encoding="utf-8")) or {}
    return {
        mod: Entrada(
            modalidad=mod,
            archivo=e["archivo"],
            origen=e["origen"],
            version=str(e["version"]),
            sha256=e["sha256"],
            bytes=e["bytes"],
            registrado=str(e["registrado"]),
            historial=e.get("historial", []),
        )
        for mod, e in (datos.get("plantillas") or {}).items()
    }


def guardar(entradas: dict[str, Entrada]) -> None:
    cuerpo = {
        "plantillas": {
            mod: {
                "archivo": e.archivo,
                "origen": e.origen,
                "version": e.version,
                "sha256": e.sha256,
                "bytes": e.bytes,
                "registrado": e.registrado,
                **({"historial": e.historial} if e.historial else {}),
            }
            for mod, e in sorted(entradas.items())
        }
    }
    texto = yaml.safe_dump(cuerpo, allow_unicode=True, sort_keys=False, default_flow_style=False)
    REGISTRO.write_text(CABECERA + texto, encoding="utf-8")


# -- operaciones -------------------------------------------------------------


def registrar(hoy: date | None = None) -> list[str]:
    """Crea el juego de trabajo desde `referencias/`, según `config/plantillas.yaml`.

    Es idempotente: si el sha256 no cambió, no toca nada — ni el archivo ni la fecha
    de registro. Correrlo dos veces deja el repositorio igual.
    """
    hoy = hoy or date.today()
    DIR.mkdir(exist_ok=True)
    entradas = cargar()
    acciones: list[str] = []

    for modalidad, cfg in _config().items():
        origen = RAIZ / cfg["origen"]
        if not origen.exists():
            raise ErrorPlantilla(
                f"No existe el original de {modalidad}: {cfg['origen']}. "
                f"Es un archivo de referencias/ y solo lo repone el usuario."
            )
        destino = DIR / f"{modalidad}.docx"
        h = sha256(origen)
        previa = entradas.get(modalidad)

        if previa and previa.sha256 == h and destino.exists() and sha256(destino) == h:
            continue  # ya está, y es la misma

        shutil.copy2(origen, destino)
        entradas[modalidad] = Entrada(
            modalidad=modalidad,
            archivo=destino.name,
            origen=cfg["origen"],
            version=str(cfg["version"]),
            sha256=h,
            bytes=origen.stat().st_size,
            # La fecha solo se mueve cuando cambia el contenido.
            registrado=previa.registrado if previa and previa.sha256 == h else hoy.isoformat(),
            historial=previa.historial if previa else [],
        )
        acciones.append(f"registrada {modalidad} ← {cfg['origen']} ({h[:12]})")

    guardar(entradas)
    return acciones


def actualizar(modalidad: str, nueva: Path, version: str = "", hoy: date | None = None) -> str:
    """Sustituye una plantilla, archivando la anterior en `plantillas/historico/`.

    Nada se pierde: la plantilla saliente queda con su versión y su hash en el nombre,
    de modo que un documento generado hace un año se puede reproducir.
    """
    hoy = hoy or date.today()
    nueva = Path(nueva).resolve()
    if not nueva.exists():
        raise ErrorPlantilla(f"No existe {nueva}")
    if nueva.suffix.lower() != ".docx":
        raise ErrorPlantilla(f"Una plantilla CIAD es un .docx, no {nueva.suffix!r}")

    entradas = cargar()
    if modalidad not in entradas:
        raise ErrorPlantilla(
            f"Modalidad desconocida: {modalidad}. "
            f"Registradas: {', '.join(sorted(entradas)) or 'ninguna'}. "
            f"Corre primero `python src/plantillas.py registrar`."
        )

    previa = entradas[modalidad]
    h = sha256(nueva)
    if h == previa.sha256:
        return f"{modalidad} ya está en esa versión ({h[:12]}); no se toca nada."

    HISTORICO.mkdir(parents=True, exist_ok=True)
    archivado = HISTORICO / f"{modalidad}-{previa.version}-{previa.sha256[:8]}.docx"
    if previa.ruta.exists():
        shutil.copy2(previa.ruta, archivado)

    shutil.copy2(nueva, previa.ruta)
    entradas[modalidad] = Entrada(
        modalidad=modalidad,
        archivo=previa.archivo,
        origen=_ruta_relativa(nueva),
        version=version or previa.version,
        sha256=h,
        bytes=nueva.stat().st_size,
        registrado=hoy.isoformat(),
        historial=previa.historial
        + [
            {
                "version": previa.version,
                "sha256": previa.sha256,
                "origen": previa.origen,
                "reemplazada": hoy.isoformat(),
                "archivada": _ruta_relativa(archivado),
            }
        ],
    )
    guardar(entradas)
    return (
        f"{modalidad}: {previa.sha256[:12]} → {h[:12]}. "
        f"La anterior quedó en {_ruta_relativa(archivado)}.\n"
        f"Revisa config/plantillas.yaml: si la estructura cambió (columnas, filas de semana, "
        f"pasos ordinales), los hechos declarados ahí ya no son ciertos."
    )


def _ruta_relativa(p: Path) -> str:
    try:
        return p.relative_to(RAIZ).as_posix()
    except ValueError:
        return p.as_posix()


def verificar(modalidad: str | None = None) -> list[str]:
    """Recalcula el sha256 de cada plantilla. Devuelve los problemas encontrados."""
    entradas = cargar()
    if not entradas:
        return ["No hay plantillas registradas. Corre `python src/plantillas.py registrar`."]

    problemas: list[str] = []
    for mod, e in sorted(entradas.items()):
        if modalidad and mod != modalidad:
            continue
        if not e.ruta.exists():
            problemas.append(f"{mod}: falta {_ruta_relativa(e.ruta)}.")
            continue
        if (h := sha256(e.ruta)) != e.sha256:
            problemas.append(
                f"{mod}: el archivo cambió ({e.sha256[:12]} → {h[:12]}). "
                f"Alguien escribió sobre la plantilla. Restaura con "
                f"`git checkout plantillas/{e.archivo}` o registra el cambio con "
                f"`python src/plantillas.py actualizar {mod} <ruta>`."
            )
        origen = RAIZ / e.origen
        if origen.exists() and sha256(origen) != e.sha256 and not e.historial:
            problemas.append(
                f"{mod}: el original {e.origen} ya no coincide con la plantilla registrada. "
                f"Si el CIAD publicó una versión nueva, corre "
                f"`python src/plantillas.py actualizar {mod} {e.origen}`."
            )
    return problemas


def copia_de_trabajo(modalidad: str, destino: Path) -> Path:
    """Copia verificada de la plantilla al destino. **Es la única puerta al renderizado.**

    Verifica el hash antes de copiar, para que ningún documento salga de una plantilla
    que no es la registrada.
    """
    entradas = cargar()
    if modalidad not in entradas:
        raise ErrorPlantilla(
            f"No hay plantilla registrada para la modalidad {modalidad}. "
            f"Corre `python src/plantillas.py registrar`."
        )
    if problemas := verificar(modalidad):
        raise ErrorPlantilla("\n".join(problemas))

    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(entradas[modalidad].ruta, destino)
    return destino


# -- consola -----------------------------------------------------------------


def _imprimir_registro() -> None:
    entradas = cargar()
    if not entradas:
        print("Sin plantillas registradas.")
        return
    for mod, e in sorted(entradas.items()):
        print(f"{mod:<16} v{e.version:<8} {e.sha256[:12]}  {e.bytes:>7} B  {e.registrado}")
        for h in e.historial:
            print(f"{'':<16} ← v{h['version']} {h['sha256'][:12]} archivada {h['reemplazada']}")


def main(argv: list[str]) -> int:
    orden = argv[1] if len(argv) > 1 else "verificar"
    try:
        if orden == "registrar":
            for a in registrar() or ["Nada que hacer: el registro ya estaba al día."]:
                print(a)
            _imprimir_registro()

        elif orden == "actualizar":
            if len(argv) < 4:
                print(
                    "Uso: python src/plantillas.py actualizar <modalidad> <ruta.docx> "
                    "[--version <ver>]",
                    file=sys.stderr,
                )
                return 2
            version = argv[argv.index("--version") + 1] if "--version" in argv else ""
            print(actualizar(argv[2], Path(argv[3]), version))

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
