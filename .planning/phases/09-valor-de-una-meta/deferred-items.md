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
