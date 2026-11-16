# Evidencia de verificación de la extracción (Fase 1)

> Fecha: 2026-11-16 · Pipeline: `src/extraction/` · Logs: `results/extraction_log.csv`, `results/verification_log.csv`

## Alcance

- **101 FDS procesadas** (carpetas FDS 2018–2025), 101/101 con verificación registrada.
- Salida: Markdown por ficha en `corpus/<año>/<slug>.md` con:
  - Cabecera de trazabilidad (documento fuente, fabricante, versión/fecha, páginas).
  - **Mapa de las 16 secciones** con página y estado (OK / AUSENTE EN ORIGINAL).
  - Contenido por página con encabezados de sección inline (anclas para chunking).
  - Tablas en formato Markdown (celdas multilínea con `<br>`).
  - Imágenes enlazadas con rutas relativas + caption con documento/página/sección.
  - Páginas problemáticas marcadas en el propio documento:
    "PÁGINA ESCANEADA: requiere OCR" o "PÁGINA EN BLANCO EN EL ORIGINAL".

## Verificación cruzada de tablas (metodología)

Cada tabla se extrae con **pdfplumber** y se valida contra el texto de la misma
página extraído con **PyMuPDF** (dos bibliotecas independientes). Se verifica la
primera tabla sustantiva del documento: cobertura = celdas cuyo texto normalizado
aparece en el texto de la página.

- **TABLA VERIFICADA (cobertura ≥ 80 %): 74/101**
- **TABLA CON DIFIERENCIAS (revisar): 27/101** — típicamente tablas con celdas
  fusionadas o layouts no rectangulares; se registra y queda para revisión manual.
- Sin tablas detectables → se verifica un bloque de datos de texto (fallback documentado).

## Secciones FDS

- Detección por encabezado numerado + respaldo por palabras clave por sección.
- Clasificación honesta: si no se detecta → **"AUSENTE EN ORIGINAL (no inferir)"**,
  a verificar contra el PDF original en revisión manual. No se completó ninguna
  sección por inferencia.

## Metadatos de procedencia y versión

| Campo | Resultado |
|---|---|
| Fabricante | 97/101 correctos por contenido o nombre de archivo; 4 marcados para revisión manual |
| Producto | 101/101 |
| Versión / fecha | 90/101 capturados; 11 N/D (formatos sin etiqueta reconocible) |

Reglas anti-falsos-positivos aplicadas (documentadas en `extractor.py`):
anclaje de etiquetas a inicio de línea, ventana corta de candidatos, rechazo de
direcciones/teléfonos/web, y preferencia por razones sociales con tokens
corporativos. **Si no hay confianza, se registra N/D en lugar de inferir.**

## OCR y páginas problemáticas

- **Tesseract 5.4** instalado con paquete de español (`tessdata/spa.traineddata`).
- Revisión página a página del corpus completo:
  - **0 páginas escaneadas** que requieran OCR.
  - **1 página en blanco en el original** (FDS 97 - MADETEC, pág. 17):
    verificada visualmente con el render del PDF y por OCR (0 caracteres).
    Documentada como "PÁGINA EN BLANCO EN EL ORIGINAL", no como fallo de
    extracción.
- Limitación documentada: los **pictogramas GHS son imágenes no textuales**;
  su interpretación se limita a lo que el propio documento declara en texto.
  No se intenta inferir su significado.

## Limitaciones registradas

1. **Tablas con diferencias (27)**: layout no rectangular / celdas fusionadas;
   el contenido textual se conserva igualmente en el Markdown.
2. **Versiones N/D (11)**: completar manualmente contra el PDF
   (`results/pendientes_revision.csv`).
3. **4 fabricantes dudosos**: confirmar en el PDF y corregir el log.
4. Las tablas "de layout" de algunos fabricantes (celdas fusionadas) se
   extraen como tablas de una sola celda multilínea — contenido fiel, forma
   imprecisa.

## Muestreo manual pendiente (tarea del grupo)

- Plantilla y fichas asignadas: **`docs/muestreo_manual.md`** (12 fichas:
  1 por fabricante + las de tablas con diferencias).
- Si se hallan errores sistemáticos → ajustar pipeline y regenerar
  (`python -m src.extraction.run`, ~3 min).

## Próximos pasos (Fase 2)

- Chunking por secciones usando el mapa de secciones del Markdown.
- Índice ChromaDB con metadatos de trazabilidad.
- RAG con Ollama en EC2 (Learner Lab).
