"""Pruebas del grafo del dominio.

Las dos que importan son las dos preguntas de REQ-31 —qué temas quedaron sin meta y qué
materias comparten competencias—, y se prueban con materias sintéticas: sobre el repositorio
real la respuesta cambia cada vez que alguien escribe un curso, y una prueba que depende de
eso deja de significar algo.

Contra los archivos reales se prueba lo que sí debe ser estable: que el PUA se lee completo y
que ninguna arista apunta al vacío.
"""

from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

import grafo  # noqa: E402

PUA_REAL = RAIZ / "puas" / "md" / "39056-big-data.md"
CURSO_REAL = RAIZ / "cursos" / "2026-2" / "39056-big-data" / "curso.yaml"

PUA_SINTETICO = """---
clave: "{clave}"
nombre: "{nombre}"
programa_educativo: "Programa de prueba"
---

# PUA {clave} — {nombre}

## III. COMPETENCIA GENERAL DE LA UNIDAD DE APRENDIZAJE

{competencia}

## V. DESARROLLO POR UNIDADES

### UNIDAD I. Fundamentos

**Competencia:** Identificar los fundamentos, mediante ejemplos, para probar el grafo.

**Duración:** 4 horas

**Contenido:**

- 1.1. Tema que sí tiene meta
- 1.2. Tema que quedó suelto

## VI. ESTRUCTURA DE LAS PRÁCTICAS DE LABORATORIO

| No. | Unidad | Nombre de la Práctica | Procedimiento | Recursos | Duración |
|---|---|---|---|---|---|
| 1 | I | Práctica con meta | 1. Hacer. | Nada | 2 horas |
| 2 | I | Práctica sin meta | 1. Hacer. | Nada | 2 horas |

## VII. MÉTODO DE TRABAJO

Prueba.
"""

COMPETENCIA = (
    "Analizar datos mediante herramientas de prueba, para verificar el grafo, "
    "con rigor y honestidad."
)


def escribir_pua(destino: Path, clave: str, nombre: str, competencia: str = COMPETENCIA) -> Path:
    ruta = destino / f"{clave}-prueba.md"
    ruta.write_text(
        PUA_SINTETICO.format(clave=clave, nombre=nombre, competencia=competencia),
        encoding="utf-8",
    )
    return ruta


