"""Capa de validación del Diseño Instruccional.

Ocho reglas que bloquean la generación de un DI defectuoso. La prueba de que sirven es
que detectan los dos defectos reales del ejemplo dorado `ejemplos/961 (1).pdf`: sus
porcentajes por rubro no cuadran con el esquema que él mismo declara (Proyecto ~22 %
contra 40 % declarado, Tareas ~58 % contra 40 %), aunque el total sí sume 100.

De ahí la regla 2: **no basta con que el total sume 100**. Hay que comparar rubro por
rubro, porque es ahí donde el error se esconde.

Uso:
    python src/validar.py cursos/2026-2/39056-big-data/curso.yaml
"""

from __future__ import annotations

import sys
from collections import Counter
from dataclasses import dataclass
from datetime import time, timedelta
from pathlib import Path

import calendario
import modelo
from modelo import Config, Curso

ERROR = "error"
AVISO = "aviso"
RECORDATORIO = "recordatorio"

SIMBOLO = {ERROR: "✗", AVISO: "!", RECORDATORIO: "·"}

# El IEDI evalúa cursos semipresenciales y a distancia (CIAD, v2023-1).
MODALIDADES_IEDI = ("semipresencial", "a_distancia")

# Taquigrafía que este repositorio usa entre agentes y que no significa nada para un
# alumno. Se vigila solo en el texto que acaba impreso; en comentarios del `curso.yaml`
# es correcta y necesaria. Ver `Validador.estilo`.
JERGA_INTERNA = {
    "§": "el símbolo de sección, que aquí abrevia apartados del PUA",
    "PUA": "la palabra «PUA», que nombra un documento que el alumno no tiene",
    "REQ-": "un identificador de requisito del proyecto",
    "curso.yaml": "el nombre de un archivo interno",
    "cubre_temas": "el nombre de un campo del modelo",
    "practica_pua": "el nombre de un campo del modelo",
    "IEDI": "la rúbrica interna de evaluación docente",
}

# Indicadores indispensables que dependen de la plataforma institucional, no del
# documento. Se reportan al docente como recordatorio: el generador no puede
# comprobarlos. Ver conocimiento/rubricas/iedi-2023-1.md.
IEDI_PLATAFORMA = {
    "2.4": "Indica la autoría o ficha bibliográfica de cada recurso de apoyo de terceros.",
    "3.1": "Publica la planeación para lectura en el navegador, no solo como archivo adjunto.",
    "3.2": "Usa la herramienta adecuada para publicar cada recurso (elemento, carpeta, enlace).",
    "3.5": "Crea el Foro de dudas del curso.",
    "4.1": "Coloca cada elemento de la planeación en su sección con la herramienta correcta.",
}


@dataclass
class Hallazgo:
    regla: str
    nivel: str
    mensaje: str

    def __str__(self) -> str:
        return f"{SIMBOLO[self.nivel]} [{self.regla}] {self.mensaje}"


class Informe:
    """Los hallazgos de una validación, con el veredicto."""

    def __init__(self, curso: Curso, hallazgos: list[Hallazgo]):
        self.curso = curso
        self.hallazgos = hallazgos

    def de(self, nivel: str) -> list[Hallazgo]:
        return [h for h in self.hallazgos if h.nivel == nivel]

    @property
    def errores(self) -> list[Hallazgo]:
        return self.de(ERROR)

    @property
    def valido(self) -> bool:
        return not self.errores

    def texto(self) -> str:
        cabecera = (
            f"{self.curso.nombre} · {self.curso.clave} · ciclo {self.curso.ciclo} · "
            f"{self.curso.modalidad} · grupos "
            f"{', '.join(g.numero for g in self.curso.grupos)}"
        )
        lineas = [cabecera, "-" * len(cabecera)]
        for nivel in (ERROR, AVISO, RECORDATORIO):
            lineas += [str(h) for h in self.de(nivel)]
        n_err, n_av = len(self.errores), len(self.de(AVISO))
        cola = f", {n_av} aviso(s)" if n_av else ""
        lineas.append("")
        lineas.append(
            "VÁLIDO" if self.valido else f"NO VÁLIDO — {n_err} error(es){cola}"
        )
        return "\n".join(lineas)


