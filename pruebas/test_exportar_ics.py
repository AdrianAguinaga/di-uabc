"""Contrato de la exportación de clases a iCalendar."""

from __future__ import annotations

import io
import sys
import tempfile
import unittest
from collections import Counter
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

import calendario  # noqa: E402
import exportar_ics  # noqa: E402


class CalendarioReal20262(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cal = calendario.cargar("2026-2")
        cursos, omitidos = exportar_ics.cargar_cursos(exportar_ics.rutas_curso("2026-2"))
        if omitidos:
            raise AssertionError(f"Cursos de control que no cargaron: {omitidos}")
        cls.resultado = exportar_ics.eventos_de(
            [c for c in cursos if c.profesor_id == "ara"], cls.cal
        )

    def test_cuenta_las_154_clases_reales(self):
        self.assertEqual(154, len(self.resultado.eventos))

    def test_cada_evento_esta_dentro_de_clases_y_fuera_de_suspension(self):
        for evento in self.resultado.eventos:
            local = evento.inicio.astimezone(exportar_ics.ZONA).date()
            self.assertTrue(self.cal.en_periodo_de_clases(local))
            self.assertIsNone(self.cal.es_suspension(local))

    def test_las_semanas_suspendidas_y_ordinarias_cuentan_lo_esperado(self):
        por_semana = Counter(
            self.cal.semana_de(e.inicio.astimezone(exportar_ics.ZONA).date())
            for e in self.resultado.eventos
        )
        self.assertEqual(10, por_semana[1])
        self.assertEqual(8, por_semana[6])
        self.assertEqual(8, por_semana[13])
        self.assertEqual(8, por_semana[15])

    def test_cuenta_los_bloques_y_omite_los_grupos_sin_horario_real(self):
        conteo = Counter(e.uid.split("@")[0].rsplit("-", 1)[-1] for e in self.resultado.eventos)
        self.assertEqual(106, conteo["presencial"])
        self.assertEqual(48, conteo["virtual"])
        self.assertTrue(any("-932-" in e.uid for e in self.resultado.eventos))
        self.assertTrue(all("-962-" not in e.uid for e in self.resultado.eventos))
        self.assertTrue(all("-531-" not in e.uid for e in self.resultado.eventos))
        self.assertIn("39056 · grupo 962", self.resultado.grupos_no_impartidos)
        self.assertEqual([], self.resultado.grupos_sin_bloques)

    def test_presencial_tiene_aula_y_virtual_no_tiene_ubicacion(self):
        for evento in self.resultado.eventos:
            if "virtual" in evento.resumen:
                self.assertEqual("", evento.ubicacion)
            else:
                self.assertEqual("Laboratorio de cómputo", evento.ubicacion)

    def test_el_cambio_estacional_conserva_la_hora_local_de_la_clase(self):
        lunes_agosto = next(e for e in self.resultado.eventos if "39056-961-20260810-1200" in e.uid)
        lunes_noviembre = next(e for e in self.resultado.eventos if "39056-961-20261109-1200" in e.uid)
        self.assertEqual(12, lunes_agosto.inicio.astimezone(exportar_ics.ZONA).hour)
        self.assertEqual(12, lunes_noviembre.inicio.astimezone(exportar_ics.ZONA).hour)
        self.assertNotEqual(lunes_agosto.inicio.hour, lunes_noviembre.inicio.hour)


class SerializacionIcalendar(unittest.TestCase):
    SELLO = datetime(2026, 8, 6, 0, 0, tzinfo=timezone.utc)

    @classmethod
    def setUpClass(cls):
        cal = calendario.cargar("2026-2")
        cursos, _ = exportar_ics.cargar_cursos(exportar_ics.rutas_curso("2026-2"))
        eventos = exportar_ics.eventos_de(
            [c for c in cursos if c.profesor_id == "ara"], cal
        ).eventos
        cls.texto = exportar_ics.serializar(
            eventos, cls.SELLO, "Clases 2026-2 · Adrian Rodriguez Aguiñaga", "Agenda de ara"
        )

    def test_lleva_la_estructura_y_campos_requeridos(self):
        self.assertTrue(self.texto.startswith("BEGIN:VCALENDAR\r\nVERSION:2.0\r\n"))
        self.assertTrue(self.texto.endswith("END:VCALENDAR\r\n"))
        self.assertNotIn("\n", self.texto.replace("\r\n", ""))
        self.assertEqual(154, self.texto.count("BEGIN:VEVENT\r\n"))
        self.assertEqual(154, self.texto.count("UID:"))
        self.assertEqual(154, self.texto.count("DTSTAMP:20260806T000000Z"))
        self.assertEqual(154, self.texto.count("DTSTART:"))
        self.assertEqual(154, self.texto.count("DTEND:"))
        self.assertIn("X-WR-CALNAME:Clases 2026-2 · Adrian Rodriguez Aguiñaga", self.texto)
        self.assertIn("X-WR-CALDESC:Agenda de ara", self.texto)

    def test_solo_serializa_clases(self):
        for prohibido in ("VTODO", "VALARM", "Entrega", "Examen", "Tutoría", "Investigación"):
            self.assertNotIn(prohibido, self.texto)

    def test_virtual_se_marca_y_no_lleva_location(self):
        for bloque in self.texto.split("BEGIN:VEVENT\r\n")[1:]:
            if "· virtual\r\n" in bloque:
                self.assertNotIn("LOCATION:", bloque)
            else:
                self.assertIn("LOCATION:Laboratorio de cómputo", bloque)

    def test_escapa_y_pliega_por_octetos(self):
        valor = "Áula, 12; ruta\\nueva\n" + "á" * 50
        escapado = exportar_ics.escapar(valor)
        self.assertIn("\\,", escapado)
        self.assertIn("\\;", escapado)
        self.assertIn("\\\\", escapado)
        self.assertIn("\\n", escapado)
        plegado = exportar_ics.plegar(f"LOCATION:{escapado}")
        self.assertGreater(len(plegado.split("\r\n")), 1)
        self.assertTrue(all(len(linea.encode("utf-8")) <= 75 for linea in plegado.split("\r\n")))
        self.assertTrue(all(linea.startswith(" ") for linea in plegado.split("\r\n")[1:]))


class ComandoDeExportacion(unittest.TestCase):
    def test_el_id_del_profesor_es_obligatorio(self):
        salida = io.StringIO()
        with redirect_stderr(salida):
            codigo = exportar_ics.main(["exportar_ics.py", "2026-2"])
        self.assertEqual(2, codigo)
        self.assertIn("<id-profesor>", salida.getvalue())

    def test_el_comando_escribe_el_archivo_y_el_curso_ausente_no_bloquea(self):
        cursos, omitidos = exportar_ics.cargar_cursos([
            RAIZ / "cursos" / "2026-2" / "39056-big-data" / "curso.yaml",
            RAIZ / "cursos" / "2026-2" / "932-ausente" / "curso.yaml",
        ])
        self.assertEqual(1, len(cursos))
        self.assertEqual(1, len(omitidos))

        with tempfile.TemporaryDirectory() as temporal:
            salida = Path(temporal) / "Clases-2026-2.ics"
            fuera, resultado = exportar_ics.exportar(
                "2026-2", "ara", salida, SerializacionIcalendar.SELLO
            )
            self.assertEqual(salida, fuera)
            self.assertTrue(fuera.exists())
            self.assertEqual(154, len(resultado.eventos))
            self.assertEqual("ara", resultado.profesor_id)
            self.assertEqual("Adrian Rodriguez Aguiñaga", resultado.profesor_nombre)
            self.assertEqual(154, fuera.read_text(encoding="utf-8").count("BEGIN:VEVENT"))

    def test_no_mezcla_profesores_y_no_escribe_una_agenda_vacia(self):
        with tempfile.TemporaryDirectory() as temporal:
            salida = Path(temporal) / "Clases-2026-2-zra.ics"
            with self.assertRaises(exportar_ics.ErrorIcs) as ctx:
                exportar_ics.exportar("2026-2", "zra", salida)
        self.assertIn("Zurisaddai", str(ctx.exception))
        self.assertFalse(salida.exists())

    def test_la_cli_informa_el_archivo_y_las_omisiones(self):
        with tempfile.TemporaryDirectory() as temporal:
            salida = Path(temporal) / "Clases-2026-2.ics"
            out, err = io.StringIO(), io.StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                codigo = exportar_ics.main(
                    ["exportar_ics.py", "2026-2", "ara", "--salida", str(salida)]
                )
        self.assertEqual(0, codigo, err.getvalue())
        self.assertIn("Adrian Rodriguez Aguiñaga (ara): 154 eventos", out.getvalue())
        self.assertIn("39056 · grupo 962", out.getvalue())


if __name__ == "__main__":
    unittest.main()
