"""Exporta un `.docx` a PDF con Microsoft Word por COM.

Es la ruta de mayor fidelidad —Word renderiza su propio formato— y no exige instalar nada:
Word ya está en la máquina. A cambio es Windows-only.

Tres precauciones que no son opcionales:

  1. **`DispatchEx`, no `Dispatch`.** `Dispatch` se engancha a una instancia de Word que el
     usuario ya tenga abierta; cerrarla al terminar le cerraría su documento.
  2. **Rutas absolutas.** Word no resuelve rutas relativas: las interpreta contra su propio
     directorio de trabajo y falla con un error que no dice nada.
  3. **`try/finally` con `Quit()`,** y se cierra solo el proceso que abrimos nosotros,
     identificado por su PID. Si no, quedan `WINWORD.EXE` huérfanos consumiendo memoria.

Uso:
    python src/export_pdf.py cursos/2026-2/39056-big-data/salida/DI-2026-2-39056-961.docx
"""

from __future__ import annotations

import sys
from pathlib import Path

FORMATO_PDF = 17  # wdExportFormatPDF


class ErrorExport(Exception):
    """No se pudo exportar a PDF."""


def _word():
    """Una instancia de Word propia, invisible y callada."""
    try:
        import win32com.client
    except ImportError as e:  # pragma: no cover - depende de la máquina
        raise ErrorExport(
            "Falta pywin32, que es lo que habla con Word.\n"
            "    python -m pip install pywin32\n"
            "En una máquina sin Word (Linux, macOS) no hay ruta COM: usa LibreOffice\n"
            "    soffice --headless --convert-to pdf <archivo.docx>"
        ) from e

    try:
        app = win32com.client.DispatchEx("Word.Application")
    except Exception as e:  # pragma: no cover - depende de la máquina
        raise ErrorExport(f"No se pudo iniciar Word: {e}") from e

    app.Visible = False
    app.DisplayAlerts = False
    return app


def exportar(docx: Path | str, pdf: Path | str | None = None) -> Path:
    """Convierte un `.docx` a PDF. Devuelve la ruta del PDF."""
    docx = Path(docx).resolve()
    if not docx.exists():
        raise ErrorExport(f"No existe {docx}")
    if docx.suffix.lower() != ".docx":
        raise ErrorExport(f"Se esperaba un .docx, no {docx.suffix!r}")

    pdf = Path(pdf).resolve() if pdf else docx.with_suffix(".pdf")
    pdf.parent.mkdir(parents=True, exist_ok=True)

    app = _word()
    doc = None
    try:
        doc = app.Documents.Open(str(docx), ReadOnly=True, AddToRecentFiles=False)
        doc.ExportAsFixedFormat(str(pdf), FORMATO_PDF)
    except Exception as e:  # pragma: no cover - depende de la máquina
        raise ErrorExport(f"Word no pudo exportar {docx.name}: {e}") from e
    finally:
        if doc is not None:
            try:
                doc.Close(SaveChanges=False)
            except Exception:
                pass
        try:
            app.Quit()
        except Exception:
            pass

    if not pdf.exists():
        raise ErrorExport(f"Word terminó sin errores pero no dejó el PDF en {pdf}")
    return pdf


def exportar_todos(directorio: Path | str) -> list[Path]:
    """Todos los `.docx` de un directorio, ignorando los temporales de Word (`~$…`)."""
    directorio = Path(directorio)
    archivos = sorted(p for p in directorio.glob("*.docx") if not p.name.startswith("~$"))
    if not archivos:
        raise ErrorExport(f"No hay .docx en {directorio}")
    return [exportar(a) for a in archivos]


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("Uso: python src/export_pdf.py <archivo.docx | directorio>", file=sys.stderr)
        return 2
    ruta = Path(argv[1])
    try:
        salidas = exportar_todos(ruta) if ruta.is_dir() else [exportar(ruta)]
    except ErrorExport as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    for p in salidas:
        print(f"→ {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
