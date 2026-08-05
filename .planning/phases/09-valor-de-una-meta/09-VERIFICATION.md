---
phase: 09-valor-de-una-meta
verified: 2026-08-05T23:14:01Z
status: passed
score: 5/5 must-haves verified (criterios del ROADMAP) — 24/24 must-haves de los 6 planes verificados
overrides_applied: 0
---

# Fase 9: El valor de una meta deja de ser un porcentaje — Reporte de verificación

**Meta de la fase:** que `curso.yaml` pueda decir en qué unidad vale cada meta, a qué rubros
aporta y cómo se llama, sin que nada de eso cambie el significado de un curso que no lo declare.
**Verificado:** 2026-08-05T23:14:01Z
**Estado:** passed
**Re-verificación:** No — verificación inicial

## Logro de la meta

### Verdades observables (criterios de éxito del ROADMAP §Fase 9)

| # | Verdad | Estado | Evidencia |
|---|--------|--------|-----------|
| 1 | Un `curso.yaml` que declare «Actividades 30 %» en puntos con total 150, junto a «Exámenes 50 %» en porcentaje, carga sin `ErrorModelo` | ✓ VERIFICADO | `test_puntos_y_porcentaje_conviven_en_el_mismo_curso` pasa; `src/modelo.py` `Rubro.unidad`/`total`/`__post_init__` implementados exactamente como especifica el plan 09-02 |
| 2 | Una meta con un componente adicional sigue siendo una sola meta con una sola semana | ✓ VERIFICADO | `test_una_meta_con_componente_sigue_siendo_una_meta_con_una_semana` pasa; `Meta.componentes` no altera `semanas` ni `len(curso.metas)` |
| 3 | Metas con id `1.0`, `2.0`, `6.0` cargan y conservan el orden declarado; renombrar el encuadre `0`→`1.0` de Big Data deja el documento igual salvo esa cadena | ✓ VERIFICADO (con desvío razonado) | `test_ids_terminados_en_punto_cero_cargan`, `test_se_conserva_el_orden_declarado` pasan. El renombrado real de `cursos/2026-2/39056-big-data/curso.yaml` (`id: "1.0"` confirmado) fue medido con `huella.py`: el sha del texto con las **tres** apariciones del id revertidas (`"Meta 1.0."` en Sección 2 y 3, y `"La meta 1.0 equivale al 0%…"`) coincide exactamente con la línea base previa — ver "Atención a los desvíos" abajo |
| 4 | Existe un comando que regenera 39056 y 39062 y compara la huella de texto contra la registrada, y corre en verde | ✓ VERIFICADO | `python -X utf8 src/huella.py verificar` → `Todo intacto. 4 documentos comparados.`, código 0; `git status --porcelain cursos/` vacío tras verificar (D-23/D-28 respetados) |
| 5 | `python -X utf8 -m unittest discover -s pruebas` pasa: las anteriores intactas más las nuevas | ✓ VERIFICADO | 216 pruebas, 0 fallos, 27.2s (re-ejecutado en esta verificación) |

**Puntuación:** 5/5 verdades del ROADMAP verificadas.

### Artefactos requeridos (must_haves de los 6 planes)

