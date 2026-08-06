"""Pruebas del esquema de `curso.yaml`.

`validar.py` comprueba que las cantidades cuadren; esto comprueba que el contrato
**cargue**. Son cosas distintas y fallan distinto: un rubro cuya unidad no existe es un
defecto de esquema y revienta al cargar; un rubro cuyas metas no suman lo declarado carga
bien y lo reporta una regla.

La mitad de la no contaminación (REQ-48) se defiende aquí: los tres `curso.yaml` que ya
existen deben seguir cargando sin declarar ninguna clave nueva.
"""

from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

import modelo  # noqa: E402

try:
    from test_validar import CURSO_VALIDO, _meta  # noqa: E402
except ImportError:
    from pruebas.test_validar import CURSO_VALIDO, _meta  # noqa: E402


def curso_con(rubros, metas=None):
    """Copia del curso válido con otros rubros (y, si se dan, otras metas)."""
    d = copy.deepcopy(CURSO_VALIDO)
    d["evaluacion"]["rubros"] = rubros
    if metas is not None:
        d["metas"] = metas
    return modelo.desde_dict(d)


class RubroEnPuntos(unittest.TestCase):
    """REQ-38, criterio 1: un rubro en puntos carga junto a uno en porcentaje."""

    def test_puntos_y_porcentaje_conviven_en_el_mismo_curso(self):
        """El 531 real declara actividades en puntos y exámenes en porcentaje a la vez."""
        rubros = [
            {"id": "actividades", "etiqueta": "Entrega de actividades en clases y tareas",
             "porcentaje": 30, "unidad": "puntos", "total": 150},
            {"id": "examenes", "etiqueta": "Exámenes", "porcentaje": 50},
            {"id": "proyecto", "etiqueta": "Proyecto final", "porcentaje": 20},
        ]
        c = curso_con(rubros)
        self.assertEqual(c.rubro("actividades").unidad, "puntos")
        self.assertEqual(c.rubro("actividades").total, 150)
        self.assertEqual(c.rubro("examenes").unidad, "")

    def test_unidad_desconocida_es_error_modelo(self):
        """Una unidad fuera del vocabulario cerrado revienta al cargar, no al validar."""
        rubros = [
            {"id": "actividades", "etiqueta": "Actividades", "porcentaje": 30,
             "unidad": "creditos", "total": 150},
        ]
        with self.assertRaises(modelo.ErrorModelo) as ctx:
            curso_con(rubros)
        self.assertIn("creditos", str(ctx.exception))
        self.assertIn("puntos", str(ctx.exception))

    def test_puntos_sin_total_es_error_modelo(self):
        """Un rubro en puntos sin declarar cuántos reparte es un defecto de esquema."""
        rubros = [
            {"id": "actividades", "etiqueta": "Actividades", "porcentaje": 30,
             "unidad": "puntos"},
        ]
        with self.assertRaises(modelo.ErrorModelo) as ctx:
            curso_con(rubros)
        self.assertIn("total", str(ctx.exception))

    def test_el_total_no_se_infiere_de_la_suma_de_las_metas(self):
        """Inferirlo haría invisible el defecto real del 531 —150 declarados contra 140
        sumados— que la Fase 10 debe atrapar."""
        rubros = [
            {"id": "actividades", "etiqueta": "Actividades", "porcentaje": 30,
             "unidad": "puntos"},
            {"id": "examenes", "etiqueta": "Exámenes", "porcentaje": 50},
            {"id": "proyecto", "etiqueta": "Proyecto final", "porcentaje": 20},
        ]
        metas = [
            _meta("0", "I", [1], 0, "actividades", tipo="encuadre"),
            _meta("1.1", "I", [2], 70, "actividades"),
            _meta("1.2", "I", [3], 70, "actividades"),
        ]
        with self.assertRaises(modelo.ErrorModelo):
            curso_con(rubros, metas)

    def test_convierte_puntos_a_porcentaje(self):
        rubro = modelo.Rubro(id="actividades", etiqueta="Actividades", porcentaje=30,
                              unidad="puntos", total=150)
        self.assertAlmostEqual(2.0, rubro.a_porcentaje(10))

    def test_un_rubro_en_porcentaje_se_convierte_en_si_mismo(self):
        """Es la identidad que permite a las Fases 10 y 13 llamar siempre a la misma
        función sin preguntar la unidad."""
        rubro = modelo.Rubro(id="examenes", etiqueta="Exámenes", porcentaje=50)
        self.assertAlmostEqual(15, rubro.a_porcentaje(15))


