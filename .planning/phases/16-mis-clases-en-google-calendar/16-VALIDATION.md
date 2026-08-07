---
phase: 16
slug: mis-clases-en-google-calendar
status: pending_human
nyquist_compliant: true
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

## Resultado local (2026-08-06)

- [x] Los doce controles nuevos de `.ics` pasan dentro de la suite completa (332 pruebas).
- [x] El archivo real de 2026-2 tiene 122 `VEVENT`, sin eventos en las tres suspensiones.
- [x] La estructura, campos obligatorios, CRLF, escape y plegado se comprueban sin dependencia externa.
- [x] Las plantillas y las cuatro huellas de control permanecen íntegras.
- [ ] Un usuario autorizado importa `Clases-2026-2.ics` en Google Calendar y confirma que no aparece error.
