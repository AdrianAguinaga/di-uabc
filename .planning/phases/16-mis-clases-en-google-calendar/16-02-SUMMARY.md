---
phase: 16
plan: 02
subsystem: cli-y-documentacion
tags: [ics, cli, google-calendar, docs]
requires: [16-01]
provides:
  - Comando de exportación con salida por omisión e indicación de omisiones.
  - Archivo real `Clases-2026-2.ics` generado en una ruta ignorada.
  - Contrato, README e ignore alineados con la agenda de clases.
affects: [horarios, AGENTS.md, README.md]
key-files:
  modified: [.gitignore, AGENTS.md, README.md]
key-decisions:
  - `horarios/salida/` es regenerable y no se versiona.
  - La importación a Google Calendar sigue siendo una acción manual y no sincroniza actualizaciones.
requirements-completed: [REQ-53]
completed: 2026-08-06
---

# Fase 16, plan 02 — Comando y entrega local

El comando ya produce el archivo real:

```text
python -X utf8 src/exportar_ics.py 2026-2
Calendario de clases 2026-2: 122 eventos.
Archivo: horarios/salida/Clases-2026-2.ics
· Omitido: 39056 · grupo 962 no se imparte este ciclo.
· Omitido: 38985 · grupo 531 no declara bloques con horas.
```

`horarios/salida/` queda ignorado porque la agenda se vuelve a derivar de los bloques. El README
incluye la importación manual a Google Calendar y AGENTS.md fija que la agenda nunca lee metas,
sesiones, entregas ni evaluaciones. El 932 no aparece porque no tiene `curso.yaml`; no bloquea la
agenda de las materias declaradas.
