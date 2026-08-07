---
phase: 15
plan: 05
subsystem: datos-y-medicion
tags: [horario, cursos, huella, grafo]
requires: [15-01, 15-02, 15-03, 15-04]
provides:
  - Los cuatro grupos de control declaran el horario 2026-2 que les corresponde.
  - Una medición de fechas y campos de huella antes de aceptar el cambio.
  - Grafo regenerado desde los cursos con bloques.
affects: [cursos, grafo, huellas]
key-files:
  created: [15-MEDICION-HUELLA.md]
  modified:
    - cursos/2026-2/39056-big-data/curso.yaml
    - cursos/2026-2/39062-patrones-de-comportamiento/curso.yaml
    - grafo/grafo.json
    - grafo/index.html
    - grafo/AUDITORIA.md
key-decisions:
  - 39056·962 permanece declarado con su horario heredado y se marca imparte: false: no aparece en la carga 2026-2.
  - Las semanas sin otro bloque presencial se avisan; no se inventa una reprogramación.
requirements-completed: [REQ-50, REQ-51, REQ-52]
completed: 2026-08-06
---

# Fase 15, plan 05 — Horarios reales y medición previa

Los grupos 39056·961, 39062·971 y 39062·972 ahora declaran los bloques de
`horarios/2026-2.md`; 39056·962 conserva su horario heredado y declara `imparte: false` porque no
se ofrece este ciclo. El grafo fue regenerado: 368 nodos, 654 aristas, cero anclas rotas y un PUA
ausente ya conocido (Contabilidad Financiera).

Antes de re-registrar la huella se escribió `15-MEDICION-HUELLA.md`. Comprobó las 16 fechas
presenciales de cada grupo en los documentos recién generados. Predijo nueve cambios de campos:
texto y manifiesto de 961; solo manifiesto de 962 por su acoplamiento por curso; y texto, informe
y manifiesto de 971 y 972. La salida posterior de `huella verificar` coincidió con esa medición.

Las tres semanas sin día presencial disponible quedan explícitas: 971 semanas 13 y 15, y 972
semana 6. El generador conserva la fecha suspendida y R6 avisa para que el docente la reprograme,
en vez de inventar otra fecha.

## Verificación

```text
Suite completa: 320 pruebas — OK
Grafo: 368 nodos, 654 aristas; 0 anclas rotas
Medición: 16/16 fechas comprobadas para 961, 962, 971 y 972
Huella antes del registro: 9 cambios de campos, exactamente los previstos
```
