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

from collections.abc import Iterator
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
UNIDADES_RUBRO = ("puntos",)  # ausente = porcentaje
# Vocabulario propio, distinto de TIPOS_META: un componente no es una meta.
TIPOS_COMPONENTE = ("examen_parcial", "examen_ordinario", "actividad", "proyecto")
# El segundo valor es válido en el contrato y R1 lo rechaza: tiene que poder escribirse para que
# la regla pueda explicar por qué está mal.
EXENCION_CONTRA = ("promedio", "calificacion_final")


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
class Componente:
    """Un aporte adicional de una meta a otro rubro.

    No es una meta aparte: la meta sigue teniendo una sola semana y un solo enunciado. Es
    lo que hace la meta 2.4 del 531 —10 pts de actividades y, en la misma sesión, el
    Examen I que vale 15 % de exámenes—.

    `valor` se lee en la unidad del rubro al que se imputa, que puede no ser el de su meta.
    """

    rubro: str
    valor: float
    etiqueta: str
    tipo: str                       # sin valor por omisión: quien declara un componente dice de qué tipo es
    evidencia: Evidencia | None = None

    def __post_init__(self) -> None:
        if self.tipo not in TIPOS_COMPONENTE:
            raise ErrorModelo(
                f"Componente «{self.etiqueta}»: tipo inválido {self.tipo!r}. "
                f"Válidos: {', '.join(TIPOS_COMPONENTE)}."
            )


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
    valor: float = 0.0  # en la unidad de su rubro: porcentaje, o puntos si el rubro los declara
    semanas: list[int] = field(default_factory=list)
    caracter: str = "individual"
    que_voy_a_aprender: list[str] = field(default_factory=list)
    sesiones: list[Sesion] = field(default_factory=list)
    evidencias: list[Evidencia] = field(default_factory=list)
    componentes: list[Componente] = field(default_factory=list)
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
    unidad: str = ""            # ausente = porcentaje; "puntos" = los valores de sus metas son pts
    total: float | None = None  # los puntos que reparte el rubro. Obligatorio si unidad == "puntos"

    def __post_init__(self) -> None:
        if self.unidad and self.unidad not in UNIDADES_RUBRO:
            raise ErrorModelo(
                f"Rubro {self.id}: unidad inválida {self.unidad!r}. "
                f"Válidas: {', '.join(UNIDADES_RUBRO)} (o ausente, para porcentaje)."
            )
        if self.unidad == "puntos":
            if self.total is None:
                raise ErrorModelo(
                    f"Rubro {self.id}: declara unidad «puntos» sin `total`. "
                    f"Un rubro en puntos debe declarar su total (p. ej. `total: 150`). "
                    f"No se infiere de la suma de sus metas: esa diferencia es justo lo que "
                    f"las reglas tienen que poder ver."
                )
            if self.total <= 0:
                raise ErrorModelo(
                    f"Rubro {self.id}: `total` debe ser mayor que 0, no {self.total:g}."
                )

    @property
    def base(self) -> float:
        """El total contra el que se leen los valores de sus metas."""
        return float(self.total) if self.unidad == "puntos" else float(self.porcentaje)

    def a_porcentaje(self, valor: float) -> float:
        """Convierte un valor escrito en la unidad de este rubro a % de la calificación final.

        Para un rubro en porcentaje es la identidad, así que quien compara nunca tiene que
        preguntar en qué unidad está: llama siempre a esto. No redondea — el redondeo es
        decisión de quien compara.
        """
        return 0.0 if not self.base else valor / self.base * self.porcentaje


@dataclass
class Nivel:
    """Uno de los dos sumandos de la calificación final: el promedio, o el ordinario.

    `etiqueta` es del contrato y no tiene valor por omisión: los rótulos del DI de origen
    —«Valor del promedio antes del Examen Ordinario»— son redacción de la docente, no
    vocabulario del proyecto. El renderizador los imprime, no los redacta.
    """

    porcentaje: float
    etiqueta: str


@dataclass
class SegundoNivel:
    """Cómo se combina el promedio del curso con el examen ordinario.

    Par fijo con claves nombradas y no lista: la exención se mide contra **el promedio**, una
    fila concreta, no contra «una del montón». Con una lista genérica R1 tendría que
    identificar por id cuál de las filas es el promedio antes de poder comprobar nada.
    El Estatuto no contempla un tercer sumando.
    """

    promedio: Nivel
    ordinario: Nivel


@dataclass
class FilaRubrica:
    """Un criterio literal del trabajo que evalúa la rúbrica."""

    concepto: str
    puntos: float
    descripcion: str


