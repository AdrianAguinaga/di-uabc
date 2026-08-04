"""Pruebas de la exportación a PDF.

La conversión la hace Word por COM, así que estas pruebas dependen de la máquina. Las que
no necesitan Word (validación de rutas y de extensión) corren siempre; la conversión real
se omite con un mensaje claro donde no haya Word, en vez de fallar y hacer ruido.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

import export_pdf  # noqa: E402
import modelo  # noqa: E402
import render_docx  # noqa: E402

CURSO = RAIZ / "cursos" / "2026-2" / "39056-big-data" / "curso.yaml"


def hay_word() -> bool:
    try:
        import win32com.client
    except ImportError:
        return False
    try:
        app = win32com.client.DispatchEx("Word.Application")
    except Exception:
        return False
    try:
        app.Quit()
    except Exception:
        pass
    return True


class SinTocarWord(unittest.TestCase):
    """Lo que se puede comprobar sin abrir Word."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="di-pdf-"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_rechaza_un_archivo_inexistente(self):
        with self.assertRaises(export_pdf.ErrorExport):
            export_pdf.exportar(self.tmp / "no-existe.docx")

    def test_rechaza_lo_que_no_es_docx(self):
        pdf = self.tmp / "cosa.pdf"
        pdf.write_bytes(b"%PDF-1.4")
        with self.assertRaises(export_pdf.ErrorExport) as ctx:
            export_pdf.exportar(pdf)
        self.assertIn(".docx", str(ctx.exception))

    def test_un_directorio_sin_docx_lo_dice(self):
        with self.assertRaises(export_pdf.ErrorExport) as ctx:
            export_pdf.exportar_todos(self.tmp)
        self.assertIn("No hay .docx", str(ctx.exception))

    def test_ignora_los_temporales_de_word(self):
        (self.tmp / "~$borrador.docx").write_bytes(b"basura")
        with self.assertRaises(export_pdf.ErrorExport):
            export_pdf.exportar_todos(self.tmp)


@unittest.skipUnless(hay_word(), "requiere Microsoft Word con pywin32 (solo Windows)")
class ConversionReal(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="di-pdf-real-"))
        curso = modelo.cargar(CURSO)
        cls.docx = render_docx.generar(
            curso, curso.grupos[0], cls.tmp / "DI-2026-2-39056-961.docx"
        )
        cls.pdf = export_pdf.exportar(cls.docx)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_produce_un_pdf_junto_al_docx(self):
        self.assertTrue(self.pdf.exists())
        # `.resolve()` expande los nombres cortos 8.3 de Windows (LAB920~1 → LAB9204-1).
        self.assertEqual(self.docx.with_suffix(".pdf").resolve(), self.pdf.resolve())
        self.assertGreater(self.pdf.stat().st_size, 50_000)

    def test_el_pdf_conserva_el_contenido(self):
        salida = subprocess.run(
            ["pdftotext", "-layout", "-enc", "UTF-8", str(self.pdf), "-"],
            capture_output=True, text=True, encoding="utf-8",
        )
        if salida.returncode != 0:
            self.skipTest("pdftotext no disponible")
        texto = salida.stdout
        for esperado in (
            "Universidad Autónoma de Baja California",
            "Sección 1. Descripción general del curso.",
            "Sección 2. Plan de actividades.",
            "Sección 3. Descripción de la actividad de la meta.",
            "Reglas de convivencia en el aula",
            "Firma Jefe Grupo",
            "Versión 2026-2.",
        ):
            self.assertIn(esperado, texto, f"el PDF no contiene: {esperado}")

    def test_no_deja_procesos_de_word_huerfanos(self):
        salida = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq WINWORD.EXE", "/NH"],
            capture_output=True, text=True,
        )
        self.assertNotIn("WINWORD.EXE", salida.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