class ComponentesDeMeta(unittest.TestCase):
    """REQ-39, criterio 2: una meta con componente sigue siendo una meta con una semana."""

    COMPONENTE = {
        "rubro": "examenes", "valor": 15, "etiqueta": "Examen I", "tipo": "examen_parcial",
        "evidencia": {"nombre": "Examen I resuelto", "tipo": "examen",
                      "recurso": "M2.4_Examen I"},
    }

    def _cursos_con_y_sin_componente(self):
        sin = modelo.desde_dict(copy.deepcopy(CURSO_VALIDO))
        d = copy.deepcopy(CURSO_VALIDO)
        for m in d["metas"]:
            if m["id"] == "2.1":
                m["componentes"] = [copy.deepcopy(self.COMPONENTE)]
        con = modelo.desde_dict(d)
        return sin, con

    def test_una_meta_con_componente_sigue_siendo_una_meta_con_una_semana(self):
        sin, con = self._cursos_con_y_sin_componente()
        self.assertEqual(len(sin.metas), len(con.metas))
        idx = next(i for i, m in enumerate(sin.metas) if m.id == "2.1")
        self.assertEqual(sin.metas[idx].semanas, con.metas[idx].semanas)

    def test_el_componente_conserva_sus_cinco_campos(self):
        _, con = self._cursos_con_y_sin_componente()
        meta = next(m for m in con.metas if m.id == "2.1")
        comp = meta.componentes[0]
        self.assertEqual(comp.rubro, "examenes")
        self.assertEqual(comp.valor, 15)
        self.assertEqual(comp.etiqueta, "Examen I")
        self.assertEqual(comp.tipo, "examen_parcial")
        self.assertEqual(comp.evidencia.nombre, "Examen I resuelto")

    def test_la_evidencia_del_componente_acepta_la_forma_corta(self):
        d = copy.deepcopy(CURSO_VALIDO)
        for m in d["metas"]:
            if m["id"] == "2.1":
                m["componentes"] = [{
                    "rubro": "examenes", "valor": 15, "etiqueta": "Examen I",
                    "tipo": "examen_parcial", "evidencia": "Examen I resuelto",
                }]
        c = modelo.desde_dict(d)
        meta = next(m for m in c.metas if m.id == "2.1")
        comp = meta.componentes[0]
        self.assertIsInstance(comp.evidencia, modelo.Evidencia)
        self.assertEqual(comp.evidencia.nombre, "Examen I resuelto")

    def test_un_componente_sin_evidencia_carga(self):
        d = copy.deepcopy(CURSO_VALIDO)
        for m in d["metas"]:
            if m["id"] == "2.1":
                m["componentes"] = [{
                    "rubro": "examenes", "valor": 15, "etiqueta": "Examen I",
                    "tipo": "examen_parcial",
                }]
        c = modelo.desde_dict(d)
        meta = next(m for m in c.metas if m.id == "2.1")
        self.assertIsNone(meta.componentes[0].evidencia)

    def test_tipo_de_componente_fuera_del_vocabulario_es_error_modelo(self):
        d = copy.deepcopy(CURSO_VALIDO)
        for m in d["metas"]:
            if m["id"] == "2.1":
                m["componentes"] = [{
                    "rubro": "examenes", "valor": 15, "etiqueta": "Examen I",
                    "tipo": "examen_partial",
                }]
        with self.assertRaises(modelo.ErrorModelo) as ctx:
            modelo.desde_dict(d)
        self.assertIn("examen_partial", str(ctx.exception))
        self.assertIn("examen_parcial", str(ctx.exception))

    def test_componente_sin_tipo_es_error_modelo(self):
        """No hay valor por omisión a propósito: un default silencioso convertiría un
        typo en un componente que nadie cuenta."""
        d = copy.deepcopy(CURSO_VALIDO)
        for m in d["metas"]:
            if m["id"] == "2.1":
                m["componentes"] = [{
                    "rubro": "examenes", "valor": 15, "etiqueta": "Examen I",
                }]
        with self.assertRaises(modelo.ErrorModelo) as ctx:
            modelo.desde_dict(d)
        self.assertIn("tipo", str(ctx.exception))

    def test_el_valor_del_componente_se_lee_en_la_unidad_de_su_propio_rubro(self):
        rubros = [
            {"id": "actividades", "etiqueta": "Actividades", "porcentaje": 30,
             "unidad": "puntos", "total": 150},
            {"id": "examenes", "etiqueta": "Exámenes", "porcentaje": 50},
            {"id": "proyecto", "etiqueta": "Proyecto final", "porcentaje": 20},
        ]
        metas = [
            _meta("0", "I", [1], 0, "actividades", tipo="encuadre"),
            _meta("2.4", "II", [7], 10, "actividades"),
        ]
        d = copy.deepcopy(CURSO_VALIDO)
        d["evaluacion"]["rubros"] = rubros
        for m in metas:
            if m["id"] == "2.4":
                m["componentes"] = [{
                    "rubro": "examenes", "valor": 15, "etiqueta": "Examen I",
                    "tipo": "examen_parcial",
                }]
        d["metas"] = metas
        c = modelo.desde_dict(d)
        meta = next(m for m in c.metas if m.id == "2.4")
        rubro_actividades = c.rubro("actividades")
        rubro_examenes = c.rubro("examenes")
        self.assertAlmostEqual(2.0, rubro_actividades.a_porcentaje(meta.valor))
        self.assertAlmostEqual(15.0, rubro_examenes.a_porcentaje(meta.componentes[0].valor))


