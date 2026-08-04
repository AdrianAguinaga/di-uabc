"""Grafo del dominio: qué cubre qué, y qué quedó suelto.

El proyecto tiene la información repartida entre el PUA, el calendario, el Estatuto, la
configuración y el `curso.yaml`. Cada archivo por separado es legible; lo que nadie puede
ver leyéndolos de uno en uno son las **conexiones**. Dos preguntas concretas que este grafo
contesta y que antes exigían cotejar a mano:

  - ¿qué temas del PUA quedaron sin ninguna meta que los cubra?
  - ¿qué materias comparten competencias?

Sirve además como mapa para navegar la lógica del proyecto: el grafo es, literalmente, cómo
se engancha todo.

No inventa relaciones. Cada arista sale de un dato declarado —`cubre_temas`, `practica_pua`,
`unidad`, `semanas`, `citas`— y por eso el informe de auditoría es utilizable: si dice que un
tema quedó suelto, es que nadie lo declaró cubierto.

Uso:
    python src/grafo.py            # escribe grafo/grafo.json, index.html y AUDITORIA.md
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import yaml

import calendario
import generar
import modelo
from modelo import Config

RAIZ = Path(__file__).resolve().parent.parent
DIR_GRAFO = RAIZ / "grafo"

TIPOS = (
    "pua", "unidad", "tema", "competencia", "practica",
    "curso", "meta", "evidencia", "criterio", "semana",
    "articulo", "plantilla", "profesor", "grupo",
)


class ErrorGrafo(Exception):
    """No se pudo construir el grafo."""


# -- estructura --------------------------------------------------------------


@dataclass
class Nodo:
    id: str
    tipo: str
    etiqueta: str
    datos: dict = field(default_factory=dict)


@dataclass
class Arista:
    origen: str
    destino: str
    tipo: str


class Grafo:
    def __init__(self) -> None:
        self.nodos: dict[str, Nodo] = {}
        self.aristas: list[Arista] = []

    def nodo(self, id_: str, tipo: str, etiqueta: str, datos: dict | None = None) -> str:
        """Idempotente: el mismo id no se duplica, se enriquece.

        `datos` va como diccionario y no como `**kwargs` a propósito: los atributos del
        dominio incluyen claves como `tipo`, que chocarían con los parámetros.
        """
        if tipo not in TIPOS:
            raise ErrorGrafo(f"Tipo de nodo desconocido: {tipo!r}")
        if id_ in self.nodos:
            self.nodos[id_].datos.update(datos or {})
        else:
            self.nodos[id_] = Nodo(id_, tipo, etiqueta, dict(datos or {}))
        return id_

    def arista(self, origen: str, destino: str, tipo: str) -> None:
        self.aristas.append(Arista(origen, destino, tipo))

    def de_tipo(self, tipo: str) -> list[Nodo]:
        return [n for n in self.nodos.values() if n.tipo == tipo]

    def salientes(self, id_: str, tipo: str | None = None) -> list[Arista]:
        return [a for a in self.aristas if a.origen == id_ and (tipo is None or a.tipo == tipo)]

    def entrantes(self, id_: str, tipo: str | None = None) -> list[Arista]:
        return [a for a in self.aristas if a.destino == id_ and (tipo is None or a.tipo == tipo)]

    def a_dict(self) -> dict:
        """Ordenado, para que regenerar sin cambios produzca un archivo idéntico."""
        return {
            "nodos": [
                {"id": n.id, "tipo": n.tipo, "etiqueta": n.etiqueta, **({"datos": n.datos} if n.datos else {})}
                for n in sorted(self.nodos.values(), key=lambda n: n.id)
            ],
            "aristas": [
                {"origen": a.origen, "destino": a.destino, "tipo": a.tipo}
                for a in sorted(self.aristas, key=lambda a: (a.origen, a.tipo, a.destino))
            ],
        }


# -- lectura del PUA ---------------------------------------------------------


def _normalizar(texto: str) -> str:
    """Para comparar textos entre materias: sin acentos, sin puntuación, en minúsculas."""
    sin_acentos = "".join(
        c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn"
    )
    return " ".join(re.sub(r"[^\w\s]", " ", sin_acentos.lower()).split())


def _huella(texto: str) -> str:
    return hashlib.sha256(_normalizar(texto).encode("utf-8")).hexdigest()[:12]


def leer_pua(ruta: Path) -> dict:
    """Extrae del Markdown del PUA lo que el grafo necesita.

    Se lee el PUA y no solo el `curso.yaml` a propósito: así se ve si un tema del programa
    oficial ni siquiera llegó al curso, que es un hueco que ningún archivo del curso puede
    delatar por sí mismo.
    """
    texto = ruta.read_text(encoding="utf-8")
    partes = texto.split("---", 2)
    if len(partes) < 3:
        raise ErrorGrafo(f"{ruta.name}: no tiene front-matter YAML.")
    frente = yaml.safe_load(partes[1]) or {}

    pua = {
        "clave": str(frente.get("clave", "")),
        "nombre": frente.get("nombre", ""),
        "programa_educativo": frente.get("programa_educativo", ""),
        "ruta": generar.relativa(ruta),
        "competencia_general": "",
        "unidades": [],
        "practicas": [],
    }

    if m := re.search(r"^## III\..*?\n+(.+?)(?=\n##)", texto, re.S | re.M):
        pua["competencia_general"] = " ".join(m.group(1).split())

    for bloque in re.finditer(
        r"^### UNIDAD ([IVXL]+)\.\s*(.+?)\n(.*?)(?=^### |^## )", texto, re.S | re.M
    ):
        numero, nombre, cuerpo = bloque.group(1), bloque.group(2).strip(), bloque.group(3)
        competencia = ""
        if c := re.search(r"\*\*Competencia:\*\*\s*(.+?)(?=\n\n)", cuerpo, re.S):
            competencia = " ".join(c.group(1).split())
        temas = [t.strip() for t in re.findall(r"^- (.+)$", cuerpo, re.M)]
        pua["unidades"].append(
            {"numero": numero, "nombre": nombre, "competencia": competencia, "temas": temas}
        )

    if seccion := re.search(r"^## VI\..*?\n(.*?)(?=^## )", texto, re.S | re.M):
        for fila in re.findall(r"^\|(.+)\|\s*$", seccion.group(1), re.M):
            celdas = [c.strip() for c in fila.split("|")]
            if len(celdas) < 3 or not celdas[0].isdigit():
                continue  # encabezado, separador, o continuación de una fila partida
            pua["practicas"].append(
                {"numero": int(celdas[0]), "unidad": celdas[1], "nombre": celdas[2]}
            )
    return pua


def descubrir() -> tuple[list[Path], list[Path]]:
    return (
        sorted((RAIZ / "puas" / "md").glob("*.md")),
        sorted((RAIZ / "cursos").glob("*/*/curso.yaml")),
    )


# -- construcción ------------------------------------------------------------


def _competencia(g: Grafo, texto: str, alcance: str) -> str:
    """Un nodo por texto de competencia: si dos materias declaran la misma, es el mismo nodo.

    De ahí sale la respuesta a «qué materias comparten competencias». La comparación es por
    texto normalizado —sin acentos ni puntuación—, nunca por parecido semántico: el grafo no
    adivina, y una coincidencia aquí significa que alguien copió literalmente.
    """
    return g.nodo(
        f"competencia:{_huella(texto)}",
        "competencia",
        texto[:80] + ("…" if len(texto) > 80 else ""),
        {"texto": texto, "alcance": alcance},
    )


def construir(puas: list[Path], cursos: list[Path], cfg: Config | None = None) -> Grafo:
    cfg = cfg or Config()
    g = Grafo()

    for ruta in puas:
        p = leer_pua(ruta)
        id_pua = g.nodo(
            f"pua:{p['clave']}", "pua", f"{p['clave']} {p['nombre']}",
            {"nombre": p["nombre"], "programa": p["programa_educativo"], "ruta": p["ruta"]},
        )
        if p["competencia_general"]:
            g.arista(id_pua, _competencia(g, p["competencia_general"], "general"), "declara")

        for u in p["unidades"]:
            id_u = g.nodo(
                f"unidad:{p['clave']}:{u['numero']}", "unidad",
                f"Unidad {u['numero']}. {u['nombre']}", {"nombre": u["nombre"]},
            )
            g.arista(id_pua, id_u, "tiene_unidad")
            if u["competencia"]:
                g.arista(id_u, _competencia(g, u["competencia"], "unidad"), "declara")
            for t in u["temas"]:
                id_t = g.nodo(f"tema:{p['clave']}:{_huella(t)}", "tema", t, {"texto": t})
                g.arista(id_u, id_t, "tiene_tema")

        for pr in p["practicas"]:
            id_pr = g.nodo(
                f"practica:{p['clave']}:{pr['numero']}", "practica",
                f"Práctica {pr['numero']}. {pr['nombre']}", {"unidad": pr["unidad"]},
            )
            g.arista(id_pua, id_pr, "tiene_practica")

    for ruta in cursos:
        curso = modelo.cargar(ruta)
        id_curso = g.nodo(
            f"curso:{curso.ciclo}:{curso.clave}", "curso",
            f"{curso.nombre} · {curso.ciclo}",
            {"modalidad": curso.modalidad, "ruta": generar.relativa(ruta)},
        )
        id_pua = f"pua:{curso.clave}"
        if id_pua not in g.nodos:  # el curso apunta a un PUA que no se ha ingerido
            g.nodo(id_pua, "pua", f"{curso.clave} (sin ingerir)", {"ausente": True})
        g.arista(id_curso, id_pua, "se_basa_en")

        prof = cfg.profesor(curso.profesor_id)
        g.arista(
            id_curso,
            g.nodo(f"profesor:{prof['id']}", "profesor", prof["nombre"]),
            "impartido_por",
        )
        g.arista(
            id_curso,
            g.nodo(f"plantilla:{curso.modalidad}", "plantilla", curso.modalidad),
            "usa_plantilla",
        )
        for cita in curso.citas:
            art = cfg.articulo(cita)
            g.arista(
                id_curso,
                g.nodo(f"articulo:{cita}", "articulo", f"{cita} — art. {art['articulo']}"),
                "cita",
            )
        for gr in curso.grupos:
            g.arista(
                id_curso,
                g.nodo(
                    f"grupo:{curso.ciclo}:{curso.clave}:{gr.numero}", "grupo",
                    f"Grupo {gr.numero}",
                    {"aula": gr.horario.aula, "dias_presencial": gr.horario.dias_presencial},
                ),
                "tiene_grupo",
            )

        try:
            cal = calendario.cargar(curso.ciclo)
            for n in range(1, cal.total_semanas + 1):
                g.nodo(f"semana:{curso.ciclo}:{n}", "semana", f"Semana {n}")
        except calendario.ErrorCalendario:
            pass  # sin calendario no hay nodos de semana; la auditoría lo reporta

        for u in curso.unidades:
            id_u = g.nodo(
                f"unidad:{curso.clave}:{u.numero}", "unidad",
                f"Unidad {u.numero}. {u.nombre}", {"nombre": u.nombre},
            )
            for t in u.temas:  # el curso puede declarar temas que el PUA no trae
                id_t = g.nodo(f"tema:{curso.clave}:{_huella(t)}", "tema", t, {"texto": t})
                g.arista(id_u, id_t, "tiene_tema")

        for m in curso.metas:
            id_m = g.nodo(
                f"meta:{curso.ciclo}:{curso.clave}:{m.id}", "meta",
                f"{m.etiqueta}. {m.enunciado}",
                {"clase": m.tipo, "rubro": m.rubro, "valor": m.valor, "semanas": m.semanas},
            )
            g.arista(id_curso, id_m, "tiene_meta")
            g.arista(id_m, f"unidad:{curso.clave}:{m.unidad}", "desarrolla")
            for t in m.cubre_temas:
                g.arista(id_m, f"tema:{curso.clave}:{_huella(t)}", "cubre")
            if m.practica_pua is not None:
                g.arista(id_m, f"practica:{curso.clave}:{m.practica_pua}", "realiza")
            for n in m.semanas:
                g.arista(id_m, f"semana:{curso.ciclo}:{n}", "ocurre_en")
            for i, e in enumerate(m.evidencias):
                g.arista(
                    id_m,
                    g.nodo(
                        f"evidencia:{curso.ciclo}:{curso.clave}:{m.id}:{i}", "evidencia",
                        e.nombre, {"clase": e.tipo, "recurso": e.recurso},
                    ),
                    "produce",
                )
            for i, c in enumerate(m.criterios_evaluacion):
                g.arista(
                    id_m,
                    g.nodo(
                        f"criterio:{curso.ciclo}:{curso.clave}:{m.id}:{i}", "criterio", c
                    ),
                    "se_evalua_con",
                )

    return g


# -- auditoría ---------------------------------------------------------------


def auditar(g: Grafo) -> dict[str, list[str]]:
    """Las preguntas que el grafo existe para contestar. Cada lista vacía es una buena noticia."""
    informe: dict[str, list[str]] = {}

    def nombre(id_: str) -> str:
        return g.nodos[id_].etiqueta if id_ in g.nodos else id_

    # 1. Temas del PUA que ninguna meta declara cubrir.
    sueltos = []
    for t in g.de_tipo("tema"):
        if not g.entrantes(t.id, "cubre"):
            unidad = next((a.origen for a in g.entrantes(t.id, "tiene_tema")), "")
            sueltos.append(f"{nombre(unidad)} → «{t.etiqueta}»")
    informe["Temas sin meta que los cubra"] = sorted(sueltos)

    # 2. Prácticas del PUA que ninguna meta realiza.
    informe["Prácticas sin meta"] = sorted(
        p.etiqueta for p in g.de_tipo("practica") if not g.entrantes(p.id, "realiza")
    )

    # 3. Unidades sin meta y semanas sin actividad.
    informe["Unidades sin meta"] = sorted(
        u.etiqueta for u in g.de_tipo("unidad") if not g.entrantes(u.id, "desarrolla")
    )
    informe["Semanas sin meta"] = sorted(
        s.etiqueta for s in g.de_tipo("semana") if not g.entrantes(s.id, "ocurre_en")
    )

    # 4. Anclas rotas: una meta que apunta a un tema o práctica inexistente. La validación
    #    lo bloquea antes de renderizar, así que aquí debería salir siempre vacío.
    rotas = [
        f"{nombre(a.origen)} --{a.tipo}--> {a.destino}"
        for a in g.aristas
        if a.destino not in g.nodos
    ]
    informe["Anclas rotas"] = sorted(rotas)

    # 5. Competencias compartidas entre materias — la segunda pregunta de REQ-31.
    compartidas = []
    for c in g.de_tipo("competencia"):
        # Quien declara es `pua:<clave>` o `unidad:<clave>:<romano>`: la clave va en medio.
        claves = sorted({a.origen.split(":")[1] for a in g.entrantes(c.id, "declara")})
        if len(claves) > 1:
            compartidas.append(f"{', '.join(claves)} → «{c.etiqueta}»")
    informe["Competencias compartidas entre materias"] = sorted(compartidas)

    # 6. PUAs ingeridos que todavía no tienen curso, y cursos cuyo PUA no está ingerido.
    informe["PUAs sin curso"] = sorted(
        p.etiqueta for p in g.de_tipo("pua")
        if not p.datos.get("ausente") and not g.entrantes(p.id, "se_basa_en")
    )
    informe["Cursos cuyo PUA no está ingerido"] = sorted(
        nombre(a.origen) for p in g.de_tipo("pua") if p.datos.get("ausente")
        for a in g.entrantes(p.id, "se_basa_en")
    )
    return informe


# -- salida ------------------------------------------------------------------


def texto_auditoria(g: Grafo, informe: dict[str, list[str]]) -> str:
    conteo = {t: len(g.de_tipo(t)) for t in TIPOS}
    lineas = [
        "# Auditoría del grafo",
        "",
        f"Generado: {datetime.now().isoformat(timespec='seconds')} · "
        f"{len(g.nodos)} nodos · {len(g.aristas)} aristas",
        "",
        "Lo escribe `src/grafo.py`. Cada sección vacía es una buena noticia; una entrada es",
        "un hueco del diseño que alguien tiene que decidir si cierra o acepta.",
        "",
        "## Conteo por tipo",
        "",
        "| Tipo | Nodos |",
        "|---|---|",
        *(f"| {t} | {n} |" for t, n in conteo.items() if n),
        "",
    ]
    for titulo, entradas in informe.items():
        lineas += [f"## {titulo}", ""]
        lineas += [f"- {e}" for e in entradas] if entradas else ["_Nada que reportar._"]
        lineas.append("")
    return "\n".join(lineas)


def escribir(g: Grafo, informe: dict[str, list[str]], destino: Path = DIR_GRAFO) -> list[Path]:
    destino.mkdir(parents=True, exist_ok=True)
    datos = g.a_dict()

    ruta_json = destino / "grafo.json"
    ruta_json.write_text(
        json.dumps(datos, ensure_ascii=False, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )
    ruta_html = destino / "index.html"
    ruta_html.write_text(
        PLANTILLA_HTML.replace("/*__DATOS__*/", json.dumps(datos, ensure_ascii=False)),
        encoding="utf-8",
    )
    ruta_md = destino / "AUDITORIA.md"
    ruta_md.write_text(texto_auditoria(g, informe), encoding="utf-8")
    return [ruta_json, ruta_html, ruta_md]


PLANTILLA_HTML = """<!doctype html>
<html lang="es">
<meta charset="utf-8">
<title>Grafo del dominio — DI UABC</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
  :root {
    --fondo: #fbfbfa; --texto: #22201d; --tenue: #6b665e; --linea: #e0dcd4;
    --panel: #ffffff;
  }
  @media (prefers-color-scheme: dark) {
    :root { --fondo:#171614; --texto:#eceae5; --tenue:#9a948a; --linea:#33302b; --panel:#1f1e1b; }
  }
  * { box-sizing: border-box; }
  body { margin:0; font:14px/1.5 system-ui, sans-serif; background:var(--fondo); color:var(--texto);
         display:grid; grid-template-columns: 280px 1fr; height:100vh; }
  aside { border-right:1px solid var(--linea); padding:16px; overflow-y:auto; background:var(--panel); }
  h1 { font-size:15px; margin:0 0 4px; letter-spacing:.02em; }
  .sub { color:var(--tenue); font-size:12px; margin-bottom:16px; }
  input[type=search] { width:100%; padding:6px 8px; border:1px solid var(--linea); border-radius:6px;
                       background:var(--fondo); color:var(--texto); margin-bottom:12px; }
  .tipo { display:flex; align-items:center; gap:8px; padding:3px 0; cursor:pointer; font-size:13px; }
  .punto { width:10px; height:10px; border-radius:50%; flex:none; }
  .tipo .n { margin-left:auto; color:var(--tenue); font-variant-numeric:tabular-nums; }
  .tipo.off { opacity:.35; }
  main { position:relative; overflow:hidden; }
  canvas { display:block; width:100%; height:100%; }
  #detalle { position:absolute; right:16px; top:16px; width:320px; max-height:calc(100% - 32px);
             overflow-y:auto; background:var(--panel); border:1px solid var(--linea);
             border-radius:8px; padding:14px; font-size:13px; display:none; }
  #detalle h2 { font-size:14px; margin:0 0 2px; }
  #detalle .t { color:var(--tenue); font-size:12px; text-transform:uppercase; letter-spacing:.06em; }
  #detalle ul { list-style:none; padding:0; margin:8px 0 0; }
  #detalle li { padding:3px 0; border-top:1px solid var(--linea); }
  #detalle a { color:inherit; text-decoration:none; cursor:pointer; }
  #detalle a:hover { text-decoration:underline; }
  .rel { color:var(--tenue); font-size:11px; }
