---
phase: 15
plan: 07
subsystem: contrato-y-cierre
tags: [documentacion, skills, validacion]
requires: [15-01, 15-02, 15-03, 15-04, 15-05, 15-06]
provides:
  - Contrato canónico actualizado para bloques, imparte, componentes y rubros en puntos.
  - Skills de creación y validación alineadas con el modelo y R6.
  - Cierre verificable de los seis criterios del roadmap.
affects: [AGENTS.md, skills, roadmap]
key-files:
  modified:
    - AGENTS.md
    - .claude/skills/di-nuevo/SKILL.md
    - .claude/skills/di-validar/SKILL.md
key-decisions:
  - R6 se documenta como la misma regla ampliada, no como una R9.
  - El criterio histórico de discrepancia entre días y bloques se sustituyó por solapamiento, porque los días se derivan de bloques.
requirements-completed: [REQ-50, REQ-51, REQ-52]
completed: 2026-08-06
---

# Fase 15, plan 07 — Contrato y cierre

`AGENTS.md` ya lista `bloques`, `imparte`, `componentes`, `unidad` y `total` en el contrato de
`curso.yaml`. También explica la compatibilidad con `dias_presencial`, los bloques virtuales, el
filtrado de grupos no impartidos y la ampliación de R6. Las skills `/di-nuevo` y `/di-validar`
preguntan y validan ese mismo contrato.

## Contraste contra los seis criterios del roadmap

1. **Bloques aditivos.** `HorarioConBloques` y `LosCursosDeControlNoCambian` prueban que los
   bloques con ambiente derivan los días presenciales y que el 531 heredado sigue cargando sin
   bloques.
2. **Virtual no mueve fechas.** `BloqueVirtualNoCambiaLasFechas` resuelve dos copias del curso con
   y sin el bloque virtual y confirma las mismas fechas impresas y de entrega.
3. **R6 rechaza horarios inválidos.** `Regla6HorarioMalDeclarado` cubre hora mal formada, fin no
   posterior al inicio y bloques solapados; los dos martes reales de 961 son el caso no solapado.
   El tercer error ya no es una discrepancia con `dias_presencial`: D-01 la volvió imposible al
   derivar esa lista de los bloques. D-05 la sustituyó por el solapamiento.
4. **Cuatro grupos y cambio medido.** `15-MEDICION-HUELLA.md` confrontó 16/16 fechas por grupo
   antes del registro. El commit `012c091` re-registró la huella de forma aislada; la huella de
   962 conserva intactos texto e informe y solo cambia su manifiesto compartido.
5. **Grupo declarado, pero no impartido.** 39056·962 declara `imparte: false`; las pruebas de
   `PaqueteDeBigData` y `ElGrupoQueNoSeImparteNoSeGenera` verifican que la corrida normal lo salta
   y que `--grupo` o `--incluir-no-impartidos` lo recuperan. Las dos expectativas de Big Data ya
   no emiten dos documentos por defecto: es la consecuencia buscada, no una regresión.
6. **Regresión completa.** La suite terminó con 320 pruebas —las 283 de partida más 37— y sin
   fallos.

## Verificación de cierre

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

La última validación emite tres avisos R6 deliberados: semanas 13 y 15 de 971, y semana 6 de 972;
las suspensiones dejan a esos grupos sin otro bloque presencial esa semana. Son avisos para la
decisión docente, no errores ni fechas inventadas.
