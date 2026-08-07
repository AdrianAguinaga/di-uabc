---
phase: 16
plan: 03
subsystem: verificacion
tags: [ics, pruebas, huella, plantillas]
requires: [16-01, 16-02]
provides:
  - Verificación local completa del archivo real 2026-2.
  - Registro explícito de la única comprobación humana pendiente.
affects: [roadmap, requisitos]
key-files:
  created: [16-VERIFICATION.md]
key-decisions:
  - No se importan eventos a una cuenta externa sin autorización explícita del usuario.
requirements-completed: []
requirements-pending: [REQ-53]
completed: 2026-08-06
---

# Fase 16, plan 03 — Verificación local y entrega para importación

La salida real para Adrian se creó en `horarios/salida/Clases-2026-2-ara.ics`. Incluye 122 clases:
90 presenciales con `LOCATION:Laboratorio de cómputo` y 32 virtuales sin ubicación. Se excluyen las
seis ocurrencias que coinciden con suspensión; 962 se omite por no impartirse y el curso de Zuri no
se mezcla en el archivo de Adrian.

## Verificación

```text
python -X utf8 -m unittest discover -s pruebas
Ran 332 tests in 26.001s
OK

python src/plantillas.py verificar
Las plantillas coinciden con su registro.

python -X utf8 src/huella.py verificar
Todo intacto. 4 documentos comparados.

python -X utf8 src/exportar_ics.py 2026-2 ara
Calendario de clases 2026-2 · Adrian Rodriguez Aguiñaga (ara): 122 eventos.
```

La importación en Google Calendar no se automatizó: crea eventos en una cuenta externa y requiere
autorización explícita. El archivo queda listo para esa comprobación humana.
