# CLAUDE.md

**Lee `AGENTS.md` primero.** Es el archivo canónico: reglas invariables, arquitectura, contexto de
dominio (calendario, modalidades, estructura del PUA, estilo CIAD, fundamento legal) y notas
técnicas. Todo lo que necesitas para trabajar aquí está ahí.

Este archivo solo añade lo específico de Claude Code.

## Skills del proyecto

| Skill | Qué hace |
|---|---|
| `/di-pua <pdf>` | Ingiere un PUA: PDF → `puas/md/` + registro en `puas/INDICE.md` |
| `/di-nuevo` | Orquestador interactivo: ciclo → materia → profesor → modalidad → grupos → esquema |
| `/di-validar <ruta>` | Aplica las 8 reglas de validación a un DI generado |

## Reparto de modelos

`.planning/config.json` fija el perfil GSD **`adaptive`**: Opus planifica y redacta las metas,
Sonnet ejecuta, Haiku verifica. No lo cambies sin decírselo al usuario.

Al planear una fase con `/gsd-plan-phase`, el trabajo de criterio pedagógico (redacción de metas,
mapeo de temas a semanas, reparto de porcentajes) pertenece a la planeación, no a la ejecución.

## Antes de tocar el renderizado

Las plantillas de `referencias/` son la fuente de formato y **no se modifican**. Si necesitas
entender su estructura, léela con `python-docx` en el scratchpad — no la abras para editarla.

El criterio de aceptación del renderizador es reproducir `ejemplos/961 (1).pdf`. Compara contra él
antes de dar por buena cualquier salida.

## Idioma

El proyecto y todos sus documentos son **en español**. El código y los nombres de archivo también:
`calendario.py`, `render_docx.py`, `curso.yaml`. Mantén la consistencia.
