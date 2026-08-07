---
phase: 15
decision: pending_teacher_approval
measured: 2026-08-06
---

# Medición de huellas — horario real 2026-2

Este informe se escribió después de declarar los bloques reales y **antes** de ejecutar
`python src/huella.py registrar`. Las fechas fueron comprobadas en los `.docx` recién generados:
16/16 para 961, 971, 972 y 962.

## 1. Campo de huella, documento por documento

| Documento | `texto_docx` | `informe` | `manifiesto` | Por qué |
|---|---|---|---|---|
| 39056 · 961 | cambia | intacto | cambia | martes → lunes; el manifiesto gana sus bloques. |
| 39056 · 962 | intacto | intacto | cambia | El horario heredado de jueves no cambia; el `MANIFIESTO.yaml` es por curso y su forma se aplica a ambos grupos. |
| 39062 · 971 | cambia | cambia | cambia | martes → lunes; el informe gana los avisos de las semanas 13 y 15. |
| 39062 · 972 | cambia | cambia | cambia | jueves → miércoles; comparte el informe con 971 y recibe el aviso de la semana 6. |

Por eso `huella verificar` reporta **cuatro documentos**, no tres. La cuarta línea de 39056 · 962
es el acoplamiento deliberado del manifiesto compartido; no indica que su `.docx` ni su informe
hayan cambiado. El testimonio de que la excepción queda acotada es que conserva dos de sus tres
campos de huella.

## 2. Fecha por fecha, grupo por grupo

Las entregas virtuales permanecen en sábado; estas tablas sólo miden la fecha presencial impresa.

### 39056 · 961 — martes → lunes

| Sem | Antes | Ahora |
|---:|---|---|
| 1 | 11 ago | 10 ago |
| 2 | 18 ago | 17 ago |
| 3 | 25 ago | 24 ago |
| 4 | 1 sep | 31 ago |
| 5 | 8 sep | 7 sep |
| 6 | 15 sep | 14 sep |
| 7 | 22 sep | 21 sep |
| 8 | 29 sep | 28 sep |
| 9 | 6 oct | 5 oct |
| 10 | 13 oct | 12 oct |
| 11 | 20 oct | 19 oct |
| 12 | 27 oct | 26 oct |
| 13 | 3 nov | **3 nov (igual)** |
| 14 | 10 nov | 9 nov |
| 15 | 17 nov | **17 nov (igual)** |
| 16 | 24 nov | 23 nov |

Las semanas 13 y 15 no se mueven: el lunes está suspendido y el recorrido llega al martes, que
era el día declarado antes. Es una coincidencia medida, no una regla especial.

### 39062 · 971 — martes → lunes

| Sem | Antes | Ahora |
|---:|---|---|
| 1 | 11 ago | 10 ago |
| 2 | 18 ago | 17 ago |
| 3 | 25 ago | 24 ago |
| 4 | 1 sep | 31 ago |
| 5 | 8 sep | 7 sep |
| 6 | 15 sep | 14 sep |
| 7 | 22 sep | 21 sep |
| 8 | 29 sep | 28 sep |
| 9 | 6 oct | 5 oct |
| 10 | 13 oct | 12 oct |
| 11 | 20 oct | 19 oct |
| 12 | 27 oct | 26 oct |
| 13 | 3 nov | **2 nov — suspensión** |
| 14 | 10 nov | 9 nov |
| 15 | 17 nov | **16 nov — suspensión** |
| 16 | 24 nov | 23 nov |

### 39062 · 972 — jueves → miércoles

| Sem | Antes | Ahora |
|---:|---|---|
| 1 | 13 ago | 12 ago |
| 2 | 20 ago | 19 ago |
| 3 | 27 ago | 26 ago |
| 4 | 3 sep | 2 sep |
| 5 | 10 sep | 9 sep |
| 6 | 17 sep | **16 sep — suspensión** |
| 7 | 24 sep | 23 sep |
| 8 | 1 oct | 30 sep |
| 9 | 8 oct | 7 oct |
| 10 | 15 oct | 14 oct |
| 11 | 22 oct | 21 oct |
| 12 | 29 oct | 28 oct |
| 13 | 5 nov | 4 nov |
| 14 | 12 nov | 11 nov |
| 15 | 19 nov | 18 nov |
| 16 | 26 nov | 25 nov |