| Artefacto | Esperado | Estado | Detalle |
|-----------|----------|--------|---------|
| `src/huella.py` | CLI verificar/registrar, `extraer_texto`, `forma_del_manifiesto`, sha256 por 3 campos | ✓ VERIFICADO | Las 7 funciones y `class ErrorHuella` presentes; `VOLATILES_MANIFIESTO = ("generado", "commit")`, `CAMPOS = ("texto_docx", "informe", "manifiesto")`; sin `git checkout`, sin `import subprocess`; reusa `generar.paquete(` sin reimplementar validar→renderizar |
| `pruebas/huellas.yaml` | Registro versionado, 4 documentos × 3 hashes | ✓ VERIFICADO | Las 4 claves `2026-2:39056:961/962` y `2026-2:39062:971/972` presentes, cada una con `texto_docx`, `informe`, `manifiesto`, `registrado` |
| `pruebas/test_huella.py` | Pruebas de extracción y forma, sin invocar `generar.paquete()` | ✓ VERIFICADO | 13 pruebas en 3 clases; `grep "generar.paquete\|import generar"` no encuentra nada (el docstring se reescribió en 09-01 para evitar el falso positivo) |
| `src/modelo.py` | `Rubro.unidad/total/a_porcentaje`, `Componente`, `Meta.componentes`, `TIPOS_COMPONENTE`, `UNIDADES_RUBRO` | ✓ VERIFICADO | Todo presente línea por línea según lo especificado en 09-02; sin `sorted(`/`.sort(`/`id.split(` aplicados a ids de meta; `desde_dict` no se tocó |
| `pruebas/test_modelo.py` | 4 clases, ≥18 pruebas | ✓ VERIFICADO | `RubroEnPuntos`, `ComponentesDeMeta`, `IdentificadoresLibres`, `LosCursosExistentesNoCambian` — 18 pruebas, todas en verde |
| `src/validar.py` | `Counter` de ids de meta duplicados en `regla_2` | ✓ VERIFICADO | `Counter(m.id for m in self.c.metas)` y `"Metas duplicadas: "` presentes; diff de 3 líneas añadidas, 0 eliminadas |
| `pruebas/test_validar.py` | Prueba hermana en `Regla2Metas` | ✓ VERIFICADO | `test_dos_metas_con_el_mismo_id_son_error_de_regla` y `test_el_curso_con_ids_repetidos_carga_igual` presentes y en verde; `test_detecta_el_defecto_del_ejemplo_961` intacto |
| `src/render_docx.py` | `_evidencias(meta)` concatenando evidencias de componentes | ✓ VERIFICADO | `def _evidencias` y `", ".join(_evidencias(meta))` presentes; los 2 usos de `f"{meta.valor:g}%"` (columna Valor y Sección 3) intactos, confirmando que la Fase 13 no se adelantó |
| `pruebas/test_render_docx.py` | `class EvidenciaDeComponente`, regresión con/sin componentes | ✓ VERIFICADO | 4 pruebas, todas en verde |
| `cursos/2026-2/39056-big-data/curso.yaml` | Encuadre declarado como `id: "1.0"` | ✓ VERIFICADO | `grep 'id: "1.0"'` → 1 ocurrencia; `git diff --numstat` histórico reportó `1 1` (una línea) |

### Verificación de enlaces clave (wiring)

| De | A | Vía | Estado | Detalle |
|----|---|-----|--------|---------|
| `src/huella.py` | `src/generar.py` | `generar.paquete(ruta, pdf=False, grupos=[...])` | ✓ WIRED | Confirmado en `_generar_control` |
| `src/huella.py` | `pruebas/huellas.yaml` | `cargar()`/`guardar()` con `yaml.safe_dump` | ✓ WIRED | `yaml.safe_dump(cuerpo, allow_unicode=True, sort_keys=False, default_flow_style=False)` presente |
| `src/huella.py:forma_del_manifiesto` | `cursos/**/MANIFIESTO.yaml` | sha256 sin claves volátiles | ✓ WIRED | `VOLATILES_MANIFIESTO`/`VOLATILES_ARCHIVO` aplicados antes de `sha_texto(yaml.safe_dump(...))` |
| `src/modelo.py:_construir_meta` | `src/modelo.py:_construir_componente` | `d.pop("componentes", [])` | ✓ WIRED | Confirmado en `_construir_meta` |
| `src/modelo.py:Rubro.a_porcentaje` | `Rubro.porcentaje`/`Rubro.total` | `valor / base * porcentaje` | ✓ WIRED | Implementado como `def a_porcentaje` sobre `self.base` |
| `src/validar.py:regla_2` | `collections.Counter` | `Counter(m.id for m in self.c.metas)` | ✓ WIRED | Confirmado, `Counter` ya estaba importado |
| `src/render_docx.py:_filas_de_meta` | `meta.componentes` | `_evidencias(meta)` en la celda de evidencias | ✓ WIRED | `", ".join(_evidencias(meta)) if ultima else ""` presente |
| `cursos/2026-2/39056-big-data/curso.yaml` | `grafo/grafo.json` | regenerado con `python src/grafo.py` | ✓ WIRED | Nodos `meta:2026-2:39056:1.0` presentes; 377 nodos / 669 aristas idéntico a antes del renombrado |

