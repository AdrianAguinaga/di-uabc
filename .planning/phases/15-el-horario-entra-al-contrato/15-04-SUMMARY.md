---
phase: 15
plan: 04
subsystem: validacion
tags: [r6, horario, suspensiones, fechas]
requires: [15-01, 15-02]
provides:
  - Validación R6 de formato, rango y solapamiento de bloques
  - Aviso R6 para semanas sin día presencial disponible
  - Aviso para escapes Sesion.dia fuera del horario presencial del grupo
affects: [generar, calendario, informe]
key-files:
  created: []
  modified: [src/validar.py, pruebas/test_validar.py]
key-decisions:
  - R6 se amplía; no nace una novena regla.
  - Una semana sin bloque disponible es aviso, no error: reprogramarla corresponde al docente.
  - El aviso consulta Calendario.dia_de_clase sin depender de Sesion.fecha.
requirements-completed: [REQ-50]
completed: 2026-08-06
---

# Fase 15, plan 04 — Validación del horario

R6 ahora bloquea horarios con horas inválidas, fin no posterior al inicio o bloques que se
solapan. Las semanas donde una suspensión deja al grupo sin ningún bloque presencial se avisan
con semana y grupo, sin impedir la generación del borrador.

El cálculo del aviso usa el mismo `Calendario.dia_de_clase` que la resolución de fechas y no lee
`Sesion.fecha`, porque el pipeline valida antes de renderizar.

## Verificación

```text
Pruebas nuevas de R6: 10 — OK
test_validar completo: 92 — OK
Suite completa: 320 — OK
Big Data y Patrones: VÁLIDO, sin avisos de bloque presencial
Huellas: Todo intacto. 4 documentos comparados.
Plantillas: íntegras
```

Los `curso.yaml` reales continúan sin bloques hasta la ola de datos y medición posterior.
