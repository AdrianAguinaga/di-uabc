---
name: di-pua
description: Ingiere un Programa de Unidad de Aprendizaje (PUA) en PDF y lo convierte a Markdown normalizado en puas/md/, registrándolo en puas/INDICE.md. Úsala cuando el usuario suba un PUA nuevo o pida convertir un PDF de PUA.
---

# Ingerir un PUA

Convierte el PDF oficial de un Programa de Unidad de Aprendizaje en Markdown con front-matter
YAML, para que quede en git como contexto consultable.

## Uso

```
python src/ingesta_pua.py puas/fuente/<archivo>.pdf
```

Si el usuario no indica archivo, lista `puas/fuente/*.pdf` y compara contra `puas/INDICE.md`:
ingiere solo los que falten.

Produce `puas/md/<clave>-<slug>.md` y actualiza `puas/INDICE.md` con clave, nombre, programa,
plan y `sha256`. Reingerir el mismo PDF produce salida idéntica y no duplica el registro.

## Reglas

1. **No corrijas el PUA.** Sus defectos de origen (numeración repetida, campos vacíos) se
   conservan literales y se reportan como avisos. El PUA es un documento oficial; si trae un
   error, el error se hace visible, no se enmienda en silencio.
2. **No inventes datos ausentes.** Si un campo viene vacío en el PDF, queda vacío y se emite un
   aviso pidiendo confirmación contra el programa impreso.
3. **Repórtale al usuario los avisos** al terminar. Son las decisiones que el generador no puede
   tomar solo.
4. El PDF fuente se conserva en `puas/fuente/` — es la trazabilidad del `sha256`.

## Después de ingerir

Haz un commit atómico por PUA: `git add puas/md/<archivo>.md puas/INDICE.md puas/fuente/<pdf>`.
No uses `git add -A`.

## Notas técnicas

Las secciones I–V y VII–X se extraen con `pdftotext -layout -enc UTF-8`. La **§VI (prácticas de
laboratorio)** se desordena con `-layout` porque la columna *Procedimiento* envuelve líneas y se
intercala con `UNIDAD`/`Duración`; se extrae con `pdfplumber` cosiendo las filas partidas entre
páginas. Si aparece un PUA cuya §VI no se extraiga bien, revisa `_practicas()` antes de aceptar
la salida.