### Rastro de datos (Nivel 4) — no aplica de forma extensa

Esta fase es principalmente de contrato (modelo + instrumento de medición), no de UI dinámica. El
único punto con "datos que fluyen" relevante es la celda de evidencias del `.docx`, verificado
directamente con las pruebas de `EvidenciaDeComponente` (Nivel 3 = Nivel 4 aquí: el dato entra por
el `curso.yaml`, pasa por `_evidencias()` y llega al documento real, confirmado con
`assertIn(f"{meta.evidencias[-1].nombre}, Examen I resuelto", salida)`).

### Comprobaciones de comportamiento (spot-checks)

| Comportamiento | Comando | Resultado | Estado |
|---|---|---|---|
| `huella.py verificar` regenera y compara 4 documentos | `python -X utf8 src/huella.py verificar` | `Todo intacto. 4 documentos comparados.`, código 0 | ✓ PASS |
| `git status` limpio tras `verificar` | `git status --porcelain cursos/` | vacío | ✓ PASS |
| Plantillas no tocadas | `python -X utf8 src/plantillas.py verificar` | Las tres plantillas coinciden con su registro | ✓ PASS |
| `curso.yaml` de 39056 sigue validando | `python -X utf8 src/validar.py cursos/2026-2/39056-big-data/curso.yaml` | `VÁLIDO` | ✓ PASS |
| Suite completa | `python -X utf8 -m unittest discover -s pruebas` | 216 pruebas, 0 fallos, 27.2s | ✓ PASS |
| Grafo mantiene su forma tras el renombrado | conteo de nodos/aristas | 377 nodos / 669 aristas — idéntico | ✓ PASS |
| `grafo/AUDITORIA.md` sin huecos nuevos | lectura directa | 0 anclas rotas; único hueco conocido: Contabilidad Financiera · 2026-2 | ✓ PASS |

### Cobertura de requisitos

| Requisito | Plan(es) que lo declaran | Descripción | Estado | Evidencia |
|-----------|---------------------------|-------------|--------|-----------|
| REQ-38 | 09-02 | Rubro puede expresar valores en puntos con total declarado, conviviendo con rubros en % | ✓ SATISFECHO | `Rubro.unidad`/`total`/`a_porcentaje` implementados y probados (18 pruebas de `RubroEnPuntos`) |
| REQ-39 | 09-02, 09-04 | Meta puede aportar a más de un rubro vía `componentes`, sin dejar de ser una meta | ✓ SATISFECHO | `Componente`, `Meta.componentes`, y su evidencia llega al `.docx` (`EvidenciaDeComponente`, 4 pruebas) |
| REQ-42 | 09-02, 09-03, 09-05 | Identificador de meta libre; ninguna función asume `.0`/`.1`; colisión de ids es error de R2 | ✓ SATISFECHO | `IdentificadoresLibres` (4 pruebas), `Regla2Metas` (2 pruebas nuevas), renombrado real `0`→`1.0` demostrado en el repositorio con huella medida |
| REQ-48 | 09-01, 09-05, 09-06 | Ningún rasgo de v2.0 se activa si `curso.yaml` no lo declara; instrumento de medición | ✓ SATISFECHO | `src/huella.py` construido y en verde; línea base tomada antes del contrato (D-15 paso 1); el único cambio de huella del milestone (el renombrado) fue medido y aceptado deliberadamente; confirmación humana en 09-06 (Word abre sin reparar, diff revisado y aprobado) |

No hay requisitos huérfanos: los 4 IDs que el brief de verificación señala (REQ-38, REQ-39, REQ-42,
REQ-48) están todos declarados en al menos un plan, y ningún plan declara un ID fuera de esa lista.

### Antipatrones encontrados

Ninguno bloqueante. Se revisaron `src/huella.py`, `src/modelo.py`, `src/validar.py` y
`src/render_docx.py` (los cuatro archivos de producción tocados por la fase) buscando
`TODO`/`FIXME`/`placeholder`/retornos vacíos sin flujo de datos real: ningún hallazgo.

### Atención a los dos desvíos señalados en 09-05-SUMMARY.md

Ambos se revisaron contra el repositorio real y el juicio del verificador coincide con el del
ejecutor:

