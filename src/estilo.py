"""Estilo tipográfico CIAD: de énfasis semántico a runs de Word.

`curso.yaml` nunca dice «negrita». Dice `{t: "M1.1_Mapa conceptual", enfasis: recurso}`, y
la traducción a negrita/cursiva/subrayado vive **solo aquí**. Si el CIAD cambia su guía de
estilo se toca esta tabla y nada más.

Regla de oro al escribir en una plantilla: **nunca asignes `paragraph.text`**. Eso colapsa
todos los runs y destruye el formato del párrafo. Se añaden runs, clonando el `rPr` de un run
modelo del propio documento para heredar tipografía y tamaño.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from docx.oxml.ns import qn
from docx.text.paragraph import Paragraph
from docx.text.run import Run

# Del CIAD_DI_EstiloRedaccionRecomendado_2023 y verificado contra el ejemplo 961.
ENFASIS: dict[str, dict[str, bool]] = {
    "recurso": {"bold": True, "italic": True},      # M1.1_Fundamentos (presentación)
    "evidencia": {"bold": True, "underline": True},  # el tipo de evidencia
    "meta": {"bold": True},                          # «Meta 1.1.»
    "valor": {"bold": True},                         # «…equivale al 3% …»
    "fecha": {"bold": True},                         # fechas de entrega
    "ordinal": {"bold": True},                       # «Primero.», «Segundo.»
    "etiqueta": {"bold": True},                      # «Clave:», «Competencia general:»
    "normal": {},
}


class ErrorEstilo(Exception):
    """Se pidió un énfasis que no existe en la guía."""


def limpiar(p: Paragraph) -> Paragraph:
    """Quita los runs del párrafo conservando su `pPr` (estilo, sangría, espaciado)."""
    for r in list(p.runs):
        r._r.getparent().remove(r._r)
    return p


def run_modelo(p: Paragraph) -> Run | None:
    """El primer run del párrafo, para heredar su tipografía al escribir encima."""
    return p.runs[0] if p.runs else None


def escribir(p: Paragraph, texto: str, enfasis: str = "normal", modelo: Run | None = None) -> Run:
    """Añade un run al final del párrafo, con el énfasis semántico indicado."""
    if enfasis not in ENFASIS:
        raise ErrorEstilo(
            f"Énfasis desconocido: {enfasis!r}. Válidos: {', '.join(sorted(ENFASIS))}."
        )
    run = p.add_run()
    if modelo is not None and (rpr := modelo._r.find(qn("w:rPr"))) is not None:
        run._r.insert(0, deepcopy(rpr))
    # El énfasis se aplica DESPUÉS de heredar, para que gane sobre el rPr del modelo.
    for atributo in ("bold", "italic", "underline"):
        setattr(run, atributo, ENFASIS[enfasis].get(atributo, False))
    run.text = texto
    return run


def reemplazar(p: Paragraph, contenido: Any, enfasis: str = "normal") -> Paragraph:
    """Sustituye el contenido del párrafo, heredando la tipografía del run que había.

    `contenido` puede ser texto plano o una lista de tramos:

        reemplazar(p, "texto simple")
        reemplazar(p, [{"t": "Meta 1.1.", "enfasis": "meta"}, {"t": " Identificar…"}])
    """
    modelo = run_modelo(p)
    limpiar(p)
    for tramo in _tramos(contenido, enfasis):
        escribir(p, tramo["t"], tramo.get("enfasis", enfasis), modelo)
    return p


def anexar(p: Paragraph, contenido: Any, enfasis: str = "normal") -> Paragraph:
    """Añade contenido **conservando** los runs existentes.

    Es la forma correcta de rellenar los campos de la Sección 1: la plantilla ya trae
    `[('Clave', bold), (': ', normal)]` y solo falta el valor.
    """
    modelo = p.runs[-1] if p.runs else None
    for tramo in _tramos(contenido, enfasis):
        escribir(p, tramo["t"], tramo.get("enfasis", enfasis), modelo)
    return p


def _tramos(contenido: Any, enfasis: str) -> list[dict]:
    if isinstance(contenido, str):
        return [{"t": contenido, "enfasis": enfasis}]
    if isinstance(contenido, dict):
        return [contenido]
    return [{"t": c, "enfasis": enfasis} if isinstance(c, str) else c for c in contenido]
