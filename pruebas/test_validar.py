"""Pruebas de la capa de validación.

El método es siempre el mismo: se parte de un curso válido y se rompe **una** cosa.
Si la regla no protesta, la regla no sirve.

La prueba que da sentido a todas las demás es
`test_detecta_el_defecto_del_ejemplo_961`: el ejemplo dorado suma 100 en total pero sus
rubros no cuadran, y ese es exactamente el error que R2 existe para atrapar.
"""

from __future__ import annotations

import copy
import inspect
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


def _en_puntos() -> dict:
    """`CURSO_VALIDO` con «Tareas» en puntos: declara 150 y sus aportes suman 140.

    Es el defecto real del DI de Contabilidad (531), hermano del defecto en porcentajes del
    961. Los rubros vecinos —Exámenes y Proyecto— siguen en porcentaje **a propósito**: R2
    nunca debe sumar unidades distintas entre sí.
    """
    d = copy.deepcopy(CURSO_VALIDO)
    tareas = next(r for r in d["evaluacion"]["rubros"] if r["id"] == "tareas")
    tareas["unidad"] = "puntos"
    tareas["total"] = 150
    puntos = {"0": 0, "1.1": 40, "1.2": 40, "2.1": 35, "2.2": 25}   # 140 de los 150
    for m in d["metas"]:
        if m["id"] in puntos:
            m["valor"] = puntos[m["id"]]
    return d


CURSO_EN_PUNTOS = _en_puntos()


def curso_en_puntos(retoque=None):
    """Copia del curso en puntos con un retoque opcional aplicado sobre el diccionario."""
    d = copy.deepcopy(CURSO_EN_PUNTOS)
    if retoque:
        retoque(d)
    return modelo.desde_dict(d)


def informe_en_puntos(retoque=None):
    return validar.validar(curso_en_puntos(retoque))


def _rubro(d, id_):
    return next(r for r in d["evaluacion"]["rubros"] if r["id"] == id_)


def _meta_de(d, id_):
    return next(m for m in d["metas"] if m["id"] == id_)


def _con_examenes_en_componentes() -> dict:
    """`CURSO_VALIDO` con los exámenes dentro de la actividad de otras metas.

    Es la forma del DI de Contabilidad (531): los tres exámenes viven en la actividad de las
    metas 2.4, 3.3 y 6.0, y **ninguna meta es de tipo `examen_parcial`**. Hasta la Fase 10 R3
    contaba cero aquí y el documento no validaba.

    Las metas P1 y P2 desaparecen; sus semanas (5 y 10) se absorben en 1.2 y 2.2 para que R5
    siga viendo las 16 semanas cubiertas. El rubro «Exámenes» conserva su 20 %, repartido
    ahora entre tres componentes (7 + 7 + 6).
    """
    d = copy.deepcopy(CURSO_VALIDO)
    next(r for r in d["evaluacion"]["rubros"] if r["id"] == "examenes")["parciales"] = 3
    d["metas"] = [m for m in d["metas"] if m["id"] not in ("P1", "P2")]
    examenes = {"1.2": ("Examen I", 7), "2.2": ("Examen II", 7), "3.1": ("Examen III", 6)}
    for m in d["metas"]:
        if m["id"] == "1.2":
            m["semanas"] = [3, 4, 5]      # absorbe la semana de P1
        if m["id"] == "2.2":
            m["semanas"] = [8, 9, 10]     # absorbe la semana de P2
        if m["id"] in examenes:
            etiqueta, valor = examenes[m["id"]]
            m["componentes"] = [{
                "rubro": "examenes", "valor": valor, "etiqueta": etiqueta,
                "tipo": "examen_parcial",
            }]
    return d


CURSO_CON_EXAMENES_EN_COMPONENTES = _con_examenes_en_componentes()


def curso_con_examenes(retoque=None):
    d = copy.deepcopy(CURSO_CON_EXAMENES_EN_COMPONENTES)
    if retoque:
        retoque(d)
    return modelo.desde_dict(d)


def informe_con_examenes(retoque=None):
    return validar.validar(curso_con_examenes(retoque))


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


