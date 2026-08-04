---
name: di-nuevo
description: Orquestador interactivo para generar un Diseño Instruccional completo. Pregunta ciclo, materia, profesor, modalidad, grupos y esquema de evaluación, escribe curso.yaml, valida y renderiza a .docx y .pdf. Úsala cuando el usuario pida un DI nuevo, o diga "generar diseño instruccional" o "/di-nuevo".
---

# Nuevo Diseño Instruccional

Seis preguntas, un documento firmable. Esta skill es **un menú**: el usuario debe saber en todo
momento en qué paso está, qué ya contestó y qué falta.

## El menú se imprime, no se describe

Al arrancar, imprime el rótulo **tal cual**, sin envolverlo en bloque de código:

```
██████╗ ██╗    ███╗   ██╗██╗   ██╗███████╗██╗   ██╗ ██████╗
██╔══██╗██║    ████╗  ██║██║   ██║██╔════╝██║   ██║██╔═══██╗
██║  ██║██║    ██╔██╗ ██║██║   ██║█████╗  ██║   ██║██║   ██║
██║  ██║██║    ██║╚██╗██║██║   ██║██╔══╝  ╚██╗ ██╔╝██║   ██║
██████╔╝██║    ██║ ╚████║╚██████╔╝███████╗ ╚████╔╝ ╚██████╔╝
╚═════╝ ╚═╝    ╚═╝  ╚═══╝ ╚═════╝ ╚══════╝  ╚═══╝   ╚═════╝
   Generador de Diseño Instruccional · UABC · CIAD
```

Y enseguida el panel de progreso, en el estado inicial:

```
┌─ DI · NUEVO ───────────────────────────────── paso 1 de 6 ─┐
│  ▶ 1  Ciclo                                                │
│    2  Materia (PUA)                                        │
│    3  Profesor                                             │
│    4  Modalidad                                            │
│    5  Grupos y horario                                     │
│    6  Esquema de evaluación                                │
└────────────────────────────────────────────────────────────┘
```

**Antes de cada pregunta reimprime el panel completo**, con el paso contestado marcado `✓` y su
respuesta a la derecha. Así:

```
┌─ DI · NUEVO ───────────────────────────────── paso 4 de 6 ─┐
│  ✓ 1  Ciclo                    2026-2 · 16 semanas         │
│  ✓ 2  Materia (PUA)            39056 Big Data              │
│  ✓ 3  Profesor                 Adrian Rodriguez A.         │
│  ▶ 4  Modalidad                                            │
│    5  Grupos y horario                                     │
│    6  Esquema de evaluación                                │
└────────────────────────────────────────────────────────────┘
```

Glifos: `✓` contestado · `▶` en curso · vacío pendiente. La columna de respuesta empieza en la
misma posición siempre; recorta a 20 caracteres con `…` si no cabe.

El panel orienta; la pregunta se hace con **AskUserQuestion** para que el usuario elija con las
flechas. Panel primero, pregunta después, una sola pregunta por vez.

## Los seis pasos

| # | Pregunta | Opciones salen de | Predeterminado |
|---|---|---|---|
| 1 | Ciclo escolar | `calendarios/*.yaml` | El ciclo vigente (`2026-2`) |
| 2 | Materia | `puas/INDICE.md` | — |
| 3 | Profesor | `config/profesores.yaml` | El que tiene `predeterminado: true` |
| 4 | Modalidad | escolarizada · semipresencial · a distancia | La que declara §I del PUA |
| 5 | Grupos y horario | los teclea el usuario | — |
| 6 | Esquema de evaluación | `config/esquemas-evaluacion.yaml` | `predeterminado:` del archivo |

Detalles que cambian el resultado:

1. **Ciclo.** Si no existe `calendarios/<ciclo>.yaml`, **para aquí**: pide el PDF oficial del
   calendario. No estimes fechas (regla invariable 1). Al confirmarlo, muestra semanas totales,
   primer y último día de clases, y los días de suspensión.
2. **Materia.** Si la clave no está en `puas/INDICE.md`, ofrece ingerirla en el momento con
   `/di-pua` y continúa cuando termine. Los avisos de la ingesta se arrastran a `avisos:`.
