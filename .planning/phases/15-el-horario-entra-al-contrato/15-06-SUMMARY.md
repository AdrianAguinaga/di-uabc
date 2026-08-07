---
phase: 15
plan: 06
subsystem: huella
tags: [huella, manifiesto, aprobacion]
requires: [15-05]
provides:
  - Línea base de huella aceptada después de medir el cambio de horarios.
  - Commit aislado que documenta que el cambio de fechas es deliberado.
affects: [pruebas/huellas.yaml, manifiestos-de-control]
key-files:
  modified:
    - pruebas/huellas.yaml
    - cursos/2026-2/39056-big-data/MANIFIESTO.yaml
    - cursos/2026-2/39062-patrones-de-comportamiento/MANIFIESTO.yaml
key-decisions:
  - El registro se ejecutó únicamente tras la aprobación explícita del usuario y con la medición disponible.
  - Los manifiestos de control quedaron registrados con --sin-pdf; cualquier PDF existente se conserva como artefacto previo y no forma parte de esta nueva línea base.
requirements-completed: [REQ-52]
completed: 2026-08-06
---

# Fase 15, plan 06 — Huella deliberadamente re-registrada

Tras aprobar la medición, `python -X utf8 src/huella.py registrar` aceptó la nueva línea base de
los cuatro documentos de control. La diferencia de 39056·962 permanece limitada al manifiesto:
su `.docx` y su informe no cambiaron.

El resultado quedó en el commit aislado `012c091`:

```text
chore(15): re-registrar la huella de control — el cambio de días es deliberado
```

Ese commit contiene exclusivamente `pruebas/huellas.yaml` y los dos `MANIFIESTO.yaml` de los cursos
de control. Se registraron sin exportar PDF; el registro valida las representaciones que genera la
huella, no declara actualizados los PDF que ya estuvieran en disco.

## Verificación

```text
✓ 39056 grupo 961      huella intacta
✓ 39056 grupo 962      huella intacta
✓ 39062 grupo 971      huella intacta
✓ 39062 grupo 972      huella intacta

Todo intacto. 4 documentos comparados.
```