</style>
<aside>
  <h1>Grafo del dominio</h1>
  <div class="sub" id="resumen"></div>
  <input type="search" id="buscar" placeholder="Buscar nodo…">
  <div id="tipos"></div>
</aside>
<main>
  <canvas id="lienzo"></canvas>
  <div id="detalle"></div>
</main>
<script>
const G = /*__DATOS__*/;
const COLOR = {
  pua:"#c2410c", unidad:"#b45309", tema:"#a16207", competencia:"#7c3aed", practica:"#0f766e",
  curso:"#1d4ed8", meta:"#0369a1", evidencia:"#0891b2", criterio:"#64748b", semana:"#15803d",
  articulo:"#9f1239", plantilla:"#4d7c0f", profesor:"#b91c1c", grupo:"#7e22ce",
};
const visible = {}; Object.keys(COLOR).forEach(t => visible[t] = t !== "criterio");
const nodos = G.nodos.map(n => ({...n, x: Math.random()*800-400, y: Math.random()*600-300, vx:0, vy:0}));
const porId = Object.fromEntries(nodos.map(n => [n.id, n]));
const aristas = G.aristas.filter(a => porId[a.origen] && porId[a.destino]);

document.getElementById("resumen").textContent = nodos.length + " nodos · " + aristas.length + " aristas";
const cajaTipos = document.getElementById("tipos");
for (const t of Object.keys(COLOR)) {
  const n = nodos.filter(x => x.tipo === t).length;
  if (!n) continue;
  const d = document.createElement("div");
  d.className = "tipo" + (visible[t] ? "" : " off");
  d.innerHTML = `<span class="punto" style="background:${COLOR[t]}"></span>${t}<span class="n">${n}</span>`;
  d.onclick = () => { visible[t] = !visible[t]; d.classList.toggle("off"); };
  cajaTipos.appendChild(d);
}

