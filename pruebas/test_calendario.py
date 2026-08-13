"""Pruebas del motor de calendario.

    python -m unittest discover -s pruebas -v
"""

import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import calendario as cal  # noqa: E402


class TestCiclo2026_2(unittest.TestCase):
    """El ciclo vigente. Estas fechas salen del calendario oficial de la UABC."""

    @classmethod
    def setUpClass(cls):
        cls.c = cal.cargar("2026-2")

    def test_son_16_semanas_no_17(self):
        """El hallazgo que condiciona todo el proyecto: 16 semanas, no las 17
        que asumen las plantillas CIAD."""
        self.assertEqual(self.c.total_semanas, 16)

    def test_inicio_y_fin(self):
        self.assertEqual(self.c.inicio, date(2026, 8, 10))
        self.assertEqual(self.c.fin, date(2026, 11, 28))

    def test_el_curso_empieza_en_lunes(self):
        self.assertEqual(self.c.inicio.weekday(), 0)

    def test_primera_y_ultima_semana(self):
        self.assertEqual(self.c.semana(1).inicio, date(2026, 8, 10))
        self.assertEqual(self.c.semana(16).inicio, date(2026, 11, 23))
        self.assertEqual(self.c.semana(16).fin, date(2026, 11, 28))

    def test_las_tres_suspensiones_caen_donde_deben(self):
        for numero, dia in ((6, date(2026, 9, 16)), (13, date(2026, 11, 2)), (15, date(2026, 11, 16))):
            with self.subTest(semana=numero):
                fechas = [s.fecha for s in self.c.semana(numero).suspensiones]
                self.assertIn(dia, fechas)

    def test_las_demas_semanas_no_tienen_suspension(self):
        con_suspension = {s.numero for s in self.c.semanas if s.suspensiones}
        self.assertEqual(con_suspension, {6, 13, 15})

    def test_semana_con_suspension_tiene_5_dias_habiles(self):
        self.assertEqual(len(self.c.semana(6).dias_habiles()), 5)
        self.assertEqual(len(self.c.semana(1).dias_habiles()), 6)

    def test_periodos_de_examen(self):
        ord_ = self.c.periodos["examenes_ordinarios"]
        self.assertEqual((ord_.inicio, ord_.fin), (date(2026, 11, 30), date(2026, 12, 8)))
        ext = self.c.periodos["examenes_extraordinarios"]
        self.assertEqual((ext.inicio, ext.fin), (date(2026, 12, 14), date(2026, 12, 17)))


