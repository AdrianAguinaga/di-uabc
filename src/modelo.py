"""Modelo de datos del Diseño Instruccional.

`curso.yaml` es el contrato entre la etapa de planeación (Opus, que redacta) y la
de renderizado (Python, determinista). Todo lo que aparece en el documento sale de
aquí; el renderizador no inventa nada. Si el renderizador necesitara "decidir" algo,
es señal de que falta un campo en este modelo.

Tres decisiones que sostienen las reglas invariables:

  1. El horario vive en el grupo, no en el curso: si dos grupos tienen días de clase
     distintos, todas las fechas divergen.
  2. Las fechas se escriben como marcadores (`{{fecha_entrega}}`) que resuelve
     `calendario.py`. Opus nunca escribe una fecha literal.
  3. El énfasis es semántico (`enfasis: recurso`), no tipográfico. El mapa a
     negrita/cursiva/subrayado vive solo en `estilo.py`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

import yaml

RAIZ = Path(__file__).resolve().parent.parent
DIR_CONFIG = RAIZ / "config"

MODALIDADES = ("semipresencial", "escolarizada", "a_distancia")
TIPOS_META = ("encuadre", "aprendizaje", "examen_parcial", "cierre")
AMBIENTES = ("presencial", "virtual")


class ErrorModelo(Exception):
    """`curso.yaml` no cumple el esquema."""


# -- configuración -----------------------------------------------------------


def _cargar_yaml(ruta: Path) -> dict:
    if not ruta.exists():
        raise ErrorModelo(f"Falta el archivo de configuración: {ruta}")
    return yaml.safe_load(ruta.read_text(encoding="utf-8"))


class Config:
    """Los cuatro archivos de `config/`, cargados una vez."""

    def __init__(self) -> None:
        self.profesores = _cargar_yaml(DIR_CONFIG / "profesores.yaml")
        self.esquemas = _cargar_yaml(DIR_CONFIG / "esquemas-evaluacion.yaml")
        self.politicas = _cargar_yaml(DIR_CONFIG / "politicas.yaml")
        self.plantillas = _cargar_yaml(DIR_CONFIG / "plantillas.yaml")

    def profesor(self, id_: str) -> dict:
        for p in self.profesores["profesores"]:
            if p["id"] == id_:
                return p
        disponibles = ", ".join(p["id"] for p in self.profesores["profesores"])
        raise ErrorModelo(f"Profesor desconocido: {id_}. Disponibles: {disponibles}")

    def esquema(self, id_: str) -> dict:
        if id_ not in self.esquemas["esquemas"]:
            disponibles = ", ".join(self.esquemas["esquemas"])
            raise ErrorModelo(f"Esquema desconocido: {id_}. Disponibles: {disponibles}")
        return self.esquemas["esquemas"][id_]

    def plantilla(self, modalidad: str) -> dict:
        if modalidad not in self.plantillas["modalidades"]:
            raise ErrorModelo(
                f"Modalidad desconocida: {modalidad}. Válidas: {', '.join(MODALIDADES)}"
            )
        return self.plantillas["modalidades"][modalidad]

    def articulo(self, cita: str) -> dict:
        arts = self.politicas["articulos"]
        if cita not in arts:
            raise ErrorModelo(
                f"Cita legal inexistente: {cita}. "
                f"Ningún texto del documento puede citar un artículo que no esté "
                f"registrado en config/politicas.yaml."
            )
        return arts[cita]


# -- piezas del curso --------------------------------------------------------


@dataclass
class Evidencia:
    nombre: str
    tipo: str = ""
    recurso: str = ""  # p. ej. "M1.1_Mapa conceptual"


@dataclass
class Sesion:
    """Un tramo de la actividad de una meta, en un ambiente concreto."""

    ambiente: str  # presencial | virtual
    semana: int
    pasos: list[Any] = field(default_factory=list)
    actividad_tabla: str = ""  # texto corto para la columna Actividad
    dia: int | None = None  # 0=lunes … 5=sábado; None = usa el horario del grupo
    fecha: date | None = None  # la resuelve calendario.py; nunca se escribe a mano

    def __post_init__(self) -> None:
        if self.ambiente not in AMBIENTES:
            raise ErrorModelo(
                f"Ambiente inválido: {self.ambiente!r}. Válidos: {', '.join(AMBIENTES)}"
            )


@dataclass
class Meta:
    id: str  # "0", "1.1", "C"
    enunciado: str
    unidad: str  # romano, coincide con el PUA
    tipo: str = "aprendizaje"
    rubro: str = "tareas"
    valor: float = 0.0  # porcentaje de la calificación final
    semanas: list[int] = field(default_factory=list)
    caracter: str = "individual"
    que_voy_a_aprender: list[str] = field(default_factory=list)
    sesiones: list[Sesion] = field(default_factory=list)
    evidencias: list[Evidencia] = field(default_factory=list)
    criterios_evaluacion: list[str] = field(default_factory=list)
    reflexion: list[str] = field(default_factory=list)  # siempre en pasado
    # Anclas anti-alucinación: deben existir en el PUA.
    cubre_temas: list[str] = field(default_factory=list)
    practica_pua: str | None = None

    def __post_init__(self) -> None:
        if self.tipo not in TIPOS_META:
            raise ErrorModelo(
                f"Meta {self.id}: tipo inválido {self.tipo!r}. "
                f"Válidos: {', '.join(TIPOS_META)}"
            )
        if not self.semanas:
            raise ErrorModelo(f"Meta {self.id}: no tiene semanas asignadas.")

    @property
    def etiqueta(self) -> str:
        return f"Meta {self.id}"


@dataclass
class Unidad:
    numero: str
    nombre: str
    competencia: str = ""
    duracion_horas: int | None = None
    temas: list[str] = field(default_factory=list)


@dataclass
class Rubro:
    id: str
    etiqueta: str
    porcentaje: float
    detalle: str = ""
    parciales: int = 0


@dataclass
class Horario:
    """Vive en el grupo: si dos grupos tienen días distintos, las fechas divergen."""

    dias_presencial: list[int] = field(default_factory=list)  # 0=lunes … 5=sábado
    dia_entrega: int = 5  # sábado
    hora_entrega: str = "23:59"
    aula: str = ""


@dataclass
class Grupo:
    numero: str
    horario: Horario = field(default_factory=Horario)
    jefe_grupo: str | None = None  # se firma a mano
    plataforma: str = "Blackboard"


@dataclass
class Curso:
    """El diseño instruccional completo de una materia en un ciclo."""

    ciclo: str
    clave: str
    nombre: str
    modalidad: str
    profesor_id: str

    identificacion: dict[str, Any] = field(default_factory=dict)
    contenido: dict[str, Any] = field(default_factory=dict)
    unidades: list[Unidad] = field(default_factory=list)
    metas: list[Meta] = field(default_factory=list)
    rubros: list[Rubro] = field(default_factory=list)
    grupos: list[Grupo] = field(default_factory=list)

    exencion_ordinario: int = 80
    tolerancia_minutos: int = 15
    practica: bool = False  # activa la nota del Art. 74
    citas: list[str] = field(default_factory=list)

    # Trazabilidad
    pua_ref: str = ""
    pua_sha256: str = ""
    esquema_id: str = ""
    avisos: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.modalidad not in MODALIDADES:
            raise ErrorModelo(
                f"Modalidad inválida: {self.modalidad!r}. Válidas: {', '.join(MODALIDADES)}"
            )
        if not self.grupos:
            raise ErrorModelo("El curso debe tener al menos un grupo.")

    @property
    def presencial(self) -> bool:
        return self.modalidad in ("semipresencial", "escolarizada")

    def unidad(self, numero: str) -> Unidad | None:
        return next((u for u in self.unidades if u.numero == numero), None)

    def rubro(self, id_: str) -> Rubro | None:
        return next((r for r in self.rubros if r.id == id_), None)

    def metas_de(self, unidad: str) -> list[Meta]:
        return [m for m in self.metas if m.unidad == unidad]

    def nombre_archivo(self, grupo: str, ext: str) -> str:
        return f"DI-{self.ciclo}-{self.clave}-{grupo}.{ext}"


# -- carga -------------------------------------------------------------------


def _construir_meta(d: dict) -> Meta:
    sesiones = [Sesion(**s) for s in d.pop("sesiones", [])]
    evidencias = [
        Evidencia(**e) if isinstance(e, dict) else Evidencia(nombre=e)
        for e in d.pop("evidencias", [])
    ]
    semanas = d.pop("semanas", None)
    if semanas is None and (s := d.pop("semana", None)) is not None:
        semanas = [s]
    return Meta(semanas=semanas or [], sesiones=sesiones, evidencias=evidencias, **d)


def _construir_grupo(g: Any) -> Grupo:
    if not isinstance(g, dict):  # forma corta: solo el número
        return Grupo(numero=str(g))
    horario = Horario(**g.pop("horario", {}))
    return Grupo(numero=str(g.pop("numero")), horario=horario, **g)


def desde_dict(d: dict) -> Curso:
    d = dict(d)
    meta = d.pop("meta", {})
    evaluacion = d.pop("evaluacion", {})
    ident = d.pop("identificacion", {})

    return Curso(
        ciclo=meta["ciclo"],
        clave=str(meta["clave"]),
        nombre=d.pop("nombre", "") or ident.get("nombre", ""),
        modalidad=ident.get("modalidad", ""),
        profesor_id=d.pop("profesor", meta.get("profesor", "")),
        identificacion=ident,
        contenido=d.pop("contenido", {}),
        unidades=[Unidad(**u) for u in d.pop("unidades", [])],
        metas=[_construir_meta(dict(m)) for m in d.pop("metas", [])],
        rubros=[Rubro(**r) for r in evaluacion.get("rubros", [])],
        grupos=[_construir_grupo(g) for g in d.pop("grupos", [])],
        exencion_ordinario=evaluacion.get("exencion_ordinario", 80),
        esquema_id=evaluacion.get("esquema_id", ""),
        tolerancia_minutos=d.pop("tolerancia_minutos", 15),
        practica=ident.get("practica", False),
        citas=d.pop("citas", []),
        pua_ref=meta.get("pua_ref", ""),
        pua_sha256=meta.get("pua_sha256", ""),
        avisos=d.pop("avisos", []),
    )


def resolver_fechas(curso: Curso, grupo: Grupo, cal) -> Curso:
    """Asigna a cada sesión su fecha real, según el horario **de ese grupo**.

    Aquí es donde se cumple la regla de que Opus nunca escribe fechas: el planeador
    asigna semanas y el calendario las convierte en días concretos, saltando las
    suspensiones.

    Ojo: las sesiones son compartidas por todos los grupos del curso, así que esto
    **sobrescribe** la resolución anterior. Llámalo justo antes de renderizar cada
    grupo, no una vez para todos.
    """
    h = grupo.horario
    presencial = h.dias_presencial[0] if h.dias_presencial else 0
    for m in curso.metas:
        for s in m.sesiones:
            dia = s.dia if s.dia is not None else (
                presencial if s.ambiente == "presencial" else h.dia_entrega
            )
            s.fecha = cal.fecha_de(s.semana, dia)
    return curso


def cargar(ruta: Path | str) -> Curso:
    ruta = Path(ruta)
    if not ruta.exists():
        raise ErrorModelo(f"No existe {ruta}")
    datos = yaml.safe_load(ruta.read_text(encoding="utf-8"))
    if not isinstance(datos, dict):
        raise ErrorModelo(f"{ruta} no contiene un mapa YAML.")
    try:
        return desde_dict(datos)
    except KeyError as e:
        raise ErrorModelo(f"{ruta}: falta el campo obligatorio {e}") from e
    except TypeError as e:
        raise ErrorModelo(f"{ruta}: campo inesperado o faltante — {e}") from e
