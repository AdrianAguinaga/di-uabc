# Fase 12: La rúbrica en el contrato — Investigación

**Investigado:** 2026-08-06
**Dominio:** contrato YAML, dataclasses, validación R2 y trazabilidad del manifiesto.
**Confianza:** alta; todo se midió contra el árbol vivo tras el cierre de la Fase 11.

## Requisitos de fase

| ID | Necesidad | Decisión que la cubre |
|---|---|---|
| REQ-43 | Declarar concepto, puntos, descripción, total y asociación a meta o trabajo final | D-01 a D-03 |
| REQ-47 | Filas suman el total declarado | D-05 y D-06 |
| REQ-26 | El renderizador no inventa criterios | D-08; no se toca el renderizador |
| REQ-48 | Sin rúbrica no cambia salida, huella, manifiesto ni grafo | D-09 y D-10 |

## Arquitectura medida

| Responsabilidad | Archivo y punto de extensión | Decisión |
|---|---|---|
| Contrato y carga | `src/modelo.py`, dataclasses y `desde_dict()` | Añadir `FilaRubrica`, `Rubrica`, `Curso.rubrica` y constructor privado. |
| Sumas y referencias | `src/validar.py`, `Validador.regla_2()` | Validar filas, total y asociación dentro de R2. |
| Texto que podrá imprimirse | `src/validar.py`, `_texto_visible()` | Incluir concepto y descripción en el guardia `ESTILO`. |
| Trazabilidad | `src/generar.py`, `manifiesto()` | Emitir bloque `rubrica` sólo cuando se declara. |
| Renderizado | `src/render_docx.py` | No tocar: Fase 13. |
| Grafo | `src/grafo.py` | No tocar ni regenerar: no consume el bloque de evaluación del curso. |

El `Curso` actual construye sus rubros desde `evaluacion:` y el resto de las claves del contrato
desde el diccionario raíz. `rubrica:` debe leerse antes de que se descarten los campos desconocidos
del diccionario y conservar la forma opcional `None`. El patrón existente de construcción anidada
es `Rubro(**r)`; una función `_construir_rubrica(valor)` evita que `desde_dict()` decida cómo crear
filas.

`regla_2()` ya es la casa del control de aportes por rubro. A diferencia de R1, no tiene la guarda
textual que prohíbe atributos de rubros; puede comparar `fila.puntos` y `rubrica.total` directamente.
Crear R9 contradice el contrato documentado de ocho reglas y cambiaría el informe conceptual de los
cursos sin rúbrica.

## Fuentes primarias consultadas

- `AGENTS.md`: contrato de `curso.yaml`, ocho reglas, reglas de no invención y trazabilidad.
- `.planning/ROADMAP.md`: Fase 12 y sucesoras 13–14.
- `.planning/REQUIREMENTS.md`: REQ-26, REQ-43, REQ-47 y REQ-48.
- `src/modelo.py`, `src/validar.py`, `src/generar.py`, `src/grafo.py`, `src/huella.py`.
- `pruebas/test_modelo.py`, `pruebas/test_validar.py`, `pruebas/test_generar.py` y
  `pruebas/huellas.yaml`.
- `conocimiento/ejemplos/531-contabilidad-financiera-2026-1.md` y consulta de sólo lectura de
  `ejemplos/38985-531-2026-1-Rubio Arriaga Zurisaddai.docx`.
- `grafo/AUDITORIA.md`: 377 nodos y 669 aristas; no se regeneró.

## Línea base reproducida

```text
python -X utf8 -m unittest discover -s pruebas   -> 262 pruebas, OK
python -X utf8 src/huella.py verificar            -> 4 documentos intactos
```

39056 y 39062 no tienen R1 ni un bloque de rúbrica; 38985 sigue deliberadamente fuera de cambios
hasta la Fase 14. La Fase 12 no debe ejecutar `huella.py registrar`, generar documentos ni tocar
`cursos/`.

## Riesgos y defensas

| Riesgo | Defensa |
|---|---|
| Tratar la descripción como texto de sistema | Campo obligatorio y copia literal; probar igualdad de cadena en modelo/manifiesto. |
| Hacer que 100 puntos signifiquen 100 % | Comparación exclusivamente puntos contra `rubrica.total`; prueba con rúbrica asociada a meta de peso menor. |
| Admitir asociación ambigua | `ErrorModelo` si hay cero o dos referencias. |
| Cambiar manifiestos de control | Inclusión condicional y verificación de huellas. |
| Colar el renderizado | `render_docx.py` queda fuera de los planes y se comprueba el diff. |

## Recomendación

Tres olas: (1) contrato y pruebas de carga, (2) R2/ESTILO y pruebas de validación, (3)
manifiesto, no contaminación, documentación y cierre. No hay dependencias externas ni necesidad de
Word/PDF para esta fase.
