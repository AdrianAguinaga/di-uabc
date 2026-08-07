---
phase: 16
slug: mis-clases-en-google-calendar
status: draft
nyquist_compliant: false
created: 2026-08-06
---

# Fase 16 — Estrategia de validación

| Criterio | Señal observable |
|---|---|
| `.ics` importable | Cabecera y cierre exactos, CRLF, `VERSION`, `PRODID`, `VEVENT` con `UID`, `DTSTAMP`, `DTSTART`, `DTEND`; salida creada por CLI. |
| Presencial y virtual | Presencial incluye materia, grupo, horario y `LOCATION`; virtual incluye «virtual» y no contiene `LOCATION`. |
| Fechas escolares | Todos los eventos están entre inicio/fin y no pertenecen a `cal.suspensiones`; pruebas cuentan semanas 1 y 6/13/15. |
| Solo clases | El número real es 122 y cada evento viene de un `Bloque`; no hay `VTODO`, `VALARM`, entregas, exámenes ni texto de metas. |
| Curso ausente | Un descubrimiento que incluye una ruta inexistente reporta aviso y conserva los eventos de las rutas válidas. |
| Cierre | Suite total, integridad de plantillas y huella en verde. |

La importación en una cuenta real de Google Calendar se registra como comprobación humana posterior:
es el único paso que cambia un servicio externo.