class Regla1EsInsensibleALaUnidad(unittest.TestCase):
    """REQ-45 nombra a R1 además de a R2, pero R1 no necesitó cambio alguno.

    Sus cuatro comprobaciones (`validar.py:126-169`) miran la suma de `r.porcentaje` contra
    100, los ids de rubro duplicados, el umbral de exención y el catálogo de esquemas. Ninguna
    toca un valor de meta ni ninguna clave de unidad, y `porcentaje` existe igual en un rubro
    en puntos. Se fija en vez de implementarse, como D-12 y D-13 de la Fase 9.
    """

    def test_el_curso_en_puntos_no_produce_ningun_hallazgo_de_r1(self):
        """El curso defectuoso de la Fase 10 —150 declarados, 140 sumados— es problema de R2."""
        inf = informe_en_puntos()
        self.assertEqual([], [h for h in inf.hallazgos if h.regla == "R1"])

    def test_r1_calla_aunque_los_valores_de_las_metas_esten_del_todo_mal(self):
        """Duplicar el valor de todas las metas rompe R2 y deja R1 en silencio."""
        metas = copy.deepcopy(CURSO_VALIDO["metas"])
        for m in metas:
            m["valor"] = m["valor"] * 2
        inf = informe(metas=metas)
        self.assertIn("R2", reglas_con_error(inf))
        self.assertNotIn("R1", reglas_con_error(inf))

    def test_poner_un_rubro_en_puntos_no_altera_lo_que_r1_comprueba(self):
        """`porcentaje` sigue siendo lo que cuenta contra el 100, también en puntos."""
        sin = [h.mensaje for h in informe().hallazgos if h.regla == "R1"]
        con = [h.mensaje for h in informe_en_puntos().hallazgos if h.regla == "R1"]
        self.assertEqual(sin, con)

    def test_el_codigo_de_r1_no_menciona_la_unidad_de_ningun_rubro(self):
        """La afirmación, escrita como prueba: si alguien mete aritmética de unidades en R1,
        esto se rompe y le obliga a decidirlo en vez de colarlo."""
        fuente = inspect.getsource(validar._Validador.regla_1)
        for termino in (".base", "a_porcentaje", ".unidad", ".total", ".valor"):
            self.assertNotIn(termino, fuente, f"R1 pasó a leer «{termino}»")


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

    # -- Fase 10: la unidad declarada -------------------------------------

    def test_el_rubro_en_puntos_denuncia_el_faltante_en_puntos(self):
        """Criterio 1: 150 declarados, 140 sumados, y el error se redacta en puntos."""
        inf = informe_en_puntos()
        self.assertIn("R2", reglas_con_error(inf))
        mensajes = " ".join(h.mensaje for h in inf.errores if h.regla == "R2")
        self.assertIn("140 pts", mensajes)
        self.assertIn("150 pts", mensajes)

    def test_corregido_el_total_el_curso_en_puntos_valida(self):
        """Criterio 2: con el total en 140, R2 calla aunque los vecinos estén en porcentaje."""
        inf = informe_en_puntos(lambda d: _rubro(d, "tareas").update({"total": 140}))
        self.assertNotIn("R2", reglas_con_error(inf))

    def test_r2_nunca_suma_unidades_distintas_entre_si(self):
        """El rubro en puntos cuadra y el vecino en porcentaje no: solo protesta el vecino."""
        def retoque(d):
            _rubro(d, "tareas")["total"] = 140
            _meta_de(d, "3.1")["valor"] = 10      # proyecto: 10+10+15 = 35 de 40
        inf = informe_en_puntos(retoque)
        mensajes = " ".join(h.mensaje for h in inf.errores if h.regla == "R2")
        self.assertIn("Proyecto final", mensajes)
        self.assertNotIn("Tareas y actividades de clase", mensajes)

    def test_el_componente_cuenta_para_el_total_de_su_rubro(self):
        """El hueco general: hasta ahora un componente no sumaba en ningún rubro, nunca."""
        def retoque(d):
            _meta_de(d, "2.2")["componentes"] = [{
                "rubro": "tareas", "valor": 10, "etiqueta": "Presentación",
                "tipo": "actividad",
            }]
        inf = informe_en_puntos(retoque)          # 140 + 10 = 150, los que declara
        self.assertNotIn("R2", reglas_con_error(inf))

    def test_un_componente_en_el_mismo_rubro_que_su_meta_no_genera_hallazgo(self):
        """D-09: «Reporte 5 pts» y «Presentación 5 pts» dentro de la misma meta es legítimo."""
        def retoque(d):
            _rubro(d, "tareas")["total"] = 140
            _meta_de(d, "1.1")["valor"] = 30
            _meta_de(d, "1.1")["componentes"] = [{
                "rubro": "tareas", "valor": 10, "etiqueta": "Presentación",
                "tipo": "actividad",
            }]
        inf = informe_en_puntos(retoque)
        self.assertEqual([], [h for h in inf.hallazgos if h.regla == "R2"])

    def test_veintidos_aportes_de_puntos_exactos_no_inventan_un_faltante(self):
        """D-06, medido: convirtiendo aporte a aporte, 21×7+3 sobre 150 dan
        29.99999999999999 y R2 denunciaría un curso correcto. Se convierte por rubro."""
        def retoque(d):
            otras = [m for m in d["metas"] if m["rubro"] != "tareas"]
            nuevas = [_meta(f"T{i}", "I", [(i % 16) + 1], 7, "tareas") for i in range(21)]
            nuevas.append(_meta("T21", "I", [1], 3, "tareas"))   # 21×7 + 3 = 150 exactos
            d["metas"] = otras + nuevas
        inf = informe_en_puntos(retoque)
        self.assertNotIn("R2", reglas_con_error(inf))

    def test_un_componente_en_un_rubro_inexistente_es_error_de_r2(self):
        def retoque(d):
            _meta_de(d, "2.2")["componentes"] = [{
                "rubro": "participacion", "valor": 10, "etiqueta": "Presentación",
                "tipo": "actividad",
            }]
        inf = informe_en_puntos(retoque)
        self.assertIn("R2", reglas_con_error(inf))
        mensajes = " ".join(h.mensaje for h in inf.errores if h.regla == "R2")
        self.assertIn("participacion", mensajes)
        self.assertIn("Presentación", mensajes)

    def test_el_curso_con_un_componente_mal_imputado_carga_igual(self):
        """Precedente de D-17 de la Fase 9: es defecto de regla, no de esquema."""
        def retoque(d):
            _meta_de(d, "2.2")["componentes"] = [{
                "rubro": "participacion", "valor": 10, "etiqueta": "Presentación",
                "tipo": "actividad",
            }]
        c = curso_en_puntos(retoque)              # no lanza ErrorModelo
        self.assertEqual(1, len(next(m for m in c.metas if m.id == "2.2").componentes))

    def test_un_componente_con_valor_negativo_es_error_de_r2(self):
        def retoque(d):
            _meta_de(d, "2.2")["componentes"] = [{
                "rubro": "tareas", "valor": -10, "etiqueta": "Presentación",
                "tipo": "actividad",
            }]
        inf = informe_en_puntos(retoque)
        mensajes = " ".join(h.mensaje for h in inf.errores if h.regla == "R2")
        self.assertIn("Componentes con valor negativo", mensajes)
        self.assertIn("Presentación", mensajes)


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

    # -- Fase 10: un examen es un aporte, no necesariamente una meta ------

    def test_tres_examenes_en_componentes_y_ninguna_meta_pasan_r3(self):
        """Criterio 4 del roadmap: es la forma real del DI de Contabilidad (531)."""
        c = curso_con_examenes()
        self.assertEqual([], [m for m in c.metas if m.tipo == "examen_parcial"])
        inf = validar.validar(c)
        self.assertNotIn("R3", reglas_con_error(inf))
        self.assertNotIn("R2", reglas_con_error(inf))

    def test_un_solo_examen_en_componente_no_basta(self):
        """Criterio 4, la otra mitad: con uno solo falla, y con el mensaje del Art. 68."""
        def retoque(d):
            for m in d["metas"]:
                if m["id"] in ("2.2", "3.1"):
                    m.pop("componentes", None)
                if m["id"] == "1.2":
                    m["componentes"][0]["valor"] = 20      # el rubro sigue cuadrando
            next(r for r in d["evaluacion"]["rubros"] if r["id"] == "examenes")["parciales"] = 1
        inf = informe_con_examenes(retoque)
        self.assertIn("R3", reglas_con_error(inf))
        self.assertIn("68", " ".join(h.mensaje for h in inf.errores if h.regla == "R3"))

    def test_una_meta_de_examen_y_un_componente_de_examen_cuentan_dos(self):
        """D-10: cada aporte cuenta uno, sin deduplicar por meta."""
        metas = copy.deepcopy(CURSO_VALIDO["metas"])
        next(m for m in metas if m["id"] == "P2")["tipo"] = "aprendizaje"
        next(m for m in metas if m["id"] == "P1")["componentes"] = [{
            "rubro": "examenes", "valor": 0, "etiqueta": "Examen I bis",
            "tipo": "examen_parcial",
        }]
        inf = informe(metas=metas)                 # 1 meta + 1 componente = 2 parciales
        self.assertNotIn("R3", reglas_con_error(inf))

    def test_el_aviso_de_parciales_no_habla_solo_de_metas(self):
        """D-11: el texto del aviso deja de mentir en cuanto un examen vive en un componente."""
        def retoque(d):
            next(r for r in d["evaluacion"]["rubros"] if r["id"] == "examenes")["parciales"] = 2
        inf = informe_con_examenes(retoque)         # declara 2, hay 3
        avisos = [h for h in inf.de(validar.AVISO) if h.regla == "R3"]
        self.assertTrue(avisos, "no avisó de la divergencia entre `parciales:` y los exámenes")
        self.assertNotIn("metas de tipo", avisos[0].mensaje)
        self.assertIn("3", avisos[0].mensaje)


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
