# Instalación

Cómo dejar el generador funcionando en una computadora nueva. Pensado para Windows, que es
donde se exporta a PDF con Word.

Al terminar, `python src/comprobar.py` debe salir todo en verde. Si algo falla, ese comando
dice qué falta y no hay que adivinar.

---

## Resumen

| Qué | Para qué | ¿Obligatorio? |
|---|---|---|
| Python 3.11 o mayor | todo el generador | Sí |
| Los 5 paquetes de `requirements.txt` | plantillas, PDF, YAML, rúbrica | Sí |
| **Poppler** (aporta `pdftotext`) | leer el PDF del PUA | Sí |
| Microsoft Word | exportar el `.docx` a `.pdf` | No, pero sin él no hay PDF |
| Git | traer y actualizar el proyecto | Recomendado |
| Claude Code | los comandos `/di-nuevo`, `/di-pua`, `/di-validar` | No, hay equivalentes en Python |

---

## 1. Python

Descárgalo de <https://www.python.org/downloads/>. Se necesita **3.11 o mayor**.

> En el instalador, marca **«Add python.exe to PATH»** antes de darle a instalar. Es la casilla
> que más problemas ahorra: sin ella, `python` no se reconoce en la terminal.

Comprueba abriendo una terminal nueva:

```
python --version
```

## 2. Traer el proyecto

```
git clone https://github.com/AdrianAguinaga/di-uabc.git
cd di-uabc
```

Sin Git, descarga el ZIP desde la página del repositorio y descomprímelo.

## 3. Paquetes de Python

```
python -m pip install -r requirements.txt
```

Instala `python-docx`, `pdfplumber`, `PyYAML`, `openpyxl` y `pywin32`. El último es solo de
Windows y es el que habla con Word.

## 4. Poppler — el paso que suele fallar

El generador lee el PDF del PUA con `pdftotext`, que **no viene con Python**: es un programa
aparte, parte de Poppler.

1. Descarga la versión para Windows desde
   <https://github.com/oschwartz10612/poppler-windows/releases>.
2. Descomprime el ZIP en una carpeta estable, por ejemplo `C:\poppler`.
3. Añade al PATH la subcarpeta que contiene los `.exe` — termina en **`Library\bin`**, algo como
   `C:\poppler\poppler-24.08.0\Library\bin`.
   - Menú Inicio → «Editar las variables de entorno del sistema» → *Variables de entorno* →
     selecciona **Path** → *Editar* → *Nuevo* → pega la ruta → Aceptar.
4. **Cierra la terminal y abre una nueva.** El PATH no se actualiza en las ya abiertas.

Comprueba:

```
pdftotext -v
```

Debe responder con la versión. Si dice que no se reconoce el comando, la ruta del PATH está mal
o la terminal es la de antes.

## 5. Microsoft Word

Si ya está instalado y activado, no hay nada que hacer: `pywin32` lo encuentra solo.

Sin Word se generan igual los `.docx` — solo no se exportan a `.pdf`. La alternativa es abrir el
documento y guardarlo como PDF a mano, o instalar LibreOffice y convertir con:

```
soffice --headless --convert-to pdf <archivo.docx>
```

## 6. Comprobar

```
python src/comprobar.py
```

Verifica Python, los cinco paquetes, `pdftotext`, Word, los archivos de configuración y que las
plantillas CIAD sigan intactas. Sale con error si falta algo indispensable.

Y para asegurar que la lógica está sana:

```
python -X utf8 -m unittest discover -s pruebas
```

---

## Primer uso

Con Claude Code, que es como está pensado usarlo:

```
/di-pua puas/fuente/<archivo>.pdf     # ingiere un PUA nuevo
/di-nuevo                              # pregunta y genera el DI completo
/di-validar cursos/2026-2/<clave>      # revisa un DI ya hecho
```

Sin Claude Code, los mismos pasos en Python:

```
python src/ingesta_pua.py puas/fuente/<archivo>.pdf
python src/validar.py cursos/2026-2/<clave>/curso.yaml
python src/generar.py cursos/2026-2/<clave>/curso.yaml
```

`/di-nuevo` no tiene equivalente directo: es el que hace las preguntas y **redacta las metas**.
Sin él hay que escribir el `curso.yaml` a mano, tomando como modelo
`cursos/2026-2/39056-big-data/curso.yaml`.

---

## Problemas comunes

**«`python` no se reconoce como un comando»**
No se marcó «Add python.exe to PATH» al instalar. Reinstala Python marcando la casilla, o añade
su carpeta al PATH a mano.

**«No se encontró `pdftotext`»**
Falta el paso 4, o la terminal se abrió antes de tocar el PATH. Cierra y abre otra.

**«Falta pywin32, que es lo que habla con Word»**
`python -m pip install pywin32`. En una máquina sin Word no hay ruta COM.

**El renderizado falla diciendo que una plantilla no coincide con su registro**
Alguien escribió sobre una plantilla de `referencias/`. **No sigas generando documentos.**
Recupérala desde Git:

```
git checkout -- referencias/
python src/plantillas.py verificar
```

**Los acentos salen mal en la terminal**
Usa `python -X utf8 …`, como en los ejemplos. Windows no siempre asume UTF-8.

---

## Qué NO hay que tocar

- **`referencias/`** — las plantillas oficiales del CIAD y el Estatuto. El generador copia,
  nunca escribe encima; su `sha256` está registrado y se verifica antes de cada copia.
- **`ejemplos/`** — los documentos de referencia contra los que se compara el resultado.

Si alguno cambia, el renderizado se detiene en vez de producir un documento de origen
desconocido. Es a propósito.
