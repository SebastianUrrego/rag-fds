# RAG con Fichas de Datos de Seguridad (FDS)

Sistema de **Recuperación Aumentada por Generación (RAG)** para consultar Fichas de
Datos de Seguridad (FDS) del sector de pinturas, con énfasis en fidelidad,
trazabilidad, reproducibilidad y eficiencia de recursos.

**Parcial final de NLP.**

---

## Arquitectura general

```
┌──────────────────────────────┐        ┌──────────────────────────────────┐
│        LOCAL (Windows)       │        │        AWS EC2 (Learner Lab)     │
│                              │  SSH   │                                  │
│  1. Extracción PDF → Markdown│ tunnel │  Ollama (API :11434)             │
│     (PyMuPDF + Tesseract)    │ ─────► │   ├─ qwen2.5:3b / llama3.2:3b    │
│                              │ ◄───── │   └─ nomic-embed-text            │
│  2. Chunking por secciones   │        │                                  │
│  3. Índice vectorial         │        │  3 métricas RAGAS evaluadas      │
│     (ChromaDB)               │        │  con el LLM local del EC2        │
│  4. RAG: retrieve + generate │        │                                  │
│  5. Evaluación RAGAS         │        │                                  │
└──────────────────────────────┘        └──────────────────────────────────┘
```

- Los **PDF y el índice vectorial** quedan en local; solo las llamadas de
  inferencia (embeddings y generación) van al EC2.
- Toda la inferencia usa **modelos locales vía Ollama** (sin APIs de pago).

## Estructura del repositorio

```
├── data/                  # PDFs originales (no versionados)
├── corpus/                # Markdown generado + imágenes + log de extracción
│   └── <año>/<producto>/
├── src/
│   ├── extraction/        # Pipeline PDF → Markdown + verificación + OCR
│   ├── rag/               # Chunking, embeddings, índice, generación
│   └── evaluation/        # Conjunto de 12 preguntas + RAGAS
├── results/               # CSV/JSON con resultados por pregunta y top-k
├── docs/
│   ├── arquitectura.md    # Decisiones de diseño y justificaciones
│   └── roadmap.md         # Plan de trabajo y checklist de entregables
├── requirements.txt
└── README.md
```

## Requisitos

- Python 3.12
- Tesseract OCR (para el OCR puntual)
- Cuenta AWS Learner Lab (EC2 con Ollama para inferencia)

## Ejecución

*(se completa a medida que se implementan los módulos)*

```bash
pip install -r requirements.txt

# 1. Extracción: 101 FDS -> corpus/ (~3 minutos)
python -m src.extraction.run

#    ...o solo 5 fichas para probar cambios rápido:
python -m src.extraction.run --limit 5

# 2. Índice vectorial
python -m src.rag.build_index

# 3. Consulta
python -m src.rag.query "¿Cuáles son los primeros auxilios para el KORAZA BLANCO 2650?"

# 4. Evaluación RAGAS
python -m src.evaluation.run --topk 3
python -m src.evaluation.run --topk 6
```

## Documentación

- [Arquitectura y decisiones de diseño](docs/arquitectura.md)
- [Roadmap y checklist de entregables](docs/roadmap.md)
- [Evidencia y metodología de verificación de extracción](docs/verificacion_extraccion.md)
- [Plantilla de muestreo manual (verificación humana)](docs/muestreo_manual.md)

---

## Avance por fases

### Fase 1 — Extracción y fidelidad documental (30 % — Completada)

En esta fase se construyó y ejecutó el pipeline de extracción documental que convierte las **101 Fichas de Datos de Seguridad (FDS)** suministradas —de fabricantes como Pintuco, CORLANC, SIKA, Corona, Invesa, PPG, AKZONOBEL, TECNIDECOR, QUIMICA COSMOS, Pintubler y Axalta (años 2018–2025)— a documentos Markdown estructurados, preservando su fidelidad técnica y garantizando la trazabilidad de cada elemento.

- **Pipeline de extracción (`src/extraction/`):**
  - Implementado en Python con **PyMuPDF (`fitz`)** y **`pdfplumber`** (100 % open source).
  - Genera un archivo `.md` por cada FDS en `corpus/<año>/<producto>.md` preservando cabeceras de metadatos, los títulos de las 16 secciones estándar GHS, listas, notas, unidades de medida y referencias normativas.
  - Las tablas se extraen con `pdfplumber` y se renderizan en tablas Markdown estándar (soporte de celdas multilínea con `<br>`).
  - Las imágenes técnicas (pictogramas GHS, diagramas, logos) se conservan como archivos independientes en `corpus/<año>/<producto>/img/` enlazadas con **rutas relativas** y trazabilidad de documento, página y sección (**923 imágenes extraídas, 0 enlaces rotos**).

