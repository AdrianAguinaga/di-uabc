---
phase: 15
plan: 02
subsystem: calendario
tags: [horario, suspensiones, fechas, contrato]
requires: [15-01]
provides:
  - Calendario.dia_de_clase acotado a la semana
  - fecha_de opcionalmente filtrada por días presenciales
  - resolver_fechas que respeta bloques, escapes y entregas
affects: [validar, renderizado, agenda]
key-files:
  created: []
  modified: [src/calendario.py, src/modelo.py, pruebas/test_calendario.py, pruebas/test_modelo.py]
key-decisions:
  - El recorrido de una suspensión con horario no sale de la semana declarada.
  - La ausencia de un día presencial conserva la fecha suspendida para que R6 la reporte.
  - Sin bloques, la resolución de fechas conserva exactamente la conducta anterior.
requirements-completed: [REQ-50, REQ-51]
completed: 2026-08-06
---

# Fase 15, plan 02 — Fechas según el horario real

`Calendario.dia_de_clase` concentra la definición de «siguiente día con clase». Solo se activa
cuando el grupo declara bloques; así el 531 y los cursos futuros sin horario explícito mantienen
su resolución anterior.

## Comportamiento fijado

- El grupo 961 pasa de los lunes suspendidos de las semanas 13 y 15 a martes 3 y 17 de noviembre.
- Los grupos 971 y 972 que no tienen otro bloque presencial se quedan en el día suspendido: no
  saltan a otra semana.
- Un bloque virtual no afecta las fechas presenciales ni las entregas del sábado.
- `Sesion.dia` conserva su escape declarado sin ser sustituida por el filtro del horario.

## Verificación

```text
python -X utf8 -m unittest pruebas.test_modelo
Ran 49 tests — OK

python -X utf8 -m unittest discover -s pruebas
Ran 302 tests — OK

python -X utf8 src/huella.py verificar
Todo intacto. 4 documentos comparados.
```

Las plantillas siguen coincidiendo con su registro. Ningún `curso.yaml` ha sido modificado aún.