const lienzo = document.getElementById("lienzo"), ctx = lienzo.getContext("2d");
let ancho = 0, alto = 0, escala = 1, ox = 0, oy = 0, sel = null, filtro = "";
function medir() {
  const r = lienzo.getBoundingClientRect(), dpr = devicePixelRatio || 1;
  ancho = r.width; alto = r.height;
  lienzo.width = ancho * dpr; lienzo.height = alto * dpr; ctx.setTransform(dpr,0,0,dpr,0,0);
}
addEventListener("resize", medir); medir();

const activo = n => visible[n.tipo] && (!filtro || n.etiqueta.toLowerCase().includes(filtro));
function paso() {
  const vivos = nodos.filter(activo);
  for (const a of nodos) { a.fx = 0; a.fy = 0; }
  for (let i = 0; i < vivos.length; i++) for (let j = i+1; j < vivos.length; j++) {
    const a = vivos[i], b = vivos[j];
    let dx = a.x-b.x, dy = a.y-b.y, d2 = dx*dx + dy*dy || 0.01;
    const f = 900 / d2;
    dx *= f; dy *= f; a.fx += dx; a.fy += dy; b.fx -= dx; b.fy -= dy;
  }
  for (const e of aristas) {
    const a = porId[e.origen], b = porId[e.destino];
    if (!activo(a) || !activo(b)) continue;
    const dx = b.x-a.x, dy = b.y-a.y, d = Math.hypot(dx,dy) || 0.01, f = (d-70) * 0.006;
    a.fx += dx/d*f; a.fy += dy/d*f; b.fx -= dx/d*f; b.fy -= dy/d*f;
  }
  for (const n of vivos) {
    n.fx -= n.x * 0.002; n.fy -= n.y * 0.002;               // gravedad al centro
    n.vx = (n.vx + n.fx) * 0.82; n.vy = (n.vy + n.fy) * 0.82;
    n.x += n.vx; n.y += n.vy;
  }
}
function pintar() {
  ctx.clearRect(0,0,ancho,alto);
  ctx.save(); ctx.translate(ancho/2 + ox, alto/2 + oy); ctx.scale(escala, escala);
  ctx.lineWidth = 1;
  for (const e of aristas) {
    const a = porId[e.origen], b = porId[e.destino];
    if (!activo(a) || !activo(b)) continue;
    const tocado = sel && (e.origen === sel.id || e.destino === sel.id);
    ctx.strokeStyle = tocado ? COLOR[sel.tipo] : "rgba(128,124,116,.28)";
    ctx.beginPath(); ctx.moveTo(a.x,a.y); ctx.lineTo(b.x,b.y); ctx.stroke();
  }
  for (const n of nodos) {
    if (!activo(n)) continue;
    const r = n.tipo === "pua" || n.tipo === "curso" ? 8 : n.tipo === "unidad" ? 6 : 4;
    ctx.beginPath(); ctx.arc(n.x, n.y, r, 0, 7);
    ctx.fillStyle = COLOR[n.tipo]; ctx.fill();
    if (sel && sel.id === n.id) { ctx.strokeStyle = "#000"; ctx.lineWidth = 2; ctx.stroke(); ctx.lineWidth = 1; }
    if (escala > 0.75 && r > 4) {
      ctx.fillStyle = getComputedStyle(document.body).color;
      ctx.font = "11px system-ui"; ctx.fillText(n.etiqueta.slice(0,34), n.x + r + 3, n.y + 3);
    }
  }
  ctx.restore();
}
function bucle() { paso(); pintar(); requestAnimationFrame(bucle); }
bucle();

