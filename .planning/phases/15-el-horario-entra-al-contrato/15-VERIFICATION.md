---
phase: 15-el-horario-entra-al-contrato
verified: 2026-08-06
status: passed
score: 6/6 criterios de éxito del roadmap verificados
requirements: [REQ-50, REQ-51, REQ-52]
---

# Fase 15: El horario entra al contrato — Reporte de verificación

**Meta:** que los grupos declaren sus bloques de clase, que el documento resuelva las fechas con
ese horario y que el cambio de los cuatro documentos de control quede medido y aceptado, no
oculto.

## Criterios de éxito del roadmap

| # | Criterio | Estado | Evidencia |
|---|---|---|---|
| 1 | Horas y ambiente de bloques, sin romper `dias_presencial` heredado | ✓ | `Bloque`, `Horario` y `Grupo.imparte` están en `src/modelo.py`; `HorarioConBloques` y `LosCursosDeControlNoCambian` cubren bloques y el 531 heredado. |
| 2 | Un bloque virtual no altera las fechas de clase | ✓ | `BloqueVirtualNoCambiaLasFechas` compara copias independientes con y sin bloque virtual; la suite pasa. |
| 3 | R6 rechaza hora inválida, intervalo invertido y solapamiento | ✓ | `Regla6HorarioMalDeclarado` cubre los tres casos y el martes doble real de 961 que no se solapa. La antigua discrepancia con `dias_presencial` es imposible: esa lista se deriva de los bloques. |
| 4 | Los cuatro grupos expresan el horario real y la huella se mide antes de aceptar | ✓ | `15-MEDICION-HUELLA.md` comprobó 16/16 fechas por grupo; `012c091` aisló el re-registro deliberado. |
| 5 | El grupo declarado que no se imparte queda definido | ✓ | 39056·962 declara `imparte: false`; `PaqueteDeBigData` y `ElGrupoQueNoSeImparteNoSeGenera` cubren la exclusión por defecto y las dos inclusiones explícitas. |
| 6 | Regresión y plantillas en verde | ✓ | `python -X utf8 -m unittest discover -s pruebas` terminó con 320 pruebas (283 iniciales + 37); `python src/plantillas.py verificar` confirmó las tres plantillas. |

## Comprobaciones reproducidas al cierre

```text
python -X utf8 -m unittest discover -s pruebas
Ran 320 tests in 25.921s
OK

python src/plantillas.py verificar
Las plantillas coinciden con su registro.

python -X utf8 src/huella.py verificar
Todo intacto. 4 documentos comparados.

python -X utf8 src/validar.py cursos/2026-2/39062-patrones-de-comportamiento/curso.yaml
VÁLIDO
```

La última validación muestra tres avisos R6, no errores: semanas 13 y 15 del grupo 971 y semana 6
del 972. En esos casos la suspensión deja sin otro bloque presencial dentro de la semana; el sistema
no inventa una fecha y le pide al docente reprogramarla si corresponde.

## Trazabilidad de la huella

La medición precedió al registro. Predijo texto y manifiesto para 961; solo manifiesto compartido
para 962; y texto, informe y manifiesto para 971 y 972. `huella verificar` confirmó la nueva línea
base de los cuatro documentos. El commit `012c091` contiene únicamente
`pruebas/huellas.yaml` y los dos manifiestos de control, y dice explícitamente que el cambio de
días es deliberado.

No hay huecos que bloqueen la fase. La Fase 16 puede construir el `.ics` sobre los bloques ya
declarados.
