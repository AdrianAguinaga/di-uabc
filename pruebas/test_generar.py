"""Pruebas de la cadena completa: `curso.yaml` → documentos + `MANIFIESTO.yaml`.

Dos promesas que aquí se defienden y que ninguna revisión visual del `.docx` detecta:

  - un curso con errores de validación **no deja ni un archivo** en disco, y
  - el manifiesto ancla cada documento a su PUA, su calendario y su plantilla, con hashes
    que se pueden recomprobar meses después (regla invariable 7).

La exportación a PDF se omite (`pdf=False`): depende de que la máquina tenga Word y ya tiene
sus propias pruebas en `test_export_pdf.py`.
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

import calendario  # noqa: E402
import generar  # noqa: E402
import plantillas  # noqa: E402

CURSO = RAIZ / "cursos" / "2026-2" / "39056-big-data" / "curso.yaml"


def copia_del_curso(destino: Path, retoque=None) -> Path:
    """El curso real en un directorio temporal, para no ensuciar `cursos/`."""
    datos = yaml.safe_load(CURSO.read_text(encoding="utf-8"))
    if retoque:
        retoque(datos)
    ruta = destino / "curso.yaml"
    ruta.write_text(yaml.safe_dump(datos, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return ruta


class PaqueteDeBigData(unittest.TestCase):
    """Se genera una vez para toda la clase: renderizar dos documentos es caro."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="di-generar-"))
        cls.ruta = copia_del_curso(cls.tmp)
        cls.pasos: list[tuple] = []
        cls.paquete = generar.paquete(
            cls.ruta, pdf=False, traza=lambda *a: cls.pasos.append(a)
        )
        cls.manifiesto = yaml.safe_load(cls.paquete.manifiesto.read_text(encoding="utf-8"))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    # -- lo que produce -----------------------------------------------------

    def test_un_documento_por_grupo(self):
        nombres = sorted(p.name for p in (self.tmp / "salida").glob("*.docx"))
        self.assertEqual(
            ["DI-2026-2-39056-961.docx", "DI-2026-2-39056-962.docx"], nombres
        )

    def test_el_manifiesto_queda_junto_al_curso(self):
        # `resolve()` porque en Windows el temporal llega con el nombre corto 8.3.
        self.assertEqual(
            (self.tmp / "MANIFIESTO.yaml").resolve(), self.paquete.manifiesto.resolve()
        )

    def test_generar_no_toca_las_plantillas(self):
        self.assertEqual([], plantillas.verificar())

    def test_la_traza_reporta_cada_paso(self):
        etiquetas = [p[1] for p in self.pasos]
        self.assertEqual(
            ["validación", "grupo 961", "grupo 962", "MANIFIESTO"], etiquetas
        )
        self.assertTrue(all(p[0] == "✓" for p in self.pasos))

    # -- trazabilidad (regla invariable 7) ----------------------------------

    def test_el_manifiesto_ancla_el_pua_al_pdf_oficial(self):
        pua = self.manifiesto["pua"]
        self.assertTrue(pua["coincide"], "el PDF del PUA ya no hashea como se declaró")
        self.assertEqual(
            plantillas.sha256(RAIZ / pua["fuente"]), pua["sha256_declarado"]
        )

    def test_el_manifiesto_ancla_el_calendario(self):
        cal = self.manifiesto["calendario"]
        archivo = RAIZ / cal["archivo"]
        self.assertEqual(plantillas.sha256(archivo), cal["sha256"])
        self.assertEqual(calendario.cargar("2026-2").total_semanas, cal["semanas"])

    def test_el_manifiesto_ancla_la_plantilla_registrada(self):
        registrada = plantillas.cargar()["semipresencial"]
        self.assertEqual(registrada.sha256, self.manifiesto["plantilla"]["sha256"])
        self.assertEqual(registrada.version, self.manifiesto["plantilla"]["version"])

    def test_el_manifiesto_hashea_cada_archivo_producido(self):
        producidos = {p.name: p for p in self.paquete.archivos}
        self.assertEqual(len(producidos), len(self.manifiesto["archivos"]))
        for a in self.manifiesto["archivos"]:
            ruta = producidos[Path(a["ruta"]).name]
            self.assertEqual(plantillas.sha256(ruta), a["sha256"])
            self.assertEqual(ruta.stat().st_size, a["bytes"])

    def test_el_manifiesto_registra_profesor_esquema_y_commit(self):
        self.assertEqual("ara", self.manifiesto["profesor"]["id"])
        self.assertEqual("estandar-2026", self.manifiesto["evaluacion"]["esquema_id"])
        self.assertTrue(self.manifiesto["commit"])

    def test_el_manifiesto_lista_los_dos_grupos_con_su_horario(self):
        grupos = {g["numero"]: g for g in self.manifiesto["grupos"]}
        self.assertEqual({"961", "962"}, set(grupos))
        # El horario vive en el grupo: por eso las fechas de uno y otro divergen.
        self.assertNotEqual(
            grupos["961"]["dias_presencial"], grupos["962"]["dias_presencial"]
        )


class UnCursoInvalidoNoProduceNada(unittest.TestCase):
    """La regla que justifica el orden de la cadena: validar antes de escribir."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="di-generar-malo-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def test_porcentajes_que_no_suman_cien_detienen_la_cadena(self):
        def romper(d):
            d["evaluacion"]["rubros"][0]["porcentaje"] = 5  # 5 + 40 + 40 = 85

        ruta = copia_del_curso(self.tmp, romper)
        with self.assertRaises(generar.ErrorGenerar) as ctx:
            generar.paquete(ruta, pdf=False)

        self.assertIn("R1", str(ctx.exception))
        self.assertFalse((self.tmp / "salida").exists(), "renderizó pese al error")
        self.assertFalse((self.tmp / "MANIFIESTO.yaml").exists())

    def test_un_ciclo_sin_calendario_no_llega_a_renderizar(self):
        def romper(d):
            d["meta"]["ciclo"] = "1999-2"

        ruta = copia_del_curso(self.tmp, romper)
        with self.assertRaises(calendario.ErrorCalendario):
            generar.paquete(ruta, pdf=False)
        self.assertFalse((self.tmp / "salida").exists())


class Panel(unittest.TestCase):
    """El marco lo dibuja el script para que el orquestador no tenga que cuadrar anchuras."""

    ANCHO_TOTAL = generar.ANCHO + 2

    def test_todas_las_lineas_miden_lo_mismo(self):
        lineas = [
            generar.cabecera(),
            generar.linea("✓", "validación", "0 errores · 2 avisos · 5 recordatorios"),
            generar.linea("!", "grupo 961", "DI-2026-2-39056-961.docx · sin PDF"),
            generar.PIE,
        ]
        self.assertEqual({self.ANCHO_TOTAL}, {len(l) for l in lineas})

    def test_un_detalle_larguisimo_se_recorta_sin_romper_el_marco(self):
        l = generar.linea("✓", "archivo", "x" * 200)
        self.assertEqual(self.ANCHO_TOTAL, len(l))
        self.assertTrue(l.endswith("…│"))


if __name__ == "__main__":
    unittest.main()
