---
phase: 16
plan: 04
subsystem: identidad-de-calendario
tags: [ics, profesor, aislamiento]
requires: [16-01, 16-02]
provides:
  - Una agenda exclusivamente de un profesor identificado.
  - Nombre de archivo, UID y metadatos de calendario trazables al profesor.
  - Falla segura para profesores sin bloques activos.
affects: [src/exportar_ics.py, AGENTS.md, README.md]
requirements-completed: [REQ-53]
completed: 2026-08-06
---

# Fase 16, plan 04 — La agenda tiene propietario

El comando recibe de forma obligatoria el id de profesores.yaml. Para Adrian, ara, genera
horarios/salida/Clases-2026-2-ara.ics. El exportador filtra los cursos antes de construir eventos y
escribe el nombre y el id en el archivo, X-WR-CALNAME, X-WR-CALDESC y los UID. Por tanto, una agenda
de Adrian no puede incluir clases de Zuri.

Hoy zra no tiene bloques con hora para 2026-2. Su comando responde con un error explícito y no crea
un archivo vacío. En cuanto declare grupos y bloques, se ejecuta el mismo comando con zra; no se
modifica el código ni el calendario de Adrian.

## Verificación

La prueba especializada del exportador pasó: 14 pruebas en 0.739 s. Cubre la agenda de Adrian, los
metadatos de propiedad y el rechazo de una agenda vacía para Zuri.
