"""Comprueba que la máquina tiene todo lo que el generador necesita.

Existe para que montar el proyecto en otra computadora no acabe en un rastro de
excepciones. Cada comprobación dice qué falta y cómo instalarlo, no solo que falló.

    python src/comprobar.py

Sale con código 1 si falta algo indispensable. Lo opcional —Word -- se reporta pero no
hace fallar: sin Word se generan los `.docx`, solo no se exportan a PDF.
"""
from __future__ import annotations

import importlib
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

PAQUETES = {
    "docx": ("python-docx", "rellenar las plantillas CIAD"),
    "pdfplumber": ("pdfplumber", "leer la tabla de prácticas del PUA"),
    "yaml": ("PyYAML", "curso.yaml, calendarios y configuración"),
    "openpyxl": ("openpyxl", "leer la rúbrica IEDI"),
}


def _linea(ok: bool | None, que: str, detalle: str) -> None:
    print(f"  {'✓' if ok else '·' if ok is None else '✗'} {que:<22}{detalle}")


def comprobar() -> list[str]:
    """Devuelve la lista de problemas indispensables encontrados."""
    faltan: list[str] = []

    print("\nPython")
    v = sys.version_info
    if v >= (3, 11):
        _linea(True, f"{v.major}.{v.minor}.{v.micro}", "")
    else:
        _linea(False, f"{v.major}.{v.minor}.{v.micro}", "se requiere 3.11 o mayor")
        faltan.append("Python 3.11+")

    print("\nPaquetes de Python")
    for modulo, (paquete, para) in PAQUETES.items():
        try:
            importlib.import_module(modulo)
            _linea(True, paquete, para)
        except ImportError:
            _linea(False, paquete, f"falta — pip install {paquete}")
            faltan.append(paquete)

    print("\nProgramas externos")
    if ruta := shutil.which("pdftotext"):
        try:
            v_pdf = subprocess.run(["pdftotext", "-v"], capture_output=True).stderr
            version = v_pdf.decode(errors="replace").splitlines()[0]
        except Exception:  # pragma: no cover - depende de la máquina
            version = ruta
        _linea(True, "pdftotext", version)
    else:
        _linea(False, "pdftotext", "falta — viene en Poppler, ver INSTALACION.md")
        faltan.append("pdftotext (Poppler)")

    print("\nExportación a PDF (opcional)")
    try:
        import win32com.client

        win32com.client.DispatchEx("Word.Application").Quit()
        _linea(True, "Microsoft Word", "disponible por COM")
    except ImportError:
        _linea(None, "pywin32", "falta — sin él se generan .docx pero no .pdf")
    except Exception:
        _linea(None, "Microsoft Word", "no responde — se generarán .docx sin .pdf")

    print("\nProyecto")
    for rel in ("config/profesores.yaml", "calendarios/2026-2.yaml", "puas/INDICE.md"):
        existe = (RAIZ / rel).exists()
        _linea(existe or False, rel.split("/")[-1], rel if existe else "no encontrado")
        if not existe:
            faltan.append(rel)

    try:
        sys.path.insert(0, str(RAIZ / "src"))
        import plantillas

        plantillas.verificar()
        _linea(True, "plantillas CIAD", "coinciden con su registro")
    except Exception as e:
        _linea(False, "plantillas CIAD", str(e)[:60])
        faltan.append("plantillas CIAD")

    return faltan


def main() -> int:
    print("Comprobación del entorno · Generador de Diseño Instruccional UABC")
    faltan = comprobar()
    if faltan:
        print(f"\nFalta por resolver: {', '.join(faltan)}.")
        print("Instrucciones paso a paso en INSTALACION.md.\n")
        return 1
    print("\nTodo listo. Empieza con:  python src/calendario.py 2026-2\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
