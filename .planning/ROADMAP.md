# Roadmap: Generador de Diseño Instruccional UABC

## Panorama

De un PDF de PUA a un DI firmable en `.docx` y `.pdf`. Se construye de abajo hacia arriba: primero
los cimientos y el banco de conocimientos que da contexto a los agentes, luego los dos motores que
aportan los datos duros (calendario y PUA), después el modelo que los une y lo valida, y al final
el renderizado, el orquestador que lo hace usable y el grafo que lo hace consultable.

El punto de mayor riesgo es la Fase 6: rellenar las plantillas CIAD reales sin destruir su formato.
Por eso todo lo anterior existe — para que cuando se llegue ahí, los datos ya estén completos y
validados.

## Fases

- [x] **Fase 1: Cimientos y normalización** — repositorio, árbol, contratos de agentes
- [ ] **Fase 2: Banco de conocimientos** — todos los documentos fuente a Markdown
- [ ] **Fase 3: Motor de calendario** — ciclo → semanas numeradas, saltando suspensiones
- [ ] **Fase 4: Ingesta de PUA** — PDF → Markdown normalizado + índice
- [ ] **Fase 5: Modelo y validación** — `curso.yaml` y las 8 reglas
- [ ] **Fase 6: Renderizado docx + pdf** — rellenar las plantillas CIAD reales
- [ ] **Fase 7: Orquestador** — `/di-nuevo`, multi-grupo, de extremo a extremo
- [ ] **Fase 8: Grafo de conocimiento** — cobertura PUA↔metas

## Detalle

### Fase 1: Cimientos y normalización
**Meta**: repositorio listo y contratos de agentes escritos.
**Depende de**: nada.
**Requisitos**: REQ-33, REQ-34, REQ-36, REQ-37
**Criterios de éxito**:
1. `git init` hecho, `.gitignore` excluye salidas regenerables pero versiona `curso.yaml`.
2. El árbol completo existe y `referecnias/` → `referencias/`, `ejmplos/` → `ejemplos/`.
3. `AGENTS.md` contiene las reglas invariables, el contexto de dominio y las notas técnicas.
4. `.planning/config.json` fija el perfil `adaptive`.

### Fase 2: Banco de conocimientos
**Meta**: que cualquier agente pueda consultar la normatividad y las plantillas sin abrir binarios.
**Depende de**: Fase 1.
**Requisitos**: REQ-04
**Criterios de éxito**:
1. `conocimiento/normatividad/` tiene el Estatuto (arts. 63–75), propiedad intelectual y las
   políticas de curso de la Facultad.
2. `conocimiento/plantillas/` tiene el espejo de las 3 plantillas CIAD y las instrucciones de
   llenado, con los deltas entre modalidades explícitos.
3. `conocimiento/estilo/` recoge las reglas de redacción y las convenciones tipográficas.
4. `conocimiento/rubricas/iedi-2023-1.md` lista los indicadores con su clasificación I/N/R.
5. `conocimiento/ejemplos/` tiene el 961 como referencia dorada.

### Fase 3: Motor de calendario
**Meta**: fechas correctas, derivadas del calendario oficial.
**Depende de**: Fase 1.
**Requisitos**: REQ-06, REQ-07, REQ-08, REQ-09
**Criterios de éxito**:
1. `calendarios/2026-2.yaml` refleja el PDF oficial guardado en `calendarios/fuente/`.
2. `python src/calendario.py 2026-2` imprime **16** semanas con sus rangos de fecha.
3. Las semanas 6, 13 y 15 quedan marcadas con su suspensión.
4. Una fecha que cae en suspensión se recorre al siguiente día hábil.
5. Una fecha posterior al 28 nov 2026 es rechazada.

### Fase 4: Ingesta de PUA
**Meta**: convertir PUAs a Markdown consultable, de forma incremental.
**Depende de**: Fase 2.
**Requisitos**: REQ-01, REQ-02, REQ-03, REQ-05
**Criterios de éxito**:
1. `python src/ingesta_pua.py` sobre el PUA de Big Data produce `puas/md/39056-big-data.md`.
2. El front-matter trae los 9 campos de §I; las secciones I–X son encabezados.
3. La §VI se reconstruye con sus 10 prácticas y sus 5 columnas.
4. `puas/INDICE.md` registra clave, nombre, programa, plan, ruta y hash.
5. Reingerir el mismo PDF no duplica el registro.

### Fase 5: Modelo y validación
**Meta**: el contrato entre planeación y renderizado, con sus reglas.
**Depende de**: Fases 3 y 4.
**Requisitos**: REQ-19, REQ-20, REQ-21, REQ-22, REQ-23, REQ-24, REQ-25, REQ-26
**Criterios de éxito**:
1. `src/modelo.py` carga y valida un `curso.yaml` contra su esquema.
2. `config/profesores.yaml`, `esquemas-evaluacion.yaml`, `politicas.yaml` y `plantillas.yaml`
   existen y se cargan.
3. Las 8 reglas están implementadas y cada una tiene una prueba que la hace fallar a propósito.
4. Un esquema que suma 99 es rechazado; uno con un solo parcial también (Art. 68).

### Fase 6: Renderizado docx + pdf
**Meta**: el documento, con el formato institucional intacto.
**Depende de**: Fase 5.
**Requisitos**: REQ-10, REQ-11, REQ-12, REQ-13, REQ-14, REQ-15, REQ-16, REQ-28, REQ-29
**Criterios de éxito**:
1. El `.docx` abre en Word conservando logo, estilos y tablas de la plantilla.
2. La Sección 1 reproduce literalmente la identificación del PUA.
3. La Sección 2 tiene tantas filas-semana como semanas reales, ni una más.
4. La Sección 3 repite el bloque por meta con sus convenciones tipográficas.
5. Las secciones fusionadas y el bloque de firma aparecen al final.
6. El `.pdf` se genera sin dejar procesos `WINWORD.EXE` huérfanos.
7. Comparado contra `ejemplos/961 (1).pdf`, es equivalente en estructura y formato.

### Fase 7: Orquestador
**Meta**: que generar un DI sean seis preguntas.
**Depende de**: Fase 6.
**Requisitos**: REQ-14, REQ-17, REQ-18, REQ-27
**Criterios de éxito**:
1. `/di-nuevo` pregunta en orden y con defaults sensatos.
2. Si el PUA no está en el índice, lo pide y ofrece ingerirlo en el momento.
3. Big Data 2026-2 con grupos 961 y 962 produce cuatro archivos.
4. Los dos documentos difieren solo en el número de grupo y el bloque de firma.
5. `MANIFIESTO.yaml` permite reconstruir el origen de cada dato.

### Fase 8: Grafo de conocimiento
**Meta**: hacer consultable lo que hoy está disperso.
**Depende de**: Fase 7.
**Requisitos**: REQ-30, REQ-31
**Criterios de éxito**:
1. `grafo/` contiene HTML navegable, JSON y un informe de auditoría.
2. El grafo responde qué temas del PUA quedaron sin meta.
3. El grafo responde qué materias comparten competencias.
