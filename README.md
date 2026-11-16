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

# 1. Extracción
python -m src.extraction.run --input data/ --output corpus/

# 2. Índice vectorial
python -m src.rag.build_index

# 3. Consulta
python -m src.rag.query "¿Cuáles son los primeros auxilios para el KORAZA BLANCO 2650?"

# 4. Evaluación RAGAS
python -m src.evaluation.run --topk 3
python -m src.evaluation.run --topk 6
```

## Documentación

- [Arquitectura y decisiones](docs/arquitectura.md)
- [Roadmap y entregables](docs/roadmap.md)