3. **Profesor.** Si el correo está en `null`, pídelo o déjalo vacío con aviso; no lo inventes.
4. **Modalidad.** Preselecciona la del PUA pero **confírmala**: decide la plantilla, si la columna
   *Entrega* se divide en Presencial/Virtual y si la Sección 3 lleva pasos `Primero…Quinto`.
5. **Grupos y horario.** Uno o varios. Por cada grupo: días de sesión, día y hora de entrega, aula,
   jefe de grupo y plataforma. **El horario vive en el grupo**: si dos grupos difieren en días,
   difieren todas sus fechas. Un documento por grupo.
6. **Esquema.** Muestra los rubros con sus porcentajes y el umbral de exención. Si el usuario
   captura uno a mano, verifica que sume 100 y traiga ≥ 2 parciales antes de aceptarlo (Arts. 67
   y 68) — no esperes a la validación.

Si el usuario vuelve sobre un paso ya contestado, reimprime el panel con ese paso en `▶` y **borra
los posteriores que dependan de él**: cambiar el ciclo invalida todas las fechas; cambiar la
modalidad, la plantilla; cambiar la materia, todo lo demás.

## Antes de generar: el resumen

Contestados los seis, redacta las metas (es juicio pedagógico, no mecánico: ver
`conocimiento/estilo/estilo-redaccion-ciad.md`) y enseña el resumen para que el usuario confirme:

```
┌─ DI · NUEVO ── resumen ────────────────────────────────────┐
│  Ciclo      2026-2 · 16 semanas · 10 ago – 28 nov          │
│  Materia    39056 Big Data                                 │
│  Profesor   Adrian Rodriguez Aguiñaga                      │
│  Modalidad  Semipresencial                                 │
│  Grupos     961 · 962                                      │
│  Esquema    Estándar 2026 · exención 80                    │
│  Metas      14 metas · 5 unidades · 100 %                  │
│  Salida     4 archivos en cursos/2026-2/39056-…/           │
└────────────────────────────────────────────────────────────┘
```

Solo con el «sí» del usuario escribes `curso.yaml`.

## Generar

Escrito el `curso.yaml`, **un solo comando** encadena todo: valida, renderiza un documento por
grupo, exporta a PDF y firma el manifiesto.

```bash
python src/generar.py cursos/<ciclo>/<clave>-<slug>/curso.yaml     # --sin-pdf si no hay Word
```

El panel de avance **lo imprime el comando**. Relaya su salida tal cual; no la redibujes:

```
┌─ DI · NUEVO ── generando ──────────────────────────────────┐
│  ✓ validación     0 errores · 2 avisos · 5 recordatorios   │
│  ✓ grupo 961      DI-2026-2-39056-961.docx → .pdf          │
│  ✓ grupo 962      DI-2026-2-39056-962.docx → .pdf          │
│  ✓ MANIFIESTO     cursos/2026-2/39056-big-data/            │
└────────────────────────────────────────────────────────────┘
```

Cómo leerlo: `✓` hecho · `!` hecho con reserva (sin Word no hay PDF, pero el `.docx` ya es
entregable) · `✗` se detuvo ahí. Si la validación falla, el comando **no escribe ningún archivo**
y termina en 1: se corrige el `curso.yaml` y se vuelve a correr. Los avisos se listan completos al
cerrar el panel — son decisiones del docente, no fallas, y hay que enseñárselos.

`MANIFIESTO.yaml` queda junto al `curso.yaml`: PUA y su hash, calendario, versión de plantilla,
profesor, grupos, esquema, commit, y el sha256 de cada archivo producido. Si el PDF del PUA ya no
hashea como cuando se escribió el curso, el panel lo avisa y el manifiesto lo deja asentado.

## Reglas

- **El resultado es un borrador.** Dilo al entregarlo: el profesor tiene que revisarlo antes de
  usarlo con sus alumnos (regla invariable 9).
- **No inventes nada para no interrumpir.** Falta un calendario, un correo o un dato del PUA:
  se pregunta o se deja vacío con aviso.
- Si `python src/plantillas.py verificar` falla en cualquier momento, **para** y averigua qué
  escribió sobre la plantilla antes de seguir generando documentos.
- Lo demás —contrato de `curso.yaml`, marcadores de fecha, estilo tipográfico— está en `AGENTS.md`.
