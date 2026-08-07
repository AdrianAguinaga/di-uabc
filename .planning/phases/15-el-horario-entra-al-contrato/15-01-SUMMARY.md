---
phase: 15
plan: 01
subsystem: modelo
tags: [horario, bloques, contrato, huella]
requires: []
provides:
  - Bloque con día, horas y ambiente declarado
  - Horario.bloques que deriva dias_presencial
  - Grupo.imparte con valor predeterminado true
affects: [calendario, generar, validar, grafo]
tech-stack:
  added: []
  patterns: [dataclass, TDD, contrato-aditivo]
key-files:
  created: []
  modified: [src/modelo.py, pruebas/test_modelo.py]
key-decisions:
  - Los bloques normalizan dicts y objetos en Horario.__post_init__.
  - Solo los bloques presenciales derivan dias_presencial.
  - imparte es verdadero por omisión para conservar los cursos existentes.
requirements-completed: [REQ-50, REQ-51]
duration: n/a
completed: 2026-08-06
---

# Fase 15, plan 01 — Contrato de horario

Se incorporó la pieza mínima del horario semanal sin modificar los `curso.yaml` reales: `Bloque`,
`Horario.bloques` y `Grupo.imparte`.

## Línea base de huella

Antes de cualquier cambio, `python -X utf8 src/huella.py verificar` produjo literalmente:

```text
  ✓ 39056 grupo 961      huella intacta
  ✓ 39056 grupo 962      huella intacta
  ✓ 39062 grupo 971      huella intacta
  ✓ 39062 grupo 972      huella intacta

Todo intacto. 4 documentos comparados.
```

`git status --short cursos/` no produjo ninguna línea.

## Implementación

- `Bloque` exige un día de lunes a sábado y uno de los ambientes `presencial` o `virtual`.
- `Horario` acepta bloques como diccionarios del YAML u objetos `Bloque`; cuando los hay, deriva
  días presenciales únicos y ordenados. Declarar además días explícitos es un error del modelo.
- `Grupo.imparte` es aditivo: mantiene `True` por omisión y acepta `False` desde el YAML.

## Pruebas

Se escribió primero la prueba roja: falló únicamente por la inexistencia de `bloques`, `Bloque` e
`imparte`. Tras implementar el modelo:

```text
python -X utf8 -m unittest pruebas.test_modelo
Ran 46 tests — OK

python -X utf8 -m unittest discover -s pruebas
Ran 293 tests — OK
```

También validaron Big Data, las cuatro huellas y el registro de las tres plantillas. Los cursos
aún no declaran bloques; por eso la huella continúa intacta 4/4, como exige la secuencia de la
fase.