@dataclass
class Rubrica:
    """La rúbrica declarada por la docente para una meta o un rubro del curso.

    Los puntos de sus filas pertenecen a la propia rúbrica; no son porcentajes de la
    calificación final. Concepto y descripción llegan listos para imprimirse: el modelo
    los conserva, no los completa ni los normaliza.
    """

    total: float
    filas: list[FilaRubrica]
    meta: str = ""
    rubro: str = ""

    def __post_init__(self) -> None:
        if self.total <= 0:
            raise ErrorModelo(f"Rúbrica: total debe ser mayor que 0, no {self.total:g}.")
        if not self.filas:
            raise ErrorModelo("Rúbrica: debe declarar al menos una fila.")
        if negativas := [f.concepto for f in self.filas if f.puntos < 0]:
            raise ErrorModelo(
                f"Rúbrica: filas con puntos negativos: {', '.join(negativas)}."
            )
        if bool(self.meta) == bool(self.rubro):
            raise ErrorModelo(
                "Rúbrica: declara exactamente uno de meta o rubro para indicar qué evalúa."
            )


@dataclass
class Bloque:
    """Una franja de clase del grupo en la semana: día, horas y ambiente.

    No es una ``Sesion``: la sesión es un tramo de la actividad de una meta; el bloque es una
    franja del horario del grupo. Comparten el vocabulario de ``AMBIENTES`` y nada más.
    """

    dia: int  # 0=lunes … 5=sábado
    inicio: str  # "HH:MM", como hora_entrega
    fin: str  # "HH:MM"
    ambiente: str  # presencial | virtual

    def __post_init__(self) -> None:
        if not 0 <= self.dia <= 5:
            raise ErrorModelo(
                f"Bloque de horario: el día {self.dia} está fuera de la semana de clases "
                f"(0=lunes … 5=sábado)."
            )
        if self.ambiente not in AMBIENTES:
            raise ErrorModelo(
                f"Bloque del día {self.dia}: ambiente inválido {self.ambiente!r}. "
                f"Válidos: {', '.join(AMBIENTES)}."
            )


@dataclass
class Horario:
    """Vive en el grupo: si dos grupos tienen días distintos, las fechas divergen."""

    dias_presencial: list[int] = field(default_factory=list)  # 0=lunes … 5=sábado
    dia_entrega: int = 5  # sábado
    hora_entrega: str = "23:59"
    aula: str = ""
    bloques: list[Bloque] = field(default_factory=list)

    def __post_init__(self) -> None:
        # Llegan como dicts desde el YAML o ya construidos desde una prueba: los dos casos entran
        # por aquí, para que el contrato tenga una única normalización.
        self.bloques = [b if isinstance(b, Bloque) else Bloque(**b) for b in self.bloques]
        if self.bloques and self.dias_presencial:
            raise ErrorModelo(
                "Horario: declara bloques o dias_presencial, no ambos. Con bloques, "
                "dias_presencial se deriva de los presenciales — quita dias_presencial."
            )
        if self.bloques:
            self.dias_presencial = sorted(
                {b.dia for b in self.bloques if b.ambiente == "presencial"}
            )


@dataclass
class Grupo:
    numero: str
    horario: Horario = field(default_factory=Horario)
    jefe_grupo: str | None = None  # se firma a mano
    plataforma: str = "Blackboard"
    imparte: bool = True  # declarado pero fuera del ciclo → false


@dataclass(frozen=True)
class Aporte:
    """Lo que una meta aporta a un rubro: ella misma, o uno de sus componentes.

    `valor` va en la unidad **cruda** del rubro al que se imputa: `10` son 10 pts o 10 %
    según lo que declare ese rubro, y no según el rubro de la meta. Convertir es cosa de
    `Rubro.a_porcentaje()`, y quien compara decide cuándo. Llevar aquí los dos valores
    sería un derivado que puede desincronizarse.

    `meta` es la meta entera, no su id: la Fase 13 tiene que poder llegar desde un aporte
    a la semana, las sesiones y las evidencias de quien lo declaró.
    """

    meta: Meta
    rubro: str
    valor: float
    etiqueta: str
    tipo: str
    es_componente: bool


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
    segundo_nivel: SegundoNivel | None = None  # None = un solo nivel: el promedio ES la nota
    rubrica: Rubrica | None = None
    grupos: list[Grupo] = field(default_factory=list)

    exencion_ordinario: int = 80
    exencion_contra: str = ""  # ausente = promedio; obligatoria si hay segundo nivel
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
        if self.exencion_contra and self.exencion_contra not in EXENCION_CONTRA:
            raise ErrorModelo(
                f"`exencion_contra` inválido: {self.exencion_contra!r}. "
                f"Válidos: {', '.join(EXENCION_CONTRA)}. «promedio» mide el umbral contra el "
                f"promedio del curso; «calificacion_final» contra la calificación ya combinada "
                f"con el examen ordinario."
            )
        if self.segundo_nivel is not None and not self.exencion_contra:
            raise ErrorModelo(
                "El curso declara `segundo_nivel` pero no `exencion_contra`. Con dos niveles "
                "hay que decir contra cuál se mide el umbral de exención: `promedio` o "
                "`calificacion_final`. No hay valor por omisión a propósito: suponerlo "
                "convertiría una decisión del docente en una suposición del generador."
            )

    @property
    def presencial(self) -> bool:
        return self.modalidad in ("semipresencial", "escolarizada")

    def unidad(self, numero: str) -> Unidad | None:
        return next((u for u in self.unidades if u.numero == numero), None)

    def rubro(self, id_: str) -> Rubro | None:
        return next((r for r in self.rubros if r.id == id_), None)

    def metas_de(self, unidad: str) -> list[Meta]:
        return [m for m in self.metas if m.unidad == unidad]

    def aportes(self) -> Iterator[Aporte]:
        """Todo lo que aporta valor a un rubro, en orden: cada meta y luego sus componentes.

        Es la única definición de «lo que cuenta para un rubro» del proyecto. R2 filtra por
        `rubro`, R3 por `tipo` y la Fase 13 por `meta`; ninguna de las tres deriva la suya.
        Se devuelve plano —no agrupado por rubro— porque agrupar solo le sirve a R2.
        """
        for m in self.metas:
            yield Aporte(m, m.rubro, m.valor, m.etiqueta, m.tipo, False)
            for c in m.componentes:
                yield Aporte(m, c.rubro, c.valor, c.etiqueta, c.tipo, True)

    def nombre_archivo(self, grupo: str, ext: str) -> str:
        return f"DI-{self.ciclo}-{self.clave}-{grupo}.{ext}"


