---
phase: 09-valor-de-una-meta
reviewed: 2026-08-05T23:16:31Z
depth: standard
files_reviewed: 6
files_reviewed_list:
  - src/huella.py
  - src/modelo.py
  - src/validar.py
  - src/render_docx.py
  - pruebas/test_huella.py
  - pruebas/test_modelo.py
  - pruebas/test_render_docx.py
  - pruebas/test_validar.py
findings:
  critical: 0
  warning: 2
  info: 2
  total: 4
status: issues_found
---

# Fase 9: Reporte de revisión de código

**Revisado:** 2026-08-05T23:16:31Z
**Profundidad:** standard (con lectura cruzada de `src/generar.py` y ejecución de la suite de pruebas relevante)
**Archivos revisados:** 8 (4 de `src/`, 4 de `pruebas/`)
**Estado:** issues_found

## Resumen

Se revisaron los cinco puntos de la Fase 9: `src/huella.py` (nuevo), la extensión de `Rubro`/`Meta`/`Componente`
en `src/modelo.py`, la regla de metas duplicadas en `src/validar.py`, la concatenación de evidencias de
componentes en `src/render_docx.py`, y las pruebas nuevas/ampliadas. La suite `pruebas.test_modelo`,
`pruebas.test_validar` y `pruebas.test_huella` corre en verde (75 pruebas, 1.3 s); `test_render_docx.py` no se
ejecutó porque requiere Word por COM, pero se revisó por lectura.

El diseño general es sólido y coincide con las decisiones registradas en `09-CONTEXT.md` (D-01 a D-28): el
vocabulario cerrado de `unidad`/`total`/`tipo` falla en carga con `ErrorModelo`, los tres `curso.yaml`
existentes siguen cargando por construcción (probado explícitamente en `LosCursosExistentesNoCambian`), y
`_evidencias()` en `render_docx.py` preserva la salida byte-por-byte para cursos sin `componentes:` (probado en
`test_una_lista_de_componentes_vacia_no_cambia_ni_un_caracter`). No se encontró ningún hallazgo crítico: no hay
inyección, secretos, `eval`, ni escritura sobre plantillas o sobre `referencias/`.

Se confirmó, por diseño explícito de la Fase 9 (`09-CONTEXT.md`, sección "El código que se toca"), que R1 y R2
de `src/validar.py` **no** suman todavía el `valor` de los `componentes` de una meta contra el rubro al que se
imputan — eso es Fase 10 y no se reporta aquí como hallazgo.

Los dos hallazgos de advertencia están en `src/huella.py`, en el manejo de excepciones y restauración del
`MANIFIESTO.yaml` dentro de `_generar_control()`, que es justo el punto delicado señalado en el encargo de
revisión.

## Advertencias

### WR-01: `verificar()` no es de solo lectura si el `MANIFIESTO.yaml` no existía antes de correr

**Archivo:** `src/huella.py:143,151-152`

**Problema:** `_generar_control()` decide si restaura el manifiesto anterior con:

```python
previo = manifiesto.read_bytes() if manifiesto.exists() else None
...
finally:
    if restaurar_manifiesto and previo is not None:
        manifiesto.write_bytes(previo)
```

