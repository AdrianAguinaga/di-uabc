---
phase: 9
slug: valor-de-una-meta
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-05
---

# Fase 9 — Estrategia de validación

> Contrato de validación de la fase: con qué instrumento se muestrea cada criterio durante la
> ejecución. Derivado de `09-RESEARCH.md` §Validation Architecture.

---

## Infraestructura de pruebas

| Propiedad | Valor |
|---|---|
| **Framework** | `unittest` (stdlib) |
| **Archivo de config** | ninguno — convención de directorio `pruebas/`, sin `pytest.ini` ni `setup.cfg` |
| **Comando rápido** | `python -X utf8 -m unittest pruebas.test_modelo -v` |
| **Comando completo** | `python -X utf8 -m unittest discover -s pruebas` |
| **Tiempo estimado** | ~13 s (179 pruebas, medido en la investigación) |

---

## Frecuencia de muestreo

- **Tras cada commit de tarea:** `python -X utf8 -m unittest discover -s pruebas`
  (la suite completa ya son 13 s — no hace falta un comando rápido separado).
- **Tras cada ola:** suite completa en verde.
- **Antes de cerrar la fase:** suite completa + `python src/huella.py verificar` en verde
  + `python src/plantillas.py verificar` en verde.
- **Latencia máxima de retroalimentación:** 15 s.

---

## Mapa de verificación por requisito

| Req / Criterio | Comportamiento | Tipo | Comando automatizado | ¿Archivo existe? | Estado |
|---|---|---|---|---|---|
| REQ-38 / criterio 1 | Rubro `unidad: puntos` + `total: 150` junto a un rubro en porcentaje carga sin `ErrorModelo` | unitario | `python -X utf8 -m unittest pruebas.test_modelo -v` | ❌ Ola 0 — crear `pruebas/test_modelo.py` | ⬜ pendiente |
| REQ-38 (D-03) | `unidad:` fuera del vocabulario cerrado → `ErrorModelo` al cargar | unitario | idem | ❌ Ola 0 | ⬜ pendiente |
| REQ-38 (D-05) | `unidad: puntos` sin `total` → `ErrorModelo`; el total no se infiere de la suma de metas | unitario | idem | ❌ Ola 0 | ⬜ pendiente |
| REQ-38 (D-04) | La conversión puntos→porcentaje vive en un solo sitio del modelo y da el valor correcto | unitario | idem | ❌ Ola 0 | ⬜ pendiente |
| REQ-39 / criterio 2 | Meta con `componentes:` sigue siendo **una** meta con **una** semana: `len(curso.metas)` y `m.semanas` idénticos a la misma meta sin componente | unitario | idem | ❌ Ola 0 | ⬜ pendiente |
| REQ-39 (D-08/D-26) | `tipo` de componente fuera de `TIPOS_COMPONENTE`, o ausente, → `ErrorModelo` | unitario | idem | ❌ Ola 0 | ⬜ pendiente |
| REQ-39 (D-07) | El `valor` del componente se lee en la unidad del rubro al que se imputa, distinto al de su meta | unitario | idem | ❌ Ola 0 | ⬜ pendiente |
| REQ-39 (D-11) | La evidencia del componente se concatena en la columna de evidencias de la Sección 2; un curso **sin** `componentes:` produce exactamente el mismo texto que hoy | unitario | `python -X utf8 -m unittest pruebas.test_render_docx -v` | ✅ ampliar existente | ⬜ pendiente |
| REQ-42 / criterio 3 | Metas con id `1.0`, `2.0`, `6.0` cargan y conservan el orden declarado en el YAML | unitario | `python -X utf8 -m unittest pruebas.test_modelo -v` | ❌ Ola 0 | ⬜ pendiente |
| REQ-42 (D-12/D-13) | Ningún módulo de `src/` ordena las metas ni deduce semántica del id: un curso con ids fuera de orden numérico preserva el orden del YAML de extremo a extremo | unitario | idem | ❌ Ola 0 | ⬜ pendiente |
| REQ-42 (D-17) | Dos metas con el mismo id → error de **R2**, no `ErrorModelo` (el curso carga y se puede inspeccionar) | unitario | `python -X utf8 -m unittest pruebas.test_validar -v` | ✅ ampliar existente | ⬜ pendiente |
| REQ-42 (regresión) | `test_detecta_el_defecto_del_ejemplo_961` sigue pasando **sin tocarse** | unitario | `python -X utf8 -m unittest pruebas.test_validar -v` | ✅ ya existe | ⬜ pendiente |
| Criterio 4 (D-18/D-19) | `huella.extraer_texto()` es determinista: dos lecturas del mismo `.docx` dan el mismo sha256, y celdas con `vMerge` no duplican texto | unitario | `python -X utf8 -m unittest pruebas.test_huella -v` (contra un `.docx` sintético en memoria, **sin** `generar.paquete`) | ❌ Ola 0 | ⬜ pendiente |
| Criterio 4 (REQ-48) | `huella verificar` regenera los 4 documentos de control y compara contra `pruebas/huellas.yaml`; corre en verde | integración / manual | `python src/huella.py verificar` — **fuera de `pruebas/`** por D-18 | N/A — manual por decisión | ⬜ pendiente |
| Criterio 4 (D-23) | Tras `huella verificar`, `git status` está limpio: los `MANIFIESTO.yaml` de control quedan restaurados | manual | `python src/huella.py verificar && git status --porcelain` | N/A — manual | ⬜ pendiente |
| D-15 paso 6 | Tras el rename, la única diferencia del texto del `.docx` de 39056 es `"Meta 0." → "Meta 1.0."` | manual | comparar el texto extraído antes/después: `texto_a.replace("Meta 0.", "Meta 1.0.") == texto_b`, con `git diff` como constancia | N/A — manual, requiere generar dos veces | ⬜ pendiente |
| Criterio 5 | Las 179 pruebas anteriores pasan intactas, más las nuevas | integración | `python -X utf8 -m unittest discover -s pruebas` | ✅ ya existe (179/179 en verde) | ⬜ pendiente |
| Invariante del proyecto | Ninguna plantilla de `referencias/` fue modificada | integración | `python src/plantillas.py verificar` | ✅ ya existe | ⬜ pendiente |

