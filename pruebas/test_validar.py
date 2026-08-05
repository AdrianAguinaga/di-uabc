"""Pruebas de la capa de validación.

El método es siempre el mismo: se parte de un curso válido y se rompe **una** cosa.
Si la regla no protesta, la regla no sirve.

La prueba que da sentido a todas las demás es
`test_detecta_el_defecto_del_ejemplo_961`: el ejemplo dorado suma 100 en total pero sus
rubros no cuadran, y ese es exactamente el error que R2 existe para atrapar.
"""

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


def _meta(id_, unidad, semanas, valor, rubro, tipo="aprendizaje"):
    """Una meta completa: con pasos, evidencia y criterios, como exige el IEDI."""
    return {
        "id": id_,
        "unidad": unidad,
        "semanas": list(semanas),
        "valor": valor,
        "rubro": rubro,
        "tipo": tipo,
        "enunciado": f"Meta {id_} de la unidad {unidad}.",
        "sesiones": [
            {
                "ambiente": "presencial",
                "semana": semanas[0],
                "pasos": ["Primero, revisa el material.", "Segundo, resuelve el ejercicio."],
            },
            {
                "ambiente": "virtual",
                "semana": semanas[-1],
                "pasos": ["Tercero, sube la evidencia a la plataforma."],
            },
        ],
        "evidencias": [{"nombre": f"Evidencia {id_}", "tipo": "Documento"}],
        "criterios_evaluacion": ["Cumple con la estructura solicitada."],
    }


# 16 semanas del ciclo 2026-2, todas cubiertas. Exámenes 20 · Tareas 40 · Proyecto 40.
CURSO_VALIDO = {
    "meta": {"ciclo": "2026-2", "clave": "39056", "pua_ref": "puas/md/39056-big-data.md"},
    "profesor": "ara",
    "identificacion": {
        "nombre": "Big Data",
        "modalidad": "semipresencial",
        "nivel_academico": "Licenciatura.",
        "practica": False,
    },
    "contenido": {
        "competencia_general": "Analizar grandes volúmenes de datos…",
        "proposito_general": "El curso aporta al perfil de egreso…",
        "estrategia_general": "Aprendizaje basado en proyectos.",
        "evidencias_desempeno": "Proyecto integrador de análisis de datos.",
        "criterios_evaluacion": "Exámenes 20 %, tareas 40 %, proyecto 40 %.",
    },
    "unidades": [
        {"numero": "I", "nombre": "Fundamentos de Big Data"},
        {"numero": "II", "nombre": "Almacenamiento y procesamiento"},
        {"numero": "III", "nombre": "Análisis y visualización"},
    ],
    "metas": [
        _meta("0", "I", [1], 0, "tareas", tipo="encuadre"),
        _meta("1.1", "I", [2], 10, "tareas"),
        _meta("1.2", "I", [3, 4], 10, "tareas"),
        _meta("P1", "I", [5], 10, "examenes", tipo="examen_parcial"),
        _meta("2.1", "II", [6, 7], 10, "tareas"),
        _meta("2.2", "II", [8, 9], 10, "tareas"),
        _meta("P2", "II", [10], 10, "examenes", tipo="examen_parcial"),
        _meta("2.3", "II", [11], 10, "proyecto"),
        _meta("3.1", "III", [12, 13], 15, "proyecto"),
        _meta("3.2", "III", [14, 15, 16], 15, "proyecto"),
    ],
    "evaluacion": {
        "esquema_id": "estandar-2026",
        "exencion_ordinario": 80,
        "rubros": [
            {"id": "examenes", "etiqueta": "Exámenes", "porcentaje": 20, "parciales": 2},
            {"id": "tareas", "etiqueta": "Tareas y actividades de clase", "porcentaje": 40},
            {"id": "proyecto", "etiqueta": "Proyecto final", "porcentaje": 40},
        ],
    },
    "grupos": [
        {"numero": "961", "horario": {"dias_presencial": [1], "dia_entrega": 5}},
        {"numero": "962", "horario": {"dias_presencial": [3], "dia_entrega": 5}},
    ],
    "citas": ["EE-65", "EE-66", "EE-67", "EE-68", "EE-70", "EE-71", "EE-75", "RPIDA-59"],
}