Si `manifiesto` **no existía** antes de la corrida (`previo is None`), la condición del `finally` nunca se
cumple, así que el `MANIFIESTO.yaml` que `generar.paquete()` acaba de escribir se queda en disco aunque
`restaurar_manifiesto=True`. Esto contradice D-28 ("cumple lo que D-23 pedía —que `verificar` sea de solo
lectura sobre el repo—") y el docstring de `verificar()` ("No escribe nada (D-28)"): en este caso concreto sí
escribe, y el archivo se queda.

Hoy el riesgo es bajo porque los cuatro `MANIFIESTO.yaml` de control están versionados y casi siempre existen,
pero es exactamente el tipo de corte que rompe en un clon fresco antes de la primera generación, o si alguien
borra el manifiesto a mano para depurar. No hay ninguna prueba que cubra este camino (`EnRegistroTemporal` en
`pruebas/test_huella.py` nunca ejerce `_generar_control`, que es lo único que toca archivos reales del repo).

**Corrección sugerida:**

```python
finally:
    if restaurar_manifiesto:
        if previo is not None:
            manifiesto.write_bytes(previo)
        else:
            manifiesto.unlink(missing_ok=True)
```

### WR-02: Una excepción de `forma_del_manifiesto()` no se envuelve en `ErrorHuella` y puede enmascarar el error original

**Archivo:** `src/huella.py:144-152`

**Problema:**

```python
try:
    paq = generar.paquete(ruta, pdf=False, grupos=list(grupos))
    forma = forma_del_manifiesto(paq.manifiesto)
except generar.ErrorGenerar as e:
    raise ErrorHuella(f"{rel}: no se pudo generar — {e}") from e
finally:
    if restaurar_manifiesto and previo is not None:
        manifiesto.write_bytes(previo)
```

El `except` solo atrapa `generar.ErrorGenerar`. Si `forma_del_manifiesto(paq.manifiesto)` falla por cualquier
otro motivo — el YAML recién escrito no parsea, un `OSError` de disco, una clave inesperada — la excepción no
se envuelve en `ErrorHuella` y se escapa cruda hasta `main()`, que solo captura `ErrorHuella` (línea 272). El
resultado es una traza de Python sin el mensaje amigable que el resto de la herramienta cuida (compárese con
los mensajes de `ErrorHuella` en `verificar()`, que dicen qué pasó y qué comando correr).

Además, como esa excepción ocurre dentro del `try`, Python primero ejecuta el `finally` (que si
`restaurar_manifiesto` es verdadero intenta `manifiesto.write_bytes(previo)`); si esa escritura también fallara
(permiso denegado, disco lleno), la excepción del `finally` **reemplaza** a la de `forma_del_manifiesto`, y el
motivo original de la falla se pierde por completo. Es un caso extremo, pero es precisamente el tipo de
enmascaramiento que este instrumento —pensado para dar diagnósticos claros al cerrar cada fase— no debería
tener.

**Corrección sugerida:** ampliar el `except` para envolver cualquier error de la generación o del cálculo de
la forma, preservando la causa:

```python
try:
    paq = generar.paquete(ruta, pdf=False, grupos=list(grupos))
    forma = forma_del_manifiesto(paq.manifiesto)
except generar.ErrorGenerar as e:
    raise ErrorHuella(f"{rel}: no se pudo generar — {e}") from e
except Exception as e:
    raise ErrorHuella(f"{rel}: no se pudo calcular la forma del manifiesto — {e}") from e
finally:
    ...
```

## Info

### IN-01: `forma_del_manifiesto()` no valida que el archivo exista, a diferencia del resto del proyecto

**Archivo:** `src/huella.py:103-118`

**Problema:** `modelo._cargar_yaml()` comprueba `ruta.exists()` y levanta `ErrorModelo` con un mensaje claro si
falta el archivo. `forma_del_manifiesto()` va directo a `Path(ruta).read_text(...)`, así que si alguna vez se
invoca con una ruta que no existe (hoy solo ocurre internamente, justo después de generar, así que el archivo
siempre está ahí) el error es un `FileNotFoundError` crudo en vez de un mensaje consistente con el resto de la
capa de trazabilidad.

**Corrección sugerida:** replicar el patrón de `_cargar_yaml` — comprobar existencia y levantar `ErrorHuella`
con un mensaje que diga qué faltó — si esta función llega a exponerse fuera de `_generar_control`.

### IN-02: `extraer_texto()` podría duplicar texto si algún `.docx` de control llegara a tener tablas anidadas

**Archivo:** `src/huella.py:80-91`

**Problema:** para cada `<w:tbl>` de primer nivel del cuerpo, el código hace
`for tr in hijo.iter(qn("w:tr"))`, que recorre **todos** los `<w:tr>` descendientes, incluidos los de una tabla
anidada dentro de una celda. Hoy no es un problema porque la Sección 2 de las plantillas CIAD es una tabla
plana de 7 columnas de rejilla (documentado en `AGENTS.md`), pero si una plantilla futura introdujera una tabla
anidada, el texto de esa tabla se contaría junto con las filas de la tabla exterior, en un orden potencialmente
distinto al visual, y `test_el_texto_respeta_el_orden_del_documento` no lo detectaría porque no ejercita ese
caso.

**Corrección sugerida:** ninguna acción necesaria ahora; si en una fase futura aparece una tabla anidada real,
filtrar con `hijo.findall(qn("w:tr"))` combinado con un recorrido explícito de subtablas, o documentar la
suposición de "sin tablas anidadas" junto al comentario que ya explica por qué se evita `row.cells[i].text`.

---

_Revisado: 2026-08-05T23:16:31Z_
_Revisor: Claude (gsd-code-reviewer)_
_Profundidad: standard_
