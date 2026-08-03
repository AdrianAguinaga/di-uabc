"""Pruebas de la ingesta de PUA, contra el PUA real de Big Data.

    python -m unittest discover -s pruebas -v
"""

import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

import ingesta_pua as ing  # noqa: E402

PDF = RAIZ / "puas" / "fuente" / "36.-39056-Big-Data.pdf"


@unittest.skipUnless(PDF.exists(), f"falta {PDF}")
class TestPUABigData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pua = ing.leer(PDF)

    def test_identificacion(self):
        self.assertEqual(self.pua.clave, "39056")
        self.assertEqual(self.pua.nombre, "Big Data")
        ident = self.pua.identificacion
        self.assertEqual(ident["programa_educativo"], "Licenciado en Inteligencia de Negocios")
        self.assertEqual(ident["plan_estudios"], "2021-2")
        self.assertEqual(ident["etapa_formacion"], "Disciplinaria")
        self.assertEqual(ident["caracter"], "Obligatoria")

    def test_horas_y_creditos(self):
        horas = ing._horas_a_dict(self.pua.identificacion["horas"])
        self.assertEqual(horas, {"HC": 1, "HT": 0, "HL": 4, "HPC": 0, "HCL": 0, "HE": 1, "CR": 6})

    def test_cinco_unidades_con_competencia_y_duracion(self):
        self.assertEqual(len(self.pua.unidades), 5)
        self.assertEqual([u.numero for u in self.pua.unidades], ["I", "II", "III", "IV", "V"])
        for u in self.pua.unidades:
            with self.subTest(unidad=u.numero):
                self.assertTrue(u.competencia, "sin competencia")
                self.assertIsNotNone(u.duracion_horas, "sin duración")
                self.assertTrue(u.contenido, "sin contenido")

    def test_primera_unidad(self):
        u = self.pua.unidades[0]
        self.assertEqual(u.nombre, "Fundamentos de Big Data")
        self.assertEqual(u.duracion_horas, 4)
        self.assertTrue(u.competencia.startswith("Identificar los fundamentos del Big Data"))

    def test_diez_practicas_con_unidad(self):
        """La §VI se desordena con `pdftotext -layout`; se extrae con pdfplumber."""
        self.assertEqual(len(self.pua.practicas), 10)
        for p in self.pua.practicas:
            with self.subTest(practica=p.numero):
                self.assertTrue(p.nombre)
                self.assertTrue(p.procedimiento)
                self.assertRegex(p.unidad, r"^[IVX]+$")

    def test_practica_partida_entre_paginas_se_cose(self):
        """La práctica 3 se parte entre las páginas 8 y 9; su procedimiento
        debe quedar completo, no truncado."""
        p3 = next(p for p in self.pua.practicas if p.numero == "3")
        self.assertIn("Atiende las indicaciones", p3.procedimiento)
        self.assertIn("Identifica las fuentes de datos", p3.procedimiento)

    def test_avisa_de_la_duracion_ausente_sin_inventarla(self):
        """El PUA oficial deja vacía la duración de la práctica 3.
        No se fabrica un valor: se reporta."""
        p3 = next(p for p in self.pua.practicas if p.numero == "3")
        self.assertEqual(p3.duracion.strip(), "")
        self.assertIn("no traen duración", " ".join(self.pua.avisos))

    def test_las_demas_practicas_si_traen_duracion(self):
        for p in self.pua.practicas:
            if p.numero != "3":
                with self.subTest(practica=p.numero):
                    self.assertRegex(p.duracion, r"\d+\s*horas?")

    def test_todas_las_secciones_presentes(self):
        esperadas = {r for r, _ in ing.SECCIONES}
        self.assertEqual(set(self.pua.secciones) & esperadas, esperadas)

    def test_competencia_general_literal(self):
        """La §III se copia literal al DI; no debe perderse nada."""
        self.assertIn("Gestionar datos masivos", self.pua.secciones["III"])

    def test_avisa_de_la_numeracion_repetida_del_pua(self):
        """El PUA oficial repite números de tema en las 5 unidades.
        Se conserva literal y se avisa; renumerar rompería la trazabilidad."""
        avisos = " ".join(self.pua.avisos)
        self.assertIn("repite la numeración", avisos)

    def test_nombre_de_archivo_derivado(self):
        self.assertEqual(self.pua.archivo_md, "39056-big-data.md")

    def test_markdown_lleva_front_matter_y_hash(self):
        md = ing.a_markdown(self.pua)
        self.assertTrue(md.startswith("---\n"))
        self.assertIn('clave: "39056"', md)
        self.assertIn(self.pua.sha256, md)
        self.assertIn("## VI. ESTRUCTURA DE LAS PRÁCTICAS DE LABORATORIO", md)

    def test_ingesta_es_determinista(self):
        self.assertEqual(ing.a_markdown(self.pua), ing.a_markdown(ing.leer(PDF)))


class TestUtilidades(unittest.TestCase):
    def test_slug(self):
        self.assertEqual(ing.slug("Big Data"), "big-data")
        self.assertEqual(ing.slug("Diseño de Algoritmos"), "diseno-de-algoritmos")
        self.assertEqual(ing.slug("Programación  I"), "programacion-i")

    def test_pdf_inexistente(self):
        with self.assertRaises(ing.ErrorIngesta):
            ing.leer(Path("no-existe.pdf"))

    def test_pdf_que_no_es_pua(self):
        otro = RAIZ / "calendarios" / "fuente" / "Calendario-de-Actividades-2026-2-2027-1.pdf"
        if not otro.exists():
            self.skipTest("falta el PDF de calendario")
        with self.assertRaises(ing.ErrorIngesta) as ctx:
            ing.leer(otro)
        self.assertIn("PUA", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