class ContratoDelSegundoNivel(unittest.TestCase):
    """REQ-41: la calificación puede tener dos niveles, y el contrato dice contra cuál se mide
    la exención.

    Aquí solo se comprueba que **cargue**. Que los dos porcentajes sumen 100, que 100/0 sea
    aviso y que `calificacion_final` con segundo nivel sea error son hallazgos de R1, y viven
    en `test_validar.py`: un valor conocido y prohibido es juicio semántico, territorio de las
    reglas, no brecha de vocabulario.
    """

    NIVEL_60_40 = {
        "promedio": {
            "porcentaje": 60,
            "etiqueta": "Valor del promedio antes del Examen Ordinario",
        },
        "ordinario": {
            "porcentaje": 40,
            "etiqueta": "Valor del examen Ordinario",
        },
    }

    def _cargar(self, **evaluacion):
        """Copia del curso válido con las claves indicadas fundidas en `evaluacion:`."""
        d = copy.deepcopy(CURSO_VALIDO)
        d["evaluacion"] = {**copy.deepcopy(CURSO_VALIDO["evaluacion"]), **evaluacion}
        return modelo.desde_dict(d)

    def test_el_par_de_niveles_carga_con_sus_porcentajes_y_sus_etiquetas(self):
        c = self._cargar(segundo_nivel=self.NIVEL_60_40, exencion_contra="promedio")
        self.assertIsInstance(c.segundo_nivel, modelo.SegundoNivel)
        self.assertIsInstance(c.segundo_nivel.promedio, modelo.Nivel)
        self.assertEqual(60, c.segundo_nivel.promedio.porcentaje)
        self.assertEqual(40, c.segundo_nivel.ordinario.porcentaje)
        self.assertEqual(
            "Valor del promedio antes del Examen Ordinario",
            c.segundo_nivel.promedio.etiqueta,
        )
        self.assertEqual("Valor del examen Ordinario", c.segundo_nivel.ordinario.etiqueta)

    def test_un_curso_que_no_lo_declara_lo_deja_en_none(self):
        """El rasgo entero cuelga de este `None`: sin él no hay nada que activar."""
        c = self._cargar()
        self.assertIsNone(c.segundo_nivel)
        self.assertEqual("", c.exencion_contra)
        self.assertEqual("promedio", c.exencion_contra or "promedio")

    def test_segundo_nivel_sin_exencion_contra_es_error_modelo(self):
        """El dato que decide el significado no se infiere. Con dos niveles hay que decir
        contra cuál se mide el umbral."""
        with self.assertRaises(modelo.ErrorModelo) as ctx:
            self._cargar(segundo_nivel=self.NIVEL_60_40)
        self.assertIn("exencion_contra", str(ctx.exception))
        self.assertIn("segundo_nivel", str(ctx.exception))

    def test_exencion_contra_fuera_del_vocabulario_es_error_modelo(self):
        """Un valor que el modelo no conoce revienta al cargar, no al validar."""
        with self.assertRaises(modelo.ErrorModelo) as ctx:
            self._cargar(exencion_contra="promedio_del_curso")
        self.assertIn("promedio_del_curso", str(ctx.exception))
        self.assertIn("calificacion_final", str(ctx.exception))

    def test_calificacion_final_carga_aunque_r1_la_rechace(self):
        """`calificacion_final` está en el vocabulario a propósito para que R1 explique
        por qué el curso no es válido."""
        c = self._cargar(segundo_nivel=self.NIVEL_60_40, exencion_contra="calificacion_final")
        self.assertEqual("calificacion_final", c.exencion_contra)

    def test_exencion_contra_sin_segundo_nivel_es_opcional(self):
        """Sin segundo nivel la clave es opcional y declararla no rompe nada."""
        self.assertEqual("", self._cargar().exencion_contra)
        self.assertEqual("promedio", self._cargar(exencion_contra="promedio").exencion_contra)


