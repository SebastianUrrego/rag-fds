# Arquitectura y decisiones de diseño

> Documento vivo: cada decisión se registra aquí con su justificación,
> porque el informe final debe justificar desempeño, costo computacional
> y complejidad operativa.

## 1. Diagrama de componentes

| Componente | Herramienta | Justificación |
|---|---|---|
| Extracción PDF → MD | PyMuPDF (fitz) + pdfplumber | PyMuPDF: rápido y extrae imágenes; pdfplumber: tablas precisas. Ambos open source |
| OCR puntual | Tesseract (pytesseract) | Open source, corre local, sin costo |
| Chunking | Por secciones de la FDS (16 secciones GHS) con solapamiento | Respeta la estructura semántica del documento y mejora la trazabilidad por sección |
| Embeddings | `nomic-embed-text` vía Ollama (EC2) | Open source, alto desempeño en MTEB, tamaño manejable |
| Índice vectorial | ChromaDB (local, persistente) | Embebido, sin servidor, reproducible, guarda metadatos (fabricante, producto, doc, página, sección) |
| Generador | `qwen2.5:3b` o `llama3.2:3b` vía Ollama (EC2) | Cabe en la infraestructura del Learner Lab; open source |
| Evaluación | RAGAS + LLM evaluador local vía Ollama | La guía exige evaluador local compatible con RAGAS, sin APIs pagas |

## 2. Pipeline de extracción (30 %)

```
data/FDS EVALUADAS/FDS <año>/*.pdf
        │
        ▼
  extracción PyMuPDF ──► corpus/<año>/<producto>.md
        │                    ├── imágenes → corpus/<año>/<producto>/img/
        │                    └── rutas relativas en el .md
        ▼
  verificación
   ├─ tabla de referencia por ficha: comparación MD vs PDF (muestreo + capturas)
   ├─ detección de las 16 secciones GHS
   │    ├─ ausente en original  → marcada "SECCIÓN AUSENTE EN ORIGINAL"
   │    └─ esperada pero vacía  → marcada "FALLO DE EXTRACCIÓN"
   └─ log CSV: documento, página, sección, estado, notas
```

Reglas de fidelidad:
- **No se infiere información faltante.**
- Toda imagen con contenido técnico se conserva y se enlaza con ruta relativa.
- La asociación imagen↔tabla solo se hace si hay evidencia explícita.
- Se registran limitaciones del OCR para pictogramas (no textuales).

## 3. RAG (25 %)

- **Chunking**: por sección/subsección de la FDS, con solapamiento de N tokens
  (valor exacto en `src/rag/config.py`; se documenta al calibrar).
- **Metadatos por fragmento**: fabricante, producto, documento, página, sección.
- **Trazabilidad**: el generador recibe el instruction de citar fuente por cada
  afirmación; la respuesta final ancla cada afirmación a su fragmento.
- **Evidencia insuficiente**: si la similitud máxima queda bajo un umbral o los
  fragmentos no sustentan la respuesta, se declara "evidencia insuficiente".

## 4. Evaluación (20 %)

- 12 preguntas fijas: 6 directas, 4 de integración/comparación, 2 sin respuesta.
- Dos configuraciones: **top-k = 3** y **top-k = 6**; corpus, chunking,
  embeddings, generador, prompt y evaluador constantes.
- Métricas: **Faithfulness, Context Precision, Context Recall** (RAGAS).
- Guardado por pregunta y configuración: `user_input`, `retrieved_contexts`,
  `response`, `reference`, fuentes y puntuaciones → `results/`.
- Fallos de evaluación se registran como tales (no como cero).

## 5. Infraestructura y consumo

- EC2 del Learner Lab (tipo por confirmar: GPU g4dn o CPU t3.xlarge).
- Registro de: tipo de instancia, horas encendida, consumo de VRAM/RAM
  (`nvidia-smi` / `free`), y costo estimado por fase.
- La instancia se **detiene** cuando no se usa para no quemar el presupuesto.

## 6. Reproducibilidad

- `requirements.txt` con versiones fijadas.
- Semillas aleatorias y `temperature=0` en generación para determinismo.
- Modelos Ollama con versión (digest) documentada.
- Misma instancia de evaluador para ambas configuraciones.
