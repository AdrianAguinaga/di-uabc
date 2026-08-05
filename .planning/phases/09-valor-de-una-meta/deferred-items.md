# Fase 9 — Hallazgos fuera de alcance

## `test_no_deja_procesos_de_word_huerfanos` intermitente al correr la suite completa

- **Encontrado durante:** 09-03, verificación de `python -X utf8 -m unittest discover -s pruebas`.
- **Síntoma:** la prueba falla cuando se corre dentro de `discover -s pruebas` (detecta
  `WINWORD.EXE` en `tasklist`), pero pasa en verde al correrla sola
  (`python -X utf8 -m unittest pruebas.test_export_pdf.ConversionReal.test_no_deja_procesos_de_word_huerfanos`).
- **Causa probable:** ejecución en paralelo con el plan 09-02 en otro worktree de la misma
  máquina, que también dispara Word vía COM durante su propia corrida de pruebas. `tasklist`
  ve todos los procesos del sistema, no solo los del worktree actual.
- **No se toca aquí:** no tiene relación con `src/validar.py` ni `pruebas/test_validar.py`
  (los únicos archivos de 09-03). Fuera de alcance según la regla de límite del executor.
- **Siguiente paso sugerido:** re-verificar en solitario (sin ejecución paralela) al cerrar la
  fase, antes de dar la suite completa por buena.
- **Resuelto (5 de agosto de 2026, al cerrar la ola 2):** la causa probable era la correcta. Con
  los dos worktrees ya fusionados y sin ejecución concurrente, la suite completa da 212 pruebas en
  verde, esta incluida. No hay defecto que arreglar. Queda como nota de operación: la suite dispara
  Word por COM y `tasklist` ve toda la máquina, así que **esta prueba no tolera dos corridas
  simultáneas** —el aislamiento por worktree no la cubre, porque Word no es un recurso del
  directorio de trabajo—.