class TestReglasDeFecha(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c = cal.cargar("2026-2")

    def test_fecha_en_suspension_se_recorre_al_siguiente_habil(self):
        # Semana 15 empieza el lunes 16 nov, que es suspensión → cae en martes 17.
        self.assertEqual(self.c.fecha_de(15, 0), date(2026, 11, 17))

    def test_fecha_normal_no_se_mueve(self):
        self.assertEqual(self.c.fecha_de(2, 0), date(2026, 8, 17))
        self.assertEqual(self.c.fecha_de(2, 4), date(2026, 8, 21))

    def test_entrega_en_dia_de_suspension_es_rechazada(self):
        with self.assertRaises(cal.ErrorCalendario) as ctx:
            self.c.validar_entrega(date(2026, 9, 16))
        self.assertIn("suspensión", str(ctx.exception))

    def test_entrega_despues_del_fin_de_cursos_es_rechazada(self):
        with self.assertRaises(cal.ErrorCalendario):
            self.c.validar_entrega(date(2026, 12, 1))

    def test_entrega_antes_del_inicio_es_rechazada(self):
        with self.assertRaises(cal.ErrorCalendario):
            self.c.validar_entrega(date(2026, 8, 5))  # curso de inducción

    def test_entrega_valida_no_lanza(self):
        self.c.validar_entrega(date(2026, 8, 21))

    def test_pedir_semana_17_falla_con_mensaje_util(self):
        with self.assertRaises(cal.ErrorCalendario) as ctx:
            self.c.semana(17)
        self.assertIn("16 semanas", str(ctx.exception))

    def test_semana_de_una_fecha(self):
        self.assertEqual(self.c.semana_de(date(2026, 8, 10)), 1)
        self.assertEqual(self.c.semana_de(date(2026, 11, 28)), 16)
        self.assertIsNone(self.c.semana_de(date(2026, 12, 1)))


class ElRecorridoMiraElHorarioDelGrupo(unittest.TestCase):
    """D-07/D-15: la suspensión recorre días con clase y no sale de la semana."""

    LUN_MAR_MIE = {0, 1, 2}  # 39056·961
    SOLO_LUNES = {0}  # 39062·971
    SOLO_MIERCOLES = {2}  # 39062·972

    @classmethod
    def setUpClass(cls):
        cls.c = cal.cargar("2026-2")

    def test_961_recorre_del_lunes_suspendido_al_martes_de_la_misma_semana(self):
        self.assertEqual(date(2026, 11, 3), self.c.fecha_de(13, 0, self.LUN_MAR_MIE))
        self.assertEqual(date(2026, 11, 17), self.c.fecha_de(15, 0, self.LUN_MAR_MIE))

    def test_971_no_tiene_a_donde_recorrer_y_no_cruza_de_semana(self):
        """Sin este límite la semana 13 imprimiría el 9 nov, que es de la semana 14."""
        self.assertEqual(date(2026, 11, 2), self.c.fecha_de(13, 0, self.SOLO_LUNES))
        self.assertEqual(date(2026, 11, 16), self.c.fecha_de(15, 0, self.SOLO_LUNES))

    def test_972_tampoco_y_se_queda_en_el_miercoles_suspendido(self):
        self.assertEqual(date(2026, 9, 16), self.c.fecha_de(6, 2, self.SOLO_MIERCOLES))

    def test_dia_de_clase_dice_que_no_hay_dia_solo_en_esos_tres_casos(self):
        self.assertIsNone(self.c.dia_de_clase(13, 0, self.SOLO_LUNES))
        self.assertIsNone(self.c.dia_de_clase(15, 0, self.SOLO_LUNES))
        self.assertIsNone(self.c.dia_de_clase(6, 2, self.SOLO_MIERCOLES))
        self.assertIsNotNone(self.c.dia_de_clase(13, 0, self.LUN_MAR_MIE))
        for n in range(1, 17):
            if n not in (13, 15):
                with self.subTest(semana=n):
                    self.assertIsNotNone(self.c.dia_de_clase(n, 0, self.SOLO_LUNES))

    def test_una_semana_sin_suspension_no_se_mueve(self):
        self.assertEqual(date(2026, 8, 17), self.c.fecha_de(2, 0, self.SOLO_LUNES))

    def test_sin_horario_el_recorrido_es_el_de_siempre(self):
        """Protege al 531 y a cualquier curso futuro que no declare bloques (D-07)."""
        self.assertEqual(date(2026, 11, 17), self.c.fecha_de(15, 0))
        self.assertEqual(date(2026, 9, 17), self.c.fecha_de(6, 2))

    def test_la_siguiente_sesion_virtual_es_posterior_a_la_suspension(self):
        martes = {1}
        self.assertEqual(
            date(2026, 11, 3),
            self.c.siguiente_dia_de_bloque(date(2026, 11, 2), martes),
        )
        self.assertEqual(
            date(2026, 11, 17),
            self.c.siguiente_dia_de_bloque(date(2026, 11, 16), martes),
        )
        # El martes 15 ya pasó cuando se suspende el miércoles 16: corresponde el 22.
        self.assertEqual(
            date(2026, 9, 22),
            self.c.siguiente_dia_de_bloque(date(2026, 9, 16), martes),
        )

    def test_no_inventa_un_bloque_despues_del_fin_de_cursos(self):
        self.assertIsNone(
            self.c.siguiente_dia_de_bloque(date(2026, 11, 28), {0, 1, 2, 3, 4, 5})
        )


class TestUtilidades(unittest.TestCase):
    def test_ciclo_actual(self):
        self.assertEqual(cal.ciclo_actual(date(2026, 8, 3)), "2026-2")
        self.assertEqual(cal.ciclo_actual(date(2026, 12, 20)), "2026-2")
        self.assertEqual(cal.ciclo_actual(date(2027, 1, 25)), "2027-1")
        self.assertEqual(cal.ciclo_actual(date(2027, 6, 30)), "2027-1")

    def test_texto_fecha(self):
        self.assertEqual(cal.texto_fecha(date(2026, 8, 18)), "18 de agosto")
        self.assertEqual(cal.texto_fecha(date(2026, 8, 18), True), "18 de agosto de 2026")

    def test_rango_texto_cruzando_mes(self):
        c = cal.cargar("2026-2")
        self.assertEqual(c.semana(1).rango_texto(), "10–15 ago")
        self.assertEqual(c.semana(4).rango_texto(), "31 ago – 5 sep")

    def test_ciclo_inexistente_pide_el_calendario_oficial(self):
        with self.assertRaises(cal.ErrorCalendario) as ctx:
            cal.cargar("2030-1")
        self.assertIn("No estimes las fechas", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
