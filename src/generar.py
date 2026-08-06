"""De `curso.yaml` al paquete entregable: valida, renderiza, exporta y firma el manifiesto.

Es el único comando que necesita el orquestador `/di-nuevo` una vez que las seis preguntas
están contestadas y `curso.yaml` escrito.

El orden no se negocia: **primero valida**. Si hay un solo error no se escribe ni un archivo.
Un DI con los porcentajes mal o con una entrega en día de suspensión no debe llegar a existir
en disco, porque en cuanto existe alguien lo abre y lo entrega.

Al final deja `MANIFIESTO.yaml` junto al `curso.yaml`: con qué PUA, qué calendario, qué
plantilla y qué versión del código se produjo cada archivo (regla invariable 7). Es lo que
permite defender una fecha o un porcentaje seis meses después.
"""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import yaml

import calendario
import export_pdf
import modelo
import plantillas
import render_docx
import validar
from modelo import Config, Curso

RAIZ = Path(__file__).resolve().parent.parent
ANCHO = 60  # ancho interior del panel — el mismo del menú de /di-nuevo

CABECERA = (
    "# Manifiesto de generación. Lo escribe src/generar.py: no lo edites a mano.\n"
    "#\n"
    "# Regla invariable 7 — todo dato es trazable. De aquí se reconstruye con qué PUA, qué\n"
    "# calendario, qué plantilla y qué versión del código salió cada archivo. Si alguien pone\n"
    "# en duda una fecha o un porcentaje del documento, se empieza por este archivo.\n"
    "#\n"
    "# El documento generado es un BORRADOR: requiere la revisión del profesor antes de\n"
    "# entregarse a la facultad o publicarse a los alumnos (Art. 66 del Estatuto Escolar).\n"
)


class ErrorGenerar(Exception):
    """El paquete no se generó. Lo que ya estaba en disco no se tocó."""


@dataclass
class Paquete:
    curso: Curso
    informe: validar.Informe
    archivos: list[Path]
    manifiesto: Path


# -- panel -------------------------------------------------------------------
#
# El mismo marco que usa el menú de /di-nuevo, pero dibujado aquí: las anchuras salen
# bien siempre y el orquestador solo tiene que repetir la salida.


def cabecera(titulo: str = "generando") -> str:
    izq = f"─ DI · NUEVO ── {titulo} "
    return "┌" + izq + "─" * (ANCHO - len(izq)) + "┐"


PIE = "└" + "─" * ANCHO + "┘"


def linea(glifo: str, etiqueta: str, detalle: str = "") -> str:
    # El ancho mínimo es 15, pero una etiqueta más larga —«grupo POR-DEFINIR»— se comía
    # el separador y quedaba pegada al detalle. Siempre queda al menos un espacio.
    cuerpo = f"  {glifo} {etiqueta:<{max(15, len(etiqueta) + 1)}}{detalle}"
    if len(cuerpo) > ANCHO:
        cuerpo = cuerpo[: ANCHO - 1] + "…"
    return "│" + cuerpo.ljust(ANCHO) + "│"


# -- trazabilidad ------------------------------------------------------------


def _commit() -> str:
    """El commit con el que se generó. `-sucio` si el árbol tenía cambios sin commitear."""
    def git(*args: str) -> str | None:
        try:
            r = subprocess.run(
                ["git", *args], cwd=RAIZ, capture_output=True, text=True, timeout=15
            )
        except (OSError, subprocess.SubprocessError):
            return None
        return r.stdout.strip() if r.returncode == 0 else None

    commit = git("rev-parse", "--short", "HEAD")
    if commit is None:
        return "sin git"
    return f"{commit}-sucio" if git("status", "--porcelain") else commit


def relativa(p: Path) -> str:
    p = Path(p).resolve()
    try:
        return p.relative_to(RAIZ).as_posix()
    except ValueError:
        return p.as_posix()


def _pua(curso: Curso) -> dict:
    """El PUA que respalda el curso, con el sha del PDF oficial verificado hoy.

    `pua_sha256` en `curso.yaml` es el hash del **PDF** de origen. Si el PDF ya no
    hashea igual, el DI está construido sobre un programa que cambió: se registra y se
    avisa, no se corrige solo.
    """
    datos: dict = {"md": curso.pua_ref, "sha256_declarado": curso.pua_sha256}
    md = RAIZ / curso.pua_ref if curso.pua_ref else None
    if not (md and md.exists()):
        datos["coincide"] = None
        return datos

    datos["md_sha256"] = plantillas.sha256(md)
    frente = yaml.safe_load(md.read_text(encoding="utf-8").split("---", 2)[1]) or {}
    datos["fuente"] = frente.get("fuente", "")
    pdf = RAIZ / datos["fuente"] if datos["fuente"] else None
    if pdf and pdf.exists():
        datos["fuente_sha256"] = plantillas.sha256(pdf)
        datos["coincide"] = datos["fuente_sha256"] == curso.pua_sha256
    else:
        datos["coincide"] = None  # el PDF no está a mano; no se puede afirmar nada
    return datos


