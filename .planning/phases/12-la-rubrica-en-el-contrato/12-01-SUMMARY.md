---
phase: 12
plan: 01
status: complete
completed: 2026-08-06
---

# Plan 12-01 — Resumen

## Resultado

- Se añadieron FilaRubrica, Rubrica, su carga opcional y Curso.rubrica.
- El modelo conserva concepto, puntos y descripción sin reescritura.
- Rechaza total no positivo, filas vacías, puntos negativos y destino ausente o ambiguo.
- AGENTS.md describe la nueva clave de primer nivel y su literalidad.

## Verificación

python -X utf8 -m unittest pruebas.test_modelo -v  -> 35 pruebas, OK
python -X utf8 -m unittest discover -s pruebas     -> 267 pruebas, OK

No se tocaron cursos, renderizador, grafo, plantillas ni fuentes.