1. **El criterio 3 se demostró revirtiendo tres apariciones del id, no una.** El plan 09-05
   proponía comprobar el alcance del renombrado sustituyendo solo `"Meta 1.0." → "Meta 0."` en el
   texto extraído. El documento real de Big Data contiene el identificador en tres cadenas
   derivadas: la fila de la Sección 2 (`"Meta 1.0."`), el encabezado de la Sección 3
   (`"Meta 1.0."`) y la línea de valor (`"La meta 1.0 equivale al 0% de tu calificación final."`,
   impresa por `render_docx.py:420`, `f"La {meta.etiqueta.lower()} equivale al {meta.valor:g}% "`
   con `meta.etiqueta = f"Meta {self.id}"` → contiene el id en minúsculas sin punto). Revirtiendo
   las tres, el sha coincide exacto con la línea base. Esto no es una laguna del criterio 3 del
   ROADMAP (que pide "el documento igual salvo esa cadena", en singular pero refiriéndose al
   *identificador*, no a un único lugar donde aparece) — es la comprobación *escrita en el plan*
   la que estaba incompleta, y el ejecutor la corrigió con evidencia verificable (el hash coincide
   exacto). No se encontró ninguna otra diferencia en el documento. **No se trata como hueco.**

2. **`grep -c "Meta 0\." grafo/grafo.json` devuelve 1, no 0 (verificado directamente en esta
   sesión).** Se inspeccionó el nodo con esa cadena: `meta:2026-2:39062:0`, el encuadre del curso
   de control 39062, que la fase explícitamente no debía tocar (D-16, "no se toca Patrones"). No
   queda ningún nodo `meta:2026-2:39056:0`. El criterio de aceptación literal del plan 09-05
   (`grep -c "Meta 0\." grafo/grafo.json` = 0) fue mal escrito por el planificador: el conteo global
   no distingue entre el curso que se renombra y el curso de control que debe permanecer intacto.
   El criterio correcto — "ningún nodo de 39056 conserva el id viejo" — sí se cumple. **No se trata
   como hueco.**

Ambos desvíos están razonados con evidencia verificable en el repositorio (no solo en la narrativa
del SUMMARY), y ninguno compromete REQ-42, REQ-48 ni el criterio 3 del ROADMAP.

### Cabos sueltos conocidos (no son huecos de la fase)

Presentados al usuario en el checkpoint de 09-06 y aprobados por él el 5 de agosto de 2026:

- El recurso `M0_Foro de presentación` conserva el prefijo `M0_` con su meta ya renombrada a `1.0`
  (deliberado, D-14, para no contaminar la medición del criterio 3). Pendiente de acordar con el
  docente si debe renombrarse.
- `huella registrar` genera con `pdf=False`, así que los `MANIFIESTO.yaml` de los cursos de control
  dejaron de listar sus `.pdf` (solo listan los `.docx` de esa corrida). Los PDFs siguen en disco;
  es coherente con el diseño "solo los archivos de esta corrida" del manifiesto.

### Verificación humana requerida

Ninguna. El checkpoint bloqueante del plan 09-06 (`type: checkpoint:human-verify`) ya se ejecutó y
el usuario respondió "aprobado" el 5 de agosto de 2026, confirmando que el `.docx` renombrado abre
en Word sin pedir reparación, que dice «Meta 1.0.» en las Secciones 2 y 3, y que el diff completo
de la fase no contiene nada fuera de lo prometido.

### Resumen de huecos

Ninguno. Los cinco criterios de éxito del ROADMAP §Fase 9 están verificados sobre el repositorio
real (no solo sobre lo que los SUMMARYs afirman): el modelo carga el contrato nuevo en sus tres
puntos, el instrumento de no contaminación existe y corre en verde, el renombrado del encuadre de
Big Data quedó medido y aceptado con el diff como constancia, y la suite completa (216 pruebas)
pasa. Los dos desvíos documentados por el ejecutor en 09-05 son correcciones bien razonadas a
criterios de aceptación mal escritos en el plan, no defectos de la implementación. Los dos cabos
sueltos son decisiones pendientes del docente, ya presentadas y registradas, no bloqueos técnicos.

---

*Verificado: 2026-08-05T23:14:01Z*
*Verificador: Claude (gsd-verifier)*
