---
phase: 16-mis-clases-en-google-calendar
verified: 2026-08-06
status: pending_human_import
score: 5/6 criterios del roadmap verificados localmente; importación real pendiente
requirements: [REQ-53]
---

# Fase 16: Mis clases en Google Calendar — Reporte de verificación

## Criterios del roadmap

| # | Criterio | Estado | Evidencia |
|---|---|---|---|
| 1 | Comando produce un `.ics` que Google Calendar importe sin error | ◐ PENDIENTE HUMANO | `python -X utf8 src/exportar_ics.py 2026-2` crea `horarios/salida/Clases-2026-2.ics`; las pruebas validan la estructura RFC. Falta importarlo en una cuenta autorizada de Google. |
| 2 | Presencial con materia, grupo, horario y aula; virtual marcado y sin sala | ✓ | `CalendarioReal20262.test_presencial_tiene_aula_y_virtual_no_tiene_ubicacion` y `SerializacionIcalendar.test_virtual_se_marca_y_no_lleva_location`. |
| 3 | Respeta clases y suspensiones | ✓ | 122 eventos; `test_cada_evento_esta_dentro_de_clases_y_fuera_de_suspension` y el conteo de las semanas 6, 13 y 15. |
| 4 | Solo clases | ✓ | `eventos_de()` solo recorre `Grupo.horario.bloques`; la prueba prohíbe `VTODO`, `VALARM`, entregas, exámenes, tutorías e investigación. |
| 5 | Curso sin YAML no bloquea los demás | ✓ | `ComandoDeExportacion.test_el_comando_escribe_el_archivo_y_el_curso_ausente_no_bloquea` carga Big Data junto a 932 ausente y conserva la exportación. |
| 6 | Suite y plantillas en verde | ✓ | 332 pruebas en 26.001 s; las tres plantillas registradas íntegras. |

## Controles transversales

`python -X utf8 src/huella.py verificar` confirmó las cuatro huellas tras la exportación. El `.ics`
es una salida ignorada por Git, de modo que no cambia los documentos CIAD ni sus manifiestos.

## Único paso pendiente

En Google Calendar web: **Configuración → Importar y exportar → Seleccionar archivo del ordenador**,
elige `horarios/salida/Clases-2026-2.ics`, selecciona un calendario de destino y pulsa **Importar**.
La [guía oficial](https://support.google.com/calendar/answer/37118?hl=es) describe ese flujo. Confirma
que Google no muestra error y que aparecen 122 eventos; entonces REQ-53 y la Fase 16 podrán pasar a
`passed`.