class IdentificadoresLibres(unittest.TestCase):
    """REQ-42, criterio 3: los ids libres cargan y conservan el orden declarado."""

    def test_ids_terminados_en_punto_cero_cargan(self):
        metas = [
            _meta("1.0", "I", [1], 0, "tareas", tipo="encuadre"),
            _meta("2.0", "II", [2], 10, "tareas"),
            _meta("6.0", "III", [3], 10, "tareas"),
        ]
        c = curso_con(CURSO_VALIDO["evaluacion"]["rubros"], metas)
        self.assertEqual(["1.0", "2.0", "6.0"], [m.id for m in c.metas])

    def test_se_conserva_el_orden_declarado(self):
        """Nada en `src/` ordena las metas; si alguien introduce un `sorted()`, se
        entera aquí."""
        metas = [
            _meta("6.0", "III", [1], 10, "tareas", tipo="encuadre"),
            _meta("1.0", "I", [2], 10, "tareas"),
            _meta("2.0", "II", [3], 10, "tareas"),
        ]
        c = curso_con(CURSO_VALIDO["evaluacion"]["rubros"], metas)
        self.assertEqual(["6.0", "1.0", "2.0"], [m.id for m in c.metas])

    def test_metas_de_unidad_conserva_el_orden(self):
        metas = [
            _meta("1.0", "I", [1], 0, "tareas", tipo="encuadre"),
            _meta("1.3", "I", [4], 10, "tareas"),
            _meta("1.1", "I", [2], 10, "tareas"),
            _meta("1.2", "I", [3], 10, "tareas"),
        ]
        c = curso_con(CURSO_VALIDO["evaluacion"]["rubros"], metas)
        self.assertEqual(["1.0", "1.3", "1.1", "1.2"], [m.id for m in c.metas_de("I")])

    def test_el_encuadre_no_se_deduce_del_id(self):
        """El encuadre se distingue por su `tipo`, nunca por su identificador."""
        metas = [
            _meta("1.0", "I", [1], 0, "tareas", tipo="encuadre"),
            _meta("0", "I", [2], 10, "tareas", tipo="aprendizaje"),
        ]
        c = curso_con(CURSO_VALIDO["evaluacion"]["rubros"], metas)
        m_10 = next(m for m in c.metas if m.id == "1.0")
        m_0 = next(m for m in c.metas if m.id == "0")
        self.assertEqual(m_10.tipo, "encuadre")
        self.assertEqual(m_0.tipo, "aprendizaje")


