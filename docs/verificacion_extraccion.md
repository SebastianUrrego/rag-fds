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

## Limitaciones registradas

1. **OCR**: 1 página escaneada detectada (FDS 97 - MADETEC, AKSONOBEL) marcada
   como "REQUIERE OCR" en el Markdown; Tesseract no instalado aún en el entorno.
   Los pictogramas GHS son imágenes no textuales: su interpretación se limita a
   lo que el propio documento declara en texto.
2. **Tablas con diferencias (27)**: layout no rectangular / celdas fusionadas;
   el contenido textual se conserva igualmente en el Markdown.
3. **Versiones N/D (11)**: completar manualmente contra el PDF durante la
   verificación del corpus (tarea del grupo, no automatizable sin riesgo).
4. **923 imágenes extraídas**: incluye pictogramas, logos y diagramas; la
   asociación imagen↔tabla solo se declara cuando la página lo evidencia.

## Próximos pasos (Fase 2)

- Muestreo manual de 10 fichas comparando MD vs PDF (plantilla abajo).
- Instalar Tesseract y procesar la página escaneada pendiente.
- Chunking por secciones usando el mapa de secciones del Markdown.
