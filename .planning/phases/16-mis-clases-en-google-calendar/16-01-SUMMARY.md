---
phase: 16
plan: 01
subsystem: exportacion-ics
tags: [icalendar, horario, calendario, zoneinfo]
requires: [15-01, 15-02]
provides:
  - Eventos de clase concretos derivados exclusivamente de bloques y calendario oficial.
  - Serialización iCalendar UTF-8, CRLF, escape y plegado RFC 5545.
  - Doce pruebas del exportador, incluido el caso real de 2026-2.
affects: [horarios, calendario]
key-files:
  created: [src/exportar_ics.py, pruebas/test_exportar_ics.py]
key-decisions:
  - Un evento por bloque y fecha, no recurrencias con excepciones.
  - Horas locales America/Tijuana convertidas a UTC para no mantener VTIMEZONE manualmente.
  - Un curso sin bloques o ausente se omite; jamás se inventan horas.
requirements-completed: [REQ-53]
completed: 2026-08-06
---

# Fase 16, plan 01 — Núcleo del calendario iCalendar

`src/exportar_ics.py` toma los `Bloque` de los cursos que existen, descarta grupos no impartidos o
sin horas y recorre las semanas oficiales. Cada fecha suspendida se excluye antes de serializar un
`VEVENT`; por eso no hay que desplazar ni adivinar una clase.

Los eventos se escriben en UTC desde `America/Tijuana`, con UID estable, `DTSTAMP`, `DTSTART`,
`DTEND`, resumen y ubicación solo para bloques presenciales. El serializador usa CRLF, escapa texto
y pliega por octetos, sin añadir una dependencia iCalendar.

## Verificación

```text
python -X utf8 -m unittest pruebas.test_exportar_ics
Ran 12 tests in 0.564s
OK
```

El caso real fija 122 eventos: 90 presenciales y 32 virtuales. Excluye 962 por `imparte: false`,
531 por no declarar bloques con hora y el 932 ausente sin impedir los cursos existentes.