- **Trazabilidad de secciones:**
  - Mapa de 16 secciones GHS generado en la cabecera de cada ficha indicando página y estado (`OK` vs `AUSENTE EN ORIGINAL`).
  - Detección dual: encabezados numerados oficiales respaldados por palabras clave por sección.
  - Regla estricta: cuando una sección no existe en la fuente, se etiqueta como **`AUSENTE EN ORIGINAL (no inferir)`**, sin inventar ni completar información.

- **Verificación automática y validación cruzada:**
  - Doble verificación cruzada: contraste entre tablas extraídas con `pdfplumber` y texto de la página en `PyMuPDF`.
  - **74/101 tablas verificadas** con cobertura ≥ 80 % y **27 marcadas para revisión** debido a layouts complejos con celdas fusionadas (todas preservan su contenido textual íntegro en el Markdown).
  - La evidencia por ficha (celdas totales, celdas coincidentes, cobertura) queda registrada en `results/verification_log.csv`.

- **Metadatos de procedencia y versión:**
  - Extracción desde la sección 1 aplicando reglas anti-falsos-positivos (anclaje de etiquetas, rechazo de direcciones/teléfonos y filtro de razones sociales).
  - **97/101 fabricantes** y **90/101 versiones/fechas** identificados automáticamente; los casos dudosos quedan registrados en `results/pendientes_revision.csv` para verificación manual.

- **OCR y elementos no textuales:**
  - Tesseract 5.4 + paquete en español (`tessdata/spa.traineddata`) integrado.
  - Se confirmó que el corpus es digital: **0 páginas escaneadas**.
  - Se detectó y documentó **1 página en blanco en el original** (FDS 97, pág. 17), diferenciándola de un fallo de extracción.
  - Limitación documentada: los pictogramas GHS no se interpretan por inferencia visual; solo se cita lo expresado en texto por la FDS.

- **Artefactos y resultados generados:**
  - `corpus/`: 101 archivos Markdown y 923 imágenes organizados por año.
  - `results/extraction_log.csv`: log general de extracción por ficha.
  - `results/verification_log.csv`: métricas de validación cruzada y cobertura de tablas.
  - `results/pendientes_revision.csv`: 11 versiones y 4 fabricantes a confirmar.
  - `docs/verificacion_extraccion.md`: memoria técnica de metodología y limitaciones.
  - `docs/muestreo_manual.md`: asignación de 12 fichas para verificación humana del equipo.

### Cómo funciona el pipeline de extracción

Archivos (`src/extraction/`):

| Archivo | Rol |
|---|---|
| `config.py` | Rutas, tabla de las 16 secciones GHS y sus palabras clave de detección |
| `extractor.py` | Motor: texto por página, detección de secciones, metadatos (fabricante/producto/versión), imágenes |
| `build_markdown.py` | Genera el `.md` por ficha: cabecera de trazabilidad, mapa de secciones, tablas e imágenes |
| `verify.py` | Verificación cruzada pdfplumber ↔ PyMuPDF: cobertura de celdas, páginas escaneadas/en blanco |
| `run.py` | Orquestador: recorre las 101 carpetas, llama a los anteriores y escribe los logs CSV |
| `ocr_pending.py` | OCR puntual con Tesseract (solo si aparece una página escaneada) |

Flujo en una frase:

> `run.py` lee cada PDF → `extractor.py` separa texto/secciones/metadatos/imágenes → `build_markdown.py` arma el `.md` → `verify.py` valida las tablas contra el PDF original → todo queda en `corpus/` y en los CSV de `results/`.

Detalles de diseño relevantes:

- **Detección de secciones en dos niveles**: primero encabezados numerados
  (`"1. IDENTIFICACION..."`, `"SECCIÓN 1:..."`); si falta una sección, búsqueda
  de sus palabras clave en el cuerpo. Lo no encontrado se marca
  `AUSENTE EN ORIGINAL (no inferir)`.
- **Metadatos con reglas anti-falsos-positivos**: etiquetas ancladas a inicio de
  línea, ventana corta de candidatos, rechazo de direcciones/teléfonos/web y
  preferencia por razones sociales con tokens corporativos. Sin confianza → `N/D`.
- **Errores por ficha aislados**: si un PDF falla, se registra como
  `FALLO DE EXTRACCIÓN` y el pipeline continúa con las demás.
- Si se cambia el pipeline, el corpus completo se regenera en ~3 minutos
  (`python -m src.extraction.run`).
