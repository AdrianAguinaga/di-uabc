---
phase: 16
slug: mis-clases-en-google-calendar
researched: 2026-08-06
requirements: [REQ-53]
---

# Fase 16 — Investigación: Mis clases en Google Calendar

## Hechos verificados en el repositorio

- `Horario.bloques` ya guarda `dia`, `inicio`, `fin` y `ambiente`; el grupo conserva `aula` e
  `imparte` en `src/modelo.py`.
- `Calendario` conoce el intervalo oficial de clases y sus suspensiones. `dia_de_clase()` confirma
  que una fecha pertenece a un día de bloque no suspendido, pero para exportar cada bloque es más
  claro recorrer directamente las semanas y excluir `cal.es_suspension(fecha)`.
- Los cursos activos con bloques de 2026-2 son 39056·961, 39062·971 y 39062·972: ocho bloques
  semanales. 39056·962 está declarado con `imparte: false`; 38985·531 conserva el formato heredado
  sin horas de clase y no es exportable sin inventar una hora.
- El horario incluye 932, pero no hay `curso.yaml`. Por la regla canónica, el código no lee
  `horarios/AAAA-N.md`: su ausencia simplemente no puede bloquear los cursos que sí tienen
  contrato.

## Formato y compatibilidad

Google Calendar importa archivos `.ics` desde computadora; exige un `VCALENDAR` con `VERSION` y
`PRODID`, y cada evento entre `BEGIN:VEVENT`/`END:VEVENT`.
([Google Calendar Help](https://support.google.com/calendar/answer/37118?co=GENIE.Platform%3DDesktop&hl=en))

RFC 5545 exige `PRODID` y `VERSION` para el calendario, y en cada `VEVENT` exige `UID`, `DTSTAMP`
y, si no hay `METHOD`, `DTSTART`. `DTEND` fija el fin no inclusivo. El formato usa CRLF.
([RFC 5545, secciones 3.6 y 3.6.1](https://www.rfc-editor.org/rfc/inline-errata/rfc5545.html))

## Decisiones de diseño

1. **Fuente única:** `curso.yaml` y `calendarios/<ciclo>.yaml`; nunca el Markdown de `horarios/`.
   Así 932 no bloquea, y un bloque sin hora no produce una clase inventada.
2. **Un `VEVENT` por bloque y fecha real**, no una recurrencia con excepciones. Se excluyen las tres
   suspensiones antes de serializar; resulta fácil contar y auditar cada evento.
3. **UTC a partir de `America/Tijuana`:** `zoneinfo` de la biblioteca estándar convierte cada fecha
   y hora local a UTC. Evita mantener a mano un `VTIMEZONE` y conserva el cambio estacional si lo
   hubiera.
4. **Solo grupos impartidos con bloques:** `imparte: false`, cursos sin bloques y cursos inexistentes
   se omiten. El comando informa los omitidos para que el profesor no confunda una omisión con un
   error de importación.
5. **Campos mínimos y semánticos:** `SUMMARY` lleva materia, grupo y ambiente; `LOCATION` se escribe
   solo para `presencial`, con `aula`; el virtual se marca en `SUMMARY` y no recibe ubicación física.
   No se leen metas, sesiones, entregas, exámenes ni otros datos de DI.
6. **Salida regenerable:** `horarios/salida/Clases-<ciclo>.ics`, ignorada por Git. El archivo existe
   al ejecutar el comando pero no convierte una salida por semestre en fuente versionada.
7. **Sin dependencias nuevas:** la serialización, escape de texto, plegado de líneas y validación
   estructural viven en la stdlib. Las pruebas inspeccionan el `.ics` resultante y la salida de CLI.
8. **Importación humana separada:** generar y validar sintácticamente el `.ics` es local. Importarlo
   en Google Calendar modifica una cuenta externa y se hará solo con autorización explícita del
   usuario; la guía oficial indica Importar y exportar → seleccionar `.ics` → calendario destino →
   Importar.

## Tamaño esperado del caso real 2026-2

Hay ocho bloques activos por semana. Sobre 16 semanas serían 128 eventos; se restan seis ocurrencias
en suspensión (dos lunes de 961, un miércoles de 961, dos lunes de 971 y un miércoles de 972):
**122 `VEVENT`**. No debe aparecer ningún evento de 962, 531 ni 932.

## Riesgos y controles

| Riesgo | Control |
|---|---|
| Hora local mal desplazada por cambio estacional | `ZoneInfo("America/Tijuana")` y prueba de fechas de agosto y noviembre. |
| Texto iCalendar inválido por coma, punto y coma, barra o acento | función de escape RFC y plegado a 75 octetos; pruebas unitarias. |
| Suspensión colada por recurrencia | eventos individuales y prueba sobre semana suspendida y semana regular. |
| Que se cuelen tareas o exámenes | el exportador solo recorre `Grupo.horario.bloques`; prueba busca 122 clases y ningún componente ajeno. |
| Falta de `curso.yaml` para 932 | descubrimiento por los YAML existentes; prueba con ruta ausente demuestra que los demás se escriben. |
