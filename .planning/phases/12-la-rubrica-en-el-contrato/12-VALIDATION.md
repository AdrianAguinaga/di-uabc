---
phase: 12
slug: la-rubrica-en-el-contrato
status: complete
nyquist_compliant: true
wave_0_complete: true
created: 2026-08-06
---

# Fase 12 — Estrategia de validación

## Infraestructura

| Propiedad | Valor |
|---|---|
| Framework | `unittest` de la biblioteca estándar |
| Comando rápido | `python -X utf8 -m unittest pruebas.test_modelo pruebas.test_validar -v` |
| Comando completo | `python -X utf8 -m unittest discover -s pruebas` |
| Línea base | 262 pruebas, en verde |

Tras cada tarea que cambie código corre la suite completa; al cierre corre además huella y
custodia de plantillas. No se regeneran huellas.

## Mapa de comportamientos

| # | Comportamiento | Req | Prueba prevista | Hallazgo esperado |
|---|---|---|---|---|
| B1 | Rúbrica válida de 100 puntos carga y conserva texto literal | REQ-43, REQ-26 | `ContratoDeRubrica` en `test_modelo.py` | ninguno |
| B2 | Falta `meta` y `rubro` | REQ-43 | modelo | `ErrorModelo` |
| B3 | Declara ambos destinos | REQ-43 | modelo | `ErrorModelo` |
| B4 | Total no positivo, filas vacías o puntos negativos | REQ-43 | modelo | `ErrorModelo` |
| B5 | 98 contra total 100 | REQ-47 | `Regla2Rubrica` en `test_validar.py` | error R2 |
| B6 | 102 contra total 100 | REQ-47 | idem | error R2 |
| B7 | Total exacto, incluida fracción decimal | REQ-47 | idem | ningún error R2 de rúbrica |
| B8 | Meta o rubro declarado no existe | REQ-43 | idem | error R2 |
| B9 | Concepto/descripción pasan por guardia ESTILO | REQ-26 | idem | aviso ESTILO si contienen taquigrafía interna |
| B10 | Manifiesto incluye sólo rúbrica declarada y la preserva | REQ-26, REQ-48 | `test_generar.py` | estructura exacta |
| B11 | Cursos de control no declaran ni activan el rasgo | REQ-48 | `NoContaminacion` | silencio / `None` |
| B12 | Salidas de control conservan huella | REQ-48 | `python -X utf8 src/huella.py verificar` | éxito |

## Verificaciones de cierre

```powershell
python -X utf8 -m unittest discover -s pruebas
python -X utf8 src/huella.py verificar
python src/plantillas.py verificar
git diff --check
```

No debe haber cambios en `render_docx.py`, `grafo/`, `referencias/`, `ejemplos/` ni `cursos/`.

## Cierre ejecutado

- B1–B4: ContratoDeRubrica en test_modelo.py.
- B5–B8: Regla2Rubrica en test_validar.py.
- B9: GuardiaDeEstilo en test_validar.py.
- B10: ManifiestoDeRubrica en test_generar.py.
- B11: NoContaminacion en test_validar.py.
- B12: huella.py verificar, cuatro documentos intactos.

Resultado: 275 pruebas en verde, custodia de las tres plantillas en verde y diff sin errores.