### 39056 · 962 — sin cambio de fechas

Conserva `dias_presencial: [3]`; sus dieciséis fechas permanecen en jueves, de 13 de agosto a
26 de noviembre. La comprobación de huella confirma que su `texto_docx` permanece intacto.

## 3. Las tres semanas sin día de clase

El único bloque presencial de 971 cae en lunes y el de 972 cae en miércoles. Cuando el calendario
oficial suspende precisamente ese día, no hay otro bloque presencial dentro de la semana. La celda
conserva la fecha suspendida para no cruzar a la semana siguiente. Los avisos literales son:

```text
! [R6] Semana 13: el grupo 971 no tiene ningún día con bloque presencial (2 de noviembre es suspensión). La fecha de esa semana se queda en el día suspendido; reprograma esa clase si debe darse.
! [R6] Semana 15: el grupo 971 no tiene ningún día con bloque presencial (16 de noviembre es suspensión). La fecha de esa semana se queda en el día suspendido; reprograma esa clase si debe darse.
! [R6] Semana 6: el grupo 972 no tiene ningún día con bloque presencial (16 de septiembre es suspensión). La fecha de esa semana se queda en el día suspendido; reprograma esa clase si debe darse.
```

Reprogramar cualquiera de estas tres clases es decisión del docente; el generador sólo hace visible
la suspensión y no inventa una nueva fecha.

## Grafo y límite de cambios

`python src/grafo.py` produjo 368 nodos y 654 aristas; su auditoría mantiene un PUA ausente
(Contabilidad Financiera) y cero anclas rotas. El diff de datos de curso es exclusivamente el
bloque `grupos:` de los dos cursos:

```text
cursos/2026-2/39056-big-data/curso.yaml                  | 16 +++++++++++++++-
.../2026-2/39062-patrones-de-comportamiento/curso.yaml   | 16 ++++++++++++++--
2 files changed, 29 insertions(+), 3 deletions(-)
```

El grafo modificado queda sólo bajo `grafo/`. `pruebas/huellas.yaml` sigue sin cambios: la línea
base todavía no ha sido aceptada.

## Salida literal de `python -X utf8 src/huella.py verificar`

```text
  ✗ 39056 grupo 961: cambió el texto del documento (473992818f37 → 6fa48eab8d8e). Mira qué lo movió con `git diff` y, si el cambio es deliberado, acéptalo con `python src/huella.py registrar`.
  ✗ 39056 grupo 961: cambió la forma del MANIFIESTO.yaml (10d8afbc5570 → 462e28469c6a). Mira qué lo movió con `git diff` y, si el cambio es deliberado, acéptalo con `python src/huella.py registrar`.
  ✗ 39056 grupo 962: cambió la forma del MANIFIESTO.yaml (10d8afbc5570 → 462e28469c6a). Mira qué lo movió con `git diff` y, si el cambio es deliberado, acéptalo con `python src/huella.py registrar`.
  ✗ 39062 grupo 971: cambió el texto del documento (c4255d537780 → 6c4f524c5091). Mira qué lo movió con `git diff` y, si el cambio es deliberado, acéptalo con `python src/huella.py registrar`.
  ✗ 39062 grupo 971: cambió el informe de validación (7874fb9ed4dd → 802397be345c). Mira qué lo movió con `git diff` y, si el cambio es deliberado, acéptalo con `python src/huella.py registrar`.
  ✗ 39062 grupo 971: cambió la forma del MANIFIESTO.yaml (2932d5b2fc0d → e3a6152898d9). Mira qué lo movió con `git diff` y, si el cambio es deliberado, acéptalo con `python src/huella.py registrar`.
  ✗ 39062 grupo 972: cambió el texto del documento (60265f66576b → c0402f07964f). Mira qué lo movió con `git diff` y, si el cambio es deliberado, acéptalo con `python src/huella.py registrar`.
  ✗ 39062 grupo 972: cambió el informe de validación (7874fb9ed4dd → 802397be345c). Mira qué lo movió con `git diff` y, si el cambio es deliberado, acéptalo con `python src/huella.py registrar`.
  ✗ 39062 grupo 972: cambió la forma del MANIFIESTO.yaml (2932d5b2fc0d → e3a6152898d9). Mira qué lo movió con `git diff` y, si el cambio es deliberado, acéptalo con `python src/huella.py registrar`.

9 problema(s).
```