def escribir_curso(destino: Path, clave: str, cubre: list[str], grupos=None) -> Path:
    datos = {
        "meta": {"ciclo": "2026-2", "clave": clave, "pua_ref": f"puas/md/{clave}-prueba.md"},
        "profesor": "ara",
        "identificacion": {"nombre": "Materia de prueba", "modalidad": "semipresencial"},
        "unidades": [
            {
                "numero": "I",
                "nombre": "Fundamentos",
                "temas": ["1.1. Tema que sí tiene meta", "1.2. Tema que quedó suelto"],
            }
        ],
        "metas": [
            {
                "id": "1.1",
                "unidad": "I",
                "enunciado": "Probar el grafo.",
                "semanas": [1],
                "valor": 100,
                "cubre_temas": cubre,
                "practica_pua": 1,
                "evidencias": [{"nombre": "Reporte de prueba"}],
                "criterios_evaluacion": ["Entrega en tiempo."],
            }
        ],
        "evaluacion": {"esquema_id": "estandar-2026", "rubros": []},
        "grupos": grupos or ["001"],
        "citas": [],
    }
    ruta = destino / "curso.yaml"
    ruta.write_text(yaml.safe_dump(datos, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return ruta


class LecturaDelPuaReal(unittest.TestCase):
    def setUp(self):
        self.pua = grafo.leer_pua(PUA_REAL)

    def test_lee_las_cinco_unidades_con_sus_temas(self):
        self.assertEqual(5, len(self.pua["unidades"]))
        self.assertEqual(
            ["I", "II", "III", "IV", "V"], [u["numero"] for u in self.pua["unidades"]]
        )
        self.assertTrue(all(u["temas"] for u in self.pua["unidades"]))

    def test_lee_las_diez_practicas_de_la_seccion_vi(self):
        self.assertEqual(10, len(self.pua["practicas"]))
        self.assertEqual(list(range(1, 11)), [p["numero"] for p in self.pua["practicas"]])

    def test_lee_la_competencia_general_completa(self):
        self.assertIn("Gestionar datos masivos", self.pua["competencia_general"])
        self.assertTrue(self.pua["competencia_general"].endswith("."))


class GrafoDelRepositorio(unittest.TestCase):
    """Lo que debe ser cierto siempre, sin depender de qué cursos existan hoy."""

    @classmethod
    def setUpClass(cls):
        puas, cursos = grafo.descubrir()
        cls.g = grafo.construir(puas, cursos)
        cls.informe = grafo.auditar(cls.g)

    def test_ninguna_arista_apunta_al_vacio(self):
        self.assertEqual([], self.informe["Anclas rotas"])

    def test_estan_los_tipos_de_nodo_del_dominio(self):
        # REQ-30: PUA, Unidad, Competencia, Tema, Meta, Evidencia, Criterio, Semana,
        # Artículo, Plantilla, Profesor, Grupo, Curso.
        for tipo in grafo.TIPOS:
            self.assertTrue(self.g.de_tipo(tipo), f"no hay ningún nodo de tipo {tipo}")

    def test_cada_meta_cuelga_de_su_curso_y_de_su_unidad(self):
        for m in self.g.de_tipo("meta"):
            self.assertTrue(self.g.entrantes(m.id, "tiene_meta"), f"{m.id} sin curso")
            self.assertTrue(self.g.salientes(m.id, "desarrolla"), f"{m.id} sin unidad")

    def test_construir_dos_veces_da_el_mismo_grafo(self):
        puas, cursos = grafo.descubrir()
        self.assertEqual(self.g.a_dict(), grafo.construir(puas, cursos).a_dict())


class LasDosPreguntas(unittest.TestCase):
    """REQ-31, sobre materias sintéticas para que la respuesta sea comprobable."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="di-grafo-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def test_un_tema_sin_meta_aparece_en_la_auditoria(self):
        pua = escribir_pua(self.tmp, "99001", "Materia de prueba")
        curso = escribir_curso(self.tmp, "99001", cubre=["1.1. Tema que sí tiene meta"])
        informe = grafo.auditar(grafo.construir([pua], [curso]))

        sueltos = informe["Temas sin meta que los cubra"]
        self.assertEqual(1, len(sueltos))
        self.assertIn("1.2. Tema que quedó suelto", sueltos[0])

    def test_una_practica_sin_meta_aparece_en_la_auditoria(self):
        pua = escribir_pua(self.tmp, "99001", "Materia de prueba")
        curso = escribir_curso(self.tmp, "99001", cubre=["1.1. Tema que sí tiene meta"])
        informe = grafo.auditar(grafo.construir([pua], [curso]))

        self.assertEqual(
            ["Práctica 2. Práctica sin meta"], informe["Prácticas sin meta"]
        )

    def test_dos_materias_con_la_misma_competencia_salen_como_compartida(self):
        a = escribir_pua(self.tmp, "99001", "Materia A")
        b = escribir_pua(self.tmp, "99002", "Materia B")
        informe = grafo.auditar(grafo.construir([a, b], []))

        compartidas = informe["Competencias compartidas entre materias"]
        self.assertTrue(compartidas, "no detectó la competencia repetida")
        self.assertTrue(all("99001, 99002" in c for c in compartidas))

    def test_competencias_distintas_no_se_dan_por_compartidas(self):
        a = escribir_pua(self.tmp, "99001", "Materia A")
        b = escribir_pua(self.tmp, "99002", "Materia B", competencia="Otra cosa distinta.")
        informe = grafo.auditar(grafo.construir([a, b], []))

        # Las competencias de unidad sí coinciden (la plantilla sintética es la misma);
        # lo que no debe aparecer es la general, que se escribió distinta.
        self.assertNotIn(
            "Otra cosa distinta",
            " ".join(informe["Competencias compartidas entre materias"]),
        )

    def test_un_curso_cuyo_pua_no_esta_ingerido_se_reporta(self):
        curso = escribir_curso(self.tmp, "99009", cubre=[])
        informe = grafo.auditar(grafo.construir([], [curso]))
        self.assertEqual(1, len(informe["Cursos cuyo PUA no está ingerido"]))


class ElGrafoRegistraElHorario(unittest.TestCase):
    """D-04: el nodo del grupo lleva el horario declarado, legible en index.html."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="di-grafo-horario-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def test_el_nodo_del_grupo_lleva_sus_bloques(self):
        curso = escribir_curso(
            self.tmp, "99001", cubre=[],
            grupos=[{
                "numero": "961",
                "horario": {"bloques": [
                    {"dia": 0, "inicio": "12:00", "fin": "13:00", "ambiente": "presencial"},
                    {"dia": 1, "inicio": "17:00", "fin": "19:00", "ambiente": "virtual"},
                ]},
            }],
        )
        g = grafo.construir([], [curso])
        datos = g.nodos["grupo:2026-2:99001:961"].datos
        self.assertEqual([0], datos["dias_presencial"])
        self.assertEqual(
            ["lunes 12:00–13:00 presencial", "martes 17:00–19:00 virtual"],
            datos["bloques"],
        )

    def test_un_grupo_sin_bloques_no_gana_la_clave(self):
        curso = escribir_curso(self.tmp, "99002", cubre=[])
        g = grafo.construir([], [curso])
        self.assertNotIn("bloques", g.nodos["grupo:2026-2:99002:001"].datos)


class Archivos(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="di-grafo-salida-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        pua = escribir_pua(self.tmp, "99001", "Materia de prueba")
        curso = escribir_curso(self.tmp, "99001", cubre=["1.1. Tema que sí tiene meta"])
        self.g = grafo.construir([pua], [curso])
        self.rutas = grafo.escribir(self.g, grafo.auditar(self.g), self.tmp / "salida")

    def test_escribe_json_html_y_auditoria(self):
        self.assertEqual(
            ["grafo.json", "index.html", "AUDITORIA.md"], [r.name for r in self.rutas]
        )

    def test_el_json_es_estable_entre_corridas(self):
        antes = self.rutas[0].read_bytes()
        grafo.escribir(self.g, grafo.auditar(self.g), self.tmp / "salida")
        self.assertEqual(antes, self.rutas[0].read_bytes())

    def test_el_html_es_autocontenido(self):
        html = self.rutas[1].read_text(encoding="utf-8")
        for prohibido in ("<script src", "<link ", "@import", "http://", "https://"):
            self.assertNotIn(prohibido, html, f"el HTML depende de {prohibido!r}")
        self.assertIn('"nodos"', html)  # los datos van embebidos

    def test_la_auditoria_dice_cuantos_nodos_y_aristas(self):
        texto = self.rutas[2].read_text(encoding="utf-8")
        self.assertIn(f"{len(self.g.nodos)} nodos", texto)
        self.assertIn(f"{len(self.g.aristas)} aristas", texto)


if __name__ == "__main__":
    unittest.main()
