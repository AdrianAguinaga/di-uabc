---
phase: 11
slug: segundo-nivel-de-la-calificacion
plan: 03
subsystem: modelo-validacion-trazabilidad
tags: [segundo-nivel, r1, manifiesto, no-contaminacion, huella]
requirements-completed: [REQ-41, REQ-46, REQ-48]
completed: 2026-08-06
---

# Fase 11 — Segundo nivel de la calificación: cierre

La fase queda terminada. El contrato acepta el par fijo `promedio`/`ordinario`, R1 comprueba
su semántica y el manifiesto conserva la trazabilidad condicional. Los cursos de control no
declararon las claves nuevas, y su huella sigue intacta.

## Cambios realizados

- Se añadieron `Nivel`, `SegundoNivel`, `Curso.segundo_nivel` y `Curso.exencion_contra`.
- El catálogo `zra-contabilidad` declara el 60/40 con las etiquetas literales del DI de origen.
- R1 valida suma, extremos y base de exención del segundo nivel; contrasta también contra
  `esquema_id`, sin leer la unidad de los rubros.
- El `MANIFIESTO.yaml` registra el segundo nivel solo cuando el curso lo declara.
- Se actualizaron AGENTS y el skill de validación; se añadieron 17 pruebas: **245 → 262**.

## Salida literal de cierre

### `python -X utf8 -m unittest discover -s pruebas`

```text
......................................................................................................................................................................................................................................................................
----------------------------------------------------------------------
Ran 262 tests in 17.761s

OK
```

### `python -X utf8 src/huella.py verificar`

```text
  ✓ 39056 grupo 961      huella intacta
  ✓ 39056 grupo 962      huella intacta
  ✓ 39062 grupo 971      huella intacta
  ✓ 39062 grupo 972      huella intacta

Todo intacto. 4 documentos comparados.
```

Código de salida: `0`. No apareció `difiere` ni `cambió`.

### `python src/plantillas.py verificar`

```text
Las plantillas coinciden con su registro.
a_distancia      v2025-1   28adedddb985   219881 B  2026-08-03
escolarizada     v2023-1   59f468707657    42739 B  2026-08-03
semipresencial   v2025-1   ae3c1a67c1df   221520 B  2026-08-03
```

### Validaciones de cursos

`39056` y `39062` produjeron cada uno exactamente estos cinco recordatorios y luego `VÁLIDO`:

```text
· [IEDI 2.4] Indica la autoría o ficha bibliográfica de cada recurso de apoyo de terceros.
· [IEDI 3.1] Publica la planeación para lectura en el navegador, no solo como archivo adjunto.
· [IEDI 3.2] Usa la herramienta adecuada para publicar cada recurso (elemento, carpeta, enlace).
· [IEDI 3.5] Crea el Foro de dudas del curso.
· [IEDI 4.1] Coloca cada elemento de la planeación en su sección con la herramienta correcta.

VÁLIDO
```

Ninguno contiene R1. `38985` produjo diez hallazgos y sigue siendo válido; el adicional, antes
de sus cuatro avisos PUA y cinco recordatorios IEDI, fue literalmente:

```text
! [R1] El segundo nivel del curso no coincide con el esquema «zra-contabilidad» del catálogo ({'promedio': {'porcentaje': 60, 'etiqueta': 'Valor del promedio antes del Examen Ordinario'}, 'ordinario': {'porcentaje': 40, 'etiqueta': 'Valor del examen Ordinario'}} contra None). Si el cambio es intencional, quita `esquema_id` o registra un esquema nuevo.
```

El curso pasa de 9 a **10 hallazgos**, conserva `VÁLIDO` y no se modificó. Ese aviso es la deuda
deliberada de la Fase 14, no un defecto de esta fase.

## Integridad y alcance

`Select-String -Path src/grafo.py -Pattern 'segundo_nivel|exencion'` devolvió `0`; no se regeneró
`grafo/`. Antes de crear este resumen, `git diff --name-only` listó exactamente los nueve cambios
de la fase y ningún archivo bajo `cursos/`, `grafo/`, `referencias/` ni `ejemplos/`:

```text
.claude/skills/di-validar/SKILL.md
AGENTS.md
config/esquemas-evaluacion.yaml
pruebas/test_generar.py
pruebas/test_modelo.py
pruebas/test_validar.py
src/generar.py
src/modelo.py
src/validar.py
```

## Próxima fase

La Fase 14 puede declarar el segundo nivel en Contabilidad y convertir sus valores reales en
puntos sin perder trazabilidad. El aviso actual de 38985 debe desaparecer solo al realizar esa
migración, nunca suprimiéndolo desde R1.

## Self-check: PASSED

- 262 pruebas en verde (+17 desde 245).
- Huella de los cuatro documentos de control intacta.
- Plantillas verificadas contra su registro.
- 39056 y 39062 siguen válidos sin hallazgos de R1.
- 38985 sigue válido, sin modificación, con el aviso R1 esperado.