const aPantalla = ev => {
  const r = lienzo.getBoundingClientRect();
  return { x: (ev.clientX - r.left - ancho/2 - ox)/escala, y: (ev.clientY - r.top - alto/2 - oy)/escala };
};
let arrastrando = null, ultimo = null;
lienzo.onmousedown = ev => {
  const p = aPantalla(ev);
  arrastrando = nodos.filter(activo).find(n => Math.hypot(n.x-p.x, n.y-p.y) < 10) || null;
  ultimo = { x: ev.clientX, y: ev.clientY };
  if (arrastrando) mostrar(arrastrando);
};
lienzo.onmousemove = ev => {
  if (!ultimo) return;
  if (arrastrando) { const p = aPantalla(ev); arrastrando.x = p.x; arrastrando.y = p.y; arrastrando.vx = arrastrando.vy = 0; }
  else { ox += ev.clientX - ultimo.x; oy += ev.clientY - ultimo.y; ultimo = { x: ev.clientX, y: ev.clientY }; }
};
addEventListener("mouseup", () => { arrastrando = null; ultimo = null; });
lienzo.onwheel = ev => { ev.preventDefault(); escala = Math.min(3, Math.max(0.2, escala * (ev.deltaY < 0 ? 1.1 : 0.9))); };
document.getElementById("buscar").oninput = ev => { filtro = ev.target.value.toLowerCase(); };