class Aportes(unittest.TestCase):
    """El accesor plano que R2, R3 y la Fase 13 consumen (Fase 10, D-01 a D-03)."""

    def test_un_curso_sin_componentes_da_un_aporte_por_meta(self):
        """La mitad de la no contaminación: sin `componentes:` nada cambia de forma."""
        c = modelo.desde_dict(copy.deepcopy(CURSO_VALIDO))
        aportes = list(c.aportes())
        self.assertEqual(len(c.metas), len(aportes))
        self.assertEqual([m.id for m in c.metas], [a.meta.id for a in aportes])
        self.assertFalse(any(a.es_componente for a in aportes))

    def test_el_aporte_de_una_meta_copia_su_rubro_su_valor_y_su_tipo(self):
        c = modelo.desde_dict(copy.deepcopy(CURSO_VALIDO))
        a = next(a for a in c.aportes() if a.meta.id == "P1")
        self.assertEqual("examenes", a.rubro)
        self.assertEqual(10, a.valor)
        self.assertEqual("examen_parcial", a.tipo)
        self.assertEqual("Meta P1", a.etiqueta)
        self.assertFalse(a.es_componente)

    def test_el_componente_emite_su_propio_aporte_con_su_rubro(self):
        """El caso de la meta 2.4 del 531: 10 pts en actividades y el Examen I en exámenes."""
        d = copy.deepcopy(CURSO_VALIDO)
        for m in d["metas"]:
            if m["id"] == "2.1":
                m["componentes"] = [{
                    "rubro": "examenes", "valor": 15, "etiqueta": "Examen I",
                    "tipo": "examen_parcial",
                }]
        c = modelo.desde_dict(d)
        aportes = list(c.aportes())
        self.assertEqual(len(c.metas) + 1, len(aportes))
        comp = next(a for a in aportes if a.es_componente)
        self.assertEqual("examenes", comp.rubro)
        self.assertEqual(15, comp.valor)
        self.assertEqual("Examen I", comp.etiqueta)
        self.assertEqual("examen_parcial", comp.tipo)

    def test_el_componente_va_justo_detras_del_aporte_de_su_meta(self):
        """El orden importa: los mensajes de R2 enumeran aportes y deben leerse en orden."""
        d = copy.deepcopy(CURSO_VALIDO)
        for m in d["metas"]:
            if m["id"] == "2.1":
                m["componentes"] = [{
                    "rubro": "examenes", "valor": 15, "etiqueta": "Examen I",
                    "tipo": "examen_parcial",
                }]
        etiquetas = [a.etiqueta for a in modelo.desde_dict(d).aportes()]
        self.assertEqual(etiquetas.index("Meta 2.1") + 1, etiquetas.index("Examen I"))

    def test_desde_el_aporte_se_llega_a_la_meta_que_lo_declaro(self):
        """Condición de la Fase 13: el documento imprime cada aporte en la fila de su meta."""
        d = copy.deepcopy(CURSO_VALIDO)
        for m in d["metas"]:
            if m["id"] == "2.1":
                m["componentes"] = [{
                    "rubro": "examenes", "valor": 15, "etiqueta": "Examen I",
                    "tipo": "examen_parcial",
                }]
        c = modelo.desde_dict(d)
        comp = next(a for a in c.aportes() if a.es_componente)
        self.assertEqual("2.1", comp.meta.id)
        self.assertEqual([6, 7], comp.meta.semanas)

    def test_el_valor_del_aporte_sale_crudo_sin_convertir(self):
        """D-02: `10` en un rubro de 150 pts son 10 pts, no 2 %. Convertir es de quien compara."""
        rubros = [
            {"id": "actividades", "etiqueta": "Actividades", "porcentaje": 30,
             "unidad": "puntos", "total": 150},
            {"id": "examenes", "etiqueta": "Exámenes", "porcentaje": 50},
            {"id": "proyecto", "etiqueta": "Proyecto final", "porcentaje": 20},
        ]
        metas = [
            _meta("0", "I", [1], 0, "actividades", tipo="encuadre"),
            _meta("2.4", "II", [7], 10, "actividades"),
        ]
        c = curso_con(rubros, metas)
        a = next(a for a in c.aportes() if a.meta.id == "2.4")
        self.assertEqual(10, a.valor)
        self.assertAlmostEqual(2.0, c.rubro("actividades").a_porcentaje(a.valor))


class LosCursosExistentesNoCambian(unittest.TestCase):
    """REQ-48 por construcción: cargar los tres cursos reales sin declarar nada nuevo."""

    RUTAS = [
        RAIZ / "cursos/2026-2/39056-big-data/curso.yaml",
        RAIZ / "cursos/2026-2/39062-patrones-de-comportamiento/curso.yaml",
        RAIZ / "cursos/2026-2/38985-contabilidad-financiera/curso.yaml",
    ]

    def test_los_tres_cursos_cargan_sin_declarar_nada_nuevo(self):
        """Es la mitad de REQ-48 resuelta por construcción — si algún campo nuevo dejara
        de tener default, esta prueba lo delata."""
        for ruta in self.RUTAS:
            with self.subTest(curso=ruta.name, ruta=str(ruta)):
                c = modelo.cargar(ruta)
                for r in c.rubros:
                    self.assertEqual(r.unidad, "")
                    self.assertIsNone(r.total)
                for m in c.metas:
                    self.assertEqual(m.componentes, [])
                self.assertIsNone(c.segundo_nivel)
                self.assertEqual("", c.exencion_contra)


if __name__ == "__main__":
    unittest.main()
