---
phase: 16
slug: mis-clases-en-google-calendar
status: decided
created: 2026-08-06
---

# Fase 16 — Contexto de ejecución

## Alcance

Dentro: exportar y probar un `.ics` del calendario de clases del profesor, usando únicamente los
bloques de los cursos existentes y el calendario escolar oficial. Incluye el archivo real 2026-2,
la guía de uso y la validación estructural local.

Fuera: crear el curso o PUA 932, inventar horarios para 531, integrar entregas o evaluaciones,
modificar el `.docx`, y subir/importar eventos en una cuenta de Google sin autorización posterior.

## Decisiones cerradas

- El comando será `python src/exportar_ics.py <ciclo>` y escribirá
  `horarios/salida/Clases-<ciclo>.ics`; se podrá indicar `--salida` para pruebas y para elegir una
  copia a importar.
- Se exportan solo bloques de grupos `imparte` y se omiten grupos sin bloques. No hay suficientes
  datos para convertir `dias_presencial` heredado en eventos horarios.
- Cada bloque de cada fecha válida se vuelve un `VEVENT` individual. No se usa `RRULE`, `EXDATE`,
  `VTODO` ni `VALARM`.
- Las horas se interpretan en `America/Tijuana` y se escriben en UTC con sufijo `Z`; `UID` es
  determinista por ciclo, clave, grupo, fecha, hora y ambiente. `DTSTAMP` registra el instante de
  exportación en UTC.
- Presencial: `SUMMARY` con materia y grupo, `LOCATION` igual al aula. Virtual: `SUMMARY` con la
  marca «virtual» y ninguna propiedad `LOCATION`.
- El archivo usa UTF-8, CRLF, escape RFC y plegado de líneas por octetos. No se añade dependencia
  externa.
- La importación de prueba en Google Calendar no se ejecuta automáticamente: es una acción externa.

## Casos que fijan el contrato

| Caso | Resultado |
|---|---|
| 961, lunes 12:00–13:00 | 14 eventos, porque 2 y 16 de noviembre son suspensión. |
| 961, martes 12:00–13:00 y 16:00–17:00 | 32 eventos; no hay suspensión martes. |
| 971, lunes presencial y martes virtual | 14 presenciales con `LOCATION`, 16 virtuales sin ella. |
| 972, miércoles presencial | 15 eventos; 16 de septiembre queda fuera. |
| 962 | 0: `imparte: false`. |
| 531 | 0: no declara bloques con horas. |
| 932 | 0: no existe `curso.yaml`, sin error para los demás. |

**Resultado esperado:** 122 eventos para 2026-2.
