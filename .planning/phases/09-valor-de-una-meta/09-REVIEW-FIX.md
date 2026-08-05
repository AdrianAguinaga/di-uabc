---
phase: 09-valor-de-una-meta
fixed_at: 2026-08-05T23:31:08Z
review_path: .planning/phases/09-valor-de-una-meta/09-REVIEW.md
iteration: 1
findings_in_scope: 2
fixed: 2
skipped: 0
status: all_fixed
---

# Fase 9: Reporte de arreglo de revisión de código

**Arreglado en:** 2026-08-05T23:31:08Z
**Revisión de origen:** .planning/phases/09-valor-de-una-meta/09-REVIEW.md
**Iteración:** 1

**Resumen:**
- Hallazgos en alcance: 2 (WR-01, WR-02 — IN-01 e IN-02 quedaron fuera del alcance por instrucción explícita)
- Arreglados: 2
- Omitidos: 0

## Hallazgos arreglados

### WR-01: `verificar()` no es de solo lectura si el `MANIFIESTO.yaml` no existía antes de correr

**Archivos modificados:** `src/huella.py`, `pruebas/test_huella.py`
**Commit:** a9afa11
**Arreglo aplicado:** en `_generar_control()`, el bloque `finally` ahora borra el `MANIFIESTO.yaml`
recién escrito con `manifiesto.unlink(missing_ok=True)` cuando `previo is None` (no existía antes de
la corrida), en vez de solo restaurar cuando `previo is not None`. Se añadió la clase
`GeneracionDeControl` a `pruebas/test_huella.py` — la primera prueba que ejerce `_generar_control`,
con `generar.paquete()` sustituido por un doble ligero que solo escribe un `MANIFIESTO.yaml` de
prueba (sin invocar Word, para no romper el tiempo de la suite por D-18). Cubre ambas ramas del
`if`: cuando el manifiesto no existía antes (debe quedar borrado) y cuando ya existía (debe quedar
restaurado exactamente igual).

### WR-02: Una excepción de `forma_del_manifiesto()` no se envuelve en `ErrorHuella` y puede enmascarar el error original

**Archivos modificados:** `src/huella.py`
**Commit:** 0f74914
**Arreglo aplicado:** se añadieron dos cláusulas `except` después de `except generar.ErrorGenerar`:
primero `except ErrorHuella: raise` (para no volver a envolver un `ErrorHuella` que ya venga
envuelto — evita el doble envoltorio que señalaba el contexto de la corrección), y después
`except Exception as e: raise ErrorHuella(...) from e` para envolver cualquier otro fallo de
`forma_del_manifiesto()` (YAML que no parsea, `OSError` de disco, etc.) con un mensaje consistente
con el resto de `ErrorHuella` en vez de dejarlo escapar crudo hasta `main()`.

## Verificación

- `python -X utf8 -m unittest discover -s pruebas`: 218 pruebas en verde (216 previas + 2 nuevas de
  `GeneracionDeControl`).
- `python -X utf8 src/huella.py verificar`: código 0, los 4 documentos de control intactos.
- `python -X utf8 src/plantillas.py verificar`: código 0, las 3 plantillas coinciden con su registro.
- `git status --porcelain cursos/` vacío después de `verificar`: confirma que se restauró el
  invariante D-23/D-28 que WR-01 rompía.

## Hallazgos omitidos

Ninguno — ambos hallazgos en alcance (WR-01, WR-02) se arreglaron. IN-01 e IN-02 quedaron fuera del
alcance de esta corrida por instrucción explícita (IN-02 ya dice en el propio REVIEW.md "ninguna
acción necesaria ahora").

---

_Arreglado: 2026-08-05T23:31:08Z_
_Corrector: Claude (gsd-code-fixer)_
_Iteración: 1_
