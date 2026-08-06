---
phase: 12
plan: 03
status: complete
completed: 2026-08-06
---

# Plan 12-03 — Resumen

## Resultado

- MANIFIESTO.yaml recibe una copia condicional de rubrica, sus filas y su destino.
- La forma y el orden de evaluación de cursos sin rubrica permanecen intactos.
- No se tocó render_docx.py, grafo, cursos ni documentos fuente.

## Verificación de cierre

python -X utf8 -m unittest pruebas.test_generar -v -> 20 pruebas, OK
python -X utf8 -m unittest discover -s pruebas     -> 275 pruebas, OK
python -X utf8 src/huella.py verificar             -> 4 documentos intactos
python src/plantillas.py verificar                 -> 3 plantillas verificadas
git diff --check                                   -> sin errores

## Pendientes explícitos

- Fase 13 renderizará la tabla de rubrica; este plan no generó ningún documento nuevo.
- Fase 14 declarará las filas literales de Contabilidad Financiera en 38985.
