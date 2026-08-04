"""Motor de calendario escolar.

Convierte un ciclo escolar UABC en semanas numeradas con sus fechas reales,
respetando los días de suspensión de labores.

Regla fundamental del proyecto: **el número de semanas lo manda el calendario,
no la plantilla**. Para 2026-2 son 16 semanas, aunque la plantilla CIAD traiga 17.

Uso:
    python src/calendario.py 2026-2
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parent.parent
DIR_CALENDARIOS = RAIZ / "calendarios"

MESES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]
DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]


class ErrorCalendario(Exception):
    """Fecha o ciclo inválido para el calendario cargado."""


def texto_fecha(f: date, con_anio: bool = False) -> str:
    """`date(2026, 8, 18)` → `18 de agosto` (o `18 de agosto de 2026`)."""
    base = f"{f.day} de {MESES[f.month - 1]}"
    return f"{base} de {f.year}" if con_anio else base


def texto_fecha_corta(f: date) -> str:
    """`date(2026, 9, 1)` → `1 Sep`. La columna Entrega de la tabla es estrecha."""
    return f"{f.day} {MESES[f.month - 1][:3].capitalize()}"


@dataclass
class Suspension:
    fecha: date
    motivo: str


@dataclass
class Semana:
    """Una semana de clases, de lunes a sábado."""

    numero: int
    inicio: date  # lunes
    fin: date  # sábado
    suspensiones: list[Suspension] = field(default_factory=list)

    def dias_habiles(self) -> list[date]:
        """Lunes a sábado, descontando las suspensiones."""
        inhabiles = {s.fecha for s in self.suspensiones}
        return [
            d
            for i in range(6)
            if (d := self.inicio + timedelta(days=i)) not in inhabiles
        ]

    def rango_texto(self) -> str:
        """`10–15 ago` · `31 ago – 5 sep` cuando cruza de mes."""
        ini, fin = self.inicio, self.fin
        if ini.month == fin.month:
            return f"{ini.day}–{fin.day} {MESES[ini.month - 1][:3]}"
        return (
            f"{ini.day} {MESES[ini.month - 1][:3]} – {fin.day} {MESES[fin.month - 1][:3]}"
        )


@dataclass
class Periodo:
    inicio: date
    fin: date

    def contiene(self, f: date) -> bool:
        return self.inicio <= f <= self.fin

    def texto(self) -> str:
        """`Del 30 de noviembre al 8 de diciembre de 2026`."""
        if self.inicio.year == self.fin.year:
            return f"Del {texto_fecha(self.inicio)} al {texto_fecha(self.fin, True)}"
        return f"Del {texto_fecha(self.inicio, True)} al {texto_fecha(self.fin, True)}"


class Calendario:
    """Calendario escolar de un ciclo, cargado desde `calendarios/<ciclo>.yaml`."""

    def __init__(self, datos: dict):
        self.ciclo: str = datos["ciclo"]
        self.descripcion: str = datos.get("descripcion", "")
        self.inicio: date = datos["clases"]["inicio"]
        self.fin: date = datos["clases"]["fin"]

        if self.inicio.weekday() != 0:
            raise ErrorCalendario(
                f"{self.ciclo}: el inicio de clases ({self.inicio}) debería ser lunes, "
                f"pero es {DIAS[self.inicio.weekday()]}. Verifica el calendario oficial."
            )

        self.suspensiones = [
            Suspension(fecha=s["fecha"], motivo=s["motivo"])
            for s in datos.get("suspensiones", [])
        ]
        self.periodos: dict[str, Periodo | date] = {}
        for nombre, valor in (datos.get("periodos") or {}).items():
            if isinstance(valor, dict):
                self.periodos[nombre] = Periodo(valor["inicio"], valor["fin"])
            else:
                self.periodos[nombre] = valor

        self.semanas = self._construir_semanas()

    # -- construcción --------------------------------------------------------

    def _construir_semanas(self) -> list[Semana]:
        semanas: list[Semana] = []
        lunes = self.inicio
        numero = 1
        while lunes <= self.fin:
            sabado = min(lunes + timedelta(days=5), self.fin)
            semana = Semana(numero=numero, inicio=lunes, fin=sabado)
            semana.suspensiones = [
                s for s in self.suspensiones if lunes <= s.fecha <= sabado
            ]
            semanas.append(semana)
            lunes += timedelta(days=7)
            numero += 1
        return semanas

    # -- consulta ------------------------------------------------------------

    @property
    def total_semanas(self) -> int:
        return len(self.semanas)

    def semana(self, numero: int) -> Semana:
        if not 1 <= numero <= self.total_semanas:
            raise ErrorCalendario(
                f"{self.ciclo} tiene {self.total_semanas} semanas; "
                f"se pidió la {numero}."
            )
        return self.semanas[numero - 1]

    def es_suspension(self, f: date) -> Suspension | None:
        return next((s for s in self.suspensiones if s.fecha == f), None)

    def en_periodo_de_clases(self, f: date) -> bool:
        return self.inicio <= f <= self.fin

    def fecha_de(self, semana: int, dia: int = 0) -> date:
        """Fecha del día `dia` (0=lunes … 5=sábado) de la semana indicada.

        Si cae en suspensión, se recorre al siguiente día hábil dentro del
        periodo de clases.
        """
        s = self.semana(semana)
        objetivo = s.inicio + timedelta(days=dia)
        while self.es_suspension(objetivo):
            objetivo += timedelta(days=1)
        if objetivo > self.fin:
            raise ErrorCalendario(
                f"La fecha calculada ({objetivo}) queda después del fin de cursos "
                f"({self.fin}). Adelanta la entrega."
            )
        return objetivo

    def validar_entrega(self, f: date) -> None:
        """Lanza `ErrorCalendario` si la fecha no sirve como fecha de entrega."""
        if not self.en_periodo_de_clases(f):
            raise ErrorCalendario(
                f"{texto_fecha(f, True)} queda fuera del periodo de clases "
                f"({texto_fecha(self.inicio, True)} – {texto_fecha(self.fin, True)})."
            )
        if susp := self.es_suspension(f):
            raise ErrorCalendario(
                f"{texto_fecha(f, True)} es día de suspensión de labores: {susp.motivo}."
            )

    def semana_de(self, f: date) -> int | None:
        """Número de semana al que pertenece una fecha, o `None` si está fuera."""
        return next((s.numero for s in self.semanas if s.inicio <= f <= s.fin), None)


def cargar(ciclo: str) -> Calendario:
    """Carga `calendarios/<ciclo>.yaml`."""
    ruta = DIR_CALENDARIOS / f"{ciclo}.yaml"
    if not ruta.exists():
        disponibles = sorted(p.stem for p in DIR_CALENDARIOS.glob("*.yaml"))
        raise ErrorCalendario(
            f"No hay calendario para el ciclo {ciclo}.\n"
            f"Disponibles: {', '.join(disponibles) or 'ninguno'}.\n"
            f"Consigue el calendario oficial de la UABC, guárdalo en "
            f"calendarios/fuente/ y crea {ruta.name}. No estimes las fechas."
        )
    return Calendario(yaml.safe_load(ruta.read_text(encoding="utf-8")))


def ciclo_actual(hoy: date | None = None) -> str:
    """Deduce el ciclo de una fecha: AAAA-2 = ago–dic · AAAA-1 = ene–jun."""
    hoy = hoy or date.today()
    return f"{hoy.year}-{'2' if hoy.month >= 7 else '1'}"


# -- salida por consola ------------------------------------------------------


def _imprimir(cal: Calendario) -> None:
    print(f"Ciclo {cal.ciclo} — {cal.descripcion}")
    print(
        f"Clases: {texto_fecha(cal.inicio, True)} al {texto_fecha(cal.fin, True)}"
        f"  ({cal.total_semanas} semanas)\n"
    )
    print(f"{'Sem':>3}  {'Rango':<16}  Nota")
    print("-" * 64)
    for s in cal.semanas:
        notas = [f"⚠ {texto_fecha(x.fecha)}: {x.motivo}" for x in s.suspensiones]
        if s.numero == 1:
            notas.append("Inicio de cursos")
        if s.numero == cal.total_semanas:
            notas.append("Fin de cursos")
        limite = cal.periodos.get("limite_baja")
        if isinstance(limite, date) and s.inicio <= limite <= s.fin:
            notas.append(f"Límite de baja: {texto_fecha(limite)}")
        print(f"{s.numero:>3}  {s.rango_texto():<16}  {' · '.join(notas)}")

    print()
    for nombre in ("examenes_ordinarios", "examenes_extraordinarios"):
        if isinstance(p := cal.periodos.get(nombre), Periodo):
            print(f"{nombre.replace('_', ' ').capitalize()}: {p.texto()}")


def main(argv: list[str]) -> int:
    ciclo = argv[1] if len(argv) > 1 else ciclo_actual()
    try:
        _imprimir(cargar(ciclo))
    except ErrorCalendario as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
