---
phase: 12
plan: 02
status: complete
completed: 2026-08-06
---

# Plan 12-02 — Resumen

## Resultado

- R2 valida sumas de filas de rúbrica y referencias a meta o rubro.
- La suma se compara en puntos propios y no se confunde con el porcentaje del curso.
- ESTILO analiza concepto y descripción sin modificarlos.
- Los cursos de control siguen sin declarar ni cargar el rasgo.
- AGENTS.md registra la ampliación de R2 sin crear una novena regla.

## Verificación

python -X utf8 -m unittest pruebas.test_validar -v -> 80 pruebas, OK
python -X utf8 -m unittest discover -s pruebas     -> 273 pruebas, OK