function mostrar(n) {
  sel = n;
  const caja = document.getElementById("detalle");
  const rel = [
    ...aristas.filter(a => a.origen === n.id).map(a => ({ t: a.tipo, o: porId[a.destino], dir: "→" })),
    ...aristas.filter(a => a.destino === n.id).map(a => ({ t: a.tipo, o: porId[a.origen], dir: "←" })),
  ];
  caja.innerHTML = `<div class="t">${n.tipo}</div><h2>${n.etiqueta}</h2>` +
    (n.datos ? `<div class="rel">${Object.entries(n.datos).map(([k,v]) => k+": "+v).join(" · ")}</div>` : "") +
    `<ul>${rel.map((r,i) => `<li><span class="rel">${r.dir} ${r.t}</span><br><a data-i="${i}">${r.o.etiqueta}</a></li>`).join("")}</ul>`;
  caja.style.display = "block";
  caja.querySelectorAll("a").forEach((a,i) => a.onclick = () => mostrar(rel[i].o));
}
</script>
</html>
"""


# -- consola -----------------------------------------------------------------


def main(argv: list[str]) -> int:
    for flujo in (sys.stdout, sys.stderr):
        if hasattr(flujo, "reconfigure"):
            flujo.reconfigure(encoding="utf-8", errors="replace")

    puas, cursos = descubrir()
    print(generar.cabecera("grafo"))
    try:
        g = construir(puas, cursos)
    except (ErrorGrafo, modelo.ErrorModelo) as e:
        print(generar.PIE)
        print(f"\n{e}", file=sys.stderr)
        return 1
    print(generar.linea("✓", "leído", f"{len(puas)} PUA(s) · {len(cursos)} curso(s)"))
    print(generar.linea("✓", "grafo", f"{len(g.nodos)} nodos · {len(g.aristas)} aristas"))

    informe = auditar(g)
    huecos = sum(len(v) for k, v in informe.items() if k != "Anclas rotas")
    rotas = len(informe["Anclas rotas"])
    print(generar.linea("!" if rotas else "✓", "auditoría",
                        f"{huecos} hueco(s) · {rotas} ancla(s) rota(s)"))
    for ruta in escribir(g, informe):
        print(generar.linea("✓", ruta.name, generar.relativa(ruta.parent) + "/"))
    print(generar.PIE)

    for titulo, entradas in informe.items():
        if entradas:
            print(f"\n{titulo} ({len(entradas)}):")
            for e in entradas[:10]:
                print(f"  · {e}")
            if len(entradas) > 10:
                print(f"  … y {len(entradas) - 10} más")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