# -- carga -------------------------------------------------------------------


def _construir_componente(c: dict) -> Componente:
    c = dict(c)
    if "tipo" not in c:
        raise ErrorModelo(
            f"Componente «{c.get('etiqueta', '?')}»: falta `tipo`. "
            f"Válidos: {', '.join(TIPOS_COMPONENTE)}. No hay valor por omisión a propósito: "
            f"un tipo supuesto convertiría un examen mal escrito en un componente que nadie cuenta."
        )
    ev = c.pop("evidencia", None)
    evidencia = (
        Evidencia(**ev) if isinstance(ev, dict)
        else Evidencia(nombre=ev) if ev
        else None
    )
    return Componente(evidencia=evidencia, **c)


def _construir_meta(d: dict) -> Meta:
    sesiones = [Sesion(**s) for s in d.pop("sesiones", [])]
    evidencias = [
        Evidencia(**e) if isinstance(e, dict) else Evidencia(nombre=e)
        for e in d.pop("evidencias", [])
    ]
    componentes = [_construir_componente(c) for c in d.pop("componentes", [])]
    semanas = d.pop("semanas", None)
    if semanas is None and (s := d.pop("semana", None)) is not None:
        semanas = [s]
    return Meta(
        semanas=semanas or [],
        sesiones=sesiones,
        evidencias=evidencias,
        componentes=componentes,
        **d,
    )


def _construir_grupo(g: Any) -> Grupo:
    if not isinstance(g, dict):  # forma corta: solo el número
        return Grupo(numero=str(g))
    horario = Horario(**g.pop("horario", {}))
    return Grupo(numero=str(g.pop("numero")), horario=horario, **g)


def _construir_segundo_nivel(sn: dict | None) -> SegundoNivel | None:
    if sn is None:
        return None
    return SegundoNivel(
        promedio=Nivel(**sn["promedio"]),
        ordinario=Nivel(**sn["ordinario"]),
    )


def _construir_rubrica(rubrica: dict | None) -> Rubrica | None:
    if rubrica is None:
        return None
    r = dict(rubrica)
    filas = [FilaRubrica(**f) for f in r.pop("filas", [])]
    return Rubrica(filas=filas, **r)


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
        segundo_nivel=_construir_segundo_nivel(evaluacion.get("segundo_nivel")),
        rubrica=_construir_rubrica(d.pop("rubrica", None)),
        grupos=[_construir_grupo(g) for g in d.pop("grupos", [])],
        exencion_ordinario=evaluacion.get("exencion_ordinario", 80),
        exencion_contra=evaluacion.get("exencion_contra", ""),
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

    Un grupo con bloques filtra el recorrido de suspensiones por sus días presenciales. Una
    sesión con ``dia`` conserva su escape declarado y una virtual sigue en el día de entrega.
    """
    h = grupo.horario
    presencial = h.dias_presencial[0] if h.dias_presencial else 0
    # Solo un grupo que declara bloques filtra el recorrido de una suspensión. Sin bloques, el
    # comportamiento de cursos existentes y futuros permanece intacto.
    dias_clase = set(h.dias_presencial) if h.bloques else None
    for m in curso.metas:
        for s in m.sesiones:
            if s.dia is not None:  # escape declarado: se respeta literal
                dia, filtro = s.dia, None
            elif s.ambiente == "presencial":
                dia, filtro = presencial, dias_clase
            else:  # la entrega no se mueve con el horario de clase
                dia, filtro = h.dia_entrega, None
            s.fecha = cal.fecha_de(s.semana, dia, filtro)
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
