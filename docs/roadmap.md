# Roadmap del taller — RAG FDS

> Checklist vivo. Cada fase marca lo hecho y lo pendiente.
> La guía exige que cada integrante pueda explicar y verificar el código:
> revisar cada módulo antes de la demo.

## Fase 0 — Setup e infraestructura
- [ ] Autenticar GitHub CLI y crear el repositorio remoto
- [ ] Verificar en Learner Lab: tipos de instancia disponibles (¿GPU?) y presupuesto
- [ ] Lanzar EC2 (t3.xlarge o g4dn.xlarge según disponibilidad)
- [ ] Instalar Ollama en el EC2 y descargar modelos:
      generador (`qwen2.5:3b` / `llama3.2:3b`), embeddings (`nomic-embed-text`),
      evaluador (`qwen2.5:7b` si hay GPU)
- [ ] Probar túnel SSH al puerto 11434 y una inferencia de prueba
- [ ] Script de registro de hardware y consumo (nvidia-smi/free + horas + costo)

## Fase 1 — Extracción documental (30 %)
- [ ] Pipeline PyMuPDF + pdfplumber: ~100 FDS → Markdown
- [ ] Extracción de imágenes con rutas relativas
- [ ] OCR puntual con Tesseract (donde aplique)
- [ ] Verificador: al menos 1 tabla/bloque por ficha comparada contra el PDF
- [ ] Detector de las 16 secciones GHS (ausente vs. fallo de extracción)
- [ ] Log de extracción en CSV (documento, página, sección, estado, notas)
- [ ] Evidencia de verificación guardada (capturas/comparaciones)

## Fase 2 — RAG funcional (25 %)
- [ ] Chunking por secciones con solapamiento (documentar tamaño/solapamiento)
- [ ] Índice ChromaDB con metadatos (fabricante, producto, doc, página, sección)
- [ ] Generador conectado a Ollama (EC2) con citas obligatorias
- [ ] Manejo de "evidencia insuficiente"
- [ ] Documentar limitaciones y medidas de mitigación
- [ ] Preguntas de desarrollo (distintas a las del set de evaluación) para calibrar

## Fase 3 — Evaluación con RAGAS (20 %)
- [ ] 12 preguntas: 6 directas + 4 integración/comparación + 2 sin respuesta
      (cubrir ≥4 secciones; NotebookLM puede proponer, el grupo revisa)
- [ ] Verificar las 10 referencias contra los PDFs con fragmentos de evidencia
- [ ] Evaluar top-k = 3 y top-k = 6 (todo lo demás constante)
- [ ] Métricas: Faithfulness, Context Precision, Context Recall
- [ ] Resultados por pregunta y configuración en CSV/JSON
- [ ] Revisar las 2 preguntas sin respuesta (no inventar)
- [ ] Analizar 3 casos respondibles (incluidos los de menor puntaje)
- [ ] LLM evaluador local configurado y probado con 2 casos primero

## Fase 4 — Entregables
- [ ] README completo (ejecución, arquitectura, modelos, decisiones)
- [ ] requirements.txt con versiones fijadas
- [ ] Informe máx. 2 páginas (comparación, 3 casos, limitaciones, conclusión)
- [ ] Demo funcional ensayada

## Riesgos a vigilar
- **Presupuesto Learner Lab**: detener la instancia siempre; medir horas.
- **Expiración de sesión EC2** (4 h en Learner Lab): scripts de arranque rápido
  para reanudar en minutos.
- **Calidad de extracción**: tablas complejas de fabricantes distintos → iterar
  el parser con verificación continua, no al final.
