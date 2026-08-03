---
titulo: "Deltas entre las 3 plantillas CIAD (Escolarizada, Semipresencial, A Distancia)"
fuente: "referencias/CIAD_DI_Plantilla_PRESENCIAL.docx, referencias/CIAD_DI_Plantilla_Semipresencial-2025.docx, referencias/CIAD_DI_Plantilla_A_Distancia-2025.docx"
tipo: plantilla
convertido: 2026-08-03
---

# Deltas entre las 3 plantillas CIAD

> **Nota de extracción:** tabla comparativa construida verificando directamente el contenido de
> las tres plantillas (ver `ciad-presencial.md`, `ciad-semipresencial.md`, `ciad-a-distancia.md`),
> no sólo el mapeo previo de `AGENTS.md`. Las diferencias fueron confirmadas celda por celda.

## Tabla comparativa

| Aspecto | Escolarizada (Presencial) | Semipresencial | A Distancia |
|---|---|---|---|
| Archivo de plantilla | `CIAD_DI_Plantilla_PRESENCIAL.docx` | `CIAD_DI_Plantilla_Semipresencial-2025.docx` | `CIAD_DI_Plantilla_A_Distancia-2025.docx` |
| Versión declarada en el pie | 2023-1 | 2025-1 | 2025-1 |
| Etiqueta "Modalidad Instruccional" (Sección 1) | `Escolarizada` | `Semipresencial.` | `A distancia.` |
| Etiqueta final de autoría (Sección 1) | `Diseño Instruccional para la modalidad semipresencial:` — **error de origen**, ver abajo | `Diseño Instruccional para la modalidad semipresencial:` (correcto para esta plantilla) | `Diseño Instruccional para la modalidad a distancia:` |
| Encabezado de tabla en Sección 2 | `Nombre del curso` | `Nombre del curso` | `Nombre de la asignatura` |
| Filas de semana (Sección 2) | **14** (Unidad 1: 1–5, Unidad 2: 6–10, Unidad 3: 11–14) | **17** (Unidad 1: 1–5, Unidad 2: 6–10, Unidad 3: 11–17) | **17** (misma distribución que semipresencial) |
| Columna `Entrega` | **Dividida**: `Presencial / Sincrónico` y `Virtual / Asincrónico` | **Dividida**: igual que Escolarizada | **Sin dividir** — una sola celda por semana |
| Columnas de rejilla reales de la tabla de Sección 2 | 7 (`Semana` fusionada horizontalmente sobre 2 columnas visuales de Entrega) | 7 (igual) | 6 (no hay sub-división de Entrega) |
| Sección 3 — pasos `Primero…Quinto` | **No** | **Sí** | **Sí** |
| Sección 3 — encabezado `► Reflexión de aprendizaje \| ¿Cómo sabré que logré la meta?` | **No** | **Sí** | **Sí** |
| Sección 3 — `Criterios de evaluación` dentro del bloque de reflexión | No aplica (no hay bloque de reflexión) | Sí | Sí |
| Documento de instrucciones de llenado propio | **No existe** (`referencias/` no tiene un `..._PRESENCIAL_Instrucciones...docx`) | `CIAD_DI_Plantilla_Semipresencial_Instrucciones-2025.docx` | `CIAD_DI_Plantilla_A_Distancia_Instrucciones-2025.docx` |
| Sección 2 en Blackboard (según instrucciones de llenado) | No aplica (no es plataforma-dependiente en el mismo grado) | Tabla o imagen | **Archivo descargable** (Blackboard Ultra no acepta tablas) |

## Error de origen documentado: plantilla Escolarizada (Presencial)

La plantilla `CIAD_DI_Plantilla_PRESENCIAL.docx`, en la Sección 1, bajo el bloque
**"►Autores, fechas de elaboración y última actualización"**, trae el campo:

```
Diseño Instruccional para la modalidad semipresencial:
```

Esto es un **error de autoría de la plantilla CIAD original** — la plantilla es para la
modalidad Escolarizada/Presencial, no semipresencial. Se confirmó revisando directamente el
`.docx` con `pandoc` (ver línea correspondiente en `ciad-presencial.md`).

**Regla para el renderizador:** el DI generado para modalidad Escolarizada debe reproducir este
campo **corregido** —

```
Diseño Instruccional para la modalidad escolarizada:
```

— dejando esta nota como constancia del error de origen, tal como indica `AGENTS.md` § Notas
técnicas. No se debe reproducir el error tal cual en los documentos generados; sí queda
documentado aquí para que quien audite el generador entienda por qué el texto generado no
coincide letra por letra con la plantilla original en ese campo específico.

## Semanas: la plantilla no manda, el calendario sí

Las tres plantillas traen un número fijo de filas de semana (14 la presencial, 17 las otras dos).
Para el ciclo **2026-2** (10 de agosto – 28 de noviembre de 2026 = 16 semanas), ninguna plantilla
calza exacto:

- Escolarizada (14 filas) necesita **agregar 2 filas**.
- Semipresencial y A Distancia (17 filas) necesitan **eliminar 1 fila**.

El número de semanas siempre lo determina `calendarios/<ciclo>.yaml`, nunca la plantilla (ver
REQ-07 y Fase 3 del roadmap). El renderizador clona o elimina filas de la tabla de Sección 2 según
corresponda (`copy.deepcopy(tr._tr)` + `tbl._tbl.insert()`, ver notas técnicas de `AGENTS.md`).