def curso(**cambios):
    """Copia del curso válido con los cambios indicados aplicados en la raíz."""
    d = copy.deepcopy(CURSO_VALIDO)
    d.update(cambios)
    return modelo.desde_dict(d)


def informe(**cambios):
    return validar.validar(curso(**cambios))


def reglas_con_error(inf) -> set[str]:
    return {h.regla for h in inf.errores}


class PuntoDePartida(unittest.TestCase):
    """Si el curso base no valida, todas las demás pruebas mienten."""

    def test_el_curso_base_es_valido(self):
        inf = informe()
        self.assertTrue(
            inf.valido,
            "el curso de referencia no debería tener errores:\n"
            + "\n".join(str(h) for h in inf.errores),
        )

    def test_el_informe_lista_los_grupos(self):
        self.assertIn("961, 962", informe().texto())

    def test_carga_el_calendario_del_ciclo(self):
        # Sin calendario, R6 protesta a gritos.
        self.assertNotIn("R6", reglas_con_error(informe()))


class Regla1Porcentajes(unittest.TestCase):
    def test_los_rubros_deben_sumar_cien(self):
        ev = copy.deepcopy(CURSO_VALIDO["evaluacion"])
        ev["rubros"][0]["porcentaje"] = 25
        self.assertIn("R1", reglas_con_error(informe(evaluacion=ev)))

    def test_avisa_del_error_con_el_desglose(self):
        ev = copy.deepcopy(CURSO_VALIDO["evaluacion"])
        ev["rubros"][0]["porcentaje"] = 25
        mensajes = " ".join(h.mensaje for h in informe(evaluacion=ev).errores)
        self.assertIn("105", mensajes)

    def test_rechaza_exencion_por_debajo_de_la_minima_aprobatoria(self):
        ev = copy.deepcopy(CURSO_VALIDO["evaluacion"])
        ev["exencion_ordinario"] = 55
        inf = informe(evaluacion=ev)
        self.assertIn("R1", reglas_con_error(inf))
        self.assertIn("65", " ".join(h.mensaje for h in inf.errores))

    def test_acepta_la_exencion_de_ochenta(self):
        self.assertNotIn("R1", reglas_con_error(informe()))

    def test_avisa_si_los_rubros_se_apartan_del_esquema_declarado(self):
        ev = copy.deepcopy(CURSO_VALIDO["evaluacion"])
        ev["rubros"][1]["porcentaje"] = 30
        ev["rubros"][2]["porcentaje"] = 50
        avisos = [h for h in informe(evaluacion=ev).de(validar.AVISO) if h.regla == "R1"]
        self.assertTrue(avisos, "no avisó de la divergencia con el catálogo")


