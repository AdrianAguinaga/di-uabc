"""Exporta las clases de un ciclo a iCalendar (``.ics``).

Uso:
    python src/exportar_ics.py 2026-2 ara
    python src/exportar_ics.py 2026-2 ara --salida C:\\ruta\\Clases-2026-2-ara.ics

El contrato son los bloques de ``curso.yaml`` y el calendario escolar oficial; no se interpreta el
Markdown de ``horarios/`` ni las sesiones, metas o entregas del diseño instruccional. Importar el
archivo resultante en Google Calendar es una acción manual del profesor.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import calendario
import modelo

RAIZ = Path(__file__).resolve().parent.parent
ZONA = ZoneInfo("America/Tijuana")
PRODID = "-//DI-UABC//Calendario de clases//ES"


class ErrorIcs(Exception):
    """No se puede construir un calendario de clases defendible."""


@dataclass(frozen=True)
class Evento:
    """Una ocurrencia concreta de un bloque de clase, lista para serializar."""

    uid: str
    inicio: datetime
    fin: datetime
    resumen: str
    ubicacion: str = ""


@dataclass
class Resultado:
    """Eventos y omisiones deliberadas para que la CLI las haga visibles."""

    eventos: list[Evento] = field(default_factory=list)
    grupos_no_impartidos: list[str] = field(default_factory=list)
    grupos_sin_bloques: list[str] = field(default_factory=list)
    cursos_omitidos: list[str] = field(default_factory=list)
    profesor_id: str = ""
    profesor_nombre: str = ""


def rutas_curso(ciclo: str, raiz: Path = RAIZ) -> list[Path]:
    """Los ``curso.yaml`` existentes del ciclo, ordenados y sin suponer materias faltantes."""
    return sorted((raiz / "cursos" / ciclo).glob("*/curso.yaml"))


def cargar_cursos(rutas: list[Path]) -> tuple[list[modelo.Curso], list[str]]:
    """Carga lo disponible: una ruta ausente o inválida no borra las demás clases."""
    cursos: list[modelo.Curso] = []
    omitidos: list[str] = []
    for ruta in rutas:
        try:
            cursos.append(modelo.cargar(ruta))
        except modelo.ErrorModelo as e:
            omitidos.append(f"{ruta}: {e}")
    return cursos, omitidos


def _hora(valor: str, etiqueta: str) -> time:
    try:
        return time.fromisoformat(valor)
    except ValueError as e:
        raise ErrorIcs(f"{etiqueta}: hora inválida {valor!r}.") from e


def _fecha_hora(fecha: date, hora: str, etiqueta: str) -> datetime:
    return datetime.combine(fecha, _hora(hora, etiqueta), tzinfo=ZONA).astimezone(timezone.utc)


def _fechas_de_bloque(cal: calendario.Calendario, bloque: modelo.Bloque):
    """Cada ocurrencia dentro de clases, sin convertir una suspensión en otra fecha."""
    for semana in cal.semanas:
        fecha = semana.inicio + timedelta(days=bloque.dia)
        if fecha > cal.fin or cal.es_suspension(fecha):
            continue
        yield fecha


def _uid(curso: modelo.Curso, grupo: modelo.Grupo, bloque: modelo.Bloque, fecha: date) -> str:
    inicio = bloque.inicio.replace(":", "")
    fin = bloque.fin.replace(":", "")
    return (
        f"{curso.ciclo}-{curso.profesor_id}-{curso.clave}-{grupo.numero}-{fecha:%Y%m%d}-"
        f"{inicio}-{fin}-{bloque.ambiente}@di-uabc"
    )


def eventos_de(cursos: list[modelo.Curso], cal: calendario.Calendario) -> Resultado:
    """Convierte exclusivamente los bloques de grupos impartidos en clases concretas."""
    resultado = Resultado()
    for curso in cursos:
        for grupo in curso.grupos:
            etiqueta = f"{curso.clave} · grupo {grupo.numero}"
            if not grupo.imparte:
                resultado.grupos_no_impartidos.append(etiqueta)
                continue
            if not grupo.horario.bloques:
                resultado.grupos_sin_bloques.append(etiqueta)
                continue
            for bloque in grupo.horario.bloques:
                if bloque.ambiente == "presencial" and not grupo.horario.aula.strip():
                    raise ErrorIcs(f"{etiqueta}: un bloque presencial requiere aula para el .ics.")
                for fecha in _fechas_de_bloque(cal, bloque):
                    inicio = _fecha_hora(fecha, bloque.inicio, etiqueta)
                    fin = _fecha_hora(fecha, bloque.fin, etiqueta)
                    if fin <= inicio:
                        raise ErrorIcs(
                            f"{etiqueta}: el bloque {bloque.inicio}–{bloque.fin} no termina "
                            "después de iniciar."
                        )
                    ambiente = "virtual" if bloque.ambiente == "virtual" else "presencial"
                    resultado.eventos.append(Evento(
                        uid=_uid(curso, grupo, bloque, fecha),
                        inicio=inicio,
                        fin=fin,
                        resumen=f"{curso.nombre} · Grupo {grupo.numero} · {ambiente}",
                        ubicacion=grupo.horario.aula if bloque.ambiente == "presencial" else "",
                    ))
    resultado.eventos.sort(key=lambda e: (e.inicio, e.fin, e.uid))
    return resultado


def escapar(texto: str) -> str:
    """Escapa texto RFC 5545 sin perder UTF-8."""
    return (
        texto.replace("\\", "\\\\")
        .replace(";", "\\;")
        .replace(",", "\\,")
        .replace("\r\n", "\\n")
        .replace("\n", "\\n")
        .replace("\r", "\\n")
    )


def plegar(linea: str) -> str:
    """Pliega una content line a 75 octetos, usando espacio al continuar (RFC 5545)."""
    partes: list[str] = []
    actual = ""
    for caracter in linea:
        if len((actual + caracter).encode("utf-8")) <= 75:
            actual += caracter
            continue
        if not actual:  # defensivo: ningún carácter UTF-8 válido alcanza 75 octetos.
            raise ErrorIcs("No se puede plegar una línea iCalendar vacía.")
        partes.append(actual)
        actual = " " + caracter
    partes.append(actual)
    return "\r\n".join(partes)


def _instante(valor: datetime) -> str:
    return valor.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def serializar(
    eventos: list[Evento],
    sello: datetime | None = None,
    nombre_calendario: str = "",
    descripcion_calendario: str = "",
) -> str:
    """Serializa un `VCALENDAR` mínimo, importable y sin contenido ajeno a clases."""
    sello = sello or datetime.now(timezone.utc)
    lineas = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        f"PRODID:{PRODID}",
        "CALSCALE:GREGORIAN",
    ]
    if nombre_calendario:
        lineas.append(f"X-WR-CALNAME:{escapar(nombre_calendario)}")
    if descripcion_calendario:
        lineas.append(f"X-WR-CALDESC:{escapar(descripcion_calendario)}")
    for evento in eventos:
        lineas.extend([
            "BEGIN:VEVENT",
            f"UID:{evento.uid}",
            f"DTSTAMP:{_instante(sello)}",
            f"DTSTART:{_instante(evento.inicio)}",
            f"DTEND:{_instante(evento.fin)}",
            f"SUMMARY:{escapar(evento.resumen)}",
        ])
        if evento.ubicacion:
            lineas.append(f"LOCATION:{escapar(evento.ubicacion)}")
        lineas.append("END:VEVENT")
    lineas.append("END:VCALENDAR")
    return "\r\n".join(plegar(linea) for linea in lineas) + "\r\n"


def exportar(
    ciclo: str,
    profesor_id: str,
    salida: Path | str | None = None,
    ahora: datetime | None = None,
) -> tuple[Path, Resultado]:
    """Exporta una agenda por profesor, sin mezclar sus bloques con los de otra persona."""
    cal = calendario.cargar(ciclo)
    profesor = modelo.Config().profesor(profesor_id)
    cursos, omitidos = cargar_cursos(rutas_curso(ciclo))
    cursos_del_profesor = [c for c in cursos if c.profesor_id == profesor_id]
    resultado = eventos_de(cursos_del_profesor, cal)
    resultado.cursos_omitidos.extend(omitidos)
    resultado.profesor_id = profesor_id
    resultado.profesor_nombre = profesor["nombre"]

    if not resultado.eventos:
        raise ErrorIcs(
            f"{profesor['nombre']} ({profesor_id}) no tiene bloques de clase impartidos "
            f"declarados para {ciclo}. No se genera una agenda vacía."
        )

    destino = (
        Path(salida)
        if salida
        else RAIZ / "horarios" / "salida" / f"Clases-{ciclo}-{profesor_id}.ics"
    )
    destino.parent.mkdir(parents=True, exist_ok=True)
    with destino.open("w", encoding="utf-8", newline="") as archivo:
        archivo.write(serializar(
            resultado.eventos,
            ahora,
            nombre_calendario=f"Clases {ciclo} · {profesor['nombre']}",
            descripcion_calendario=(
                f"Calendario de clases de {profesor['nombre']} ({profesor_id}) · "
                "generado desde DI-UABC."
            ),
        ))
    return destino, resultado


def _uso() -> str:
    return "Uso: python src/exportar_ics.py <ciclo> <id-profesor> [--salida <archivo.ics>]"


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print(_uso(), file=sys.stderr)
        return 2
    ciclo = argv[1]
    profesor_id = argv[2]
    salida: Path | None = None
    resto = argv[3:]
    if resto:
        if len(resto) != 2 or resto[0] != "--salida":
            print(_uso(), file=sys.stderr)
            return 2
        salida = Path(resto[1])
    try:
        destino, resultado = exportar(ciclo, profesor_id, salida)
    except (ErrorIcs, calendario.ErrorCalendario, modelo.ErrorModelo) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    print(
        f"Calendario de clases {ciclo} · {resultado.profesor_nombre} "
        f"({resultado.profesor_id}): {len(resultado.eventos)} eventos."
    )
    print(f"Archivo: {destino.resolve()}")
    for etiqueta in resultado.grupos_no_impartidos:
        print(f"· Omitido: {etiqueta} no se imparte este ciclo.")
    for etiqueta in resultado.grupos_sin_bloques:
        print(f"· Omitido: {etiqueta} no declara bloques con horas.")
    for detalle in resultado.cursos_omitidos:
        print(f"! Curso omitido: {detalle}")
    print("Importa este borrador manualmente en Google Calendar y revisa el calendario destino.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
