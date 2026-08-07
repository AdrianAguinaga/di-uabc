---
phase: 15
plan: 03
subsystem: trazabilidad
tags: [manifiesto, grafo, generacion, horario]
requires: [15-01]
provides:
  - bloques e imparte condicionales en MANIFIESTO.yaml
  - filtro de grupos no impartidos y bandera de inclusión explícita
  - bloques legibles en nodos de grupo del grafo
affects: [huella, cli, grafo]
key-files:
  created: []
  modified: [src/generar.py, src/grafo.py, pruebas/test_generar.py, pruebas/test_grafo.py]
key-decisions:
  - Los nuevos campos del manifiesto son condicionales para preservar la forma de cursos sin horario.
  - Pedir un grupo por número omite el filtro imparte, como exige huella.py.
  - El grafo guarda bloques como cadenas para que index.html no imprima objetos sin formato.
requirements-completed: [REQ-50, REQ-52]
completed: 2026-08-06
---

# Fase 15, plan 03 — Horario trazable y grupos activos

El manifiesto conserva sus seis claves históricas cuando el curso no declara el rasgo. Cuando sí
lo hace, registra cada bloque y solo escribe `imparte: false` para los grupos excluidos del ciclo.

## Generación

- La corrida normal omite grupos con `imparte: false`.
- `--grupo <n>` los sigue generando de forma explícita, para las huellas de control.
- `--incluir-no-impartidos` los incorpora de nuevo a la corrida completa.

El grafo ahora muestra bloques como, por ejemplo, `lunes 12:00–13:00 presencial`.

## Verificación

```text
Pruebas focalizadas de manifiesto y grafo: 25 — OK
Suite completa: 310 — OK
Huellas: Todo intacto. 4 documentos comparados.
Plantillas: íntegras
```

Todavía no se modifican los grupos reales; por tanto, la forma registrada de sus manifiestos no
cambia en esta ola.