---

## Requisitos de Ola 0

- [ ] `pruebas/test_modelo.py` — archivo nuevo. Cubre REQ-38 (rubro en puntos, sus dos variantes de
      `ErrorModelo`, la conversión de D-04), REQ-39 (componentes, vocabulario cerrado, no
      contaminación de `len(metas)`/`semanas`, unidad cruzada de D-07) y REQ-42 (ids libres, orden
      preservado). Hoy no existe: las pruebas de carga viven implícitamente en `test_validar.py`.
- [ ] `pruebas/test_huella.py` — archivo nuevo, **acotado**: solo `extraer_texto()` contra un
      `.docx` sintético armado en memoria. Nunca invoca `generar.paquete()` — D-18 prohíbe colgar la
      generación completa del ciclo de pruebas unitarias. Replica el patrón `EnDirectorioTemporal`
      de `test_plantillas.py` si necesita tocar disco.
- [ ] Ampliación de `pruebas/test_validar.py` — una prueba para D-17 (dos metas con el mismo id →
      error de R2). No se toca `test_detecta_el_defecto_del_ejemplo_961`.
- [ ] Ampliación de `pruebas/test_render_docx.py` — regresión de D-11: la evidencia del componente
      se concatena, y su ausencia no cambia un carácter.

---

## Verificaciones solo manuales

| Comportamiento | Requisito | Por qué es manual | Instrucciones |
|---|---|---|---|
| `huella verificar` en verde contra los 4 documentos de control | REQ-48 / criterio 4 | D-18 lo aparta del ciclo de pruebas a propósito: genera dos cursos completos y depende de las plantillas de `referencias/`, que las pruebas unitarias no tocan | `python src/huella.py verificar` → debe listar los 4 documentos intactos y salir en 0. Después, `git status --porcelain` debe salir vacío (D-23) |
| La única diferencia del rename es `"Meta 0." → "Meta 1.0."` | REQ-42 / criterio 3 | Requiere generar el `.docx` de 39056 antes y después del rename; automatizarlo duplicaría la generación completa dentro de la suite | Paso 6 de D-15: `huella verificar` debe señalar 39056 y **solo** 39056; `git diff` sobre `curso.yaml` y `grafo/` no debe mostrar nada más que esa cadena |
| El grafo sigue al `curso.yaml` tras el rename | D-24 | `grafo.py` reescribe `grafo.json`, `index.html` y `AUDITORIA.md` juntos; la revisión es de contenido, no de esquema | Paso 5 de D-15: `python src/grafo.py`, luego `git diff grafo/` — solo debe cambiar la etiqueta de esa meta, no la estructura de nodos ni aristas |
| El `.docx` de 39056 abre en Word sin pedir reparar | REQ-48 | Requiere Word | Abrir el archivo generado tras el rename |

---

## Firma de validación

- [ ] Toda tarea tiene verificación `<automated>` o depende de Ola 0
- [ ] Continuidad de muestreo: no hay 3 tareas seguidas sin verificación automatizada
- [ ] Ola 0 cubre todas las referencias marcadas ❌
- [ ] Ningún comando en modo watch
- [ ] Latencia de retroalimentación < 15 s
- [ ] `nyquist_compliant: true` en el frontmatter

**Aprobación:** pendiente