def manifiesto(
    curso: Curso,
    ruta_curso: Path,
    informe: validar.Informe,
    archivos: list[Path],
    cfg: Config,
    cal: calendario.Calendario,
) -> dict:
    prof = cfg.profesor(curso.profesor_id)
    plantilla = plantillas.cargar()[curso.modalidad]
    return {
        "generado": datetime.now().isoformat(timespec="seconds"),
        "commit": _commit(),
        "curso": {
            "archivo": relativa(ruta_curso),
            "sha256": plantillas.sha256(ruta_curso),
            "ciclo": curso.ciclo,
            "clave": curso.clave,
            "nombre": curso.nombre,
            "modalidad": curso.modalidad,
        },
        "pua": _pua(curso),
        "calendario": {
            "archivo": relativa(calendario.DIR_CALENDARIOS / f"{curso.ciclo}.yaml"),
            "sha256": plantillas.sha256(calendario.DIR_CALENDARIOS / f"{curso.ciclo}.yaml"),
            "semanas": cal.total_semanas,
            "inicio": cal.inicio,
            "fin": cal.fin,
        },
        "plantilla": {
            "modalidad": plantilla.modalidad,
            "archivo": plantilla.archivo,
            "version": plantilla.version,
            "sha256": plantilla.sha256,
            "origen": plantilla.origen,
        },
        "profesor": {
            "id": prof["id"],
            "nombre": prof["nombre"],
            "correo": prof.get("correo"),
        },
        "evaluacion": {
            "esquema_id": curso.esquema_id,
            "exencion_ordinario": curso.exencion_ordinario,
            "rubros": [{"id": r.id, "porcentaje": r.porcentaje} for r in curso.rubros],
            # Solo si el curso los declara: la forma del manifiesto entra en la huella, así que
            # un curso a un solo nivel tiene que producir exactamente el mismo dict que antes.
            **(
                {
                    "segundo_nivel": {
                        "promedio": {
                            "porcentaje": curso.segundo_nivel.promedio.porcentaje,
                            "etiqueta": curso.segundo_nivel.promedio.etiqueta,
                        },
                        "ordinario": {
                            "porcentaje": curso.segundo_nivel.ordinario.porcentaje,
                            "etiqueta": curso.segundo_nivel.ordinario.etiqueta,
                        },
                    },
                    "exencion_contra": curso.exencion_contra or "promedio",
                }
                if curso.segundo_nivel is not None
                else {}
            ),
        },
        "grupos": [
            {
                "numero": g.numero,
                "aula": g.horario.aula,
                "dias_presencial": g.horario.dias_presencial,
                "dia_entrega": g.horario.dia_entrega,
                "hora_entrega": g.horario.hora_entrega,
                "jefe_grupo": g.jefe_grupo,
            }
            for g in curso.grupos
        ],
        "validacion": {
            "errores": len(informe.errores),
            "avisos": [h.mensaje for h in informe.de(validar.AVISO)],
            "recordatorios": len(informe.de(validar.RECORDATORIO)),
        },
        # Solo los de esta corrida: si se regeneró un grupo suelto, el manifiesto lo dice.
        # El número de grupo cierra el nombre del archivo (ver modelo.nombre_archivo).
        "archivos": [
            {
                "ruta": relativa(a),
                "grupo": a.stem.rsplit("-", 1)[-1],
                "sha256": plantillas.sha256(a),
                "bytes": a.stat().st_size,
            }
            for a in archivos
        ],
    }


def escribir_manifiesto(datos: dict, destino: Path) -> Path:
    cuerpo = yaml.safe_dump(datos, allow_unicode=True, sort_keys=False, default_flow_style=False)
    destino.write_text(CABECERA + cuerpo, encoding="utf-8")
    return destino


# -- la cadena ---------------------------------------------------------------