class Regla2Metas(unittest.TestCase):
    def test_detecta_el_defecto_del_ejemplo_961(self):
        """El total suma 100 pero los rubros no: el error real del ejemplo dorado."""
        metas = copy.deepcopy(CURSO_VALIDO["metas"])
        for m in metas:  # todo se imputa a tareas; el total sigue siendo 100
            m["rubro"] = "tareas"
        inf = informe(metas=metas)
        self.assertIn("R2", reglas_con_error(inf))
        mensajes = " ".join(h.mensaje for h in inf.errores if h.regla == "R2")
        self.assertIn("Proyecto final", mensajes)
        self.assertIn("Exámenes", mensajes)

    def test_el_total_correcto_no_absuelve_al_rubro_incorrecto(self):
        metas = copy.deepcopy(CURSO_VALIDO["metas"])
        metas[1]["rubro"] = "proyecto"  # 10 puntos cambian de rubro; el total no varía
        inf = informe(metas=metas)
        mensajes = " ".join(h.mensaje for h in inf.errores if h.regla == "R2")
        self.assertNotIn("El valor de las metas suma", mensajes)
        self.assertIn("R2", reglas_con_error(inf))

    def test_el_total_de_las_metas_debe_igualar_al_esquema(self):
        metas = copy.deepcopy(CURSO_VALIDO["metas"])
        metas[1]["valor"] = 5
        self.assertIn("R2", reglas_con_error(informe(metas=metas)))

    def test_rechaza_meta_imputada_a_un_rubro_inexistente(self):
        metas = copy.deepcopy(CURSO_VALIDO["metas"])
        metas[1]["rubro"] = "participacion"
        inf = informe(metas=metas)
        self.assertIn("R2", reglas_con_error(inf))
        self.assertIn("participacion", " ".join(h.mensaje for h in inf.errores))

    def test_dos_metas_con_el_mismo_id_son_error_de_regla(self):
        """Con ids libres la colisión deja de ser evidente al leer el YAML, y el grafo
        construye la clave de cada nodo con el id: la segunda pisaría a la primera."""
        metas = copy.deepcopy(CURSO_VALIDO["metas"])
        metas[2]["id"] = metas[1]["id"]      # dos metas "1.1"
        inf = informe(metas=metas)
        self.assertIn("R2", reglas_con_error(inf))
        mensajes = " ".join(h.mensaje for h in inf.errores if h.regla == "R2")
        self.assertIn(metas[1]["id"], mensajes)

    def test_el_curso_con_ids_repetidos_carga_igual(self):
        """Es un defecto de regla, no de esquema: el curso tiene que poder cargarse para
        poder inspeccionarlo. Si reventara al cargar, quien lo escribió no vería el resto."""
        metas = copy.deepcopy(CURSO_VALIDO["metas"])
        metas[2]["id"] = metas[1]["id"]
        c = curso(metas=metas)               # no lanza ErrorModelo
        self.assertEqual(len(metas), len(c.metas))


class Regla3Parciales(unittest.TestCase):
    def test_exige_dos_parciales_segun_el_articulo_68(self):
        metas = copy.deepcopy(CURSO_VALIDO["metas"])
        for m in metas:
            if m["tipo"] == "examen_parcial":
                m["tipo"] = "aprendizaje"
        inf = informe(metas=metas)
        self.assertIn("R3", reglas_con_error(inf))
        self.assertIn("68", " ".join(h.mensaje for h in inf.errores))

    def test_un_solo_parcial_no_basta(self):
        metas = copy.deepcopy(CURSO_VALIDO["metas"])
        next(m for m in metas if m["id"] == "P2")["tipo"] = "aprendizaje"
        self.assertIn("R3", reglas_con_error(informe(metas=metas)))


class Regla4Unidades(unittest.TestCase):
    def test_toda_unidad_debe_tener_meta(self):
        unidades = CURSO_VALIDO["unidades"] + [{"numero": "IV", "nombre": "Gobernanza"}]
        inf = informe(unidades=unidades)
        self.assertIn("R4", reglas_con_error(inf))
        self.assertIn("IV", " ".join(h.mensaje for h in inf.errores))

    def test_rechaza_meta_de_una_unidad_que_no_existe_en_el_pua(self):
        metas = copy.deepcopy(CURSO_VALIDO["metas"])
        metas[1]["unidad"] = "IX"
        self.assertIn("R4", reglas_con_error(informe(metas=metas)))

    def test_avisa_de_los_temas_del_pua_que_nadie_cubre(self):
        unidades = copy.deepcopy(CURSO_VALIDO["unidades"])
        unidades[0]["temas"] = ["1.1. Definición de Big Data", "1.2. Las cinco V"]
        avisos = [h for h in informe(unidades=unidades).de(validar.AVISO) if h.regla == "R4"]
        self.assertTrue(avisos, "no avisó de los temas sin meta")

    def test_no_avisa_de_un_tema_que_si_esta_cubierto(self):
        unidades = copy.deepcopy(CURSO_VALIDO["unidades"])
        unidades[0]["temas"] = ["1.1. Definición de Big Data"]
        metas = copy.deepcopy(CURSO_VALIDO["metas"])
        metas[1]["cubre_temas"] = ["1.1. Definición de Big Data"]
        avisos = [
            h
            for h in informe(unidades=unidades, metas=metas).de(validar.AVISO)
            if h.regla == "R4"
        ]
        self.assertEqual([], avisos)


