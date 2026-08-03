"""Pruebas de la custodia de plantillas.

Lo que estas pruebas defienden es una sola promesa: **generar un documento nunca modifica
la plantilla**. Si esa promesa se rompe, el formato institucional se degrada una copia a la
vez y nadie se entera hasta que el CIAD rechaza un diseño.
"""

from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

import plantillas  # noqa: E402


class EnDirectorioTemporal(unittest.TestCase):
    """Trabaja sobre una copia desechable: nunca toca plantillas/ de verdad."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="di-plantillas-"))
        self._original = (plantillas.DIR, plantillas.REGISTRO, plantillas.HISTORICO)
        plantillas.DIR = self.tmp
        plantillas.REGISTRO = self.tmp / "REGISTRO.yaml"
        plantillas.HISTORICO = self.tmp / "historico"

    def tearDown(self):
        plantillas.DIR, plantillas.REGISTRO, plantillas.HISTORICO = self._original
        shutil.rmtree(self.tmp, ignore_errors=True)


class Registro(EnDirectorioTemporal):
    def test_registra_las_tres_modalidades(self):
        plantillas.registrar()
        entradas = plantillas.cargar()
        self.assertEqual(
            {"semipresencial", "escolarizada", "a_distancia"}, set(entradas)
        )
        for e in entradas.values():
            self.assertTrue(e.ruta.exists(), f"no se copió {e.archivo}")
            self.assertEqual(64, len(e.sha256))

    def test_la_copia_es_identica_al_original(self):
        plantillas.registrar()
        for mod, e in plantillas.cargar().items():
            self.assertEqual(
                plantillas.sha256(RAIZ / e.origen),
                plantillas.sha256(e.ruta),
                f"la plantilla {mod} no es idéntica a su original",
            )

    def test_registrar_dos_veces_no_cambia_nada(self):
        plantillas.registrar()
        antes = plantillas.REGISTRO.read_bytes()
        self.assertEqual([], plantillas.registrar(hoy=date(2030, 1, 1)))
        self.assertEqual(antes, plantillas.REGISTRO.read_bytes())

    def test_la_fecha_de_registro_no_se_mueve_sola(self):
        plantillas.registrar(hoy=date(2026, 8, 3))
        plantillas.registrar(hoy=date(2030, 1, 1))
        self.assertEqual(
            "2026-08-03", plantillas.cargar()["semipresencial"].registrado
        )

    def test_repone_una_plantilla_borrada(self):
        plantillas.registrar()
        e = plantillas.cargar()["escolarizada"]
        e.ruta.unlink()
        plantillas.registrar()
        self.assertTrue(e.ruta.exists())


class Verificacion(EnDirectorioTemporal):
    def setUp(self):
        super().setUp()
        plantillas.registrar()

    def test_un_juego_intacto_no_tiene_problemas(self):
        self.assertEqual([], plantillas.verificar())

    def test_detecta_que_alguien_escribio_sobre_la_plantilla(self):
        ruta = plantillas.cargar()["semipresencial"].ruta
        with ruta.open("ab") as f:
            f.write(b"un byte de mas")
        problemas = plantillas.verificar()
        self.assertEqual(1, len(problemas))
        self.assertIn("semipresencial", problemas[0])

    def test_detecta_una_plantilla_ausente(self):
        plantillas.cargar()["a_distancia"].ruta.unlink()
        self.assertIn("a_distancia", " ".join(plantillas.verificar()))

    def test_sin_registro_lo_dice_y_no_revienta(self):
        plantillas.REGISTRO.unlink()
        self.assertIn("registrar", " ".join(plantillas.verificar()))


class CopiaDeTrabajo(EnDirectorioTemporal):
    def setUp(self):
        super().setUp()
        plantillas.registrar()

    def test_entrega_una_copia_identica(self):
        destino = self.tmp / "salida" / "DI-2026-2-39056-961.docx"
        plantillas.copia_de_trabajo("semipresencial", destino)
        self.assertEqual(
            plantillas.cargar()["semipresencial"].sha256, plantillas.sha256(destino)
        )

    def test_crea_el_directorio_de_salida(self):
        destino = self.tmp / "no" / "existe" / "todavia" / "x.docx"
        self.assertTrue(plantillas.copia_de_trabajo("a_distancia", destino).exists())

    def test_rellenar_la_copia_no_toca_la_plantilla(self):
        """La promesa entera del módulo, en una prueba."""
        antes = plantillas.sha256(plantillas.cargar()["semipresencial"].ruta)
        destino = self.tmp / "salida" / "uno.docx"
        plantillas.copia_de_trabajo("semipresencial", destino)
        with destino.open("ab") as f:  # simula el renderizado
            f.write(b"contenido rellenado")
        plantillas.copia_de_trabajo("semipresencial", self.tmp / "salida" / "dos.docx")
        self.assertEqual(antes, plantillas.sha256(plantillas.cargar()["semipresencial"].ruta))
        self.assertEqual([], plantillas.verificar())

    def test_se_niega_a_copiar_una_plantilla_alterada(self):
        ruta = plantillas.cargar()["escolarizada"].ruta
        with ruta.open("ab") as f:
            f.write(b"alterada")
        with self.assertRaises(plantillas.ErrorPlantilla):
            plantillas.copia_de_trabajo("escolarizada", self.tmp / "x.docx")

    def test_modalidad_desconocida(self):
        with self.assertRaises(plantillas.ErrorPlantilla) as ctx:
            plantillas.copia_de_trabajo("hibrida", self.tmp / "x.docx")
        self.assertIn("hibrida", str(ctx.exception))


class Actualizacion(EnDirectorioTemporal):
    def setUp(self):
        super().setUp()
        plantillas.registrar(hoy=date(2026, 8, 3))
        # Una "versión nueva" del CIAD: el original de a distancia, que es otro archivo.
        self.nueva = self.tmp / "CIAD_nueva.docx"
        shutil.copy2(RAIZ / "referencias" / "CIAD_DI_Plantilla_A_Distancia (2).docx", self.nueva)

    def test_sustituye_la_plantilla_y_registra_el_hash_nuevo(self):
        antes = plantillas.cargar()["a_distancia"].sha256
        plantillas.actualizar("a_distancia", self.nueva, version="2026-1")
        e = plantillas.cargar()["a_distancia"]
        self.assertNotEqual(antes, e.sha256)
        self.assertEqual(plantillas.sha256(self.nueva), e.sha256)
        self.assertEqual("2026-1", e.version)
        self.assertEqual([], plantillas.verificar("a_distancia"))

    def test_archiva_la_anterior_sin_perderla(self):
        antes = plantillas.cargar()["a_distancia"]
        plantillas.actualizar("a_distancia", self.nueva, version="2026-1", hoy=date(2026, 9, 1))
        archivada = plantillas.HISTORICO / f"a_distancia-2025-1-{antes.sha256[:8]}.docx"
        self.assertTrue(archivada.exists(), "la plantilla saliente se perdió")
        self.assertEqual(antes.sha256, plantillas.sha256(archivada))

    def test_deja_rastro_en_el_historial(self):
        plantillas.actualizar("a_distancia", self.nueva, version="2026-1", hoy=date(2026, 9, 1))
        historial = plantillas.cargar()["a_distancia"].historial
        self.assertEqual(1, len(historial))
        self.assertEqual("2025-1", historial[0]["version"])
        self.assertEqual("2026-09-01", historial[0]["reemplazada"])

    def test_actualizar_a_la_misma_version_no_hace_nada(self):
        e = plantillas.cargar()["a_distancia"]
        mensaje = plantillas.actualizar("a_distancia", RAIZ / e.origen)
        self.assertIn("no se toca nada", mensaje)
        self.assertEqual([], plantillas.cargar()["a_distancia"].historial)

    def test_avisa_de_revisar_los_hechos_estructurales(self):
        mensaje = plantillas.actualizar("a_distancia", self.nueva, version="2026-1")
        self.assertIn("config/plantillas.yaml", mensaje)

    def test_rechaza_un_archivo_que_no_es_docx(self):
        pdf = self.tmp / "cosa.pdf"
        pdf.write_bytes(b"%PDF-1.4")
        with self.assertRaises(plantillas.ErrorPlantilla):
            plantillas.actualizar("a_distancia", pdf)

    def test_rechaza_una_modalidad_desconocida(self):
        with self.assertRaises(plantillas.ErrorPlantilla):
            plantillas.actualizar("hibrida", self.nueva)


class RegistroReal(unittest.TestCase):
    """Sobre el juego versionado en git, sin tocarlo."""

    def test_el_repositorio_trae_las_tres_plantillas_verificadas(self):
        self.assertEqual(
            [], plantillas.verificar(), "el juego de plantillas del repo no cuadra"
        )

    def test_config_y_registro_hablan_de_las_mismas_modalidades(self):
        self.assertEqual(set(plantillas._config()), set(plantillas.cargar()))


if __name__ == "__main__":
    unittest.main(verbosity=2)