def paquete(
    ruta_curso: Path | str,
    pdf: bool = True,
    traza=None,
    grupos: list[str] | None = None,
) -> Paquete:
    """Valida, renderiza un documento por grupo, exporta a PDF y escribe el manifiesto.

    `traza(glifo, etiqueta, detalle)` se llama al cerrar cada paso, para que la consola
    (o el orquestador) muestre el avance. Devuelve el `Paquete` con todo lo producido.

    `grupos` limita la generación a esos números — para rehacer el documento de un grupo
    sin volver a pasar por Word con los demás. El curso **no se toca**: los otros grupos
    siguen declarados, y el manifiesto dice cuáles se generaron esta vez.
    """
    traza = traza or (lambda *_: None)
    ruta_curso = Path(ruta_curso).resolve()

    curso = modelo.cargar(ruta_curso)
    cfg = Config()
    cal = calendario.cargar(curso.ciclo)

    pedidos = curso.grupos
    if grupos:
        pedidos = [g for g in curso.grupos if g.numero in grupos]
        if faltan := set(grupos) - {g.numero for g in pedidos}:
            raise ErrorGenerar(
                f"El curso no declara el/los grupo(s) {', '.join(sorted(faltan))}. "
                f"Declarados: {', '.join(g.numero for g in curso.grupos)}."
            )

    informe = validar.validar(curso, cfg, cal)
    if not informe.valido:
        traza("✗", "validación", f"{len(informe.errores)} error(es) — no se generó nada")
        raise ErrorGenerar(informe.texto())
    traza(
        "✓",
        "validación",
        f"0 errores · {len(informe.de(validar.AVISO))} avisos · "
        f"{len(informe.de(validar.RECORDATORIO))} recordatorios",
    )

    if len(pedidos) < len(curso.grupos):
        traza(
            "!",
            "parcial",
            f"solo {', '.join(g.numero for g in pedidos)} — el manifiesto cubre eso",
        )

    salida = ruta_curso.parent / "salida"
    archivos: list[Path] = []
    for g in pedidos:
        destino = salida / curso.nombre_archivo(g.numero, "docx")
        try:
            render_docx.generar(curso, g, destino, cfg)
        except (render_docx.ErrorRender, plantillas.ErrorPlantilla) as e:
            traza("✗", f"grupo {g.numero}", "no se pudo renderizar")
            raise ErrorGenerar(str(e)) from e
        archivos.append(destino)

        if not pdf:
            traza("✓", f"grupo {g.numero}", destino.name)
            continue
        try:
            archivos.append(export_pdf.exportar(destino))
            traza("✓", f"grupo {g.numero}", f"{destino.name} → .pdf")
        except export_pdf.ErrorExport as e:
            # Sin Word no hay PDF, pero el .docx ya es entregable: no se tira el trabajo.
            traza("!", f"grupo {g.numero}", f"{destino.name} · sin PDF")
            informe.hallazgos.append(
                validar.Hallazgo("PDF", validar.AVISO, f"No se exportó el PDF: {e}")
            )

    datos = manifiesto(curso, ruta_curso, informe, archivos, cfg, cal)
    if datos["pua"]["coincide"] is False:
        traza("!", "PUA", "el PDF de origen cambió desde que se escribió el curso")
    ruta_manifiesto = escribir_manifiesto(datos, ruta_curso.parent / "MANIFIESTO.yaml")
    traza("✓", "MANIFIESTO", relativa(ruta_manifiesto.parent) + "/")

    return Paquete(curso, informe, archivos, ruta_manifiesto)


# -- consola -----------------------------------------------------------------


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(
            "Uso: python src/generar.py <ruta a curso.yaml> [--sin-pdf] [--grupo <n>]…",
            file=sys.stderr,
        )
        return 2
    grupos = [argv[i + 1] for i, a in enumerate(argv) if a == "--grupo" and i + 1 < len(argv)]
    # El panel usa caracteres de marco; en una consola cp1252 reventaría al imprimir.
    for flujo in (sys.stdout, sys.stderr):
        if hasattr(flujo, "reconfigure"):
            flujo.reconfigure(encoding="utf-8", errors="replace")

    print(cabecera())
    try:
        p = paquete(
            Path(argv[1]),
            pdf="--sin-pdf" not in argv,
            traza=lambda *a: print(linea(*a), flush=True),
            grupos=grupos or None,
        )
    except (ErrorGenerar, modelo.ErrorModelo, calendario.ErrorCalendario) as e:
        print(PIE)
        print(f"\n{e}", file=sys.stderr)
        return 1
    print(PIE)

    for h in p.informe.de(validar.AVISO):
        print(f"  ! {h.mensaje}")
    print(
        "\nBorrador. Revísalo antes de entregarlo a la facultad o publicarlo a los alumnos."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