class Regla5Semanas(unittest.TestCase):
    def test_ninguna_semana_puede_quedar_vacia(self):
        metas = [m for m in copy.deepcopy(CURSO_VALIDO["metas"]) if m["id"] != "1.2"]
        inf = informe(metas=metas)
        self.assertIn("R5", reglas_con_error(inf))
        self.assertIn("3, 4", " ".join(h.mensaje for h in inf.errores))

    def test_rechaza_la_semana_17_que_trae_la_plantilla(self):
        """La plantilla CIAD tiene 17 filas; el ciclo 2026-2 tiene 16 semanas."""
        metas = copy.deepcopy(CURSO_VALIDO["metas"])
        metas[-1]["semanas"] = [14, 15, 16, 17]
        inf = informe(metas=metas)
        self.assertIn("R5", reglas_con_error(inf))
        self.assertIn("17", " ".join(h.mensaje for h in inf.errores))


class Regla6Fechas(unittest.TestCase):
    def _con_fecha(self, f):
        metas = copy.deepcopy(CURSO_VALIDO["metas"])
        metas[1]["sesiones"][0]["fecha"] = f
        return informe(metas=metas)

    def test_rechaza_entrega_en_dia_de_suspension(self):
        inf = self._con_fecha(date(2026, 9, 16))  # Independencia
        self.assertIn("R6", reglas_con_error(inf))
        self.assertIn("Independencia", " ".join(h.mensaje for h in inf.errores))

    def test_rechaza_entrega_despues_del_fin_de_cursos(self):
        inf = self._con_fecha(date(2026, 12, 1))
        self.assertIn("R6", reglas_con_error(inf))

    def test_acepta_un_dia_habil(self):
        self.assertNotIn("R6", reglas_con_error(self._con_fecha(date(2026, 9, 15))))

    def test_sin_calendario_del_ciclo_no_da_las_fechas_por_buenas(self):
        meta = copy.deepcopy(CURSO_VALIDO["meta"])
        meta["ciclo"] = "2099-1"
        inf = informe(meta=meta)
        self.assertIn("R6", reglas_con_error(inf))
        self.assertIn("2099-1", " ".join(h.mensaje for h in inf.errores))


class Regla7CitasYFirmas(unittest.TestCase):
    def test_exige_las_citas_obligatorias(self):
        inf = informe(citas=["EE-66"])
        self.assertIn("R7", reglas_con_error(inf))
        self.assertIn("EE-70", " ".join(h.mensaje for h in inf.errores))

    def test_semipresencial_exige_el_articulo_75(self):
        citas = [c for c in CURSO_VALIDO["citas"] if c != "EE-75"]
        inf = informe(citas=citas)
        self.assertIn("EE-75", " ".join(h.mensaje for h in inf.errores))

    def test_la_unidad_practica_exige_el_articulo_74(self):
        ident = copy.deepcopy(CURSO_VALIDO["identificacion"])
        ident["practica"] = True
        inf = informe(identificacion=ident)
        self.assertIn("EE-74", " ".join(h.mensaje for h in inf.errores))

    def test_rechaza_una_cita_inventada(self):
        inf = informe(citas=CURSO_VALIDO["citas"] + ["EE-999"])
        self.assertIn("R7", reglas_con_error(inf))
        self.assertIn("EE-999", " ".join(h.mensaje for h in inf.errores))

    def test_rechaza_grupos_repetidos(self):
        inf = informe(grupos=["961", "961"])
        self.assertIn("R7", reglas_con_error(inf))

    def test_un_curso_sin_grupos_no_se_puede_construir(self):
        with self.assertRaises(modelo.ErrorModelo):
            curso(grupos=[])