class _Validador:
    """Acumula hallazgos aplicando las ocho reglas."""

    def __init__(self, curso: Curso, cfg: Config, cal: calendario.Calendario | None):
        self.c = curso
        self.cfg = cfg
        self.cal = cal
        self.hallazgos: list[Hallazgo] = []

    def _add(self, regla: str, nivel: str, mensaje: str) -> None:
        self.hallazgos.append(Hallazgo(regla, nivel, mensaje))

    def error(self, regla: str, mensaje: str) -> None:
        self._add(regla, ERROR, mensaje)

    def aviso(self, regla: str, mensaje: str) -> None:
        self._add(regla, AVISO, mensaje)

    # -- Regla 1: los porcentajes del esquema suman exactamente 100 ----------

    def regla_1(self) -> None:
        reglas = self.cfg.esquemas["reglas"]
        if not self.c.rubros:
            self.error("R1", "El curso no declara rubros de evaluación.")
            return

        total = round(sum(r.porcentaje for r in self.c.rubros), 2)
        exacta = reglas["suma_exacta"]
        if total != exacta:
            desglose = " + ".join(f"{r.etiqueta} {r.porcentaje:g}" for r in self.c.rubros)
            self.error(
                "R1",
                f"Los porcentajes del esquema suman {total:g}, no {exacta}: {desglose}.",
            )

        cuenta = Counter(r.id for r in self.c.rubros)
        if repetidos := [i for i, n in cuenta.items() if n > 1]:
            self.error("R1", f"Rubros duplicados: {', '.join(sorted(repetidos))}.")

        ex = self.c.exencion_ordinario
        if not reglas["exencion_minima"] <= ex <= reglas["exencion_maxima"]:
            self.error(
                "R1",
                f"El umbral de exención ({ex}) queda fuera de "
                f"[{reglas['exencion_minima']}, {reglas['exencion_maxima']}]. "
                f"No puede ser menor que la calificación mínima aprobatoria (Art. 65).",
            )

        # La calificación puede tener dos niveles: el promedio del curso y el examen
        # ordinario. Un curso que no los declara califica a uno solo —el promedio es la
        # calificación— y no recibe ninguna de estas comprobaciones.
        sn = self.c.segundo_nivel
        contra = self.c.exencion_contra or "promedio"
        if sn is not None:
            suma = round(sn.promedio.porcentaje + sn.ordinario.porcentaje, 2)
            if suma != exacta:
                self.error(
                    "R1",
                    f"El segundo nivel suma {suma:g}, no {exacta}: "
                    f"{sn.promedio.etiqueta} {sn.promedio.porcentaje:g} + "
                    f"{sn.ordinario.etiqueta} {sn.ordinario.porcentaje:g}.",
                )
            elif sn.ordinario.porcentaje == 0:
                self.aviso(
                    "R1",
                    f"El segundo nivel deja el examen ordinario en 0 y el promedio en "
                    f"{sn.promedio.porcentaje:g}: es decir que no hay segundo nivel. Si el "
                    f"ordinario no pesa, quita `segundo_nivel` en vez de declararlo en cero.",
                )
            elif sn.promedio.porcentaje == 0:
                self.aviso(
                    "R1",
                    f"El segundo nivel deja el promedio del curso en 0 y el examen ordinario "
                    f"en {sn.ordinario.porcentaje:g}: nada de lo que el alumno haga durante el "
                    f"ciclo cuenta para su calificación. El Art. 68 pide evaluación permanente.",
                )
            if contra == "calificacion_final":
                self.error(
                    "R1",
                    f"La exención ({ex}) está declarada contra la calificación final, pero el "
                    f"curso califica a dos niveles: el promedio pesa "
                    f"{sn.promedio.porcentaje:g} % y el examen ordinario "
                    f"{sn.ordinario.porcentaje:g} %. Medido contra el promedio, el umbral se "
                    f"alcanza antes de presentar el ordinario —que es justo de lo que exenta—; "
                    f"medido contra la calificación final habría que presentarlo para poder "
                    f"llegar a él. Declara `exencion_contra: promedio` (Art. 68).",
                )
        elif contra == "calificacion_final":
            self.aviso(
                "R1",
                f"La exención ({ex}) está declarada contra la calificación final y el curso no "
                f"declara `segundo_nivel`: hoy el promedio es la calificación final, así que da "
                f"lo mismo. Dejará de darlo el día que el curso declare los dos niveles; "
                f"escríbelo como `exencion_contra: promedio` (Art. 68).",
            )

        # Si se declaró un esquema del catálogo, debe coincidir con lo capturado.
        if self.c.esquema_id:
            try:
                esquema = self.cfg.esquema(self.c.esquema_id)
            except modelo.ErrorModelo as e:
                self.error("R1", str(e))
                return
            catalogo = {r["id"]: r["porcentaje"] for r in esquema["rubros"]}
            propio = {r.id: r.porcentaje for r in self.c.rubros}
            if catalogo != propio:
                self.aviso(
                    "R1",
                    f"Los rubros del curso no coinciden con el esquema «{self.c.esquema_id}» "
                    f"del catálogo ({catalogo} contra {propio}). Si el cambio es "
                    f"intencional, quita `esquema_id` o registra un esquema nuevo.",
                )
            nivel_catalogo = esquema.get("segundo_nivel")
            nivel_propio = None
            if sn is not None:
                nivel_propio = {
                    "promedio": {
                        "porcentaje": sn.promedio.porcentaje,
                        "etiqueta": sn.promedio.etiqueta,
                    },
                    "ordinario": {
                        "porcentaje": sn.ordinario.porcentaje,
                        "etiqueta": sn.ordinario.etiqueta,
                    },
                }
            if nivel_catalogo != nivel_propio:
                self.aviso(
                    "R1",
                    f"El segundo nivel del curso no coincide con el esquema "
                    f"«{self.c.esquema_id}» del catálogo ({nivel_catalogo} contra "
                    f"{nivel_propio}). Si el cambio es intencional, quita `esquema_id` o "
                    f"registra un esquema nuevo.",
                )

    # -- Regla 2: las metas suman lo que dice el esquema, rubro por rubro ----

    def regla_2(self) -> None:
        if rubrica := self.c.rubrica:
            suma_rubrica = round(sum(f.puntos for f in rubrica.filas), 2)
            total_rubrica = round(rubrica.total, 2)
            if suma_rubrica != total_rubrica:
                self.error(
                    "R2",
                    f"La rúbrica suma {suma_rubrica:g} puntos, pero declara "
                    f"{total_rubrica:g} puntos.",
                )
            if rubrica.meta and rubrica.meta not in {m.id for m in self.c.metas}:
                self.error(
                    "R2",
                    f"La rúbrica se asocia a la meta «{rubrica.meta}», que no existe.",
                )
            if rubrica.rubro and rubrica.rubro not in {r.id for r in self.c.rubros}:
                self.error(
                    "R2",
                    f"La rúbrica se asocia al rubro «{rubrica.rubro}», que no existe.",
                )

        if not self.c.rubros:
            return  # ya reportado en R1

        ids = {r.id for r in self.c.rubros}
        for m in self.c.metas:
            if m.rubro not in ids:
                self.error(
                    "R2",
                    f"{m.etiqueta} se imputa al rubro «{m.rubro}», que no existe. "
                    f"Rubros declarados: {', '.join(sorted(ids))}.",
                )

        for a in self.c.aportes():
            if a.es_componente and a.rubro not in ids:
                self.error(
                    "R2",
                    f"{a.meta.etiqueta}: el componente «{a.etiqueta}» se imputa al rubro "
                    f"«{a.rubro}», que no existe. "
                    f"Rubros declarados: {', '.join(sorted(ids))}.",
                )

        # Lo que un rubro aporta al 100 se convierte UNA vez, sobre su suma cruda. Convertir
        # aporte a aporte acumula error de coma flotante: 21 aportes de 7 pts más uno de 3
        # sobre un rubro de 150 dan 29.99999999999999 contra los 30 % declarados, y R2
        # denunciaría un curso correcto. Los aportes a rubros que no existen quedan fuera de
        # esta suma; ya se denunciaron arriba y abajo.
        total_metas = round(
            sum(
                r.a_porcentaje(sum(a.valor for a in self.c.aportes() if a.rubro == r.id))
                for r in self.c.rubros
            ),
            2,
        )
        total_rubros = round(sum(r.porcentaje for r in self.c.rubros), 2)
        if total_metas != total_rubros:
            self.error(
                "R2",
                f"El valor de las metas suma {total_metas:g} %, pero el esquema declara "
                f"{total_rubros:g} %.",
            )

        # El defecto del ejemplo 961: el total cuadra, los rubros no. Y el del 531: el rubro
        # declara 150 pts y sus aportes suman 140. Se compara dentro de cada rubro, contra su
        # `base` y en su propia unidad, así que nunca se suman unidades distintas entre sí.
        for r in self.c.rubros:
            aportes = [a for a in self.c.aportes() if a.rubro == r.id]
            suma = round(sum(a.valor for a in aportes), 2)
            if suma != r.base:
                unidad = "pts" if r.unidad == "puntos" else "%"
                imputados = ", ".join(a.etiqueta for a in aportes) or "ninguno"
                self.error(
                    "R2",
                    f"Rubro «{r.etiqueta}»: sus aportes suman {suma:g} {unidad} pero el rubro "
                    f"declara {r.base:g} {unidad}. Aportes imputados: {imputados}.",
                )

        if negativas := [m.id for m in self.c.metas if m.valor < 0]:
            self.error("R2", f"Metas con valor negativo: {', '.join(negativas)}.")
        if negativos := [
            f"{a.meta.etiqueta} · {a.etiqueta}"
            for a in self.c.aportes()
            if a.es_componente and a.valor < 0
        ]:
            self.error("R2", f"Componentes con valor negativo: {', '.join(negativos)}.")
        cuenta = Counter(m.id for m in self.c.metas)
        if repetidos := [i for i, n in cuenta.items() if n > 1]:
            self.error("R2", f"Metas duplicadas: {', '.join(sorted(repetidos))}.")

    # -- Regla 3: mínimo dos exámenes parciales (Art. 68) --------------------

    def regla_3(self) -> None:
        minimo = self.cfg.esquemas["reglas"]["parciales_minimos"]
        # Un examen parcial es un aporte de ese tipo, se declare como meta propia o dentro de
        # la actividad de otra meta —los tres del 531 viven así—. Cada aporte cuenta uno: una
        # meta de examen con un componente de examen son dos exámenes distintos, con etiqueta
        # y valor propios, y el documento los imprimirá por separado.
        parciales = [a for a in self.c.aportes() if a.tipo == "examen_parcial"]
        if len(parciales) < minimo:
            self.error(
                "R3",
                f"Hay {len(parciales)} examen(es) parcial(es); el artículo 68 del Estatuto "
                f"Escolar exige no menos de {minimo} por periodo escolar.",
            )

        declarados = sum(r.parciales for r in self.c.rubros)
        if declarados and declarados != len(parciales):
            self.aviso(
                "R3",
                f"El esquema declara {declarados} parciales pero el curso declara "
                f"{len(parciales)} examen(es) parcial(es), contando los que viven como "
                f"componente de la actividad de otra meta.",
            )

    # -- Regla 4: toda unidad del PUA tiene al menos una meta ----------------

    def regla_4(self) -> None:
        if not self.c.unidades:
            self.error("R4", "El curso no declara unidades. ¿Se ingirió el PUA?")
            return

        for u in self.c.unidades:
            if not self.c.metas_de(u.numero):
                self.error(
                    "R4",
                    f"La unidad {u.numero} «{u.nombre}» no tiene ninguna meta asignada.",
                )

        numeros = {u.numero for u in self.c.unidades}
        for m in self.c.metas:
            if m.unidad not in numeros:
                self.error(
                    "R4",
                    f"{m.etiqueta} se asigna a la unidad «{m.unidad}», que no existe en el "
                    f"PUA. Unidades: {', '.join(sorted(numeros))}.",
                )

        # Cobertura temática: un tema del PUA sin meta es un hueco del diseño.
        cubiertos = {t for m in self.c.metas for t in m.cubre_temas}
        for u in self.c.unidades:
            if sueltos := [t for t in u.temas if t not in cubiertos]:
                self.aviso(
                    "R4",
                    f"Unidad {u.numero}: {len(sueltos)} tema(s) sin meta que los cubra "
                    f"— {'; '.join(sueltos[:3])}{'…' if len(sueltos) > 3 else ''}.",
                )

    # -- Regla 5: toda semana 1..N tiene actividad ---------------------------

    def regla_5(self) -> None:
        if self.cal is None:
            return  # ya reportado en R6

        n = self.cal.total_semanas
        ocupadas = {s for m in self.c.metas for s in m.semanas}
        ocupadas |= {s.semana for m in self.c.metas for s in m.sesiones}

        if vacias := [i for i in range(1, n + 1) if i not in ocupadas]:
            self.error(
                "R5",
                f"El ciclo {self.c.ciclo} tiene {n} semanas y quedan sin actividad: "
                f"{', '.join(map(str, vacias))}.",
            )

        if fuera := sorted(s for s in ocupadas if not 1 <= s <= n):
            self.error(
                "R5",
                f"Hay metas programadas en semanas inexistentes ({', '.join(map(str, fuera))}); "
                f"el ciclo {self.c.ciclo} tiene {n}.",
            )

    # -- Regla 6: ninguna entrega en suspensión ni fuera del periodo ---------

    def _horario(self) -> None:
        """Forma del horario: horas legibles, coherentes y sin cruzarse (D-05).

        Vive en R6 —el dominio de calendario y fechas— en vez de abrir una regla nueva. La hora
        ilegible es un hallazgo, no un error de carga: así llega al mismo informe que el resto de
        los defectos de un DI y bloquea la generación con una explicación concreta.
        """
        for g in self.c.grupos:
            tramos: dict[int, list[tuple[time, time]]] = {}
            for b in g.horario.bloques:
                dia = calendario.DIAS[b.dia]
                horas: dict[str, time] = {}
                for campo, valor in (("inicio", b.inicio), ("fin", b.fin)):
                    try:
                        horas[campo] = time.fromisoformat(str(valor))
                    except ValueError:
                        self.error(
                            "R6",
                            f"Grupo {g.numero}, bloque del {dia}: la hora de {campo} "
                            f"«{valor}» no está escrita como HH:MM.",
                        )
                if len(horas) < 2:
                    continue
                if horas["fin"] <= horas["inicio"]:
                    self.error(
                        "R6",
                        f"Grupo {g.numero}, bloque del {dia}: la hora de fin ({b.fin}) no es "
                        f"posterior a la de inicio ({b.inicio}).",
                    )
                    continue
                tramos.setdefault(b.dia, []).append((horas["inicio"], horas["fin"]))

            for dia, lista in tramos.items():
                lista.sort()
                for (ini, fin), (sig_ini, sig_fin) in zip(lista, lista[1:]):
                    if sig_ini < fin:
                        self.error(
                            "R6",
                            f"Grupo {g.numero}: dos bloques del {calendario.DIAS[dia]} se "
                            f"solapan ({ini:%H:%M}–{fin:%H:%M} y "
                            f"{sig_ini:%H:%M}–{sig_fin:%H:%M}); un grupo no puede estar en dos "
                            f"clases a la vez.",
                        )

    def _sesiones_suspendidas_sin_reprogramacion(self) -> None:
        """Bloquea una sesión suspendida que no tiene alternativa declarada.

        Una sesión presencial suspendida usa el siguiente bloque virtual del grupo. Si ese bloque
        no existe dentro del ciclo, todavía puede usar otro bloque presencial de la misma semana;
        sin ninguna de las dos alternativas no se puede escribir una fecha válida en el DI.
        """
        for g in self.c.grupos:
            if not g.imparte or not g.horario.bloques or not g.horario.dias_presencial:
                continue
            dias = set(g.horario.dias_presencial)
            virtuales = set(g.horario.dias_virtual)
            primero = g.horario.dias_presencial[0]

            for m in self.c.metas:
                for sesion in m.sesiones:
                    if sesion.ambiente != "presencial":
                        continue
                    if not 1 <= sesion.semana <= self.cal.total_semanas:
                        continue  # R5 ya informa la semana inexistente.
                    dia = sesion.dia if sesion.dia is not None else primero
                    if sesion.dia is not None and sesion.dia not in dias:
                        self.aviso(
                            "R6",
                            f"La {m.etiqueta} fija su sesión presencial en "
                            f"{calendario.DIAS[sesion.dia]} y el grupo {g.numero} no tiene "
                            "bloque presencial ese día.",
                        )
                    fecha = self.cal.semana(sesion.semana).inicio + timedelta(days=dia)
                    if not self.cal.es_suspension(fecha):
                        continue
                    if self.cal.siguiente_dia_de_bloque(fecha, virtuales) is not None:
                        continue
                    if self.cal.dia_de_clase(sesion.semana, dia, dias) is not None:
                        continue
                    self.error(
                        "R6",
                        f"{m.etiqueta}: el grupo {g.numero} tiene suspensión el "
                        f"{calendario.texto_fecha(fecha)} y no declara un bloque virtual "
                        "posterior ni otro bloque presencial esa semana para reprogramarla.",
                    )

    def regla_6(self) -> None:
        self._horario()
        if self.cal is None:
            self.error(
                "R6",
                f"No se pudo cargar el calendario del ciclo {self.c.ciclo}; las fechas no "
                f"son verificables. No des el documento por bueno.",
            )
            return

        for m in self.c.metas:
            for s in m.sesiones:
                if s.fecha is None:
                    continue  # aún sin resolver; la resuelve calendario.py
                try:
                    self.cal.validar_entrega(s.fecha)
                except calendario.ErrorCalendario as e:
                    self.error("R6", f"{m.etiqueta} ({s.ambiente}): {e}")

        # Las suspensiones deben quedar visibles en el documento, no solo evitadas.
        for susp in self.cal.suspensiones:
            sem = self.cal.semana_de(susp.fecha)
            if sem is not None and sem not in {s for m in self.c.metas for s in m.semanas}:
                self.aviso(
                    "R6",
                    f"La semana {sem} contiene la suspensión del "
                    f"{calendario.texto_fecha(susp.fecha)} ({susp.motivo}) y no tiene metas.",
                )

        self._sesiones_suspendidas_sin_reprogramacion()

    # -- Regla 7: citas legales obligatorias y firma por grupo ---------------

    def regla_7(self) -> None:
        pol = self.cfg.politicas
        requeridas = list(pol["citas_obligatorias"])
        if self.c.practica:
            requeridas += pol["citas_si_practica"]
        if self.c.modalidad != "escolarizada":
            requeridas += pol["citas_si_no_presencial"]

        presentes = set(self.c.citas)
        if faltan := [c for c in requeridas if c not in presentes]:
            self.error(
                "R7",
                f"Faltan citas legales obligatorias: {', '.join(faltan)}. El artículo 66 "
                f"del Estatuto Escolar obliga a dar a conocer criterios y metodología al "
                f"inicio del curso.",
            )

        for cita in self.c.citas:
            try:
                self.cfg.articulo(cita)
            except modelo.ErrorModelo as e:
                self.error("R7", str(e))

        if not self.c.grupos:
            self.error("R7", "El curso no tiene grupos; no hay bloque de firma que emitir.")
        for g in self.c.grupos:
            if not g.numero.strip():
                self.error("R7", "Hay un grupo sin número: el bloque de firma quedaría anónimo.")
        numeros = [g.numero for g in self.c.grupos]
        if len(set(numeros)) != len(numeros):
            self.error("R7", f"Grupos repetidos: {', '.join(numeros)}.")

        if not pol.get("convivencia"):
            self.error("R7", "config/politicas.yaml no define reglas de convivencia.")
        for regla in pol.get("convivencia", []):
            if not regla.get("sancion"):
                self.error(
                    "R7",
                    f"La regla de convivencia «{regla.get('titulo', regla.get('id'))}» no "
                    f"declara sanción. Sin sanción no es una regla.",
                )

    # -- Regla 8: indicadores indispensables del IEDI ------------------------

    def regla_8(self) -> None:
        if self.c.modalidad not in MODALIDADES_IEDI:
            self.aviso(
                "R8",
                f"El IEDI v2023-1 evalúa cursos semipresenciales y a distancia; la modalidad "
                f"{self.c.modalidad} no se rige por él. Se omiten sus indicadores.",
            )
            return

        semipresencial = self.c.modalidad == "semipresencial"

        # 1.1 — descripción general completa
        exigidos = {
            "competencia_general": "competencia y justificación",
            "proposito_general": "propósito general",
            "estrategia_general": "estrategia de enseñanza-aprendizaje",
            "evidencias_desempeno": "evidencias de desempeño",
            "criterios_evaluacion": "criterios generales de evaluación",
        }
        if faltan := [
            etiqueta
            for campo, etiqueta in exigidos.items()
            if not str(self.c.contenido.get(campo, "")).strip()
        ]:
            self.error("IEDI 1.1", f"La descripción general no incluye: {', '.join(faltan)}.")
        if not self.c.identificacion:
            self.error("IEDI 1.1", "Faltan los datos de identificación del PUA §I.")

        # 1.5 — toda meta con evidencia y valor porcentual
        for m in self.c.metas:
            if not m.evidencias:
                self.error("IEDI 1.5", f"{m.etiqueta} no declara evidencia ni producto.")
            if m.valor == 0 and m.tipo not in ("encuadre", "cierre"):
                self.error("IEDI 1.5", f"{m.etiqueta} no tiene valor porcentual.")

        # 1.6 — el plan distingue lo presencial de lo asincrónico
        if semipresencial:
            ambientes = {s.ambiente for m in self.c.metas for s in m.sesiones}
            if not {"presencial", "virtual"} <= ambientes:
                self.error(
                    "IEDI 1.6",
                    f"El plan de actividades no distingue sesiones presenciales de virtuales "
                    f"(ambientes usados: {', '.join(sorted(ambientes)) or 'ninguno'}).",
                )

        # 1.7 — cada meta descrita en pasos
        for m in self.c.metas:
            if not m.sesiones:
                self.error("IEDI 1.7", f"{m.etiqueta} no tiene sesiones descritas.")
            elif sin_pasos := [s.ambiente for s in m.sesiones if not s.pasos]:
                self.error(
                    "IEDI 1.7",
                    f"{m.etiqueta}: sesión {'/'.join(sin_pasos)} sin pasos. La actividad debe "
                    f"describir la secuencia a seguir.",
                )

        # 1.8 — recursos, evidencia y fecha de entrega
        for m in self.c.metas:
            if not m.semanas:
                self.error("IEDI 1.8", f"{m.etiqueta} no tiene semana de entrega.")
            if not m.criterios_evaluacion:
                self.aviso(
                    "IEDI 1.8",
                    f"{m.etiqueta} no declara criterios de evaluación de la evidencia.",
                )

        # 1.9 — en semipresencial, cada meta ubica sus pasos en un espacio
        if semipresencial:
            for m in self.c.metas:
                if any(s.ambiente not in modelo.AMBIENTES for s in m.sesiones):
                    self.error(
                        "IEDI 1.9",
                        f"{m.etiqueta} tiene pasos sin espacio de aprendizaje identificado.",
                    )

        # 1.16 — políticas del curso
        pol = self.cfg.politicas
        if not pol.get("acreditacion"):
            self.error("IEDI 1.16", "No hay criterios de acreditación en config/politicas.yaml.")
        if not any(r.get("id") == "honestidad" for r in pol.get("convivencia", [])):
            self.error("IEDI 1.16", "Las políticas no incluyen honestidad académica.")

        # Lo que depende de la plataforma, no del documento.
        for indicador, texto in IEDI_PLATAFORMA.items():
            self._add(f"IEDI {indicador}", RECORDATORIO, texto)

    # -- Guardia de estilo: nada de jerga interna en lo que el alumno lee ----

    def estilo(self) -> None:
        """El documento lo lee un alumno que no tiene el PUA ni este repositorio delante.

        No es una novena regla —las ocho son el contrato— sino un guardia contra una fuga
        concreta que ya ocurrió: `detalle: "nueve prácticas conforme a la §VI del PUA"` se
        escribió con la taquigrafía que `AGENTS.md` usa para mapear secciones, y acabó
        impresa en el documento. Se avisa, no se falla: si el PUA trae literalmente una de
        estas marcas, copiarla es lo correcto y el profesor decide.
        """
        for texto, donde in self._texto_visible():
            for marca, motivo in JERGA_INTERNA.items():
                if marca in texto:
                    self.aviso(
                        "ESTILO",
                        f"{donde} contiene {motivo}: «{texto.strip()[:70]}». El alumno no "
                        f"tiene esa referencia a la vista; redáctalo en sus términos.",
                    )
                    break

    def _texto_visible(self):
        """Cada cadena que acaba impresa en el documento, con su procedencia."""
        for r in self.c.rubros:
            yield r.detalle, f"El detalle del rubro «{r.etiqueta}»"
        if self.c.rubrica is not None:
            for f in self.c.rubrica.filas:
                yield f.concepto, "El concepto de una fila de la rúbrica"
                yield f.descripcion, f"La descripción del concepto «{f.concepto}»"
        for campo, valor in self.c.contenido.items():
            yield str(valor), f"El campo «{campo}»"
        for m in self.c.metas:
            yield m.enunciado, f"El enunciado de la {m.etiqueta}"
            for lista, nombre in (
                (m.que_voy_a_aprender, "qué voy a aprender"),
                (m.criterios_evaluacion, "criterios de evaluación"),
                (m.reflexion, "reflexión"),
            ):
                for t in lista:
                    yield str(t), f"La {nombre} de la {m.etiqueta}"
            for s in m.sesiones:
                yield s.actividad_tabla, f"La actividad de la {m.etiqueta} ({s.ambiente})"
                for p in s.pasos:
                    yield str(p), f"Un paso de la {m.etiqueta} ({s.ambiente})"
            for e in m.evidencias:
                yield e.nombre, f"Una evidencia de la {m.etiqueta}"

    def correr(self) -> list[Hallazgo]:
        for regla in (
            self.regla_1, self.regla_2, self.regla_3, self.regla_4,
            self.regla_5, self.regla_6, self.regla_7, self.regla_8,
            self.estilo,
        ):
            regla()
        for a in self.c.avisos:
            self.aviso("PUA", a)
        return self.hallazgos


def validar(
    curso: Curso,
    cfg: Config | None = None,
    cal: calendario.Calendario | None = None,
) -> Informe:
    """Aplica las ocho reglas. El calendario se carga solo si no se pasa."""
    cfg = cfg or Config()
    if cal is None:
        try:
            cal = calendario.cargar(curso.ciclo)
        except calendario.ErrorCalendario:
            cal = None
    return Informe(curso, _Validador(curso, cfg, cal).correr())


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("Uso: python src/validar.py <ruta a curso.yaml>", file=sys.stderr)
        return 2
    try:
        curso = modelo.cargar(Path(argv[1]))
    except modelo.ErrorModelo as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    informe = validar(curso)
    print(informe.texto())
    return 0 if informe.valido else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