class Regla8IEDI(unittest.TestCase):
    def test_exige_la_descripcion_general_completa(self):
        contenido = copy.deepcopy(CURSO_VALIDO["contenido"])
        del contenido["estrategia_general"]
        inf = informe(contenido=contenido)
        self.assertIn("IEDI 1.1", reglas_con_error(inf))

    def test_toda_meta_evaluable_necesita_evidencia(self):
        metas = copy.deepcopy(CURSO_VALIDO["metas"])
        metas[1]["evidencias"] = []
        self.assertIn("IEDI 1.5", reglas_con_error(informe(metas=metas)))

    def test_la_meta_de_encuadre_puede_valer_cero(self):
        self.assertNotIn("IEDI 1.5", reglas_con_error(informe()))

    def test_semipresencial_debe_distinguir_presencial_de_virtual(self):
        metas = copy.deepcopy(CURSO_VALIDO["metas"])
        for m in metas:
            m["sesiones"] = [s for s in m["sesiones"] if s["ambiente"] == "virtual"]
        self.assertIn("IEDI 1.6", reglas_con_error(informe(metas=metas)))

    def test_toda_meta_se_describe_en_pasos(self):
        metas = copy.deepcopy(CURSO_VALIDO["metas"])
        metas[1]["sesiones"][0]["pasos"] = []
        self.assertIn("IEDI 1.7", reglas_con_error(informe(metas=metas)))

    def test_recuerda_los_indicadores_que_dependen_de_la_plataforma(self):
        recordatorios = {h.regla for h in informe().de(validar.RECORDATORIO)}
        self.assertIn("IEDI 3.5", recordatorios)  # Foro de dudas
        self.assertIn("IEDI 3.1", recordatorios)

    def test_la_modalidad_escolarizada_no_se_rige_por_el_iedi(self):
        ident = copy.deepcopy(CURSO_VALIDO["identificacion"])
        ident["modalidad"] = "escolarizada"
        citas = [c for c in CURSO_VALIDO["citas"] if c != "EE-75"]
        inf = informe(identificacion=ident, citas=citas)
        self.assertEqual([], [h for h in inf.hallazgos if h.regla.startswith("IEDI 1")])
        self.assertTrue(inf.valido, "\n".join(str(h) for h in inf.errores))


class GuardiaDeEstilo(unittest.TestCase):
    """El documento lo lee un alumno sin el PUA ni el repositorio delante.

    La fuga que motivó el guardia fue real: un `detalle` de rubro se escribió como
    «nueve prácticas conforme a la §VI del PUA» —la taquigrafía que AGENTS.md usa para
    mapear secciones— y acabó impresa en el .docx entregable.
    """

    def _avisos_de_estilo(self, inf) -> list[str]:
        return [h.mensaje for h in inf.de(validar.AVISO) if h.regla == "ESTILO"]

    def test_el_curso_base_no_tiene_jerga(self):
        self.assertEqual([], self._avisos_de_estilo(informe()))

    def test_denuncia_la_taquigrafia_de_seccion_en_un_rubro(self):
        ev = copy.deepcopy(CURSO_VALIDO["evaluacion"])
        ev["rubros"][0]["detalle"] = "dos parciales conforme a la §VIII del PUA"
        avisos = self._avisos_de_estilo(informe(evaluacion=ev))
        self.assertEqual(1, len(avisos), avisos)
        self.assertIn("§VIII", avisos[0])

    def test_denuncia_la_jerga_en_lo_que_el_alumno_lee(self):
        """No solo en los rubros: cualquier texto que acabe impreso."""
        metas = copy.deepcopy(CURSO_VALIDO["metas"])
        metas[0]["enunciado"] = "Revisar el curso.yaml del proyecto."
        self.assertEqual(1, len(self._avisos_de_estilo(informe(metas=metas))))

    def test_la_jerga_avisa_pero_no_invalida(self):
        """Si el PUA trae literalmente la marca, copiarla es lo correcto: decide el
        profesor. Por eso es aviso y no error."""
        ev = copy.deepcopy(CURSO_VALIDO["evaluacion"])
        ev["rubros"][0]["detalle"] = "según la §VIII"
        inf = informe(evaluacion=ev)
        self.assertTrue(inf.valido)
        self.assertNotIn("ESTILO", reglas_con_error(inf))


class ArrastreDeAvisos(unittest.TestCase):
    def test_los_avisos_del_pua_llegan_al_informe(self):
        inf = informe(avisos=["La práctica 3 no trae duración en el PUA oficial."])
        mensajes = [h.mensaje for h in inf.de(validar.AVISO) if h.regla == "PUA"]
        self.assertEqual(1, len(mensajes))


if __name__ == "__main__":
    unittest.main(verbosity=2)
